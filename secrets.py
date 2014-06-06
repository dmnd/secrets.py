#!/usr/bin/env python

_HELP = """usage: secrets.py <command>

Commands:
    encrypt: Add new secrets. Overwrites the ciphertext
             with a newly encrypted secrets.py

    decrypt: Discard changes to secrets.py. Overwrites
             secrets.py by decrypting the ciphertext.
             All changes to secrets.py will be lost,
             so be careful with this!

    help:    Prints this message.


secrets.py
==========

Import secrets.py to gain access to its secrets:

    import secrets
    print secret.key

Don't commit secrets.py to your repository though! Instead,
encrypt it:

    secrets.py encrypt

Then commit the secrets.py.cast5 ciphertext file that is
generated.

At import time, secrets.py checks to see if juicy new
secrets are present in the ciphertext by comparing mtimes.
If the ciphertext is newer, secrets.py will update in
place.


Adding new secrets
==================

To add a new secret, edit secrets.py, then run:

    secrets.py encrypt


Decrypting secrets
==================

If you made a mistake while editing secrets.py, you can
force decrypt with `secrets.py decrypt`. Not that this
will overwrite your current version of secrets.py and all
changes will be lost! Be careful!
"""


# a comment about data
data = 'upstream'


##############################################################################
#### secrets.py implementation follows! put your secrets above this line. ####
##############################################################################
import os
import sys


# __file__ may be foo.pyc or foo.pyo; this converts all to foo.py
py_file = os.path.splitext(__file__)[0] + ".py"
cast5_file = py_file + ".cast5"


def decrypt(local_context=None, global_context=None):
    # decrypt the new file
    with open(cast5_file) as f:
        decrypted = f.read()

    # overwrite this very file
    with open(py_file, 'w') as f:
        f.write(decrypted)

    print "Decrypted %s to %s" % (cast5_file, py_file)

    # during this import we still have the old secrets, so exec the
    # decrypted file, taking care to avoid infinitely recursing
    if local_context is not None:
        local_context['inception'] = True
        exec decrypted in local_context, global_context


def import_and_maybe_decrypt(local_context, global_context):
    try:
        py_timestamp = os.stat(py_file).st_mtime
    except OSError:    # probably 'file doesn't exist'
        print >>sys.stderr, ("WARNING: unable to stat %s, skipping check."
                             " secrets.py may be out of date" % py_file)
        return

    try:
        cast5_timestamp = os.stat(cast5_file).st_mtime
    except OSError:    # probably 'file doesn't exist'
        print >>sys.stderr, ("WARNING: unable to stat %s, skipping check."
                             " secrets.py may be out of date" % cast5_file)
        return

    if cast5_timestamp > py_timestamp and not local_context.get('inception'):
        print "%s is newer than %s, automatically decrypting..." % (
            cast5_file, py_file)
        decrypt(local_context, global_context)


def encrypt():
    # encrypt the current file
    with open(py_file) as f:
        plaintext = f.read()

    with open(cast5_file, 'w') as f:
        f.write(plaintext)

    print "Encrypted %s to %s" % (py_file, cast5_file)


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None
    if command in (None, "help", "usage"):
        print _HELP
    elif command in ("encrypt", "save", "commit"):
        encrypt()
    elif command in ("decrypt", "revert"):
        decrypt()
    else:
        print >>sys.stderr, ("Invalid command '%s'" % command)


if __name__ == '__main__':
    main()
else:
    import_and_maybe_decrypt(locals(), globals())
