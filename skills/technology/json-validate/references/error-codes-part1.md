# Error Codes

Complete list of error codes reported by z-schema. Each error appears in `SchemaErrorDetail.code`.

## Table of contents

- [Type and format errors](#type-and-format-errors)
- [Enum errors](#enum-errors)
- [Combinator errors](#combinator-errors)
- [Array errors](#array-errors)
- [Numeric errors](#numeric-errors)
- [Object errors](#object-errors)
- [String errors](#string-errors)
- [Schema validation errors](#schema-validation-errors)
- [Reference and remote errors](#reference-and-remote-errors)
- [Draft-06+ errors](#draft-06-errors)
- [Draft-2019-09+ errors](#draft-2019-09-errors)
- [Runtime safeguard errors](#runtime-safeguard-errors)

---

## Type and format errors

| Code             | Message template                                  | Trigger                                   |
| ---------------- | ------------------------------------------------- | ----------------------------------------- |
| `INVALID_TYPE`   | Expected type {0} but found type {1}              | Value does not match schema `type`        |
| `INVALID_FORMAT` | Object didn't pass validation for format {0}: {1} | Value fails a registered format validator |

## Enum errors

| Code                 | Message template                  | Trigger                                                                       |
| -------------------- | --------------------------------- | ----------------------------------------------------------------------------- |
| `ENUM_MISMATCH`      | No enum match for: {0}            | Value not in `enum` list                                                      |
| `ENUM_CASE_MISMATCH` | Enum does not match case for: {0} | Value matches enum ignoring case (when `enumCaseInsensitiveComparison: true`) |

## Combinator errors

| Code              | Message template                                        | Trigger                             |
| ----------------- | ------------------------------------------------------- | ----------------------------------- |
| `ANY_OF_MISSING`  | Data does not match any schemas from 'anyOf'            | No `anyOf` branch matched           |
| `ONE_OF_MISSING`  | Data does not match any schemas from 'oneOf'            | No `oneOf` branch matched           |
| `ONE_OF_MULTIPLE` | Data is valid against more than one schema from 'oneOf' | Multiple `oneOf` branches matched   |
| `NOT_PASSED`      | Data matches schema from 'not'                          | Data validated against `not` schema |

These errors produce nested sub-errors in `detail.inner`.
