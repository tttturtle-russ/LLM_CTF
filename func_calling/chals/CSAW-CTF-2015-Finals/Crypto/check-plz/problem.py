#!/usr/bin/env python2

import os, sys
from Crypto import Random
from Crypto.Cipher import AES

flag = 'flag{temp}'
bs = AES.block_size

def pad(msg):
    pad_length = bs - (len(msg) % bs)
    return msg + '\x80' + '\x00' * (pad_length - 1)


def xor(s1, s2):
    return ''.join(map(lambda t: chr(ord(t[0]) ^ ord(t[1])), zip(s1, s2)))


def MAC(cipher, msg):
    msg = pad(msg)
    blocks = [msg[i:i+bs] for i in range(0, len(msg), bs)]
    mac = '\x00' * bs
    for i in range(len(blocks)):
        m = xor(mac, blocks[i])
        mac = cipher.encrypt(m)

    return mac


def main():
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    key = Random.new().read(bs)
    cipher = AES.new(key, AES.MODE_ECB)

    msg = raw_input('Give me a message: ')
    mac = MAC(cipher, msg)

    print "Here's the MAC: " + mac.encode('hex')
    print ''
    print 'Ok, your turn. Give me a message and a valid MAC'

    msg_input = raw_input('Message: ')
    mac_input = raw_input('MAC: ')

    if msg_input == msg:
        print "Hey, that's cheating!"
        return

    if MAC(cipher, msg_input) == mac_input.decode('hex'):
        print "Congrats, here's your flag: " + flag

if __name__ == '__main__':
    main()
