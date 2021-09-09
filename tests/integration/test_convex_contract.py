"""

    Test Convex Contract

"""

import pytest
import secrets

from convex_api import (
    API,
    Account
)

from convex_api.exceptions import ConvexAPIError
from convex_api.utils import to_address

from convex_contracts.convex_contract import ConvexContract

TEST_CONTRACT_NAME = 'starfish-test.contract'

class TestContract(ConvexContract):

    def __init__(self, convex, name=None):
        ConvexContract.__init__(self, convex, name or TEST_CONTRACT_NAME, '0.0.1')

        self._source = f'''
            (defn version
                ^{{:callable? true}}
                []
                "{self.version}"
            )
            (def stored-data
                ^{{:private? true}}
                nil
            )
            (defn get
                ^{{:callable? true}}
                []
                stored-data
            )
            (defn set
                ^{{:callable? true}}
                [x]
                (def stored-data x)
            )
        '''

def test_contract_not_registered(convex):

    contract_name = f'starfish-test.{secrets.token_hex(8)}'
    contract = ConvexContract(convex, contract_name, '0.0.1')
    assert(contract.name)
    assert(contract.address is None)
    assert(contract.owner_address is None)
    assert(contract.is_registered is False)

def test_contract_register(convex, contract_account):
    contract = TestContract(convex)
    convex.topup_account(contract_account)
    assert(contract.deploy(contract_account))
    owner_address = contract.resolve_owner_address(contract.name)
    if owner_address and owner_address != contract_account.address:
        contract_account.address = owner_address
    assert(contract.register(contract_account))

    # test get deloy version
    assert(contract.deploy_version == contract.version)

    value = secrets.token_hex(32)
    # test send and query functions
    assert(contract.send((f'(set "{value}")'), contract_account))
    result = contract.query('(get)')
    assert(result)
    assert(result['value'])
    assert(result['value'] == value)

