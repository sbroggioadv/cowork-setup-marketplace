# cowork-setup — organize sua pasta COWORK-OS no método Code-OS

Plugin gratuito para o **Claude** (Cowork ou Code) **e para o Codex** (terminal ou app) que organiza a pasta de trabalho do escritório: **um lugar por cliente**, um `STATE.md` por caso (onde o trabalho está), uma `FICHA.md` por caso (o que sabemos e o que provamos), versões antigas em `historico/`, os seus **modelos canônicos por área** em `knowledge/modelos/` (é deles que toda peça parte), bases de jurisprudência, doutrina e legislação com nível de citação, e uma cadeia de comando que impede o Claude de "inventar": **Zeus** organiza → **Gandalf** faz o brief → **Chefe** produz a partir do seu modelo → **Corte** revisa o mérito, fora do contexto de quem escreveu → **Thor** confere a entrega.

**Nenhum plugin é obrigatório.** Ele acopla os plugins jurídicos que você tiver instalados — um, vários ou nenhum.

**A mesma pasta abre no Claude e no Codex**, alternando, sem reorganizar nada: o plugin é um só, a constituição da bancada sai em dois arquivos idênticos (`CLAUDE.md` para o Claude, `AGENTS.md` para o Codex) e os agentes Zeus · Gandalf · Chefe · Corte · Thor têm as mesmas ordens nos dois.

O plugin traz **só a mecânica**. Identidade, voz, regras, modelos e clientes são seus — ele pergunta e registra.

## Instalar (uma vez)
**Claude** — no app: **Configurações → Plugins → Marketplaces → adicionar** o endereço deste repositório e instale **cowork-setup**. No terminal:
```
/plugin install cowork-setup --marketplace sbroggioadv/cowork-setup-marketplace
```
**Codex — terminal** (Windows ou macOS):
```
codex plugin marketplace add sbroggioadv/cowork-setup-marketplace
codex plugin add cowork-setup@cowork-setup-marketplace
```
**Codex — só o app** (Windows ou macOS; o app já traz o `codex` dentro dele). Num chat do app, cole:
> Instale um plugin para mim rodando no terminal, nesta ordem: `codex plugin marketplace add sbroggioadv/cowork-setup-marketplace` e depois `codex plugin add cowork-setup@cowork-setup-marketplace`. Use o `codex` que vem dentro deste app se ele não estiver no PATH. Peça a minha aprovação se precisar rodar fora do sandbox e, no fim, me diga a versão instalada.

No Mac também dá pelo Terminal, com o `codex` do app: `/Applications/Codex.app/Contents/Resources/codex-cli/bin/codex plugin marketplace add sbroggioadv/cowork-setup-marketplace` e depois o mesmo caminho com `plugin add cowork-setup@cowork-setup-marketplace`. No Windows, o caminho do app muda de máquina para máquina — use o pedido acima.

Depois de instalar: **feche o app de vez e abra de novo** (no Mac, ⌘Q; no Windows, feche também pela bandeja do sistema). O plugin aparece em **Plugins → Instalados**. Para atualizar: o mesmo pedido, com `codex plugin marketplace upgrade cowork-setup-marketplace`.
Os plugins jurídicos que você já usa continuam iguais (e as pastas deles continuam na raiz, onde eles as procuram). Plugin jurídico funciona no programa em que está instalado.

## Organizar (uma vez por pasta)
1. Abra o Cowork na sua pasta **COWORK-OS** (a que já usa, ou uma nova).
2. No Finder, duplique a pasta (⌘D) — é o seu backup.
3. No chat: `/cowork-setup` (no Codex: `$cowork-setup`). Ele conta o que encontrou, faz a entrevista (quem você é, áreas, voz, regras), mostra o **plano** do que vai para onde e **só move depois que você aprovar**. Nada é apagado: o que não tem lugar vai para `_legado/triagem/` para você decidir.
4. Cole o bloco que ele gera em **Configurações → Preferências Pessoais** (Claude) ou em `~/.codex/AGENTS.md` (Codex).
5. Feche e reabra a pasta. O painel de abertura passa a aparecer sozinho (no Codex, confie uma vez nos hooks do plugin: `/hooks`).

