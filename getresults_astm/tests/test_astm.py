from django.test import TestCase

from astm import codec
from astm.constants import ENCODING

from getresults.models import Result, ResultItem, Panel, PanelItem, Utestid, Order

from getresults.utils import (
    load_panel_items_from_csv, load_utestids_from_csv, load_panels_from_csv
)

from ..mixins import DispatcherDbMixin
from ..records import CommonOrder, CommonResult, CommonPatient, Header


def decode_record(r):
    return codec.decode_record(r.encode(), ENCODING)


class TestGetresult(TestCase):

    def setUp(self):
        """Load testdata."""
        load_panels_from_csv()
        load_utestids_from_csv()
        load_panel_items_from_csv()

    def test_mixin_db_update_single(self):
        mixin = DispatcherDbMixin()
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '2P|1|WT33721|||^||||||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        message = '3O|1|WT33721||ALL|R|20150108072200|||||X||||1||||||||||F'
        order = CommonOrder(*decode_record(message[1:]))
        message = '4R|1|^^^ALPL^^^^148.1|44.42893|||N||F||^System||20150107072208|148.1'
        result = CommonResult(*decode_record(message[1:]))
        mixin.save_to_db(header, patient, order, [result])
        self.assertGreater(Panel.objects.filter(name='ALL').count(), 0)
        panel = Panel.objects.get(name='ALL')
        self.assertGreater(Order.objects.filter(panel=panel).count(), 0)
        order = Order.objects.get(panel=panel)
        self.assertGreater(Utestid.objects.filter().count(), 0)
        utestid = Utestid.objects.get(name='ALPL')
        self.assertGreater(PanelItem.objects.filter(panel=panel, utestid=utestid).count(), 0)
        self.assertGreater(Result.objects.filter(order__order_identifier='WT33721').count(), 0)
        self.assertGreater(ResultItem.objects.filter(value='44.42893').count(), 0)

    def test_mixin_db_update_multi(self):
        mixin = DispatcherDbMixin()
        orders = []
        results = []
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '2P|1|WT33721|||^||||||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        message = '3O|1|WT33721||ALL|R|20150108072200|||||X||||1||||||||||F'
        order = CommonOrder(*decode_record(message[1:]))
        message = '5R|2|^^^CL-I^^^^148.1|105.0383|||N||F||^System||20150107072206|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '6R|3|^^^CO2-L^^^^148.1|16.95361|||N||F||^System||20150107072207|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '7R|4|^^^CREJ^^^^148.1|62.69189|||N||F||^System||20150107072209|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '0R|5|^^^NA-I^^^^148.1|132.5616|||N||F||^System||20150107072205|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '1R|6|^^^PHOS^^^^148.1|1.597954|||N||F||^System||20150107072208|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '2R|7|^^^UREL^^^^148.1|3.188942|||N||F||^System||20150107072207|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        self.assertIsNone(mixin.save_to_db(header, patient, order, results))

        message = '3P|2|WT36840|||^||||||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        message = '4O|1|WT36840||ALL|R|20150108072200|||||X||||1||||||||||F'
        order = CommonOrder(*decode_record(message[1:]))
        message = '5R|1|^^^ALPL^^^^148.1|67.95654|||N||F||^System||20150107072213|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '6R|2|^^^ALTL^^^^148.1|10.55941|||N||F||^System||20150107072212|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '7R|3|^^^CL-I^^^^148.1|106.7179|||N||F||^System||20150107072211|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '0R|4|^^^CO2-L^^^^148.1|20.16562|||N||F||^System||20150107072211|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '1R|5|^^^CREJ^^^^148.1|56.58432|||N||F||^System||20150107072214|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '2R|6|^^^K-I^^^^148.1|4.395318|||N||F||^System||20150107072210|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '3R|7|^^^NA-I^^^^148.1|136.6808|||N||F||^System||20150107072209|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '4R|8|^^^PHOS^^^^148.1|1.356225|||N||F||^System||20150107072213|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        message = '5R|9|^^^UREL^^^^148.1|4.367106|||N||F||^System||20150107072212|148.1'
        results.append(CommonResult(*decode_record(message[1:])))
        self.assertIsNone(mixin.save_to_db(header, patient, order, results))
