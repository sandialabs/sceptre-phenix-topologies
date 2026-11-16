#!/bin/bash
# Injected to /etc/phenix/startup/influx-setup.sh on the historian; runs every boot (idempotent).
# Creates org/bucket/token once, then restarts telegraf so it picks up the injected telegraf.conf.
# Token/org/bucket must match telegraf.conf.
INFLUX_ORG=sceptre
INFLUX_BUCKET=waterway
INFLUX_TOKEN=waterway-historian-token
INFLUX_PASS=waterway-admin-pass   # lab range, not a secret

systemctl start influxdb
for _ in $(seq 1 60); do influx ping >/dev/null 2>&1 && break; sleep 1; done
if ! influx ping >/dev/null 2>&1; then echo "influxd not up" >&2; exit 1; fi
if influx setup --skip-verify --force --username admin --password "$INFLUX_PASS" \
     --org "$INFLUX_ORG" --bucket "$INFLUX_BUCKET" --token "$INFLUX_TOKEN" --retention 0 >/dev/null 2>&1; then
  echo "influx: initial setup done"
else
  echo "influx: already set up"   # setup fails once an instance is initialised
fi
systemctl restart telegraf
