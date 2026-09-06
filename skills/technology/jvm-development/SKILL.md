---
name: jvm-development
description: 'java, kotlin, jvm development'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:marker:build.gradle","detect:marker:build.gradle.kts","detect:marker:gradlew","detect:marker:pom.xml","detect:marker:settings.gradle","detect:marker:settings.gradle.kts","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:project","technology:jvm","updates:manual","usage:router"]'
---

# JVM Development

Read `the procedure` (skill file) for Java, Kotlin, Gradle, Maven, or
mixed JVM work.

The repository owns language levels, plugins, dependency resolution, formatting,
static analysis, frameworks, and test engines. Use its wrapper and canonical
tasks; never introduce a parallel build path or assume one JVM framework.
