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

import sys, os, threading, types, tempfile, random, platform
import srpydecorators

class PythonEngine:
	_id_=''
	_vars_={}
	_counter_=1
	_lock_timeout_=30
	
	def __init__(self, debug=False, showExecTime=False):
		self._debug_=debug
		self._time_=showExecTime
		self._lock_=threading.Event()
		self._lock_.set()
		self._tempdir_=tempfile.mkdtemp('PyEngineSandbox')
		sys.path.append(self._tempdir_)
		for me in dir(self):
			f=getattr(self, me)
			if type(f)==types.InstanceType:
				f.fself=self
			
	@srpydecorators.ThreadSafeDecorator
	def get(self, var_name):
		"Get a variable from globals"
		v=self._vars_[var_name]
		return self._vars_[var_name]
	
	@srpydecorators.ThreadSafeDecorator	
	def set(self, var_name, value):
		"Set a variable inside globals"
		self._vars_[var_name]=value
	
	@srpydecorators.ThreadSafeDecorator	
	def list(self):
		"Returns globals keys"
		return self._vars_.keys()
	
	@srpydecorators.ThreadSafeDecorator		
	def exe(self, cmd):
		"Similar to exec"
		exec cmd in self._vars_
	
	@srpydecorators.BaseDecorator
	def vexe(self, cmd, get=[], **vars):
		"Volatile exec, varibles will be deleted after execution"
		exec cmd in vars
		output={}
		for var in get: output[var]=vars[var]
		return output
	
	@srpydecorators.ThreadSafeDecorator	
	def eval(self, cmd):
		"Similar to eval"
		return eval(cmd, self._vars_)

	@srpydecorators.ThreadSafeDecorator
	def install(self, modname, modtxt):
		"Install a module on a tempdir"
		modfile=os.path.join(self._tempdir_, modname)
		open(modfile, 'w').write(modtxt)
		pymodname=os.path.splitext(modname)[0]
		if self._vars_.has_key(pymodname):
			self._vars_[pymodname]=reload(self._vars_[pymodname])

	@srpydecorators.ThreadSafeDecorator		
	def isModuleInstance(self, varname):
		"Returns true if the namespace variable is a module instance"
		if varname in self._vars_:
			return isinstance(self._vars_[varname], types.ModuleType)
		else:
			return False
	
	@srpydecorators.ThreadSafeDecorator
	def clear(self):
		"Deletes items of the current namespace"
		self._vars_.clear()
	
	@srpydecorators.BaseDecorator	
	def ping(self):
		"Pings the Python Server"
		return "pong"

	@srpydecorators.BaseDecorator
	def isBusy(self):
		"Returns true if the PythonEngine is busy (locked)"
		return not self._lock_.isSet()

	@srpydecorators.BaseDecorator
	def wait(self, timeout=None):
		"Waits for PythonEngine to stop being busy"
		self._lock_.wait(timeout)

	@srpydecorators.BaseDecorator	
	def getID(self):
		return self._id_, platform.node()
	
	@srpydecorators.BaseDecorator	
	def whoami(self):
		"Returns a dictionary with information about the python engine"
		info={}
		info['OS System'], info['Hostname'], info['OS Release'], \
		info['OS Version'], info['Machine Architecture'], \
		info['Processor Architecture'] = platform.uname()
		info['Python Version'] = platform.python_version()
		info['Python Compiler'] = platform.python_compiler()
		info['PythonEngine ID'] = (self._id_, platform.node())
		return info

class PythonEngineServer:
	def __init__(self, urifile=None, *args, **kwds):
		import Pyro, Pyro.core, atexit
		# Check pyeng is given, if not, start a new one
		self.pyeng=PythonEngine(*args, **kwds)
		# Initialize Pyro server
		Pyro.core.initServer()
		self.daemon=Pyro.core.Daemon()
		pyrocom=Pyro.core.ObjBase()
		pyrocom.delegateTo(self.pyeng)
		self.uri=self.daemon.connect(pyrocom, "PythonEngine")
		self.pyeng._id_=self.uri.objectID[-10:]
		if urifile!=None: open(urifile, 'a').write(str(self.uri)+'\n')
		#print self.uri
		atexit.register(self.stop)
		#print Pyro.config.PYRO_CONFIG_FILE
		
	def start(self, threaded=False):
		if not threaded: self.daemon.requestLoop()
		if threaded: threading.Thread(target=self.daemon.requestLoop).start()
		
	def stop(self):
		self.daemon.shutdown(True)
