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

        >>> repr(RawData((1, 2, 3))) == 'RawData(010203)'
        True
        >>> repr(RawData('abc')) == 'RawData(616263)'
        True
        >>> repr(RawData(String('abc'))) == 'RawData(616263)'
        True
        '''
        if isinstance(value, int):
            value = (value,)
        try:
            iter(value)
        except TypeError:
            raise TypeError('value must be iterable')
        if isinstance(value, bytes):
            # this makes sure that iterating over value gives one byte at a time
            # in python 2 and 3
            if bytes == str:
                # in python 2 iterating over bytes gives characters instead of integers
                value = (ord(c) for c in value)
            value = tuple(value)
        elif isinstance(value, str) or (bytes==str and isinstance(value, unicode)):
            # only unicode strings will get here
            value = tuple(value.encode('utf-8'))
        elif isinstance(value, String):
            value = value.toRawData()._data
        else:
            # maybe a list of ints?
            try:
                value = tuple((int(i) for i in value))
            except ValueError:
                raise ValueError('values must be ints')

            for i in value:
                if i < 0 or i > 255:
                    raise ValueError('values not in range(256)')

        self._data = value

    def __eq__(self, other):
        '''
        >>> RawData('abc') == RawData((97, 98, 99))
        True
        >>> RawData('abc') == 'abc'
        False
        '''
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return NotImplemented

    def __add__(self, other):
        '''
        >>> RawData('ab') + RawData('c') == RawData('ab') + 99 == RawData('abc')
        True
        >>> RawData('ab') + object() # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        TypeError: unsupported operand type(s) for +: 'RawData' and 'object'
        '''
        if not isinstance(other, self.__class__):        
            try:
                other = self.__class__(other)
            except (TypeError, ValueError):
                return NotImplemented
        return self.__class__(self._data.__add__(other._data))
    
    def __len__(self):
        '''
        >>> len(RawData('ab')) == 2
        True
        '''
        return self._data.__len__()

    def __getitem__(self, key):
        '''
        >>> RawData('ab')[1] == RawData('b')
        True
        '''
        return self.__class__(self._data.__getitem__(key))

    def __iter__(self):
        '''
        >>> for c in RawData('abc'):
        ...     print(c)
        ...
        97
        98
        99
        '''
        return self._data.__iter__()

    def __repr__(self):
        '''
        >>> repr(RawData('abc')) == 'RawData(616263)'
        True
        '''
        return 'RawData(' + str().join([format(c, '02x') for c in self._data]) + ')'
    
    def __int__(self):
        '''
        Converts the data to an int if it contains exactly one byte.

        >>> int(RawData('a')) == 97
        True
        >>> int(RawData('abc'))
        Traceback (most recent call last):
        TypeError: must be of length 1
        '''
        if self.__len__() != 1:
            raise TypeError('must be of length 1')
        return self._data[0]
     
    def toString(self):
        '''
        >>> RawData('abc').toString() == String('abc')
        True
        '''
        return String(self.export().decode('utf-8'))
    
    def export(self):
        '''
        Returns the data as bytes() so that you can use it for methods that
        expect bytes. Don't use this for comparison!

        >>> RawData(RawData('abc').export()) == RawData('abc')
        True
        '''
        if bytes == str:
            return bytes().join(chr(c) for c in self._data)
        return bytes(self._data)


class String(object):
    '''
    This class stores unicode strings and treats them depending on the python
    version.
    '''
    def __init__(self, string):
        '''
        Takes an string or RawData and converts it to unicode.
        '''

        if isinstance(string, RawData):
            string = string.toString()._data
        if isinstance(string, bytes):
            string = RawData(string).toString()._data
        elif (bytes == str):
            # python2 only here
            if not isinstance(string, unicode):
                raise TypeError('string must be of type str, unicode or RawData')
        elif not isinstance(string, str):
            # python3 only here
            raise TypeError('string must be of type bytes, str or RawData')
        self._data = string

    def __eq__(self, other):
        '''
        >>> String('abc') == String(RawData((97, 98, 99)))
        True
        >>> String('abc') == 'abc'
        False
        '''
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return NotImplemented

    def __add__(self, other):
        '''
        >>> String('a') + String('b') == String('ab')
        True
        >>> String('a') + 'b' == String('ab')
        True
        >>> String('a') + RawData(98) == String('ab')
        True
        >>> String('abc') + object() # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        TypeError: unsupported operand type(s) for +: 'RawData' and 'object'
        '''
        if not isinstance(other, self.__class__):
            try:
                other = self.__class__(other)
            except TypeError:
                return NotImplemented
        return self.__class__(self._data.__add__(other._data))

    def __len__(self):
        '''
        >>> len(String('abc')) == 3
        True
        '''
        return self._data.__len__()
    
    def __getitem__(self, key):
        '''
        >>> String('abc')[1] == String('b')
        True
        '''
        return self.__class__(self._data.__getitem__(key))
    
    def __iter__(self):
        '''
        >>> val = True
        >>> for c in String('aaa'):
        ...     val &= (c == 'a')
        ...
        >>> val
        True
        '''
        # in python2 unicode somehow only iterates with iter()
        if hasattr(self._data, '__iter__'):
            return self._data.__iter__()
        return iter(self._data)
    
    def __repr__(self):
        '''
        >>> repr(String('abc')) == "String('abc')"
        True
        '''
        rep = self._data.__repr__()
        if rep[0] == 'u':
            # in python2 for unicode
            rep = rep[1:]
        return 'String(' + rep + ')'

    def toRawData(self):
        '''
        >>> String('abc').toRawData() == RawData('abc')
        True
        '''
        return RawData(self._data.encode('utf-8'))
    
    def export(self):
        '''
        Returns unicode representation of the String. Don't use this for
        comparison since it depends on the python version how unicode strings
        are handled!

        >>> String(String('abc').export()) == String('abc')
        True
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
        return self

    def _decoratedFunc(self, *args, **kwargs):
        raise NotImplementedError('this method must be implemented by subclasses')
    
    def __get__(self, instance, owner):
        # this method only gets called, if the decorated function is a method
        # so we have to make sure that instance will be included in the call
        from functools import partial
        return partial(self._decoratedFunc, partial(self._func, instance))

class RawDataDecorator(DataDecorator):
    '''
    Tries to parse arguments into RawData.

    >>> @RawDataDecorator()
    ... def test(a, b):
    ...     print(a)
    ...
    >>> test('abc', 123)
    RawData(616263)
    >>> test(1234, 'Hello world!')
    1234
    >>> @RawDataDecorator(args=False, kwargs=True, strict=True)
    ... def test(a = 123, b = 'abc'):
    ...     print(b)
    ...
    >>> test(b = 'ab')
    RawData(6162)
    >>> test(b = 1234) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...
    >>> @RawDataDecorator(args=False, ret=True)
    ... def test():
    ...     return 'abc'
    ...
    >>> test()
    RawData(616263)
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

