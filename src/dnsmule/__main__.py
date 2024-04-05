import argparse
import json

from . import load_config_from_file, RRType
from .utils import jsonize

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DNSMule')
    parser.add_argument('--config', required=True)
    parser.add_argument('TARGET')

    args = parser.parse_args()
    mule = load_config_from_file(args.config)
    with mule:
        result = mule.scan(args.TARGET)
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
