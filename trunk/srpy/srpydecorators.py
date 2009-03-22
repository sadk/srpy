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

class BaseDecorator:
	def __init__(self, f):
		self.f=f
		self.__name__=f.__name__
		self.__repr__=f.__repr__
		self.__str__=f.__str__
		self.__repr__=f.__repr__
		self.__doc__=f.__doc__
	
	def __call__(self, *args, **kwds):
		fself=self.fself
		if fself._debug_: self.debug(fself, *args, **kwds)
		if fself._time_: startTime=time.time()
		v = self.f(fself, *args, **kwds)
		if fself._time_: self.showTime(startTime, time.time())
		return v
	
	def debug(self, fself, *args, **kwds):
		argstxt=str(args)
		kwdstxt=str(kwds)
		msg = "%s: args=%s, kwds=%s" % (self.f.__name__, argstxt, kwdstxt)
		print timeString(), "[%d]=> " % fself._counter_, msg
		fself._counter_+=1
		
	def showTime(self, startTime, stopTime):
		print "%s command took %.2fs to execute" % (self.__name__,
							    stopTime-startTime)

class ThreadSafeDecorator(BaseDecorator):	
	def __call__(self, *args, **kwds):
		fself=self.fself
		fself._lock_.wait(fself._lock_timeout_)
		try:
			fself._lock_.clear()
			v = BaseDecorator.__call__(self, *args, **kwds)
			return v
		except:
			raise
		finally:
			fself._lock_.set()

def timeString():
    t=time.localtime()[:6]
    return str(t[0])+"-"+str(t[1])+"-"+str(t[2])+" "+\
           str(t[3]).zfill(2)+":"+str(t[4]).zfill(2)+":"+str(t[5]).zfill(2)
