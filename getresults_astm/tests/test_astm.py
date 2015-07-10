import pytz

from dateutil.parser import parse
from uuid import uuid4

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from astm import codec
from astm.constants import ENCODING

from getresults.models import (
    Result, ResultItem, Panel, PanelItem, Utestid, Order, Sender, UtestidMapping)
from getresults_aliquot.models import Aliquot, AliquotType
from getresults_receive.models import Patient, Receive
from getresults.utils import (
    load_panel_items_from_csv, load_utestids_from_csv, load_panels_from_csv
)

from getresults.astm.dispatchers import GetResultsDispatcher
from ..records import CommonOrder, CommonResult, CommonPatient, Header

tz = pytz.timezone(settings.TIME_ZONE)


def decode_record(r):
    return codec.decode_record(r.encode(), ENCODING)


class TestGetresult(TestCase):

    def setUp(self):
        """Load testdata."""
        load_panels_from_csv()
        load_utestids_from_csv()
        load_panel_items_from_csv()

    def test_dispatcher_db_update_single(self):
        GetResultsDispatcher.create_dummy_records = True
        dispatcher = GetResultsDispatcher()
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '2P|1|WT33721|||^||||||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        message = '3O|1|WT33721||ALL|R|20150108072200|||||X||||1||||||||||F'
        order = CommonOrder(*decode_record(message[1:]))
        message = '4R|1|^^^ALPL^^^^148.1|44.42893|||N||F||^System||20150107072208|148.1'
        result = CommonResult(*decode_record(message[1:]))
        records = {
            'H': header,
            'P': patient,
            'O': order,
            'R': [result]}
        dispatcher.save_to_db(records)
        self.assertGreater(Panel.objects.filter(name='ALL').count(), 0)
        panel = Panel.objects.get(name='ALL')
        self.assertGreater(Order.objects.filter(panel=panel).count(), 0)
        order = Order.objects.get(panel=panel)
        self.assertGreater(Utestid.objects.filter().count(), 0)
        utestid = Utestid.objects.get(name='ALPL')
        self.assertGreater(PanelItem.objects.filter(panel=panel, utestid=utestid).count(), 0)
        self.assertGreater(Result.objects.filter(order__order_identifier='WT33721').count(), 0)
        self.assertGreater(ResultItem.objects.filter(value='44.42893').count(), 0)

    def test_dispatcher_db_update_multi(self):
        GetResultsDispatcher.create_dummy_records = True
        dispatcher = GetResultsDispatcher()
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
        records = {
            'H': header,
            'P': patient,
            'O': order,
            'R': results}
        self.assertIsNone(dispatcher.save_to_db(records))

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
        records = {
            'H': header,
            'P': patient,
            'O': order,
            'R': results}
        self.assertIsNone(dispatcher.save_to_db(records))

    def test_no_header1(self):
        GetResultsDispatcher.create_dummy_records = True
        dispatcher = GetResultsDispatcher()
        records = {
            'H': None,
            'P': None,
            'O': None,
            'R': []}
        self.assertRaises(AttributeError, dispatcher.save_to_db, records)

    def test_no_header2(self):
        GetResultsDispatcher.create_dummy_records = True
        dispatcher = GetResultsDispatcher()
        message = '3P|2|WT36840|||^||||||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        records = {
            'H': None,
            'P': patient,
            'O': None,
            'R': []}
        self.assertRaises(AttributeError, dispatcher.save_to_db, records)

    def test_patient_as_list(self):
        GetResultsDispatcher.create_dummy_records = True
        dispatcher = GetResultsDispatcher()
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '3P|2|WT36840|||^||||||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        records = {
            'H': header,
            'P': [patient],
            'O': None,
            'R': []}
        self.assertRaises(AttributeError, dispatcher.save_to_db, records)

    def test_patient(self):
        GetResultsDispatcher.create_dummy_records = True
        dispatcher = GetResultsDispatcher()
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '3P|2|WT36840|||^||19640505|F|||||||||||||||20150108072200|||||||||'
        patient_record = CommonPatient(*decode_record(message[1:]))
        records = {
            'H': header,
            'P': patient_record,
            'O': None,
            'R': []}
        dispatcher.save_to_db(records)
        patient = Patient.objects.get(patient_identifier=patient_record.practice_id)
        self.assertEqual(patient.registration_datetime, tz.localize(patient_record.admission_date))
        self.assertEqual(patient.dob, patient_record.birthdate.date())
        self.assertEqual(patient.gender, patient_record.sex)

    def test_order_save(self):
        GetResultsDispatcher.create_dummy_records = True
        dispatcher = GetResultsDispatcher()
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '3P|2|WT36840|||^||19640505|F|||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        message = '3O|1|WT33721||ALL|R|20150108072200|||||X||||1||||||||||F'
        order_record = CommonOrder(*decode_record(message[1:]))
        records = {
            'H': header,
            'P': patient,
            'O': order_record,
            'R': []}
        dispatcher.save_to_db(records)
        order = Order.objects.get(order_identifier=order_record.sample_id)
        self.assertEqual(order.order_datetime, tz.localize(order_record.created_at))
        self.assertEqual(order.panel.name, order_record.test)
        self.assertEqual(order.action_code, order_record.action_code)
        self.assertEqual(order.report_type, order_record.report_type)

    def test_result_save(self):
        GetResultsDispatcher.create_dummy_records = True
        dispatcher = GetResultsDispatcher()
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '3P|2|WT36840|||^||19640505|F|||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        message = '3O|1|WT33721||ALL|R|20150108072200|||||X||||1||||||||||F'
        order_record = CommonOrder(*decode_record(message[1:]))
        result_record = []
        message = '4R|1|^^^ALPL^^^^148.1|44.42893|||N||F||^System||20150107072208|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '5R|1|^^^ALPL^^^^148.1|67.95654|||N||F||^System||20150107072213|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '6R|2|^^^ALTL^^^^148.1|10.55941|||N||F||^System||20150107072212|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '7R|3|^^^CL-I^^^^148.1|106.7179|||N||F||^System||20150107072211|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '0R|4|^^^CO2-L^^^^148.1|20.16562|||N||F||^System||20150107072211|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '1R|5|^^^CREJ^^^^148.1|56.58432|||N||F||^System||20150107072214|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '2R|6|^^^K-I^^^^148.1|4.395318|||N||F||^System||20150107072210|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '3R|7|^^^NA-I^^^^148.1|136.6808|||N||F||^System||20150107072209|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '4R|8|^^^PHOS^^^^148.1|1.356225|||N||F||^System||20150107072213|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '5R|9|^^^UREL^^^^148.1|4.367106|||N||F||^System||20150107072212|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        records = {
            'H': header,
            'P': patient,
            'O': order_record,
            'R': result_record}
        dispatcher.save_to_db(records)
        order = Order.objects.get(order_identifier=order_record.sample_id)
        result_record = result_record[0]
        result = Result.objects.get(order=order)
