from pathlib import Path

from dnsmule import load_config_from_file


def test_config_loads():
    mule = load_config_from_file(Path(__file__).parent / 'sample.yml')

    with mule:
        result = mule.scan('example.com')

    assert result.data.get('test', False), 'Did not load or run dynamic any rule'
    assert 'DNS::REGEX::TEST::LABEL' in result.tags, 'Did not load or run regex A rule'
    assert 'scans' in result.data, 'Did not load or run timestamp rule'

    assert 'SAMPLE' in result.tags, 'Did not load test plugin'
