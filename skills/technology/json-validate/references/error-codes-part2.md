## Array errors

| Code                      | Message template                                 | Trigger                                                               |
| ------------------------- | ------------------------------------------------ | --------------------------------------------------------------------- |
| `ARRAY_LENGTH_SHORT`      | Array is too short ({0}), minimum {1}            | Array length below `minItems`                                         |
| `ARRAY_LENGTH_LONG`       | Array is too long ({0}), maximum {1}             | Array length above `maxItems`                                         |
| `ARRAY_UNIQUE`            | Array items are not unique (indexes {0} and {1}) | `uniqueItems: true` violated                                          |
| `ARRAY_ADDITIONAL_ITEMS`  | Additional items not allowed                     | Extra items when `additionalItems: false`                             |
| `ARRAY_UNEVALUATED_ITEMS` | Unevaluated items are not allowed                | Extra items when `unevaluatedItems: false` or schema (draft-2019-09+) |

## Numeric errors

| Code                | Message template                                         | Trigger                        |
| ------------------- | -------------------------------------------------------- | ------------------------------ |
| `MULTIPLE_OF`       | Value {0} is not a multiple of {1}                       | `multipleOf` check failed      |
| `MINIMUM`           | Value {0} is less than minimum {1}                       | Below `minimum`                |
| `MINIMUM_EXCLUSIVE` | Value {0} is equal or less than exclusive minimum {1}    | At or below `exclusiveMinimum` |
| `MAXIMUM`           | Value {0} is greater than maximum {1}                    | Above `maximum`                |
| `MAXIMUM_EXCLUSIVE` | Value {0} is equal or greater than exclusive maximum {1} | At or above `exclusiveMaximum` |

## Object errors

| Code                               | Message template                                          | Trigger                                                                       |
| ---------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `OBJECT_PROPERTIES_MINIMUM`        | Too few properties defined ({0}), minimum {1}             | Below `minProperties`                                                         |
| `OBJECT_PROPERTIES_MAXIMUM`        | Too many properties defined ({0}), maximum {1}            | Above `maxProperties`                                                         |
| `OBJECT_MISSING_REQUIRED_PROPERTY` | Missing required property: {0}                            | Missing `required` property                                                   |
| `OBJECT_ADDITIONAL_PROPERTIES`     | Additional properties not allowed: {0}                    | Extra property with `additionalProperties: false`                             |
| `OBJECT_UNEVALUATED_PROPERTIES`    | Unevaluated properties are not allowed: {0}               | Extra property with `unevaluatedProperties: false` or schema (draft-2019-09+) |
| `OBJECT_DEPENDENCY_KEY`            | Dependency failed - key must exist: {0} (due to key: {1}) | `dependencies` key requirement not met                                        |
