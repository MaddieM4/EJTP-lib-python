#!/usr/bin/env python

from distutils.core import setup

setup(
	name = 'ejtp',
	version = '0.9.1',
	description = 'Encrypted JSON Transport Protocol library',
	author = 'Philip Horger',
	author_email = 'philip.horger@gmail.com',
	url = 'https://github.com/campadrenalin/EJTP-lib-python/',
    scripts = [
        'scripts/ejtpd',
        'scripts/ejtp-keygen',
        'scripts/ejtp-test',
    ],
	packages = [
		'ejtp',
		'ejtp.crypto',
		'ejtp.ejforward',
		'ejtp.identity',
		'ejtp.jacks',
		'ejtp.logging',
		'ejtp.util',
		'ejtp.vendor',
	],
)
