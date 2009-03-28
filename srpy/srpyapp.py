#!/usr/bin/env python
# Simple Remote Python: http://code.google.com/p/srpy/
# Copyright (c) 2009, Ricardo Henriques
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"""
Main interface, contains tools to start new server applications
"""

import sys, os, tempfile, time, types, subprocess

def shell():
    """
    Main console interface, runned by default on 'python srpyapp.py'.
    
    @rtype: None
    """
    
    from optparse import OptionParser
    try: import srpyinfo
    except ImportError: from srpy import srpyinfo 
    
    print "SRPy Server - Simple Remote Python, Network Server"
    print "http://code.google.com/p/srpy/ - updates, documentation, examples and support"

    parser = OptionParser(version="%prog "+srpyinfo.version, usage="\n  %prog --basic [optional arguments]\n  %prog --multi [optional arguments]")
    parser.add_option("-b", "--basic", action="store_true", dest="basic", help="starts a single python engine, stdout is visible, debug mode can only be used with this option", default=False)
    parser.add_option("-m", "--multi", action="store_true", dest="multi", help="starts pyengine in multi-core mode, stdout is invisible, able to spawn servers in each available cpu, ncpus can be used with this option", default=False)
    parser.add_option("-n", "--ncpus", type='int', dest="ncpus", help="how many Python Engines should be started, by default starts one engine per cpu (Eg: dual-core computer will start 2 instances by default)", default=0)
    parser.add_option("-u", "--uri", action="store", dest="urifile", help="filename where to save Python Engines uri information")
    parser.add_option("-p", "--pyrocfg", action="store", dest="pyro_configfile", help="Pyro configuration file, check http://pyro.sourceforge.net/manual/3-install.html for options")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", help="prints extra information about data transfer and execution on the Python engine, can only be used in 'basic' mode", default=False)
    parser.add_option("-t", "--time", action="store_true", dest="time", help="prints how mutch time each remote call took to execute", default=False)
    
    (options, args) = parser.parse_args()
    
    if not options.basic and not options.multi:
        options.basic=True
        #parser.error("please select either option --basic or --multi")
    if options.basic and options.multi:
        parser.error("options --basic and --multi are mutually exclusive")
    if options.basic and options.ncpus:
        parser.error("options --ncpus can only be used in muti-core mode (--multi)")
    if options.multi and options.debug:
        parser.error("options --debug can only be used in basic mode (--basic)")
    if options.multi and options.time:
        parser.error("options --time can only be used in basic mode (--basic)")
    
    # Load Pyro Configuration
    if options.pyro_configfile!=None:
        path=options.pyro_configfile
        if os.path.exists(path):
            print "Using Pyro configuration file: "+path
            os.putenv('PYRO_CONFIG_FILE', path)
            os.environ['PYRO_CONFIG_FILE']=path
        else:
            print "WARNING, could not find Pyro configuration file: "+path
    
    # Create a location for the uri files    
    if options.urifile==None:
        tempdir=tempfile.mkdtemp('PyEngineURI')
        urifile=os.path.join(tempdir, 'uri.txt')
    else: urifile=options.urifile
    # Clean pre-existing uri files
    if os.path.exists(urifile): os.remove(urifile)
        
    ################# Start Engines ################# 
    try: import srpyserver
    except ImportError: from srpy import srpyserver
    ##### Start Basic Mode #####
    if options.basic:
        print "Starting Basic Server..."
        tempdir=tempfile.mkdtemp('PyEngineURI')
        urifile=os.path.join(tempdir, 'uri.txt')
        PES=srpyserver.PythonEngineServer(urifile=urifile, debug=options.debug)
        PES.start(threaded=True)
        uriinfo=open(urifile).read()
    ##### Start Multi-Core Mode #####
    elif options.multi:
        print "Starting Muti-Core Server..."
        ## Detecting number of cpus ##
        ncpus=options.ncpus
        if ncpus==0: ncpus=detectNCPUs()
        # Prepare to initialize
        procs=[]
        uriinfo=""
        for n in range(ncpus):
            uriinfo_, proc = newSubEngine()
            procs.append(proc)
            uriinfo=uriinfo+uriinfo_

    print "URI info:"
    print uriinfo
    
    if options.urifile!=None:
        open(options.urifile, 'a').write(uriinfo)

    while 1:
        input=raw_input("Write 'quit' or 'exit' to exit...\n")
        if input in ['exit', 'quit']:
            sys.exit(0)

def newSubEngine(timeout=30):
    """
    Starts a new srpyapp as a subprocess with the 'basic' option by default.
    
    @param timeout: maximum amount of time to wait for servers to start.
    @type timeout: int    
    @return: uri id, pipe to the new subprocess
    @rtype: str, subprocess
    """
    tempdir=tempfile.mkdtemp('PyEngineURI')
    urifile=os.path.join(tempdir, 'uri.txt')
    
    command = "\"" + sys.executable + "\" -u \"" \
              + os.path.dirname(os.path.abspath(__file__))\
              + os.sep + "srpyapp.py\" -b -u %s" % repr(urifile).replace("'", '"')
    if sys.platform.startswith("win"):
        # workargound for windows
        command = "\"" + command + "\""
    else:
        # do not show "Borken pipe message" at exit on unix/linux
        command += " 2>/dev/null"     
    proc=subprocess.Popen(command, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, shell=True)
    start=time.time()
    while (time.time()-start)<timeout:    
        if os.path.exists(urifile):
            uriinfo=open(urifile).read()
            if uriinfo.count("PYRO")>0: break
        time.sleep(0.01)
    return uriinfo, proc

def detectNCPUs():
    """
    Returns the number of CPUs on the current computer.
    
    @rtype: int
    """
    #for Linux, Unix and MacOS
    if hasattr(os, "sysconf"):
        #Linux and Unix
        if "SC_NPROCESSORS_ONLN" in os.sysconf_names:
            ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
        #MacOS X
        else:
            ncpus = int(os.popen2("sysctl -n hw.ncpu")[1].read())
    #for Windows
    if "NUMBER_OF_PROCESSORS" in os.environ:
        ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
    #return the default value
    if not (isinstance(ncpus, int) and ncpus > 0):
        return 1
    return ncpus

if __name__=="__main__":
    shell()

