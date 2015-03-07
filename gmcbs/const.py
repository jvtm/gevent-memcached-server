"""
Constants for Memcached binary protocol

Originally generated from protocol_binary.h:
  egrep "( = |^[ ]{3,}\* )" doc/protocol_binary.h \
   | sed -e "s:^[ ]*::" -e "s:^\*:#:" -e "s:^PROTOCOL_BINARY_::" -e "s:,$::" \
   > gmcbs/const.py

"""
from collections import namedtuple
import struct

# Definition of the legal "magic" values used in a packet.
# See section 3.1 Magic byte
MAGIC_REQ = 0x80
MAGIC_RES = 0x81

# Definition of the valid response status numbers.
# See section 3.2 Response Status
RESPONSE_SUCCESS = 0x00
RESPONSE_KEY_ENOENT = 0x01
RESPONSE_KEY_EEXISTS = 0x02
RESPONSE_E2BIG = 0x03
RESPONSE_EINVAL = 0x04
RESPONSE_NOT_STORED = 0x05
RESPONSE_DELTA_BADVAL = 0x06
RESPONSE_AUTH_ERROR = 0x20
RESPONSE_AUTH_CONTINUE = 0x21
RESPONSE_UNKNOWN_COMMAND = 0x81
RESPONSE_ENOMEM = 0x82

# Defintion of the different command opcodes.
# See section 3.3 Command Opcodes
CMD_GET = 0x00
CMD_SET = 0x01
CMD_ADD = 0x02
CMD_REPLACE = 0x03
CMD_DELETE = 0x04
CMD_INCREMENT = 0x05
CMD_DECREMENT = 0x06
CMD_QUIT = 0x07
CMD_FLUSH = 0x08
CMD_GETQ = 0x09
CMD_NOOP = 0x0a
CMD_VERSION = 0x0b
CMD_GETK = 0x0c
CMD_GETKQ = 0x0d
CMD_APPEND = 0x0e
CMD_PREPEND = 0x0f
CMD_STAT = 0x10
CMD_SETQ = 0x11
CMD_ADDQ = 0x12
CMD_REPLACEQ = 0x13
CMD_DELETEQ = 0x14
CMD_INCREMENTQ = 0x15
CMD_DECREMENTQ = 0x16
CMD_QUITQ = 0x17
CMD_FLUSHQ = 0x18
CMD_APPENDQ = 0x19
CMD_PREPENDQ = 0x1a
CMD_TOUCH = 0x1c
CMD_GAT = 0x1d
CMD_GATQ = 0x1e
CMD_GATK = 0x23
CMD_GATKQ = 0x24
CMD_SASL_LIST_MECHS = 0x20
CMD_SASL_AUTH = 0x21
CMD_SASL_STEP = 0x22

# this header for use in other projects.  Range operations are
# not expected to be implemented in the memcached server itself.
CMD_RGET = 0x30
CMD_RSET = 0x31
CMD_RSETQ = 0x32
CMD_RAPPEND = 0x33
CMD_RAPPENDQ = 0x34
CMD_RPREPEND = 0x35
CMD_RPREPENDQ = 0x36
CMD_RDELETE = 0x37
CMD_RDELETEQ = 0x38
CMD_RINCR = 0x39
CMD_RINCRQ = 0x3a
CMD_RDECR = 0x3b
CMD_RDECRQ = 0x3c

# Definition of the data types in the packet
# See section 3.4 Data Types
TYPE_RAW_BYTES = 0x00

# Extra bytes for GET, GETK responses. pylibmc treats this as serialization type
EXTRA_GET = '\x00\x00\x00\x00'

# Helper dictionaries etc for Python.
# Yes, a bit hacky... but I'm a lazy person.
COMMANDS = {}
RESPONSES = {}
MAGIC = {}
TYPES = {}
QUIET = []
for k, v in locals().items():
    if k.startswith('CMD_'):
        COMMANDS[v] = k[4:]
        if k.endswith('Q'):
            # 'Q' variants: commands which shouldn't flush output buffer
            QUIET.append(v)
    elif k.startswith('RESPONSE_'):
        RESPONSES[v] = k[9:]
    elif k.startswith('MAGIC_'):
        MAGIC[v] = k[6:]
    elif k.startswith('TYPE_'):
        TYPES[v] = k[5:]

assert COMMANDS[CMD_QUIT] == 'QUIT'
assert RESPONSES[RESPONSE_SUCCESS] == 'SUCCESS'
assert MAGIC[MAGIC_REQ] == 'REQ'
assert TYPES[TYPE_RAW_BYTES] == 'RAW_BYTES'
assert CMD_GETKQ in QUIET


RequestHeader = namedtuple('RequestHeader', ['magic', 'opcode', 'keylen', 'extlen',
                                             'datatype', 'bodylen', 'opaque', 'cas'])
ResponseHeader = namedtuple('ResponseHeader', ['magic', 'opcode', 'keylen', 'extlen',
                                               'datatype', 'status', 'bodylen', 'opaque', 'cas'])
Message = namedtuple('Message', ['header', 'extra', 'key', 'value'])


# magic, opcode, keylen, extralen, datatype, [reserved], bodylen, opaque, cas
HEADER_REQUEST_FORMAT = '!BBHBBxxIIQ'
HEADER_REQUEST_LEN = struct.calcsize(HEADER_REQUEST_FORMAT)
assert HEADER_REQUEST_LEN == 24

# magic, opcode, keylen, extralen, datatype, status, bodylen, opaque, cas
HEADER_RESPONSE_FORMAT = '!BBHBBHIIQ'
HEADER_RESPONSE_LEN = struct.calcsize(HEADER_RESPONSE_FORMAT)
assert HEADER_RESPONSE_LEN == 24
