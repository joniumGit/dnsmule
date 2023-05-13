import argparse

import httpx

from dnsmule.utils import load_data


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', help='server host')
    parser.add_argument('--port', default='8080', help='server port')
    parser.add_argument('--https', default=False, action='store_true', help='use https')
    parser.add_argument('--skip', default=0, type=int, help='skip n records')
    parser.add_argument('--delay', default=300, type=int, help='send delay in ms')
    parser.add_argument('--suffix', default='', help='suffix to filter domains by')
    parser.add_argument('file', help='input domain file (txt or csv[id, value])')
    args = parser.parse_args()
    s = '' if not args.https else 's'
    n = 0
    try:
        skip = args.skip
        for domain in filter(
                lambda line: not args.suffix or line.endswith(args.suffix),
                load_data(args.file)
        ):
            n += 1
            if skip != 0:
                skip -= 1
                continue
            print('Sending n: %d' % n, end='\r')
            async with httpx.AsyncClient() as client:
                await client.post(f'http{s}://{args.host}:{args.port}/scan?domain={domain}')
            await asyncio.sleep(args.delay / 1000)
    finally:
        print('\n')
        print(f'FINAL N: {n}')


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
