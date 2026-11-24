#!/usr/bin/env bash
set -euo pipefail

INVENTORY_FILE="inventory.yml"

distros=$(wsl.exe -l -q 2>/dev/null | tr -d '\r' | sed 's/\x00//g' | sed '/^$/d')

if [ -z "$distros" ]; then
    echo "Error: No WSL distributions found." >&2
    exit 1
fi

echo "Found WSL distributions:"
echo "$distros" | sed 's/^/  - /'
echo

cat > "$INVENTORY_FILE" <<'HEADER'
all:
  hosts:
HEADER

while IFS= read -r distro; do
    cat >> "$INVENTORY_FILE" <<EOF
    ${distro}:
      ansible_connection: wsl
      ansible_host: ${distro}
EOF
done <<< "$distros"

cat >> "$INVENTORY_FILE" <<'FOOTER'
  vars:
    ansible_wsl_user: root
FOOTER

echo "Wrote $INVENTORY_FILE with $(echo "$distros" | wc -l) distros."
