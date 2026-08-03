#!/usr/bin/env python

from setuptools import setup, find_packages

REQUIRES = [
    'phenix-apps @ git+https://github.com/sandia-minimega/phenix-apps.git@main#egg=phenix-apps&subdirectory=src/python',
    'minimega',
]

ENTRIES = {
    'console_scripts' : [
        'phenix-app-windy = windy.windy:main',
    ]
}

setup(
    name                 = 'windy-app',
    version              = '0.0.1',
    description          = 'User app for wind project',
    license              = 'GPLv3',
    platforms            = 'Linux',
    classifiers          = [
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points         = ENTRIES,
    packages             = find_packages(),
    install_requires     = REQUIRES,
    include_package_data = True,

    package_data = {
        # Include mako template files found in all packages.
        "": ["*.mako"]
    }
)
