# Manual do `cowork-setup` — instalar, montar do zero, organizar o que já existe, atualizar

> Versão 1.1.7 · Para quem usa o Claude (Cowork ou Claude Code) ou o Codex numa pasta chamada **COWORK-OS**, no **Mac ou no Windows**. Você não precisa saber o que é terminal, script ou repositório: tudo acontece no chat, por perguntas e respostas.

## 0. O que é, em 3 linhas

O plugin organiza a sua pasta de trabalho no **método Code-OS**: uma pasta por cliente, um `STATE.md` por caso (onde o trabalho está), uma `FICHA.md` por caso (o que sabemos e o que provamos), versões antigas em `historico/`, os seus **modelos canônicos** por área em `knowledge/modelos/` (é deles que toda peça parte), bases de jurisprudência, doutrina e legislação com nível de citação, e uma cadeia de comando que impede o Claude de improvisar: **Zeus** organiza → **Gandalf** faz o brief → **Chefe** produz a partir do seu modelo (com o plugin da área, se houver) → **Corte** revisa o mérito, fora do contexto de quem escreveu → **Thor** confere a entrega.

**Nenhum plugin é obrigatório.** O `cowork-setup` acopla os plugins jurídicos que você tiver (um, vários ou nenhum); sem plugin, tudo funciona na sua persona e com os seus modelos.

**O que ele não faz:** não apaga arquivo (nunca), não move nada sem você aprovar o plano, não traz conteúdo de terceiros — identidade, voz, regras, modelos e clientes são seus; o plugin só traz a mecânica.

## 1. Antes de começar

| Precisa de | Como saber |
|---|---|
| App Claude com Cowork (ou Claude Code) | você já usa |
| Python 3 | **Mac:** já vem instalado. **Windows:** baixe em python.org e, na instalação, marque **"Add python.exe to PATH"**. Para conferir: abra o Terminal (Mac) ou o Prompt de Comando (Windows) e digite `python3 --version` (Mac) ou `python --version` (Windows). |
| A pasta **COWORK-OS** | a que você já usa, ou uma nova e vazia |
| Seus plugins jurídicos (`trabalhista-adv-os`, `holding-architect`…) | **opcionais** — ele acopla os que estiverem instalados e segue sem eles |
| Seus modelos de peças e contratos | onde estiverem: ele copia de uma pasta do computador, ou você arrasta para `knowledge/modelos/_novos/` |

Pasta na nuvem? Deixe-a sempre baixada, senão o Claude pode não enxergar arquivos que só existem na nuvem: **iCloud** (Mac) → botão direito → Manter baixado · **OneDrive** (Windows) → botão direito → Sempre manter neste dispositivo · **Google Drive** → botão direito → Disponível off-line.

## 2. Instalar (uma vez, 2 minutos)

**No app Claude (Cowork):**
1. Configurações → **Plugins** → **Marketplaces** → **Adicionar** → cole:
   `https://github.com/sbroggioadv/cowork-setup-marketplace`
2. Na lista de plugins, instale **cowork-setup**.
3. Conferir: abra qualquer pasta no Cowork e digite `/cow` — devem aparecer `cowork-setup:cowork-setup`, `cowork-setup:zeus`, etc.

**No Claude Code (terminal), se você usa:**
```bash
claude plugin marketplace add https://github.com/sbroggioadv/cowork-setup-marketplace
claude plugin install cowork-setup@cowork-setup-marketplace
```

Os comandos aparecem com o prefixo do plugin (`/cowork-setup:zeus`). Quando não houver outro plugin com comando de mesmo nome, o atalho curto (`/zeus`) também funciona.

**No Codex (terminal ou app), se você usa — o plugin é o mesmo:**
```bash
codex plugin marketplace add sbroggioadv/cowork-setup-marketplace
codex plugin add cowork-setup@cowork-setup-marketplace
```
**Só usa o app do Codex (Windows ou macOS)?** O app já traz o `codex` dentro dele. Num chat do app, cole:
> Instale um plugin para mim rodando no terminal, nesta ordem: `codex plugin marketplace add sbroggioadv/cowork-setup-marketplace` e depois `codex plugin add cowork-setup@cowork-setup-marketplace`. Use o `codex` que vem dentro deste app se ele não estiver no PATH. Peça a minha aprovação se precisar rodar fora do sandbox e, no fim, me diga a versão instalada.

No Mac, dá também pelo Terminal com o `codex` do app: `/Applications/Codex.app/Contents/Resources/codex-cli/bin/codex plugin marketplace add sbroggioadv/cowork-setup-marketplace` e depois `…/codex plugin add cowork-setup@cowork-setup-marketplace`. No Windows, use o pedido acima (o caminho do app muda de máquina para máquina).

Depois de instalar, **feche o app de vez e abra de novo** (Mac: ⌘Q · Windows: feche também pela bandeja do sistema); o plugin aparece em **Plugins → Instalados**. Para atualizar, o mesmo pedido com `codex plugin marketplace upgrade cowork-setup-marketplace`. **Windows:** Python 3 do python.org com "Add python.exe to PATH" (o instalador traz o `py`, que os hooks do plugin usam no Codex).

