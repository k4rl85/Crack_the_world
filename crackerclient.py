import socket
import struct
import json
import hashlib


def load(filepath='login.txt'):
    res = {}
    with open(filepath, 'rb') as fp:
        for line in fp:
            user, pw = line.split()
            pw = pw.strip()
            res[pw] = user
    return res


def check_passwords(dic, passwords):
    res = {}
    for pw in passwords:
        h = hashlib.sha256(pw).hexdigest()
        if h in dic:
            username = dic[h]
            res[username] = pw
    return res


def main():
    """
    it sends user input command to the daemon server
    """
    n = 0
    with open('found.txt', 'w') as fp:
        fp.write('')

    loaded = load('login.txt')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect(("192.168.48.212", 10001))

        while True:
            message = 'a'
            length = struct.pack('!i', len(message))
            s.send(length)
            s.send(message)
            resp = s.recv(4)

            if resp:
                resp = struct.unpack('!i', resp)[0]
                length = int(resp)
                #print 'length = {:,}'.format(length)

                chunk = ''
                left = length - len(chunk)
                while left:
                    chunk += s.recv(left)
                    left = length - len(chunk)  # devo sapere esattamente quanto devo ancora ricevere
                    # altrimenti potrei prendere dati extra dal server e non torna niente!!
                #print 'chunk =', chunk
                passwords = json.loads(chunk)
                #print '{:,}'.format(len(passwords))

                found = check_passwords(loaded, passwords)
                if found:
                    with open('found.txt', 'a') as fp:
                        for username, pw in found.iteritems():
                            n += 1
                            print '{:,}: {} = "{}"'.format(n, username, pw)
                            fp.write('{:,}^ {} {}\n'.format(n, username, pw))

        s.close()
    except socket.error as err:
        print err


main()
