from setuptools import setup, find_packages
from gmcbs import __version__

setup(
    name='gevent-memcached-server',
    version=__version__,
    description='gevent based memcached binary protocol server',
    url='https://github.com/jvtm/gevent-memcached-server',
    author='Jyrki Muukkonen',
    author_email='jvtm@kruu.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='gevent memcached memcache binary protocol server',
    packages=find_packages(),
    install_requires=['gevent'],
    entry_points={
        'console_scripts': [
            'gevent-memcached = gmcbs.server:main',
        ],
    }
)
