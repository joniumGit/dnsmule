from dnsmule_plugins.ipranges.providers import Providers


def debug_ip_ranges():
    import json
    import dataclasses

    with open('service-debug.json', 'w') as f:
        json.dump(
            {
                provider: [
                    dataclasses.asdict(iprange)
                    for iprange in Providers.fetch(provider)
                ]
                for provider in Providers._mapping
            },
            f,
            default=str,
            indent=4,
            ensure_ascii=False,
        )


if __name__ == '__main__':
    debug_ip_ranges()
