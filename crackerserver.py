import json
import struct
import time
import select



import string
from itertools import product
from hashlib import sha256
import socket

charset = string.digits + string.ascii_uppercase


def generator(charset, n_min, n_max):
    for n in range(n_min, n_max + 1):
        for lst_pw in product(charset, repeat=n):
            yield ''.join(lst_pw)


def serialize_passwords(passwords):
    return json.dumps(passwords)


def deserialize_passwords(js):
    return json.loads(js)


def myselect():

    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener_socket.bind(("192.168.48.212", 10001))
    listener_socket.listen(10)
    r_list = [listener_socket]

    npass_chunk = 10000
    gen = generator(charset, 4, 7)

    try:
        while True:
            r_ready, w_ready, e_ready = select.select(r_list, [], [])

            for s in r_ready:

                if s == listener_socket:
                    # handle the server socket
                    client_socket, client_address = listener_socket.accept()
                    r_list.append(client_socket)
                else:
                    # handle all other sockets
                    length = s.recv(4)
                    if length:
                        # i need to do [0] and cast int because the struct.unpack return a tupla like (23234234,)
                        # with the length as a string
                        length = int(struct.unpack('!i', length)[0])
                        message = s.recv(length)
                        passwords = []
                        for i in xrange(npass_chunk):
                            password = gen.next()
                            passwords.append(password)

                        chunk = serialize_passwords(passwords)
                        chunk_length = len(chunk)
                        s.send(struct.pack('!i', chunk_length))
                        s.sendall(chunk)
                    else:
                        s.close()
                        r_list.remove(s)


    except KeyboardInterrupt:
        print "stop"

def main():
    myselect()

if __name__ == '__main__':
    main()
