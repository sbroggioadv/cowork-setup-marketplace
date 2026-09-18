---
name: lint-estrutura
description: 'Verifica e corrige a organização da bancada COWORK-OS contra a espec do plugin (STATE.md · FICHA.md · entrada/ · pesquisas/ · historico/ · nomes em slug · sem _versoes · entregável só em pasta de projeto · caminho absoluto zero · dado de cliente fora dos motores). Use quando o advogado disser /lint-estrutura, "confere a organização", "tem algo fora do lugar?", "a estrutura está certa?", ou quando o painel de abertura mostrar "estrutura: N erro(s)".'
---

# /lint-estrutura — a organização como regra em código

O verificador é `${CLAUDE_PLUGIN_ROOT}/scripts/lint.py` (determinístico; lê `espec/estrutura.json`). Esta skill é a porta humana; o hook SessionStart imprime o resumo e o hook Stop barra o encerramento se um cliente tocado ficou com **erro**.

1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint.py"` (ou `--cliente <slug>`). Leia cada `E`/`A` e o código.
2. **Corrija sozinho o que só adiciona:** `--corrigir` cria `FICHA.md`, `entrada/`, `pesquisas/`; também é seu: `.DS_Store`, nome de pesquisa fora de `AAAA-MM-DD-tema.md` (renomear), projeto ausente do índice do cliente (acrescentar a linha), `NOME` (renomear pasta para slug — avise o que renomeou).
3. **Corrija com o advogado o que move ou apaga conteúdo:** `VERS` (mover para `historico/`), `LUGAR` (mover entregável/arquivo para a pasta certa), `LEGADO`/`AVULSO` (absorver `_memoria-cowork.md`/`memory.md` em Decisões fixadas ou FICHA e apagar), `CASOS` (dado de cliente em `<plugin>/casos/` → mover para o projeto), `TRIAGEM` (o que está em `_legado/triagem/` esperando decisão).
4. `CRU` não se corrige aqui: caso que ainda não foi tocado — vira lista para o advogado dizer o que está vivo. `BLOAT`: reduza Gates à última rodada.
5. Toda correção em `clientes/<x>/` ganha 1 linha no Histórico do STATE (projeto ou cliente). Rode de novo até `estrutura: limpa` ou só avisos que o advogado aceitou.

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
