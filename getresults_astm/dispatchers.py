from astm.server import BaseRecordsDispatcher

from getresults_astm.records import CommonOrder, CommonPatient, CommonResult, Header, CommonComment

from .mixins import DispatcherDbMixin


class Dispatcher(DispatcherDbMixin, BaseRecordsDispatcher):

    def __init__(self, encoding=None):
        super(Dispatcher, self).__init__(encoding)

    def on_header(self, values):
        self.records = {
            'H': Header(*values),
            'P': None,
            'O': [],
            'R': [],
        }

    def on_patient(self, values):
        if self.records:
            self.save_to_db()
        self.records = {
            'H': self.records['H'],
            'P': CommonPatient(*values),
            'O': [],
            'R': [],
        }

    def on_order(self, values):
        if self.records['O']:
            self.save_to_db()
        self.records = {
            'H': self.records['H'],
            'P': self.records['P'],
            'O': [CommonOrder(*values)],
            'R': [],
        }

    def on_result(self, values):
        self.records['R'].append(CommonResult(*values))

    def on_comment(self, values):
        self.records['C'].append(CommonComment(*values))

    def on_terminator(self, record):
        if self.records:
            self.save_to_db()
