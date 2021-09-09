"""
    starfish.did contract

(import convex.trust :as trust)
(trust/trusted? owner *caller*)


"""
from convex_contracts.convex_contract import ConvexContract


class DIDRegistryContract(ConvexContract):

    def __init__(self, convex, name=None):
        ConvexContract.__init__(self, convex, name or 'starfish.did', '0.0.1')

        self._source = f'''
            (def registry
                ^{{:private? true}}
                {{}}
            )
            (def creator
                ^{{:private? true}}
                *caller*
            )
            (defn version
                ^{{:callable? true}}
                []
                "{self.version}"
            )
            (defn get-register
                ^{{:callable? false}}
                [did]
                (get registry did)
            )
            (defn set-register
                ^{{:callable? false}}
                [did owner-address ddo]
                (let [register-record {{:owner owner-address :ddo ddo}}]
                    (def registry (assoc registry did register-record))
                )
            )
            (defn delete-register
                ^{{:callable? false}}

                [did]
                (def registry (dissoc registry did))
            )
            (defn assert-owner
                ^{{:callable? false}}
                [did]
                (when-not (owner? did) (fail :NOT-OWNER "not owner"))
            )
            (defn assert-address
                ^{{:callable? false}}
                [value]
                (when-not (address? (address value)) (fail :INVALID "invalid address"))
            )
            (defn assert-did
                ^{{:callable? false}}
                [value]
                (when-not (blob? value) (fail :INVALID "DID is not a hex number"))
                (when-not (== 32 (count (blob value))) (fail :INVALID (str "DID is incorrect length of " (count (blob value)))))
            )
            (defn resolve?
                ^{{:callable? true}}
                [did]
                (assert-did did)
                (boolean (get-register did))
            )
            (defn resolve
                ^{{:callable? true}}
                [did]
                (assert-did did)
                (when-let [register-record (get-register did)] (register-record :ddo))
            )
            (defn owner
                ^{{:callable? true}}
                [did]
                (assert-did did)
                (when-let [register-record (get-register did)] (register-record :owner))
            )
            (defn owner?
                ^{{:callable? true}}
                [did]
                (= (owner did) *caller*)
            )
            (defn register
                ^{{:callable? true}}
                [did ddo]
                (assert-did did)
                (when (resolve? did) (assert-owner did))
                (set-register did *caller* ddo)
                did
            )
            (defn unregister
                ^{{:callable? true}}
                [did]
                (when (resolve? did)
                    (assert-owner did)
                    (delete-register did)
                    did
                )
            )
            (defn transfer
                ^{{:callable? true}}
                [did to-account]
                (when (resolve? did)
                    (assert-owner did)
                    (assert-address to-account)
                    (set-register did (address to-account) (resolve did))
                    [did (address to-account)]
                )
            )
            (defn owner-list
                ^{{:callable? true}}
                [the-owner]
                (assert-address the-owner)
                (mapcat (fn [v] (when (= (address the-owner) (get (last v) :owner)) [(first v)])) registry)
            )

        '''
