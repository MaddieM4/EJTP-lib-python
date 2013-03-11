'''
This file is part of the Python EJTP library.

The Python EJTP library is free software: you can redistribute it 
and/or modify it under the terms of the GNU Lesser Public License as
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

the Python EJTP library is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser Public License for more details.

You should have received a copy of the GNU Lesser Public License
along with the Python EJTP library.  If not, see 
<http://www.gnu.org/licenses/>.
'''

import os

def test_filenames(filenames, env_var=None):
    '''
    Return a list with only existent filenames.

    If env_var exists in environment variables, it will replace
    filenames already loaded.
    '''
    if env_var:
        env_files = os.environ.get(env_var, None)
        if env_files:
            filenames = tuple(env_files.split(':'))

    result = []
    for filename in filenames:
        filename = os.path.expanduser(filename)
        if os.path.exists(filename):
            result.append(filename)
    return result

def configure_identity_cache(cache, filenames=['~/.ejtp/idents.json', '~/.ejtp/console/idents.json']):
    '''
    Configure cache loading filenames.
    '''
    filenames = test_filenames(filenames, 'EJTP_IDENTITY_CACHE_PATH')
    for filename in filenames:
        cache.load_from(filename)
    return filenames

def configure_ejtpd(filenames):
    raise NotImplementedError()
