[![Build Status](https://travis-ci.org/botswana-harvard/getresults-astm.svg?branch=develop)](https://travis-ci.org/botswana-harvard/getresults-astm)
[![Coverage Status](https://coveralls.io/repos/botswana-harvard/getresults-astm/badge.svg?branch=develop)](https://coveralls.io/r/botswana-harvard/getresults-astm?branch=develop)
[![Code Health](https://landscape.io/github/botswana-harvard/getresults-astm/develop/landscape.svg?style=flat)](https://landscape.io/github/botswana-harvard/getresults-astm/develop)

# getresults-astm

ASTM interface using `python-astm` that takes dispatchers from `getresults`, '`edc` and `dmis`.
See also module `getresults`.

As a django management command:

	import sys
	
	from django.core.management.base import BaseCommand
	
	# write your own dispatcher, see getresults.astm.dispatchers
	from getresults_astm.dispatchers import Dispatcher
	
	from astm.server import Server
	
	
	class Command(BaseCommand):
	    help = 'Load data from a folder containing panels.csv, utestids.csv, panel_items.csv'
	
	    def add_arguments(self, parser):
	        parser.add_argument('host', nargs=1, type=str)
	        parser.add_argument('port', nargs=1, type=str)
	
	    def handle(self, *args, **options):
	        host = str(options['host'][0]) or 'localhost'
	        port = int(options['port'][0]) or 20581
	        sys.stdout.write('Connecting to {} on port {} ...'.format(host, port))
	        server = Server(host=host, port=port, dispatcher=Dispatcher)
	        server.serve_forever()

Run the server

    # host = '192.168.1.1'
    # port = 20851
    python manage.py astm_server '192.168.1.1' 20851

The sample message in the folder `testdata` folder is output from our implementation of _Roche PSM_.

The `python-astm` record classes are subclasses to accept data from _PSM_, which is rather incomplete in our
deployment. For example, our implementation of PSM does not report birth date, gender ,etc. The testing
panel is also not known by our implementation and just sends 'ALL'. Because of this we expect the order
identifier to be in the ASTM output and matched to an existing order in the receiving database.


