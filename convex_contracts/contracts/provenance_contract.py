"""
    starfish-provenance contract

"""
from convex_contracts.convex_contract import ConvexContract


class ProvenanceContract(ConvexContract):

    def __init__(self, convex, name=None):
        ConvexContract.__init__(self, convex, name or 'starfish.provenance', '0.0.4')

        self._source = f'''
            (def provenance-data
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
            (defn assert-blob-id
                ^{{:callable? false}}
                [value]
                (when-not (and (blob? value) (== 32 (count (blob value)))) (fail "INVALID" "invalid asset or did id"))
            )
            (defn assert-address
                ^{{:callable? false}}
                [value]
                (when-not (address? (address value)) (fail "INVALID" "invalid address"))
            )

            (defn register
                ^{{:callable? true}}
                [did-id asset-id data]
                (assert-blob-id did-id)
                (assert-blob-id asset-id)
                (let [record {{:owner *caller* :timestamp *timestamp* :data data}} owner-record {{:did-id did-id :asset-id asset-id}}]
                    (def provenance-data
                        (assoc-in provenance-data [(blob did-id) (blob asset-id)] record)
                    )
                    (def provenance-owner
                        (assoc provenance-owner *caller*
                            (conj (get provenance-owner *caller*)
                            owner-record)
                        )
                    )
                    record
                )
            )
            (defn get-data
                ^{{:callable? true}}
                [did-id asset-id]
                (assert-blob-id did-id)
                (assert-blob-id asset-id)
                (get-in provenance-data [(blob did-id) (blob asset-id)])
            )
            (defn did-id-list
                ^{{:callable? true}}
                [did-id]
                (assert-blob-id did-id)
                (get-in provenance-data [(blob did-id)])
            )
            (defn owner-list
                ^{{:callable? true}}
                [owner-id]
                (assert-address owner-id)
                (get provenance-owner (address owner-id))
            )

'''
