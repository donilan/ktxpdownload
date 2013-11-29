#!/usr/bin/env python

import sys, os

from setuptools import setup, find_packages

setup (
    name = 'ktxpdownload',
    version = '0.1',
    description = 'Auto download Anime on bt.ktxp.com',
    author = 'Doni',
    author_email = 'd@ii2d.com',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'ktxpdownload = ktxpdownload.main:main',
        ]
    },
)
