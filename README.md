Helper for creating memcached binary protocol servers in Python.

Example server uses gevent, but in theory this should work with
any socket server.

_This is still a prototype, so the internal API might change quite a bit.
Please star and/or fork the github repo if you already find this useful._

This is _very loosely_ based on
(twisted-memcached)[https://github.com/dustin/twisted-memcached]
by Dustin Sallings, but doesn't actually share any code.

