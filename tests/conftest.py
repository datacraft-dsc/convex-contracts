import pytest
import pathlib
import yaml
import logging



RESOURCES_PATH = pathlib.Path.cwd() / 'tests' / 'resources'
CONFIG_LOCAL_FILE_PATH = RESOURCES_PATH / 'config_local.yml'


# set debug logging
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope='module')
def config():
    filename = CONFIG_LOCAL_FILE_PATH
    config_data = None
    with open(filename, 'r') as fp:
        config_data = yaml.safe_load(fp.read())
    print(config_data)
    return config_data

