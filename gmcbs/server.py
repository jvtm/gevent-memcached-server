"""
Example gevent server loop

Might add config switches etc here later, to make this work
with custom settings and handlers.
"""
import gevent.monkey
gevent.monkey.patch_thread()

from gevent.server import StreamServer
from gmcbs.protocol import ClientHandler
import logging
import sys


class ConnectionHelper(object):
    """ Helper class / callable for single client connection """
    # this is still a class so that we can pass in config dict and others
    def __init__(self, handler_class=ClientHandler, handler_kwargs=None, tcp_keepalive=True):
        self.log = logging.getLogger(self.__class__.__name__)
        if tcp_keepalive is True:
            tcp_keepalive = (1800, 30, 3)
        self.tcp_keepalive = tcp_keepalive
        self.handler_class = handler_class
        self.handler_kwargs = dict(handler_kwargs or [])

    def __call__(self, sock, addr):
        addrinfo = "%s:%s" % addr
        self.log.info("connected %s", addrinfo)
        if self.tcp_keepalive:
            import socket
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, self.tcp_keepalive[0])
            sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, self.tcp_keepalive[1])
            sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, self.tcp_keepalive[2])
        handler = self.handler_class(sock, **self.handler_kwargs)
        try:
            handler.serve_client()
        finally:
            handler.log_stats("DISCONNECT")
            # needs some error handling (revisiting after seeing this in full action)
            self.log.info("disconnected %s %s", sock, addrinfo)
            sock.close()


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if 'debug' in argv:
        lvl = logging.DEBUG
    else:
        lvl = logging.INFO
    logging.basicConfig(level=lvl, format='%(asctime)s %(levelname)s %(threadName)s %(message)s')

    connhandler = ConnectionHelper()
    server = StreamServer(('127.0.0.1', 11212), connhandler)
    logging.info("server: %r", server)
    server.serve_forever()

if __name__ == '__main__':
    sys.exit(main())