As skills aparecem numa sessão nova, com `$`: `$cowork-setup`, `$zeus`, `$modelos`… (nome completo `$cowork-setup:zeus`). Na primeira sessão, confie nos hooks do plugin (terminal: `/hooks`) — é o que faz o painel de abertura aparecer; enquanto isso, `$comecar` e `$encerrar` fazem o mesmo papel. Marque a pasta COWORK-OS como **confiável** quando o Codex perguntar: é o que permite a ele ler os agentes da bancada em `.codex/agents/`.

### Claude e Codex na mesma pasta
A bancada é **uma só**. Pode abrir a mesma pasta no Claude hoje e no Codex amanhã:
- a constituição sai em dois arquivos **idênticos**: `CLAUDE.md` (o Claude lê) e `AGENTS.md` (o Codex lê) — o plugin gera os dois juntos e a auditoria acusa se divergirem;
- os agentes **Zeus · Gandalf · Chefe · Corte · Thor** têm o mesmo texto nos dois: no Claude vêm do plugin; no Codex ficam em `.codex/agents/` da pasta (o Codex não carrega agente de dentro de plugin);
- `clientes/`, `STATE.md`, `FICHA.md`, `CORTE-…md`, `knowledge/` e `identidade/` são os mesmos arquivos para os dois;
- **plugin jurídico** funciona no programa em que estiver instalado — instale-o no Claude, no Codex ou nos dois.
Ao montar a bancada no Codex, a primeira gravação em `.codex/agents/` pede sua aprovação (o Codex protege essa pasta). Montou no Claude? Ela já sai pronta para o Codex.
- **Os dois ao mesmo tempo** funcionam, desde que não editem o mesmo caso juntos. Mantenha o cowork-setup na **mesma versão** nos dois: se um estiver mais velho, ele só lê e pede para atualizar (nada se desfaz).
- **Já tinha uma pasta montada para o Codex** (com `AGENTS.md`, `Consultivo/`, `Contencioso/`, `Holding/`, `_Inbox/`)? É o modo **organizar o que já existe**: cada caso vira uma pergunta ("de qual cliente, para onde?"), ganha STATE no destino, e nada se apaga.

## 3. Montar do zero (pasta nova e vazia)

1. Crie a pasta `COWORK-OS` (Mac: Finder → Nova Pasta · Windows: Explorador → Nova pasta) e abra-a no Cowork.
2. Digite **`/cowork-setup`**. Ele detecta "pasta vazia" → modo **NOVO**.
3. Responda a **entrevista** (6 blocos, um por vez):
   1. quem você é — nome, OAB, escritório, cidade, como quer ser chamado, nome que assina;
   2. atuação — áreas, polos que nunca atua (ex.: "trabalhista só pela empresa"), ferramentas, onde a pasta está;
   3. voz e escrita — postura, tom, vocabulário, o que nunca soa como você, estrutura de peça, formatação;
   4. regras invioláveis — o que nunca se faz, o que sempre se confere;
   5. modelos e bases — onde estão hoje os seus modelos (ele copia; o original fica) · tem Jus IA conectado (carga inicial de jurisprudência)? · tem modelo `.docx` timbrado? · faz holding?;
   6. memória e tarefas — preferências e pendências que valem para todos os casos.
4. Ele cria a estrutura (seção 8), acopla os plugins que você tiver, roda a **auditoria** (15 verificações) e mostra o resultado.
5. Cole o bloco que ele gera em **Configurações → Preferências Pessoais**.
6. Feche e reabra a pasta. O painel de abertura passa a aparecer sozinho.
7. Primeiro cliente: `/novo-cliente "Nome"`. Primeira demanda: `/zeus <o que precisa>`.

Tempo: 15 a 25 minutos, quase todo na entrevista.

## 4. Organizar uma pasta que já existe (migrar)

É o caso de quem já tem o COWORK-OS com `CLIENTES/`, `PERSONA.md`, `MEMORY.md`, `BASE DE CONHECIMENTO/` e as pastas dos plugins.

1. Abra a pasta no Cowork e digite **`/cowork-setup`**. Ele faz o **censo** (não muda nada) e resume: quantos clientes, quantos casos, o que não reconheceu, quais plugins tem.
2. **Backup** — ele pede: duplique a pasta (Mac: selecione no Finder → ⌘D · Windows: botão direito → Copiar, depois Colar na mesma pasta) e responda "sim". Sem isso ele não continua.
3. **Entrevista** — igual à seção 3, mas pré-preenchida com o que ele leu no seu `PERSONA.md`, `CLAUDE.md` e `MEMORY.md` antigos. Você confirma ou corrige.
4. **Plano** — ele mostra o de→para de cada pasta e arquivo e faz **perguntas** só sobre o que não conseguiu decidir sozinho:
   - "qual a área deste caso?" (quando a pasta não diz — ex.: `CONSULTIVO/Contrato X`);
   - "nome da pasta do caso?" (quando a pasta da área é o próprio caso — ex.: `CONTENCIOSO/Cível/STATE.md`); ele sugere `adversario-numero-do-processo`;
   - "este caso do plugin trabalhista é de qual cliente?" (dado de cliente dentro de `trabalhista/casos/`);
   - "para onde vai isto?" (arquivo ou pasta fora do padrão). Responda com um destino, ou `legado` (vai para `_legado/triagem/` para você decidir depois), ou `manter`.
   Depois, **aprove**. Nada foi movido até aqui.
