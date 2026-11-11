# Linux tool set for the prek hooks of this repository, the same as CI uses.
# .devcontainer/run.sh tags the image with the hash of this file, so every
# input to the image must be in this file (there is no COPY).
FROM ubuntu:24.04@sha256:fe81560990fae86dc4743202b2cb4d3df98d0bcf949173cecef15ce1127ef852

LABEL org.opencontainers.image.source="https://github.com/sandialabs/sceptre-phenix-topologies" \
      org.opencontainers.image.description="Linux tools for the sceptre-phenix-topologies prek hooks" \
      org.opencontainers.image.licenses="GPL-3.0-only"

# PREK_VERSION must be at least minimum_prek_version in prek.toml.
ARG PREK_VERSION=0.5.10
ARG UV_VERSION=0.13.5
ARG DOCKER_APT_FINGERPRINT=9DC858229FC7DD38854AE2D88D81803C0EBFCD88

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# systemd provides systemd-analyze and desktop-file-utils provides
# desktop-file-validate. The Docker CLI lets the hadolint-docker hook start its
# container on the host's Docker daemon.
# hadolint ignore=DL3008
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl desktop-file-utils git git-lfs gnupg \
        python3 python3-pip python3-venv systemd \
    && install -d -m 0755 /etc/apt/keyrings \
    && curl -fsSL -o /etc/apt/keyrings/docker.asc https://download.docker.com/linux/ubuntu/gpg \
    && test "$(gpg --show-keys --fingerprint /etc/apt/keyrings/docker.asc | awk 'NR == 2 { gsub(/ /, ""); print }')" = "$DOCKER_APT_FINGERPRINT" \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu noble stable" \
        > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages "prek==${PREK_VERSION}" "uv==${UV_VERSION}" \
    && git lfs install --system \
    && git config --system --add safe.directory '*'

# run.sh starts the container with the host user's UID, which has no home
# directory in the image. The caches live in /cache, which run.sh mounts as a
# named volume; Docker copies this directory's mode into a new volume.
ENV HOME=/cache/home \
    PREK_HOME=/cache/prek \
    UV_CACHE_DIR=/cache/uv \
    XDG_CACHE_HOME=/cache/xdg
RUN install -d -m 1777 /cache /cache/home /cache/prek /cache/uv /cache/xdg
