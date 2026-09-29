---
name: cowork-setup
description: Organiza a pasta COWORK-OS do escritório no método Code-OS (cliente-primeiro, STATE.md por caso, FICHA, modelos canônicos por área em knowledge/modelos/, bases de jurisprudência/doutrina/legislação com nível, cadeia Zeus→Gandalf→Chefe→Corte→Thor, auditoria). Acopla os plugins que o escritório tiver — nenhum é obrigatório. Detecta sozinho o que fazer — pasta vazia (novo), pasta no formato antigo (migrar), pasta já organizada (auditar · atualizar · plugins · reconfigurar). Nunca move nada sem o advogado aprovar o plano; nunca apaga. Use quando o advogado disser /cowork-setup, "organiza minha pasta", "arruma o Cowork OS", "audita a estrutura", "atualiza a organização".
---

# /cowork-setup — organização da bancada, de ponta a ponta

Você conduz o advogado por um setup que **os scripts executam** e **você só orquestra**. Regra de ouro: rode script → leia a saída → pergunte ao advogado só o que o script apontou → rode o próximo. Tom: técnico-didático, passo a passo, sem pressupor que ele sabe o que é terminal, script ou JSON — ele nunca vê nada disso; vê perguntas e respostas.

**Onde estão os scripts:** `${CLAUDE_PLUGIN_ROOT}/scripts/` (a pasta deste plugin). Se a variável não existir, a pasta do plugin é a que contém este arquivo, um nível acima de `commands/`. Rode tudo **a partir da raiz da pasta COWORK-OS** (o diretório de trabalho da sessão). Exemplo: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/censo.py"`.

**Python:** os comandos abaixo usam `python3`. No Windows, se `python3` não existir, use `python` (ou `py -3`) no lugar — o resto é igual.

## O que você NUNCA faz
- Não cria pasta, arquivo ou nome fora do que os scripts criam (a lei é `espec/estrutura.json`). Precisa de algo fora dela → pergunta.
- Não move nem apaga arquivo à mão. Mover é o `aplicar.py`, depois do plano aprovado. Apagar, nunca — o que não tem lugar vai para `_legado/triagem/`.
- Não pula fase: cada script exige o artefato da anterior e recusa sem ele.
- Não preenche o perfil com suposição: campo que o advogado não respondeu fica `[A PREENCHER]` e a auditoria acusa.
- Não escreve caminho absoluto (`/Users/...`) em arquivo da bancada.
- Não toca nada fora da pasta COWORK-OS.
- Não renomeia nem move as pastas dos plugins jurídicos (`trabalhista/`, `holding/`…): cada plugin procura a própria pasta **na raiz** da bancada, no app Code e no Cowork. Mover quebraria o plugin.
- Não exige plugin nenhum. Sem plugin, tudo funciona: o chefe produz na persona a partir de `knowledge/modelos/`, a Corte usa o checklist da bancada.

## Passo 0 — Censo (30 segundos, não muda nada)
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/censo.py"
```
Leia o **modo detectado** e siga a trilha:
- **NOVO** (pasta vazia) → Trilha A.
- **MIGRAR** (formato antigo: `CLIENTES/`, `PERSONA.md`, `MEMORY.md`, `BASE DE CONHECIMENTO/`, casos dentro dos motores) → Trilha B.
- **ORGANIZADO** (`_sistema/versao` existe) → versão da pasta menor que a do plugin? Ofereça primeiro **atualizar** (Trilha D). Senão, pergunte o que ele quer: **auditar** (Trilha C) · **plugins** (Trilha P — instalou/removeu plugin) · **reconfigurar** identidade (Trilha E).

**Plugins (nunca trava):** olhe a sua própria lista de skills disponíveis nesta sessão e junte os nomes dos plugins jurídicos (o prefixo antes de `:` — ex.: `trabalhista-adv-os`, `holding-architect`, `marca-inpi-adv-os`). Rode:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plugins.py" detectar --sessao "<nomes separados por vírgula>"
```
Nenhum plugin → siga normalmente (a saída explica que a bancada funciona sem). Plugin fora do catálogo sem área → pergunte a área e `plugins.py area <plugin> <area>`.

