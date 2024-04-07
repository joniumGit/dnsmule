import os
import subprocess
import time
from contextlib import contextmanager

import pytest


def check(call):
    return subprocess.call(
        call,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True,
    ) == 0


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
def mysql():
    available = check('python -c "import pymysql"')
    if not available:
        pytest.skip('PyMySQL not available')
    yield


START_PORT = 5430


@contextmanager
def container_context(
        *additional_command_parts,
        connection_factory,
        ping,
        name,
        port,
        container,
        **additional_environment,
):
    global START_PORT
    START_PORT += 1
    params = {
        'host': '127.0.0.1',
        'port': START_PORT,
        **additional_environment,
    }
    start_command = (
        'docker run'
        ' --rm'
        ' -d'
        f' -p 127.0.0.1:{START_PORT}:{port}'
        f' {" ".join(additional_command_parts)}'
        f' --name {name}'
        f' {container}'
    )
    os.system(f'docker kill {name}')
    try:
        assert os.system(start_command) == 0
        c = connection_factory(**params)
        i = 10
        ex = None
        while i > 0:
            try:
                if ping(c):
                    break
                else:
                    time.sleep(1)
                    i -= 1
                    ex = 'ping failed'
            except Exception as e:
                time.sleep(1)
                i -= 1
                ex = e
        del c
        if i == 0:
            pytest.fail(f'failed to create container {name} {ex}\n{start_command}')
        yield params
    finally:
        os.system(f'docker kill {name}')


@pytest.fixture(scope='session')
def redis_container(docker, redis):
    import redis
    with container_context(
            connection_factory=redis.Redis,
            ping=redis.Redis.ping,
            name='dnsmule-test-redis',
            port=6379,
            container='redis/redis-stack-server:latest',
    ) as params:
        yield params


@pytest.fixture(scope='session')
def mongo_container(docker, mongo):
    from pymongo import MongoClient

    def connection(**kwargs):
        return MongoClient(**kwargs, connect=False)

    def ping(client):
        client.admin.command('ping')
        return True

    with container_context(
            '-e MONGO_INITDB_ROOT_USERNAME=root',
            '-e MONGO_INITDB_ROOT_PASSWORD=test',
            username='root',
            password='test',
            connection_factory=connection,
            ping=ping,
            name='dnsmule-test-mongo',
            port=27017,
            container='mongo:7.0-jammy',
    ) as params:
        yield params


@pytest.fixture(scope='session')
def mysql_container(docker, mysql):
    import pymysql

    def connect(**kwargs):
        return pymysql.connect(**kwargs, defer_connect=True)

    def ping(connection):
        connection.connect()
        connection.ping(reconnect=False)
        return True

    with container_context(
            '-e MYSQL_ROOT_PASSWORD=test',
            '-e MARIADB_DATABASE=dnsmule',
            user='root',
            password='test',
            database='dnsmule',
            connection_factory=connect,
            ping=ping,
            name='dnsmule-test-mysql',
            port=3306,
            container='mariadb:10.6',
    ) as params:
        yield params
