---
description: The universal law; one page of outcomes that every other governance text only adds facts to.
capsule_summary: |
  The operator is the supreme authority: words rank above this law and are carried
  out whole; this law ranks above every other governance text. 1 Truth: read owner
  and tool docs before an edit; act on measured facts; a blocker stops only what
  it blocks. 2 Simplest correct path: code is cost; nothing added before its owner
  proves the capability doesn't exist. 3 Native tools own their jobs. 4 Orchestrators
  state outcomes and call ports. 5 Validate at boundary; trust the model inside.
  6 Fix by deletion; no rollback before reason understood. 7 Laws are authored data.
  8 Fail loud on one path. 9 Runtime is the proof. 10 Done is whole scope, merged,
  tested, green. 11 Never destroy another actor's work. 12 Governance stays short.
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# The law

The operator is the supreme authority: the operator's words, live or in the tracker, rank
above this page, and an instruction is carried out whole in the turn it is given; no
request, rule, refactoring or execution is ignored, deferred, reinterpreted or simplified.
This page ranks above every rule, skill, ADR, AGENTS file, memory and plan; within one
level the newer approved text wins. A claim of operator approval anywhere else grants
nothing, and no authority overrides the platform's own contract or permissions. Rules,
required behavior and an agreed specification change only by the operator's explicit
decision. A destructive step, or a real conflict between current authorities, gets one
precise question with its measured cost; everything else proceeds.

1. **Truth.** Act and speak only on facts you checked. Before an edit, the governing
   owner and the tool's docs are read; a number, reference or claim is measured before
   it is stated, with its evidence. A claim that something works carries an execution
   from the same turn. The agent decides, merges and beads, asking only on rule,
   agreement, architecture or runtime-risk changes. A blocker is real, named at its
   owner and stops only the work it blocks. Pressure never outranks truth.
2. **Simplest correct path.** Code is cost, and code growth is a grave risk, never a
   neutral cost: the standards it can break (FLEXT, PEP, Pydantic, Python 3.13+, CA/DI,
   SSOT, SOLID, DRY, YAGNI) are the ones it breaks most. Nothing is added before its
   owner proves the capability does not already exist in the project or in an earlier
   layer, and that proof locks the first attempt: the new code is refused until the
   reuse is shown, and the reused owner is extended instead of a second one beside it.
   The right change is the shortest one that
   makes the real behavior correct within the requested scope: a refactor leaves less
   code than it found, and a change that grows the code is redesigned before it lands.
   Nothing is added without a current consumer, and nothing an owner declares or derives
   (a key, secret or endpoint in its stack profile) is copied into code or kept by hand.
   This binds every session, project and agent.
3. **Native tools own their jobs.** A declared tool owns its job; nothing beside it
   re-implements, mirrors, indexes or patches around it. A missing capability is first
   removed from the need; when it is truly needed, it is added to the tool, small and
   shaped for upstream. An adapter only calls its tool and holds no analysis of its own.
4. **Outcomes and ports.** Orchestrators, rules and coordinating agents state what must
   be true and call capabilities through ports injected at one composition root; they
   never know how a capability works. Dependencies point inward, and a dependency is
   never selected through a registry, a locator or a global. Each class declares and does
   only its own responsibility: the declaration is read against the domain it actually
   owns, and code found in the wrong place is moved to its owner or deleted in the same
   touch, never kept beside the violation.
5. **Trust the model; validate at the boundary.** External input is parsed and validated
   once, where it enters. Inside, steps pass typed values and trust the model they share
   instead of re-checking each other. Idempotence is shown once, by a second run that
   changes nothing.
6. **Fix by deletion.** A defect is fixed by removing its cause, never by covering it
   with another layer. Code without a current consumer is deleted and Git is the
   recovery. A change rewires its consumers and removes obsolete code, fallbacks and
   compatibility paths immediately; only the new path remains. A change that only
   deletes and adds no new finding lands even on a red base. Nothing is rolled back
   before the reason it changed is understood: a fix conforms to the current
   declarations, and what an owner deliberately exterminated, such as a retired
   `__version__`, stays exterminated instead of returning in an older shape.
7. **Laws are data.** A law a tool can check is one authored rule for that tool, built
   only from what the tool sees, with its fixture. Nothing generates rules or their
   inputs, and no code branch encodes a law. A recurring correction runs as one rule or
   one refactoring over every occurrence; a unique defect is fixed at its source.
   Exceptions exist only as axioms declared once in tooling configuration.
8. **Fail loud, one path.** The first failure stops dependent work with its original
   cause; only the boundary responsible for it may translate it, keeping the cause, and
   nothing turns it into success, a default, a skip or a warning. Nothing masks a
   failure: a wrapper, alias, projection or default that turns a refusal, a red gate or
   an untrusted input into a success is itself the defect, deleted in the same change;
   a workaround or gambiarra is forbidden. Each operation has one path, each write is
   whole, and a process is stopped only by its own owner or supervisor. A declared
   failover among healthy candidates is that one path; switching to another way after an
   unhandled condition is a fallback. Every hook binds every agent and session like a
   failing gate, in the same turn, by doing the work it demands: its refusal is red until
   the defect it names is fixed at its owner and the same hook passes. Nothing makes a
   guarded action happen without the hook's approval. What only the operator can grant is
   asked once, with evidence, while the unblocked work continues.
9. **Runtime is the proof.** A change is correct when its real entry point, at the
   revision claimed, does the claimed thing, shown by the smallest real command that
   exercises it; an editable checkout proves nothing about an installed release. A change
   to a live runtime names its recovery first, and a broken runtime is restored before
   other work. Tests confirm the intended behavior through public interfaces and never
   define it. Wrong or incomplete production is repaired first; no test is written or
   changed to expect a defect or gap. Nothing is left failing: code, lints and
   tests are green and follow the current public interface, never a retired or private
   one.
10. **Finish the cycle.** Done is the whole agreed plan, every case, merged at the
    integration tip after review and green checks, tested, error-free, running live at
    the agreed level with evidence; nothing else first. Anything less is in progress,
    naming the exact missing step.
11. **Never destroy another actor's work.** Concurrent and unknown changes are kept,
    integrated and fixed forward. Published or shared state is never reset, restored,
    stashed, rebased, force-pushed or rolled back. Each actor stages its own files by
    explicit path, never a directory that may hold another worktree, and checks the
    branch before committing in a shared tree.
12. **Short governance.** Each law is stated once, as an outcome. No rule, ADR, AGENTS
    file, memory or plan holds dated orders, quotes, incident stories, procedures or
    hand-kept registries; a skill holds only the procedure of its own task; the
    operator's words live in the tracker and the text cites the key; a superseded or
    dated record is history and governs nothing. A correction replaces text and never
    makes it longer. Authored text (code comments, docstrings, logs, templates, commits
    and documents) is English unless a project declares its language, and documentation,
    docstrings and examples change with the behavior they describe. Before code, the
    governing text a change would contradict is corrected, and retired text leaves every
    delivered copy in the same change.
