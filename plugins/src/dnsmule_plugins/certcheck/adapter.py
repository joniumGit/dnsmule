from . import certificates


def load_result(result):
    if 'resolvedCertificates' in result.data:
        result.data['resolvedCertificates'] = {
            certificates.Certificate.from_json(o)
            for o in result.data['resolvedCertificates']
        }
    return result


def save_result(result):
    if 'resolvedCertificates' in result.data:
        result.data['resolvedCertificates'] = [
            certificates.Certificate.to_json(o)
            for o in result.data['resolvedCertificates']
        ]
    return result


__all__ = [
    'load_result',
    'save_result',
]
