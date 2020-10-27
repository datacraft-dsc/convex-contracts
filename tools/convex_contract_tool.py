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


from convex_api import Account as ConvexAccount
from convex_api import ConvexAPI

from convex_contracts.convex_contract import ConvexContract
from convex_contracts.utils import auto_topup_account


CONTRACT_PACKAGE = 'convex_contracts.contracts'
DEFAULT_URL = 'https://convex.world'

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
        '-a',
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
        '-p',
        '--password',
        help='password to access the account'
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
        if args.keyfile is None or args.password is None:
            print('You need to provide an account keyfile and password to deploy the contracts')
            return
        logger.debug(f'loading account keyfile {args.keyfile}')
        if not os.path.exists(args.keyfile):
            print(f'Cannot find account keyfile {args.keyfile}')
        account = ConvexAccount.import_from_file(args.keyfile, args.password)
        logger.debug(f'connecting to convex network {args.url}')
        convex = ConvexAPI(args.url)
        if not convex:
            print(f'Cannot connect to the convex network at {args.url}')
            return

        if args.auto_topup:
            logger.debug('auto topup of account balance')
            auto_topup_account(convex, account)

        contract_items = load_contracts(CONTRACT_PACKAGE)
        values = {
            'address': account.address,
            'contracts': {}
        }
        for class_name, contract_class in contract_items.items():
            contract = contract_class()
            logger.debug(f'deploying contract {class_name} {contract.name}')
            values['contracts'][contract.name] = contract.deploy(convex, account)
        print(json.dumps(values, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
