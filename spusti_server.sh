#!/usr/bin/env bash
# Spustí jednoduchý HTTP server pre adresár s návodmi, dostupný v lokálnej sieti.
# Použitie: ./spusti_server.sh [port]      (predvolený port 8080)
# Zastavenie: Ctrl+C

set -euo pipefail

PORT="${1:-8080}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Chyba: python3 nie je nainštalovaný (sudo apt install python3)." >&2
    exit 1
fi

if ss -ltn | grep -qE "[:.]${PORT}\b"; then
    echo "Chyba: port ${PORT} je už obsadený. Skúste iný: $0 8081" >&2
    exit 1
fi

IP="$(hostname -I 2>/dev/null | awk '{print $1}')"

echo "Adresár:  ${DIR}"
echo "Lokálne:  http://localhost:${PORT}/"
[ -n "${IP}" ] && echo "V sieti:  http://${IP}:${PORT}/"
echo
echo "Ak sa stránka z iného zariadenia nenačíta, povoľte port vo firewalle:"
echo "  sudo ufw allow from 192.168.101.0/24 to any port ${PORT} proto tcp"
echo
echo "Zastavenie: Ctrl+C"
echo

exec python3 -m http.server "${PORT}" --bind 0.0.0.0 --directory "${DIR}"
