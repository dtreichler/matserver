# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import socket
import pickle
import struct
import logging

try:
    import scipy.io as sio
except ImportError:
    pass

PARAM_FLAG = 'A'
DATA_FLAG = 'B'
END_FLAG = 'ENDIT'
QUIT_FLAG = 'ALLDONE'
RESET_FLAG = 'RESET'
ERR_FLAG = 'ERR'
RESET_FLAG = 'RESET'
OK_FLAG = 'ALLCLEAR'

logging.getLogger().setLevel(logging.INFO)

class ServerBase(object):
    buf = 4096

    def recvall(self, sock):
        d = []
        while True:
            d2 = sock.recv(self.buf)
            d.append(d2)
            if END_FLAG in d2:
                d[-1] = d2[:d2.find(END_FLAG)]
                break
        d = ''.join(d)
        logging.info('Received %i bytes' % len(d))
        #logging.debug('Received: "%s"' % d)
        return d

class MatServer(ServerBase):

    def __init__(self, host='', port=50001, buf=4096):
        self.host = host
        self.port = port
        self.buf = buf
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.bind((self.host, self.port))
        self._s.listen(1)
        self.connect()

    def connect(self):
        logging.info('Accepting connections on port %i' % self.port)
        self.conn, addr = self._s.accept()
        logging.info('Connection from %s on port %i' % addr)

    def process(self):
        d = self.recvall(self.conn)
        try:
            filename, data = pickle.loads(d)
        except KeyError:
            self.conn.sendall(ERR_FLAG + END_FLAG)
        logging.info('Received data')

        try:
            sio.savemat(filename, data)
            self.conn.sendall(OK_FLAG + END_FLAG)
        except:
            self.conn.sendall(ERR_FLAG + END_FLAG)

    def shutdown(self):
        if self.conn:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        self._s.shutdown(socket.SHUT_RDWR)
        self._s.close()

    def run(self):
        while True:
            d = self.recvall(self.conn)
            if d == DATA_FLAG:
                self.process()
            elif d == RESET_FLAG:
                self.connect()
            elif d == QUIT_FLAG:
                self.shutdown()
                break


class MatClient(ServerBase):

    def __init__(self, host, port=50001, buf=4096):
        self.host = host
        self.port = port
        self.buf = buf
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((host, port))
        logging.info('Connected to %s on port %i' % (host, port))

    def savemat(self, filename, data):
        self._s.sendall(DATA_FLAG + END_FLAG)
        d = pickle.dumps((filename, data))
        self._s.sendall(d + END_FLAG)
        r = self.recvall(self._s)
        if r == ERR_FLAG:
            raise FilterError('Error during processing')

    def disconnect(self):
        self._s.sendall(RESET_FLAG + END_FLAG)
        self.close()

    def quit_server(self):
        self._s.sendall(QUIT_FLAG + END_FLAG)
        self.close()

    def close(self):
        self._s.shutdown(socket.SHUT_RDWR)
        self._s.close()


class FilterError(Exception):
    pass

