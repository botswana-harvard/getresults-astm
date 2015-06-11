import os

from astm import codec
from astm.constants import ENCODING
from astm.client import Client

from django.conf import settings

from getresults_astm.records import CommonPatient, Header, CommonOrder, CommonResult, Terminator

from getresults.models import Result, ResultItem

from getresults_astm.constants import ACCEPTED


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


class GrClient(Client):
    def __init__(self, *args, **kwargs):
        super(GrClient, self).__init__(emitter=test_emitter, *args, **kwargs)


# def string_emitter():
#     message = message.strip()
#     rectype = message[1]
#     if rectype == 'H':
#         yield Header(*decode_record(message[1:]))
#     elif rectype == 'P':
#         yield CommonPatient(*decode_record(message[1:]))
#     elif rectype == 'O':
#         yield CommonOrder(*decode_record(message[1:]))
#     elif rectype == 'R':
#         yield CommonResult(*decode_record(message[1:]))
#     elif rectype == 'L':
#         yield Terminator(*decode_record(message[1:]))
#     else:
#         yield decode_record(message[3:])


def db_emitter():
    h = Header()
    h.sender.name = 'getresults-astm'
    h.sender.manufacturer = 'Botswana-Harvard'
    h.sender.system = 'getresults-astm'
    h.sender.version = '0.1.0'
    yield h
    for result in Result.objects.filter(validation=ACCEPTED, sent=False):
        p = CommonPatient()
        yield p
        o = CommonOrder()
        yield o
        r = CommonResult()
        for result_item in ResultItem.objects.filter(result=result):
            yield r
    yield Terminator()
