from dnsmule import Rules, RRType


def test_rules_registration():
    rules = Rules()

    @rules.register(RRType.A)
    def mock(*_):
        """Ignored
        """

    assert len(rules.normal) == 1, 'Failed to add rule'
    assert rules.normal[RRType.A][0] is mock, 'Did not add the right object'


def test_rules_registration_works_both_ways():
    rules = Rules()

    @rules.register(RRType.A)
    def rule1(*_):
        """Noop
        """

    def rule2(*_):
        """Noop
        """

    rules.register(RRType.A, rule2)

    assert len(rules.normal[RRType.A]) == 2, ' Failed to add both rules'


def test_rules_batch_registration_works_both_ways():
    rules = Rules()

    @rules.register_batch
    def rule1(*_):
        """Noop
        """

    def rule2(*_):
        """Noop
        """

    rules.register_batch(rule2)

    assert len(rules.batch) == 2, ' Failed to add both rules'
