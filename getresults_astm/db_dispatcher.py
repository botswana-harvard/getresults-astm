import pytz

from uuid import uuid4

from django.conf import settings
from django.utils import timezone

from getresults_astm.dispatcher import Dispatcher

tz = pytz.timezone(settings.TIME_ZONE)


class NotFoundError(Exception):
    pass


class DbDispatcher(Dispatcher):

    """Dispatches data to a DB coming in from analyzers/Roche PSM.
    """

    create_dummy_records = False  # if True create dummy patient, receive, aliquot and order

    def new_record_event(self, records):
        self.save_to_db(records)

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
                receive = self.receive(
                    patient,
                    order_record.sample_id,
                    order_record.sampled_at,
                    order_record.created_at)
                order = self.order(
                    order_record.sample_id,
                    order_record.created_at,
                    order_record.action_code,
                    order_record.report_type,
                    panel,
                    receive)
                if records['R']:
                    result_records = records['R']
                    result = None
                    for result_record in result_records:
                        if not result:
                            result = self.result(
                                order_record.laboratory_field_1,
                                order,
                                order_record.sample_id,
                                result_record.operator.name,
                                result_record.status,
                                result_record.instrument,
                            )
                        utestid_mapping = self.utestid_mapping(result_record.test, sender, panel.name)
                        utestid = utestid_mapping.utestid
                        self.panel_item(panel, utestid)
                        self.result_item(result, utestid, result_record)
                    self.update_utestid(self, result, panel)
        except AttributeError as err:
            print(str(err))
        except NotFoundError as err:
            print(str(err))
        except Exception as err:
            print(str(err))

    def update_utestid(self, result, panel):
        """Add in missing utestid's."""
        pass

    def sender(self, sender_name, sender_description):
        pass

    def patient(self, patient_identifier, gender, dob, registration_datetime):
        pass

    def panel(self, name):
        pass

    def order(self, order_identifier, order_datetime, action_code, report_type, panel, receive):
        pass

    def aliquot(self, receive, order_identifier):
        pass

    def receive(self, patient, receive_identifier, collection_datetime, receive_datetime):
        pass

    def result(self, result_identifier, order, specimen_identifier, operator, status, instrument):
        pass

    def utestid_mapping(self, sender_utestid_name, sender, panel_name):
        pass

    def utestid(self, name):
        pass

    def panel_item(self, panel, utestid):
        pass

    def result_item(self, result, utestid, result_record):
        pass
