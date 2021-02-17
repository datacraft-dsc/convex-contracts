# Convex Contracts

![testing](https://github.com/datacraft-dsc/convex-contracts/workflows/testing/badge.svg)
![contracts_deploy](https://github.com/datacraft-dsc/convex-contracts/workflows/contracts_deploy/badge.svg)

---


## Maintainers

 [Developer Datacraft team](developer@datacraft.sg)

## Deploy Contracts

To deploy contracts you need to run the `./tools/convex_contract_tool.py`.

```bash

./tools/convex_contract_tool.py --keyword="secret keywords you get from a private store which is not stored in git" deploy

```

## Contract names

+ **starfish.did**

+ **starfish.provenance**

You need these names to use the contracts below.


## Getting contract addresses using convex

Using the convex api to get the contract address based on the contract name and owner address.

```python
    >>> from convex_api import ConvexAPI
    >>> convex_api = ConvexAPI('https://convex.world')
    >>> convex_api.query('(call *registry* (cns-resolve "starfish-test.did"))', 9)
    {'value': 1483}

```

## Getting contract addresses using the contract class

Using the contract class, it will resolve the correct address.

```python
    >>> from convex_api import ConvexAPI
    >>> from convex_contracts.contracts import DIDRegistryContract

    >>> convex_api = ConvexAPI('https://convex.world')
    >>> contract = DIDRegistryContract(convex_api)
    >>> contract.address
    1483
    >>> contract.owner_address
    1482
    >>> account = convex_api.create_account()
    >>> convex_api.topup_account(account)
    >>> contract.send('(register 0xe5b56a945e6ea79debe04028fef0345297b02d3087d28ffac953c2bfc2c58aaa "test - ddo")', account)
    {'value': 'e5b56a945e6ea79debe04028fef0345297b02d3087d28ffac953c2bfc2c58aaa'}

```

## Using the contract in the convex sandbox

You need to start a convex sandbox at https://convex.world/sandbox

```
    (import starfish.did :as did)

    *aliases*
        {did 1483}

    (did/register 0xe5b56a945e6ea79debe04028fef0345297b02d3087d28ffac953c2bfc2c58aaa "test - ddo")
        0xe5b56a945e6ea79debe04028fef0345297b02d3087d28ffac953c2bfc2c58aaa
```

## Auto deploying the contracts

If for some reason the test convex.world block chain network gets reset, and the test contracts are no longer available.

You can deploy the contracts again, by pushing to the **master** branch, or by re-running a past contracts_deploy workflow. See the [workflow contracts_deploy](https://github.com/datacraft-dsc/convex-contracts/actions?query=workflow%3Acontracts_deploy)

## Release Process

See [Release Process](https://github.com/datacraft-dsc/convex-contracts/blob/develop/RELEASE_PROCESS.md)

## License

```
Copyright 2018-2021 Datacraft Pte. Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
