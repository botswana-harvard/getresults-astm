import pytz

from django.conf import settings

from getresults.models import ResultItem, PanelItem, Utestid


tz = pytz.timezone(settings.TIME_ZONE)


class HeaderError(Exception):
    pass


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


class DmisDispatcherMixin(BaseDispatcherMixin):

    def save_to_db(self, records):
        raise NotImplemented()
