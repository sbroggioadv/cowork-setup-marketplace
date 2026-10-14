# knowledge/modelos/ — modelos canônicos do escritório

**É daqui que sai toda peça, contrato, parecer e notificação.** Antes de redigir, o chefe da área abre `modelos/<area>/INDEX.md`, escolhe o modelo pertinente, lê o modelo inteiro e redige a partir dele, na voz de `identidade/02` e `03`. O STATE do caso registra qual modelo foi usado (`Modelo-base:`); Thor confere.

## Como pôr um modelo aqui
1. **Despeje** o arquivo (ou a pasta inteira) em `modelos/_novos/`. Pode ser `.docx`, `.pdf`, `.md`, `.doc`, `.odt`, `.txt`, planilha.
2. Na próxima abertura da sessão (ou com `/modelos organizar`) o plugin **organiza sozinho**: descobre a área pelo nome e pelo conteúdo, renomeia em minúsculas (sem acento, sem espaço, sem número na frente), leva para `modelos/<area>/` e refaz o índice.
3. O que ele não souber classificar vai para `modelos/geral/` e aparece no índice como `[área?]` — diga a área (`/modelos mover <arquivo> <area>`) quando puder.
4. Tem os modelos numa pasta do computador? `/modelos importar <pasta>` copia (o original fica onde está) e organiza.

## Organização
- `modelos/<area>/` — uma pasta por área (as mesmas de `contencioso/` e `consultivo/`: `civel`, `trabalhista`, `franchising`, `societario`…), mais `honorarios/` (contratos de honorários do escritório), `procuracoes/`, `notificacoes/` (notificações e contranotificações de qualquer área) e `geral/`.
- Dentro da área, uma subpasta por tema quando o modelo veio agrupado (`franchising/teses-defesa-franquia/`).
- `modelos/<area>/INDEX.md` — arquivo · tipo · o que é · data. A coluna "o que é" começa com o título do documento; ajuste à mão quando quiser (o índice preserva o que você escrever).
- Só entra modelo **validado**. Contrato de terceiro, versão antiga e rascunho ficam no caso (`historico/`) ou em `_legado/`.
