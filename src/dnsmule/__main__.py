import argparse
import json
import logging
import sys

from . import load_config_from_file, RRType
from .utils import jsonize

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description='DNSMule')
    parser.add_argument('--config', required=True)
    parser.add_argument('TARGET', nargs='+')
    parser.add_argument(
        '-s', '--silent',
        dest='silent',
        default=False,
        action='store_true',
    )

    args = parser.parse_args()
    mule = load_config_from_file(args.config)

    targets = args.TARGET
    if len(targets) == 1 and targets[0] == '-':
        targets = sys.stdin.read().splitlines(keepends=False)

    with mule:
        for target in targets:
            result = mule.scan(target)
            if not args.silent:
                print(json.dumps(
                    {
                        'name': result.name,
                        'types': [*map(RRType.to_text, result.types)],
                        'tags': [*result.tags],
                        'data': jsonize(result.data),
                    },
                    indent=4,
                    ensure_ascii=False,
                ))
