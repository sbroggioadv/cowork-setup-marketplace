#!/usr/bin/env python3
"""SessionStart do cowork-setup: painel de abertura da bancada (também roda pelo /comecar). Nunca bloqueia e nunca quebra a sessão:
qualquer falha vira uma linha de aviso. Silencioso se a pasta não é uma COWORK-OS (e não tem cara de formato antigo).
Em pasta organizada: carimbo da sessão · versão · TASKS · modelos despejados em knowledge/modelos/_novos/ organizados por área ·
plugins acoplados (nenhum é obrigatório) · 10 casos com o próximo passo · resumo da estrutura."""
import os, subprocess, sys, time
from pathlib import Path
S = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(S))
from cwos import cmd, runtime, bancada_mais_nova, aviso_mais_nova, bancada_iapx, aviso_iapx   # /zeus no Claude · $zeus no Codex (a bancada é a mesma)
root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())   # o Codex não define CLAUDE_PROJECT_DIR: o hook roda na pasta da sessão

def rodar(*args) -> str:
    try: return subprocess.run([sys.executable, str(S / args[0]), *args[1:], "--raiz", str(root)], capture_output=True, text=True, timeout=90).stdout.strip()
    except Exception as e: return f"(falhou: {e})"

def main():
    if bancada_iapx(root):   # pasta do iAPX OS: nada de carimbo, plugins.json, roteamento ou modelos (ele cuida disso)
        print("=== COWORK-OS · " + aviso_iapx() + " ==="); return
    if not (root / "_sistema" / "versao").exists():
        antigo = any((root / n).exists() for n in ("CLIENTES", "PERSONA.md", "BASE DE CONHECIMENTO", "Base de Conhecimento"))
        if antigo or ((root / "clientes").is_dir() and not (root / "CLAUDE.md").exists()):
            print(f"=== COWORK-OS · esta pasta ainda não está organizada no método. Rode {cmd('cowork-setup')} (não move nada sem você aprovar). ===")
        return
    for nome in (".sessao", f".sessao-{runtime()}" if runtime() else None):   # carimbo por programa: Claude e Codex abertos ao mesmo tempo não se atropelam
        if nome:
            try: (root / "_sistema" / nome).write_text(str(int(time.time())), encoding="utf-8")
            except Exception: pass
    v = (root / "_sistema" / "versao").read_text(encoding="utf-8").strip()
    vp = (S.parent / "espec" / "VERSAO").read_text(encoding="utf-8").strip()
    print(f"=== COWORK-OS · {time.strftime('%Y-%m-%d')} · organização v{v} ===")
    print(f"Leia identidade/ (00 → 06) antes de qualquer tarefa. Demanda de cliente entra por {cmd('zeus')}. Pasta nova só por {cmd('novo-cliente')} e {cmd('novo-projeto')}.")
    if bancada_mais_nova(root): print("! " + aviso_mais_nova(v))
    elif v != vp: print(f"! Plugin v{vp} > organização v{v}: rode {cmd('cowork-setup')} → atualizar (mostra o plano antes de mexer).")
    t = root / "TASKS.md"
    if t.exists():
        linhas, dentro = [], False
        for l in t.read_text(encoding="utf-8", errors="ignore").splitlines():
            if l.startswith("## Ativas"): dentro = True
            elif l.startswith("## Um dia"): dentro = False
            if dentro and l.strip(): linhas.append(l)
        print("\n--- TASKS.md (Ativas / Aguardando) ---"); print("\n".join(linhas[:15]))
    if (root / "knowledge" / "modelos").is_dir():
        m = rodar("modelos.py", "organizar", "--resumo")
        if m: print("\n--- modelos ---\n" + m)
    p = rodar("plugins.py", "detectar")
    print("\n--- plugins ---\n" + (p.splitlines()[0] if p else "(sem leitura)") + ("" if not p or len(p.splitlines()) == 1 else f" (+{len(p.splitlines()) - 1} linha(s): {cmd('cowork-setup')} → plugins)"))
    print("\n--- Projetos com próximo passo (10 mais recentes) ---"); print(rodar("painel.py", "--n", "10"))
    print("\n--- estrutura ---"); print("  " + rodar("lint.py", "--resumo"))

if __name__ == "__main__":
    try: main()
    except Exception as e: print(f"(painel de abertura falhou: {e} — use {cmd('comecar')})")
    sys.exit(0)
