"""


    Test Convex Provenance Contract for starfish

"""
import pytest
import secrets

from convex_api import (
    Account as ConvexAccount,
    ConvexAPI
)
from convex_api.exceptions import ConvexAPIError


from convex_contracts.contracts.provenance_contract import ProvenanceContract
from convex_contracts.utils import auto_topup_account


provenance_contract_address = None
test_event_list = None

@pytest.fixture
def contract_address(convex, accounts):
    global provenance_contract_address
    contract_account = accounts[0]
    auto_topup_account(convex, contract_account)
    if provenance_contract_address is None:
        contract = ProvenanceContract(convex)
        provenance_contract_address = contract.deploy(contract_account)
        auto_topup_account(convex, contract_account)
    return provenance_contract_address


@pytest.fixture
def register_test_list(pytestconfig, convex, accounts, contract_address):
    global test_event_list

    test_account = accounts[0]
    other_account = accounts[1]
    if not test_event_list:
        test_event_list = []
        event_count = 10
        auto_topup_account(convex, accounts)

        register_account = other_account
        for index in range(0, event_count):
            if index % 2 == 0:
                asset_id = '0x' + secrets.token_hex(32)
                if register_account.address == test_account.address:
                    register_account = other_account
                else:
                    register_account = test_account
            result = convex.send(f'(call {contract_address} (register {asset_id}))', register_account)
            assert(result)
            record = result['value']
            assert(record['asset-id'] == asset_id)
            test_event_list.append(record)
    return test_event_list


def test_contract_version(convex, accounts, contract_address):
    contract_account = accounts[0]
    contract = ProvenanceContract(convex)
    version = contract.get_version(contract_account)
    assert(version)
    assert(version == contract.version)

def test_provenance_contract_register(register_test_list):
    assert(register_test_list)

def test_provenance_contract_event_list(convex, accounts, contract_address, register_test_list):
    test_account = accounts[0]
    record = register_test_list[secrets.randbelow(len(register_test_list))]
    result = convex.query(f'(call {contract_address} (event-list {record["asset-id"]}))', test_account)
    assert(result)
    event_list = result['value']
    assert(event_list)
    assert(len(event_list) == 2)
    event_item = event_list[0]
    assert(event_item['asset-id'] == record['asset-id'])
    assert(event_item['owner'] == record['owner'])

def test_provenance_contract_event_owner_list(convex, accounts, contract_address, register_test_list):
    other_account = accounts[1]
    record = register_test_list[secrets.randbelow(len(register_test_list))]
    owner_count = 0
    for item in register_test_list:
        if item['owner'] == record['owner']:
            owner_count += 1
    result = convex.query(f'(call {contract_address} (event-owner {record["owner"]}))', other_account)
    event_list = result['value']
    assert(event_list)
    assert(len(event_list) >= owner_count)
    for event_item in event_list:
        assert(event_item['owner'] == record["owner"])

def test_provenance_contract_event_timestamp_list(convex, accounts, contract_address, register_test_list):
    test_account = accounts[0]
    record_from = register_test_list[2]
    record_to = register_test_list[len(register_test_list) - 2]
    timestamp_from = record_from['timestamp']
    timestamp_to = record_to['timestamp']
    result = convex.query(f'(call {contract_address} (event-timestamp {timestamp_from} {timestamp_to}))', test_account)
    event_list = result['value']
    assert(event_list)
    assert(len(event_list) == len(register_test_list) - 3)
    for event_item in event_list:
        assert(event_item['timestamp'] >= timestamp_from and event_item['timestamp'] <= timestamp_to)

def test_provenance_contract_event_timestamp_item(convex, accounts, contract_address, register_test_list):
    test_account = accounts[0]
    record = register_test_list[secrets.randbelow(len(register_test_list))]
    timestamp = record['timestamp']
    result = convex.query(f'(call {contract_address} (event-timestamp {timestamp} {timestamp}))', test_account)
    event_list = result['value']
    assert(len(event_list) == 1)
    event_item = event_list[0]
    assert(event_item['timestamp'] == timestamp)

def test_bad_asset_id(convex, accounts, contract_address):
    test_account = accounts[0]
    bad_asset_id = '0x' + secrets.token_hex(20)
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = convex.send(f'(call {contract_address} (register {bad_asset_id}))', test_account)


