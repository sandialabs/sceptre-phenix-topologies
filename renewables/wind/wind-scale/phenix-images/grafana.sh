#!/bin/sh
set -eu

apt-get update
apt-get install -y ca-certificates curl gpg
install -d -m 0755 /etc/apt/keyrings
curl -fsSL https://apt.grafana.com/gpg.key -o /tmp/grafana.key
gpg --batch --yes --dearmor -o /etc/apt/keyrings/grafana.gpg /tmp/grafana.key
curl -fsSL https://artifacts.elastic.co/GPG-KEY-elasticsearch -o /tmp/elastic.key
gpg --batch --yes --dearmor -o /etc/apt/keyrings/elastic.gpg /tmp/elastic.key
rm /tmp/grafana.key /tmp/elastic.key
echo 'deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main' \
    > /etc/apt/sources.list.d/grafana.list
echo 'deb [signed-by=/etc/apt/keyrings/elastic.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main' \
    > /etc/apt/sources.list.d/elastic.list
apt-get update
apt-get install -y grafana=12.3.0 elasticsearch=8.19.5
apt-mark hold grafana elasticsearch
mkdir -p /usr/local/share
dpkg-query -W > /usr/local/share/wind-scale-packages.txt

mkdir -p /etc/elasticsearch/jvm.options.d /etc/sysctl.d
printf '%s\n' '-Xms1g' '-Xmx1g' > /etc/elasticsearch/jvm.options.d/heap.options
echo 'vm.max_map_count=262144' > /etc/sysctl.d/90-elasticsearch.conf
systemctl enable grafana-server.service elasticsearch.service
