# -*- coding: utf-8 -*-
import os
from setuptools import setup
from setuptools import find_packages

from getresults_astm.version import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='getresults-astm',
    version=__version__,
    author=u'Erik van Widenfelt',
    author_email='ew2789@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://github/botswana-harvard/getresults-astm',
    license='GPL license, see LICENSE',
    description='ASTM analyzer interface for getresults using python-astm',
    long_description=README,
    zip_safe=False,
    keywords='ASTM getresults LIMS LIS interface',
    install_requires=[
        'unipath>=1.1',
        'python-dateutil',
        'astm',
        'pytz',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
