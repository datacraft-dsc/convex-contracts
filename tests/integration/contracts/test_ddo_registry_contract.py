"""

    Test Convex ddo register contract for starfish

"""

import pytest
import secrets

from convex_api import (
    Account as ConvexAccount,
    ConvexAPI
)
from convex_api.exceptions import ConvexAPIError


from convex_contracts.contracts.ddo_registry_contract import DDORegistryContract
from convex_contracts.utils import auto_topup_account

ddo_register_contract_address = None

@pytest.fixture
def contract_address(convex, accounts):
    global ddo_register_contract_address
    contract_account = accounts[0]
    auto_topup_account(convex, contract_account)
    if ddo_register_contract_address is None:
        contract = DDORegistryContract(convex)
        ddo_register_contract_address = contract.deploy(contract_account)
        auto_topup_account(convex, contract_account)
    return ddo_register_contract_address


def test_contract_version(convex, accounts, contract_address):
    contract_account = accounts[0]
    contract = DDORegistryContract(convex)
    version = contract.get_version(contract_account)
    assert(version)
    assert(version == contract.version)
def test_contract_did_register_assert_did(convex, accounts, contract_address):

    test_account = accounts[0]
    auto_topup_account(convex, test_account)

    did_bad = secrets.token_hex(20)
    did_valid = secrets.token_hex(32)
    ddo = 'test - ddo'
    command = f'(call {contract_address} (register "{did_bad}" "{ddo}"))'
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = convex.send(command, test_account)

    command = f'(call {contract_address} (register "" "{ddo}"))'
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = convex.send(command, test_account)

    command = f'(call {contract_address} (register 42 "{ddo}"))'
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = convex.send(command, test_account)

    command = f'(call {contract_address} (register 0x{did_valid} "{ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == f'0x{did_valid}')


def test_contract_did_register_resolve(convex, accounts, contract_address):

    test_account = accounts[0]
    other_account = accounts[1]

    auto_topup_account(convex, accounts)

    did = f'0x{secrets.token_hex(32)}'
    ddo = 'test - ddo'


    # call register

    command = f'(call {contract_address} (register {did} "{ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)

    # call resolve did to ddo

    command = f'(call {contract_address} (resolve {did}))'
    result = convex.query(command, test_account)
    assert(result['value'])
    assert(result['value'] == ddo)

    # call resolve did to ddo on other account

    command = f'(call {contract_address} (resolve {did}))'
    result = convex.query(command, other_account)
    assert(result['value'])
    assert(result['value'] == ddo)

    # call owner? on owner account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, test_account)
    assert(result['value'])

    # call owner? on owner other_account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, other_account)
    assert(not result['value'])

    # call resolve unknown
    bad_did = f'0x{secrets.token_hex(32)}'
    command = f'(call {contract_address} (resolve {bad_did}))'
    result = convex.query(command, test_account)
    assert(result['value'] == '')


    new_ddo = 'new - ddo'
    # call register - update

    command = f'(call {contract_address} (register {did} "{new_ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)


    # call register - update from other account

    with pytest.raises(ConvexAPIError, match='NOT-OWNER'):
        command = f'(call {contract_address} (register {did} "{ddo}"))'
        result = convex.send(command, other_account)


    # call resolve did to new_ddo

    command = f'(call {contract_address} (resolve {did}))'
    result = convex.query(command, test_account)
    assert(result['value'])
    assert(result['value'] == new_ddo)


    # call unregister fail - from other account

    with pytest.raises(ConvexAPIError, match='NOT-OWNER'):
        command = f'(call {contract_address} (unregister {did}))'
        result = convex.send(command, other_account)


    # call unregister

    command = f'(call {contract_address} (unregister {did}))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)

    # call resolve did to empty

    command = f'(call {contract_address} (resolve {did}))'
    result = convex.query(command, test_account)
    assert(result['value'] == '')


    # call unregister - unknown did

    command = f'(call {contract_address} (unregister {bad_did}))'
    result = convex.send(command, test_account)
    assert(result['value'] == '')



def test_contract_ddo_transfer(convex, accounts):
    # register and transfer

    test_account = accounts[0]
    other_account = accounts[1]
    auto_topup_account(convex, accounts)

    ddo_registry_contract = DDORegistryContract(convex)
    contract_address = ddo_registry_contract.get_address(test_account)
    assert(contract_address)

    did = f'0x{secrets.token_hex(32)}'
    ddo = 'test - ddo'

    command = f'(call {contract_address} (register {did} "{ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)

    # call owner? on owner account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, test_account)
    assert(result['value'])

    # call owner? on other_account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, other_account)
    assert(not result['value'])


    command = f'(call {contract_address} (transfer {did} {other_account.address_checksum}))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'][0] == did)

    #check ownership to different accounts

    # call owner? on owner account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, test_account)
    assert(not result['value'])

    # call owner? on other_account
    command = f'(call {contract_address} (owner? {did}))'
    result = convex.query(command, other_account)
    assert(result['value'])

    # call unregister fail - from test_account (old owner)

    with pytest.raises(ConvexAPIError, match='NOT-OWNER'):
        command = f'(call {contract_address} (unregister {did}))'
        result = convex.send(command, test_account)


    # call unregister from other_account ( new owner )

    command = f'(call {contract_address} (unregister {did}))'
    result = convex.send(command, other_account)
    assert(result['value'])
    assert(result['value'] == did)

def test_contract_ddo_bulk_register(convex, accounts):
    test_account = accounts[0]
    ddo_registry_contract = DDORegistryContract(convex)
    contract_address = ddo_registry_contract.get_address(test_account)
    assert(contract_address)

    for index in range(0, 2):
        auto_topup_account(convex, test_account, 40000000)
        did = f'0x{secrets.token_hex(32)}'
#        ddo = secrets.token_hex(51200)
        ddo = secrets.token_hex(1024)

        command = f'(call {contract_address} (register {did} "{ddo}"))'
        result = convex.send(command, test_account)
        assert(result['value'])
        assert(result['value'] == did)

def test_contract_ddo_owner_list(convex, accounts):

    test_account = accounts[0]
    other_account = accounts[1]
    auto_topup_account(convex, accounts)

    ddo_registry_contract = DDORegistryContract(convex)
    contract_address = ddo_registry_contract.get_address(test_account)
    assert(contract_address)

    did_list = []
    for index in range(0, 4):
        auto_topup_account(convex, test_account)
        did = f'0x{secrets.token_hex(32)}'
        did_list.append(did)
#        ddo = secrets.token_hex(51200)
        ddo = f'ddo test - {index}'

        command = f'(call {contract_address} (register {did} "{ddo}"))'
        result = convex.send(command, test_account)
        assert(result['value'])
        assert(result['value'] == did)


    command = f'(call {contract_address} (owner-list "{test_account.address_api}"))'
    result = convex.query(command, test_account)
    assert(result['value'])
    for did in did_list:
        assert(did in result['value'])

