import srpyclient

__test__ = {
'Doctest': srpyclient.PythonEngine
}

if __name__=="main":
    import doctest
    print "Auto-testing module"
    doctest.testmod()