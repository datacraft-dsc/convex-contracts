"""

    Test Convex Contract

"""

import pytest
import secrets

from convex_api import (
    Account as ConvexAccount,
    ConvexAPI
)
from convex_api.exceptions import ConvexAPIError
from convex_api.utils import to_address

from convex_contracts.convex_contract import ConvexContract

TEST_CONTRACT_NAME = 'starfish-test.contract'

class TestContract(ConvexContract):

    def __init__(self, convex, name=None):
        ConvexContract.__init__(self, convex, name or TEST_CONTRACT_NAME, '0.0.1')

        self._source = f'''
            (defn version [] "{self.version}")
            (def stored-data nil)
            (defn get [] stored-data)
            (defn set [x] (def stored-data x))
            (export get set version)

        '''

def test_contract_not_registered(convex):

    contract_name = f'starfish-test.{secrets.token_hex(8)}'
    contract = ConvexContract(convex, contract_name, '0.0.1')
    assert(contract.name)
    assert(contract.address is None)
    assert(contract.owner_address is None)
    assert(contract.is_registered is False)

def test_contract_register(convex, account_import):
    account = account_import
    contract = TestContract(convex)
    if contract.owner_address:
        account.address = contract.owner_address
    else:
        account = convex.create_account(account_import)
    convex.topup_account(account)
    assert(contract.deploy(account))
    assert(contract.register(account))

    # test get deloy version
    assert(contract.deploy_version == contract.version)

    value = secrets.token_hex(32)
    # test send and query functions
    assert(contract.send((f'(set "{value}")'), account))
    result = contract.query('(get)')
    assert(result)
    assert(result['value'])
    assert(result['value'] == value)

