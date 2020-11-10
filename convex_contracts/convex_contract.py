"""


Convex Contract

"""

from convex_api.account import Account as ConvexAccount
from convex_api.convex_api import ConvexAPI


class ConvexContract:
    def __init__(self, name: str, version: str):
        self._name = name
        self._version = version
        self._source = None
        self._address = None

    def deploy(self, convex: ConvexAPI, account: ConvexAccount):
        if not self._source:
            raise ValueError(f'Cannot deploy the contract {self.name} with no source text')

        deploy_line = f"""
(def {self.name}
    (deploy-once
        (quote
            (do
                {self._source}
            )
        )
    )
)"""
        result = convex.send(deploy_line, account)
        if result and 'value' in result:
            self._address = f'0x{result["value"]}'
            return self._address

    def load(self, convex: ConvexAPI, deploy_account: str):
        self._address = self.get_address(convex, deploy_account)
        self._version = self.get_version(convex, deploy_account)
        return (self._address, self._version)

    def get_address(self, convex: ConvexAPI, deploy_account):
        address = convex.get_address(self._name, deploy_account)
        return address

    def get_version(self, convex: ConvexAPI, deploy_account):
        address = self._address
        if address is None:
            address = self.get_address(convex, deploy_account)

        result = convex.query(f'(call {address} (version))', deploy_account)
        if result and 'value' in result:
            return result['value']

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def address(self):
        return self._address
