#!/usr/bin/env python

from setuptools import setup, find_packages
from podcastbackup.meta import (__version__, __desc__, __author__,
                                __author_email__, __url__)

requires = open("requirements.txt").read().split()

setup(
    name='podcastbackup',
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "podcastbackup = podcastbackup.pb:run",
        ]
    },
    include_package_data=True,
    install_requires=requires,
    license="MIT License",
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

