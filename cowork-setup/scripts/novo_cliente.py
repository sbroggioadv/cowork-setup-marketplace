#!/usr/bin/env python3
"""Cria clientes/<slug>/ com STATE.md (índice) e cadastro/CADASTRO.md + cadastro/documentos/ a partir dos templates da bancada.
Uso: python3 novo_cliente.py "Nome do Cliente" [--raiz X]"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

ap = argparse.ArgumentParser(); ap.add_argument("nome"); ap.add_argument("--raiz")
a = ap.parse_args(); root = raiz(a.raiz); s = slug(a.nome); base = root / "clientes" / s
if (base / "STATE.md").exists(): print(f"Já existe: clientes/{s}/STATE.md — nada criado."); sys.exit(0)
(base / "cadastro" / "documentos").mkdir(parents=True, exist_ok=True)
st = template_bancada(root, "STATE-cliente.template.md").replace("<Cliente>", a.nome).replace("AAAA-MM-DD", hoje())
st = "\n".join(l for l in st.splitlines() if not l.startswith("| `contencioso/<area>/")) + "\n"
(base / "STATE.md").write_text(st, encoding="utf-8")
cad = base / "cadastro" / "CADASTRO.md"
if not cad.exists(): cad.write_text(template_bancada(root, "CADASTRO.template.md").replace("<Cliente>", a.nome).replace("AAAA-MM-DD", hoje()), encoding="utf-8")
print(f"Criado: clientes/{s}/  (STATE.md + cadastro/CADASTRO.md + cadastro/documentos/)")
