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
Provides tools to connect and control remote python instances
"""

__docformat__="epytext"

class PythonEngine:
    """
    A class that manages the comunication with a (remote) Python engine,
    variable exchange and code running.
    """
    
    def __init__(self, uri, name='', group=''):
        """
        Connects to a remote python engine.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        
        @param uri: remote PythonEngine identifier
        @type uri: str
        @param name: reference name for this PythonEngine
        @type name: str
        @param group: reference group for this PythonEngine
        @type group: str
        """
        try: import Pyro
        except ImportError:
            import sys, imp
            sys.path.append(imp.find_module('srpy')[1])
            import Pyro
                
        import Pyro.core, thread
        from srpyerror import SRPyServerNotFound
        from srpydynamic import NameSpace
        self.py=Pyro.core.getProxyForURI(uri)
        self.uri=uri
        self.name=name
        self.group=group
        self.ns=NameSpace(self)
        # Test connection and get info
        self.info=self.py.whoami()
        try: self.info=self.py.whoami()
        except: raise SRPyServerNotFound, uri
        self.hostname=self.info['Hostname']
        host_info_start=self.uri.find("//")+2
        host_info_stop=self.uri[host_info_start:].find('/')+host_info_start
        self.ip, self.port=self.uri[host_info_start:host_info_stop].split(':')
            
    def set(self, **vars):
        """
        Creates variables on the Python side.

        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> pyeng.set(a=5, b=3)
        >>> c=1
        >>> pyeng.set(c=c)
        >>> pyeng.get(['a', 'b', 'c'])
        {'a': 5, 'c': 1, 'b': 3}
        
        @param vars: the variables to be transfered
        @type vars: kwd dict
        @rtype: None
        """
        import Pyro.util
        for var_name in vars.keys():
            try: self.py.set(var_name, vars[var_name])
            except Exception, x:
                print ''.join(Pyro.util.getPyroTraceback(x))
                raise
                
    def get(self, vars=None):
        """
        Gets variables from the Python side.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> pyeng.set(a=5, b=3, c=1)
        >>> pyeng.get()
        ['a', 'c', 'b']
        >>> pyeng.get(['a', 'b'])
        {'a': 5, 'b': 3}
        >>> pyeng.get('a')
        5
        
        @type vars: None or str or list
        @param vars: if None: returns a list of available variable names;
        if str: returns the variable with the name given;
        if list: returns a dictionary of variable_names:variable_values
        @return: list of available variable names
        or variable with the given name
        or dictionary of variable_names:variable_values
        @rtype: any
        """
        import types
        import Pyro.util
        try:
            if vars==None: return self.py.list()
            if type(vars)==types.StringType: return self.py.get(vars)
            else:
                pyvars={}
                for var in vars:
                    pyvars[var]=self.py.get(var)
                return pyvars
        except Exception, x:
            print ''.join(Pyro.util.getPyroTraceback(x)) 
            raise
        
    def clear(self):
        """
        Cleans namespace (deleting variable) on the remote Python side
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> pyeng.set(a=1, b=2, c=3) 
        >>> pyeng.get()
        ['a', 'c', 'b']
        >>> pyeng.py.clear()
        >>> pyeng.get()
        []
        
        @rtype: None
        """
        try: self.py.clear()
        except Exception, x:
            print ''.join(Pyro.util.getPyroTraceback(x)) 
            raise

    def eval(self, cmd, **vars):
        """
        Evaluates cmd in the Python side and returns its value
        (similar to python's eval).
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> pyeng.eval("a+b", a=2, b=3)
        5
        
        @param cmd: python expression
        @type cmd: str
        @param vars: any variables that need to be set before evaluating 'cmd'
        @type vars: kwd dict
        @return: remote evaluation result
        @rtype: any
        """
        import Pyro.util
        if vars!={}: self.set(**vars)
        try:
            result=self.py.eval(cmd)
            return result
        except Exception, x:
            print ''.join(Pyro.util.getPyroTraceback(x))
            raise

    def exe(self, cmd, **vars):
        """
        Executes cmd in the Python side (similar to python's exec).
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> pyeng.exe('import math; n = math.sqrt(n)', n=2)
        >>> print pyeng.get('n')
        1.41421356237
        
        @param cmd: python expression
        @type cmd: str
        @param vars: any variables that need to be set before evaluating 'cmd'
        @type vars: kwd dict
        @rtype: None
        """
        import Pyro.util
        if vars!={}: self.set(**vars)
        try: self.py.exe(cmd)
        except Exception, x:
            print ''.join(Pyro.util.getPyroTraceback(x))
            raise
            
    def vexe(self, cmd, get=[], **vars):
        """Similar to exe method but all variables are runned in a temporary
        independent namespace and will be deleted after execution.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> pyeng.vexe('import math; a=math.sqrt(n); b=a**2', get=['a', 'b'], n=2)
        {'a': 1.4142135623730951, 'b': 2.0000000000000004}
        
        @param cmd: python expression
        @type cmd: str
        @param get: list of variables to retrieve
        @type get: list
        @param vars: any variables that need to be set before evaluating C{cmd}
        @type vars: kwd dict
        @return: variables mentioned in C{get}
        @rtype: dict     
        """
        import Pyro.util
        try:
            return self.py.vexe(cmd, get, **vars)
        except Exception, x:
            print ''.join(Pyro.util.getPyroTraceback(x))
            raise

    def install(self, *modules):
        """Install modules in the Python server, will be erased on server
        shutdown.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> pyeng.install('srpyinfo', 'srpybenchmark')
        
        @param modules: single string or several strings with module names
        @type modules: arg list - str
        @rtype: None
        """
        import Pyro.util, imp, os
        for mod in modules:
            modfile=imp.find_module(mod)[1]
            modname=os.path.split(modfile)[1]
            modtxt=open(modfile).read()
            try: self.py.install(modname, modtxt)
            except Exception, x:
                print ''.join(Pyro.util.getPyroTraceback(x))
                raise
        
    def imp(self, *modules):
        """
        Imports the given modules remotely.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> pyeng.imp('math', 'types')
        
        @param modules: single string or several strings with module names
        @type modules: arg list - str
        @rtype: None
        """
        for mod in modules:
            self.exe('import %s' % mod)

    def ns(self):
        """
        After initialization allows access to the PythonEngine remote namespace.
        
        Example:

        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)    
        >>> pyeng.ns.dir()
        ['__args__', '__builtins__', '__kwds__']
        >>> pyeng.ns.a=3
        >>> print pyeng.ns.a
        3
        >>> pyeng.imp('math')
        >>> print pyeng.ns.math.sqrt(3)
        1.73205080757
        
        @rtype: any
        """
        pass
    
    def associateFunction(self, func_name):
        """Dynamically generates a new local method that returns the same as
        a Python server function.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> pyeng.exe('from math import sqrt')
        >>> sqrt=pyeng.associateFunction('sqrt')
        >>> print sqrt(3)
        1.73205080757
        
        @param func_name: function name to be associated
        @type func_name: str
        @return: proxy to remote function
        @rtype: function
        """
        #import random
        #argnames=str(random.randint(1000))
        f=lambda *args, **kwds: self.eval('%s(*__args__, **__kwds__)' % func_name,
                                          __args__=args, __kwds__=kwds)
        f.__doc__=self.eval('%s.__doc__' % func_name)
        f.__repr__=lambda: '<Remote Function %s in %s>' % (func_name, self.uri)
        f.__name__=func_name
        return f
    
    def whoami(self):
        """Return information about the remote server.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> info = pyeng.whoami()
        >>> print info.keys()
        ['PythonEngine ID', 'Python Compiler', 'Machine Architecture',
        'Hostname', 'OS System', 'Python Version', 'OS Release',
        'Processor Architecture', 'OS Version']
        
        @rtype: dict
        """
        try:
            return self.py.whoami()
        except Exception, x:
            print ''.join(Pyro.util.getPyroTraceback(x))
            raise
        
    def getURI(self):
        """
        Return PythonEngine URI id.
        
        @rtype: str
        """
        return self.uri
        
    def getInfoString(self):
        """
        Return information about remote PythonEngine.
        
        @rtype: str
        """
        return self.__str__()
        
    def getHostname(self):
        """
        Return the hostname or IP of the associated PythonEngine.
        
        @rtype: str
        """
        return self.info['Hostname']
        
    def getSystem(self):
        """
        Return the OS system name of the associated PythonEngine.
        
        Example:

        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)        
        >>> pyeng.getSystem()
        
        @rtype: str
        """
        return self.info['OS System']

    def setGroup(self, name):
        """
        Updates the group to which the PythonEngine bellongs.
        
        @param name: group name
        @type name: str
        @rtype: None
        """
        self.group=name

    def getGroup(self):
        """
        Returns the associated group name.
        
        @rtype: str
        """
        return self.group

    def isBusy(self):
        """Returns true if the PythonEngine is busy (locked)
        
        @rtype: bool
        """
        return self.py.isBusy()

    def wait(self, timeout=None):
        """
        Waits for PythonEngine to stop being busy
        
        @rtype: None
        """
        self.py.wait(timeout)
        
    def ping(self):
        """
        Pings the Python server.
        
        Example:

        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)             
        >>> pyeng.ping()
        'pong'
        
        @return: server response, typically 'pong'
        @rtype: str
        """
        #import Pyro.util
        #try: self.py.ping()
        #except Exception, x:
        #    print ''.join(Pyro.util.getPyroTraceback(x))
        return self.py.ping()
    
    def benchmark(self, cycles=10):
        """Benchmarks remote engine.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)     
        >>> print pyeng.benchmark()
        
        @param cycles: how many 'sumprimes' cycles should be used,
        high values means a bigger time taken by the processor and
        slower processor benchmark
        @type cycles: int
        @return: (network benchmark in sec., processor benchmark in sec., is busy)
        @rtype: (float, float, bool)
        """
        import time
        try: from srpy.srpybenchmark import execTime
        except ImportError: from srpybenchmark import execTime
        # processor benchmark code
        pcode=""
        pcode=pcode+"\nfrom srpybenchmark import *"
        pcode=pcode+"\nproctime=execTime(lambda: sum_primes(%d))[0]" % cycles
        # start benchmark
        #nettime=execTime(self.ping)[0]
        #proctime=self.vexe(pcode, get=['proctime'])['proctime']
        f = lambda: self.vexe(pcode, get=['proctime'])['proctime']
        nettime, proctime = execTime(f)
        nettime -= proctime
        return nettime, proctime, self.isBusy()
        
    def __repr__(self):
        return "<PythonEngine %s on %s>" % self.info['PythonEngine ID']
    
    def __str__(self):
        info="PythonEngine %s on %s\n" % self.info['PythonEngine ID']
        for key in self.info.keys():
            info=info+"%s: %s\n" % (key, self.info[key])
        return info

        
class EngBox:
    "A class that manages and helps to deal with several PythonEngine(s)"

    _engines_=[]

    def __init__(self, pyengs=[]):
        """
        Creates a new EngBox instance.
        
        Example:
        
        >>> import srpy
        >>> uri1, proc1 = srpy.newSubEngine()
        >>> uri2, proc2 = srpy.newSubEngine()
        >>> pyeng1 = srpy.PythonEngine(uri1)
        >>> pyeng2 = srpy.PythonEngine(uri2)
        >>> engbox = srpy.EngBox([pyeng1, pyeng2])
        
        @param pyengs: PythonEngine(s) instance list
        @type pyengs: list
        @rtype: list of strs
        """
        import thread, srpydynamic
        self._engines_=pyengs
        self.mrp = srpydynamic.MultiRunParallel(self)
        self.mrs = srpydynamic.MultiRunSequential(self)
                    
    def append(self, pyeng):
        """
        Appends a new PythonEngine to the EngBox.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> pyeng = srpy.PythonEngine(uri)
        >>> engbox = srpy.EngBox()
        >>> engbox.append(pyeng)
        
        @rtype: None
        """
        self._engines_.append(pyeng)
        
    def startAndAppend(self, uri):
        """
        Start and append a PythonEngine based on its uri id.
        
        Example:
        
        >>> import srpy
        >>> uri, proc = srpy.newSubEngine()
        >>> engbox = srpy.EngBox()
        >>> engbox.startAndAppend(uri)
        
        @param uri: remote PythonEngine identifier
        @type uri: str
        @rtype: None
        """
        self.append(PythonEngine(uri))

    def startAndAppendFromText(self, uritxt):
        """
        Start and append a PythonEngine based on a text containing a URI id
        per line.

        @param uritxt: sequence of lines with uri identifiers
        @type uritxt: str
        @rtype: None
        """
        for uri in uritxt.split('\n'):
            if 'PYRO' in uri: self.startAndAppend(uri)

    def startAndAppendFromFile(self, urifilepath):
        """
        Start and append a PythonEngine based on a urifile.
                
        @param urifilepath: path to urifile containing the remote
        PythonEngine(s) uri identifiers
        @type urifilepath: str
        @rtype: None
        """
        txt=open(urifilepath).read()
        self.startAndAppendFromText(txt)
    
    def getEngines(self):
        """
        Returns the list of PythonEngine(s)
                
        @rtype: list
        """
        return self._engines_
    
    def toList(self):
        """
        Same as EngBox.getEngines() - Returns the list of PythonEngine(s)
        
        @rtype: list
        """
        return self._engines_
        
    def searchForEngine(self, name='', group='', ip='', hostname=''):
        """
        Search for PythonEngine(s) with given name, group, ip or hostname.
                
        @return: found PythonEngine(s)
        @rtype: EngBox
        """
        pyengs=[]
        for pyeng in self:
            if name=='': nfound=1
            else: nfound=0
            if group=='': gfound=1
            else: gfound=0
            if ip=='': ipfound=1
            else: ipfound=0
            if hostname=='': hfound=1
            else: hfound=0
            if name==pyeng.name: nfound=1
            if group==pyeng.group: gfound=1
            if ip==pyeng.ip: ipfound=1
            if hostname==pyeng.hostname: hfound=1
            if nfound and gfound and ipfound and hfound:
                pyengs.append(pyeng)
        return EngBox(pyengs)
        
    def getFastest(self, single=True, basis='all', *args, **kwds):
        """
        Returns the fastest PythonEngine based on benchmarks
        
        Example:
        
        >>> import srpy
        >>> uri1, proc1 = srpy.newSubEngine()
        >>> uri2, proc2 = srpy.newSubEngine()
        >>> pyeng1 = srpy.PythonEngine(uri1)
        >>> pyeng2 = srpy.PythonEngine(uri2)
        >>> engbox = srpy.EngBox([pyeng1, pyeng2])
        >>> engbox.getFastest()

        @param single: if True, returns the fastest PythonEngine;
        if False, returns a new EngBox with PythonEngine(s) sorted by speed
        @type single: bool
        @param basis: 'proc' to base choice on processor benchmark,
        'net' to base choice on network benchmark or
        'all' to base choice on both.
        @type basis: str
        @param args: arguments to use with the L{PythonEngine.benchmark} method
        @type args: arg list
        @param kwds: keywords to use with the L{PythonEngine.benchmark} method
        @type kwds: kwd dict
        @rtype: PythonEngine or EngBox
        """
        from operator import itemgetter
        bench = self.mrpwait(self.mrp.benchmark(*args, **kwds))
        pyengs={}
        for pyeng in bench:
            if basis=='net': pyengs[pyeng]=bench[pyeng][0]
            elif basis=='proc': pyengs[pyeng]=bench[pyeng][1]
            else: pyengs[pyeng]=bench[pyeng][0]+bench[pyeng][1]
        fastest = [x[0] for x in sorted(pyengs.items(), key=itemgetter(1))]
        if single==True: return fastest[0]
        return EngBox(fastest)
        
    def getDead(self, new=False):
        """
        Returns indexes of dead PythonEngine(s)
        
        @param new: if not False, returns a new EngBox with the PythonEngine(s)
        @type new: bool
        @rtype: list of ints or EngBox
        """
        dead=[]
        for n in range(len(self)):
            try: self[n].ping()
            except: dead.append(n)
        if new==False: return dead
        else: return EngBox(self[dead].toList())

    def cleanDead(self):
        """
        Removes dead PythonEngine(s) from internal list
        
        @rtype: None
        """
        dead=self.getDead()
        for n in dead: del self[n]
        
    def mrs(self):
        """
        mrs - Multi-Run in Sequence
        
        After initialization allows access to PythonEngine methods except 'ns'
        and runs the given method in sequence.
        
        Example:
        
        >>> import srpy
        >>> uri1, proc1 = srpy.newSubEngine()
        >>> uri2, proc2 = srpy.newSubEngine()
        >>> pyeng1 = srpy.PythonEngine(uri1)
        >>> pyeng2 = srpy.PythonEngine(uri2)
        >>> engbox = srpy.EngBox([pyeng1, pyeng2])
        >>> engbox.mrs.set(a=3)
        >>> engbox.mrs.get().values()
        [['a'], ['a']]
        >>> engbox.mrs.get('a').values()
        [3, 3]
        >>> engbox.mrs.get('lets cause an error')
        [KeyError('lets cause an error',), KeyError('lets cause an error',)]
                
        @returns: sequence of PythonEngine reference: method return values, if
        an error ocurs, it will be present as the return value
        @rtype: dict
        """
        pass
        
    def mrp(self):
        """
        mrp - Multi-Run in Parallel
        
        Similar to 'mrs' but runs the given method in parallel through threads.
        
        Example:
        
        >>> import srpy
        >>> uri1, proc1 = srpy.newSubEngine()
        >>> uri2, proc2 = srpy.newSubEngine()
        >>> pyeng1 = srpy.PythonEngine(uri1)
        >>> pyeng2 = srpy.PythonEngine(uri2)
        >>> engbox = srpy.EngBox([pyeng1, pyeng2])
        >>> res = engbox.mrp.benchmark(); res.values()
        ['__null__', '__null__']
        
        @returns: sequence of PythonEngine reference: method return values,
        return values are by default '__null__' until the thread finishes.
        See method 'mrpwait' for ways to wait for threads to finish.
        @rtype: dict
        """
        pass    
        
    def mrpwait(self, mrp_result, timeout=-1, sleeptime=0.01):
        """
        Waits for all the threads in a 'mrp' job to finish.
        
        Example:
        
        >>> import srpy
        >>> uri1, proc1 = srpy.newSubEngine()
        >>> uri2, proc2 = srpy.newSubEngine()
        >>> pyeng1 = srpy.PythonEngine(uri1)
        >>> pyeng2 = srpy.PythonEngine(uri2)
        >>> engbox = srpy.EngBox([pyeng1, pyeng2])
        >>> print engbox.mrpwait(engbox.mrp.benchmark())
        
        @param timeout: maximum amount of time to wait for 'mrp' job to finish,
        if -1 will wait forever.
        @type timeout: number
        @param sleeptime: how offen in seconds the function checks to see if
        'mrp' job has finished, if this value is too low will create high
        processor overhead, on the other side, if the value is too high it
        may cause delays in the return
        @type sleeptime: number
        @rtype: None        
        """
        import time
        start=time.time()
        while 1:
            if mrp_result.values().count('__null__') == 0: return mrp_result
            elif timeout!=-1 and (time.time()-start)>timeout: return mrp_result
            time.sleep(sleeptime)
            
    def __str__(self):
        return repr(self._engines_)

    def __repr__(self):
        return "EngBox(%s)" % (repr(self._engines_))        
        
    def __len__(self):
        return len(self._engines_)
        
    def __getitem__(self, key):
        #print key, type(key)
        if type(key)==type(0):
            return self._engines_[key]
        elif type(key) in [type(()), type([])]:
            engines=[]
            for n in key: engines.append(self._engines_[n])
            return EngBox(engines)                
        else:
            return EngBox(self._engines_[key])

    def __delitem__(self, key):
        del self._engines_[key]

    def __iter__(self):
        return self._engines_.__iter__()

if __name__=='__main__':
    import doctest
    print "Auto-testing module"
    doctest.testmod()
