import os

def test_filenames(filenames):
    '''
    Return a list with only existent filenames.

    >>> test_filenames(['resources/examplecache.json'])
    ['resources/examplecache.json']
    '''
    result = []
    for filename in filenames:
        filename = os.path.expanduser(filename)
        if os.path.exists(filename):
            result.append(filename)
    return result

def configure_ejtpd(filenames):
    raise NotImplementedError()
