# AGENTS.md

Instructions for AI coding agents that work in this repository. Read
[CONTRIBUTING.md](.github/CONTRIBUTING.md) for the branch, commit, and pull
request rules.

## Checks

All checks are [prek](https://prek.j178.dev/) hooks in `prek.toml`. Some hooks
need Linux tools (for example, `systemd-analyze`), so local runs and CI run
the hooks in the Linux dev container in `.devcontainer/`. Docker must be
installed. You do not need prek on your machine.

Do not run prek directly on your machine, and do not skip a hook with `SKIP`
or `PREK_SKIP`. The result can be different from the result in CI.

Run these commands from the repository root:

| Task | Command |
|---|---|
| Run all hooks on all files, as CI does | `make lint` |
| Run hooks on some files | `make container-run CMD='prek run --files <file> <file>'` |
| Run a different command | `make container-run CMD='<command>'` |
| Start a shell | `make container-shell` |
| Register the git pre-commit hook | `make install-dev` |

`make lint`, `make container-run`, and `make container-shell` call
`.devcontainer/run.sh`. The pre-commit hook also calls it. You can call the
script directly, for example `.devcontainer/run.sh prek run --all-files`. The
script:

- Pulls the image from GHCR. It builds the image locally only when the pull
  fails, for example on a branch that changes `.devcontainer/Dockerfile`.
- Mounts the checkout at the same path as on the host, so it also works in a
  git worktree.
- Runs the command as your user, so files that a hook changes stay yours.

Behind a network proxy that inspects TLS, prek cannot download the tools of
some hooks (the error is `invalid peer certificate: UnknownIssuer`). Set
`DEVCONTAINER_CA_FILE` to a PEM file that contains the CA certificates of the
proxy. Get this file from your IT department. Only `run.sh` uses this variable.

## Dev container

- `.devcontainer/Dockerfile` contains every pinned tool version.
  `PREK_VERSION` must be at least `minimum_prek_version` in `prek.toml`.
- The image tag is a hash of the Dockerfile. The "Dev container" workflow
  publishes the image when the Dockerfile changes on `main`.
- When a hook needs a new system tool, add the tool to the Dockerfile. Do not
  install it in a workflow step.
