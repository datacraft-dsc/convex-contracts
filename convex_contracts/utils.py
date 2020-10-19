"""
    Utils for seting up and testing development accounts

"""

from typing import (
    List,
    Union
)


from convex_api import Account as ConvexAccount
from convex_api import ConvexAPI

ConvexAccountList = List[ConvexAccount]


def auto_topup_account(convex: ConvexAPI, account: Union[ConvexAccount, ConvexAccountList], min_balance=None):
    if isinstance(account, (list, tuple)):
        for account_item in account:
            auto_topup_account(convex, account_item, min_balance)
        return
    amount = 10000000
    retry_counter = 100
    if min_balance is None:
        min_balance = amount
    balance = convex.get_balance(account)
    while balance < min_balance and retry_counter > 0:
        convex.request_funds(amount, account)
        balance = convex.get_balance(account)
        retry_counter -= 1