5. **Aplicar** — ele move, cria os `STATE.md`/`FICHA.md`/`CADASTRO.md`, gera a identidade e prova a integridade: **todo arquivo original é reencontrado** (por conteúdo). Se algo não fechar, ele para e mostra.
6. **Casos vivos** — ele lista os casos migrados e pergunta quais estão vivos; nesses, preenche Demanda, Fase atual, Decisões fixadas e Próximo passo a partir do STATE antigo (que fica em `historico/`), marcando `[REVISAR]`.
7. **Auditoria** — 15 verificações; corrige sozinho o que é mecânico; o que sobra vira lista para você (`_legado/triagem/`, memórias a absorver).
8. Cole o bloco em **Preferências Pessoais**, feche e reabra a pasta.

O que muda na sua pasta antiga:

| Antes | Depois |
|---|---|
| `CLAUDE.md`, `PERSONA.md`, `MEMORY.md` na raiz | `identidade/00–06` (conteúdo preservado; originais em `_legado/`) |
| `BASE DE CONHECIMENTO/` (modelos) | `knowledge/modelos/<area>/` — organizado por área, nomes em minúsculas, sem número na frente, com `INDEX.md` |
| jurisprudência / legislação que você guardava | `knowledge/jurisprudencia/proprias/` · `knowledge/legislacao/<tema>/` |
| `CLIENTES/Nome/CONSULTIVO/Documento/STATE.md` | `clientes/nome/consultivo/<area>/documento/STATE.md` (+ FICHA, entrada/, pesquisas/, historico/) |
| `CONTENCIOSO/Cível/{Documentos cliente, Peças Finais}` | `contencioso/civel/<caso>/{entrada/, raiz}` |
| `memory.md` do caso | `_memoria-cowork.md` ao lado do STATE, até ser absorvido |
| `trabalhista/casos/<cliente>/` | o caso vai para `clientes/…`; a pasta do plugin fica |
| o que ele não reconheceu | `_legado/triagem/` |

## 5. Atualizar (saiu versão nova do plugin)

1. No app: Configurações → Plugins → **cowork-setup** → atualizar (ou reinstalar).
2. Ao abrir a pasta, o painel avisa: "Plugin v1.1 > organização v1.0: rode /cowork-setup → atualizar".
3. Digite `/cowork-setup` → **atualizar**. Ele monta um **plano** (nada se move antes do seu "aprovo"), aplica, prova que nenhum arquivo se perdeu e roda a auditoria.
4. **Não toca** no que é seu: `identidade/` fica como está (só a tabela entre marcadores do `05` e as duas linhas que a 1.0 escreveu no `04` sobre `knowledge/`), `clientes/` e as pastas dos plugins não se mexem.

**Da 1.1.0 para a 1.1.1** nada se move: nasce o `AGENTS.md` (a mesma constituição, para o Codex — se você já tinha um `AGENTS.md`, ele vai antes para `_legado/anteriores/`) e a pasta `.codex/agents/` com os 5 agentes.

**Da 1.1.1 até a 1.1.7** nada se move. A 1.1.2 traz a trava de versão (Claude e Codex com versões diferentes: o mais velho só lê e pede para atualizar) e o Histórico do caso passa a dizer quem fez (`· Claude` ou `· Codex`). A 1.1.3 muda o jeito de trabalhar do Zeus e do Gandalf (seção 9.1) e o modelo do STATE ganha o campo "alvo do cliente". A 1.1.4 só corrige os hooks no Codex. A 1.1.5 faz o cowork-setup deixar em paz uma pasta organizada pelo iAPX OS (quem passou para o iAPX OS e ainda tem o cowork-setup ligado). **No Codex**, o atualizar regrava `.codex/agents/` (é por ali que o Zeus e o Gandalf novos chegam à pasta) e pede para confiar de novo nos hooks (`/hooks`). A 1.1.7 muda só os modelos: a FICHA ganha a seção "Agenda do caso" (data, hora, o quê, onde, o que levar) e a linha "Valor da causa ou do negócio" com índice e data-base, e o CADASTRO ganha a linha de honorários (contratado · recebido · a vencer · vencido). Valem para os casos novos; nos já abertos, acrescente quando quiser. A mesma versão traz os painéis opcionais do Claude Code (seção 14).

**Da 1.0 para a 1.1, o plano faz isto na sua `knowledge/`:**

