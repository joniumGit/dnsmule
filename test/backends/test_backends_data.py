from dnsmule import DataBackend, RRType, Record, Domain


def test_data_backend_takes_input_in_correct_form():
    backend = DataBackend(**{
        'www.example.com': [
            {
                'name': 'www.example.com',
                'type': 'CNAME',
                'data': 'example.com',
            },
            {
                'name': 'example.com',
                'type': 'A',
                'data': '127.0.0.1',
            },
            {
                'name': 'example.com',
                'type': 'MX',
                'data': '127.0.0.1',
            },
        ]
    })

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
                None,  # This will fail if it gets here the MX needs to be skipped
            ],
    ):
        assert record == expected
