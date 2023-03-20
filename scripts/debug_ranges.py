from dnsmule_plugins.ipranges.ranges import *


def debug_ip_ranges():
    services = [
        *(
            fetch_google_ip_ranges()
        ),
        *(
            fetch_amazon_ip_ranges()
        ),
        *(
            fetch_microsoft_ip_ranges()
        ),
    ]

    import json
    import dataclasses

    with open('service-debug.json', 'w') as f:
        json.dump(
            {
                'services': [
                    dataclasses.asdict(s)
                    for s in services
                ]
            },
            f,
            default=str,
            indent=4,
            ensure_ascii=False,
        )


if __name__ == '__main__':
    import logging

    from dnsmule.logger import get_logger

    get_logger().setLevel(logging.DEBUG)
    get_logger().addHandler(logging.StreamHandler())

    debug_ip_ranges()
