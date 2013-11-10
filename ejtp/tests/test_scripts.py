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
import imp
import sys
import json
import tempfile
import time
import subprocess

from ejtp.util.compat import unittest
from ejtp.tests.resource_path import *

ENV_VAR = 'EJTP_IDENTITY_CACHE_PATH'

def set_environ():
    ident_cache_path = testing_path('examplecache.json')
    os.environ[ENV_VAR] = ident_cache_path

def import_as_module(script_name):
    filename = script_path(script_name)
    with open(filename, 'rb') as fp:
        module = imp.new_module(script_name)
        exec(fp.read(), module.__dict__)
        return module

class IOMockStream(object):
    def __init__(self, parent, lines=None):
        self.parent = parent
        self.lines  = lines or []

    def readline(self):
        _input = self.lines.pop(0)
        self.parent._stream.append('$ ' + _input)
        return _input

    def read(self):
        text = '\n'.join(self.lines)
        return text

    def write(self, text):
        _output = text.strip().split('\n')
        self.parent._stream.extend(_output)
        self.lines.extend(_output)

class IOMock(object):

    def __init__(self):
        self._stream = []
        self.input   = IOMockStream(self)
        self.output  = IOMockStream(self)
        self.error   = IOMockStream(self)

    def append(self, value):
        self.input.lines.append(value)

    def extend(self, value):
        self.input.lines.extend(value)

    def __enter__(self):
        sys.stdin  = self.input
        sys.stdout = self.output
        sys.stderr = self.error

    def __exit__(self, type, value, traceback):
        sys.stdin  = sys.__stdin__
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def get_lines(self):
        return [line for line in self._stream if line]

    def get_value(self):
        return '\n'.join(self.get_lines())

    def pipe(self):
        self._stream = []
        self.input   = self.output
        self.output  = IOMockStream(self)
        self.error   = IOMockStream(self)

    def clear(self):
        self._stream = []
        self.input   = IOMockStream(self)
        self.output  = IOMockStream(self)
        self.error   = IOMockStream(self)

class IOAssert(object):
    def __init__(self, testcase, expected):
        self.testcase = testcase
        self.expected = expected

    def __enter__(self):
        self.extend()
        self.io.__enter__()

    def __exit__(self, type, value, traceback):
        if traceback == None:
            self.validate()
        return self.io.__exit__(type, value, traceback)

    def validate(self):
        for pair in zip(self.lines_expected, self.io.get_lines()):
            if pair[0].startswith('$'):
                self.testcase.assertEqual(*pair)
            else:
                self.testcase.assertIn(*pair)

    def extend(self):
        self.io.extend([
            line[2:] for line in self.lines_expected
            if line.startswith('$')
        ])

    @property
    def io(self):
        return self.testcase.io

    @property
    def lines_expected(self):
        return [line.strip() for line in self.expected.strip().split('\n')]

class TestConsole(unittest.TestCase):

    def setUp(self):
        set_environ()
        self.io = IOMock()
        self.console = import_as_module('ejtp-console')
        self.inter = self.console.Interactive()

    def _assertCLI(self, expected):
        with IOAssert(self, expected):
            self.assertRaises(SystemExit, self.inter.repl)

    def test_quit(self):
        expected = '''
        What interface do you want to use?
        Available interfaces:
        $ mitzi@lackadaisy.com
        Enter a command
        $ quit
        '''
        self._assertCLI(expected)

    def test_eval(self):
        expected = '''
        What interface do you want to use?
        Available interfaces:
        $ mitzi@lackadaisy.com
        Enter a command
        $ eval
        $ 2 ** 10
        1024
        Enter a command
        $ quit
        '''
        self._assertCLI(expected)

    def test_messages(self):
        expected = '''
        What interface do you want to use?
        Available interfaces:
        $ mitzi@lackadaisy.com
        Enter a command
        $ send
        What interface do you want to send to?
        Available interfaces:
        $ mitzi@lackadaisy.com
        What message do you want to send?
        $ "one message"
        Enter a command
        $ messages
        All messages
        ------------
        mitzi@lackadaisy.com
        "one message"
        Enter a command
        $ quit
        '''
        self._assertCLI(expected)

    def test_set_client(self):
        expected = '''
        What interface do you want to use?
        Available interfaces:
        $ mitzi@lackadaisy.com
        Enter a command
        $ set client
        What interface do you want to use?
        Available interfaces:
        $ victor@lackadaisy.com
        Enter a command
        $ quit
        '''
        self._assertCLI(expected)


