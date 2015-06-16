import pytz

from uuid import uuid4

from django.conf import settings
from django.utils import timezone

from getresults.models import Result, ResultItem, PanelItem, Panel, Order, Utestid
from getresults_aliquot.models import Aliquot, AliquotType, AliquotCondition
from getresults_receive.models import Receive, Patient

from .models import Sender, UtestidMapping

tz = pytz.timezone(settings.TIME_ZONE)


class HeaderError(Exception):
    pass

__all__ = ['GetResultsDispatcherMixin', 'DmisDispatcherMixin']


class BaseDispatcherMixin(object):

    create_dummy_records = None  # if True create dummy patient, receive, aliquot and order

    def save_to_db(self, records):
        try:
            header_record = records['H']
            sender = self.sender(
                header_record.sender.name,
                ', '.join([s for s in header_record.sender])
            )
            patient_record = records['P']
            patient = self.patient(
                patient_record.practice_id,
                gender=patient_record.sex,
                dob=patient_record.birthdate,
                registration_datetime=patient_record.admission_date,
            )
            if records['O']:
                order_record = records['O']
                panel = self.panel(order_record.test)
                order = self.order(
                    order_record.sample_id,
                    order_record.created_at,
                    order_record.action_code,
                    order_record.report_type,
                    panel,
                    patient)
                if records['R']:
                    result_records = records['R']
                    result = None
                    for result_record in result_records:
                        if not result:
                            result = self.result(
                                order,
                                order_record.sample_id,
                                result_record.operator.name,
                                result_record.status,
                                result_record.instrument,
                            )
                        utestid = self.utestid(result_record.test, sender)
                        panel_item = self.panel_item(panel, utestid)
                        self.result_item(result, utestid, panel_item, result_record)
                    # add in missing utestid's
                    utestid_names = [p.utestid.name for p in PanelItem.objects.filter(panel=panel)]
                    result_utestid_names = [r.utestid.name for r in ResultItem.objects.filter(result=result)]
                    for name in utestid_names:
                        if name not in result_utestid_names:
                            utestid = Utestid.objects.get(name=name)
                            panel_item = self.panel_item(panel, utestid)
                            self.result_item(result, utestid, panel_item, None)
        except AttributeError:
            raise
        except Exception:
            # print(e)
            raise


class GetResultsDispatcherMixin(BaseDispatcherMixin):

    def sender(self, sender_name, sender_description):
        try:
            sender = Sender.objects.get(name=sender_name)
        except Sender.DoesNotExist:
            sender = Sender.objects.create(
                name=sender_name,
                description=sender_description)
        return sender

    def patient(self, patient_identifier, gender, dob, registration_datetime):
        try:
            patient = Patient.objects.get(patient_identifier=patient_identifier)
        except Patient.DoesNotExist:
            patient = None
            if self.create_dummy_records:
                patient = Patient.objects.create(
                    patient_identifier=patient_identifier,
                    gender=gender,
                    registration_datetime=tz.localize(registration_datetime),
                    dob=dob,
                )
        return patient

    def panel(self, name):
        try:
            panel = Panel.objects.get(name=name)
        except Panel.DoesNotExist:
            panel = Panel.objects.create(name=name)
        return panel

    def order(self, order_identifier, order_datetime, action_code, report_type, panel, patient):
        try:
            order = Order.objects.get(order_identifier=order_identifier)
        except Order.DoesNotExist:
            order = None
            if self.create_dummy_records:
                aliquot = self.aliquot(patient, None)
                order = Order.objects.create(
                    order_identifier=order_identifier,
                    order_datetime=tz.localize(order_datetime),
                    specimen_identifier=order_identifier,
                    action_code=action_code,
                    report_type=report_type,
                    panel=panel,
                    aliquot=aliquot)
        return order

    def aliquot(self, patient, order_identifier):
        """Creates a fake aliquot."""
        try:
            aliquot_type = AliquotType.objects.get(name='unknown')
        except AliquotType.DoesNotExist:
            aliquot_type = AliquotType.objects.create(name='unknown', numeric_code='00', alpha_code='00')
        try:
            aliquot_condition = AliquotCondition.objects.get(name='unknown')
        except AliquotCondition.DoesNotExist:
            aliquot_condition = AliquotCondition.objects.create(name='unknown', description='unknown')
        try:
            aliquot = Order.objects.get(
                order_identifier=order_identifier
            ).aliquot
        except Order.DoesNotExist:
            aliquot = None
            if self.create_dummy_records:
                aliquot_identifier = uuid4()
                receive = self.receive(patient, aliquot_identifier)
                aliquot = Aliquot.objects.create(
                    aliquot_identifier=aliquot_identifier,
                    aliquot_type=aliquot_type,
                    aliquot_condition=aliquot_condition,
                    receive=receive)
        return aliquot

    def receive(self, patient, aliquot_identifier):
        """Creates a fake receive record."""
        try:
            Receive.objects.get(
                patient=patient,
                receive_identifier=aliquot_identifier,
            )
        except Receive.DoesNotExist:
            receive = None
            if self.create_dummy_records:
                receive = Receive.objects.create(
                    receive_identifier=uuid4(),
                    receive_datetime=timezone.now(),
                    patient=patient
                )
        return receive

    def result(self, order, specimen_identifier, operator, status, instrument):
        try:
            result = Result.objects.get(order=order)
        except Result.DoesNotExist:
            result = Result.objects.create(
                order=order,
                result_identifier=uuid4(),
                specimen_identifier=specimen_identifier,
                status=status,
                operator=operator,
                analyzer_name=instrument
            )
        return result

    def utestid(self, sender_utestid_name, sender):
        try:
            utestid_mapping = UtestidMapping.objects.get(
                sender_utestid_name=sender_utestid_name, sender=sender)
            utestid = utestid_mapping.utestid
        except UtestidMapping.DoesNotExist:
            try:
                utestid = Utestid.objects.get(name=sender_utestid_name)
            except Utestid.DoesNotExist:
                utestid = Utestid.objects.create(
                    name=sender_utestid_name,
                    value_type='absolute',
                    value_datatype='string',
                    description='unknown from interface')
            utestid_mapping = UtestidMapping.objects.create(
                utestid=utestid,
                sender_utestid_name=sender_utestid_name,
                sender=sender)
        return utestid

    def panel_item(self, panel, utestid):
        try:
            panel_item = PanelItem.objects.get(
                panel=panel,
                utestid=utestid
            )
        except PanelItem.DoesNotExist:
            panel_item = PanelItem.objects.create(
                panel=panel,
                utestid=utestid
            )
        return panel_item

    def result_item(self, result, utestid, panel_item, result_record):
        try:
            result_item = ResultItem.objects.get(
                result=result,
                utestid=utestid)
        except ResultItem.DoesNotExist:
            result_item = ResultItem()
        result_item.result = result
        result_item.utestid = utestid
        result_item.specimen_identifier = result.specimen_identifier
        try:
            result_item.status = result_record.status
            result_item.operator = result_record.operator
            result_item.quantifier, result_item.value = panel_item.value_with_quantifier(result_record.value)
            result_item.result_datetime = tz.localize(result_record.completed_at)
        except AttributeError:
            pass
        result_item.save()
        return result_item


class DmisDispatcherMixin(BaseDispatcherMixin):

    def save_to_db(self, records):
        raise NotImplemented()
