---
name: modelos
description: Modelos canônicos do escritório em knowledge/modelos/<area>/ — a base de onde toda peça, contrato e parecer é redigido. Organiza sozinho o que o advogado despejar em knowledge/modelos/_novos/ (área pelo nome e pelo texto, nomes em minúsculas, índice por área), importa cópia de uma pasta do computador, corrige a área de um modelo e refaz os índices. Use quando o advogado disser /modelos, "traz meus modelos", "onde ponho meu modelo", "organiza os modelos", "indexa os modelos", "esse modelo é de outra área".
---

# /modelos [organizar | importar <pasta> | mover <arquivo> <area> | indexar]

**O que são:** as peças, contratos, pareceres, notificações e cláusulas que o advogado **validou**. O chefe lê `knowledge/modelos/<area>/INDEX.md` e o modelo antes de redigir; o STATE registra qual usou (`Modelo-base:`); Thor confere.

## Sem argumento
Pergunte, em uma linha: "Seus modelos estão numa pasta do computador (eu copio — o original fica onde está) ou você prefere arrastar para `knowledge/modelos/_novos/`?"
- **Pasta:** peça o caminho (Finder → botão direito → "Copiar como caminho"; Windows: Shift + botão direito → "Copiar como caminho"). Mostre quantos arquivos há e confirme antes de copiar. Depois: `importar`.
- **Arrastar:** diga para despejar tudo (pode ser a pasta inteira, com subpastas e nomes do jeito que estiverem) e avisar. Depois: `organizar`.

## Comandos
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/modelos.py" organizar --simular       # mostra o de→para, não move nada
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/modelos.py" organizar                 # organiza _novos/ (e o que estiver fora do lugar em modelos/) e refaz os índices
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/modelos.py" importar "<pasta>"        # COPIA .docx .pdf .md .doc .odt .txt .xlsx… para _novos/ e organiza
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/modelos.py" mover "<arquivo>" <area>[/<tema>]   # corrige a área (ex.: um que caiu em geral/)
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/modelos.py" indexar                   # só refaz os índices
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/modelos.py" ler "<arquivo>"           # texto de um .docx/.pdf para ler o modelo
```

## Como ele organiza (explique em 3 linhas se perguntarem)
- A área se decide **pela pasta que ele despejou** (nome da pasta + nomes e começo do texto dos arquivos dela) — o agrupamento dele é mantido como subpasta de tema; arquivo solto decide sozinho. `honorarios/`, `procuracoes/` e `notificacoes/` são categorias próprias. Sem vencedor claro → `geral/`, marcado `[área?]` no índice.
- Nome do arquivo e das pastas em minúsculas, sem acento, sem espaço, **sem número na frente** (`01-Honorários Advocatícios/CONTRATO X.docx` → `honorarios/contrato-x.docx`). A subpasta de tema é mantida (`franchising/teses-defesa-franquia/`).
- Nunca apaga: arquivo idêntico a um já guardado vai para `_legado/duplicados/`; nome repetido com conteúdo diferente ganha `-2`. Tudo fica em `_sistema/modelos.log`.

## Depois de organizar
1. Mostre o resumo (quantos por área, quantos em `geral/`, duplicados).
2. **`geral/`:** para cada arquivo, leia o começo (`ler`) e proponha a área; com o "sim" do advogado, `mover`. O que ele não souber, fica.
3. **Coluna "O que é"** dos `INDEX.md`: vem com o título do documento `[auto]`. Onde o título não diz nada ("CONTRATO"), leia o modelo e escreva uma linha útil ("contrato de franquia com cláusula de não concorrência de 2 anos") — a próxima indexação preserva o que for escrito.
4. Só modelo **validado** fica: contrato de terceiro, versão antiga e rascunho → pergunte se vão para `_legado/`.
