# AGENTS.md

Instructions for AI coding agents that work in this repository. Read
[CONTRIBUTING.md](.github/CONTRIBUTING.md) for the branch, commit, and pull
request rules.

## Checks

All checks are [prek](https://prek.j178.dev/) hooks in `prek.toml`. CI runs
them in the Linux dev container in `.devcontainer/`. Some hooks need Linux
tools (for example, `systemd-analyze`), so run the checks in the same
container.

Do not skip a hook with `SKIP` or `PREK_SKIP` because a tool is missing on
your machine. Run the hook in the dev container.

### Linux and macOS

Docker must be installed. Run these commands from the repository root:

| Task | Command |
|---|---|
| Run all hooks on all files, as CI does | `make container-lint` |
| Run hooks on some files | `make container-run CMD='prek run --files <file> <file>'` |
| Run a different command | `make container-run CMD='<command>'` |
| Start a shell | `make container-shell` |

`make` calls `.devcontainer/run.sh`. You can also call the script directly,
for example `.devcontainer/run.sh prek run --all-files`. The script:

- Pulls the image from GHCR. It builds the image locally only when the pull
  fails, for example on a branch that changes `.devcontainer/Dockerfile`.
- Mounts the checkout at the same path as on the host, so it also works in a
  git worktree.
- Runs the command as your user, so files that a hook changes stay yours.

Behind a network proxy that inspects TLS, prek cannot download the tools of
some hooks (the error is `invalid peer certificate: UnknownIssuer`). Set
`DEVCONTAINER_CA_FILE` to a PEM file that contains the CA certificates of the
proxy. Get this file from your IT department. Only `run.sh` uses this variable.

### Windows

Windows usually does not have GNU make. Use one of these procedures in
PowerShell. Use a normal clone, not a git worktree, and clone with
`core.autocrlf=false`. CRLF line endings cause hook failures.

With the Dev Containers CLI (Node.js must be installed):

1. Start the container:

   ```powershell
   npx @devcontainers/cli up --workspace-folder .
   ```

2. Run the hooks:

   ```powershell
   npx @devcontainers/cli exec --workspace-folder . prek run --all-files
   ```

With Docker only:

1. Pull the image:

   ```powershell
   docker pull ghcr.io/sandialabs/sceptre-phenix-topologies/devcontainer:latest
   ```

2. Run the hooks:

   ```powershell
   docker run --rm -v "${PWD}:/workspace" -w /workspace `
     -v sceptre-phenix-topologies-cache-root:/cache `
     -v /var/run/docker.sock:/var/run/docker.sock `
     ghcr.io/sandialabs/sceptre-phenix-topologies/devcontainer:latest `
     prek run --all-files
   ```

The `latest` image is built from the `.devcontainer/Dockerfile` of the `main`
branch. If the pull fails, or if your branch changes the Dockerfile, build the
image first with `docker build -t <name> .devcontainer`, and then use `<name>`
in place of the GHCR image name.

In VS Code, the Dev Containers extension also opens the repository in the
container (command "Dev Containers: Reopen in Container").

## Dev container

- `.devcontainer/Dockerfile` contains every pinned tool version.
  `PREK_VERSION` must be at least `minimum_prek_version` in `prek.toml`.
- The image tag is a hash of the Dockerfile. The "Dev container" workflow
  publishes the image when the Dockerfile changes on `main`.
- When a hook needs a new system tool, add the tool to the Dockerfile. Do not
  install it in a workflow step.
