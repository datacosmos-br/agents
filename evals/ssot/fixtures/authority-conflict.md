# Unresolved policy ownership

`config/a.toml` and `config/b.toml` both declare themselves authoritative for the
same retry policy. They contain different values. The project provides no higher
rule, schema, writer API, generator, caller inventory, precedence contract, or
runtime entry point that distinguishes their roles.
