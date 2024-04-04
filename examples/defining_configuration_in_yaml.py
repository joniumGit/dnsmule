"""
This example uses a YAML file to load rules and other configuration

The YAML file contains declarations to load the backend and rules for the mule.
The sample collects all A records and tags them with the first number of the IP address in the record.
The backend is the builtin DNSPythonBackend.
The storage is not defined in the YAML file, so it will default to the builtin DictStorage.
"""

from pathlib import Path

from dnsmule import load_config_from_file

mule = load_config_from_file(Path(__file__).parent / 'example.yml')

if __name__ == '__main__':
    result = mule.scan('example.com')
    print('Loaded Rules:   ', mule.rules.normal)
    print('Loaded Backend: ', mule.backend)
    print('Loaded Storage: ', mule.storage)
    print('Produced Result:', result)
