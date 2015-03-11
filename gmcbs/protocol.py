"""
Extendable server handler for memcached binary protocol.

Socket servers (eg. gevent) should create one instance of ClientHandler
for each connection.

ClientHandler class can also be extended to handle your own commands:
 - add your extra context (eg. storage instance) in your own class __init__
 - add / override wanted do_OPNAME() methods

Another option is to pass in explicit handler dictionary. You then
need to define _all_ handlers, including QUIT, NOOP and others.

It's also possible to modify the handler dictionary from outside.

Note: this is just a prototype interface, and might change quite a bit
once glued together with existing storage implementations.
"""

from gmcbs.const import *
from collections import defaultdict
from datetime import timedelta
import logging
import os
import struct
import time


def pack_response(request, status=RESPONSE_SUCCESS, key=b'', extra=b'', value=b'', cas=0, datatype=TYPE_RAW_BYTES):
    """
    Formats a binary response based on request.
    NOTE: this doesn't use / create named tuples. Usually creating those objects is just extra overhead.
    Maybe those could be added later, if required (const.py already has some extra named tuples).
    For example, if connection loop part wants to access any of the values (hooks or similar)
    """
    header = struct.pack(HEADER_RESPONSE_FORMAT, MAGIC_RES, request.header.opcode,
                         len(key), len(extra), datatype, status,
                         len(key) + len(extra) + len(value),
                         request.header.opaque, cas)
    return header + extra + key + value


class ClientHandler(object):
    """ Handler for a single already-open client connection """
    def __init__(self, sock, handlers=None, set_thread_name=True):
        """
        :param sock: client socket for recv()/send()
        :param handlers: explicit request handlers, use numeric opcode as key
        :param set_thread_name: set thread name based on client address
        """
        self.log = logging.getLogger(self.__class__.__name__)
        # TODO: config? extra args, kwargs? maybe encourage sub-classing
        self.sock = sock
        if set_thread_name:
            # intentionally imported here, to make (gevent) monkey patching easier
            import threading
            threading.current_thread().setName("%s:%s" % sock.getpeername())

        self.buffer_in = bytearray()
        self.buffer_out = bytearray()

        self.stats = defaultdict(int)
        self.stats['time_init'] = time.time()

        if handlers is None:
            handlers = {}
            for opcode, opname in COMMANDS.iteritems():
                funcname = 'do_%s' % opname.lower()
                handler = getattr(self, funcname, None)
                if handler:
                    self.log.debug("registered andler %s (%#.2x): %r", opname, opcode, handler)
                    handlers[opcode] = handler
        self.handlers = handlers

    def read_bytes(self, amount, chunk_size=1024):
        """
        Return explicit amount of bytes from socket.
        Uses input buffer internally, for reading multiple request
        at the same go.

        :param amount: amount of bytes to return
        :param chunk_size: socket read sise
        :return: raw bytes
        """
        # i tried to use also memoryview + recv_into here, but something went horribly wrong.
        while len(self.buffer_in) < amount:
            chunk = self.sock.recv(chunk_size)
            self.log.debug("bytes read: %d", len(chunk))
            if chunk == '':
                continue
                #gevent.sleep()
            else:
                self.buffer_in.extend(chunk)

        ret = self.buffer_in[:amount]
        self.buffer_in = self.buffer_in[amount:]
        self.stats['bytes_read'] += amount
        return ret

    def read_request(self):
        """
        Reads a single client request using self.read_bytes().
        :return: Message named tuple (header, extra, key, value)
        """
        header = RequestHeader._make(struct.unpack(HEADER_REQUEST_FORMAT, self.read_bytes(HEADER_REQUEST_LEN)))
        self.log.debug("header: %r", header)
        if header.magic != MAGIC_REQ:
            raise ValueError("Invalid magic byte %#.2x" % header.magic)

        # extra, key, value might also be empty strings
        extra = self.read_bytes(header.extlen)
        self.log.debug("extra: %r", extra)

        key = self.read_bytes(header.keylen)
        self.log.debug("key: %r", key)

        remaining = header.bodylen - header.extlen - header.keylen
        value = self.read_bytes(remaining)
        self.log.debug("value: %r", value)

        self.stats[header.opcode] += 1
        self.stats['ops'] += 1

        return Message(header, extra, key, value)

    # XXX: this interface might still change. or these default ones might disappear.
    # right now these are enough for pylibmc doing get_multi() + disconnect
    def do_get(self, request):
        return pack_response(request, status=RESPONSE_KEY_ENOENT)

    def do_getq(self, request):
        return self.do_get(request)

    def do_getk(self, request):
        return pack_response(request, key=request.key, status=RESPONSE_KEY_ENOENT)

    def do_getkq(self, request):
        return self.do_getk(request)

    def do_noop(self, request):
        return pack_response(request)

    def do_quit(self, request):
        return pack_response(request)

    def do_quitq(self, request):
        return self.do_quit(request)

    def do_stat(self, request):
        """ STAT command, expects multiple reply packets + one empty packet  """
        if request.key:
            # would need to read more memcached code for the specific keys
            self.log.warning("TODO: STAT %r", request)
            return pack_response(request, key=request.key, status=RESPONSE_KEY_ENOENT)
        stats = {
            'time': '%d' % time.time(),
            'pid': str(os.getpid()),
        }
        ret = []
        for key, value in stats.iteritems():
            ret.append(pack_response(request, key=key, value=value))
        ret.append(pack_response(request))
        return ''.join(ret)

    def send_replies(self):
        """ Flush all buffered replies (usually at least one) """
        if self.buffer_out:
            self.sock.sendall(self.buffer_out)
            self.stats['bytes_sent'] += len(self.buffer_out)
            self.log.debug("bytes sent: %d", len(self.buffer_out))
            self.buffer_out = bytearray()

    def serve_client(self):
        """
        Client connection loop. Serve until exception or QUIT command.
        TODO: gevent Timeout object? maybe outside?
        """
        self.log_stats("CONNECT")
        while True:
            request = self.read_request()
            self.log.debug("request: %r", request)
            opcode = request.header.opcode
            if opcode in self.handlers:
                response = self.handlers[opcode](request)
            else:
                self.log.warning("No handler for %s %#.2x %r", COMMANDS.get(opcode), opcode, request.header)
                response = pack_response(request, status=RESPONSE_UNKNOWN_COMMAND)

            if response:
                self.buffer_out.extend(response)

            if opcode not in QUIET:
                self.send_replies()

            if opcode in (CMD_QUIT, CMD_QUITQ):
                self.log_stats(COMMANDS[opcode])
                self.stats['time_quit'] = time.time()
                break
        return self.stats

    def log_stats(self, prefix="STATUS", level=logging.INFO):
        """ Logs client statistics """
        # TODO: call this periodically? then it would be nice to show ops/s for the last period (not full connection)
        now = time.time()
        t_diff = now - self.stats['time_init']
        out = [
            "connection_time: %s" % timedelta(seconds=int(t_diff)),
            "ops/s: %.1f" % (self.stats['ops']/t_diff),
        ]
        for key in self.stats:
            out.append("%s: %s" % (COMMANDS.get(key, key), self.stats[key]))
        self.log.log(level, prefix + ": " + ", ".join(sorted(out)))
