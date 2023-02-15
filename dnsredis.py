import redis.asyncio as redis

client = redis.Redis()


async def main():
    await client.ping()
    await client.close(close_connection_pool=True)


if __name__ == '__main__':
    import asyncio

    result = asyncio.run(main())
    print(result)
