#!/usr/bin/env python

from distutils.core import setup

setup(
	name = 'ejtp',
	version = '0.8.1',
	description = 'Encrypted JSON Transport Protocol library',
	author = 'Philip Horger',
	author_email = 'philip.horger@gmail.com',
	url = 'https://github.com/campadrenalin/EJTP-lib-python/',
	packages = [
		'ejtp',
		'ejtp.util',
		'ejtp.util.crypto',
	],
)
