#!/usr/bin/env bash
# Descobre o Python do computador (python3 no macOS/Linux; python ou py -3 no Windows) e repassa os argumentos + stdin.
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info[0]==3 else 1)' 2>/dev/null && exec "$c" "$@"; done
command -v py >/dev/null 2>&1 && exec py -3 "$@"
echo "cowork-setup: Python 3 não encontrado (macOS: python3 · Windows: instale em python.org marcando 'Add python.exe to PATH')" >&2; exit 0
