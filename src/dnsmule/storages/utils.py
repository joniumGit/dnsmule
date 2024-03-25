def jsonize(value):
    """
    Jsonizes a couple of outliers in the standard collections

    :param value: Anything
    :return: Something hopefully JSON compatible
    """
    if isinstance(value, dict):
        return {
            k: jsonize(v)
            for k, v in value.items()
        }
    elif isinstance(value, (list, set, frozenset)):
        return [
            *value,
        ]
    else:
        return value
