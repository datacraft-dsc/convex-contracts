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


def deploy_contract(convex, contract, account_import, is_deployed):
    if contract.address:
        if not is_deployed:
            contract_account = account_import.copy()
            contract_account.address = contract.owner_address
            topup_accounts(convex, contract_account)
            assert(contract.deploy(contract_account))
            assert(contract.register(contract_account))
    else:
        contract_account = convex.create_account(account_import)
        topup_accounts(convex, contract_account)
        assert(contract.deploy(contract_account))
        assert(contract.register(contract_account))
