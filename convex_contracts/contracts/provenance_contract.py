"""
    starfish-provenance contract

"""
from convex_contracts.convex_contract import ConvexContract


class ProvenanceContract(ConvexContract):

    def __init__(self, convex, name=None):
        ConvexContract.__init__(self, convex, name or 'starfish.provenance', '0.0.2')

        self._source = f'''
            (def provenance-asset
                ^{{:private? true}}
                {{}}
            )
            (def provenance-owner
                ^{{:private? true}}
                {{}}
            )
            (defn version
                ^{{:callable? true}}
                []
                "{self.version}"
            )
            (defn assert-asset-id
                ^{{:callable? false}}
                [value]
                (when-not (and (blob? value) (== 32 (count (blob value)))) (fail "INVALID" "invalid asset-id"))
            )
            (defn assert-address
                ^{{:callable? false}}
                [value]
                (when-not (address? (address value)) (fail "INVALID" "invalid address"))
            )
            (defn register
                ^{{:callable? true}}
                [asset-id data]
                (assert-asset-id asset-id)
                (let [record {{:owner *caller* :timestamp *timestamp* :dta data}}]
                    (def provenance-asset
                        (assoc provenance-asset (blob asset-id)
                            (conj (get provenance-asset (blob asset-id))
                            record)
                        )
                    )
                    (def provenance-owner
                        (assoc provenance-owner *caller*
                            (conj (get provenance-owner *caller*)
                            (blob asset-id))
                        )
                    )
                    record
                )
            )
            (defn event-list
                ^{{:callable? true}}
                [asset-id]
                (assert-asset-id asset-id)
                (get provenance-asset (blob asset-id))
            )
            (defn asset-list
                ^{{:callable? true}}
                []
                (keys provenance-asset)
            )
            (defn owner-list
                ^{{:callable? true}}
                [owner-id]
                (assert-address owner-id)
                (get provenance-owner (address owner-id))
            )

'''
