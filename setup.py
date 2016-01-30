#!/usr/bin/env python

from podcastbackup.meta import (__version__, __desc__, __author__,
                                __author_email__, __url__)
from glob import glob
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'podcastbackup',
]

requires = open("requirements.txt").read().split()

setup(
    name='podcastbackup',
    version=__version__,
    description=__desc__,
    long_description_markdown_filename='README.md',
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'podcastbackup': 'podcastbackup'},
    entry_points={
        "console_scripts": [
            "podcastbackup = podcastbackup.pb:run",
        ]
    },
    include_package_data=True,
    setup_requires=['setuptools-markdown'],
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),
)

