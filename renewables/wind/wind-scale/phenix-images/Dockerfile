ARG MINIMEGA_IMAGE=ghcr.io/sandia-minimega/minimega@sha256:2546eb57f69268cd5bf64117c0c3d9aaff7a697b2242e8ff45a0ddc2c4b0eaa5
ARG OTSIM_IMAGE=ghcr.io/patsec/ot-sim@sha256:9cfa0d5a43a16e5f86f7979206edd210ce864bc9476ce50c26a40e60541cf063
FROM ${MINIMEGA_IMAGE} AS minimega
FROM ${OTSIM_IMAGE}
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends iproute2 iptables procps \
    && rm -rf /var/lib/apt/lists/*
COPY --from=minimega /opt/minimega/bin/miniccc /miniccc
COPY init /init
COPY readiness.py /usr/local/lib/wind-scale/readiness.py
RUN chmod 0755 /init /miniccc \
    && mkdir -p /usr/local/share \
    && dpkg-query -W > /usr/local/share/wind-scale-packages.txt \
    && sha256sum /miniccc > /usr/local/share/wind-scale-miniccc.sha256
ENTRYPOINT ["/init"]
