from astm.server import BaseRecordsDispatcher

from getresults.dispatchers import GetResultsDispatcherMixin
from getresults.models import PanelItem, ResultItem, Utestid
from getresults_astm.mixins import DmisDispatcherMixin
from getresults_astm.records import CommonOrder, CommonPatient, CommonResult, Header, CommonComment


class Dispatcher(BaseRecordsDispatcher):

    records = {}

    def __init__(self, encoding=None):
        super(Dispatcher, self).__init__(encoding)

    def on_header(self, values):
        self.records = {
            'H': Header(*values),
            'P': None,
            'O': None,
            'R': [],
        }

    def on_patient(self, values):
        if self.records['P']:
            self.save_to_db(self.records)
        self.records = {
            'H': self.records['H'],
            'P': CommonPatient(*values),
            'O': None,
            'R': [],
        }

    def on_order(self, values):
        """Saves to db then resets R and O records for a new order."""
        if self.records['O']:
            self.save_to_db(self.records)
        self.records = {
            'H': self.records['H'],
            'P': self.records['P'],
            'O': CommonOrder(*values),
            'R': [],
        }

    def on_result(self, values):
        """Appends a result for the current order."""
        self.records['R'].append(CommonResult(*values))

    def on_comment(self, values):
        self.records['C'].append(CommonComment(*values))

    def on_terminator(self, record):
        if self.records:
            self.save_to_db(self.records)
        self.records = {}


class GetResultsDispatcher(GetResultsDispatcherMixin, Dispatcher):

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
                        utestid_mapping = self.utestid_mapping(result_record.test, sender, panel.name)
                        utestid = utestid_mapping.utestid
                        panel_item = self.panel_item(panel, utestid)
                        self.result_item(result, utestid, result_record)
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


class DmisDispatcher(DmisDispatcherMixin, Dispatcher):
    pass
