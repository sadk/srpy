= Simple Remote Python =

InfoSee [http://code.google.com/p/srpy/ the Simple Remote Python site] for more information.

Ricardo Henriques <[mailto:paxcalpt@gmail.com paxcalpt@gmail.com]>2009 by Ricardo HenriquesLicenseBSD, see LICENSES folder for more details.

= About =

Simple Remote Python (SRPy) intends to harness the power of the Python by allowing multiple python programs (instances) to seamlessly communicate and share information between each other. As such, each CPU (or core) in each computer can be considered as an individual that can request for other individuals to store information or run processing tasks. In this context, SRPy abstracts itself from the physical boundaries between processors and computers by looking at them simply as volunteer workers that are able to deal with workloads - this workers can even work in a social manner by communicating with each other on a non-centralized way, sharing information and processing requests.

It is a Python/Jython module providing easy access and control of local/remote python instances. It features:

  * Remote control of python instances (through Python or Jython)
  * Parallel execution of python code on SMP and clusters
  * Low overhead
  * Pure python code
  * Cross-platform portability and interoperability (Windows, Linux, Unix, Mac OS X)
  * Cross-architecture portability and interoperability (x86, x86-64, etc.)
  * Open source


*Note*: Although Jython SRPy clients are supported, the server will not run under Jython. This is a limitation inherited by the Pyro dependency that will be fixed soon.

= Installation =

If you have [http://peak.telecommunity.com/DevCenter/setuptools setuptools]installed you should be able to do *easy_install srpy* to install SRPy. Otherwise you can download the project source and do *python setup.py install*to install. SRPy also works directly from source, just copy the folder srpy to your favorite location and import it. To start the server do: *python path/to/srpyapp.py*

= Dependencies =

The SRPy distribution depends on the [http://pyro.sourceforge.net/ Pyro], it is bundled inside SRPy. It has been tested on Python 2.5 and 2.6.

= Acknowledgments =

SRPy comes bundled with [http://pyro.sourceforge.net/ Pyro], most of its features come from interfacing with the Pyro library.

SRPy is not the only software of the genre, many other great libraries that provide similar features are available:

  * [http://pyro.sourceforge.net/ Pyro]
  * [http://www.parallelpython.com Parallel-Python]
  * [http://rpyc.wikidot.com/ RPyC]
  * [http://code.google.com/p/papyros/ papyros]
  * [http://www.freenet.org.nz/python/spiro/ SPIRO]


Many of the ideas inside SRPy have come from this packages, we don't intend to be the best, just a different flavor that concentrates in bringing:

  * easy of use
  * compatibility with the great features brought from [http://pyro.sourceforge.net/ Pyro]
  * both Python and Jython compatibility


= Documentation =

Documentation can be found on the *doc/* directory or can be generated with the [http://epydoc.sourceforge.net/ epydoc] tool by running *epydoc --config=epydoc-config*. Also do *python path/to/srpyapp.py --help*to see the server options.

= Changelog =

0.2.0    * No longer depends on Parallel-Python
    * Documentation greatly improved and is now included
    * EngBox now acts as a container
    * EngBox able to benchmark remote Python Engines
    * Improved thread safety
    * Code cleanup
    * srpyapp.py can now use a Pyro configuration file
0.1.2    * Fixed several errors
    * Added EngBox class to srpyclient to help manage multiple PythonEngines
0.1.1    * Fixed a Pyro import error: Successfully imports bundled Pyro if available
    * srpy and srpy-bundled are now a unified package


