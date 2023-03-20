from dnsmule.storages.redisstorage import RedisStorage
from dnsmule_plugins.certcheck.certificates import Certificate

if __name__ == '__main__':
    redis = RedisStorage(host='127.0.0.1')
    for k in redis:
        result = redis[k]
        for data_key in result.data:
            if data_key == 'resolvedCertificates':
                result.data[data_key] = [
                    c.to_json()
                    for c in {
                        Certificate.from_json(jc)
                        for jc in result.data[data_key]
                    }
                ]
            elif data_key.startswith('resolved'):
                result.data[data_key] = [*{*result.data[data_key]}]
        redis[k] = result
    del redis
