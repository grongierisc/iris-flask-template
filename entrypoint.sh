#!/bin/sh

set -eu

# start iris
/iris-main "$@" &
s
# wait for iris to be ready
/usr/irissys/dev/Container/waitReady.sh

#init iop
iop --init

# load production
iop --migrate /irisdev/app/community/settings.py

# start production
iop --start Python.Production
