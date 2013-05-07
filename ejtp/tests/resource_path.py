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
import os.path

def testing_path(path):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        path
    )

def script_path(path):
    # Attempt local version before resorting to global path
    return search_path(path,
        os.path.join(
            os.path.split(__file__)[0],
            '../../scripts',
        )
    ) or which(path)

def search_path(filename, search_path):
    for path in search_path.split(os.pathsep):
        potential_match = os.path.abspath(os.path.join(path, filename))
        if os.path.exists(potential_match):
            return potential_match

def which(execname):
    return search_path(execname, os.environ['PATH'])
