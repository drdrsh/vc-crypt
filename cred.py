#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

import os
import re
import sys
import argparse
import getpass
from glob import glob
from Crypto.Cipher import DES3

def parse_env_file(filename, var_dict):
    lines = [l.strip() for l in open(filename)]
    for line in lines:
        if line.startswith('#') or len(line) == 0:
            continue
        res = line.split('=', 1)
        if len(res) != 2:
            continue
        var_dict[str(res[0]).strip()] = str(res[1]).strip()
    return var_dict

def pad(text, mul=8):
    while len(text.encode('utf-8')) % mul != 0:
        text += ' '
    return text

def encrypt_file(in_filename, out_filename, key):

    des3 = DES3.new(key, DES3.MODE_ECB)

    data_in = None
    with open(in_filename, 'rb') as in_file:
        data_in = pad(in_file.read().decode('utf-8'))

    with open(out_filename, 'wb') as out_file:
        out_file.write(des3.encrypt(data_in))

def decrypt_file(in_filename, out_filename, key):

    des3 = DES3.new(key, DES3.MODE_ECB)

    data_in = None
    with open(in_filename, 'rb') as in_file:
        data_in = in_file.read()

    out = None
    try:
        out = des3.decrypt(data_in).decode('utf-8')
    except UnicodeDecodeError:
        return False
    
    with open(out_filename, 'wb') as out_file:
        out_file.write(out.strip().encode('utf-8'))
    return True

def validate_password(password):
    pass_len = len(password.encode('utf-8'))
    if pass_len > 24:
        print("Password cannot be more than 24 bytes in length", file=sys.stderr)
        sys.exit(1)

    if pass_len < 16:
        password = pad(password, 16)

    if pass_len > 16 and pass_len < 24:
        password = pad(password, 24)
    return password

class App(object):

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='A helper tool for loading encrypted version-controlled credentials into enviornment',
            usage='''cred <command> [<args>]

These are the available commands:
   encrypt    Encrypts files in the working directory that have the extension "*.secret" into "*.secret.enc"
   decrypt    Decrypts files in the working directory that have the extension "*.secret.enc" into "*.secret"
   concat     Loads all files in the working directory that have *.secret extension, followed by all *.public files, followed by all *.local files and concatenates them into .env file which is overwritten
''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def encrypt(self):
        parser = argparse.ArgumentParser(
            description='Encrypts files in the working directory that have the extension "*.secret" into "*.secret.enc"')
        parser.add_argument('-p', '--password', help="Password to use for encryption or decryption (Must be between 1 and 24 bytes long)")
        args = parser.parse_args(sys.argv[2:]).__dict__
        password_0 = None
        if args['password'] is None:
            print("Enter Encryption Password (Must be between 1 and 24 bytes long)")
            password_0 = getpass.getpass(prompt="Password:")
            password_1 = getpass.getpass(prompt="Confirm Password:")
            if password_0 != password_1:
                print("Password mismatch")
                exit(1)
        else:
            password_0 = args['password']
        password = validate_password(password_0)
        for f in glob('*.secret'):
            if os.path.isfile(f):
                out_file = os.path.basename(f) + '.enc'
                print("Encrypting file \"{}\" into \"{}\"".format(f, out_file))
                encrypt_file(f, out_file, password)

    def decrypt(self):
        parser = argparse.ArgumentParser(
            description='Decrypts files in the working directory that have the extension "*.secret.enc" into "*.secret"')
        parser.add_argument('-p', '--password', help="Password to use for encryption or decryption (Must be between 1 and 24 bytes long)")
        args = parser.parse_args(sys.argv[2:]).__dict__
        if args['password'] is None:
            password = getpass.getpass(prompt='Enter Decryption Password:')
        else:
            password = args['password']
        password = validate_password(password)
        for f in glob('*.secret.enc'):
            if os.path.isfile(f):
                out_file = re.sub('.enc$', '', os.path.basename(f))
                if decrypt_file(f, out_file, password):
                    print("Decrypted file \"{}\" into \"{}\"".format(f, out_file))
                else :
                    print("<!> Failed to decrypt file \"{}\" (Invalid password)".format(f))
                    sys.exit(1)
        
    def concat(self):
        var_dict = {}
        types = ['*.secret', '*.public', '*.local']
        for t in types:
            for f in glob(t):
                if os.path.isfile(f):
                    print("Reading variables in {}".format(f))
                    var_dict = parse_env_file(f, var_dict)
        
        with open(".env", 'w') as fl:
            for var_name in var_dict:
                var_val = var_dict[var_name]
                fl.write("{}={}\n".format(var_name, var_val))
    
if __name__ == '__main__':
    App()