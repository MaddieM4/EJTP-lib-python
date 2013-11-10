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
import tempfile

from ejtp.util.compat import unittest
from ejtp.tests.test_scripts import IOMock
from ejtp.identity import Identity

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

    def test_retry(self):
        def callback(data):
            if data != "good": raise ValueError("Not 'good'!")
            return data

        with self.io:
            self.io.extend(['bad', 'also bad', 'good'])
            result = retry("Good or bad?", callback)
            self.assertEqual(result, 'good')
        self.assertEqual(self.io.get_lines(), [
            'Good or bad?',
            '$ bad',
            "ValueError: Not 'good'!",
            'Good or bad?',
            '$ also bad',
            "ValueError: Not 'good'!",
            'Good or bad?',
            '$ good',
        ])

    def test_retrying_save(self):
        _, writeable_fn = tempfile.mkstemp()
        _, nowrite_fn   = tempfile.mkstemp()
        os.chmod(nowrite_fn, 0o444) # No write

        filecontents = 'Hello, world!'
        def write(fname):
            open(fname, 'w').write(filecontents)

        with self.io:
            self.io.extend([nowrite_fn, writeable_fn])
            retry("What file name?", write)
        self.assertEqual(
            [
                line.replace('PermissionError', 'IOError')
                for line in self.io.get_lines()
            ],
            [
                'What file name?',
                '$ ' + nowrite_fn,
                'IOError: [Errno 13] Permission denied: \'%s\'' % nowrite_fn,
                'What file name?',
                '$ ' + writeable_fn,
            ]
        )

    def test_get_identity(self):
        '''
        Tries to overlap minimally with more specific tests, except for
        the encryptor retry mechanism, which is specific to get_identity
        and must not kill the process during encryptor creation failure.
        '''
        with self.io:
            self.io.extend([
                'boomer@galactica.gov',
                'y',
                'local',
                'athena',
                'y',
                'y',
                'rsa',
                '120',
                'y',
                'rotate',
                '120',
                'y',
            ])
            result = get_identity()
            expected_ident = Identity(
                'boomer@galactica.gov',
                ['rotate', 120],
                ['local', None, 'athena']
            )
            self.assertEqual(result, expected_ident)
        lines = self.io.get_lines()
        expected_beginning = [
            'NOTE: If you intend to host this identity in the DJDNS',
            'registry, the email domain needs to match your branch',
            'regex to be accessible.',
            'http://roaming-initiative.com/blog/blog/djdns-ident-registration.html',
            'Your identity name, in email form:',
            '$ boomer@galactica.gov',
            "The name you chose: 'boomer@galactica.gov'",
            'Is this correct? [y/n]',
            '$ y',
            'The following types are available:',
            'local : Can only communicate within a single OS process',
            'tcp : IPv6 address, accessed over TCP',
            'tcp4 : IPv4 address, accessed over TCP',
            'udp : IPv6 address, accessed over UDP',
            'udp4 : IPv4 address, accessed over UDP',
            'Which type do you want?',
            '$ local',
            'Your callsign:',
            '$ athena',
            'Is this correct? [y/n]',
            '$ y',
            'Your location is:',
            "['local', None, 'athena']",
            'Is this correct? [y/n]',
            '$ y',
            'Now we generate your encryptor.',
            'The following types are available:',
            'rotate : Only for trivial demos, not recommended!',
            'rsa : RSA Public-Key encryption (recommended)',
            'Which type do you want?',
            '$ rsa',
            'How many bits?',
            '$ 120',
            'Is this correct? [y/n]',
            '$ y',
            'Generating... if it takes awhile, wiggle your mouse.',
        ]
        # Intentionally ignore the env-specific Crypto traceback
        expected_end = [
            "AttributeError: 'NoneType' object has no attribute 'exportKey'",
            'The following types are available:',
            'rotate : Only for trivial demos, not recommended!',
            'rsa : RSA Public-Key encryption (recommended)',
            'Which type do you want?',
            '$ rotate',
            'How much to rotate?',
            '$ 120',
            'Is this correct? [y/n]',
            '$ y',
        ]
        self.assertEqual(lines[:len(expected_beginning)], expected_beginning)
        self.assertEqual(lines[-len(expected_end):], expected_end)

    def test_get_name(self):
        with self.io:
            self.io.extend([
                'notanemail',
                'yesanemail@domain.net',
            ])
            self.assertRaises(ValueError, get_name)
            self.assertEquals(get_name(), 'yesanemail@domain.net')
        self.assertEqual(self.io.get_lines(), [
            'Your identity name, in email form:',
            '$ notanemail',
            'Your identity name, in email form:',
            '$ yesanemail@domain.net',
        ])

    def test_get_location(self):
        ip   = '81.21.42.96'
        port = 9999
        call = 'somecallsign'
        with self.io:
            self.io.extend([
                # First demo local
                'local',
                call,
                'yes',
                # then demo an address-taking ltype.
                'tcp4',
                ip,
                str(port),
                'yes',
                call,
                'yes',
            ])
            local = get_location()
            tcp4  = get_location()
            self.assertEquals(local, ['local', None, call])
            self.assertEquals(tcp4 , ['tcp4', [ip,port], call])
        self.assertEqual(self.io.get_lines(), [
            'The following types are available:',
            'local : Can only communicate within a single OS process',
            'tcp : IPv6 address, accessed over TCP',
            'tcp4 : IPv4 address, accessed over TCP',
            'udp : IPv6 address, accessed over UDP',
            'udp4 : IPv4 address, accessed over UDP',
            'Which type do you want?',
            '$ local',
            'Your callsign:',
            '$ somecallsign',
            'Is this correct? [y/n]',
            '$ yes',
            'The following types are available:',
            'local : Can only communicate within a single OS process',
            'tcp : IPv6 address, accessed over TCP',
            'tcp4 : IPv4 address, accessed over TCP',
            'udp : IPv6 address, accessed over UDP',
            'udp4 : IPv4 address, accessed over UDP',
            'Which type do you want?',
            '$ tcp4',
            'Your IP address, at which you can be contacted:',
            '$ 81.21.42.96',
            'Port at which you are reachable:',
            '$ 9999',
            "Address = ['81.21.42.96', 9999]",
            'Is this correct? [y/n]',
            '$ yes',
            'Your callsign:',
            '$ somecallsign',
            'Is this correct? [y/n]',
            '$ yes'
        ])

    def test_get_addr(self):
        with self.io:
            self.io.extend(['a','b','c','5'])
            self.assertRaises(ValueError, get_addr)
            self.assertEquals(get_addr(), ['c', 5])
        self.assertEqual(self.io.get_lines(), [
            'Your IP address, at which you can be contacted:',
            '$ a',
            'Port at which you are reachable:',
            '$ b',
            'Your IP address, at which you can be contacted:',
            '$ c',
            'Port at which you are reachable:',
            '$ 5',
        ])

    def test_get_callsign(self):
        with self.io:
            callsign = "some callsign"
            self.io.append(callsign)
            self.assertEqual(callsign, get_callsign())
        self.assertEqual(self.io.get_lines(), [
            'Your callsign:',
            '$ ' + callsign,
        ])

    def test_get_encryptor_rotate(self):
        with self.io:
            self.io.extend([
                'rotate',
                'not an int',
                '-7',
                'n',
                '97',
                'y',
            ])
            self.assertEquals(get_encryptor(), ['rotate', 97])
        self.assertEqual(self.io.get_lines(), [
            'The following types are available:',
            'rotate : Only for trivial demos, not recommended!',
            'rsa : RSA Public-Key encryption (recommended)',
            'Which type do you want?',
            '$ rotate',
            'How much to rotate?',
            '$ not an int',
            'Invalid input: ValueError("invalid literal for int() with base 10: \'not an int\'",)',
            'How much to rotate?',
            '$ -7',
            'Is this correct? [y/n]',
            '$ n',
            'How much to rotate?',
            '$ 97',
            'Is this correct? [y/n]',
            '$ y',
        ])

    def test_get_encryptor_rsa_bad_bitscount(self):
        with self.io:
            self.io.extend([
                'rsa',
                'not an int',
                '-7',
                'n',
                '97',
                'y',
            ])
            self.assertRaises(ValueError, get_encryptor)
        lines = self.io.get_lines()
        expected_beginning = [
            'The following types are available:',
            'rotate : Only for trivial demos, not recommended!',
            'rsa : RSA Public-Key encryption (recommended)',
            'Which type do you want?',
            '$ rsa',
            'How many bits?',
            '$ not an int',
            'Invalid input: ValueError("invalid literal for int() with base 10: \'not an int\'",)',
            'How many bits?',
            '$ -7',
            'Is this correct? [y/n]',
            '$ n',
            'How many bits?',
            '$ 97',
            'Is this correct? [y/n]',
            '$ y',
            'Generating... if it takes awhile, wiggle your mouse.',
        ]
        expected_end = [
            "AttributeError: 'NoneType' object has no attribute 'exportKey'",
        ]
        self.assertEqual(lines[:len(expected_beginning)], expected_beginning)
        self.assertEqual(lines[-len(expected_end):], expected_end)

    def test_get_encryptor_rsa_good_bitscount(self):
        with self.io:
            self.io.extend([
                'rsa',
                '1024',
                'y',
            ])
            result = get_encryptor()
            self.assertEquals(len(result), 2)
            self.assertEquals(result[0], 'rsa')
            self.assertIn('PRIVATE KEY', str(result[1]))
        self.maxDiff = None
        self.assertEqual(self.io.get_lines(), [
            'The following types are available:',
            'rotate : Only for trivial demos, not recommended!',
            'rsa : RSA Public-Key encryption (recommended)',
            'Which type do you want?',
            '$ rsa',
            'How many bits?',
            '$ 1024',
            'Is this correct? [y/n]',
            '$ y',
            'Generating... if it takes awhile, wiggle your mouse.',
        ])
