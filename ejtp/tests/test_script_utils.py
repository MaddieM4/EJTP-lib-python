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

from ejtp.util.compat import unittest
from ejtp.tests.test_scripts import IOMock

from ejtp.util.scripts import *

class TestScriptUtils(unittest.TestCase):
    def setUp(self):
        self.io = IOMock()

    def test_confirm(self):
        items = ['somestr', 21, 55]
        def get_item():
            item = items.pop(0)
            try:
                item = int(item)
            except:
                raise ValueError("Not int-able")
            return item

        with self.io:
            self.io.append('n')
            self.io.append('y')
            result = confirm(get_item, "Your value is %r")
            self.assertEqual(result, 55)
        self.assertEqual(self.io.get_lines(), [
            "Invalid input: ValueError('Not int-able',)",
            'Your value is 21',
            'Is this correct? [y/n]',
            '$ n',
            'Your value is 55',
            'Is this correct? [y/n]',
            '$ y',
        ])

    def test_choose(self):
        items = {
            'thing1': 't1 Description',
            'thing2': 't2 Description',
            'thing3': 't3 Description',
            'thing4': 't4 Description',
        }
        singular = 'thing'
        plural   = 'things'
        with self.io:
            self.io.extend(['notinlist','still not in list', 'thing3'])
            result = choose(items, singular, plural)
            self.assertEqual(result, 'thing3')
        self.maxDiff = None
        list_options = [
            'The following things are available:',
            'thing1 : t1 Description',
            'thing2 : t2 Description',
            'thing3 : t3 Description',
            'thing4 : t4 Description',
            'Which thing do you want?',
        ]
        self.assertEqual(self.io.get_lines(), 
            list_options +
            ['$ notinlist'] +
            list_options +
            ['$ still not in list'] +
            list_options +
            ['$ thing3']
        )
