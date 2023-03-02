"""
Reads the IANA list of DNS Resource Records to generate an Enum
"""

import csv
import dataclasses
import pathlib
import ssl
import textwrap
import typing
import urllib.request as r

RR_CSV: str = 'https://www.iana.org/assignments/dns-parameters/dns-parameters-4.csv'


@dataclasses.dataclass
class Entry:
    label: str
    value: int
    description: str

    def __init__(self, label: str, value: str, description: str):
        self.label = label.replace('-', '_').replace('*', 'ANY')
        self.value = int(value)
        self.description = description

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.label.upper()}: int = {self.value}\n"""\n{self.description}\n"""'

    def tuple(self):
        return f"('{self.label}', {self.value})"

    @staticmethod
    def filter(line: typing.List[str]) -> bool:
        return not ('-' in line[1] or 'RESERVED' == line[0].upper())


if __name__ == '__main__':
    with r.urlopen(RR_CSV, context=ssl.create_default_context()) as f:
        data: str = f.read().decode('utf-8')

    records = [
        Entry(
            label=line[0],
            value=line[1],
            description=line[2],
        )
        for line in csv.reader(data.splitlines(keepends=False)[1:])
        if Entry.filter(line)
    ]

    print(records)

    with open(pathlib.Path(__file__).parent.parent / 'src' / 'dnsmule' / 'definitions' / 'rrtype.py', 'w') as f:
        f.write(textwrap.dedent(
            # language=python
            """
            from enum import IntEnum
            from typing import Any, Union
            
            
            class RRType(IntEnum):

                @staticmethod
                def _check_range(value: int):
                    try:
                        if not 0 <= value <= 65535:
                            raise ValueError('Value our of bounds for RR [0, 65535]', value)
                    except TypeError as e:
                        raise ValueError('Value could not be compared', value) from e
                        
                @classmethod
                def to_text(cls, value: Union['RRType', int]) -> str:
                    RRType._check_range(value)
                    for k, v in cls.__members__.items():
                        if v == value:
                            return k
                    return f'RRType.of({value})'
            
                @classmethod
                def from_any(cls, value: Union[int, str, Any]) -> Union['RRType', int]:
                    if isinstance(value, str):
                        value = value.upper()
                        prefix = 'RRtype.of('.upper()
                        if value in cls.__members__:
                            return cls.__members__[value]
                        elif value.startswith(prefix):
                            value = int(value.removeprefix(prefix).removesuffix(')'))
                        else:
                            value = int(value)
                    RRType._check_range(value)
                    for k, v in cls.__members__.items():
                        if k == value or v == value:
                            return v
                    return int(value)
            
                @classmethod
                def from_text(cls, value: str) -> Union['RRType', int]:
                    return cls.from_any(value)
                    
                @classmethod
                def of(cls, value: int) -> Union['RRType', int]:
                    return cls.from_any(value)
            
            """
        ).lstrip())
        for record in records:
            f.write(textwrap.indent(f'{record}', ' ' * 4))
            f.write('\n\n')
        f.write(textwrap.dedent(
            """
            __all__ = [
                'RRType',
            ]
            """
        ))
