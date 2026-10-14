---
name: comecar
description: "Abre a sessão na bancada COWORK-OS — lê identidade/ e TASKS.md, imprime o painel dos casos com próximo passo e o estado da estrutura. Use quando o advogado disser $comecar, \"bom dia\", \"o que temos hoje\", \"onde paramos\", ou no início de qualquer sessão em que o painel automático não apareceu."
metadata:
  short-description: "Abre a sessão na bancada COWORK-OS"
---

> **Codex.** Versão para o Codex da skill `comecar` do plugin `cowork-setup` v1.1.4 — gerada do mesmo texto da versão do Claude (não editar).
> - **`<plugin>`** = a pasta do plugin: `../../..` a partir da pasta deste SKILL.md (a que tem `scripts/`, `espec/` e `templates/`). Use o caminho absoluto dela nos comandos abaixo e rode-os **a partir da raiz da pasta COWORK-OS**.
> - Comandos da bancada no Codex começam com `$` (`$zeus` · nome completo `$cowork-setup:zeus`); skill de outro plugin: `$<plugin>:<skill>`. Textos da bancada (CLAUDE.md = AGENTS.md, identidade/) escrevem `/x`: leia como `$x`.
> - "Agente `X`" = o subagente `X` desta bancada (`.codex/agents/X.toml`). Ao chamá-lo, passe no pedido o caminho absoluto de `<plugin>` — ele não o recebe sozinho. Sem `.codex/agents/` na pasta (ou o setup avisou que não conseguiu gravá-la — o sandbox do Codex protege `.codex/`): rode `python3 "<plugin>/scripts/aplicar.py" --agentes-codex` **pedindo execução fora do sandbox** (o Codex mostra o pedido ao advogado; explique em uma linha que é só para gravar os 5 agentes da bancada) e depois abra uma sessão nova; a pasta precisa estar marcada como confiável no Codex para ele ler os agentes.

# $comecar — abertura da sessão

1. Rode o painel: `python3 "<plugin>/hooks/session-start.py"` (é o mesmo do hook; grava o carimbo da sessão em `_sistema/.sessao`, que o `$encerrar` usa, e organiza o que estiver em `knowledge/modelos/_novos/`).
2. Leia `identidade/00-PERFIL-MESTRE.md` → `06-MEMORIA.md` e `TASKS.md`. Não anuncie que leu; fique informado.
3. Diga ao advogado, em 6 linhas: pendências ativas · 3 casos mais recentes com o próximo passo · modelos organizados agora (se houve) · avisos de estrutura (se houver) · "por onde começamos?".
4. Se a pasta ainda não está organizada (`_sistema/versao` não existe), diga só: "Esta pasta ainda não está no método — rode `$cowork-setup`."

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
