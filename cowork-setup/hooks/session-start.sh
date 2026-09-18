#!/usr/bin/env bash
# SessionStart do cowork-setup: painel de abertura da bancada. Silencioso se a pasta não é uma COWORK-OS organizada.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; S="$HERE/../scripts"; PY="bash $HERE/python.sh"
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"; cd "$ROOT" 2>/dev/null || exit 0
if [ ! -f "_sistema/versao" ]; then
  if [ -d "CLIENTES" ] || [ -f "PERSONA.md" ] || [ -d "BASE DE CONHECIMENTO" ] || [ -d "clientes" ]; then
    echo "=== COWORK-OS · esta pasta ainda não está organizada no método. Rode /cowork-setup (não move nada sem você aprovar). ==="
  fi
  exit 0
fi
date +%s > _sistema/.sessao
echo "=== COWORK-OS · $(date +%Y-%m-%d) · organização v$(cat _sistema/versao) ==="
echo "Leia identidade/ (00 → 06) antes de qualquer tarefa. Demanda de cliente entra por /zeus. Pasta nova só por /novo-cliente e /novo-projeto."
V="$(cat "$S/../espec/VERSAO" 2>/dev/null)"; [ -n "$V" ] && [ "$V" != "$(cat _sistema/versao)" ] && echo "! Plugin v$V > organização v$(cat _sistema/versao): rode /cowork-setup → atualizar."
echo
echo "--- TASKS.md (Ativas / Aguardando) ---"
awk '/^## Ativas/{f=1} /^## Um dia/{f=0} f' TASKS.md 2>/dev/null | grep -v "^$" | head -15
echo
echo "--- Projetos com próximo passo (10 mais recentes) ---"
$PY "$S/painel.py" --n 10 2>/dev/null
echo
echo "--- estrutura ---"
$PY "$S/lint.py" --resumo 2>/dev/null | sed 's/^/  /'
exit 0
