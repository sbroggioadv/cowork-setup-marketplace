---
name: jurisprudencia
description: Bases de citação da bancada, sempre com nível — jurisprudência (pesquisa no Jus IA por área e situação de uso, decisões próprias dos casos), súmulas e precedentes qualificados embarcados no plugin, doutrina (autor, obra, página) e legislação por tema. Use quando o advogado disser /jurisprudencia, "pesquisa jurisprudência sobre X", "tem súmula sobre", "monta meu banco", "guarda essa sentença", "doutrina sobre", "guarda essa lei".
---

# /jurisprudencia <carga | buscar "<tema>" [area] | sumulas "<termos>" | propria <arquivo> <area> | doutrina "<tema>" [area] | legislacao <arquivo> <tema> | indexar>

**Níveis de citação (valem para tudo):** 1 validado na fonte oficial · 2 indicativo, `[VALIDAR]` antes de citar · 3 não localizado — declarar. Peça com citação sem nível volta (Thor C1).

## Onde vive
- `knowledge/jurisprudencia/jusia/<area>/<tema>/busca-AAAAMMDD-HHMMSS.json` + `.md` — pesquisas pelo Jus IA. Schema `jusia-bank-v1`: `schema_version, fonte, citavel:false, departamento, tema, situacao, query, tribunais, decision_date_min, executado_em, total, itens[{tribunal, numero, tipo, relator, orgao, julgamento, publicacao, ementa, url_oficial}]`. **Nível 2.**
- `knowledge/jurisprudencia/proprias/<area>/` — sentenças e acórdãos dos casos do escritório (cópia + `.md`: processo, órgão, data, o que decidiu, o que ensinou). Nível 1.
- **Súmulas e precedentes qualificados** (STF súmulas, vinculantes e repercussão geral · STJ súmulas, repetitivos e IAC · TST · TJSP · TRT-15 · CJF · FONAJE — ~8.000 verbetes, retrato datado) **vivem no plugin** e são lidos sob demanda, sem copiar nada:
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sumulas.py" buscar <termos> [--tribunal STF|SV|STF-RG|STJ|STJ-TEMAS|TST|TJSP|TRT15|CJF|FONAJE] [--n 10]` · `ver "<id>"` (`"STJ 479"`, `"SV 10"`, `"STF Tema 796"`) · `status`. Nível 1 — **conferir vigência na fonte oficial antes de citar**.
- `knowledge/doutrina/jusia/<area>/<tema>/busca-*.json` + `.md` (schema `jusia-doutrina-v1`: mesmos campos, com `itens[{autor, obra, edicao, ano, pagina, trecho, url}]`) — nível 2 até conferir na obra · `knowledge/doutrina/proprias/<area>/` — trecho de livro/artigo do escritório com autor · obra · edição · ano · página (nível 1).
- `knowledge/legislacao/<tema>/` — texto da norma copiado da fonte oficial, com **de onde veio e em que data** no topo; revogada em `nao-vigente/`. Vale a norma do ano do fato gerador.

## Jus IA (conector)
As ferramentas aparecem como `mcp__<id>__juris_search`, `doutrina_search`, `legislacao_search`. **Ache-as por busca de ferramenta ("juris_search"), nunca por nome fixo.** Sem o conector: "conecte o Jus IA em Configurações → Conectores" e ofereça registrar a pesquisa manual em `pesquisas/` do caso. Sem Jus IA a bancada funciona: súmulas, decisões próprias, doutrina e legislação que o escritório guardar continuam valendo.

## Rotinas
- **carga** — pergunte as áreas (as de `_sistema/areas.json`) e, para cada uma, 3 a 6 *situações de uso* ("prescrição em cobrança", "dano moral por negativação"). Para cada situação: `juris_search` (4 por chamada; varie os termos até ~10 itens úteis), grave `busca-*.json` + `.md` (ementa completa + link oficial + `[VALIDAR]`). Ao fim, `indexar`.
- **buscar "<tema>" [area]** — primeiro `sumulas.py buscar` (verbete encontrado entra primeiro, com `ver "<id>"` para o enunciado exato); depois o Jus IA; grave e indexe. Se for para um caso, também `<projeto>/pesquisas/AAAA-MM-DD-tema.md` com o nível de cada citação.
- **propria <arquivo> <area>** — copie a decisão para `proprias/<area>/` com nome em minúsculas, crie o `.md` (processo, órgão, data, decidiu, ensinou; sem dado de terceiro além do necessário) e indexe.
- **doutrina "<tema>" [area]** — `doutrina_search` no Jus IA → grave em `doutrina/jusia/…` (nível 2) — ou registre trecho de obra do escritório em `doutrina/proprias/<area>/` com a página.
- **legislacao <arquivo ou link oficial> <tema>** — guarde o texto em `legislacao/<tema>/` com a fonte e a data no topo; norma revogada → `nao-vigente/`.
- **indexar** — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/jusia_index.py"` (índices de jurisprudência, doutrina e legislação).

## Regras
Nunca citar item de banco como certo sem nível; o chefe usa nível 2 como `[VALIDAR]`. Validação na fonte oficial → skill de validação do `juris-adv-os`, se instalado; senão, conferência manual registrada em `pesquisas/`. Nomes de arquivo e pasta sempre em minúsculas, hífen, sem acento.

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
