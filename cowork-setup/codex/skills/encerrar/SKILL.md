---
name: encerrar
description: "Fecha a sessão na bancada COWORK-OS — confere que todo caso tocado teve o STATE.md atualizado (Fase atual · Próximo passo · Histórico), registra o significativo em identidade/06-MEMORIA.md ou no STATE do cliente, atualiza TASKS.md e roda o verificador de estrutura. Use quando o advogado disser $encerrar, \"por hoje é isso\", \"fecha a sessão\", \"salva tudo\", ou antes de encerrar qualquer sessão que tocou pasta de cliente."
metadata:
  short-description: "Fecha a sessão na bancada COWORK-OS"
---

> **Codex.** Versão para o Codex da skill `encerrar` do plugin `cowork-setup` v1.1.4 — gerada do mesmo texto da versão do Claude (não editar).
> - **`<plugin>`** = a pasta do plugin: `../../..` a partir da pasta deste SKILL.md (a que tem `scripts/`, `espec/` e `templates/`). Use o caminho absoluto dela nos comandos abaixo e rode-os **a partir da raiz da pasta COWORK-OS**.
> - Comandos da bancada no Codex começam com `$` (`$zeus` · nome completo `$cowork-setup:zeus`); skill de outro plugin: `$<plugin>:<skill>`. Textos da bancada (CLAUDE.md = AGENTS.md, identidade/) escrevem `/x`: leia como `$x`.
> - "Agente `X`" = o subagente `X` desta bancada (`.codex/agents/X.toml`). Ao chamá-lo, passe no pedido o caminho absoluto de `<plugin>` — ele não o recebe sozinho. Sem `.codex/agents/` na pasta (ou o setup avisou que não conseguiu gravá-la — o sandbox do Codex protege `.codex/`): rode `python3 "<plugin>/scripts/aplicar.py" --agentes-codex` **pedindo execução fora do sandbox** (o Codex mostra o pedido ao advogado; explique em uma linha que é só para gravar os 5 agentes da bancada) e depois abra uma sessão nova; a pasta precisa estar marcada como confiável no Codex para ele ler os agentes.

# $encerrar — fechamento da sessão (regra 9 sem git)

1. Descubra o que foi tocado nesta sessão: arquivos em `clientes/` modificados depois do carimbo `_sistema/.sessao` (se não houver carimbo, pergunte ao advogado quais casos foram mexidos).
2. Para cada projeto tocado, abra o `STATE.md` e garanta: **Fase atual** marcada · **Próximo passo** com 1 linha concreta (nunca vazio; se acabou: "arquivar após protocolo/assinatura") · **Histórico** com 1 linha desta sessão (data · o que foi feito · arquivo). Atualize a linha do projeto na tabela do `STATE.md` do cliente.
3. Versão nova de entregável gravada por cima da antiga? Se a antiga não foi para `historico/`, rode `python3 "<plugin>/scripts/historico.py" <arquivo>` **antes** de salvar a nova (regra 10).
4. Aconteceu algo que vale para todos os casos (preferência, decisão de organização, ferramenta nova)? Uma linha datada em `identidade/06-MEMORIA.md`. Vale só para um cliente? "Decisões fixadas" do `STATE.md` dele. Pendência que atravessa casos → `TASKS.md`.
5. `python3 "<plugin>/scripts/lint.py" --desde "$(cat _sistema/.sessao 2>/dev/null || echo 0)"` — erro (`E`) corrige agora; aviso vira nota.
6. Responda em 4 linhas: casos fechados com o próximo passo de cada · o que foi para a memória · avisos de estrutura · "até a próxima".

Python: `python3` no macOS/Linux; no Windows, `python` ou `py -3`.
