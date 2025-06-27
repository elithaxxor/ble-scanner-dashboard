#!/usr/bin/env bash
set -e
OFFLINE=0
for arg in "$@"; do
    if [[ "$arg" == "--offline" ]]; then
        OFFLINE=1
    fi
done

grep -vE '^[[:space:]]*bleak' requirements.txt > /tmp/req.txt
if [[ $OFFLINE -eq 0 ]]; then
    pip install --upgrade pip
    pip install -r /tmp/req.txt
    pip install --upgrade bleak
else
    pip install -r /tmp/req.txt --no-index --find-links offline_pkgs || true
    pip install bleak --no-index --find-links offline_pkgs || true
fi
