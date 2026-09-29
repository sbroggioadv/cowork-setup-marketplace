#!/usr/bin/env python3
"""Camada C4 — conflito de interesses. Cruza um nome (e CNPJ/CPF, se houver) com TODOS os cadastros da bancada:
clientes/<x>/cadastro/CADASTRO.md, nomes de pasta de cliente, e adversários já registrados nos STATE.md de projeto.
Uso: python3 conflito.py "<nome ou documento>" [--raiz X] [--json]
Exit 3 = coincidência encontrada (a criação deve travar até o advogado decidir). Não julga: lista onde bateu."""
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

DOC = re.compile(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}|\d{3}\.?\d{3}\.?\d{3}-?\d{2}")

def tokens(s: str) -> set:
    stop = {"ltda", "me", "epp", "sa", "s", "a", "eireli", "de", "da", "do", "dos", "das", "e", "cia", "comercio", "servicos", "industria", "empresa", "grupo"}
    return {t for t in re.split(r"[^a-z0-9]+", norm(s)) if len(t) > 2 and t not in stop}

def so_digitos(s: str) -> str: return re.sub(r"\D", "", s)

def cruzar(root: Path, alvo: str) -> list[dict]:
    hits = []; ta = tokens(alvo); docs_alvo = {so_digitos(d) for d in DOC.findall(alvo)}
    base = root / "clientes"
    if not base.exists(): return hits
    for cli in sorted(base.iterdir()):
        if not cli.is_dir(): continue
        nome_pasta = cli.name.replace("-", " ")
        cad = ler(cli / "cadastro" / "CADASTRO.md")
        # documento
        for d in DOC.findall(cad):
            if so_digitos(d) in docs_alvo: hits.append({"onde": f"clientes/{cli.name}/cadastro/CADASTRO.md", "tipo": "documento", "papel": "cliente", "evidencia": d})
        # nome do cliente (pasta + cadastro)
        for fonte, txt in (("pasta", nome_pasta), ("cadastro", cad[:600])):
            tt = tokens(txt)
            inter = ta & tt
            if ta and len(inter) >= max(1, min(2, len(ta))):
                hits.append({"onde": f"clientes/{cli.name}", "tipo": "nome", "papel": "cliente", "evidencia": " ".join(sorted(inter))}); break
        # adversários nos STATE de projeto
        for st in cli.glob("*/*/*/STATE.md"):
            cab = ler(st)[:400]
            m = re.search(r"#\s*STATE\s*[—-]\s*(.+?)\s*[×x]\s*(.+)", cab)
            if not m: continue
            adv = m.group(2)
            inter = ta & tokens(adv)
            if ta and len(inter) >= max(1, min(2, len(ta))):
                hits.append({"onde": rel(root, st.parent), "tipo": "nome", "papel": "adversario", "evidencia": adv.strip()[:60]})
    return hits

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("alvo"); ap.add_argument("--raiz"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args(); root = raiz(a.raiz); h = cruzar(root, a.alvo)
    if a.json: print(json.dumps({"alvo": a.alvo, "coincidencias": h}, ensure_ascii=False, indent=2))
    elif h:
        print(f"CONFLITO POSSÍVEL — '{a.alvo}' coincide com {len(h)} registro(s) da bancada (o advogado decide antes de criar):")
        for x in h: print(f"  - {x['papel']:10} {x['tipo']:9} {x['onde']} — {x['evidencia']}")
    else: print(f"sem coincidência para '{a.alvo}' nos cadastros e adversários da bancada")
    sys.exit(3 if h else 0)

if __name__ == "__main__":
    main()
