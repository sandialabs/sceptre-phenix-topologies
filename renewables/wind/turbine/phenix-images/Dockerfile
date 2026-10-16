ARG MINIMEGA_IMAGE=ghcr.io/sandia-minimega/minimega:master
ARG OTSIM_IMAGE=ghcr.io/patsec/ot-sim:9dc3304
FROM ${MINIMEGA_IMAGE} AS minimega
FROM ${OTSIM_IMAGE}
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends iproute2 iptables procps \
    && rm -rf /var/lib/apt/lists/*
COPY --from=minimega /opt/minimega/bin/miniccc /miniccc
COPY init /init
RUN chmod 0755 /init /miniccc
ENTRYPOINT ["/init"]
