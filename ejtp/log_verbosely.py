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

# Importing this file sets up some logging properties.

import logging
import sys

configured = False

def configure(loud=False):
    '''
    Doctestall should run the following before any other code.

    >>> configure(True)
    >>> debug("example")
    DEBUG:log_verbosely: example
    '''
    global configured
    if configured:
        return
    if loud:
        logging.basicConfig(
            format='%(levelname)s:%(module)s: %(message)s',
            stream=sys.stdout,
            level=logging.DEBUG,
        )
    else:
        logging.basicConfig(
            format='%(levelname)s:%(module)s: %(message)s',
            level=logging.WARNING,
        )
    configured = True

def debug(msg, *args, **kwargs):
    configure()
    logging.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    configure()
    logging.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    configure()
    logging.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    configure()
    logging.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    configure()
    logging.critical(msg, *args, **kwargs)

def log(msg, *args, **kwargs):
    configure()
    logging.log(msg, *args, **kwargs)

def exception(msg, *args):
    configure()
    logging.exception(msg, *args)
