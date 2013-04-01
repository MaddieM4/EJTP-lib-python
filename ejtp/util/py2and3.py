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

class RawData(object):
    '''
    This class is supposed to store raw data and behaves similar to str in
    python 2.x and bytes in python 3.x
    '''
    def __init__(self, value=()):
        '''
        Takes an iterable value that should contain either integers in range(256)
        or corresponding characters.
        Some examples for working with RawData:

        >>> r = RawData('Hello world!')
        >>> r[0]
        RawData((0x48))
        >>> byte_tuple = (115, 101, 99, 114, 101, 116)
        >>> RawData(byte_tuple) == RawData('secret')
        True
        >>> RawData('Hello world!').toString()
        String('Hello world!')
        '''
        if isinstance(value, RawData):
            value = value._data
        else:
            if isinstance(value, int):
                value = (value,)
            if not (hasattr(value, '__iter__') or hasattr(value, '__getitem__')):
                raise TypeError('value must be iterable')
            if isinstance(value, bytes):
                # this makes sure that iterating over value gives one byte at a time
                # in python 2 and 3
                if bytes == str:
                    # in python 2 iterating over bytes gives characters instead of integers
                    value = tuple(map(ord, value))
                else:
                    # Only tuple-ify if not already tuple-ified by map above
                    value = tuple(value)
            elif bytes==str and isinstance(value, unicode):
                value = tuple(map(ord, value.encode('utf-8')))
            elif isinstance(value, str):
                # only python3 strings here
                value = tuple(value.encode('utf-8'))
            elif isinstance(value, String):
                value = value.toRawData()._data
            else:
                # maybe a list of ints?
                try:
                    value = tuple(map(int, value))
                except ValueError:
                    raise ValueError('values must be ints')

                for i in value:
                    if i < 0 or i > 255:
                        raise ValueError('values not in range(256)')

        self._data = value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return NotImplemented

    def __add__(self, other):
        if not isinstance(other, self.__class__):        
            try:
                other = self.__class__(other)
            except (TypeError, ValueError):
                return NotImplemented
        return self.__class__(self._data.__add__(other._data))
    
    def __len__(self):
        return self._data.__len__()

    def __getitem__(self, key):
        return self.__class__(self._data.__getitem__(key))

    def __contains__(self, key):
        try:
            key = self.__class__(key)
        except (TypeError, ValueError):
            return False
        if len(key) > 1:
            return False
        return self._data.__contains__(key._data[0])

    def __iter__(self):
        return self._data.__iter__()

    def __hash__(self):
        return self._data.__hash__()

    def __repr__(self):
        return 'RawData((' + ','.join(map(hex, self._data)) + '))'
    
    def __int__(self):
        '''
        Converts the data to an int if it contains exactly one byte.
        '''
        if self.__len__() != 1:
            raise TypeError('must be of length 1')
        return self._data[0]
    
    def index(self, byte):
        '''
        Returns index of byte in RawData.
        Raises ValueError if byte is not in RawData and TypeError if can't be
        converted RawData or its length is not 1.
        '''
        if not isinstance(byte, RawData):
            try:
                byte = self.__class__(byte)
            except (TypeError, ValueError):
                raise TypeError("can't convert byte to RawData")
        if len(byte) != 1:
            raise TypeError('byte must be of length 1')
        try:
            return self._data.index(byte._data[0])
        except ValueError:
            raise ValueError('byte not in RawData')

    def split(self, byte, maxsplit=-1):
        '''
        Splits RawData on every occurrence of byte.
        '''
        if (maxsplit == 0):
            return [self]
        try:
            ind = self.index(byte)
        except ValueError:
            return [self]
        return [self.__class__(self._data[:ind])] + self.__class__(self._data[ind+1:]).split(byte, maxsplit-1)

    def toString(self):
        return String(self.export().decode('utf-8'))
    
    def export(self):
        '''
        Returns the data as bytes() so that you can use it for methods that
        expect bytes. Don't use this for comparison!
        '''
        if bytes == str:
            return bytes().join(map(chr,self._data))
        return bytes(self._data)


