import pytz

from django.conf import settings

from getresults.models import Result, ResultItem, PanelItem, Panel, Order, Utestid

from .models import Sender, UtestidMapping

tz = pytz.timezone(settings.TIME_ZONE)


class DispatcherDbMixin(object):

    records = {}

    def save_to_db(self, header=None, patient=None, order=None, results=None, comment=None):
        header_record = header or self.records['H']
        # patient_record = patient or self.records['P']
        order_record = order or self.records['O']
        result_records = results or self.records['R']
        sender = self.sender(header_record.sender)
        panel = self.panel(order_record.test)
        order = self.order(order_record.sample_id, panel)
        result = None
        for result_record in result_records:
            if not result:
                result = self.result(
                    order, order_record.sample_id, order_record.sample_id, result_record.operator)
            utestid = self.utestid(result_record.test, sender)
            panel_item = self.panel_item(panel, utestid)
            self.result_item(result, utestid, panel_item, result_record)

    def sender(self, name):
        try:
            sender = Sender.objects.get(name=name)
        except Sender.DoesNotExist:
            sender = Sender.objects.create(name=name)
        return sender

    def panel(self, name):
        try:
            panel = Panel.objects.get(name=name)
        except Panel.DoesNotExist:
            panel = Panel.objects.create(name=name)
        return panel

    def order(self, order_identifier, panel):
        try:
            order = Order.objects.get(order_identifier=order_identifier, panel=panel)
        except Order.DoesNotExist:
            order = Order.objects.create(
                order_identifier=order_identifier,
                specimen_identifier=order_identifier,
                panel=panel)
        return order

    def result(self, order, result_identifier, specimen_identifier, operator):
        try:
            result = Result.objects.get(order=order)
        except Result.DoesNotExist:
            result = Result.objects.create(
                order=order,
                result_identifier=result_identifier,
                specimen_identifier=specimen_identifier,
                status=None,
                operator=operator,
            )
        return result

    def utestid(self, name, sender):
        try:
            utestid_mapping = UtestidMapping.objects.get(utestid_name=name, sender=sender)
            utestid = utestid_mapping.utestid
        except UtestidMapping.DoesNotExist:
            try:
                utestid = Utestid.objects.get(name=name)
            except Utestid.DoesNotExist:
                utestid = Utestid.objects.create(
                    name=name,
                    value_type='absolute',
                    value_datatype='string',
                    description='unknown from interface')
            utestid_mapping = UtestidMapping.objects.create(
                utestid=utestid,
                utestid_name=name,
                sender=sender)
        return utestid

    def panel_item(self, panel, utestid):
        try:
            panel_item = PanelItem.objects.get(
                panel=panel,
                utestid=utestid)
        except PanelItem.DoesNotExist:
            panel_item = PanelItem.objects.create(
                panel=panel,
                utestid=utestid)
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
        result_item.status = None
        result_item.operator = result_record.operator
        result_item.quantifier, result_item.value = panel_item.value_with_quantifier(result_record.value)
        result_item.result_datetime = tz.localize(result_record.completed_at)
        result_item.save()
        return result_item
