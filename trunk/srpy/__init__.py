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
Simple Remote Python (SRPy) intends to harness the power of the Python by
allowing multiple python programs (instances) to seamlessly communicate and
share information between each other. As such, each CPU (or core) in each
computer can be considered as an individual that can request for other
individuals to store information or run processing tasks. In this context,
SRPy abstracts itself from the physical boundaries between processors and
computers by looking at them simply as volunteer workers that are able to
deal with workloads - this workers can even work in a social manner by
communicating with each other on a non-centralized way, sharing information
and processing requests.

B{Quick Start} - X{Starting a Server}:

    - Create a server on a computer by running the srpyapp.py script.
    
Example:

C{toseinin:srpy paxcal$ python2.5 srpy/srpyapp.py}

C{SRPy Server - Simple Remote Python, Network Server}

C{http://code.google.com/p/srpy/ - updates, documentation, examples and support}

C{Starting Basic Server...}

C{URI info:}

C{PYRO://192.168.1.23:7829/c0a801171909517cdef4645b78192636}

C{Write 'quit' or 'exit' to exit...}

    - Copy the X{URI info} as it will be needed when connecting with a client. 

I{Note:} run the server with '--help' to see a list of available options,
srpyapp.py is able to generate multiple servers in one go, optimally you
should have one server per CPU available.


B{Quick Start} - X{Connecting to a Server}:

Here's an example of connecting to the created server:

>>> import srpy
>>> pyeng=srpy.PythonEngine("PYRO://192.168.1.23:7829/c0a801171909517cdef4645b78192636")

Check the L{PythonEngine <srpyclient.PythonEngine>} and
L{EngBox <srpyclient.PythonEngine>} classes for more info on how to work with
remote python engines.

"""

from srpyclient import *
from srpyapp import newSubEngine, detectNCPUs
from srpyinfo import version, copyright
