"""
    Helpers for seting up and testing development accounts

"""

TOPUP_AMOUNT = 10000000

from typing import (
    List,
    Union
)


from convex_api import Account as ConvexAccount
from convex_api import ConvexAPI

ConvexAccountList = List[ConvexAccount]


def topup_accounts(convex: ConvexAPI, account: Union[ConvexAccount, ConvexAccountList], min_balance=None):
    if isinstance(account, (list, tuple)):
        for account_item in account:
            topup_accounts(convex, account_item, min_balance)
        return
    if min_balance is None:
        min_balance = TOPUP_AMOUNT
    return convex.topup_account(account, min_balance)


def deploy_contract(convex, contract, contract_account):
    topup_accounts(convex, contract_account)
    assert(contract.deploy(contract_account))
    # fix when the registered contract was not registered by the named contract_account address
    account = contract_account
    owner_address = contract._registry.resolve_owner(contract.name)
    if owner_address and owner_address != contract_account.address:
        account = ConvexAccount.import_from_account(contract_account, owner_address)
    assert(contract.register(account))
