#!/usr/bin/env python3
"""F1 — Perfil: guarda as respostas da entrevista em _sistema/perfil.json (é o que preenche os templates).
Uso:
  python3 perfil.py show                          mostra o perfil
  python3 perfil.py set CHAVE "valor"             grava um campo (texto; use \\n para quebrar linha)
  python3 perfil.py set-json '{"CHAVE": "…"}'     grava vários de uma vez
  python3 perfil.py faltam                        lista os campos que os templates usam e ainda não têm valor
  python3 perfil.py preferencias                  imprime o bloco para colar em Configurações → Preferências Pessoais
  python3 perfil.py importar-legado               pré-preenche o que dá a partir de _legado/PERSONA|CLAUDE|MEMORY-cowork.md (marca [REVISAR])
Campos de texto que a entrevista preenche: NOME OAB ESCRITORIO CIDADE_UF TRATAMENTO NOME_DOCUMENTO AREAS POLOS_VETADOS FERRAMENTAS
ATUACAO COMO_TRABALHO LOCAL_PASTA PROIBICOES PROTOCOLOS POSTURA TOM VOCABULARIO ANTI_VOZ ESTRUTURA_PECA REGRAS_ESTILO FORMATACAO
CAMADAS_EXTRAS FERRAMENTAS_DETALHE PREFERENCIAS CONTEXTO ENTREGAS COMO_TRABALHAR. Listas: PLUGINS. Objeto: MODULOS {timbrado, sumulas, holding}."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cwos import *

CALCULADOS = {"DATA", "VERSAO", "MOTORES", "AREAS_LISTA", "TABELA_ROTEAMENTO", "TABELA_APOIOS", "PLUGINS", "MEMORIA_IMPORTADA", "ORIGEM_MEMORIA",
              "TAREFAS_IMPORTADAS", "INDICE_KNOWLEDGE", "IMPORTADO_KNOWLEDGE", "ORIGEM_REGRAS", "ORIGEM_VOZ", "ORIGEM_ESCRITA", "AREAS"}

def campos_templates() -> set:
    campos = set()
    for f in TEMPLATES.rglob("*.md"):
        campos |= set(PLACEHOLDER.findall(f.read_text(encoding="utf-8")))
    return campos

def main():
    root = raiz(); pj = sistema(root) / "perfil.json"; perfil = ler_json(pj, {}) or {}
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "show":
        print(json.dumps(perfil, ensure_ascii=False, indent=2))
    elif cmd == "set":
        perfil[sys.argv[2]] = sys.argv[3].replace("\\n", "\n"); gravar_json(pj, perfil); print(f"ok {sys.argv[2]}")
    elif cmd == "set-json":
        perfil.update(json.loads(sys.argv[2])); gravar_json(pj, perfil); print("ok " + ", ".join(json.loads(sys.argv[2]).keys()))
    elif cmd == "preferencias":
        sys.path.insert(0, str(Path(__file__).resolve().parent)); from aplicar import vars_render
        print(render(template("preferencias-pessoais.md"), vars_render(root)))
    elif cmd == "faltam":
        faltam = sorted(c for c in campos_templates() - CALCULADOS if not str(perfil.get(c, "")).strip())
        print("\n".join(faltam) if faltam else "(nada falta)")
    elif cmd == "importar-legado":
        leg = root / "_legado"; novos = {}
        for arq, campos in (("PERSONA-cowork.md", ["POSTURA"]), ("CLAUDE-cowork.md", ["PROIBICOES"]), ("MEMORY-cowork.md", ["PREFERENCIAS"])):
            p = leg / arq
            if not p.exists(): p = root / arq.replace("-cowork", "")
            if p.exists():
                txt = ler(p).strip()
                for c in campos:
                    if not str(perfil.get(c, "")).strip():
                        novos[c] = f"[REVISAR — importado de {p.name}]\n" + txt
        # dados básicos por regex (nome/OAB) a partir da persona
        base = "\n".join(ler(leg / n) for n in ("PERSONA-cowork.md", "CLAUDE-cowork.md")) + ler(root / "PERSONA.md")
        m = re.search(r"OAB/?([A-Z]{2})\s*(?:nº|n\.?)?\s*([\d.]+)", base)
        if m and not perfil.get("OAB"): novos["OAB"] = f"OAB/{m.group(1)} {m.group(2)}"
        perfil.update(novos); gravar_json(pj, perfil)
        print("importados: " + (", ".join(novos) if novos else "(nada encontrado)"))
    else:
        print(__doc__); sys.exit(1)

if __name__ == "__main__":
    main()
