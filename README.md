[![Build Status](https://travis-ci.org/botswana-harvard/getresults-astm.svg?branch=develop)](https://travis-ci.org/botswana-harvard/getresults-astm)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/getresults-astm/badge.svg?branch=develop)](https://coveralls.io/r/botswana-harvard/getresults-astm?branch=develop)
[![Code Health](https://landscape.io/github/botswana-harvard/getresults-astm/develop/landscape.svg?style=flat)](https://landscape.io/github/botswana-harvard/getresults-astm/develop)

# getresults-astm

ASTM interface for getresults using python-astm.

The sample message in the testdata folder is output from our implementation of Roche PSM.

The python-astm records classes are subclasses to accept data from PSM, which is rather incomplete in our implementation. For example, our implementation of PSM does not report birth date, gender ,etc. The testing panel is also not known by our implementation and just sends 'ALL'. Because of this we expect the order identifier to be in the ASTM output and matched to an existing order in the receiving database.

The dispatcher class is customized to save data into the getresults data model.

Missing data items, such as UTESTID's, can be created on the fly to avoid disruption in data flow. However creating
fake orders, aliquots, receive records and patient records is not ideal.

Unless the dispatcher class attribute create_dummy_data=True, missing data items in the receiving database will cause an exception.

Run the server

    # host = '192.168.1.1'
    # port = 20851
    python manage.py astm_server '192.168.1.1' 20851
