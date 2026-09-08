# Crate context

Edition: 2024. Public API: `parse_port(&str) -> Result<u16, ParsePortError>`.
The current body calls `raw.parse::<u16>().unwrap()` and therefore panics on
invalid input. Unsafe code is forbidden by the crate policy.
Canonical gates: `cargo fmt --check`, `cargo clippy --all-targets --all-features
-- -D warnings`, and `cargo test --all-features`.