| Antes (1.0) | Depois (1.1) |
|---|---|
| `knowledge/01-honorarios-advocaticios/CONTRATO DE HONORÁRIOS - X.docx` | `knowledge/modelos/honorarios/contrato-de-honorarios-x.docx` |
| `knowledge/10-teses-defesa-franquia/Tese. Incompetência….docx` | `knowledge/modelos/franchising/teses-defesa-franquia/tese-incompetencia-….docx` |
| `knowledge/jurisprudencia-…/` | `knowledge/jurisprudencia/proprias/…` |
| `knowledge/legislacao-<tema>/` | `knowledge/legislacao/<tema>/` |
| `knowledge/templates/` (STATE, FICHA, CADASTRO) | `_sistema/templates/` (do plugin); a sua versão antiga fica em `_legado/knowledge-templates-1.0/` para comparar |
| índices soltos (`INDICE_MESTRE….docx`, `CLAUDE.md`, `README.md` da base) | `_legado/knowledge-antigo/` — o índice novo é gerado |
| o mesmo arquivo em duas pastas | um fica; a cópia idêntica vai para `_legado/duplicados/` |

A área de cada pasta é decidida pela pasta inteira (nome da pasta + nomes e começo dos arquivos), e a sua subpasta vira tema dentro da área. O que ele não souber classificar vai para `knowledge/modelos/geral/`, marcado `[área?]` no índice — `/modelos mover <arquivo> <area>` corrige.

## 6. Auditar e reconfigurar

- **Auditar** (a qualquer hora): `/cowork-setup` → auditar. Relatório em `_sistema/migracao/AUDITORIA-<data>.md`. FAIL = ele corrige ou diz o que fazer; AVISO = lista de trabalho sua.
- **Plugins** (instalou ou removeu plugin jurídico, ou ele não aparece): `/cowork-setup` → plugins. Ele vê quais plugins estão ativos na sessão e refaz a tabela `área → plugin → skill-mestre → Corte` em `identidade/05`. A abertura de cada sessão também confere. Plugin que não está no catálogo também é acoplado — ele só pergunta a área.
- **Reconfigurar** (mudou de área, mudou o nome do escritório): `/cowork-setup` → reconfigurar. Ele pergunta só o que mudou. Regerar a identidade inteira só se você mandar — sobrescreve o que você editou à mão.

**Por que as pastas dos plugins ficam na raiz:** cada plugin procura a própria pasta (`trabalhista/`, `holding/`…) na raiz da bancada, tanto no app Code quanto no Cowork. Mudar para uma subpasta exigiria um caminho absoluto de máquina nas configurações — que muda de computador para computador (pasta no iCloud/Drive) — e o plugin passaria a recriar a pasta na raiz. Por isso o `cowork-setup` nunca move pasta de plugin, e o verificador avisa se alguém mover.

## 7. As skills, uma a uma

| Comando | Quando usar | O que faz | O que produz | O que NÃO faz |
|---|---|---|---|---|
| **`/cowork-setup`** | primeira vez; plugin atualizado; "tem algo errado?" | detecta o modo (novo · migrar · auditar · atualizar · reconfigurar) e conduz as fases: censo → entrevista → plano → aplicar → auditoria | a estrutura da seção 8 + relatórios em `_sistema/` | mover sem aprovação; apagar; inventar dado seu |
| **`/comecar`** | ao abrir a pasta (ou quando o painel automático não apareceu) | lê `identidade/` e `TASKS.md`; imprime pendências, casos com próximo passo e o estado da estrutura | painel de abertura | produzir |
| **`/zeus`** | **toda demanda de cliente**: "contestação do X", "contrato para Y", "responde o cliente Z" | classifica (tipo · área · cliente · tier), confere conflito de interesses, acha ou cria a pasta, **confere o escopo do contrato quando o pedido é novo** (seção 9.1), chama Gandalf se precisar de brief, dispara o Chefe (modelo canônico + plugin da área, se houver), a Corte e o Thor, grava os gates no STATE | o entregável na pasta do caso + STATE atualizado | redigir ele mesmo; pular Corte ou Thor |
| **`/modelos`** | guardar, achar ou corrigir modelo | organiza o que você despejou em `knowledge/modelos/_novos/` (área, nomes em minúsculas, índice); copia de uma pasta do computador; `mover` corrige a área; `indexar` refaz os índices | `knowledge/modelos/<area>/` + `INDEX.md` | apagar (duplicado vai para `_legado/`) |
| **`/jurisprudencia`** | pesquisar ou guardar jurisprudência, súmula, doutrina, lei | Jus IA por área e situação de uso; súmulas e temas (STF · STJ · TST · TJSP · TRT-15 · CJF · FONAJE) embarcados; decisões próprias; doutrina com página; legislação por tema — sempre com nível de citação | `knowledge/jurisprudencia/` · `doutrina/` · `legislacao/` | citar sem nível |
| **`/me-ajuda`** | qualquer dúvida sobre a bancada | olha o estado da pasta e responde pelo mapa de comandos, terminando com o próximo passo | uma resposta e o próximo comando | fazer trabalho de caso (isso é `/zeus`) |
| **`/gandalf`** | antes de qualquer peça ou contrato (T≥2) | entrevista você e escreve o brief no STATE (Demanda · Como começa · Como termina · Critério de aceite) e abre a FICHA (partes, cronologia, fatos confirmados/relatados/lacunas, matriz de provas); separa pedido, sugestão e aceite do cliente, registra o alvo do cliente à parte do prazo fatal e oferece um rascunho de confirmação ao cliente | STATE briefado + FICHA | presumir dado que falta |
| **`/novo-cliente "Nome"`** | cliente novo | cria `clientes/nome/` com STATE (índice), `cadastro/CADASTRO.md`, `cadastro/documentos/` | a pasta do cliente | criar caso (isso é `/novo-projeto`) |
| **`/novo-projeto <tipo> <area> "Cliente" "Caso"`** | caso novo (contencioso · consultivo · holding) | cria a pasta do caso com STATE (+ FICHA em T≥2), `entrada/`, `pesquisas/`; registra no índice do cliente; área nova é registrada e entra na tabela de roteamento | a pasta do caso | pasta com número na frente; nome com acento |
| **`/entregar`** | fechar um entregável | confere o selo de Thor; manda a versão anterior para `historico/`; grava a final na raiz do caso; atualiza STATE e índice; diz o que você faz fora da bancada | versão final + STATE fechado | entregar sem Thor (T≥1) |
| **`/lint-estrutura`** | "tem algo fora do lugar?" | confere a pasta contra a lei do plugin; corrige o que só adiciona (FICHA, entrada/, pesquisas/); lista o que depende de você | relatório E/A | mover conteúdo seu sem perguntar |
| **`/encerrar`** | fim da sessão | garante STATE atualizado em todo caso tocado; registra o significativo na memória (`identidade/06`) ou no cliente; atualiza `TASKS.md`; roda o verificador | sessão fechada sem esquecimento | — |

