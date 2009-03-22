#!/usr/bin/env python
# Simple Remote Python setup script
# For the latest version of the SRPy
# software visit: http://code.google.com/p/srpy/
"""
Standard build tool for python libraries.
"""

import ez_setup
ez_setup.use_setuptools()

import os, sys
#from distutils.core import setup
from setuptools import setup, find_packages
from srpy.srpyinfo import version as VERSION

if sys.version_info < (2, 4):
    print 'ERROR: SRPy requires at least Python 2.5 to run.'
    sys.exit(1)

setup(
        name="SRPy",
        url="http://code.google.com/p/srpy",
        version=VERSION,
        download_url="http://srpy.googlecode.com/files/srpy-%s.zip" % (
            VERSION),
        author="Ricardo Henriques",
        author_email="paxcalpt@gmail.com",
        packages=find_packages(),
        include_package_data=True,
        scripts=[os.path.join("srpy", "srpyapp.py")],
        description="Easy access and remote control of local/remote Python instances",
        platforms=["Windows", "Linux", "Unix"],
        long_description=open("README.rst").read(),
        license="BSD-like",
        classifiers=[
        "Topic :: Software Development",
        "Topic :: System :: Distributed Computing",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        ]
)
