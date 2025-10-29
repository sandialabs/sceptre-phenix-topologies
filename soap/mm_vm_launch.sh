#!/bin/bash

NAMESPACE=minimega
NAME=test
# used in order to do base image setup
# this makes changes persistent in the .qc2 image
SNAPSHOT=false
DISK=/phenix/images/ignition.qc2

# execute minimega commands inside the minimega container
MM="docker exec -it minimega mm -e namespace $NAMESPACE"


set -e
set -x
$MM namespace $NAMESPACE
$MM clear vm config
$MM vm config cpu host
$MM vm config memory 8192
$MM vm config net 500
$MM vm config vcpus 4
$MM vm config snapshot $SNAPSHOT
$MM vm config disk $DISK
$MM vm config qemu-append -vga qxl
$MM vm launch kvm $NAME
$MM vm start $NAME

