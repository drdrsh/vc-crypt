# Python script for encrypting secret credentials for version control

This is a simple python script that can be used to encrypt/decrypt secret credentials (API secret keys, HTTP passwords, etc.) using a password to be able to safely put them under version control. It doesn't require building binaries, its only dependency is pyCrypto which is included in Anaconda python distribution, or can be installed manually using pip.

# Why should you use this?
It is very likely that other git encryption methods like git-crypt are better for you, I wrote this because I wanted a solution that works well on any platform (Specifically Windows) without having to download cumbersome build tools.

# Dependencies

You will need python and pyCrypto module installed.


# File structure

This utility will only act on files of the following extension in the same directory
- #### *.secret
These are absolutely secret and must not be committed to VCS. They are committed as encrypted files named “*.secret.enc”
- #### *.public
These are the public config files, they should be committed to the VCS
- #### *.local
These are local override config files, any variable in these files will override values in the other two, they shouldn’t be committed.

# How to use

## To use this demo

1. Checkout this repo ```git checkout https://github.com/drdrsh/vc-crypt.git``` 
2. Run ```python cred.py decrypt``` and use password ```dummy_password```.
3. Run ```python cred.py concat``` to generate ```.env``` file.

To modify secret params, edit your `env.secret` and run ```python cred.py encrypt``` again.

## To start from scratch
1. Download ```cred.py``` and  ```.gitignore``` (or add entries in this ```.gitignore``` file to yours).
3. Create your own *.secret, *.public, *.local files.
4. Run ``` python cred.py encrypt``` to be prompted for password, alternatively you can specify the password in the command line by passing arguments ```--password your_password``` but this will cause the password to appear in shell history.
5. Commit your work.

- To generate .env file run ```python cred.py concat```
- To decrypt  encrypted credentials run ```python cred.py decrypt``` and you will be prompted to enter the password, alternatively you can specify the password in the command line by passing arguments ```--password your_password``` but this will cause the password to appear in shell history.

# License
MIT