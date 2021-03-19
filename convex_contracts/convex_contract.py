"""


Convex Contract

"""

from convex_api.account import Account as ConvexAccount
from convex_api.convex_api import ConvexAPI
from convex_api.registry import Registry
from convex_api.utils import to_address


class ConvexContract:
    def __init__(self, convex: ConvexAPI, name: str, version: str):
        self._convex = convex
        self._registry = Registry(convex)
        self._name = name
        self._version = version
        self._source = None
        self._address = None
        self._owner_address = None

    def deploy(self, account: ConvexAccount):
        if not self._source:
            raise ValueError(f'Cannot deploy the contract {self.name} with no source text')

        deploy_line = f"""
    (deploy
        (quote
            (do
                {self._source}
            )
        )
    )
"""
        #print(deploy_line)
        result = self._convex.send(deploy_line, account)
        if result and 'value' in result:
            self._address = to_address(result["value"])
            return self._address

    def register(self, account, name=None, address=None):
        if name is None:
            name = self._name
        if address is None:
            address = self._address

        return self._registry.register(name, address, account)

    def send(self, transaction, account):
        if not self.address:
            raise ValueError(f'No contract address found for {self._name}')
        return self._convex.send(f'(call {self.address} {transaction})', account)

    def query(self, transaction, account_address=None):
        if account_address is None:
            account_address = self.address
        if not self.address:
            raise ValueError(f'No contract address found for {self._name}')
        return self._convex.query(f'(call {self.address} {transaction})', account_address)

    @property
    def deploy_version(self):
        if self.address:
            result = self.query('(version)')
            if result and 'value' in result:
                return result['value']

    @property
    def is_registered(self):
        return self.address is not None

    @property
    def address(self):
        if self._address is None:
            self._address = self._registry.resolve_address(self._name)
        return self._address

    @property
    def owner_address(self):
        if self._owner_address is None:
            self._owner_address = self._registry.resolve_owner(self._name)
        return self._owner_address

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version
