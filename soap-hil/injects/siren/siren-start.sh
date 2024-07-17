#!/bin/bash

cd /siren

pkill pybennu-siren

pybennu-siren -c ./siren.json >> /var/log/siren.log 2>&1