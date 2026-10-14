#!/usr/bin/env python3
"""F0 — Censo: inventário da pasta COWORK-OS. Não move nada. Grava _sistema/censo.json e imprime o resumo.
Uso: python3 censo.py [--raiz <pasta>] [--json]
Reconhece: o formato antigo (prompt de setup: CLAUDE/MEMORY/PERSONA na raiz, BASE DE CONHECIMENTO, CLIENTES/<x>/CONSULTIVO|CONTENCIOSO
com STATE/memory por caso), os motores dos plugins (/start-*) e o formato novo (clientes/, identidade/, _sistema/)."""
import argparse, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

IGNORAR = {".DS_Store", ".git", ".claude", "__pycache__", ".Trash", "desktop.ini", "Icon\r"}

def norm(s: str) -> str: return slug(s)

def mapa_legado(esp: dict, chave: str) -> dict:
    return {norm(k): v for k, v in esp["legado_antigo"][chave].items()}

def classificar_projeto(d: Path, esp: dict) -> dict:
    """Uma pasta de caso: STATE/memory + subpastas conhecidas + arquivos soltos."""
    pa = esp["legado_antigo"]["projeto_arquivos"]; pp = mapa_legado(esp, "projeto_pastas")
    info = {"pasta": d.name, "slug": norm(d.name), "state": None, "memory": None, "claude": None,
            "subpastas": [], "arquivos_soltos": 0, "arquivos_total": contar_arquivos(d)}
    for f in sorted(d.iterdir()):
        if f.name in IGNORAR: continue
        if f.is_file():
            dest = pa.get(f.name)
            if dest == "STATE.md": info["state"] = f.name
            elif dest == "_memoria-cowork.md": info["memory"] = f.name
            elif dest == "_claude-cowork.md": info["claude"] = f.name
            else: info["arquivos_soltos"] += 1
        else:
            info["subpastas"].append({"nome": f.name, "destino": pp.get(norm(f.name)), "arquivos": contar_arquivos(f)})
    return info

def eh_projeto(d: Path, esp: dict) -> bool:
    pa = esp["legado_antigo"]["projeto_arquivos"]; pp = mapa_legado(esp, "projeto_pastas")
    nomes = [f.name for f in d.iterdir() if f.name not in IGNORAR]
    if any(pa.get(n) == "STATE.md" for n in nomes): return True
    if any(norm(n) in pp for n in nomes if (d / n).is_dir()): return True
    subdirs = [d / n for n in nomes if (d / n).is_dir()]
    if not subdirs and any((d / n).is_file() for n in nomes): return True   # só arquivos = caso simples
    return False

