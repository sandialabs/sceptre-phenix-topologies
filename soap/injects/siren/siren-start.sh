#!/bin/bash

cd /siren || exit 1

pkill pybennu-siren

pybennu-siren -c ./siren.json >> /var/log/siren.log 2>&1
