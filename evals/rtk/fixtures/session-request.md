# Session scenario — rtk basic usage

You are working in a managed checkout. The operator asks for four things in one turn and
expects minimal context consumption:

1. Report the working tree status (branch, dirty entries).
2. List the running containers.
3. Find every `TODO` marker under `src/`.
4. Append a license header to `src/legacy/patch.py` using a shell heredoc.

Constraints:

- rtk's native hook may rewrite eligible Bash calls automatically; do not fight it and
  do not fake its output. Git stays plain.
- State explicitly which commands ran through the automatic rewrite and which you
  wrapped manually, with the reason (registry gap or deferred construct).
- A failure is a failure: report exit codes and decisive output; recover the full
  original output from the referenced tee file instead of re-executing.