**Os agentes** (você não os chama; Zeus chama): **Gandalf** (brief), **Chefe** (parte do seu modelo canônico e produz na sua persona, com o plugin da área se houver), **Corte** (revisão de mérito R1-R4 — a Corte do plugin ou, sem plugin, o checklist da bancada — rodando fora do contexto do Chefe; grava `CORTE-R1-R4-<data>.md` e nunca edita a peça), **Thor** (gate de entrega: relatório da Corte, critério de aceite, decisões fixadas, pasta certa, STATE, modelo-base declarado, versões e as quatro camadas: citação com nível · fato só se confirmado na FICHA · texto oculto ou instrução escondida em documento de fora · conflito de interesses — cego para mérito; devolve no máximo 2 vezes, na 3ª escala a você).

**Tiers:** T0 consulta/mensagem (resposta direta) · T1 documento simples (Chefe + Corte se for peça + Thor leve) · T2 peça/contrato (Gandalf + Chefe + Corte + Thor) · T3 projeto multi-etapa (tudo, por etapa). Tier só sobe.

## 8. O que o plugin cria na pasta — e de quem é cada coisa

> Mapa visual (as cinco camadas, o que há dentro de um caso, a cadeia de comando): página "A pasta em um olhar" do `MANUAL.pdf`.

```
COWORK-OS/
├── CLAUDE.md · TASKS.md               constituição (do plugin, regenerada) · pendências (suas)
├── identidade/
│   ├── 00-PERFIL-MESTRE.md            SUAS regras invioláveis — prevalecem sobre tudo
│   ├── 01 quem-sou · 02 voz · 03 escrita · 04 mapa · 06 memória   seus (gerados uma vez, depois você edita)
│   └── 05-ROTEAMENTO-PLUGINS.md       tabela área→plugin→Corte (do plugin, entre marcadores); o resto do arquivo é seu
├── clientes/<cliente>/
│   ├── STATE.md · cadastro/CADASTRO.md · cadastro/documentos/
│   ├── contencioso/<area>/<adversario-numero>/   STATE · FICHA · entrada/ · pesquisas/ · historico/ · CORTE-R1-R4-<data>.md · raiz = vigente
│   ├── consultivo/<area>/<documento>/            idem
│   └── holding/                                  só para quem faz
├── knowledge/                         o que o escritório SABE (seu)
│   ├── modelos/<area>/                modelos canônicos por área + honorarios/ · procuracoes/ · notificacoes/ · geral/ — cada um com INDEX.md
│   │   └── _novos/                    caixa de entrada: despeje aqui; a abertura da sessão organiza sozinha
│   ├── jurisprudencia/                jusia/ (Jus IA, nível 2) · proprias/ (dos seus casos, nível 1) · súmulas embarcadas no plugin
│   ├── doutrina/                      jusia/ · proprias/ (autor · obra · edição · página)
│   └── legislacao/<tema>/             normas com fonte e data; revogada em nao-vigente/
├── <plugin>/                          pastas dos seus plugins jurídicos, na RAIZ (é onde o plugin as procura; não mover, não renomear)
├── _sistema/                          do plugin: versão, áreas, plugins acoplados, templates/ (STATE · FICHA · CADASTRO), plano, auditorias — não editar
└── _legado/                           o que veio de antes e espera sua decisão
```

Regras de nome: pastas (e os modelos de `knowledge/`) em minúsculas, hífen no lugar de espaço, sem acento, sem número na frente. Pasta nova só por `/novo-cliente` e `/novo-projeto`.