#         self.assertEqual(result.collection_datetime, tz.localize(order_record.created_at))
        self.assertEqual(result.operator, result_record.operator.name)
        self.assertEqual(result.status, result_record.status)
        self.assertEqual(result.analyzer_name, result_record.instrument)

    def test_no_create_dummy(self):
        GetResultsDispatcher.create_dummy_records = False
        dispatcher = GetResultsDispatcher()
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '3P|2|WT36840|||^||19640505|F|||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        message = '3O|1|WT33721||ALL|R|20150108072200|||||X||||1||||||||||F'
        order_record = CommonOrder(*decode_record(message[1:]))
        message = '5R|9|^^^UREL^^^^148.1|4.367106|||N||F||^System||20150107072212|148.1'
        result_record = CommonResult(*decode_record(message[1:]))
        records = {
            'H': header,
            'P': patient,
            'O': order_record,
            'R': [result_record]}
        self.assertRaises(ValueError, dispatcher.save_to_db, records)

    def test_find_existing_order(self):
        GetResultsDispatcher.create_dummy_records = True
        dispatcher = GetResultsDispatcher()
        patient = Patient.objects.create(
            patient_identifier='123456789',
            registration_datetime=timezone.now())
        receive = Receive.objects.create(
            receive_identifier=uuid4(),
            patient=patient,
            receive_datetime=timezone.now(),
        )
        aliquot_type = AliquotType.objects.create(alpha_code='WB', numeric_code='02')
        aliquot = Aliquot.objects.create(
            aliquot_identifier='123456789',
            receive=receive,
            aliquot_type=aliquot_type)
        panel = Panel.objects.create(name='chem')
        new_order = Order.objects.create(
            order_identifier='WT33721',
            order_datetime=tz.localize(parse('20150108072200')),
            panel=panel,
            aliquot=aliquot)
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '3P|2|WT36840|||^||19640505|F|||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        message = '3O|1|WT33721||ALL|R|20150108072200|||||X||||1||||||||||F'
        order_record = CommonOrder(*decode_record(message[1:]))
        message = '5R|9|^^^UREL^^^^148.1|4.367106|||N||F||^System||20150107072212|148.1'
        result_record = CommonResult(*decode_record(message[1:]))
        records = {
            'H': header,
            'P': patient,
            'O': order_record,
            'R': [result_record]}
        dispatcher.save_to_db(records)
        result = ResultItem.objects.get(value='4.367106').result
        self.assertEquals(new_order.order_identifier, result.order.order_identifier)
        self.assertNotEqual(new_order.panel.name, order_record.test)

    def test_adds_unresulted_utestid_from_panel(self):
        Panel.objects.all().delete()
        UtestidMapping.objects.all().delete()
        Utestid.objects.all().delete()
        message = '1H|\^&|||PSM^Roche Diagnostics^PSM^2.01.00.c|||||||P||20150108072227'
        header = Header(*decode_record(message[1:]))
        message = '3P|2|WT36840|||^||19640505|F|||||||||||||||20150108072200|||||||||'
        patient = CommonPatient(*decode_record(message[1:]))
        message = '3O|1|NEWORDER||CHEM|R|20150108072200|||||X||||1||||||||||F'
        order_record = CommonOrder(*decode_record(message[1:]))
        sender = Sender.objects.create(name='PSM', description='PSM,Roche Diagnostics,PSM,2.01.00.c')
        panel = Panel.objects.create(name='CHEM')
        self.create_panel_items(panel, sender)
        records = {
            'H': header,
            'P': patient,
            'O': order_record,
            'R': self.result_records}
        patient = Patient.objects.create(
            patient_identifier='123456789',
            registration_datetime=timezone.now())
        receive = Receive.objects.create(
            receive_identifier=uuid4(),
            patient=patient,
            receive_datetime=timezone.now(),
        )
        aliquot_type = AliquotType.objects.create(alpha_code='WB', numeric_code='02')
        aliquot = Aliquot.objects.create(
            aliquot_identifier='123456789',
            receive=receive,
            aliquot_type=aliquot_type)
        order = Order.objects.create(
            order_identifier='NEWORDER',
            order_datetime=timezone.now(),
            panel=panel,
            aliquot=aliquot)
        GetResultsDispatcher.create_dummy_records = None
        dispatcher = GetResultsDispatcher()
        dispatcher.save_to_db(records)
        result = Result.objects.get(order=order)
        self.assertEquals(ResultItem.objects.filter(result=result).count(), 9)

    @property
    def result_records(self):
        result_record = []
        message = '5R|1|^^^ALPL^^^^148.1|67.95654|||N||F||^System||20150107072213|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '6R|2|^^^ALTL^^^^148.1|10.55941|||N||F||^System||20150107072212|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '7R|3|^^^CL-I^^^^148.1|106.7179|||N||F||^System||20150107072211|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '0R|4|^^^CO2-L^^^^148.1|20.16562|||N||F||^System||20150107072211|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '1R|5|^^^CREJ^^^^148.1|56.58432|||N||F||^System||20150107072214|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '2R|6|^^^K-I^^^^148.1|4.395318|||N||F||^System||20150107072210|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '3R|7|^^^NA-I^^^^148.1|136.6808|||N||F||^System||20150107072209|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '4R|8|^^^PHOS^^^^148.1|1.356225|||N||F||^System||20150107072213|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        message = '5R|9|^^^UREL^^^^148.1|4.367106|||N||F||^System||20150107072212|148.1'
        result_record.append(CommonResult(*decode_record(message[1:])))
        return result_record

    def create_panel_items(self, panel, sender):
        utestid = Utestid.objects.create(
            name='ALPL', description='ALPL', value_type='absolute', value_datatype='decimal', precision=2)
        UtestidMapping.objects.create(
            sender=sender,
            utestid=utestid,
            sender_utestid_name='ALPL',
            panel=panel)
        PanelItem.objects.create(
            panel=panel,
            utestid=utestid
        )
        utestid = Utestid.objects.create(
            name='ALTL', description='ALTL', value_type='absolute', value_datatype='decimal', precision=2)
        UtestidMapping.objects.create(
            sender=sender,
            utestid=utestid,
            sender_utestid_name='ALTL',
            panel=panel)
        PanelItem.objects.create(
            panel=panel,
            utestid=utestid,
        )
        utestid = Utestid.objects.create(
            name='CL-I', description='CL-I', value_type='absolute', value_datatype='decimal', precision=2)
        UtestidMapping.objects.create(
            sender=sender,
            utestid=utestid,
            sender_utestid_name='CL-I',
            panel=panel)
        PanelItem.objects.create(
            panel=panel,
            utestid=utestid,
        )
        utestid = Utestid.objects.create(
            name='CO2-L', description='CO2-L', value_type='absolute', value_datatype='decimal', precision=2)
        UtestidMapping.objects.create(
            sender=sender,
            utestid=utestid,
            sender_utestid_name='CO2-L',
            panel=panel)
        PanelItem.objects.create(
            panel=panel,
            utestid=utestid,
        )
        utestid = Utestid.objects.create(
            name='CREJ', description='CREJ', value_type='absolute', value_datatype='decimal', precision=2)
        UtestidMapping.objects.create(
            sender=sender,
            utestid=utestid,
            sender_utestid_name='CREJ',
            panel=panel)
        PanelItem.objects.create(
            panel=panel,
            utestid=utestid,
        )
        utestid = Utestid.objects.create(
            name='K-I', description='K-I', value_type='absolute', value_datatype='decimal', precision=2)
        UtestidMapping.objects.create(
            sender=sender,
            utestid=utestid,
            sender_utestid_name='K-I',
            panel=panel)
        PanelItem.objects.create(
            panel=panel,
            utestid=utestid,
        )
        utestid = Utestid.objects.create(
            name='NA-I', description='NA-I', value_type='absolute', value_datatype='decimal', precision=2)
        UtestidMapping.objects.create(
            sender=sender,
            utestid=utestid,
            sender_utestid_name='NA-I',
            panel=panel)
        PanelItem.objects.create(
            panel=panel,
            utestid=utestid,
        )
        utestid = Utestid.objects.create(
            name='PHOS', description='PHOS', value_type='absolute', value_datatype='decimal', precision=2)
        UtestidMapping.objects.create(
            sender=sender,
            utestid=utestid,
            sender_utestid_name='PHOS',
            panel=panel)
        PanelItem.objects.create(
            panel=panel,
            utestid=utestid
        )
        utestid = Utestid.objects.create(
            name='UREL', description='UREL', value_type='absolute', value_datatype='decimal', precision=2)
        UtestidMapping.objects.create(
            sender=sender,
            utestid=utestid,
            sender_utestid_name='UREL',
            panel=panel)
        PanelItem.objects.create(
            panel=panel,
            utestid=utestid,
        )
