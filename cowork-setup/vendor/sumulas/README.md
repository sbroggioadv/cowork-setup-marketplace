# Repertório de súmulas, precedentes qualificados e enunciados — base local de consulta

Súmulas, **temas repetitivos do STJ, temas de repercussão geral do STF**, orientações jurisprudenciais, precedentes normativos e enunciados oficiais convertidos para Markdown e organizados **por tema** (o caminho do agente) e **por fonte** (o caminho pelo número). Base fixa, montada em 2026-09-16: não se recarrega por rotina — só quando o Doc pedir. Não é modelo nem precedente validado: é **texto de referência** para o agente checar o enunciado exato antes de fundamentar. Entrada: [INDEX.md](INDEX.md).

<!-- gerado por automacoes-do-escritorio/sumulas_index.py — não editar à mão -->
Gerado em 2026-09-16 · STF 736 súmulas (portal 2026-09-16) + 63 vinculantes · STJ 676 súmulas (29 canceladas; inteiro teor em 14 lotes; 12 ramos) · STF RG 1482 temas (1300 com tese) · STJ repetitivos 1474 temas (1140 com tese) + 22 IAC · TST 1292 verbetes (2026-09-16) · TJSP 165 súmulas · TRT-15 146 súmulas + teses/OJs · CJF 1777 enunciados · FONAJE 178 enunciados cíveis · índice temático: 13 temas / 208 subtemas.
<!-- fim gerado -->

## Como navegar (agente) — direto ao ponto, sem varrer arquivo grande

1. **Tema sensível (ITBI, holding, terceirização, dano moral, ICMS, franquia…):** `INDEX.md` → seção *Caminho rápido — por tema* → link do subtema em `temas/<tema>.md`. Abra só aquela seção: `grep -n '^## ' knowledge/sumulas/temas/tributario.md` dá a linha de cada subtema; leia com Read a partir dela. Cada linha da seção é um verbete inteiro (fonte + nº + texto); a íntegra com precedentes está no arquivo indicado no fim da seção.
2. **Número conhecido ("Súmula 331 do TST", "Tema 796 do STF", "Tema 1113 do STJ"):** `INDEX-STF-RG.md` / `INDEX-STJ-TEMAS.md` para teses (situação, tese, questão, leading case; íntegra em `stf/repercussao-geral/` e `stj/temas-repetitivos/`, `grep -n '^## STF Tema 796 '`); súmulas: `INDEX-<FONTE>.md`, linha `| 331 |` → íntegra em `tst/sumulas-tst.md` (`grep -n '^## Súmula 331 '`).
3. **Palavra em tudo:** `grep -rin "termo" knowledge/sumulas/INDEX-*.md`.

| Tema | Arquivo | Subtemas (exemplos) |
|---|---|---|
| Tributário | `temas/tributario.md` | ITBI/integralização/holding · ITCMD · ICMS · ISS · IR/CSLL · PIS/COFINS/contribuições · imunidade/isenção · execução fiscal/CDA/sócio · prescrição/decadência · repetição/compensação |
| Societário e empresarial | `temas/societario-empresarial.md` | sócios/quotas/dissolução · desconsideração/grupo econômico · holding/usufruto/bem de família · falência/RJ · títulos de crédito · contratos empresariais/locação comercial · arbitragem · marcas/INPI |
| Franchising | `temas/franchising.md` | franquia/COF/royalties (+ nota sobre a Lei 13.966 e os enunciados do TJSP) |
| Cível | `temas/civel.md` | contratos/cláusula penal · responsabilidade civil/dano moral · prescrição · compromisso de compra e venda/incorporação · locação · posse/propriedade/condomínio · seguros · família e sucessões · juros/correção |
| Consumidor | `temas/consumidor.md` | CDC/fornecedor · negativação/cobrança indevida · planos de saúde/médico · serviços essenciais |
| Bancário | `temas/bancario.md` | contratos bancários/juros/SFH · alienação fiduciária/leasing · fraude/PIX/fortuito interno |
| Trabalhista (Reclamada) | `temas/trabalhista.md` | vínculo/terceirização/grupo · jornada/horas extras · remuneração · rescisão/justa causa/estabilidade · saúde e segurança/dano moral · prescrição/competência · recursos · execução · provas/rescisória/MS · honorários/custas · coletivo/sindicato · servidor celetista/leis municipais · categorias especiais |
| Processo civil | `temas/processo-civil.md` | competência · prazos/intimação · honorários/custas · recursos · REsp/RE/prequestionamento · execução/penhora · tutela/MS · provas · coisa julgada/rescisória/legitimidade · juizados · ações coletivas |
| Administrativo e licitações | `temas/administrativo-licitacoes.md` | licitação/contrato administrativo · servidor/concurso · responsabilidade do Estado/precatório/desapropriação/conselhos |
| Previdenciário · Penal · Imigração · Constitucional | `temas/previdenciario.md` · `temas/penal.md` · `temas/imigracao-internacional.md` · `temas/constitucional.md` | RGPS/benefícios · penal empresarial e penal geral · estrangeiro/extradição/nacionalidade · controle de constitucionalidade |

Cada tema tem subtemas largos (ex.: *Jornada · horas extras…*) e subtemas finos (ex.: *Intervalos · intrajornada · art. 384*; *Terceirização · Súmula 331*; *ITBI · integralização · holding*; *Cláusula de não concorrência*), 208 ao todo — vá no fino quando o assunto é preciso, no largo quando é exploratório. Um verbete pode aparecer em mais de um subtema (classificação por palavras-chave, recall alto): leia o verbete e decida. Verbete *alterado/revisado* fica na lista principal com a marca *(alterada)*; cancelado/superado/revogado vai para a linha final do subtema. O que nenhuma palavra-chave alcançou está em `temas/_sem-tema.md` (poucas dezenas). Localização por número: `grep -n '^## Súmula N'`, `'^## OJ SDI-1 N '`, `'^## Enunciado N'`, `'^## <Jornada> — Enunciado N'`.

