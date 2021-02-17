"""

    Test Convex Registry

"""

import pytest
import secrets

from convex_api.utils import to_address
from convex_contracts.convex_registry import ConvexRegistry

TEST_CONTRACT_NAME = 'starfish-test.contract'

TEST_DEPLOY = """
(deploy
    '(do
        (def stored-data nil)
        (defn get [] stored-data)
        (defn set [x] (def stored-data x))
        (export get set)
    )
)
"""

@pytest.fixture
def registry(convex):
    return ConvexRegistry(convex)


def test_convex_registry_address(registry):
    assert(registry.address)

def test_convex_registry_is_registered(registry):
    contract_name = f'starfish-test.{secrets.token_hex(8)}'
    assert(registry.is_registered(contract_name) is False)


def test_convex_registry_register_update(registry, convex, account_import):
    contract_name = f'starfish-test.{secrets.token_hex(8)}'
    owner_address = registry.resolve_owner(contract_name)
    assert(owner_address is None)

    # deploy function get set
    account = convex.create_account(account_import)
    convex.topup_account(account)
    result = convex.send(TEST_DEPLOY, account)
    assert(result)
    assert('value' in result)
    contract_address = to_address(result["value"])
    assert(contract_address)

    # register with standard text name
    owner_address = registry.resolve_owner(TEST_CONTRACT_NAME)
    if owner_address:
        account.address = owner_address

    result = registry.register(TEST_CONTRACT_NAME, contract_address, account)
    assert(result)
    print(result)

