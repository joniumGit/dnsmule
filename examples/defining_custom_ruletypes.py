"""
This example shows how to register new rule creators in code

These rule creators can then be used when loading yaml files or creating rules in code.
"""
from dnsmule import Rules, Rule, Record, DNSMule
from dnsmule.loader import ConfigLoader

rules = Rules()
mule = DNSMule.make(rules=rules)


@rules.register('custom.factory')
def create_rule(**definition) -> Rule:
    """
    Defines a handler function for creating rules

    This can be used for creating any kind of rules and could be used for example defining presets for rules.
    """
    print('Registering Rule from Function with definition:', definition)
    return Rule(f=lambda r: r.tag('FACTORY'))


@rules.register
class CustomRule(Rule):
    """
    Rules can also be registered as types inheriting from Rule

    These can be useful as you can directly register classes with the _id attribute set to whatever
    will be used in the YAML file. This is a good way to register rules if you prefer working with classes.
    """
    id = 'custom.rule'

    def __init__(self, **kwargs):
        super(CustomRule, self).__init__(**kwargs)
        print('Registering Rule from Class with definition:   ', kwargs)

    def __call__(self, record: Record):
        record.tag('RULE')


if __name__ == '__main__':
    # Directly setting up and loading as opposed to loading the configuration from file
    # using Mule.append(file)
    loader = ConfigLoader(mule)
    loader.config = {
        'rules': [
            {
                'name': 'FACTORY',
                'type': 'custom.factory',
                'record': 'A',
                'config': {
                    'custom': 'value',
                }
            },
            {
                'name': 'DIRECT',
                'type': 'custom.rule',
                'record': 'A',
                'config': {
                    'hello': 'world',
                }
            },
        ]
    }
    loader.append_rules()
    print('Loaded Rules:', *mule.rules)