Mostre ao advogado o resumo em 5 linhas no máximo: quantos clientes, quantos projetos, o que não foi reconhecido, quais plugins foram acoplados.

## Trilha B — MIGRAR (a mais comum)

### B1 · Backup (gate humano)
Antes de qualquer coisa: "Duplique a pasta COWORK-OS no Finder (selecione → ⌘D) ou confirme que tem backup. Confirma?" Sem "sim", pare aqui.

### B2 · Entrevista (o conteúdo é dele — você só pergunta e registra)
Pré-preencha o que der a partir dos arquivos antigos:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/perfil.py" importar-legado
```
Depois pergunte **em blocos, um por vez**, mostrando o que já achou e pedindo só o que falta (use botões/opções quando a plataforma oferecer):
1. **Identidade** — nome completo · OAB (nº e UF) · nome do escritório · cidade/UF · como quer ser chamado no chat (ex.: "Dr. João") · nome como assina documento.
2. **Atuação** — áreas (mostre as que o censo detectou nas pastas + a lista: civel, consumidor, empresarial, franchising, societario, tributario, holding, trabalhista, bancario, familia, licitacoes, previdenciario, medico, marcas-inpi, imigracao, execucao, penal-empresarial; pode criar outra) · polos que **nunca** atua (ex.: "trabalhista só pela empresa") · ferramentas (WhatsApp, Drive, sistema de processos, assinatura eletrônica) · onde a pasta está (iCloud / Google Drive / local — se for nuvem, avise: "mantenha 'baixado' para o Cowork sempre enxergar os arquivos").
3. **Voz e escrita** — leia `_legado/PERSONA-cowork.md` (ou o `PERSONA.md` ainda na raiz) e proponha, em 3 linhas cada: postura · tom · vocabulário-assinatura · o que nunca soa como ele · estrutura de peça · regras de estilo · formatação/entrega. Ele confirma ou corrige. Sem persona antiga: pergunte esses itens em 2 rodadas.
4. **Regras invioláveis** — leia `_legado/CLAUDE-cowork.md` (ou `CLAUDE.md` antigo), liste o que parece regra ("nunca…", "sempre…") e pergunte "mantenho estas? tem outras?". Numere PA-01, PA-02… Protocolos (o que sempre se confere antes de entregar) idem.
5. **Modelos e bases** — "Onde estão hoje os seus modelos de peças e contratos?" Pasta do computador → anote o caminho: depois do setup, `/modelos importar <pasta>` (copia; o original fica). Prefere arrastar → diga que depois do setup é só despejar em `knowledge/modelos/_novos/` que a bancada organiza por área sozinha. · Tem Jus IA conectado? Quer uma carga inicial de jurisprudência por área (`/jurisprudencia carga`)? · Tem modelo `.docx` timbrado? (sim → pasta `timbrado/`) · Faz holding? (sim → `clientes/<x>/holding/` quando houver).
6. **Memória e tarefas** — leia `_legado/MEMORY-cowork.md` e `TASKS` antigo, se existirem; pergunte o que ainda vale (preferências de trabalho · contexto do escritório · pendências vivas).

Grave tudo de uma vez (uma chamada, JSON com as chaves do `perfil.py`; texto com quebras usa `\n`):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/perfil.py" set-json '{"NOME":"…","OAB":"…","ESCRITORIO":"…","CIDADE_UF":"…","TRATAMENTO":"…","NOME_DOCUMENTO":"…","AREAS":"civel, trabalhista","POLOS_VETADOS":"…","FERRAMENTAS":"…","LOCAL_PASTA":"…","ATUACAO":"…","COMO_TRABALHO":"…","PROIBICOES":"PA-01 …\nPA-02 …","PROTOCOLOS":"P1 …","POSTURA":"…","TOM":"…","VOCABULARIO":"…","ANTI_VOZ":"…","ESTRUTURA_PECA":"…","REGRAS_ESTILO":"…","FORMATACAO":"…","FERRAMENTAS_DETALHE":"…","PREFERENCIAS":"…","CONTEXTO":"…","ENTREGAS":"…","COMO_TRABALHAR":"…","PLUGINS":["trabalhista-adv-os"],"MODULOS":{"timbrado":false,"sumulas":false,"holding":false}}'
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/perfil.py" faltam
```
`faltam` tem de devolver "(nada falta)". Se listar campo, pergunte só ele.

