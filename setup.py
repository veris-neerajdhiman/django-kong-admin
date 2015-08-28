#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pip.req import parse_requirements

import kong_admin

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = kong_admin.__version__

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open(os.path.join(BASE_DIR, 'README.rst'),).read()
history = open(os.path.join(BASE_DIR, 'CHANGELOG.rst')).read().replace('.. :changelog:', '')

requirements = [str(ir.req) for ir in parse_requirements(os.path.join(BASE_DIR, 'requirements.txt'), session=False)]

setup(
    name='django-kong-admin',
    version=version,
    description="""A reusable Django App to manage a Kong service (http://getkong.org)""",
    long_description=readme + '\n\n' + history,
    author='Dirk Moors',
    author_email='dirk.moors@vikingco.com',
    url='https://github.com/vikingco/django-kong-admin',
    packages=[
        'kong_admin',
    ],
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='django-kong-admin',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
