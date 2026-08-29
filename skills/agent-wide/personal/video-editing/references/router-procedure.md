# Video Editing procedure

# Video Editing

Activate for cutting, assembling, processing, or delivering edits from existing
source footage. Do not activate for prompt-only video generation.

## Preflight

Before creating a proxy, segment, transcript, or output, load and validate:

- every exact source path, stream, duration, frame rate, and usage right;
- the complete edit decision list, ordering, and requested creative assets;
- output container, codecs, resolution, frame rate, loudness, destination, and
  overwrite policy;
- the one operator- or project-selected editing toolchain and its versions;
- destination-filesystem staging, capacity, publication, cleanup, and recovery
  ownership;
- every non-derivable environment value genuinely required by an explicitly
  selected external service. Owner-calculated defaults require no consumer input.

Missing, empty, conflicting, unreadable, or unexpanded input stops at the first
defect with zero media or filesystem effects. Credentials come only from the
validated current process environment; keyring, secret-tool, profiles, aliases,
and embedded secrets are prohibited.

## Edit contract

1. Preserve source media byte-for-byte and write only to the approved staging
   and destination paths.
2. Convert the validated decision list into deterministic operations for the
   selected toolchain. Do not add cuts, captions, generated footage, music,
   voice, reframe, provider, or model that the operator did not request.
3. Execute child processes causally. The first nonzero exit, timeout, signal, or
   incomplete output stops the edit with its original failure; never catch and
   continue, retry, change encoder, switch provider/model, or finish manually.
4. Verify the staged artifact's exact segment order, duration, streams, codecs,
   resolution, frame rate, loudness, and requested content before publication.
5. Publish the complete verified artifact atomically. A failed verification or
   publication leaves no destination artifact and no proxy, segment, transcript,
   list, or partial render residue.

Cleanup may catch only to attach a secondary cleanup failure while re-raising
the original cause. Report the material artifact, preserved source, exact
verification evidence, and zero-residue result. Do not offer an alternate or
reduced deliverable.
