# Bancada (v0.3)

Painel lateral do Claude Code para bancadas jurídicas organizadas no método Code-OS / cowork-setup.
Mostra o caso desta conversa (o projeto cujo STATE.md ou FICHA.md a conversa leu ou editou por último):
trilha Brief → Redação → Corte → Thor → Entrega, há quanto tempo o pedido está em curso e os últimos
eventos, próximo passo, fatos e provas da FICHA, prazo, próximo compromisso da Agenda do caso, ações que
apenas escrevem o pedido na caixa de mensagem (com Adversário e Juiz pelo método do prisma-julgador-os)
e o quadro vermelho de pendências do TASKS.md.

O que ele grava: `.bancada/pedidos.jsonl` na raiz da pasta (o registro de pedidos) e, quando você marca
o ☐ de uma pendência, a mudança dela para "## Feito" no TASKS.md, com Desfazer. Nada mais.
Comando: `/bancada [clientes/<cliente>/<tipo>/<area>/<projeto>]`.