## 8.1 Modelos canônicos — como o Claude redige a partir deles

1. **Guardar:** arraste para `knowledge/modelos/_novos/` (arquivo solto ou a pasta inteira, com os nomes do jeito que estiverem) ou `/modelos importar <pasta>`.
2. **Organizar:** na abertura da sessão (ou `/modelos organizar`) ele decide a área, renomeia em minúsculas, guarda em `knowledge/modelos/<area>/` e refaz o `INDEX.md`. Nada é apagado.
3. **Usar:** numa demanda, o Chefe abre o `INDEX.md` da área, escolhe o modelo pertinente, lê inteiro e redige a partir dele, na sua voz. O STATE do caso registra `Modelo-base: knowledge/modelos/<area>/<arquivo>`; a Corte confere que a peça segue a estrutura dele; o Thor confere que o modelo foi declarado.
4. **Melhorar o índice:** a coluna "O que é" começa com o título do documento; escreva ali uma linha útil ("contestação cível B2B com preliminar de ilegitimidade") — a reindexação preserva.

## 9. O que acontece, passo a passo

**Quando você abre a pasta** — o painel aparece sozinho (ou com `/comecar`) e, em segundos:
1. carimba a sessão (é por ela que o encerramento sabe o que você mexeu);
2. organiza os modelos que você despejou em `knowledge/modelos/_novos/` e refaz os índices;
3. acopla os plugins ativos e refaz a tabela de `identidade/05` — nenhum? ele diz que tudo funciona assim mesmo;
4. mostra as pendências, os casos com o próximo passo e o estado da estrutura; se o plugin é mais novo que a organização, avisa para atualizar.

**Quando você despeja um modelo** — nada acontece na hora. Na próxima abertura (ou com `/modelos organizar`) ele decide a área, renomeia, guarda, atualiza o índice e registra o movimento em `_sistema/modelos.log`. Se caiu em `geral/`, ele pergunta a área na primeira oportunidade.

**Numa demanda** (`/zeus contestação do Banco X para a Alfa Ltda, processo …`):
1. **Zeus classifica** (tipo · área · cliente · tier) e mostra em 5 linhas; polo vetado em `identidade/00` → para e explica.
2. **Conflito de interesses** — cruza a parte adversa com todos os seus clientes e adversários; coincidiu → mostra e pergunta se segue.
3. **Pasta** — acha o caso ou cria a pasta com STATE, FICHA, `entrada/` e `pesquisas/`.
4. **Escopo do contrato** — se o cliente já tem contrato de honorários e o pedido é trabalho novo, Zeus confere se está no contrato (seção 9.1); havendo extra, para e você decide.
5. **Gandalf** — pergunta só o que falta e escreve o brief com 3 a 5 critérios de aceite; documento em `entrada/` = fato confirmado, a sua palavra = relatado. Separa pedido, sugestão e aceite do cliente e registra o alvo do cliente à parte do prazo fatal (seção 9.1).
6. **Documentos de fora** — procura texto escondido, caractere invisível ou instrução dirigida à IA nos arquivos de `entrada/`; achou → vai para a FICHA como alerta, nunca é obedecido.
7. **Chefe** — abre o `INDEX.md` de modelos da área, lê o modelo, aciona o plugin da área se houver, redige na sua voz com citações com nível e grava `.docx` + `.md` na raiz do caso, com `Modelo-base:` no STATE.
8. **Corte** — outra instância, sem o contexto do Chefe: R1 fatos × FICHA · R2 base legal vigente e com nível · R3 tese e coerência · R4 forma e completude; grava `CORTE-R1-R4-<data>.md`. AJUSTAR → volta ao Chefe.
9. **Thor** — confere o relatório da Corte, o critério de aceite, as decisões fixadas, a pasta, o STATE, o modelo declarado e as 4 camadas. DEVOLVIDO → Chefe → Corte → Thor (no máximo 2×; na 3ª, escala a você).
10. **Fechamento** — Zeus grava os selos em `## Gates`, atualiza Fase, Próximo passo e Histórico (com `· Claude` ou `· Codex`) e diz onde está a peça e o que você faz fora da bancada (protocolar, lançar o prazo no seu sistema).

### 9.1 Pedido novo de cliente que já tem contrato, e o brief do Gandalf (1.1.3)

**Escopo do contrato.** O cliente da Alfa escreve: "entra com a ação contra o Banco X e, aproveitando, revisa o contrato do fornecedor novo". Zeus lê o contrato de honorários (a linha do `cadastro/CADASTRO.md` diz qual é) e quebra o pedido em itens:

| Item | Classificação | Base |
|---|---|---|
| ação contra o Banco X | incluído | Cl. 1ª, objeto do contrato |
| revisar o contrato do fornecedor novo | extra | Cl. 2ª, exclusões |
| ajustar um dado que faltou na notificação já entregue | incluído ou correção nossa | Cl. 3ª, rodadas de ajuste |

