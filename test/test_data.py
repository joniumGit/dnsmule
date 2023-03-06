import pytest

from dnsmule.definitions import Data, RRType


@pytest.fixture(autouse=True)
def clear_adapters():
    yield
    Data._adapters.clear()


def test_data_repr_create_simple():
    d = Data(type=RRType.TXT, value='test')
    d1 = eval(repr(d))
    assert d1.value == d.value
    assert d1.type == d.type
    assert d1 == d


def test_data_repr_create_kwargs():
    d = Data(type=RRType.TXT, value='test', a='b', c=1)
    d1 = eval(repr(d))
    assert d1 == d


def test_data_to_text_equals_value():
    d = Data(type=RRType.TXT, value='a')
    assert d.to_text() is d.value, 'Data.to_text() returned an unexpected object'


def test_data_to_bytes_equals_value_bytes():
    d = Data(type=RRType.TXT, value='a')
    assert d.to_bytes() == d.value.encode('utf-8'), 'Data.to_text() returned an unexpected result'


def test_data_hashed_by_type():
    d = Data(type=RRType.TXT, value='b')
    assert hash(d) == hash(RRType.TXT), 'Data hash result was unexpected'


def test_data_does_not_equal_other_types():
    d = Data(type=RRType.TXT, value='b')
    assert 'b' != d, 'String equaled data'
    assert 16 != d, 'Int equaled data'


def test_data_does_not_equal_other_data_types():
    d1 = Data(type=RRType.TXT, value='b')
    d2 = Data(type=RRType.A, value='b')
    assert d1 != d2, 'Datas with different types were equal'


def test_data_register_adapter():
    d = Data(type=RRType.A, value='dummy', original=100)

    def get_from_data_adapter(self, item: str):
        assert self is d, 'Self reference not correct'
        return self.data[item]

    Data.register_adapter(get_from_data_adapter)

    assert d.original is d.data['original'], 'Failed to call adapter correctly'


def test_data_register_adapter_prefers_first():
    d = Data(type=RRType.A, value='dummy', original=100)

    def get_from_data_adapter(self, item: str):
        return self.data[item]

    def get_from_data_adapter_2(__, _: str):
        raise AssertionError('Should not get to adapter 2')

    Data.register_adapter(get_from_data_adapter)
    Data.register_adapter(get_from_data_adapter_2)

    assert d.original is d.data['original'], 'Failed to call adapter correctly'


def test_data_register_multiple_adapters():
    d = Data(type=RRType.A, value='dummy', original=100)

    def get_from_data_adapter(self, item: str):
        return self.data.get(item, None)

    def get_from_data_adapter_as_getter(self, item: str):
        return lambda: self.data[item.removeprefix('get_')]

    Data.register_adapter(get_from_data_adapter)
    Data.register_adapter(get_from_data_adapter_as_getter)

    assert d.original is d.data['original'], 'Failed to call first adapter correctly'
    assert d.get_original() is d.data['original'], 'Failed to call second adapter correctly'


def test_data_register_adapter_throwing_stops_early():
    d = Data(type=RRType.A, value='dummy', original=100)

    def adapter_1(__, _: str):
        raise ValueError('test')

    def adapter_2(__, _: str):
        raise AssertionError('Should not get to adapter 2')

    Data.register_adapter(adapter_1)
    Data.register_adapter(adapter_2)

    with pytest.raises(ValueError) as e:
        d.get_original()

    assert e.value.args[0] == 'test', 'Raised an unexpected value error'


def test_data_register_adapter_not_found():
    d = Data(type=RRType.A, value='dummy', original=100)

    def adapter(__, _: str):
        return None

    Data.register_adapter(adapter)

    with pytest.raises(AttributeError) as e:
        d.get_original()

    assert 'adapter' in e.value.args[0], 'Raised an unexpected attribute error'


def test_data_instance_has_no_adapters():
    def adapter(__, _: str):
        return None

    Data.register_adapter(adapter)

    d = Data(type=RRType.A, value='dummy', original=100)

    assert not d._adapters, 'Adapters were not empty for instance'
    assert d._adapters is not Data._adapters, 'Adapters for instance were Class adapters'


def test_data_getitem_contains_setitem():
    data = Data(RRType.A, value='data')
    data['a'] = 'abcd'
    assert 'a' in data, 'Failed contains'
    assert data['a'] == 'abcd', 'Failed item get'
