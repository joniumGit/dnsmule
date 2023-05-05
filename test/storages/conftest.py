import os
import subprocess
import time

import pytest


def check(call):
    return subprocess.call(call, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True) == 0


@pytest.fixture(scope='session')
def docker():
    available = check('docker info')
    if not available:
        pytest.skip('Docker not available')
    yield


@pytest.fixture(scope='session')
def redis():
    available = check('python -c "import redis"')
    if not available:
        pytest.skip('RedisPy not available')
    yield


@pytest.fixture(scope='session')
def mongo():
    available = check('python -c "import pymongo"')
    if not available:
        pytest.skip('PyMongo not available')
    yield


@pytest.fixture(scope='session')
def redis_container(docker, redis):
    os.system('docker kill dnsmule-test-redis')
    assert os.system(
        'docker run --rm -d -p 127.0.0.1:5431:6379 '
        '--name dnsmule-test-redis '
        'redis/redis-stack-server:latest'
    ) == 0
    params = {'host': '127.0.0.1', 'port': 5431}
    import redis
    c = redis.Redis(**params)
    i = 5
    while True:
        try:
            if c.ping():
                break
        except redis.exceptions.RedisError:
            time.sleep(1)
            i -= 1
            if i <= 0:
                raise AssertionError('Failed to connect') from e
    c.close()
    del c
    yield params
    assert os.system('docker kill dnsmule-test-redis') == 0


@pytest.fixture(scope='session')
def mongo_container(docker, mongo):
    os.system('docker kill dnsmule-test-mongo')
    assert os.system(
        'docker run --rm -d -p 127.0.0.1:5432:27017 '
        '--name dnsmule-test-mongo '
        '-e MONGO_INITDB_ROOT_USERNAME=root '
        '-e MONGO_INITDB_ROOT_PASSWORD=test '
        'mongo:jammy'
    ) == 0
    params = {'host': '127.0.0.1', 'port': 5432, 'username': 'root', 'password': 'test'}
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    with MongoClient(**params, connect=False) as c:
        i = 5
        while True:
            try:
                c.admin.command('ping')
                break
            except ConnectionFailure as e:
                time.sleep(1)
                i -= 1
                if i <= 0:
                    raise AssertionError('Failed to connect') from e
    yield params
    assert os.system('docker kill dnsmule-test-mongo') == 0