class String(object):
    '''
    This class stores unicode strings and treats them depending on the python
    version.
    Some examples for working with String:

    >>> s = String('Hello world!')
    >>> s
    String('Hello world!')
    >>> s[:5]
    String('Hello')
    >>> s[:5].toRawData()
    RawData((0x48,0x65,0x6c,0x6c,0x6f))
    '''
    def __init__(self, string):
        '''
        Takes an string or RawData and converts it to unicode.
        '''
        if isinstance(string, String):
            self._data = string._data
        elif isinstance(string, RawData):
            try:
                self._data = string.toString()._data
            except UnicodeDecodeError:
                raise TypeError("can't convert RawData to String")
        elif isinstance(string, bytes):
            self._data = RawData(string).toString()._data
        elif (bytes == str):
            # python2 only here
            if not isinstance(string, unicode):
                raise TypeError('string must be of type str, unicode or RawData')
            self._data = string
        elif not isinstance(string, str):
            # python3 only here
            raise TypeError('string must be of type bytes, str or RawData')
        else:
            self._data = string

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self._data.__eq__(other._data)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self._data < other._data
        return NotImplemented

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            try:
                other = self.__class__(other)
            except TypeError:
                return NotImplemented
        return self.__class__(self._data.__add__(other._data))

    def __len__(self):
        return self._data.__len__()
    
    def __getitem__(self, key):
        return self.__class__(self._data.__getitem__(key))
    
    def __iter__(self):
        # in python2 unicode somehow only iterates with iter()
        if hasattr(self._data, '__iter__'):
            return self._data.__iter__()
        return iter(self._data)
  
    def __hash__(self):
        return self._data.__hash__()
      
    def __repr__(self):
        rep = self._data.__repr__()
        if rep[0] == 'u':
            # in python2 for unicode
            rep = rep[1:]
        return 'String(' + rep + ')'

    def index(self, substr):
        '''
        Returns index of substr in String.
        Raises ValueError if substr is not in String and TypeError if substr
        can't be converted to String.

        >>> s = String('abc')
        >>> s.index('bc')
        1
        >>> s.index(1)
        Traceback (most recent call last):
        TypeError: can't convert substr to String
        >>> s.index('d')
        Traceback (most recent call last):
        ValueError: substr not in String
        '''
        if not isinstance(substr, String):
            try:
                substr = self.__class__(substr)
            except TypeError:
                raise TypeError("can't convert substr to String")
        try:
            return self._data.index(substr._data)
        except ValueError:
            raise ValueError('substr not in String')
    
    def join(self, iterable):
        '''
        Joins the String with the iterable.
        Raises TypeError if iterable is not iterable or values can't be
        converted to String

        >>> String(',').join(('a', 'b', 'c')) == String('a,b,c')
        True
        '''

        try:
            return String(self._data.join((String(i)._data for i in iterable)))
        except TypeError:
            raise TypeError('iterable must be iterable of values that can be converted to String')
 
    def toRawData(self):
        return RawData(self._data.encode('utf-8'))
    
    def export(self):
        '''
        Returns unicode representation of the String. Don't use this for
        comparison since it depends on the python version how unicode strings
        are handled!
        '''
        return self._data


class DataDecorator(object):
    '''
    Base class for RawDataDecorator and StringDecorator.
    dec_args is a dictionary containing following keys with boolean values:
    args: tries to convert normal arguments
    kwargs: tries to convert keyword arguments
    ret: tries to convert returned value
    strict: raises exception if conversion fails
    '''

    _default_dec_args = {
        'args': True,
        'kwargs': False,
        'ret': False,
        'strict': False,
    }

    def __init__(self, **dec_args):
        for key in dec_args:
            if key not in self._default_dec_args:
                raise ValueError('keyword %s is not allowed' % key)
            if not isinstance(dec_args[key], bool):
                raise TypeError('keyword arguments must be boolean')
        self._dec_args = self._default_dec_args.copy()
        self._dec_args.update(dec_args)

    def __call__(self, func = None, *args, **kwargs):
        if hasattr(self, '_func'):
            # the instance will only be called twice, if func is not a method
            # so we just pass the arguments to _decoratedFunc here
            if func is not None:
                return self._decoratedFunc(self._func, *((func,)+args), **kwargs)
            return self._decoratedFunc(self._func, *args, **kwargs)
        self._func = func
        self._wrap_func(self, func)
        return self

    def __get__(self, instance, owner):
        # this method only gets called, if the decorated function is a method
        # so we have to make sure that instance will be included in the call
        from functools import partial
        return self._wrap_func(partial(self._decoratedFunc, partial(self._func, instance)), self._func)
    
    def _wrap_func(self, wrapper, func):
        '''
        Wraps the original function in the decorator.
        '''
        from functools import update_wrapper
        return update_wrapper(wrapper, func, updated=())
    
    def _decoratedFunc(self, *args, **kwargs):
        raise NotImplementedError('this method must be implemented by subclasses')
 
