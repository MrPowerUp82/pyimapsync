#!/usr/bin/python3.9

import mailbox
import sys
import email
import os

def maildir2mailbox(maildirname, mboxfilename):
    # Abre o maildir existente e o arquivo mbox de destino
    maildir = mailbox.Maildir(maildirname, factory=email.message_from_binary_file)
    mbox = mailbox.mbox(mboxfilename)

    # Trava o mbox
    mbox.lock()

    # Itera sobre as mensagens no maildir e adiciona ao mbox
    for msg in maildir:
        mbox.add(msg)

    # Fecha e destrava
    mbox.close()
    maildir.close()

# Cria o mailbox principal
dirname = sys.argv[-2]
mboxname = sys.argv[-1]
print(dirname + ' -> ' + mboxname)
mboxdirname = mboxname + '.sbd'
maildir2mailbox(dirname, mboxname)
if not os.path.exists(mboxdirname):
    os.makedirs(mboxdirname)

listofdirs = [dn for dn in next(os.walk(dirname))[1] if dn not in ['new', 'cur', 'tmp']]
for curfold in listofdirs:
    curlist = [mboxname] + curfold.split('.')
    curpath = os.path.join(*[dn + '.sbd' for dn in curlist if dn])
    if not os.path.exists(curpath):
        os.makedirs(curpath)
    print('| ' + curfold + ' -> ' + curpath[:-4])
    maildir2mailbox(os.path.join(dirname, curfold), curpath[:-4])

print('Done')
