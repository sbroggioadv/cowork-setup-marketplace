#!/usr/bin/env python3
"""Painel dos STATE.md: projetos com 'Próximo passo', os mais recentes primeiro (usado pelo hook SessionStart e pelo /comecar).
Uso: python3 painel.py [--n 10] [--tipo contencioso|consultivo|holding] [--cliente slug] [--raiz X]"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=10); ap.add_argument("--tipo"); ap.add_argument("--cliente"); ap.add_argument("--raiz")
a = ap.parse_args(); root = raiz(a.raiz); base = root / "clientes"
itens = []
for st in base.glob("*/**/STATE.md"):
    relp = st.relative_to(base); partes = relp.parts; nome = partes[0]
    tipo = partes[1] if len(partes) > 2 else "(índice do cliente)"
    if a.cliente and nome != a.cliente: continue
    if a.tipo and tipo != a.tipo: continue
    itens.append((st.stat().st_mtime, "clientes/" + str(relp.parent), tipo, proximo_passo(st)))
itens.sort(reverse=True)
if not itens: print("Nenhum STATE.md em clientes/ ainda — comece por /novo-cliente ou /zeus."); sys.exit(0)
for _, caminho, tipo, prox in itens[:a.n]:
    print(f"- {caminho}  [{tipo}]\n    → {prox}")
