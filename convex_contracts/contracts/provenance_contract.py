"""
    starfish-provenance contract

"""
from convex_api import ConvexAPI
from convex_contracts.convex_contract import ConvexContract


class ProvenanceContract(ConvexContract):

    def __init__(self, name = None):
        ConvexContract.__init__(self, name or 'starfish-provenance', '0.0.1')

        self._source = f'''
            (def provenance [])
            (defn version [] "{self.version}")
            (defn assert-asset-id [value]
                (when-not (and (blob? value) (== 32 (count (blob value)))) (fail "INVALID" "invalid asset-id"))
            )
            (defn assert-address [value]
                (when-not (address? (address value)) (fail "INVALID" "invalid address"))
            )
            (defn register [asset-id]
                (assert-asset-id asset-id)
                (let [record {{:owner *caller* :timestamp *timestamp* :asset-id (blob asset-id)}}]
                    (def provenance (conj provenance record))
                    record
                )
            )
            (defn event-list [asset-id]
                (assert-asset-id asset-id)
                (mapcat (fn [record] (when (= (blob asset-id) (record :asset-id)) [record])) provenance)
            )
            (defn event-owner [owner-id]
                (assert-address owner-id)
                (mapcat (fn [record] (when (= (address owner-id) (record :owner)) [record])) provenance)
            )
            (defn event-timestamp [time-from time-to]
                (mapcat
                    (fn [record]
                        (when
                            (and
                                (<= time-from (record :timestamp))
                                (>= time-to (record :timestamp))
                            )
                        [record] )
                    )
                provenance)
            )
            (export event-list event-owner event-timestamp register version)

'''
