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

    with open(pathlib.Path(__file__).parent.parent / 'src' / 'dnsmule' / 'definitions' / 'rrtypes.py', 'w') as f:
        f.write(textwrap.dedent(
            # language=python
            """
            from enum import IntEnum
            from typing import Any, Union
            
            
            class RRTypes(IntEnum):
            
                @classmethod
                def to_text(cls, value: Union['RRTypes', int]) -> str:
                    for k, v in cls.__members__.items():
                        if v == value:
                            return k
                    return f'UNKNOWN({value})'
            
                @classmethod
                def from_any(cls, value: Union[int, str, Any]) -> 'RRTypes':
                    if value in cls.__members__:
                        return cls.__members__[value]
                    elif value.startswith('UNKNOWN('):
                        value = int(value.removeprefix('UNKNOWN(').removesuffix(')'))
                    else:
                        value = int(value)
                    for _, v in cls.__members__.items():
                        if v == value:
                            return v
                
                @classmethod
                def from_text(cls, value: str):
                    return cls(value=cls.from_any(value))
                            
                def __str__(self):
                    return self.to_text(self.value)
                    
                def __repr__(self):
                    return self.__str__()
            
            """
        ).lstrip())
        for record in records:
            f.write(textwrap.indent(f'{record}', ' ' * 4))
            f.write('\n\n')
        f.write(textwrap.dedent(
            """
            __all__ = [
                'RRTypes',
            ]
            """
        ))
