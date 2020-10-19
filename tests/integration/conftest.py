import pytest
import pathlib
import logging


from convex_api import ConvexAPI
from convex_api import Account as ConvexAccount

INTEGRATION_PATH = pathlib.Path.cwd() / 'tests' / 'integration'

logging.getLogger('urllib3').setLevel(logging.INFO)

@pytest.fixture(scope='module')
def convex(config):
    convex = ConvexAPI(config['network']['url'])
    return convex


@pytest.fixture(scope='module')
def accounts(config):
    result = []
    # load in the test accounts
    account_1 = config['accounts']['account1']
    result = [
        ConvexAccount.import_from_file(account_1['keyfile'], account_1['password']),
        ConvexAccount.create_new(),
    ]
    return result

