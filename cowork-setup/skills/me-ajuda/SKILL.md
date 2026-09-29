---
name: me-ajuda
description: Socorro para qualquer dúvida sobre a bancada COWORK-OS — mecânica ("como abro um caso?", "onde ponho meu modelo?"), plugin, erro, orientação ("e agora?"). Termina sempre com o próximo comando; demanda de cliente vai para /zeus. Use quando o advogado disser /me-ajuda, "me ajuda", "como faço", "não sei", "não consigo", "deu erro", "não entendi".
---

# /me-ajuda — qualquer coisa que ele não saiba

Tom: de gente para gente, sem termo técnico sem explicação, **uma coisa por vez**. Nunca responda só "rode o comando X": diga o que ele faz e o que vai aparecer.

1. **Entenda o que ele quer** em uma pergunta, se não estiver claro. Demanda de cliente (peça, contrato, prazo, mensagem) → "isso é trabalho do caso: `/zeus <o que precisa>`" e pare.
2. **Olhe antes de responder:** `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint.py" --resumo` (estado da estrutura) e, se a dúvida for de plugin, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plugins.py" mostrar`.
3. **Responda pelo mapa:**
   | Ele quer… | Resposta |
   |---|---|
   | abrir cliente / caso | `/novo-cliente "<nome>"` → `/novo-projeto …` (ou só `/zeus`, que faz os dois) |
   | onde parou | `/comecar` (painel dos casos com o próximo passo) |
   | guardar modelo de peça/contrato | despejar em `knowledge/modelos/_novos/` ou `/modelos importar <pasta>` |
   | achar um modelo | `knowledge/modelos/<area>/INDEX.md` |
   | jurisprudência, súmula, doutrina, lei | `/jurisprudencia` |
   | plugin novo instalado / não aparece | `/cowork-setup` → plugins (nenhum plugin é obrigatório) |
   | "está bagunçado", aviso de estrutura | `/lint-estrutura` |
   | organização antiga / versão nova do plugin | `/cowork-setup` (auditar · atualizar) |
   | fechar o dia | `/encerrar` |
4. **Erro de Python** ("python3 não encontrado"): macOS já tem; Windows → instalar em python.org marcando "Add python.exe to PATH" e reabrir o app. Pasta no iCloud/Drive com arquivo "na nuvem" → "Manter baixado" na pasta.
5. **Termine sempre com o próximo comando** a rodar, em uma linha.