class RawDataDecorator(DataDecorator):
    '''
    Tries to parse arguments into RawData.

    >>> @RawDataDecorator()
    ... def test(a, b):
    ...     print(a)
    ...
    >>> test('abc', 123)
    RawData((0x61,0x62,0x63))
    >>> test(1234, 'Hello world!')
    1234
    >>> @RawDataDecorator(args=False, kwargs=True, strict=True)
    ... def test(a = 123, b = 'abc'):
    ...     print(b)
    ...
    >>> test(b = 'ab')
    RawData((0x61,0x62))
    >>> test(b = 1234) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...
    >>> @RawDataDecorator(args=False, ret=True)
    ... def test():
    ...     return 'abc'
    ...
    >>> test()
    RawData((0x61,0x62,0x63))
    '''
    def _decoratedFunc(self, func, *args, **kwargs):
        if self._dec_args['args']:
            newargs = []
            for arg in args:
                if not isinstance(arg, RawData):
                    try:
                        newargs.append(RawData(arg))
                    except (TypeError, ValueError):
                        if self._dec_args['strict']:
                            raise TypeError("can't convert arg %i to RawData" % args.index(arg))
                        newargs.append(arg)
                else:
                    newargs.append(arg)
            args = tuple(newargs)
        if self._dec_args['kwargs']:
            for key in kwargs:
                if not isinstance(kwargs[key], RawData):
                    try:
                        kwargs[key] = RawData(kwargs[key])
                    except (TypeError, ValueError):
                        if self._dec_args['strict']:
                            raise TypeError("can't convert kwarg %s to RawData" % key)
        
        if self._dec_args['ret']:
            ret = func(*args, **kwargs)
            if not isinstance(ret, RawData):
                try:
                    ret = RawData(ret)
                except (TypeError, ValueError):
                    if self._dec_args['strict']:
                        raise TypeError("can't convert return value to RawData")
            return ret
        return func(*args, **kwargs)

class StringDecorator(DataDecorator):
    '''
    Tries to parse arguments into String.

    >>> @StringDecorator()
    ... def test(a, b):
    ...     print(a)
    ...
    >>> test('Hello world!', 123)
    String('Hello world!')
    >>> test(123, 'Hello world!')
    123
    >>> @StringDecorator(args=False, kwargs=True, strict=True)
    ... def test(a = 'Hello world!', b = '123'):
    ...     print(b)
    ...
    >>> test(b = 'abc')
    String('abc')
    >>> test(b = 123) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...
    >>> @StringDecorator(args=False, ret=True)
    ... def test():
    ...     return 'abc'
    ...
    >>> test()
    String('abc')
    '''
    def _decoratedFunc(self, func, *args, **kwargs):
        if self._dec_args['args']:
            newargs = []
            for arg in args:
                if not isinstance(arg, String):
                    try:
                        newargs.append(String(arg))
                    except TypeError:
                        if self._dec_args['strict']:
                            raise TypeError("can't convert arg %i to String" % args.index(arg))
                        newargs.append(arg)
                else:
                    newargs.append(arg)
            args = tuple(newargs)
        if self._dec_args['kwargs']:
            for key in kwargs:
                if not isinstance(kwargs[key], String):
                    try:
                        kwargs[key] = String(kwargs[key])
                    except TypeError:
                        if self._dec_args['strict']:
                            raise TypeError("can't convert kwarg %s to String" % key)

        if self._dec_args['ret']:
            ret = func(*args, **kwargs)
            if not isinstance(ret, String):
                try:
                    ret = String(ret)
                except TypeError:
                    if self._dec_args['strict']:
                        raise TypeError("can't convert return value to String")
            return ret
        return func(*args, **kwargs)

def JSONBytesEncoder(python_object):
    if isinstance(python_object, bytes):
        return String(python_object).export()
    raise TypeError(repr(python_object) + ' is not JSON serializable')
