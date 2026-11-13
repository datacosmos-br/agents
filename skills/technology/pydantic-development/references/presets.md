# Preset selection

Choose by contract, not taste:

| Preset                                    | Config essence                                    | Use for                                        |
| ----------------------------------------- | ------------------------------------------------- | ---------------------------------------------- |
| `m.FrozenModel`                           | frozen + strict chain                             | read-only domain payloads, value data          |
| `m.FrozenValueModel` / `m.Value`          | frozen + value `__eq__`/`__hash__`                | value objects compared by content              |
| `m.ContractModel`                         | frozen, `validate_return`, `hide_input_in_errors` | immutable public contracts                     |
| `m.StrictModel` / `m.StrictBoundaryModel` | strict, `validate_default`                        | external ingress boundaries                    |
| `m.ManagedModel`                          | mutable, `validate_assignment`, `extra=forbid`    | validated mutable state                        |
| `m.FlexibleInternalModel`                 | normalized, `extra=ignore`                        | internal domain plumbing                       |
| `m.TaggedModel`                           | `extra=forbid` + `tag`                            | discriminated-union variants                   |
| `m.Metadata`                              | frozen audit fields                               | metadata blocks (timestamps, tags, attributes) |
| `m.Entity` / `m.AggregateRoot`            | id + timestamps + version + events                | DDD entities/aggregates                        |
| `m.TimestampedModel`                      | created/updated timestamps                        | any time-audited record                        |

Decision order: read-only domain data → frozen; external input → strict; mutable state →
managed; never "flexible" at a boundary; never frozen where the domain requires
assignment.

