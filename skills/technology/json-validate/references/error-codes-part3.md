## String errors

| Code         | Message template                             | Trigger                        |
| ------------ | -------------------------------------------- | ------------------------------ |
| `MIN_LENGTH` | String is too short ({0} chars), minimum {1} | Below `minLength`              |
| `MAX_LENGTH` | String is too long ({0} chars), maximum {1}  | Above `maxLength`              |
| `PATTERN`    | String does not match pattern {0}: {1}       | `pattern` regex does not match |

## Schema validation errors

These are reported during `validateSchema()`, not during data validation.

| Code                           | Message template                                      | Trigger                                    |
| ------------------------------ | ----------------------------------------------------- | ------------------------------------------ |
| `KEYWORD_TYPE_EXPECTED`        | Keyword '{0}' is expected to be of type '{1}'         | Schema keyword has wrong type              |
| `KEYWORD_UNDEFINED_STRICT`     | Keyword '{0}' must be defined in strict mode          | Missing keyword when `strictMode: true`    |
| `KEYWORD_UNEXPECTED`           | Keyword '{0}' is not expected to appear in the schema | Extra keyword with `noExtraKeywords: true` |
| `KEYWORD_MUST_BE`              | Keyword '{0}' must be {1}                             | Keyword value out of specification         |
| `KEYWORD_DEPENDENCY`           | Keyword '{0}' requires keyword '{1}'                  | Missing dependent keyword                  |
| `KEYWORD_PATTERN`              | Keyword '{0}' is not a valid RegExp pattern: {1}      | Invalid regex in `pattern`                 |
| `KEYWORD_VALUE_TYPE`           | Each element of keyword '{0}' array must be a '{1}'   | Array keyword element has wrong type       |
| `UNKNOWN_FORMAT`               | There is no validation function for format '{0}'      | Format not registered and not built-in     |
| `CUSTOM_MODE_FORCE_PROPERTIES` | {0} must define at least one property if present      | `forceProperties: true` violated           |

## Reference and remote errors

| Code                              | Message template                                        | Trigger                              |
| --------------------------------- | ------------------------------------------------------- | ------------------------------------ |
| `REF_UNRESOLVED`                  | Reference has not been resolved during compilation: {0} | `$ref` not resolved at compile time  |
| `UNRESOLVABLE_REFERENCE`          | Reference could not be resolved: {0}                    | `$ref` target not found              |
| `SCHEMA_NOT_REACHABLE`            | Validator was not able to read schema with uri: {0}     | Schema reader returned nothing       |
| `SCHEMA_TYPE_EXPECTED`            | Schema is expected to be of type 'object'               | Schema is not an object              |
| `SCHEMA_NOT_AN_OBJECT`            | Schema is not an object: {0}                            | Schema not an object (with value)    |
| `ASYNC_TIMEOUT`                   | {0} asynchronous task(s) have timed out after {1} ms    | Async format exceeded `asyncTimeout` |
| `PARENT_SCHEMA_VALIDATION_FAILED` | Schema failed to validate against its parent schema     | Meta-schema validation failed        |
| `REMOTE_NOT_VALID`                | Remote reference didn't compile successfully: {0}       | Remote schema failed compilation     |