class TestCrypto(unittest.TestCase):

    def setUp(self):
        set_environ()
        self.crypto = import_as_module('ejtp-crypto')
        self.io = IOMock()


    def _test_encode_decode(self, text, id_=None, with_=None):
        if id_:
            args = ['id', id_]
        elif with_:
            args = ['with', with_]

        argv = ['ejtp-crypto', 'encode'] + args
        self.io.append(text)
        with self.io:
            self.crypto.main(argv)

        argv = ['ejtp-crypto', 'decode'] + args
        self.io.pipe()
        with self.io:
            self.crypto.main(argv)

        self.assertEqual(text, self.io.get_value())

    def test_encode_decode_id(self):
        self._test_encode_decode(text='banana', id_='mitzi@lackadaisy.com')

    def test_encode_decode_with(self):
        self._test_encode_decode(text='banana', with_='["rsa","-----BEGIN RSA PRIVATE KEY-----\\nMIICXAIBAAKBgQDAZQNip0GPxFZsyxcgIgyvuPTHsruu66DBsESG5/Pfbcye3g4W\\nwfg+dBP3IfUnLB4QXGzK42BAd57fCBXOtalSOkFoze/C2q74gYFBMvIPbEfef8yQ\\n83uoNkYAFBVp6yNlT51IQ2mY19KpqoyxMZftxwdtImthE5UG1knZE64sIwIDAQAB\\nAoGAIGjjyRqj0LQiWvFbU+5odLGTipBxTWYkDnzDDnbEfj7g2WJOvUavqtWjB16R\\nDahA6ECpkwP6kuGTwb567fdsLkLApwwqAtpjcu96lJpbRC1nq1zZjwNB+ywssqfV\\nV3R2/rgIEE6hsWS1wBHufJeqBZtlkeUp/VEx/uopyuR/WgECQQDJOaFSutj1q1dt\\nNO23Q6w3Ie4uMQ59rWeRxXA5+KjDZCxrizzo/Bew5ZysJzHB2n8QQ15WJ7gTSjwJ\\nMQdl/7SJAkEA9MQG/6JivkhUNh45xMYqnMHuutyIeGE17QndSfknU+8CX9UBLjsL\\nw1QU+llJ3iYfMPEDaydn0HJ8+iinyyAISwJAe7Z2vEorwT5KTdXQoG92nZ66tKNs\\naVAG8NQWH04FU7tuo9/C3uq+Ff/UxvKB4NDYdcM1aHqa7SEir/P4vHjtIQJAFKc9\\n1/BB2MCNqoteYIZALj4HAOl+8nlxbXD5pTZK5UAzuRZmJRqCYZcEtiM2onIhC6Yq\\nna4Tink+pnUrw24OhQJBAIjujQS5qwOf2p5yOqU3UYsBv7PS8IitmYFARTlcYh1G\\nrmcIPHRtkxIwNuFxy3ZRRPEDGFa82id5QHUJT8sJbqY=\\n-----END RSA PRIVATE KEY-----"]')

    def test_test_encode_decode_from_file(self):
        argv = ['ejtp-crypto', 'encode', 'id', 'mitzi@lackadaisy.com']
        self.io.append('banana')
        with self.io:
            self.crypto.main(argv)

        tmp = tempfile.mktemp()
        with open(tmp, 'w') as f:
            f.write(self.io.get_value())

        argv = ['ejtp-crypto', 'decode', 'id', 'mitzi@lackadaisy.com', '-f', tmp]
        self.io.clear()
        with self.io:
            self.crypto.main(argv)

        self.assertEqual('banana', self.io.get_value())

    def test_signature(self):
        argv = ['ejtp-crypto', 'sign', 'id', 'mitzi@lackadaisy.com']
        self.io.append('banana')
        with self.io:
            self.crypto.main(argv)

        tmp = tempfile.mktemp()
        with open(tmp, 'w') as f:
            f.write(self.io.get_value())

        argv = ['ejtp-crypto', 'sig-verify', 'id', 'mitzi@lackadaisy.com', '--sigfile', tmp]
        self.io.clear()
        self.io.append('banana')
        with self.io:
            self.crypto.main(argv)

        self.assertEqual('True', self.io.get_value())


