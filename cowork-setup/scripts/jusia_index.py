#!/usr/bin/env python3
"""Índices das bases de citação de knowledge/, cada uma com o nível de citação:
  knowledge/jurisprudencia/jusia/INDEX.md   pesquisas pelo Jus IA (juris_search), schema jusia-bank-v1 — nível 2 até validar
  knowledge/jurisprudencia/INDEX.md         geral: jusia + proprias + súmulas embarcadas no plugin
  knowledge/doutrina/INDEX.md               jusia (doutrina_search, schema jusia-doutrina-v1) + proprias (livros/artigos do escritório)
  knowledge/legislacao/INDEX.md             normas por tema (vigentes e nao-vigente/)
Uso: python3 jusia_index.py [--raiz X]
Só lê e escreve os INDEX.md — nunca move nem apaga pesquisa."""
from __future__ import annotations
import argparse, json, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

DOCS = (".md", ".pdf", ".docx", ".doc", ".odt", ".txt", ".html")

def buscas(bank: Path, schema: str) -> list[dict]:
    out = []
    for js in sorted(bank.glob("*/*/busca-*.json")):
        d = ler_json(js, {}) or {}
        if d.get("schema_version") != schema: continue
        d["_rel"] = js.relative_to(bank).as_posix(); out.append(d)
    return out

def ultimas(bs: list[dict]) -> dict:
    last = {}
    for d in bs:
        k = (d.get("departamento", "?"), d.get("tema", "?"))
        if k not in last or d.get("executado_em", "") > last[k].get("executado_em", ""): last[k] = d
    return last

def index_jusia(bank: Path, schema: str, titulo: str, nota: str) -> tuple[int, int]:
    bs = buscas(bank, schema); last = ultimas(bs); por = defaultdict(list)
    for (dep, _), d in sorted(last.items()): por[dep].append(d)
    itens = sum(d.get("total", len(d.get("itens", []))) for d in last.values())
    L = [f"# {titulo} — índice", "", f"Gerado em {hoje()} · {itens} item(ns) · {len(last)} tema(s) · {len(bs)} busca(s)", "", f"> {nota}", "",
         "| área | temas | itens |", "|---|---:|---:|"]
    L += [f"| {dep} | {len(ds)} | {sum(d.get('total', len(d.get('itens', []))) for d in ds)} |" for dep, ds in sorted(por.items())]
    for dep, ds in sorted(por.items()):
        L += ["", f"## {dep}", "", "| tema | situação de uso | itens | arquivo |", "|---|---|---:|---|"]
        for d in ds:
            md = d["_rel"].replace(".json", ".md")
            L.append(f"| **{d.get('tema','?')}** | {d.get('situacao','')} | {d.get('total', len(d.get('itens', [])))} | [{Path(md).name}]({md}) |")
    bank.mkdir(parents=True, exist_ok=True); (bank / "INDEX.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return itens, len(last)

def arquivos_de(d: Path) -> list[Path]:
    return [f for f in sorted(d.rglob("*")) if f.is_file() and f.suffix.lower() in DOCS and f.name not in ("README.md", "INDEX.md")] if d.exists() else []

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--raiz"); a = ap.parse_args(); root = raiz(a.raiz); K = root / "knowledge"
    if not K.exists(): print("sem knowledge/ — nada a indexar"); return 0
    # jurisprudência
    J = K / "jurisprudencia"; ji, jt = index_jusia(J / "jusia", "jusia-bank-v1", "Jurisprudência — Jus IA",
        "descoberta via Jus IA (`juris_search`): ementa da base, **não conferida no portal do tribunal** — nível 2 (`[VALIDAR]`) até validação na fonte oficial.")
    prop = arquivos_de(J / "proprias"); vend = VENDOR / "sumulas"; ns = len(list(vend.glob("INDEX-*.md"))) if vend.exists() else 0
    G = [f"# knowledge/jurisprudencia/ — índice geral · {hoje()}", "", "| Banco | O que é | Itens | Nível de citação | Índice |", "|---|---|---|---|---|",
         f"| `jusia/` | pesquisas pelo Jus IA, por área e situação de uso | {ji} em {jt} tema(s) | 2 — `[VALIDAR]` na fonte antes de citar | [jusia/INDEX.md](jusia/INDEX.md) |",
         f"| `proprias/` | sentenças e acórdãos dos casos do escritório | {len(prop)} arquivo(s) | 1 — é dos autos | lista abaixo |",
         f"| súmulas | STF · STJ · TST · TJSP · TRT-15 · CJF · FONAJE, embarcadas no plugin (`/jurisprudencia sumulas`) | {ns} índice(s) | 1 — conferir vigência | `sumulas/README.md` |",
         "", "Regra: nível 1 validado · nível 2 `[VALIDAR]` · nível 3 não localizado — declarar. Peça com citação sem nível volta (Thor C1).", ""]
    if prop: G += ["## proprias/", ""] + [f"- `{f.relative_to(J / 'proprias').as_posix()}`" for f in prop] + [""]
    J.mkdir(parents=True, exist_ok=True); (J / "INDEX.md").write_text("\n".join(G), encoding="utf-8")
    # doutrina
    D = K / "doutrina"; di, dt = index_jusia(D / "jusia", "jusia-doutrina-v1", "Doutrina — Jus IA",
        "descoberta via Jus IA (`doutrina_search`) — nível 2: conferir autor, obra, edição e página antes de citar.")
    dp = arquivos_de(D / "proprias")
    DL = [f"# knowledge/doutrina/ — índice · {hoje()}", "", "| Banco | Itens | Nível |", "|---|---|---|",
          f"| `jusia/` | {di} em {dt} tema(s) — [jusia/INDEX.md](jusia/INDEX.md) | 2 — conferir na obra |",
          f"| `proprias/` | {len(dp)} arquivo(s) | 1 — com página conferida |", ""]
    if dp: DL += ["## proprias/", ""] + [f"- `{f.relative_to(D / 'proprias').as_posix()}`" for f in dp] + [""]
    D.mkdir(parents=True, exist_ok=True); (D / "INDEX.md").write_text("\n".join(DL), encoding="utf-8")
    # legislação
    Lg = K / "legislacao"; lf = arquivos_de(Lg); por = defaultdict(list)
    for f in lf:
        r = f.relative_to(Lg).parts; por[r[0] if len(r) > 1 else "(solto)"].append(f)
    LL = [f"# knowledge/legislacao/ — índice · {hoje()}", "", "Cada arquivo diz de onde veio e em que data foi conferido. `nao-vigente/` = revogada (só para fato gerador antigo).", "",
          "| Tema | Arquivos | Não vigentes |", "|---|---:|---:|"]
    LL += [f"| `{t}` | {len(fs)} | {sum(1 for f in fs if 'nao-vigente' in f.parts)} |" for t, fs in sorted(por.items())]
    for t, fs in sorted(por.items()):
        LL += ["", f"## {t}", ""] + [f"- `{f.relative_to(Lg).as_posix()}`" for f in fs]
    Lg.mkdir(parents=True, exist_ok=True); (Lg / "INDEX.md").write_text("\n".join(LL) + "\n", encoding="utf-8")
    print(f"jurisprudência: jusia {ji} item(ns)/{jt} tema(s) · próprias {len(prop)} · doutrina: jusia {di}/{dt} · próprias {len(dp)} · legislação: {len(lf)} arquivo(s)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
