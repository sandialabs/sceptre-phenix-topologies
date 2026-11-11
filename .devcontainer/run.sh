#!/usr/bin/env bash
# Run a command in the Linux dev container of this repository.
#
#   .devcontainer/run.sh                         start a shell
#   .devcontainer/run.sh prek run --all-files    run a command
#   .devcontainer/run.sh --print-image           print the image name
#
# The image tag is a hash of .devcontainer/Dockerfile. The script pulls that tag
# from GHCR. It builds the image locally only when the pull fails, for example
# on a branch that changes the Dockerfile.
#
# The checkout is mounted at the same path as on the host, so git works in a
# worktree: the .git file of a worktree names the main checkout by its path.
# The cache volume has one name for each UID, because a cache that one UID
# writes is read-only to the others.
#
# Environment:
#   DEVCONTAINER_IMAGE_REPO  image repository (default: the upstream GHCR one)
#   DEVCONTAINER_DOCKER_SOCK Docker socket to mount (default: /var/run/docker.sock)
#   DEVCONTAINER_CA_FILE     PEM file with more CA certificates to trust, for a
#                            network proxy that inspects TLS
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
root=$(git -C "$here" rev-parse --show-toplevel)
common=$(cd "$root" && cd "$(git rev-parse --git-common-dir)" && pwd)
repo=${DEVCONTAINER_IMAGE_REPO:-ghcr.io/sandialabs/sceptre-phenix-topologies/devcontainer}
image="$repo:df-$(git -C "$root" hash-object "$here/Dockerfile" | cut -c1-16)"
sock=${DEVCONTAINER_DOCKER_SOCK:-/var/run/docker.sock}

if [ "${1:-}" = "--print-image" ]; then
    echo "$image"
    exit 0
fi

if ! docker image inspect "$image" > /dev/null 2>&1; then
    if ! docker pull -q "$image" > /dev/null 2>&1; then
        echo "run.sh: cannot pull $image, so it is built locally" >&2
        docker build --cache-from "$repo:latest" -t "$image" "$here" >&2
    fi
fi

workdir=$root
cwd=$(pwd -P)
case "$cwd/" in
    "$root"/*) workdir=$cwd ;;
esac

args=(
    --rm --init
    --user "$(id -u):$(id -g)"
    -v "$root:$root"
    -v "sceptre-phenix-topologies-cache-$(id -u):/cache"
    -w "$workdir"
    -e CI -e GITHUB_ACTIONS -e PREK_SKIP -e SKIP -e TERM
)
case "$common/" in
    "$root"/*) ;;
    *) args+=(-v "$common:$common") ;;
esac
if [ -S "$sock" ]; then
    gid=$(docker run --rm -v "$sock:/docker.sock" --entrypoint stat "$image" -c %g /docker.sock)
    args+=(-v "$sock:/var/run/docker.sock" --group-add "$gid")
fi
if [ -t 0 ] && [ -t 1 ]; then
    args+=(-it)
fi

if [ "$#" -eq 0 ]; then
    set -- bash
fi
if [ -n "${DEVCONTAINER_CA_FILE:-}" ]; then
    ca=$(cd "$(dirname "$DEVCONTAINER_CA_FILE")" && pwd)/$(basename "$DEVCONTAINER_CA_FILE")
    args+=(-v "$ca:/etc/devcontainer-ca.pem:ro")
    # shellcheck disable=SC2016 # expanded by the shell in the container
    set -- sh -c '
        bundle=/tmp/devcontainer-ca-bundle.pem
        cat /etc/ssl/certs/ca-certificates.crt /etc/devcontainer-ca.pem > "$bundle"
        export SSL_CERT_FILE="$bundle" REQUESTS_CA_BUNDLE="$bundle" PIP_CERT="$bundle"
        export GIT_SSL_CAINFO="$bundle" NODE_EXTRA_CA_CERTS=/etc/devcontainer-ca.pem
        exec "$@"' sh "$@"
fi
exec docker run "${args[@]}" "$image" "$@"
