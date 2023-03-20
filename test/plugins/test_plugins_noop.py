from dnsmule.plugins.noop import NOOPPlugin


def test_noop_noop():
    p = NOOPPlugin()
    p.register(None)


def test_noop_has_id():
    p = NOOPPlugin()
    assert p.id == 'plugin.noop'
    assert NOOPPlugin.id == 'plugin.noop'
