#!/usr/bin/env python3
"""Cria a pasta de projeto de um cliente com STATE.md (+ FICHA.md em T≥2) e registra no índice do cliente. Área nova é registrada em _sistema/areas.json.
Uso:
  python3 novo_projeto.py contencioso civel "Cliente" "Banco X 0001234-56.2026.8.26.0576"
  python3 novo_projeto.py consultivo empresarial "Cliente" "Contrato de Parceria X"
  python3 novo_projeto.py holding - "Cliente" "Holding Familiar"        (→ clientes/<x>/holding/)
Opções: --tier T0..T3 (padrão T2) · --raiz X"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

ap = argparse.ArgumentParser(); ap.add_argument("tipo", choices=areas_espec()["tipos"]); ap.add_argument("area"); ap.add_argument("cliente"); ap.add_argument("projeto")
ap.add_argument("--tier", default="T2"); ap.add_argument("--raiz")
a = ap.parse_args(); root = raiz(a.raiz); cli = root / "clientes" / slug(a.cliente)
if not (cli / "STATE.md").exists(): print(f"Cliente sem STATE.md: clientes/{slug(a.cliente)} — rode novo_cliente.py primeiro."); sys.exit(1)
if a.tipo == "holding":
    proj = cli / "holding"; area = "holding"
else:
    area = area_por_nome(a.area, root) or slug(a.area)
    if not re.match(espec()["nome"]["regex"], area): print(f"Área inválida: '{a.area}' (use slug: civel, trabalhista, familia…)"); sys.exit(1)
    proj = cli / a.tipo / area / slug(a.projeto)
if (proj / "STATE.md").exists(): print(f"Já existe: {rel(root, proj)}/STATE.md"); sys.exit(0)
proj.mkdir(parents=True, exist_ok=True)
m = re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", a.projeto)
ref = m.group(0) if m else ("(sem processo)" if a.tipo != "contencioso" else "<a preencher>")
st = (template_bancada(root, "STATE.template.md")
      .replace("<Cliente> × <Adversário | Documento | Família>", f"{a.cliente} × {a.projeto}")
      .replace("- Tipo: Contencioso | Consultivo | Holding · Área: <área> · Ref/Nº processo: <…>", f"- Tipo: {a.tipo.capitalize()} · Área: {area} · Ref/Nº processo: {ref}")
      .replace("@chefe (área <área>) · Plugin: <plugin> · Tier: T0–T3", f"@chefe (área {area}) · Plugin: ver identidade/05 · Tier: {a.tier}")
      .replace("AAAA-MM-DD", hoje()))
(proj / "STATE.md").write_text(st, encoding="utf-8")
for d in ("entrada", "pesquisas"): (proj / d).mkdir(exist_ok=True)
if a.tier in ("T2", "T3"):
    (proj / "FICHA.md").write_text(template_bancada(root, "FICHA.template.md").replace("<Cliente> × <Adversário | Documento | Família>", f"{a.cliente} × {a.projeto}"), encoding="utf-8")
if registrar_area(root, area):
    import subprocess; subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "aplicar.py"), "--roteamento", "--raiz", str(root)], capture_output=True)
idx = cli / "STATE.md"; txt = ler(idx); marca = "|---|---|---|---|---|"
linha = f"| `{rel(cli, proj)}/` | {a.tipo}/{area} | aberto | brief pendente | {hoje()} |"
if marca in txt and linha not in txt: idx.write_text(txt.replace(marca, marca + "\n" + linha, 1), encoding="utf-8")
print(f"Criado: {rel(root, proj)}/  STATE.md{' + FICHA.md' if a.tier in ('T2','T3') else ''} + entrada/ + pesquisas/  (tier {a.tier}; área '{area}' registrada; no índice do cliente)")
