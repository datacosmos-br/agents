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
| 3 | Backup/compaction chain (Dolt) | `gc-tz3x5` (city store) | CONSOLIDATED 2026-10-12. Canonical producer = **mol-dog-backup** (49 DBs, 4.8GB, fresh 10-12 10:35, ~6h cadence — city.toml gct-lv2pe: "the city's only scheduled Dolt backup producer"). bd native pipeline RETIRED (backup.enabled=false; the backup/dolt 2.5GB destination is a dead 10-07 remnant). FASE 1 = isolated RESTORE PROOF from .dolt-backup (hq + flext; the real acceptance — nothing downstream runs without it). FASE 2 = Mayor window: flext noms 2.78GB GC, compactor 171+ failures, flext+cosmos pending-push holds. FASE 3 = retire backup/dolt remnant + point the doctor bd-backup-freshness finding at the canonical pipeline (today it tracks the dead bd one). Closed into it: m2pkp, 3ami8c, 4by53n. jrdcsr is NOT this theme (workspace/Drive domain — own consolidation, T9). |
| 4 | Forks governance | `gc-aw0av` (city store) | CONSOLIDATED 2026-10-12. The real quinteto (measured): beads/gascity/cliproxy/ccs/cliproxy-mgmt in **marlon-costa-dc** (the old flext-mirror descriptions are superseded). F1 = identity migration (city.toml :400 cliproxyapi→cliproxy, :464 gct→gascity, dirs :714/:719; no-data-loss law). F2 = mirror cure (upstream-sync.yml failing 3 consecutive days on cliproxy; prove ONE green run + sync PR). F3 = uniform protection matrix (ccs/main UNPROTECTED 404 today; the other four mains protected; dc-use lanes with empty contexts) via the MERGED forge-governance-settings plan/apply verbs (#1131) with exit-0 receipts. Closed into it: aw0av.2/.3/.4/.5. Fixes are mine (gh admin available). |
| 5 | Runtime v3 — Model Pipeline | `gc-7ocws` (city store) | CONSOLIDATED 2026-10-12. OPERATOR RULE (verbatim): models are computed automatically — zero hardcoded member counts/lists, no chain-size limit, strict calculation/pipeline rules, must work. F1 = ai-hub dev cure (3 defects; owner ACTIVE on fix/model-projection-agents-20261012 @3f3da2881 — do NOT adopt). F2 = activate ai-hub-model-pipeline.service + prove generations 41/42 (enabled but dead; CCS consumption healthy on gen 40). F3 = dynamic lane computation (today: 4 lanes × exactly 2 hardcoded-shape members). F4 = real failover receipt. F5 = standing clean-base proof per owner repo. Closed into it: 7ocws.2, 3z7pc.4 (identical daemon leg), 3z7pc.3 (criterion replaced by the dynamic rule), 7ocws.4. Detached children now own themes: aw0av=T4, 6kei7=T2, uxtxnz=T6. |
| 6 | Attestation rollout | `gc-uxtnz` (city store) | CONSOLIDATED 2026-10-12. F1 PROVEN (dcdoc consumption post-make-work-removal: removal landed 30/09 + dev CI GREEN 10-11 ×2 after the adopt-fleet wave window). F2 = rollout on lanes (native hooks today are beads-integration only; NO attestation workflow in ai-hub; deliver hook in pre-commit/CI for ai-hub/algar/cosmos-docgen + a green run — venue: mine; the primitive is landed in flext-infra). F3 = PH-F8 EXTERNAL (cosmos-hoxsq.9, active cosmos-rig work since 10-11, depends PH-F7 — coordinate, don't adopt). PH-F1 resolved (hoxsq.2 CLOSED, CI GREEN). Closed into it: uxtxnz.5/.6/.7. |
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
