---
name: lint-estrutura
description: "Verifica e corrige a organização da bancada COWORK-OS contra a espec do plugin (STATE.md · FICHA.md · entrada/ · pesquisas/ · historico/ · nomes em slug · sem _versoes · entregável só em pasta de projeto · caminho absoluto zero · dado de cliente fora dos motores). Use quando o advogado disser $lint-estrutura, \"confere a organização\", \"tem algo fora do lugar?\", \"a estrutura está certa?\", ou quando o painel de abertura mostrar \"estrutura: N erro(s)\"."
metadata:
  short-description: "Verifica e corrige a organização da bancada COWORK-OS contra a espec do plugin (STATE.md · FICHA.md · entrada/ · pesq…"
---

> **Codex.** Versão para o Codex da skill `lint-estrutura` do plugin `cowork-setup` v1.1.4 — gerada do mesmo texto da versão do Claude (não editar).
> - **`<plugin>`** = a pasta do plugin: `../../..` a partir da pasta deste SKILL.md (a que tem `scripts/`, `espec/` e `templates/`). Use o caminho absoluto dela nos comandos abaixo e rode-os **a partir da raiz da pasta COWORK-OS**.
> - Comandos da bancada no Codex começam com `$` (`$zeus` · nome completo `$cowork-setup:zeus`); skill de outro plugin: `$<plugin>:<skill>`. Textos da bancada (CLAUDE.md = AGENTS.md, identidade/) escrevem `/x`: leia como `$x`.
> - "Agente `X`" = o subagente `X` desta bancada (`.codex/agents/X.toml`). Ao chamá-lo, passe no pedido o caminho absoluto de `<plugin>` — ele não o recebe sozinho. Sem `.codex/agents/` na pasta (ou o setup avisou que não conseguiu gravá-la — o sandbox do Codex protege `.codex/`): rode `python3 "<plugin>/scripts/aplicar.py" --agentes-codex` **pedindo execução fora do sandbox** (o Codex mostra o pedido ao advogado; explique em uma linha que é só para gravar os 5 agentes da bancada) e depois abra uma sessão nova; a pasta precisa estar marcada como confiável no Codex para ele ler os agentes.

# $lint-estrutura — a organização como regra em código

O verificador é `<plugin>/scripts/lint.py` (determinístico; lê `espec/estrutura.json`). Esta skill é a porta humana; o hook SessionStart imprime o resumo e o hook Stop barra o encerramento se um cliente tocado ficou com **erro**.

1. `python3 "<plugin>/scripts/lint.py"` (ou `--cliente <slug>`). Leia cada `E`/`A` e o código.
2. **Corrija sozinho o que só adiciona:** `--corrigir` cria `FICHA.md`, `entrada/`, `pesquisas/`; também é seu: `.DS_Store`, nome de pesquisa fora de `AAAA-MM-DD-tema.md` (renomear), projeto ausente do índice do cliente (acrescentar a linha), `NOME` (renomear pasta para slug — avise o que renomeou).
3. **Corrija com o advogado o que move ou apaga conteúdo:** `VERS` (mover para `historico/`), `LUGAR` (mover entregável/arquivo para a pasta certa), `LEGADO`/`AVULSO` (absorver `_memoria-cowork.md`/`memory.md` em Decisões fixadas ou FICHA e apagar), `CASOS` (dado de cliente em `<plugin>/casos/` → mover para o projeto), `TRIAGEM` (o que está em `_legado/triagem/` esperando decisão).
4. **Novos (1.1):** `KNOW` (knowledge/ fora da organização, modelos em `_novos/` ou em `geral/`) → `$modelos organizar` ou `$cowork-setup` → atualizar · `NOME`/`NUM` dentro de knowledge/ → `$modelos organizar` renomeia · `CORTE` (relatório com nome errado) → renomear para `CORTE-R1-R4-AAAA-MM-DD.md` · `GATE` (entregável sem `Thor: ok`) → passou por `$zeus`? · `SEGREDO` (token/senha num arquivo) → apague a linha e peça ao advogado para trocar a chave · `MOTOR` (pasta de plugin fora da raiz) → devolva para a raiz (o plugin só a acha lá).
5. `CRU` não se corrige aqui: caso que ainda não foi tocado — vira lista para o advogado dizer o que está vivo. `BLOAT`: reduza Gates à última rodada.
6. Toda correção em `clientes/<x>/` ganha 1 linha no Histórico do STATE (projeto ou cliente). Rode de novo até `estrutura: limpa` ou só avisos que o advogado aceitou.

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