## Usar (todo dia)
No Claude os comandos começam com `/`; no Codex, com `$` (`$zeus`, `$modelos`…).

| Você diz | O que acontece |
|---|---|
| `/comecar` (ou reabrir a pasta) | painel: pendências, casos com próximo passo, estado da estrutura |
| `/zeus contestação do caso X do cliente Y` | classifica, confere conflito de interesses, abre a pasta certa, faz o brief se precisar, produz a partir do seu modelo (com o plugin da área, se houver), passa pela Corte e pelo Thor e grava no STATE |
| arrastar modelos para `knowledge/modelos/_novos/` · `/modelos` | organiza sozinho por área, nomes em minúsculas, índice por área |
| `/jurisprudencia` | pesquisa (Jus IA), súmulas e temas embarcados, doutrina e legislação — sempre com nível de citação |
| `/me-ajuda` | qualquer dúvida sobre a bancada |
| `/novo-cliente "Nome"` · `/novo-projeto contencioso civel "Cliente" "Adversário nº"` | as únicas formas de criar pasta — sempre certas |
| `/gandalf` | brief + FICHA antes de qualquer peça ou contrato |
| `/entregar` | versão final na raiz do caso, anterior em `historico/`, STATE atualizado |
| `/lint-estrutura` | "tem algo fora do lugar?" |
| `/encerrar` | fecha a sessão: STATE de tudo que foi tocado, memória, tarefas |
| `/cowork-setup` de novo | auditar · atualizar (versão nova do plugin) · plugins (instalou ou removeu) · reconfigurar |

## O que ele cria
```
COWORK-OS/
├── CLAUDE.md = AGENTS.md · TASKS.md   constituição (gerada; uma para o Claude, outra idêntica para o Codex) · pendências vivas
├── .codex/agents/                   zeus · gandalf · chefe · corte · thor para o Codex (no Claude eles vêm do plugin)
├── identidade/00–06                 suas regras, quem você é, voz, escrita, mapa, roteamento, memória
├── clientes/<cliente>/              STATE (índice) · cadastro/ · contencioso/<area>/<caso>/ · consultivo/<area>/<doc>/ · holding/
│     cada caso: STATE.md · FICHA.md · entrada/ · pesquisas/ · historico/ · (raiz = versão vigente)
├── knowledge/modelos/<area>/        seus modelos canônicos (+ honorarios · procuracoes · notificacoes · geral) · _novos/ = caixa de entrada
├── knowledge/jurisprudencia · doutrina · legislacao   bases de citação, com nível
├── <plugin>/                        pastas dos seus plugins jurídicos (na raiz, onde eles as procuram)
├── _sistema/                        do plugin: versão, plugins acoplados, templates (STATE · FICHA · CADASTRO), plano, auditorias
└── _legado/                         o que veio de antes e espera sua decisão
```

## Garantias
- **Nada se move sem você aprovar o plano; nada se apaga.** Prova de integridade ao final: todo arquivo original é reencontrado (por conteúdo). A única organização automática é a da caixa `knowledge/modelos/_novos/` — despejar ali é o pedido; cada movimento fica em `_sistema/modelos.log` e duplicado vai para `_legado/duplicados/`.
- **Rodar de novo não bagunça:** o setup é idempotente.
- **A organização é regra em código** (`espec/estrutura.json`): o verificador, o painel e a auditoria leem a mesma lei — o Claude não improvisa.
- **Pronto para o próximo passo:** quando quiser versionar com git, a estrutura já é compatível (o `historico/` vira histórico do git).

Requisitos: Claude (Cowork ou Code) e/ou Codex (terminal ou app desktop) · Windows ou macOS · Python 3 (o macOS já traz; no Windows, instale pelo python.org marcando "Add python.exe to PATH" — o instalador já traz o `py`, que o Codex usa no Windows). Súmulas e temas do STF, STJ, TST, TJSP, TRT-15, CJF e FONAJE vêm embarcados (retrato datado — conferir vigência antes de citar). **Passo a passo completo: [MANUAL.md](MANUAL.md).** Dúvidas: `/cowork-setup` e pergunte.
