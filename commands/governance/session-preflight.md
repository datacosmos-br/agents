---
name: session-preflight
description:
  Run the session startup preflight covering runtime-lock verification, tracker identity, and the adoption sweep.
argument-hint:
  "[--repo PATH]... [--skip-adoption | --skip-mail]"
metadata:
  aihub.tags: '["decision:ADR-0028","effective:2026-09-27","route:project"]'
---

# Session Preflight

Run this before the first effect of a session, in this order, stopping at the
first red with its exact output. Every step reads state; none mutates.

1. **Tracker identity.** In a repository that contains `.beads/`, read the
   selected tracker context (`bd context --json`) and confirm the intended
   server/store identity before any mutation. A repository without `.beads/`
   invokes neither tracker command and creates no substitute.
2. **Runtime-lock verification (ADR-0028).** For every repository whose gates
   you will run or whose findings you will trust: compare the installed
   dependency commit in the physical `.venv`
   (`.venv/lib/python3*/site-packages/<dist>-*.dist-info/direct_url.json`,
   field `vcs_info.commit_id`) against the commit resolved for that
   dependency in the lock (`uv.lock`, the `source.git` `#<commit>` fragment).
   A mismatch voids every debt map the runtime would produce: sync through
   the repository's declared upgrade verb and recompute before planning.
3. **Adoption sweep.** List claimed/deferred work and flag every item abandoned
   under rule `bead-branch-pr-cadence` §2; adopt through the tracker
   with a recorded claim comment, never by silently starting the work.
4. **Coordination channel.** Read the session inbox (gc mail when available;
   tracker comments otherwise) for roll-call, lane claims, and blockers, and
   announce your own lane claim before the first effect.
5. **Unpushed-work check.** For each lane you own, if local commits are ahead
   of the remote by more than one landing cycle, land or push before starting
   new work — unpublished work is unreconcilable work.

Report the outcome as one line per step: pass, or the red output verbatim.
With `--skip-adoption` skip step 3; with `--skip-mail` skip step 4's read
(not the announce). Never normalize a red step into a pass.