### B3 · Plano (de→para; nada se move)
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/planejar.py"
```
Abra `_sistema/migracao/PLANO.md`. Para cada **pergunta** da tabela, pergunte ao advogado em linguagem de gente (mostre a sugestão como opção padrão; para "nome do projeto" leia o STATE antigo e proponha `adversario-numero-do-processo`; para caso dentro de motor de plugin proponha o cliente certo). Registre cada resposta:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/planejar.py" --responder <nº da pergunta> "<resposta>"
```
Respostas possíveis: um caminho (`clientes/x/consultivo/empresarial/contrato-y`), `legado` (vai para `_legado/triagem/`), `manter` (fica onde está). Depois mostre o plano resumido (clientes → pastas novas; o que vai para legado; contagem de arquivos) e peça a aprovação explícita. Com "aprovo":
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/planejar.py" --aprovar
```

### B4 · Aplicar
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/aplicar.py"
```
Confira na saída: `prova de integridade: 0 arquivo(s) … não reencontrado(s) ✓`. Se não for 0, **pare** e mostre a lista ao advogado (nada foi apagado — está em `_legado/triagem/conflitos/` ou ficou no lugar). Log completo em `_sistema/migracao/MIGRACAO.md`.

### B4.1 · Modelos
O `aplicar` já levou a base de conhecimento antiga para `knowledge/modelos/_novos/` e organizou por área (nomes em minúsculas, sem número; duplicados em `_legado/duplicados/`; jurisprudência, doutrina e legislação nas pastas delas). Abra `knowledge/modelos/INDEX.md`, mostre quantos modelos há por área e resolva `geral/` como diz a skill `/modelos` (propor a área de cada um e `modelos.py mover` com o "sim" dele). Se ele indicou uma pasta de modelos na entrevista: `/modelos importar <pasta>`.

### B5 · Casos vivos (trabalho seu, bem delimitado)
Liste os projetos migrados (`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/painel.py" --n 50`) e pergunte: "Quais destes estão vivos?" Para cada vivo: leia `historico/AAAA-MM-DD-STATE-cowork.md` e `_memoria-cowork.md` do projeto e preencha no `STATE.md` novo: **Demanda** (3 linhas) · **Fase atual** · **Decisões fixadas** (o que a memória antiga dizia que vale) · **Próximo passo** (1 linha, concreta). Marque `[REVISAR]` no que deduziu. Apague o `_memoria-cowork.md` **só** depois de absorvido. Os não vivos ficam como estão (o próximo passo já diz "ler historico/… e preencher").

### B6 · Auditoria
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/auditar.py" --corrigir
```
FAIL → corrija o que é mecânico (rode de novo com `--corrigir`; preencha campo que faltou no perfil e `aplicar.py --so-render`) e repita. **Máximo 2 tentativas**; na 3ª, mostre a lista de FAIL ao advogado e pare. AVISO não barra: vira lista de trabalho dele (`_legado/triagem/`, memórias a absorver).

### B7 · Fechar
1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/perfil.py" preferencias` → mostre o bloco e diga: "Copie e cole em **Configurações → Preferências Pessoais** do Claude (substitui o antigo)."
2. Diga o que mudou, em 8 linhas: onde estão os clientes, onde está a identidade, o que ficou em `_legado/triagem/` para ele decidir, onde está o relatório (`_sistema/migracao/AUDITORIA-<data>.md`).
3. Próximos passos: "Feche e reabra a pasta no Cowork (o painel de abertura passa a aparecer e organiza os modelos que você despejar em `knowledge/modelos/_novos/`). Primeira demanda: `/zeus <o que precisa>`. Cliente novo: `/novo-cliente`. Dúvida: `/me-ajuda`. Fim de sessão: `/encerrar`."
4. Termine com 1 linha de como ele pode pedir melhor da próxima vez.