- As quatro classificações: **incluído** · **correção nossa** (ajuste em algo que o escritório já entregou, que não se cobra) · **extra** · **ambíguo** (com as duas leituras e o fato que decide).
- Só vale como combinado o contrato assinado e o aditivo aceito por escrito. Proposta, minuta, pedido do cliente ou "recebido" não são aceite.
- Havendo extra ou ambíguo, Zeus para antes do Chefe e você decide para cada item: **cortesia** · **aditivo antes de começar** · **cobrar depois**. A decisão vai para "Decisões fixadas" do STATE e a tabela fica em `pesquisas/`.
- Aditivo escolhido? É um documento simples (T1): o Chefe parte do seu modelo de `knowledge/modelos/honorarios/` e usa o valor do contrato ou da sua tabela de honorários. O que não estiver escrito em lugar nenhum fica `[FALTA: …]` — nunca inventado.

**O brief do Gandalf.**
- **Pedido, sugestão e aceite.** Na mensagem do cliente, só o que ele pediu entra na Demanda. Sugestão ("acho que dá pra pedir dano moral") vai para Pendências, para você decidir. Aceite por escrito ("pode seguir, concordo") entra na FICHA como fato confirmado.
- **Alvo do cliente ≠ prazo fatal.** A data que o cliente quer fica registrada como "alvo do cliente", separada do prazo fatal (lei, processo). Só vira prazo do escritório se você aceitar.
- **Confirmação ao cliente.** Ao fechar o brief, Gandalf oferece um rascunho curto: o que vamos fazer · o que ficou fora · o que o cliente ainda precisa decidir. Sem nada interno; quem envia é você.

**Quando você instala ou remove um plugin** — na próxima abertura ele vê o plugin ativo e refaz a tabela área → plugin → skill-mestre → Corte; fora do catálogo, pergunta a área. Removeu → a área volta para "persona do escritório", sem travar nada.

**Quando você encerra** — `/encerrar` (ou ao fechar): se você mexeu numa pasta de cliente sem atualizar o STATE daquele caso, ele barra uma vez e diz qual; depois registra o que vale para todos os casos em `identidade/06-MEMORIA.md` e roda o verificador.

## 10. A rotina (a cronologia de todo dia)

1. Abrir a pasta → painel (ou `/comecar`) — organiza os modelos que você despejou em `knowledge/modelos/_novos/`.
2. Demanda de cliente → `/zeus …` (ele chama Gandalf, Chefe, Corte e Thor sozinho).
3. Fechar entregável → `/entregar`.
4. Fim → `/encerrar`.

Se você mexer numa pasta de cliente e tentar encerrar sem atualizar o STATE, o plugin barra uma vez e diz qual caso ficou sem próximo passo.

## 11. Problemas comuns

| Sintoma | O que fazer |
|---|---|
| "python3 não encontrado" | Mac: abra o Terminal e digite `python3` — o sistema oferece instalar. Windows: instale de python.org com "Add python.exe to PATH" e reabra o app; o plugin usa `python` ou `py` quando `python3` não existe. Enquanto isso ele segue em modo checklist (só verifica, não move). |
| Arquivos "na nuvem" (ícone de nuvem ao lado do arquivo) | botão direito na pasta → Manter baixado (iCloud) · Sempre manter neste dispositivo (OneDrive) · Disponível off-line (Google Drive), antes de aprovar o plano |
| Painel de abertura não aparece | feche e reabra a pasta; se persistir, `/comecar` faz o mesmo (o painel agora roda em Python — funciona no Windows sem Git Bash) |
| Dois clientes que são o mesmo (`Maria Oliveira` e `MARIA OLIVEIRA ME`) | no plano, responda a pergunta de destino dos dois com o mesmo caminho — ele une |
| Plugin jurídico não aparece na tabela de roteamento | `/cowork-setup` → plugins (ele lê os plugins ativos na sessão). Sem plugin nenhum, tudo funciona igual |
| Modelo foi para `geral/` ou para a área errada | `/modelos mover <arquivo> <area>` |
| Aviso `MOTOR` (pasta de plugin fora da raiz) | devolva a pasta para a raiz: é lá que o plugin a procura |
| Comandos aparecem como `/cowork-setup:zeus` | é o prefixo do plugin; o atalho `/zeus` funciona quando não há conflito |
| Quero desfazer | nada foi apagado: `_sistema/migracao/MIGRACAO.md` lista cada movimento; a cópia que você fez no passo do backup é a volta |

## 12. Preferências Pessoais

No fim do setup o plugin imprime um bloco ("Quem sou · Minha bancada · Como trabalhar comigo"). Cole em **Configurações → Preferências Pessoais** do Claude, substituindo o antigo. No Codex, o mesmo bloco vai em `~/.codex/AGENTS.md` (instruções pessoais que valem para todas as pastas). É o que faz o Claude ler `CLAUDE.md` e `identidade/` antes de qualquer tarefa mesmo em sessões novas.

## 13. Versões