class TestIdentity(unittest.TestCase):

    def _run(self, command, *args, **kwargs):
        argv = ['ejtp-identity']
        argv.append(command)
        argv.extend(args)
        with self.io:
            try:
                self.identity.main(argv)
            except SystemExit:
                if not kwargs.get('error'):
                    raise
        return self.io.get_value()

    def _tmp_file_with_env_cache(self):
        _, fname = tempfile.mkstemp()
        with open(fname, 'w') as f:
            f.write(open(os.environ[ENV_VAR]).read())
        return fname

    def setUp(self):
        set_environ()
        self.identity = import_as_module('ejtp-identity')
        self.io = IOMock()

    def test_list(self):
        records = self._run('list').strip().split('\n')
        for name in ('mitzi', 'victor', 'atlas'):
            self.assertIn(name + '@lackadaisy.com (rsa)', records)

    def test_list_by_file(self):
        records = self._run('list', '--by-file').strip().split('\n')
        self.assertIn('examplecache.json', records[0])
        for name in ('mitzi', 'victor', 'atlas'):
            self.assertIn(name + '@lackadaisy.com (rsa)', records)

    def test_details(self):
        data = json.loads(self._run('details', 'mitzi@lackadaisy.com'))
        self.assertEqual('mitzi@lackadaisy.com', data['name'])
        encryptor = data['encryptor']
        self.assertEqual('rsa', encryptor[0])
        self.assertTrue(encryptor[1].startswith('-----BEGIN RSA PRIVATE KEY-----'))

    def test_details_multi(self):
        atlas = self._run('details', 'atlas@lackadaisy.com')
        self.io.clear()
        mitzi = self._run('details', 'mitzi@lackadaisy.com')
        self.io.clear()
        both  = self._run('details', 'mitzi@lackadaisy.com', 'atlas@lackadaisy.com')
        self.assertIn(atlas, both)
        self.assertIn(mitzi, both)

    def test_details_export(self):
        dict_data = json.loads(self._run('details', 'mitzi@lackadaisy.com', '-e'))
        self.assertIsInstance(dict_data, dict)
        self.assertEqual(1, len(dict_data))
        location, data = list(dict_data.items())[0]
        self.assertEqual('["local",null,"mitzi"]', location)
        self.assertEqual('mitzi@lackadaisy.com', data['name'])
        encryptor = data['encryptor']
        self.assertEqual('rsa', encryptor[0])
        self.assertTrue(encryptor[1].startswith('-----BEGIN RSA PRIVATE KEY-----'))

    def test_details_multi_export(self):
        atlas = json.loads(self._run('details', 'atlas@lackadaisy.com'))
        self.io.clear()
        mitzi = json.loads(self._run('details', 'mitzi@lackadaisy.com'))
        self.io.clear()
        both  = json.loads(self._run('details', '-e', 'mitzi@lackadaisy.com', 'atlas@lackadaisy.com'))
        self.assertIsInstance(both, dict)
        self.assertEqual(both['["local",null,"atlas"]'], atlas)
        self.assertEqual(both['["local",null,"mitzi"]'], mitzi)

    def test_details_public(self):
        data = json.loads(self._run('details', 'mitzi@lackadaisy.com', '--public'))
        self.assertEqual('mitzi@lackadaisy.com', data['name'])
        encryptor = data['encryptor']
        self.assertEqual('rsa', encryptor[0])
        self.assertTrue(encryptor[1].startswith('-----BEGIN PUBLIC KEY-----'))

    def test_new_identity_with_required_parameters(self):
        output = self._run('new',
            '--name=freckle@lackadaisy.com',
            '--location=["local", null, "freckle"]',
            '--encryptor=["rotate", 5]')
        data = json.loads(output)['["local",null,"freckle"]']
        self.assertEqual('freckle@lackadaisy.com', data['name'])
        self.assertEqual(['local', None, 'freckle'], data['location'])
        self.assertEqual(['rotate', 5], data['encryptor'])

    def test_list_with_cache_source(self):
        _, fname = tempfile.mkstemp()
        output = self._run('new',
            '--name=freckle@lackadaisy.com',
            '--location=["local", null, "freckle"]',
            '--encryptor=["rotate", 5]')
        with open(fname, 'w') as f:
            f.write(output)
        self.io.clear()
        output = self._run('list', '--cache-source=' + fname)
        self.assertEqual('freckle@lackadaisy.com (rotate)', output)

    def test_new_interactive(self):
        _, fname = tempfile.mkstemp()
        expected = '''
        NOTE: If you intend to host this identity in the DJDNS
        registry, the email domain needs to match your branch
        regex to be accessible.
        http://roaming-initiative.com/blog/blog/djdns-ident-registration.html
        Your identity name, in email form:
        $ boomer@galactica.gov
        The name you chose: 'boomer@galactica.gov'
        Is this correct? [y/n]
        $ y
        The following types are available:
        local : Can only communicate within a single OS process
        tcp : IPv6 address, accessed over TCP
        tcp4 : IPv4 address, accessed over TCP
        udp : IPv6 address, accessed over UDP
        udp4 : IPv4 address, accessed over UDP
        Which type do you want?
        $ local
        Your callsign:
        $ athena
        Is this correct? [y/n]
        $ y
        Your location is:
        ['local', None, 'athena']
        Is this correct? [y/n]
        $ y
        Now we generate your encryptor.
        The following types are available:
        rotate : Only for trivial demos, not recommended!
        rsa : RSA Public-Key encryption (recommended)
        Which type do you want?
        $ rotate
        How much to rotate?
        $ 120
        Is this correct? [y/n]
        $ y
        Your full identity is:
        {
            "encryptor": [
                "rotate",
                120
            ],
            "location": [
                "local",
                null,
                "athena"
            ],
            "name": "boomer@galactica.gov"
        }
        Is this correct? [y/n]
        $ y
        File location to save your new cache? 
        $ %s
        Congratulations!
        ''' % fname
        with IOAssert(self, expected):
            self._run('new-interactive')
        written = open(fname, 'r').read()
        self.assertEqual(written.replace(' \n','\n'), '''{
  "[\\"local\\",null,\\"athena\\"]": {
    "encryptor": [
      "rotate",
      120
    ],
    "location": [
      "local",
      null,
      "athena"
    ],
    "name": "boomer@galactica.gov"
  }
}''')

    def test_merge_files(self):
        fname = self._tmp_file_with_env_cache()
        self._run('new',
            '--name=freckle@lackadaisy.com',
            '--location=["local", null, "freckle"]',
            '--encryptor=["rotate", 5]')
        self.io.pipe()
        self._run('merge', fname)

        with open(fname, 'r') as f:
            data = json.load(f)
        self.assertEqual(4, len(data))

    def test_dl(self):
        '''
        Need to run local webserver for this test.
        '''
        # run server
        if int(sys.version[0]) == 2:
            server_module = 'SimpleHTTPServer'
        elif int(sys.version[0]) == 3:
            server_module = 'http.server'
        else:
            raise Exception("Unknown Python version")

        port = 8888
        args = ['python', '-m' + server_module, str(port)]
        webserver = subprocess.Popen(
            args,
            cwd='ejtp/tests',
            # Suppress output
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(0.8) # Allow server to start up
        try:
            names = ('philip@ri.hype', 'jonathan@matrix.hype')
            for name in names:
                self._run('dl', name, '--server=http://localhost:%d' % port)
                txt_cache = self.io.output.read()
                self.assertEqual(
                    json.loads(txt_cache),
                    json.load(open('ejtp/tests/idents/'+name))
                )
                expected_stderr = "\n".join([
                    "Downloading via http://localhost:%d/...",
                    "",
                    "* http://localhost:%d/idents/%s...",
                    "",
                    "done\n",
                ]) % (port, port, name)
                self.assertEqual(
                    self.io.error.read(),
                    expected_stderr
                )
                self.io.clear()
        finally:
            webserver.terminate()

    def test_set_attribute(self):
        fname = self._tmp_file_with_env_cache()
        self._run('set',
            'atlas@lackadaisy.com',
            '--args={"noob":true}',
            '--cache-source=' + fname)
        self.io.clear()
        output = self._run('details',
            'atlas@lackadaisy.com',
            '--cache-source=' + fname)
        data = json.loads(output)
        self.assertEqual(True, data['noob'])

    def test_without_env_var(self):
        self.env_data = None
        if ENV_VAR in os.environ:
            self.env_data = os.environ.pop(ENV_VAR)
        try:
            self._run('list')
        finally:
            if self.env_data:
                os.environ[ENV_VAR] = self.env_data

    def test_rm_valid_name(self):
        fname = self._tmp_file_with_env_cache()
        output = self._run('rm', 'atlas@lackadaisy.com', '--cache-source=' + fname)
        self.assertIn('atlas@lackadaisy.com removed from file %s' % fname, output)

        self.io.clear()
        output = self._run('list', '--cache-source=' + fname)
        self.assertNotIn('atlas@lackadaisy.com', self.io.get_value())

    def test_rm_two_valid_names(self):
        fname = self._tmp_file_with_env_cache()
        names = ('atlas@lackadaisy.com', 'victor@lackadaisy.com')

        data = self._run('rm', '--cache-source=' + fname, *names)
        for name in names:
            self.assertIn(name + ' removed from file %s' % fname, data)

        self.io.clear()
        data = self._run('list', '--cache-source=' + fname)
        for name in names:
            self.assertNotIn(name, data)

    def test_rm_invalid_name(self):
        fname = self._tmp_file_with_env_cache()
        output = self._run('rm', 'none@lackadaisy.com', '--cache-source=' + fname)
        self.assertIn('none@lackadaisy.com not found in any cache file', output)

    def test_rm_invalid_name(self):
        fname = self._tmp_file_with_env_cache()
        output = self._run('rm', 'none@lackadaisy.com', '--cache-source=' + fname)
        self.assertIn('none@lackadaisy.com not found in any cache file', output)

    def test_rm_error_with_name_repeated_across_files(self):
        fname1 = self._tmp_file_with_env_cache()
        fname2 = self._tmp_file_with_env_cache()
        self._curr_var = os.environ[ENV_VAR]
        os.environ[ENV_VAR] = ':'.join([fname1, fname2])
        try:
            output = self._run('rm', 'mitzi@lackadaisy.com', error=True)
            self.assertIn('Identity mitzi@lackadaisy.com found in multiple files', output)
        finally:
            os.environ[ENV_VAR] = self._curr_var

    def test_rm_name_in_all_files(self):
        fname1 = self._tmp_file_with_env_cache()
        fname2 = self._tmp_file_with_env_cache()
        self._curr_var = os.environ[ENV_VAR]
        os.environ[ENV_VAR] = ':'.join([fname1, fname2])
        try:
            data = self._run('rm', 'mitzi@lackadaisy.com', '-A')
            self.assertIn('mitzi@lackadaisy.com removed from file %s' % fname1, data)
            self.assertIn('mitzi@lackadaisy.com removed from file %s' % fname2, data)
        finally:
            os.environ[ENV_VAR] = self._curr_var
