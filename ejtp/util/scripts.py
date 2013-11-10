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

from __future__ import print_function
try:
    input = raw_input
except:
    pass

import sys
import re
import traceback

from ejtp.identity import Identity

IDENT_TYPES = {
    "udp"  : "IPv6 address, accessed over UDP",
    "udp4" : "IPv4 address, accessed over UDP",
    "tcp"  : "IPv6 address, accessed over TCP",
    "tcp4" : "IPv4 address, accessed over TCP",
    "local": "Can only communicate within a single OS process",
}
ENC_TYPES = {
    #"aes"    : "AES Shared-Key encryption (not currently useful)",
    "rotate" : "Only for trivial demos, not recommended!",
    "rsa"    : "RSA Public-Key encryption (recommended)",
}

EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')

NOTICE_EMAIL = '''
NOTE: If you intend to host this identity in the DJDNS
registry, the email domain needs to match your branch
regex to be accessible.

http://roaming-initiative.com/blog/blog/djdns-ident-registration.html
'''.strip()

NOTICE_LOCATION = '''
Next, we need your network location.
These are made of 3 parts - type, address, and callsign.
For example, ["udp4", ["107.6.106.82", 9090], "randall"]
'''.strip()

NOTICE_CALLSIGN = '''
Your callsign distinguishes you from other people on
the same host and port - or just lets you run more
than one service for yourself on the same 'line'.
'''.strip()

def print_exception():
    traceback.print_exc()

def print_exception_only():
    exc_type, exc_value, _ = sys.exc_info()
    print(
        "".join(traceback.format_exception_only(exc_type, exc_value)),
        file=sys.stderr
    )

def print_exception_fmt(fmt):
    if fmt == "short":
        print_exception_only()
    elif fmt == "long":
        print_exception()

def confirm(func, label = None, show = None):
    '''
    Get a bit of data from the user, confirming that it's correct.
    '''
    confirmed = False
    value = None
    while not confirmed:
        try:
            value = func()
        except ValueError as e:
            print("Invalid input: %r" % e)
            continue
        if show:
            show(value)
        elif label:
            print(label % value)
        correct = input('Is this correct? [y/n] ')
        confirmed = 'y' in correct.lower()
    return value

def choose(options, singular, plural):
    choice = None
    while not choice in options:
        print("The following %s are available:\n" % plural)
        for name in sorted(options.keys()):
            desc = options[name]
            print("    {0} : {1}".format(name, desc))
        choice = input("\nWhich %s do you want? " % singular)
    return choice

def retry(prompt, callback, max_retry=-1, fmt="short", catches=(Exception,)):
    attempts  = 0
    while (max_retry < 0) or (attempts <= max_retry):
        user_input = input(prompt)
        try:
            return callback(user_input)
        except catches:
            print_exception_fmt(fmt)
            attempts += 1
            if (max_retry > 0) and (attempts >= max_retry):
                raise

def get_identity():
    print(NOTICE_EMAIL)
    name = confirm(get_name, 'The name you chose: %r')
    loc  = confirm(
        get_location,
        'Your location is:\n%r'
    )
    print("\nNow we generate your encryptor.")
    enc = None
    while enc == None:
        try:
            enc = get_encryptor()
        except ValueError:
            pass

    return Identity(name, enc, loc)
    
def get_name():
    '''
    Get an email address from STDIN.
    '''
    name = input('Your identity name, in email form: ')
    if not EMAIL_REGEX.match(name):
        raise ValueError('Not a valid email address-style name.')
    return name

def get_location():
    '''
    Get an EJTP location from STDIN.
    '''
    ltype = choose(IDENT_TYPES, 'type', 'types')
    if ltype == "local":
        laddr = None
    else:
        laddr = confirm(get_addr, 'Address = %r')
    lcall = confirm(get_callsign)
    return [ltype, laddr, lcall]

def get_addr():
    ip = input('Your IP address, at which you can be contacted: ')
    port = input('Port at which you are reachable: ')
    return [ip, int(port)]

def get_callsign():
    return input("Your callsign: ")

def get_encryptor():
    etype = choose(ENC_TYPES, 'type', 'types')
    def get_rotation():
        return int(input("How much to rotate? "))
    def get_crypto_bits():
        return int(input("How many bits? "))
    if etype == "rotate":
        amount = confirm(get_rotation)
        enc = [etype, amount]
    else:
        amount = confirm(get_crypto_bits)
        from ejtp.crypto.rsa import RSA
        try:
            print("Generating... if it takes awhile, wiggle your mouse.")
            enc = RSA(None, amount).proto()
        except:
            print_exception()
            raise ValueError("Could not generate key with %d bits." % amount)
    return enc
