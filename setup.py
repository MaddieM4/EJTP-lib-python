#!/usr/bin/env python

from distutils.core import setup

setup(
	name = 'ejtp',
	version = '0.9.3',
	description = 'Encrypted JSON Transport Protocol library',
	author = 'Philip Horger',
	author_email = 'philip.horger@gmail.com',
	url = 'https://github.com/campadrenalin/EJTP-lib-python/',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
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
        'scripts/ejtp-crypto'
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
