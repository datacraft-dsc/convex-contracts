"""


    Test Convex Provenance Contract for starfish

"""
import json
import pytest
import re
import secrets

from convex_api import (
    Account,
    API
)
from convex_api.exceptions import ConvexAPIError
from convex_api.utils import to_address

from convex_contracts.contracts.provenance_contract import ProvenanceContract
from tests.helpers import (
    topup_accounts,
    deploy_contract
)

test_event_list = None
is_contract_deployed = False
TEST_CONTRACT_NAME = 'starfish-test.provenance'


def decode_asset_did(did):
    match = re.match('^did:([a-z0-9]+):([a-f0-9]{64})/([a-f0-9]{64})', did, re.IGNORECASE)
    return {
        'method': match.group(1),
        'id': f'0x{match.group(2)}',
        'asset_id': f'0x{match.group(3)}',
    }

def generate_asset_did():
    did_id = secrets.token_hex(32)
    asset_id = secrets.token_hex(32)
    return f'did:dep:{did_id}/{asset_id}'

@pytest.fixture
def provenance_contract(convex, contract_account):
    global is_contract_deployed
    contract = ProvenanceContract(convex, TEST_CONTRACT_NAME)
    if not is_contract_deployed:
        deploy_contract(convex, contract, contract_account)
        is_contract_deployed = True
    return contract


@pytest.fixture
def register_test_list(pytestconfig, convex, provenance_contract, accounts):
    global test_event_list

    account_test = accounts[0]
    account_other = accounts[1]
    test_data = {
        'name': secrets.token_hex(32),
        'info': secrets.token_hex(32),
    }
    if not test_event_list:
        test_event_list = []
        event_count = 10
        topup_accounts(convex, accounts)

        register_account = account_other
        for index in range(0, event_count):
            asset_did = generate_asset_did()
            did = decode_asset_did(asset_did)

            if index % 2 == 0:
                if register_account.address == account_test.address:
                    register_account = account_other
                else:
                    register_account = account_test

            test_data_text = re.sub(r'\"', '//#', json.dumps(test_data))
            register_line = f'(register {did["id"]} {did["asset_id"]} "{test_data_text}")'
            print(register_line)
            result = provenance_contract.send(register_line, register_account)
            assert(result)
            record = result['value']
            assert(record['owner'] == register_account.address)
            record['asset_did'] = asset_did
            test_event_list.append(record)
    return test_event_list


def test_provenance_contract_register(register_test_list):
    assert(register_test_list)


def test_provenance_contract_event_list(convex, provenance_contract, accounts, register_test_list):
    account_test = accounts[0]
    topup_accounts(convex, account_test)

    record = register_test_list[secrets.randbelow(len(register_test_list))]
    asset_did = record['asset_did']
    did = decode_asset_did(asset_did)
    result = provenance_contract.query(f'(get-data {did["id"]} {did["asset_id"]})', account_test)
    assert(result)
    event_item = result['value']
    assert(event_item['owner'] == record['owner'])
    assert(event_item['timestamp'])
    assert(event_item['data'])


def test_provenance_contract_event_owner_list(convex, provenance_contract, accounts, register_test_list):
    account_other = accounts[1]
    topup_accounts(convex, account_other)
    record = register_test_list[secrets.randbelow(len(register_test_list))]
    owner_count = 0
    for item in register_test_list:
        if item['owner'] == record['owner']:
            owner_count += 1
    owner_address = to_address(record['owner'])
    result = provenance_contract.query(f'(owner-list {owner_address})', account_other)
    asset_list = result['value']
    print(asset_list)
    assert(asset_list)
    assert(len(asset_list) >= owner_count)



def test_bad_asset_id(convex, provenance_contract, accounts):
    account_test = accounts[0]
    topup_accounts(convex, account_test)
    bad_asset_id = '0x' + secrets.token_hex(20)
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = provenance_contract.send(f'(register {bad_asset_id} {bad_asset_id} "test data")', account_test)


