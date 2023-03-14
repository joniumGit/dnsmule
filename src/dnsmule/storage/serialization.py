from abc import ABCMeta, abstractmethod
from typing import Dict, Generic, TypeVar, Union, List

from ..definitions import Record, RRType, Result, Domain, Data

T = TypeVar('T')


class Mapper(Generic[T], metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def to_json(value: T) -> Union[Dict, List, str, int, float]:
        """Serialize to JSON
        """

    @staticmethod
    @abstractmethod
    def from_json(value: Union[Dict, List, str, int, float]) -> T:
        """Deserialize from JSON
        """


class RRTypeMapper(Mapper[RRType]):

    @staticmethod
    def to_json(value: Union[RRType, int]) -> str:
        return str(RRType.from_any(value))

    @staticmethod
    def from_json(value: str) -> Union[RRType, int]:
        return RRType.from_any(value)


class DataMapper(Mapper[Data]):

    @staticmethod
    def to_json(value: Data) -> Dict:
        return {
            'type': RRTypeMapper.to_json(value.type),
            'value': value.value,
            'data': value.data,
        }

    @staticmethod
    def from_json(value: Dict) -> Data:
        d = Data(
            type=RRTypeMapper.from_json(value['type']),
            value=value['value']
        )
        d.data = value.get('data', {})
        return d


class DomainMapper(Mapper[Domain]):

    @staticmethod
    def to_json(value: Domain) -> Dict:
        return {
            'name': value.name,
            'data': value.data,
        }

    @staticmethod
    def from_json(value: Dict) -> T:
        d = Domain(name=value['name'])
        d.data = value.get('data', {})
        return d


class RecordMapper(Mapper[Record]):

    @staticmethod
    def to_json(record: Record) -> Dict:
        v = {
            'domain': DomainMapper.to_json(record.domain),
            'type': RRTypeMapper.to_json(record.type),
            'data': DataMapper.to_json(record.data),
        }
        if record.result():
            v['result'] = ResultMapper.to_json(record.result())
        return v

    @staticmethod
    def from_json(value: Dict) -> Record:
        r = Record(
            domain=DomainMapper.from_json(value['domain']),
            type=RRTypeMapper.from_json(value['type']),
            data=DataMapper.from_json(value['data']),
        )
        if 'result' in value:
            r.result() + ResultMapper.from_json(value['result'])
        return r


class ResultMapper(Mapper[Result]):

    @staticmethod
    def to_json(result: Result) -> Dict:
        return {
            'domain': result.domain,
            'type': [
                RRTypeMapper.to_json(t)
                for t in sorted(result.type)
            ],
            'tags': [*result.tags],
            'data': result.data
        }

    @staticmethod
    def from_json(value: Dict) -> Result:
        r = Result(domain=value['domain'])
        r.type.update(map(RRTypeMapper.from_json, value.get('type', [])))
        r.tags.update(value.get('tags', []))
        r.data.update(value.get('data', {}))
        return r


__all__ = [
    'DataMapper',
    'DomainMapper',
    'RRTypeMapper',
    'RecordMapper',
    'ResultMapper',
]
