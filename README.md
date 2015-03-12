Helper for creating memcached binary protocol servers in Python.

Example server uses gevent, but in theory this should work with
any socket server.

*This is still a prototype, so the internal API might change quite a bit.
Please star and/or fork the github repo if you already find this useful.*

Specifications and related software:

 * [Memcache Binary Protocol](https://code.google.com/p/memcached/wiki/MemcacheBinaryProtocol)
 * [twisted-memcached](https://github.com/dustin/twisted-memcached)
 * [pyermc](https://github.com/upsight/pyermc)
 * [pylibmc](http://sendapatch.se/projects/pylibmc/)
 * ...

