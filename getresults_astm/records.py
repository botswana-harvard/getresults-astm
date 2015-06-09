from astm import __version__
from astm.mapping import (
    Component, ConstantField, ComponentField, DateField, DateTimeField,
    IntegerField, SetField, TextField, Field
)
from astm.records import (
    HeaderRecord, PatientRecord, OrderRecord, ResultRecord, CommentRecord,
    TerminatorRecord
)


__all__ = ['Header', 'CommonPatient', 'CommonOrder',
           'CommonResult', 'CommonComment', 'Terminator']

Sender = Component.build(
    TextField(name='name', default='python-astm'),
    TextField(name='manufacturer', default=__version__),
    TextField(name='system', default=__version__),
    TextField(name='version', default=__version__)
)

PatientName = Component.build(
    TextField(name='last', length=50),
    TextField(name='first', length=50)
)

ResultOperator = Component.build(
    TextField(name='initials', length=25),
    TextField(name='name', length=25)
)


class TestField(Field):
    """Mapping field for integer values."""
    def _get_value(self, value):
        return str(value)

    def _set_value(self, value):
        if not isinstance(value, (list, )):
            try:
                value = self._get_value(value)
            except Exception:
                raise TypeError('List value expected, got %r' % value)
        return super(TestField, self)._set_value(value[3])


class Header(HeaderRecord):
    """ASTM header record."""
    sender = ComponentField(Sender)
    processing_id = ConstantField(default='P')
    version = ConstantField(default='E 1394-97')


class CommonPatient(PatientRecord):
    """ASTM patient record."""
    birthdate = DateField()
    laboratory_id = TextField(required=True, length=16)
    location = TextField(length=20)
    name = ComponentField(PatientName)
    practice_id = TextField(required=True, length=12)
    sex = SetField(values=('M', 'F', None, 'I'))
    special_2 = SetField(values=(0, 1), field=IntegerField())
    admission_date = DateTimeField(required=True)


class CommonOrder(OrderRecord):
    biomaterial = TextField(length=20)
    laboratory_field_2 = TextField(length=12)
    priority = SetField(default='S', values=('S', 'R'))
    sample_id = TextField(required=True, length=12)
    user_field_1 = TextField(length=20)
    user_field_2 = TextField(length=1024)
    test = TextField(length=5)
    created_at = DateTimeField(required=True)
    action_code = TextField(length=1, required=True)
    report_type = TextField(length=1, required=True)


class CommonResult(ResultRecord):
    abnormal_flag = TextField(required=True, length=1)
    completed_at = DateTimeField(required=True)
    instrument = TextField(required=True, length=5)
    operator = ComponentField(ResultOperator)
    status = SetField(default='F', values=('P', 'F'))
    test = TestField(required=True)
    value = TextField(required=True, length=20)


class CommonComment(CommentRecord):
    ctype = ConstantField(default='G')


class Terminator(TerminatorRecord):
    """ASTM terminator record."""
    pass
