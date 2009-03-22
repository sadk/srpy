#!/bin/bash
rst2html.py README.rst > README.html
epydoc --config=epydoc-config
/opt/local/Library/Frameworks/Python.framework/Versions/2.5/bin/wikir README.rst > README.txt
