# Skills

`config/skills.json` is the classification and distribution authority. Do not
duplicate its skill lists here.

- Personal targets receive workflows and non-technological capabilities.
- Projects receive project-generic bundles plus technology bundles selected from
  detected markers or dependencies.
- Every destination receives an independent physical copy; bundles contain no
  symbolic links, local cross-repository paths, or synchronization metadata.

Each skill is self-contained under `skills/<name>/`. Keep `SKILL.md` concise,
put conditional detail in local `references/`, and use comma-separated trigger
keywords in frontmatter descriptions.
