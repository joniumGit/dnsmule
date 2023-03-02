"""
Creates a list of top domains from a file::

    python scripts/dstat.py -n 10 umbrella-top-1m.csv

    Total entries: 1000000

    Top domains
    0        24281 googlevideo.com
    1        15259 amazonaws.com
    2        14700 fbcdn.net
    3        14088 co.uk
    4        13466 sharepoint.com
    5         9782 webex.com
    6         8018 edgekey.net
    7         6290 windows.net
    8         6184 gvt1.com
    9         5544 akamaiedge.net

    Top sub-domains
    0        68308 www
    1        16176 cdn
    2        15832 fna
    3        14200 com
    4        13333 api
    5         6049 c
    6         5867 infra
    7         5491 elb
    8         4621 app
    9         4595 fls

"""
from argparse import ArgumentParser
from typing import List

from dnsmule.utils import limit, count_by, load_data


def main(file_lines: List[str], n: int = 10):
    print()
    print(f'Total entries: {len(file_lines)}')

    print()
    print('Top domains')
    for idx, (domain, count) in enumerate(limit(count_by(
            file_lines,
            lambda e: '.'.join(e.split('.')[-2:])
    ), n=n)):
        print(f'{idx: <5d} {count: >8d}', domain)

    print()
    print('Top sub-domains')
    for idx, (domain, count) in enumerate(limit(count_by(
            filter(lambda o: o.count('.') >= 3, file_lines),
            lambda e: e.split('.')[-3]
    ), n=n)):
        print(f'{idx: <5d} {count: >8d}', domain)
    print()


if __name__ == '__main__':
    _parser = ArgumentParser(description='Lists top domains and top first subdomains')
    _parser.add_argument(
        '-n', '--limit',
        dest='n',
        help='Limit to top n-entries',
        default=10,
        type=int,
    )
    _parser.add_argument(
        'lines',
        metavar='FILE',
        type=load_data,
        help='Input file',
    )
    _args = _parser.parse_args()
    main(
        file_lines=list(_args.lines),
        n=_args.n,
    )