def censo_cliente_legado(cli: Path, esp: dict, root: Path) -> dict:
    cp = mapa_legado(esp, "cliente_pastas")
    c = {"pasta": cli.name, "nome": cli.name, "slug": norm(cli.name), "arquivos_soltos": [], "tipos": [], "outros": [],
         "state": None, "memory": None, "arquivos_total": contar_arquivos(cli)}
    pa = esp["legado_antigo"]["projeto_arquivos"]
    for f in sorted(cli.iterdir()):
        if f.name in IGNORAR: continue
        if f.is_file():
            dest = pa.get(f.name)
            if dest == "STATE.md": c["state"] = f.name
            elif dest == "_memoria-cowork.md": c["memory"] = f.name
            else: c["arquivos_soltos"].append(f.name)
            continue
        tipo = cp.get(norm(f.name))
        if tipo is None:
            c["outros"].append({"pasta": f.name, "arquivos": contar_arquivos(f), "parece_projeto": eh_projeto(f, esp)})
            continue
        t = {"pasta": f.name, "tipo": tipo, "projetos": [], "arquivos_soltos": 0}
        if tipo == "holding":
            t["projetos"].append({"pasta": ".", "slug": ".", "area": "holding", "area_nome": "holding", "area_conhecida": True,
                                  "detalhe": classificar_projeto(f, esp)})
            c["tipos"].append(t); continue
        for g in sorted(f.iterdir()):
            if g.name in IGNORAR: continue
            if g.is_file(): t["arquivos_soltos"] += 1; continue
            area = area_por_nome(g.name, root)
            if eh_projeto(g, esp):
                # a própria pasta é o caso (ex.: CONTENCIOSO/Cível/STATE.md) — área = nome da pasta se conhecida, senão perguntar
                t["projetos"].append({"pasta": g.name, "slug": norm(g.name), "area": area, "area_nome": g.name if area else None,
                                      "area_conhecida": area is not None, "nivel": 1, "detalhe": classificar_projeto(g, esp)})
            else:
                # pasta de área com casos dentro (ex.: CONTENCIOSO/Cível/Banco X 0001/STATE.md)
                for h in sorted(g.iterdir()):
                    if h.name in IGNORAR or not h.is_dir(): continue
                    t["projetos"].append({"pasta": f"{g.name}/{h.name}", "slug": norm(h.name), "area": area, "area_nome": g.name,
                                          "area_conhecida": area is not None, "nivel": 2, "detalhe": classificar_projeto(h, esp)})
                soltos = [h for h in g.iterdir() if h.is_file() and h.name not in IGNORAR]
                if soltos: t["arquivos_soltos"] += len(soltos)
        c["tipos"].append(t)
    return c

def censo_materia(d: Path, root: Path, esp: dict) -> dict:
    """Consultivo/ · Contencioso/ · Holding/ na raiz: cada subpasta é um caso ou um cliente (o advogado diz qual e para onde).
    Pasta intermediária (Holding/Projetos-ativos/…) é atravessada; arquivo solto em qualquer nível vai para a triagem."""
    inter = {norm(x) for x in esp["legado_antigo"].get("materia_intermediarias", [])}
    itens, soltos = [], []
    def varre(p: Path):
        for g in sorted(p.iterdir()):
            if g.name in IGNORAR or g.name.startswith("."): continue
            if g.is_file(): soltos.append(rel(root, g)); continue
            if norm(g.name) in inter and any(h.is_dir() for h in g.iterdir()): varre(g); continue
            itens.append({"caminho": rel(root, g), "nome": g.name, "slug": norm(g.name), "arquivos": contar_arquivos(g),
                          "area": area_por_nome(g.name, root), "tem_state": any((g / n).exists() for n in ("STATE.md", "CASO.md", "caso.md"))})
    varre(d)
    return {"itens": itens, "soltos": soltos, "arquivos": contar_arquivos(d)}

