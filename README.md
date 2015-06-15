[![Build Status](https://travis-ci.org/botswana-harvard/getresults-astm.svg?branch=develop)](https://travis-ci.org/botswana-harvard/getresults-astm)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/getresults-astm/badge.svg?branch=develop)](https://coveralls.io/r/botswana-harvard/getresults-astm?branch=develop)
[![Code Health](https://landscape.io/github/botswana-harvard/getresults-astm/develop/landscape.svg?style=flat)](https://landscape.io/github/botswana-harvard/getresults-astm/develop)

# getresults-astm

ASTM interface for getresults using python-astm.

The sample message in the testdata folder is output from Roche PSM. The python-astm records are subclasses to accept
data from PSM, which is rather incomplete in our implementation. For example, PSM does not report the panel to us (just
sends 'ALL')

We expect the order identifier to be in the output and matched to an existing order in the database.

Run the server

    # host = '192.168.1.1'
    # port = 20851
    python manage.py astm_server '192.168.1.1' 20851
