from setuptools import setup, find_packages
from gmcbs import __version__

setup(
    name="gevent-memcached-server",
    version=__version__,
    packages=find_packages(),
    install_requires=['gevent'],
    entry_points={
        'console_scripts': [
            'gevent-memcached = gmcbs.server:main',
        ],
    }
)
