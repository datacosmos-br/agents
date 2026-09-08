## Draft-06+ errors

| Code              | Message template                                          | Trigger                                       |
| ----------------- | --------------------------------------------------------- | --------------------------------------------- |
| `SCHEMA_IS_FALSE` | Boolean schema "false" is always invalid                  | `false` used as a schema (draft-06+)          |
| `CONST`           | Value does not match const: {0}                           | `const` mismatch (draft-06+)                  |
| `CONTAINS`        | Array does not contain an item matching the schema        | `contains` not satisfied (draft-06+)          |
| `PROPERTY_NAMES`  | Property name {0} does not match the propertyNames schema | `propertyNames` validation failed (draft-06+) |

## Draft-2019-09+ errors

| Code                               | Message template                                                                           | Trigger                                                  |
| ---------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------- |
| `ARRAY_UNEVALUATED_ITEMS`          | Unevaluated items are not allowed                                                          | `unevaluatedItems` violated (draft-2019-09+)             |
| `OBJECT_UNEVALUATED_PROPERTIES`    | Unevaluated properties are not allowed: {0}                                                | `unevaluatedProperties` violated (draft-2019-09+)        |
| `COLLECT_EVALUATED_DEPTH_EXCEEDED` | Schema nesting depth exceeded maximum ({0}) during unevaluated items/properties collection | Recursion depth exceeded during `unevaluated*` traversal |

## Runtime safeguard errors

| Code                           | Message template                                                                                                                  | Trigger                                                                                     |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `MAX_RECURSION_DEPTH_EXCEEDED` | Maximum recursion depth ({0}) exceeded. If your schema or data is deeply nested and valid, increase the maxRecursionDepth option. | General recursion depth exceeded (configurable via `maxRecursionDepth` option, default 100) |
