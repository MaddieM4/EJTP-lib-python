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

__all__ = [
    'verbose',
]

import logging
import sys

def makeLogger(name, format, stream, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    streamer = logging.StreamHandler(stream)
    streamer.setLevel(level)
    formatter = logging.Formatter(format)
    streamer.setFormatter(formatter)
    logger.addHandler(streamer)
    return logger

class StreamWrapper(object):
    def __getattr__(self, name):
        return getattr(sys.stdout, name)

configured = False

loudlogger = (
    'ejtp',
    '%(levelname)s:%(name)s: %(message)s',
    StreamWrapper(),
    logging.INFO,
)

normlogger = (
    'ejtp',
    '%(levelname)s:%(module)s: %(message)s',
    sys.stderr,
    logging.WARNING,
)

logger = None

def configure(loud=False):
    '''
    In theory, Doctestall should import ejtp.logging.verbose as one of the
    first modules it imports, which should configure ejtp.logging loudly.

    >>> import verbose
    >>> debug('I am the greatest! - Bender "Bending" Rodriguez') 
    >>> info('I am the greatest! - Bender "Bending" Rodriguez') 
    INFO:ejtp: I am the greatest! - Bender "Bending" Rodriguez
    >>> named_logger = getLogger(__name__)
    >>> named_logger.info('For your information, Amy is way hotter than Bender.')
    INFO:ejtp.logging: For your information, Amy is way hotter than Bender.
    '''
    global configured, logger
    if not configured:
        if loud:
            configured = "loud"
            logger = makeLogger(*loudlogger)
        else:
            configured = "norm"
            logger = makeLogger(*normlogger)

def getLogger(name='ejtp'):
    configure()
    return logging.getLogger(name)

def debug(msg, *args, **kwargs):
    getLogger().debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    getLogger().info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    getLogger().warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    getLogger().error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    getLogger().critical(msg, *args, **kwargs)

def log(msg, *args, **kwargs):
    getLogger().log(msg, *args, **kwargs)

def exception(msg, *args):
    getLogger().exception(msg, *args)
