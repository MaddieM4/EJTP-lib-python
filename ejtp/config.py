import os

def test_filenames(filenames, env_var=None):
    '''
    Return a list with only existent filenames.

    If env_var exists in environment variables, it will replace
    filenames already loaded.

    >>> test_filenames(['resources/examplecache.json'])
    ['resources/examplecache.json']
    >>> os.environ['SOME_PATH'] = 'resources/examplecache.json'
    >>> test_filenames(['client.py'], env_var='SOME_PATH')
    ['resources/examplecache.json']
    '''
    env_files = os.environ.get(env_var, None)
    if env_files:
        filenames = tuple(env_files.split(':'))

    result = []
    for filename in filenames:
        filename = os.path.expanduser(filename)
        if os.path.exists(filename):
            result.append(filename)
    return result

def configure_ejtpd(filenames):
    raise NotImplementedError()
