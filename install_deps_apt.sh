#!/bin/bash
set -e
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root using sudo" >&2
  exit 1
fi
while read -r line; do
  pkg=$(echo "$line" | cut -d= -f1 | tr 'A-Z' 'a-z')
  apt-get install -y "python3-$pkg"
done < "$(dirname "$0")/requirements.txt"