## Trilha A — NOVO (pasta vazia)
B2 (entrevista, sem importar-legado) → `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/aplicar.py" --novo` → B6 → B7. Depois ofereça criar o primeiro cliente com `/novo-cliente`.

## Trilha C — AUDITAR
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/auditar.py" --corrigir` → explique cada FAIL/AVISO em uma linha de gente e o que fazer. Corrija o mecânico; o que move conteúdo de cliente é decisão dele.

## Trilha D — ATUALIZAR (plugin mais novo que a organização)
1. Backup (B1) se a atualização mover pastas — a 1.0 → 1.1 move `knowledge/`.
2. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/planejar.py"` → o censo viu ORGANIZADO e o plano é de **atualização**: só a mecânica muda. `identidade/` fica como está (exceto a tabela entre marcadores do 05 e as 2 linhas que a 1.0 escreveu no 04 sobre `knowledge/`); `clientes/` e os motores dos plugins não se mexem.
3. Mostre o plano em linguagem de gente — na 1.0 → 1.1: pastas de `knowledge/` (numeradas, maiúsculas) → `knowledge/modelos/<area>/` organizadas e renomeadas; jurisprudência → `knowledge/jurisprudencia/proprias/`; legislação → `knowledge/legislacao/<tema>/`; `knowledge/templates/` → `_sistema/templates/` (o antigo, com o que ele personalizou, fica em `_legado/knowledge-templates-1.0/`); índices soltos → `_legado/knowledge-antigo/`. Com "aprovo": `planejar.py --aprovar`.
4. `aplicar.py` → confira `prova de integridade: 0 … ✓` → B4.1 (modelos) → Trilha P (plugins) → Trilha C (auditar).

## Trilha P — PLUGINS (instalou, removeu ou nada aparece)
Junte da sua lista de skills os plugins jurídicos visíveis nesta sessão e rode `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/plugins.py" detectar --sessao "<nomes>"`. A tabela de `identidade/05` se refaz sozinha (área → plugin → skill-mestre → Corte). Plugin fora do catálogo: pergunte a área → `plugins.py area <plugin> <area>`. Sem plugin: explique que tudo funciona (persona + modelos + Corte genérica) e que plugin pode ser acoplado a qualquer momento.

## Trilha E — RECONFIGURAR
Mudou área/identidade: pergunte só o que mudou → `perfil.py set-json` → `aplicar.py --roteamento` (só a tabela) ou `--so-render --forcar` **apenas se ele mandar regerar a identidade inteira** (avise que sobrescreve edições manuais em `identidade/`).

## Falhas conhecidas
- `python3` não encontrado → diga: "Preciso do Python 3 no computador (macOS já tem). Se falhar, me avise que sigo em modo checklist." Modo checklist = você lê a espec (`${CLAUDE_PLUGIN_ROOT}/espec/estrutura.json`) e faz as verificações à mão, sem mover nada.
- Pasta em iCloud com arquivos "na nuvem" (não baixados) → o censo conta, mas mover pode falhar: peça para "Manter baixado" a pasta antes de B4.
- Nome de cliente duplicado com grafia diferente (`Maria Oliveira` e `MARIA OLIVEIRA ME`) → o plano cria duas pastas; pergunte se é o mesmo cliente e responda a pergunta de destino com o mesmo caminho para unir.