## Fontes e datas (o que este retrato cobre)

| Fonte | Origem oficial | Como chega aqui | Arquivo em `fontes/` |
|---|---|---|---|
| STF — súmulas 1-736 e vinculantes 1-63 | portal.stf.jus.br → Jurisprudência → *Aplicação das Súmulas no STF* (bases 30 e 26) | o portal bloqueia curl: `automacoes-do-escritorio/sumulas_stf_portal.js` roda **no navegador do app** e baixa os dois JSON na pasta | `stf-portal-sumulas.json`, `stf-portal-vinculantes.json` (+ `stf-sumulas-ed-2017.pdf`, que só complementa aprovação/referência legislativa/precedentes) |
| STF — temas de repercussão geral 1-1482 | portal.stf.jus.br → Repercussão Geral → Pesquisa avançada → *Exportar Dados* (export oficial: título, descrição, assuntos, situação, tese, datas) | o portal bloqueia curl: no navegador do app, *Exportar Dados* com situação *Todas*; o arquivo cai em Downloads → mover para `fontes/` | `stf-repercussao-geral.html` |
| STJ — temas repetitivos 1-1474 e IAC | processo.stj.jus.br/repetitivos (*Precedentes Qualificados*: tese, questão, NUGEPNAC, delimitação, RG relacionada, processos) | `--baixar stj-temas` (download direto, sem Cloudflare) | `stj-temas-repetitivos.json` |
| STJ — súmulas 1-676 (verbetes + inteiro teor) | scon.stj.jus.br → *Súmulas* (PDFs *Enunciados* e *Inteiro Teor*) | Cloudflare bloqueia download automático: o Doc baixa os PDFs e cola com o mesmo nome | `stj-verbetes.pdf`, `stj-inteiro-teor.pdf` (40 MB) |
| TST — súmulas, OJs e PNs | jurisprudencia.tst.jus.br (API pública `jurisprudencia-backend2`) | `--baixar tst` | `tst-sumulas.json`, `tst-oj.json`, `tst-pn.json` |
| TJSP — súmulas | Biblioteca do TJSP, *Súmulas do Tribunal de Justiça do Estado de São Paulo* (PDF) | `--baixar tjsp` | `tjsp-sumulas.pdf` |
| TRT-15 — súmulas, teses prevalecentes, OJs | trt15.jus.br → Jurisprudência (PDF compilado de súmulas + páginas HTML) | `--baixar trt15` (escolhe o PDF de data mais recente) | `trt15-sumulas.pdf`, `trt15-*.html` |
| CJF — enunciados das Jornadas | cjf.jus.br/enunciados (consulta por jornada) | `--baixar cjf` | `cjf-enunciados.json` |
| FONAJE — enunciados cíveis | fonaje.amb.com.br/enunciados | Cloudflare bloqueia curl: texto colado do navegador do app | `fonaje-civeis.txt` |

Fora do repertório por decisão de 2026-09-16: controvérsias/SIRDR/PUIL do STJ (etapas anteriores à afetação), TNU, CARF, TCU, enunciados do Grupo de Câmaras Empresariais do TJSP (PDF com kerning quebrado — abrir no site), enunciados criminais e da Fazenda Pública do FONAJE.

## Regras de uso

1. **Retrato datado — confirmar vigência na fonte oficial antes de citar.** Súmula/enunciado citado em peça segue o Protocolo Jurisprudencial do `00-PERFIL-MESTRE.md` (nível de confiança explícito). Verbete cancelado fica na base de propósito: serve para reconhecer citação adversa desatualizada.
2. Hierarquia de uso (art. 927 CPC): súmula vinculante e controle concentrado > tese de repercussão geral (STF Tema) e tema repetitivo/IAC (STJ Tema) > súmula STF/STJ/TST > OJ/precedente normativo/súmula regional > enunciado (CJF, FONAJE), que é doutrina qualificada ou orientação — reforço, nunca fundamento único. Tema **afetado/em julgamento/sobrestado** = tese ainda não firmada: cabe pedido de sobrestamento, não citação como tese.
3. Conversão automática: enunciados, títulos, status, órgão e datas vieram íntegros. **Listas de precedentes originários** do STF (PDF 2017) e do STJ (inteiro teor) vieram de layout em colunas e podem estar embaralhadas — para citar precedente, abrir o PDF/portal. As OJs do TRT-15 são texto corrido da página, sem parse por item.
4. Os `.md`, os `INDEX-*.md` e `temas/` são gerados: **não editar à mão.** Para acrescentar um subtema ou palavra-chave, editar `TAXONOMIA` em `automacoes-do-escritorio/sumulas_index.py` e rodar o script sem `--baixar` (não toca nas fontes). Recarga das fontes só sob pedido do Doc:

```bash
python3 automacoes-do-escritorio/sumulas_index.py --baixar tst,tjsp,trt15,cjf,stj-temas
```

STF súmulas: rodar o `.js` no navegador do app (o agente faz via `javascript_tool`) e depois o script sem `--baixar`; STF repercussão geral: novo *Exportar Dados* no portal (navegador) → `fontes/stf-repercussao-geral.html`. STJ súmulas: colar os PDFs novos. FONAJE: colar o texto novo em `fontes/fonaje-civeis.txt` mantendo a linha `FONTE: … coletado em AAAA-MM-DD`. `--sem-anydoc` reaproveita a conversão bruta dos PDFs em `fontes/.cache/` (não versionada).
