# Theme Consolidation Protocol — agents alignment work

Status: ACTIVE (operator directive 2026-10-12). This document is the rules
layer for any NEW session picking up the alignment work. Read it fully before
touching any bead.

## The mission

Analyze recent sessions, updated beads across ALL projects/agents/stores, and
adjust skills, commands, projections, rules, ADRs — everything — so there are
NO more divergences. One theme at a time.

## The protocol (per theme, in order)

1. **Locate** every bead of the theme — open AND closed — across all stores
   (city `/home/marlonsc/gc`, agents `~/agents`, ai-hub `~/ai-hub`, algar,
   flext). Keyword sweep on titles + the closed corpus.
2. **Correlate** against current code, docs, ADRs, and REALITY (runtime
   measurement, not descriptions), plus LONG-RANGE git archaeology: past
   discussions, past cures (were they upstream or workarounds? did they
   recur?), past rules.
3. **Critical analysis**: what should this theme actually BE now? What will
   really be implemented (YAGNI — no aspirational phases)? Who owns each fix
   (which repo, which lane, which person/session)?
4. **Discuss with the operator** — ONLY after the research above is done.
   Questions must be real divergences (ownership, activation, scope
   direction) — never things a grep would have answered.
5. **Consolidate**: rewrite ONE bead as the theme SSOT (phased plan, venues,
   acceptance criteria, measured evidence), close every other bead of the
   theme with a disposition note pointing at the SSOT.
6. **Persist**: update THIS document's theme map, the SSOT bead, and session
   memory. A fresh session must be able to resume from beads + docs alone.

## Standing laws during consolidation

- No claiming / no assignee changes (operator removed all claims; force is
  authorized on closes/updates).
- Every closure carries evidence (measured, with paths/shas/dates).
- Never hand-edit generated projections; fix the SSOT input and regenerate.
- Fleet doctrine (current): `dependency_revisions` pins are FORBIDDEN by the
  new workspace schema — canonical branch-ref family, one provider one ref;
  manifest identity org == live Git origin org; ledger_id/prefix == observed
  beads identity; `codegen-org.yaml` needs `release.build_constraints`
  (hash-pinned) + `refactor_csv_campaigns`.
- Subagents do COMPLETE cycles in their beads (research → decision → action →
  evidence), never fragments to assemble later.

## Theme map (2026-10-12)

| # | Theme | SSOT (single open bead) | State |
|---|-------|-------------------------|-------|
| 1 | Learning loop (ADR-0011) | `aihub-hy4lf` (ai-hub store) | Operator ruled the runtime code is ai-hub's and lands NOW. S1 LANDED: PR datacosmos-br/ai-hub #1142 (m.Learning models + 12 tests). S2-S4 pending. BLOCKER: origin/dev of ai-hub broken ×3 (AiHubMiseModels stale; tools.yaml digests; native_models.py truncated — residue of lane aihub-01b1w @3f3da2881, needs its PR). S5 = gc cadence (compound pack import: 1 TOML line pin sha:33d3a430 + `gc pack lock`; source proven: gastownhall/gascity-packs). |
| 2 | City tools (gascity/bd/doctor/orders) | `gc-6kei7` (city store) | Operator ruled: I fix Go on the fork `marlon-costa-dc/gascity` lane dc-use (merge --no-ff, tests, Go boundary law), release fc.7, re-measure. F1: doctor pool-idle timeout + orphan-sweep internal deadline (53 fails, last 10-11 20:13 WITH fc.6 live) + bd `list --assignee` filter gap. F2: author orders/digest-generate.toml (activation authorized). F3: bd cross-repo alias qualification vs bd 1.3.0-fd.7. Closed into it: w1uj8d, sg8z2, ppv3l (primary manifestations cured by fc.6 exact-orphan-cleanup), p2xuhm, ntu5, sn1if (not reproducing). |
| 3 | Backup/compaction chain | NOT yet consolidated | Open: tz3x5 (restore proof), m2pkp, 3ami8c, 4by53n (pending-push holds, Mayor window), jrdcsr (datacosmos workspace). Gated chain: restore proof → GC → compactor → holds. Needs a Mayor-scheduled window. |
| 4 | Forks governance | NOT yet consolidated | Open: aw0av + .2/.3/.4/.5 (forks live in marlon-costa-dc, mirror broken since 10-07). |
| 5 | Runtime v3 / management v3 | NOT yet consolidated | Open: 7ocws + .2/.4, 3z7pc.3/.4. Premise "supervisor inactive" is DEAD (supervisor active since 10-10). 3z7pc.3 needs operator amendment on ">3 members same-lane" criterion. |
| 6 | Attestation rollout | NOT yet consolidated | Open: uxtxnz + .5/.6/.7. PH-F1 resolved; PH-F8 in course (cosmos-hoxsq.9). |
| 7 | algar type-debt grind | (work, not beads — algar store empty) | 879→210 after three cascade roots (commit 33fadfb6 on lane reconcile/content-migration-20261003): settings TYPE_CHECKING protocol port; tests TypeVar bound algar_s; Acl alias→subclass. Remaining: mypy 109, pyrefly 34, codemod 17, deployment-contract vs new flext-tests tm.fail. |
| 8 | flext wave items | NOT yet consolidated | ajnk6n (tip check residue 331/46 + the wheel regression fixed by PR flext-infra #1940, MERGED), nwnp2 (gitignore duplicate: locus = fleet config/codegen.yaml:1613/1618 dead instances — small upstream PR pending). |

Fleet PRs landed this cycle (reference): flext-infra #1940 (wheel config
include restoration — gen was broken for ALL standalone consumers),
flext-ldap #191 (12 duplicated `self` params — SyntaxError on import),
flext-ldap #212-era wave, agents laws 13/14 landing (6b0a52d1).

## Session-start checklist (new sessions)

1. Read this file + the SSOT beads of themes you touch.
2. `bd list --json` in each store — verify no theme has 2+ open beads; if a
   consolidation was REOPENED by a parallel session, re-close with the note
   "theme SSOT is X" and coordinate on the SSOT.
3. Never start a new theme before the current one is consolidated and
   persisted here.
