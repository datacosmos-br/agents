# C++ development procedure

1. Read the build-system owner and determine the selected C/C++ standard,
   compiler set, target graph, feature flags, and public headers.
2. Trace ownership and lifetime across the changed boundary. Prefer automatic
   storage and RAII; use smart pointers only when they express actual ownership.
3. Preserve value categories, exception guarantees, thread-safety contracts,
   binary interfaces, and platform constraints.
4. Prefer standard-library types and algorithms when they make invariants
   clearer. Avoid raw allocation, unchecked narrowing, dangling views, data
   races, and undefined behavior.
5. Keep synchronization scoped and ownership explicit. Every thread or task must
   have bounded lifetime, cancellation or joining, and visible error handling.
6. Exercise the real target through the project build command. Run the selected
   formatter, compiler warnings, static analysis, tests, and configured
   sanitizers for the affected targets.

Do not mandate CMake, GoogleTest, a naming convention, warning flags, or a
language standard when the project declares a different supported contract.
Generated headers and sources are changed through their generator.
