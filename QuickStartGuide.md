# Introduction #

## Starting a Server ##
You can find the **srpyapp.py** script in either the Python scripts folder or in the **srpy** folder.
Startup options can be seen by running:

`python srpyapp.py  -h`

Then start SRPy execution server in either Basic or Multi-Core mode:

`python srpyapp.py  -bd`

This will generate one or multiple URI IDs (example: PYRO://157.99.245.20:7767/9d63f5141e3344194aae09639b8ef091) dependent on how many servers you asked to start, these will be used in the client to indicate to which server to connect.

**Note**: at this point SRPy only supports Python and not Jython servers, although it's possible to use Jython clients. This is a limitation inherited by the Pyro dependency.

## Connecting with a Client ##

To connect with a client we just need to import the **srpy** library and start the **[PythonEngine](PythonEngineAPI.md)** class passing a URI ID as argument:
```
>>> import srpy
>>> pyeng=srpy.PythonEngine("PYRO://157.99.245.20:7767/9d63f5141e70441a42018b6d48c8cc6c")
```

#### Playing with the remote [PythonEngine](PythonEngineAPI.md) ####
```
>>> pyeng.get()
['debug', '__builtins__', 'types']
>>> pyeng.set(a=3)
>>> pyeng.get()
['debug', '__builtins__', 'a', 'types']
>>> pyeng.get('a')
3
>>> pyeng.imp('math')
>>> pyeng.eval('math.sqrt(b)', b=2)
1.4142135623730951
>>> pyeng.exe('c=math.sqrt(c)', c=5)
>>> pyeng.get('c')
2.2360679774997898
```

#### Using the Namespace ####
The special variable **ns** inside the [PythonEngine](PythonEngineAPI.md) allows direct access to the remote namespace:
```
>>> pyeng.ns.dir()
['__args__', '__builtins__', '__kwds__', 'a', 'c', 'debug', 'math', 'types']
>>> pyeng.ns.math.sqrt(5)
2.2360679774997898
>>> pyeng.ns.whoami='Ricardo'
>>> pyeng.ns.whoami
'Ricardo'
```

#### Running Function inside the remote Namespace ####
All functions from the remote namespace can be run remotely through [PythonEngine](PythonEngineAPI.md), results are pulled automatically. Be careful so that the server results are compatible with the client. Here an example using Jython as client and Python with the Numpy package as server:

```
>>> pyeng.imp('numpy')
>>> pyeng.ns.numpy.zeros((4,4))
Traceback (most recent call last):
  File "/Applications/ImageJ/plugins/Py4IJ/core/pytools.py", line 96, in eval
    result=self.py.eval(cmd)
  File "/Applications/ImageJ/plugins/Py4IJ/core/Pyro/core.py", line 394, in __call__
    return self.__send(self.__name, args, kwargs)
  File "/Applications/ImageJ/plugins/Py4IJ/core/Pyro/core.py", line 477, in _invokePYRO
    return self.adapter.remoteInvocation(name, Pyro.constants.RIF_VarargsAndKeywords, vargs, kargs)
  File "/Applications/ImageJ/plugins/Py4IJ/core/Pyro/protocol.py", line 427, in remoteInvocation
    answer = pickle.loads(answer)
ImportError: No module named numpy
```
Now, lets make it Jython friendly:
```
>>> pyeng.imp('numpy')
>>> pyeng.exe("zeros=lambda *args, **kwds: numpy.zeros(*args, **kwds).tolist()")
>>> pyeng.ns.zeros((2,2))
[[0.0, 0.0], [0.0, 0.0]]
>>> pyeng.ns.zeros(shape=(2,2), dtype='uint16')
[[0, 0], [0, 0]]
```