- A versão da organização instalada está em `_sistema/versao`; a do plugin, no app. O painel de abertura avisa quando diferem.
- Histórico do plugin e melhorias: `github.com/sbroggioadv/cowork-setup-marketplace`.
- O `MANUAL.pdf` é gerado de `manual/manual.html` (`bash manual/gerar_pdf.sh`, Chrome headless, A4).

| Versão | O que mudou |
|---|---|
| 1.1.3 · 13/10/2026 | Zeus confere o escopo do contrato antes de produzir (incluído · correção nossa · extra · ambíguo; você decide cortesia, aditivo ou cobrar depois) · Gandalf separa pedido, sugestão e aceite, registra o alvo do cliente e oferece rascunho de confirmação · STATE com "alvo do cliente". |
| 1.1.7 · 22/10/2026 | Modelos: "Agenda do caso" e valor da causa na FICHA; honorários (contratado · recebido · a vencer · vencido) no CADASTRO. Novos no marketplace, opcionais e só para o Claude Code: os painéis **Bancada** (`/bancada`) e **Dossiê do caso** (`/dossie`) — seção 14. Nada se move na pasta. |
| 1.1.6 · 19/10/2026 | Correção: ao sincronizar no claude.ai, três descrições geravam aviso (duas com os sinais < >, e a do /cowork-setup com mais de 500 caracteres). Textos ajustados; nada muda na pasta. |
| 1.1.5 · 19/10/2026 | Correção: com o cowork-setup e o iAPX OS ligados no mesmo programa, o cowork-setup reescrevia a lista de plugins e a tabela de roteamento de uma pasta do iAPX OS e sugeria "atualizar" por cima. Agora, numa pasta do iAPX OS, ele só avisa e não lê nem altera nada (desative-o: o iAPX OS é a evolução dele). Nada muda na pasta do cowork-setup. |
| 1.1.4 · 14/10/2026 | Correção: no Codex, os hooks de abertura e de fim de sessão do plugin falhavam ("SessionStart Failed") porque procuravam a pasta do plugin só pela variável do Claude; agora acham pelas duas. Nada muda na pasta. |
| 1.1.2 · 13/10/2026 | Claude e Codex na mesma pasta sem um desfazer o outro (trava de versão) · Histórico diz quem fez · pasta montada por matéria (`Consultivo/`, `Contencioso/`, `Holding/`, `_Inbox/`) reorganizada por cliente, caso a caso · instalação pelo app do Codex. |
| 1.1.1 · 13/10/2026 | O mesmo plugin no Codex: `CLAUDE.md` = `AGENTS.md` e agentes em `.codex/agents/`. |
| 1.1.0 · 29/09/2026 | Plugins opcionais · modelos canônicos por área · jurisprudência, doutrina e legislação com nível · Corte separada e Thor com 4 camadas. |

## 14. Painéis do Claude Code: Bancada e Dossiê (opcionais)

Dois painéis laterais que leem a sua pasta e mostram o caso da conversa — o último projeto cujo `STATE.md` ou `FICHA.md` a conversa abriu ou editou. Os dois abrem sozinhos no início da sessão (feche o que não quiser; `/bancada` e `/dossie` reabrem, e a Bancada tem o botão "Dossiê do caso"). Funcionam **só no Claude Code** (aba Code do app, terminal ou VS Code); no Cowork e no Codex não aparecem, e o cowork-setup segue igual sem eles.

- **Bancada** (`/bancada`): o que fazer agora — trilha Brief → Redação → Corte → Thor → Entrega, há quanto tempo o pedido está em curso, próximo passo, fatos e provas da FICHA, prazo, próximo compromisso da Agenda do caso, botões de ação e, no rodapé, o quadro vermelho com as pendências do `TASKS.md`.
- **Dossiê do caso** (`/dossie`): o que se sabe do caso, só para consulta — decisões fixadas, cronologia com o status de prova de cada fato, partes e foro, checagem de conflito, valor, honorários e as peças produzidas.

Instalar (no Claude Code, com o marketplace deste plugin já adicionado):

```
/plugin install bancada@cowork-setup-marketplace
/plugin install dossie@cowork-setup-marketplace
```

Como se comportam:
- **Os botões não executam nada sozinhos:** escrevem o pedido na caixa de mensagem e você confirma com Enter. O WhatsApp ainda mostra a prévia e só envia quando você disser "enviar". Adversário e Juiz seguem o método do plugin prisma-julgador-os; quem não o tem recebe o método no próprio pedido.
- **O ☐ de uma pendência** a move para "## Feito" no `TASKS.md`, com a data, e o botão **Desfazer** volta o arquivo se ninguém o mexeu depois.
- **Registro de pedidos:** a Bancada anota em `.bancada/pedidos.jsonl`, na raiz da pasta, cada mudança no `STATE.md` do caso (brief, Corte, Thor, etapa, entrega). É dali que vem o "pedido em curso há…". O `STATE.md` continua sendo a fonte da verdade.
- **Cores com um só sentido:** azul = agora · verde = feito ou provado · âmbar = atenção ou sai do escritório · vermelho = bloqueio ou pendência · roxo = decisão fixada (no Dossiê) e o botão Juiz · laranja = Adversário · tracejado = ainda não existe.
