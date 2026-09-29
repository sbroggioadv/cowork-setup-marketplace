#!/usr/bin/env python3
"""Regra 10 sem git: antes de gravar a versão nova de um entregável, a vigente vai para historico/AAAA-MM-DD-<nome>.
Uso: python3 historico.py <caminho-do-arquivo-vigente> [--raiz X]
Se o arquivo não existe ainda, não faz nada (primeira versão). Registra 1 linha no Histórico do STATE.md do projeto."""
import argparse, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

ap = argparse.ArgumentParser(); ap.add_argument("arquivo"); ap.add_argument("--raiz")
a = ap.parse_args(); root = raiz(a.raiz); f = (root / a.arquivo) if not Path(a.arquivo).is_absolute() else Path(a.arquivo)
if not f.exists(): print(f"(primeira versão — nada a arquivar) {a.arquivo}"); sys.exit(0)
h = f.parent / "historico"; h.mkdir(exist_ok=True)
alvo = h / f"{hoje()}-{f.name}"; n = 2
while alvo.exists(): alvo = h / f"{hoje()}-v{n}-{f.name}"; n += 1
shutil.move(str(f), str(alvo))
st = f.parent / "STATE.md"
if st.exists():
    t = ler(st)
    if "## Histórico" in t:
        t = t.rstrip("\n") + f"\n{hoje()} · versão anterior de `{f.name}` arquivada em `historico/{alvo.name}`\n"; st.write_text(t, encoding="utf-8")
print(f"arquivado: {rel(root, alvo)}")
