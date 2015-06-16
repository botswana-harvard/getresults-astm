from astm.server import BaseRecordsDispatcher

from getresults_astm.records import CommonOrder, CommonPatient, CommonResult, Header, CommonComment


from getresults_astm.mixins import GetResultsDispatcherMixin, DmisDispatcherMixin


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
    pass


class DmisDispatcher(DmisDispatcherMixin, Dispatcher):
    pass
