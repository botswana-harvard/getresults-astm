# -*- coding: utf-8 -*-
import os
from setuptools import setup
from setuptools import find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='getresults-astm',
    version='0.1.0dev0',
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
        'Django>=1.8',
        'django-simple-history',
        'unipath>=1.1',
        'python-dateutil',
        'astm',
        'pytz',
        # '-e git+https://github.com/botswana-harvard/getresults@develop#egg=edc-base',
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
