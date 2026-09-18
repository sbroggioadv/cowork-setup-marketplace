---
name: comecar
description: Abre a sessão na bancada COWORK-OS — lê identidade/ e TASKS.md, imprime o painel dos casos com próximo passo e o estado da estrutura. Use quando o advogado disser /comecar, "bom dia", "o que temos hoje", "onde paramos", ou no início de qualquer sessão em que o painel automático não apareceu.
---

# /comecar — abertura da sessão

1. Rode o painel: `bash "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"` (é o mesmo do hook; grava o carimbo da sessão em `_sistema/.sessao`, que o `/encerrar` usa).
2. Leia `identidade/00-PERFIL-MESTRE.md` → `06-MEMORIA.md` e `TASKS.md`. Não anuncie que leu; fique informado.
3. Diga ao advogado, em 6 linhas: pendências ativas · 3 casos mais recentes com o próximo passo · avisos de estrutura (se houver) · "por onde começamos?".
4. Se a pasta ainda não está organizada (`_sistema/versao` não existe), diga só: "Esta pasta ainda não está no método — rode `/cowork-setup`."
