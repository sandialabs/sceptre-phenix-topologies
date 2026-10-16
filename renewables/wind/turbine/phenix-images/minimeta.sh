#!/bin/sh
set -eu

test -x /usr/local/bin/minimega
cat > /usr/local/bin/mm <<'EOF'
#!/bin/sh
exec /usr/local/bin/minimega -e "$@"
EOF
chmod 0755 /usr/local/bin/mm

mkdir -p /etc/systemd/network
cat > /etc/systemd/network/10-scale.link <<'EOF'
[Match]
Driver=virtio_net
[Link]
NamePolicy=
Name=ens1
EOF

cat > /etc/systemd/system/minimega.service <<'EOF'
[Unit]
Description=Nested minimega for Scale containers
After=openvswitch-switch.service
Requires=openvswitch-switch.service
Before=phenix.service
[Service]
ExecStart=/usr/local/bin/minimega -nostdin -degree 0 -filepath /scale
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF
systemctl enable minimega.service