def censo_motor(d: Path) -> dict:
    m = {"nome": d.name, "persona": (d / "persona.md").exists() or (d / "perfil.md").exists(),
         "state": (d / "cowork-state.json").exists(), "casos": []}
    casos = d / "casos"
    if casos.is_dir():
        for c in sorted(casos.iterdir()):
            if c.is_dir() and c.name not in IGNORAR:
                m["casos"].append({"pasta": c.name, "slug": norm(c.name), "arquivos": contar_arquivos(c),
                                   "tem_caso_md": any((c / n).exists() for n in ("CASO.md", "caso.md", "STATE.md"))})
    return m

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raiz"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args(); root = raiz(a.raiz); esp = espec()
    ra = {norm(k): k for k in esp["legado_antigo"]["raiz_arquivos"]}
    rp = mapa_legado(esp, "raiz_pastas")
    out = {"data": agora(), "raiz": root.name, "versao_plugin": versao_plugin(),
           "versao_instalada": ler(root / "_sistema" / "versao").strip() or None,
           "arquivos_total": contar_arquivos(root), "raiz_itens": [], "motores": [], "clientes_legado": [], "clientes_novo": [],
           "identidade_legado": {}, "knowledge_legado": None, "desconhecidos": [], "materia_legado": [], "avisos": []}
    for f in sorted(root.iterdir()):
        if f.name in IGNORAR or f.name.startswith("."): continue
        item = {"nome": f.name, "tipo": "arquivo" if f.is_file() else "pasta"}
        if f.is_file():
            if norm(f.name) in ra:
                item["classe"] = "legado-arquivo"; out["identidade_legado"][f.name] = True
            elif f.name in esp["raiz"]["arquivos"]:
                item["classe"] = "novo-formato"
            else:
                item["classe"] = "desconhecido"; out["desconhecidos"].append(f.name)
        else:
            if f.name in esp["raiz"]["pastas"] or f.name in esp["raiz"]["opcionais"]:
                item["classe"] = "novo-formato"
                if f.name == "clientes":
                    for c in sorted(f.iterdir()):
                        if c.is_dir() and c.name not in IGNORAR:
                            out["clientes_novo"].append({"slug": c.name, "state": (c / "STATE.md").exists(),
                                                         "cadastro": (c / "cadastro" / "CADASTRO.md").exists()})
            elif norm(f.name) in rp:
                item["classe"] = "legado-pasta"; item["destino"] = rp[norm(f.name)]
                if rp[norm(f.name)] == "clientes":
                    for c in sorted(f.iterdir()):
                        if c.is_dir() and c.name not in IGNORAR:
                            out["clientes_legado"].append(censo_cliente_legado(c, esp, root))
                elif rp[norm(f.name)] == "knowledge":
                    out["knowledge_legado"] = {"pasta": f.name, "arquivos": contar_arquivos(f),
                                               "subpastas": [g.name for g in sorted(f.iterdir()) if g.is_dir() and g.name not in IGNORAR],
                                               "soltos": [g.name for g in sorted(f.iterdir()) if g.is_file() and g.name not in IGNORAR]}
            elif norm(f.name) in mapa_legado(esp, "raiz_por_materia"):
                item["classe"] = "legado-materia"; item["tipo"] = mapa_legado(esp, "raiz_por_materia")[norm(f.name)]
                item.update(censo_materia(f, root, esp)); out["materia_legado"].append(f.name)
            elif norm(f.name) in {norm(x) for x in esp["legado_antigo"].get("raiz_caixa", [])}:
                item["classe"] = "legado-caixa"; item["arquivos"] = contar_arquivos(f); out["materia_legado"].append(f.name)
            elif eh_motor(f, esp):
                item["classe"] = "motor"; out["motores"].append(censo_motor(f))
            else:
                item["classe"] = "desconhecido"; item["arquivos"] = contar_arquivos(f); out["desconhecidos"].append(f.name + "/")
        out["raiz_itens"].append(item)
    out["plugins_detectados"] = [m["nome"] for m in out["motores"]]
    kn = root / "knowledge"
    if kn.is_dir():
        out["knowledge_atual"] = {"subpastas": [g.name for g in sorted(kn.iterdir()) if g.is_dir() and g.name not in IGNORAR],
                                  "soltos": [g.name for g in sorted(kn.iterdir()) if g.is_file() and g.name not in IGNORAR],
                                  "readme_antigo": (kn / "README.md").exists() and "Gerado pelo plugin" not in ler(kn / "README.md")}
    out["arquivos_lista"] = sorted([rel(root, f), f.stat().st_size, assinatura(f)] for f in root.rglob("*")
                                   if f.is_file() and f.name not in IGNORAR and "_sistema" not in f.parts and ".claude" not in f.parts and "__pycache__" not in f.parts)
    # modo
    if out["versao_instalada"]:
        out["modo"] = "organizado"
    elif out["clientes_legado"] or out["identidade_legado"] or out["knowledge_legado"] or out["desconhecidos"] or out["clientes_novo"] or out["materia_legado"]:
        out["modo"] = "migrar"
    else:
        out["modo"] = "novo"
    if out["modo"] == "migrar" and out["clientes_novo"] and not out["clientes_legado"]:
        out["avisos"].append("Há clientes/ no formato novo sem _sistema/versao — parece organização parcial; o plano completa o que falta.")
    if out["versao_instalada"] and out["versao_instalada"] != out["versao_plugin"]:
        out["avisos"].append(f"Versão instalada {out['versao_instalada']} ≠ plugin {out['versao_plugin']} — modo 'atualizar' disponível (planejar.py monta o plano; nada se move sem aprovação).")
    cfg = root / ".codex" / "config.toml"
    if cfg.exists() and re.search(r"^\s*(model_instructions_file|experimental_instructions_file)\s*=", ler(cfg), re.M):
        out["avisos"].append(".codex/config.toml desta pasta troca as instruções base do Codex por um arquivo (model_instructions_file) — depois de organizar, confira se ele ainda aponta para o que você quer (o AGENTS.md novo é a constituição da bancada).")
    for m in out["motores"]:
        nom = [c for c in m["casos"] if c["arquivos"] > 0]
        if nom: out["avisos"].append(f"Motor {m['nome']}/casos/ tem {len(nom)} caso(s) com arquivos — dado de cliente deve migrar para clientes/.")
    gravar_json(sistema(root) / "censo.json", out)
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return
    # resumo humano
    print(f"=== CENSO · {root.name} · {out['data']} ===")
    print(f"Modo detectado: {out['modo'].upper()}   (plugin {out['versao_plugin']} · instalada: {out['versao_instalada'] or '—'})")
    print(f"Arquivos na pasta: {out['arquivos_total']}")
    print(f"Raiz: " + ", ".join(f"{i['nome']}[{i['classe']}]" for i in out["raiz_itens"]) if out["raiz_itens"] else "Raiz: (vazia)")
    if out["motores"]:
        print("Motores de plugin (ficam onde estão): " + ", ".join(f"{m['nome']}({len(m['casos'])} casos)" for m in out["motores"]))
    if out["clientes_legado"]:
        print(f"Clientes no formato antigo: {len(out['clientes_legado'])}")
        for c in out["clientes_legado"]:
            projs = sum(len(t["projetos"]) for t in c["tipos"])
            sem_area = sum(1 for t in c["tipos"] for p in t["projetos"] if not p["area_conhecida"])
            print(f"  - {c['pasta']} → clientes/{c['slug']}/ · {projs} projeto(s)" + (f" · {sem_area} sem área reconhecida (vai perguntar)" if sem_area else "")
                  + (f" · {len(c['outros'])} pasta(s) fora do padrão" if c["outros"] else "") + (f" · {len(c['arquivos_soltos'])} arquivo(s) solto(s) → cadastro/documentos/" if c["arquivos_soltos"] else ""))
    if out["clientes_novo"]:
        print(f"Clientes já no formato novo: {len(out['clientes_novo'])}")
    if out["knowledge_legado"]:
        k = out["knowledge_legado"]; print(f"Base de conhecimento: {k['pasta']}/ ({k['arquivos']} arquivos) → knowledge/")
    if out["identidade_legado"]:
        print("Arquivos de identidade antigos: " + ", ".join(out["identidade_legado"]) + " → identidade/ (conteúdo preservado)")
    for i in out["raiz_itens"]:
        if i.get("classe") == "legado-materia":
            print(f"Pasta por matéria: {i['nome']}/ → {len(i['itens'])} caso(s)/cliente(s) para levar a clientes/<cliente>/{i['tipo']}/ (vai perguntar cada um)"
                  + (f" · {len(i['soltos'])} arquivo(s) solto(s) → _legado/triagem/" if i["soltos"] else ""))
        elif i.get("classe") == "legado-caixa":
            print(f"Caixa de entrada antiga: {i['nome']}/ ({i['arquivos']} arquivos) → _legado/triagem/ (você decide depois)")
    if out["desconhecidos"]:
        print("Não reconhecidos (vão perguntar): " + ", ".join(out["desconhecidos"]))
    for av in out["avisos"]: print("! " + av)
    print(f"Gravado: _sistema/censo.json")

if __name__ == "__main__":
    main()
