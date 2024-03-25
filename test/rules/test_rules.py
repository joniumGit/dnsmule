from dnsmule import Rules, RRType


def test_rule_registration():
    rules = Rules()

    @rules.register(RRType.A)
    def mock(*_):
        """Ignored
        """

    assert len(rules.normal) == 1, 'Failed to add rule'
    assert rules.normal[RRType.A][0] is mock, 'Did not add the right object'
