import os

from astm import codec
from astm.constants import ENCODING
from astm.client import Client

from django.conf import settings

from getresults_astm.records import CommonPatient, Header, CommonOrder, CommonResult, Terminator


def decode_record(r):
    return codec.decode_record(r.encode(), ENCODING)


def test_emitter():
    with open(os.path.join(settings.BASE_DIR, 'testdata/sample_message.txt'), 'r') as f:
        for message in f.readlines():
            message = message.strip()
            rectype = message[1]
            if rectype == 'H':
                yield Header(*decode_record(message[1:]))
            elif rectype == 'P':
                yield CommonPatient(*decode_record(message[1:]))
            elif rectype == 'O':
                yield CommonOrder(*decode_record(message[1:]))
            elif rectype == 'R':
                yield CommonResult(*decode_record(message[1:]))
            elif rectype == 'L':
                yield Terminator(*decode_record(message[1:]))
            else:
                yield decode_record(message[3:])
