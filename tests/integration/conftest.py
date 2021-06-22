import pytest
import pathlib
import logging


from convex_api import (
    API,
    Account,
    KeyPair
)

from tests.helpers import topup_accounts

INTEGRATION_PATH = pathlib.Path.cwd() / 'tests' / 'integration'

logging.getLogger('urllib3').setLevel(logging.INFO)

@pytest.fixture(scope='module')
def convex(config):
    convex = API(config['network']['url'])
    return convex


@pytest.fixture(scope='module')
def keypair_import(config, convex):
    result = []
    # load in the test accounts
    account_1 = config['accounts']['account1']
    return KeyPair.import_from_file(account_1['keyfile'], account_1['password'])

@pytest.fixture(scope='module')
def accounts(config, convex):
    result = []
    # load in the test accounts
    account_1 = config['accounts']['account1']
    keypair_import = KeyPair.import_from_file(account_1['keyfile'], account_1['password'])
    accounts = [
        convex.setup_account(account_1['name'], keypair_import),
        convex.create_account(keypair_import),
    ]
    topup_accounts(convex, accounts)
    return accounts


@pytest.fixture(scope='module')
def contract_account(accounts):
    return accounts[0]
