# 04 — MAPA DE CONTEXTO

> Onde vive cada coisa. Consultar quando a tarefa envolver buscar informação, achar documento ou entender como as ferramentas se conectam.

## Camadas
| Camada | Onde | O que guarda |
|---|---|---|
| Preferências Pessoais (Configurações do Claude) | fora da pasta | quem sou em 10 linhas + a instrução de ler esta pasta |
| Esta pasta COWORK-OS | raiz | tudo do escritório: identidade, clientes, knowledge, motores dos plugins |
| Memória | `identidade/06-MEMORIA.md` | decisões e preferências que valem em todos os casos |
| Memória de caso | `clientes/<x>/STATE.md` e `<projeto>/STATE.md` + `FICHA.md` | o que vale só para aquele cliente / caso |
{{CAMADAS_EXTRAS}}

## Onde buscar cada coisa
| Preciso de… | Vou em… |
|---|---|
| Dados do cliente, procuração, honorários | `clientes/<x>/cadastro/CADASTRO.md` e `cadastro/documentos/` |
| Onde parou um caso | `clientes/<x>/STATE.md` (índice) → `<projeto>/STATE.md` |
| O que sabemos e o que provamos | `<projeto>/FICHA.md` |
| Documento que o cliente mandou | `<projeto>/entrada/` |
| Versão anterior de uma peça | `<projeto>/historico/` |
| Modelo validado do escritório | `knowledge/<area>/` |
| Templates de STATE/FICHA/CADASTRO | `knowledge/templates/` |
| Pesquisa já feita | `<projeto>/pesquisas/AAAA-MM-DD-tema.md` |
| Pendências que atravessam casos | `TASKS.md` |
| Persona, config e rascunhos de um plugin | `<plugin>/` na raiz (motor — não mexer) |
| O que ainda não foi triado da organização antiga | `_legado/` |

## Ferramentas e integrações
{{FERRAMENTAS_DETALHE}}
