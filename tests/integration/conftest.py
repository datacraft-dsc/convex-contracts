import pytest
import pathlib
import logging


from convex_api import ConvexAPI
from convex_api import Account as ConvexAccount

from tests.helpers import topup_accounts

INTEGRATION_PATH = pathlib.Path.cwd() / 'tests' / 'integration'

logging.getLogger('urllib3').setLevel(logging.INFO)

@pytest.fixture(scope='module')
def convex(config):
    convex = ConvexAPI(config['network']['url'])
    return convex


@pytest.fixture(scope='module')
def account_import(config, convex):
    result = []
    # load in the test accounts
    account_1 = config['accounts']['account1']
    return ConvexAccount.import_from_file(account_1['keyfile'], account_1['password'])

@pytest.fixture(scope='module')
def accounts(config, convex):
    result = []
    # load in the test accounts
    account_1 = config['accounts']['account1']
    account_import = ConvexAccount.import_from_file(account_1['keyfile'], account_1['password'])
    accounts = [
        convex.setup_account(account_1['name'], account_import),
        convex.create_account(account_import),
    ]
    topup_accounts(convex, accounts)
    return accounts


@pytest.fixture(scope='module')
def contract_account(accounts):
    return accounts[0]
