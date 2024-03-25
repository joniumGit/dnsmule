from pathlib import Path

from dnsmule import CSVBackend, RRType, Record, Domain


def test_backends_csv():
    file = Path(__file__).parent / 'sample_records.csv'
    backend = CSVBackend(file=file)

    with backend:
        for record, expected in zip(
                backend.scan(
                    Domain('www.example.com'),
                    RRType.A,
                    RRType.CNAME,
                ),
                [
                    Record(
                        name=Domain('www.example.com'),
                        type=RRType.CNAME,
                        data='example.com',
                    ),
                    Record(
                        name=Domain('example.com'),
                        type=RRType.A,
                        data='127.0.0.1',
                    ),
                    Record(
                        name=Domain('example.com'),
                        type=RRType.MX,
                        data='127.0.0.1',
                    ),
                ],
        ):
            assert record == expected


def test_backends_csv_limit():
    file = Path(__file__).parent / 'sample_records.csv'
    backend = CSVBackend(file=file, limit=1)

    with backend:
        for record, expected in zip(
                backend.scan(
                    Domain('www.example.com'),
                    RRType.A,
                    RRType.CNAME,
                ),
                [
                    Record(
                        name=Domain('www.example.com'),
                        type=RRType.CNAME,
                        data='example.com',
                    ),
                    None,
                    None,
                ],
        ):
            assert record == expected, 'Did not properly limit scan'
