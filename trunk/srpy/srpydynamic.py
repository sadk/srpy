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

import types

class NameSpace:
    "Auxiliary internal class, not to be used..."

    def __init__(self, PythonEngine, root=''):
        self.__dict__['__pyeng__']=PythonEngine
        if root=='': self.__dict__['__root__']=root
        else: self.__dict__['__root__']=root+'.'
    
    def __getattr__(self, attr):
        if attr in ['bogu5_123_aTTri8ute', '_getAttributeNames']:
            raise AttributeError
        attr=self.__dict__['__root__']+attr
        # if it's a module
        if self.__dict__['__pyeng__'].py.isModuleInstance(attr):
            return NameSpace(self.__dict__['__pyeng__'], attr)
        # if it's a callable object
        elif self.__dict__['__pyeng__'].eval("hasattr(%s, '__call__')" % attr):
            return self.__dict__['__pyeng__'].associateFunction(attr)
        # if it's a var
        else:        
            return self.__dict__['__pyeng__'].get(attr)
        
    def __setattr__(self, attr, value):
        attr=self.__dict__['__root__']+attr
        self.__dict__['__pyeng__'].set(**{attr: value})

    def __delattr__(self, attr):
        attr=self.__dict__['__root__']+attr
        self.__dict__['__pyeng__'].exe('del %s' % attr)

    def __str__(self):
        return 'Remote Python object container'
    
    def __methods__(self):
        return self.__pyeng__.dir(self.__dict__['__root__'][:-1])

class MultiRun:
    def __init__(self, engbox, root=''):
        self.__dict__['__engbox__']=engbox

    def __getattr__(self, attr):
        from srpyclient import PythonEngine
        engbox=self.__dict__['__engbox__']
        run=self.__run__
        
        if not hasattr(PythonEngine, attr):
            msg = "%s has no attribute %s" % (repr(PythonEngine), repr(attr))
            raise AttributeError, msg

        obj = getattr(PythonEngine, attr)
        # if it's a callable object
        if hasattr(obj, '__call__'):
            f=lambda *args, **kwds: run(attr, *args, **kwds)
            f.__name__=obj.__name__
            f.__doc__=obj.__doc__
            f.__repr__=obj.__repr__
            return f
        
    def __run__(self, methodname, *args, **kwds):
        pass

class MultiRunSequential(MultiRun):
    def __run__(self, methodname, *args, **kwds):
        engbox = self.__dict__['__engbox__']
        results = {}
        for pyeng in engbox:
            try: results[pyeng] = getattr(pyeng, methodname)(*args, **kwds)
            except Exception, error: results[pyeng] = error
        return results

class MultiRunParallel(MultiRun):    
    def __run__(self, methodname, *args, **kwds):
        import threading
        engbox = self.__dict__['__engbox__']
        results = {}
        # define threaded function
        def f(pyeng, methodname):
            try: results[pyeng] = getattr(pyeng, methodname)(*args, **kwds)
            except Exception, error: results[pyeng] = error
        # start loop
        for pyeng in engbox:
            results[pyeng] = '__null__'
            threading.Thread(target=f, args=(pyeng, methodname)).start()
        return results
