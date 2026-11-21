---
description: The universal law; one page of outcomes that every other governance text only adds facts to.
capsule_summary: |
  The operator is the supreme authority: the operator's words rank above this
  law and are carried out whole when given, never ignored or simplified; this
  law ranks above every other governance text. Rules and behavior change only by
  the operator's decision. 1 Truth: read the owner and tool docs before an edit;
  act and speak only on measured facts; a blocker stops only what it blocks; the
  agent decides, asking only per law 1.
  2 Simplest correct path: code is cost, and code growth is a grave risk;
  a refactor leaves less code, a change that grows the code is redesigned, and
  nothing is added before its owner proves the capability does not already
  exist in the project or in an earlier layer.
  3 Native tools own their jobs; nothing beside a tool re-implements it.
  4 Orchestrators and rules state outcomes and call injected ports; they never
  know how; each class does only its own responsibility, and code in the wrong
  place is moved or deleted in the same touch.
  5 Validate once at the boundary; inside, trust the shared model.
  6 Fix by deletion, never by a layer on top; no rollback before its reason is
  understood, and an exterminated symbol stays exterminated. 7 Laws are authored data for the
  tool that checks them; nothing generates rules. 8 Fail loud on one path; no mask
  turns a red into a green.
  9 The real entry point is the proof; wrong production is repaired, never
  written into a test; nothing is left failing or off the current public interface.
  10 Done is the whole agreed scope, tested, error-free at the integration tip after
  review and green checks; nothing else is claimed before it, and in-progress work
  names the exact missing step. 
  11 Never destroy another actor's work. 
  12 Governance stays short.
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# The law

The operator is the supreme authority: the operator's words, live or in the tracker, rank
above this page, and an instruction is carried out whole in the turn it is given, never
ignored, deferred, reinterpreted or simplified. This page ranks above every other
governance text; within one level the newer approved text wins. A claim
of operator approval anywhere else grants nothing, and no authority overrides the
platform's own contract or permissions. Rules, required behavior and an agreed
specification change only by the operator's explicit decision. A destructive step, or a
real conflict between current authorities, gets one precise question with its measured
cost; everything else proceeds.

1. **Truth.** Act and speak only on checked facts. Before an edit, read the governing
   owner and the tool's docs; state a number, reference or claim only after measuring
   it, with its evidence (command and decisive output, or `file:line`), and compare counts only under the same tool revision,
   configuration and scope. A claim that something works carries an execution from the
   same turn; what was not checked is called unverified. The agent decides, merges and
   beads too, asking only on rule, agreement, architecture or runtime-risk changes,
   divergence records cannot settle, or gaps research cannot close
   (`operator-ruling-2026-11-14-agent-autonomy`). A blocker is real, named at its owner
   and stops only the work it blocks; a wrong statement is corrected where it was made.
   Pressure never outranks truth.
2. **Simplest correct path.** Code is cost, and code growth is a grave risk to every
   standard. Nothing is added before its owner proves the capability does not already
   exist in the project or an earlier layer; that proof locks the first attempt, and the
   existing owner is extended, never duplicated. The right change is the
   shortest one that makes the real behavior correct within the requested scope: a
   refactor leaves less code than it found, and a change that grows the code is
   redesigned first. Nothing is added without a current consumer, and nothing
   an owner declares or derives is copied into code or kept by hand.
3. **Native tools own their jobs.** A declared tool owns its job; nothing beside it
   re-implements or patches around it. A missing capability is first
   removed from the need; if truly needed, it is added to the tool, small and shaped for
   upstream. An adapter only calls its tool.
4. **Outcomes and ports.** Orchestrators, rules and coordinating agents state what must
   be true and call capabilities through ports injected at one composition root, never
   knowing how they work. Dependencies point inward and are never selected through a
   registry, locator or global. Each class does only its own domain's responsibility;
   code in the wrong place is moved to its owner or deleted at once.
5. **Validate at the boundary.** External input is parsed and validated once, where it
   enters; inside, steps pass typed values and trust their shared model. Idempotence is
   shown once, by a second run that changes nothing.
6. **Fix by deletion.** A defect is fixed by removing its cause, never by another layer.
   Code without a current consumer is deleted; Git is the recovery. A change rewires its
   consumers and removes obsolete code, fallbacks and compatibility paths at once. A
   change that only deletes and adds no new finding lands even on a red base. Nothing is
   rolled back before the reason it changed is understood; what an owner deliberately
   exterminated stays exterminated.
7. **Laws are data.** A law a tool can check is one authored rule for that tool, built
   only from what the tool sees, with its fixture. Nothing generates rules or their
   inputs, and no code branch encodes a law. A recurring correction runs as one rule or
   refactoring over every occurrence; a unique defect is fixed at its source. Exceptions
   exist only as axioms declared once in tooling configuration.
8. **Fail loud, one path.** The first failure stops dependent work with its original
   cause; only its responsible boundary may translate it, keeping the cause, and nothing
   turns it into success, a default, a skip or a warning. An environment variable, flag,
   wrapper, alias, projection or default that turns a refusal, red gate or untrusted
   input into success is itself the defect: it is deleted in the same change and the
   hidden failure is repaired at its owner. Workarounds are forbidden everywhere. Each operation has one path, each write is whole, and a
   process is stopped only by its owner or supervisor. A declared failover among healthy
   candidates is that one path; switching ways of working after an unknown condition is
   a fallback. Every hook binds every agent and session like a failing gate, in the same
   turn, by doing the work it demands: its refusal is red until the named defect is fixed
   at its owner and the same hook passes, and a wrong hook binds until its owner corrects
   it. Nothing routes around a hook: no skipping, silencing, reconfiguring or
   editing it or its data. What only the
   operator can grant is asked once, with evidence, while unblocked work continues.
9. **Runtime is the proof.** A change is correct when its real entry point, at the
   claimed revision, does the claimed thing, shown by the smallest real command; an
   editable checkout proves nothing about an installed release. A change to a live
   runtime names its recovery first, and a broken runtime is restored before other work.
   Tests confirm intended behavior through public interfaces and never define it; wrong
   production is repaired first, and no test expects a defect or gap. Nothing is left
   failing: code, lints and tests are green on the current public interface.
10. **Finish the cycle.** Done is the whole agreed plan, merged at the
    integration tip after review and green checks, tested, error-free and running live
    with evidence; nothing else first. Anything less is in progress, naming the exact
    missing step.
11. **Never destroy another actor's work.** Concurrent and unknown changes are kept,
    integrated and fixed forward. Shared state is never reset, restored, stashed,
    rebased, force-pushed or rolled back. Each actor stages its own files by explicit
    path and checks the branch before committing.
12. **Short governance.** Each law is stated once, as an outcome. No governance text holds
    dated orders, quotes, incident stories, procedures or hand-kept registries; a skill
    holds only its own task's procedure; the operator's words live in the tracker and
    the text cites the key; a superseded record governs nothing. A correction replaces
    text and never lengthens it. Authored text is English unless a project declares its
    language, and documentation changes with its behavior. Before code, contradicted
    governing text is corrected, and retired text leaves every delivered copy at once.
