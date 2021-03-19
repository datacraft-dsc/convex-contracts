#!/usr/bin/env python3

"""

    Script to provide convex contract tools

"""

import argparse
import importlib
import inspect
import json
import logging
import os
import re


from convex_api import Account as ConvexAccount
from convex_api import ConvexAPI

from convex_contracts.convex_contract import ConvexContract

TOPUP_AMOUNT = 10000000
CONTRACT_PACKAGE = 'convex_contracts.contracts'
DEFAULT_URL = 'https://convex.world'
DEFAULT_ACCOUNT_NAME = 'convex_contracts'

logger = logging.getLogger('convex_contract_tool')


def load_contracts(package_name):
    result = {}
    package_module = importlib.import_module(package_name)
    for item in inspect.getmembers(package_module, inspect.ismodule):
        for name, obj in inspect.getmembers(item[1], inspect.isclass):
            if issubclass(obj, ConvexContract) and name != 'ConvexContract':
                result[name] = obj
    return result


def main():

    parser = argparse.ArgumentParser(description='Convex Contract Tool')

    parser.add_argument(
        '--auto-topup',
        action='store_true',
        help='Auto topup account with sufficient funds. This only works for development networks. Default: False',
    )

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='Debug mode on or off. Default: False',
    )

    parser.add_argument(
        '-k',
        '--keyfile',
        help='account key file'
    )

    parser.add_argument(
        '--keyword',
        help='private key as key words'
    )

    parser.add_argument(
        '-p',
        '--password',
        help='password to access the account'
    )

    parser.add_argument(
        '-n',
        '--name',
        default=DEFAULT_ACCOUNT_NAME,
        help=f'Account name to use to register contracts. Default: {DEFAULT_ACCOUNT_NAME}'
    )

    parser.add_argument(
        '-a',
        '--address',
        nargs='?',
        help='Account address to use to register and deploy the contracts'
    )

    parser.add_argument(
        '-u',
        '--url',
        default=DEFAULT_URL,
        help=f'URL of the network node. Default: {DEFAULT_URL}',
    )

    parser.add_argument(
        'command',
        help='Deploy the contract or contracts on the convex network'
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.INFO)

    if args.command == 'deploy':
        keyword = os.environ.get('KEYWORD', args.keyword)
        keyfile = os.environ.get('KEYFILE', args.keyfile)
        password = os.environ.get('PASSWORD', args.password)
        if keyword:
            keyword = re.sub('_', ' ', keyword)
            account_import = ConvexAccount.import_from_mnemonic(keyword, address=args.address, name=args.name)
        else:
            if keyfile is None or password is None:
                print('You need to provide an account keyfile and password to deploy the contracts')
                return
            logger.debug(f'loading account keyfile {keyfile}')
            if not os.path.exists(keyfile):
                print(f'Cannot find account keyfile {keyfile}')
            account_import = ConvexAccount.import_from_file(keyfile, password, address=args.address, name=args.name)

        url = os.environ.get('URL', args.url)
        logger.debug(f'connecting to convex network {url}')
        convex = ConvexAPI(url)
        if not convex:
            print(f'Cannot connect to the convex network at {url}')
            return

        if account_import.address is None:
            contract_account = convex.setup_account(args.name, account_import)
            logger.debug(f'setting up account address: {contract_account.address}')
        else:
            contract_account = ConvexAccount.import_from_account(import_account, contract.address)
            logger.debug(f'loading account with address: {contract_account.address}')

        contract_items = load_contracts(CONTRACT_PACKAGE)
        values = {}
        for class_name, contract_class in contract_items.items():
            contract = contract_class(convex)

            if args.auto_topup:
                logger.debug('auto topup of account balance')
                convex.topup_account(contract_account, TOPUP_AMOUNT)

            logger.debug(f'deploying contract {class_name} {contract.name} #{contract_account.address}')
            if contract.deploy(contract_account):
                # may need to change the register address to the original address used before account naming was used.
                account = contract_account
                owner_address = contract._registry.resolve_owner(contract.name)
                if owner_address and owner_address != contract_account.address:
                    account = ConvexAccount.import_from_account(contract_account, owner_address)

                if contract.register(account):
                    values[contract.name] = contract.address
                else:
                    print(f'unable to register new contract {contract.name}')
        print(json.dumps(values, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
