#!/usr/bin/env python

from setuptools import setup

long_desc = '''

Encrypted JSON Transport Protocol
---------------------------------

EJTP is an overlay protocol that allows the pluggable use of underlying transports, such as UDP, TCP, HTTP, IRC, Email and carrier pigeon to provide a cryptographically secure network of unreliable message forwarding. You can think of it as a bit like a more general-purpose and security-minded successor to XMPP, using JSON rather than XML as its frame medium.

On top of a simple frame format, EJTP boasts a consistent and simple format for describing encryption credentials, which is useful even without the rest of EJTP. The ejtp-crypto script makes it easy for other projects to take advantage of this pending a native port of ejtp.crypto to languages other than Python.

The intention of EJTP is to make it trivial to establish secure and NAT-oblivious distributed services across a common network of message relays. Your system only has to worry about exchanging encryption credentials and establishing a connection with a relay host, helping to pave the way toward distributed apps that run entirely in HTML5 (pending a port of the project to JS). You can be serverless *and* smartphone-friendly.

Optionally supports elliptic curve cryptography if the PyECC_ module is installed.

For more technical and in-depth information, visit the `Github project <https://github.com/campadrenalin/EJTP-lib-python>`_.

.. _PyECC: https://pypi.python.org/pypi/PyECC
'''

setup(
	name = 'ejtp',
	version = '0.9.7p1',
	description = 'Encrypted JSON Transport Protocol library',
    long_description = long_desc,
	author = 'Philip Horger',
	author_email = 'philip.horger@gmail.com',
	url = 'https://github.com/campadrenalin/EJTP-lib-python/',
    package_data={
        'ejtp.tests' : ['examplecache.json', 'idents/*']
    },
    install_requires = [
        'pycrypto',
        'persei',
        'requests',
        'streql',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Security :: Cryptography',
    ],
    scripts = [
        'scripts/ejtpd',
        'scripts/ejtp-keygen',
        'scripts/ejtp-console',
        'scripts/ejtp-crypto',
        'scripts/ejtp-identity',
    ],
	packages = [
		'ejtp',
		'ejtp.applications',
		'ejtp.applications.ejforward',
		'ejtp.crypto',
		'ejtp.frame',
		'ejtp.identity',
		'ejtp.jacks',
		'ejtp.tests',
		'ejtp.util',
		'ejtp.vendor',
	],
)
