# Deployment workflow demo

Audience: platform engineers who maintain integration branches.

Before the change, an operator used eight commands to inspect a deployment,
approve it, and prepare rollback. The demo now uses two commands: `deploy plan`
shows the exact image and configuration diff, then `deploy apply` requires an
explicit approval and records the rollback revision.

Visible proof in the recording:

- the image digest changes from `sha256:91a` to `sha256:b44`;
- the configuration diff changes `workers` from 4 to 6;
- the approval prompt names integration revision `8f2c11a`;
- the rollback record points to the previous image and configuration together.

No customer adoption, reliability percentage, cost saving, or deployment-speed
measurement has been collected.
