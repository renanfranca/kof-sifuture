# Começar: KofMut e sensores do SiFuture

**Transição revisada em 2026-10-25:** documentação e registros consultados no KofMut revisão `a40b20ac37afac302efc2a0dae7702e44720e166`. A entrega atual inclui CLI por fonte e instalação local, aprovação de compatibilidade por conteúdo e comportamento, avaliação preparada em uma JVM de trabalho e documentação EN/PT com guia operacional para LLMs. M4, M5, M6/M6R/M6O e M7/M7R estão concluídos nos respectivos registros; a atribuição forense M6L conserva questões parciais. Esta revisão documental não executa novamente essas provas. A integração dos sensores permanece futura em `/home/renanfranca/projects/kof-sifuture`; **M1 é o primeiro marco pendente** e M1–M5 e S1–S3 dos sensores não estão executados.

Os contratos atuais são a [referência de CLI](/home/renanfranca/projects/kof-mut/docs/cli.pt_BR.md), a [referência JSON v1](/home/renanfranca/projects/kof-mut/docs/report-format.pt_BR.md) e o [guia operacional para LLMs](/home/renanfranca/projects/kof-mut/docs/llm-guide.pt_BR.md). O [EXECPLAN](/home/renanfranca/projects/kof-mut/EXECPLAN.md) e o [índice interno](/home/renanfranca/projects/kof-mut/.agent/README.md) registram decisões, evidências e limitações históricas; não substituem os contratos públicos atuais. A revisão acima é a fonte consultada nesta transição, não prova de adoção ou execução dos sensores no SiFuture.

**Evidência histórica M3F, 2026-10-22:** KofMut baseado em `3b1e0be6a69a30765dc6dcef7cef34e890131bb7`, identificado pelo [manifesto M3F](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m3f.sha256). Check principal e cópia limpa sem Python passaram em 21 contratos/44 testes/15 grupos. Uma rodada conjunta Background.kf + Meteor.kf, SiFuture `82111142c85f98b970ccd65fbf044e492d017729`, commandTimeoutMs=10000/budgetMs=0/maxParallelMutants=4, sem encerramento externo aos 90 s, concluiu em 96.456 s: complete/1, 42 candidatos, 29 Killed, 13 Survived e nenhuma pendência, timeout, erro, descarte ou limitação. Baseline de 114 casos e preservação do original comprovadas. Execução completa aceita, qualidade reprovada pelos sobreviventes. Ver [relatório M3P, seção M3F](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m3p.md). S1–S3 e instalação dos sensores continuam futuros; a meta histórica de 90 s está adiada e não atingida. Naquela rodada, nenhuma otimização adicional foi iniciada.

**Aceitação externa histórica M3, 2026-10-17:** revisão SiFuture `82111142c85f98b970ccd65fbf044e492d017729`, 114 casos canônicos JVM, check detectando erro importado e checkout original preservado. Background: 10.082–10.434 s quentes e 15.242 s com cache vazio, complete/0. Meteor: 85.773–85.777 s, incomplete/3, com Timeout/Pending após 85 s internos, ainda abaixo dos 90 s externos. Não há prontidão geral para ativação diária do tier nesse escopo representativo. Consultar o [relatório M3](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m3.md). A árvore avaliada naquele marco era local, baseada em `37b72ca` mais o manifesto M3; nenhum commit novo foi autorizado naquela execução. Implementação/ativação dos sensores continua no plano próprio.

**Limites da evidência histórica:** as medições M3/M3P/M3F descrevem suas árvores e ambientes datados, não o desempenho da revisão consultada acima. O [incidente de preservação](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m3p.md#preservation-incident-during-the-first-focused-run) perdeu cópias históricas autônomas de JSON/stdout e reutilizou arquivos de observação; seus bytes originais não foram recuperados. O relatório distingue as observações independentes sobreviventes. As otimizações posteriores de [M6O](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m6o.md) foram medidas em fixtures sintéticas e não repetem nem encerram a meta histórica de 90 segundos no projeto real, que continua adiada e não atingida.

Este guia foi criado em 2026-10-15 para permitir iniciar o trabalho pelo Codex CLI sem copiar textos longos. O estado de entrega vigente nesta transição é o da revisão consultada acima; as medições datadas preservam seus resultados e limitações.

**Política atual, 2026-10-22:** Stop mantém `budgetMs: 85000` e cancelamento externo aos 90 segundos. Fechamento (`check` e `check:task`) exige nova rodada com `budgetMs: 0`, sem orçamento global de mutação, sobre toda a entrega, incluindo sessões anteriores. `commandTimeoutMs` continua obrigatório e positivo; `maxParallelMutants` conserva 1..4, padrão 1. Ausente/null/negativo/decimal/exponencial/tipo incompatível em `budgetMs` é inválido, inclusive `0.0`. A primeira rodada completa já foi observada historicamente em M3F; ela não atingiu a meta de 90 segundos. Não instalar sensores nesta atualização documental.

## Ordem de leitura e execução futura

1. Ler as referências atuais de CLI, JSON v1 e operação por LLM, o EXECPLAN e o índice interno do KofMut; conferir a revisão consultada e os limites das evidências.
2. Registrar caminho/configuração e revisão exata do KofMut a consumir, confirmar a instalação concreta de Kof e validar o contrato na sessão de integração.
3. Em sessão futura explicitamente autorizada, abrir `/home/renanfranca/projects/kof-sifuture`, ler suas instruções e o plano dos sensores e executar **M1**, o primeiro marco pendente. Não implementar sensores no repositório do KofMut.

O Termux dá acesso ao Linux atual; não há requisito de executar dentro do Android. Não criar worktree ou subagentes automaticamente. Para implementar KofMut, usar GPT 6.1 Sol com esforço `xhigh`, substituindo a preferência histórica Luna/high, e confirmar a configuração efetiva; escrever o nome do modelo no pedido não muda a sessão por si só.

## Caminhos completos

**Plano 1 — KofMut**

```text
/home/renanfranca/projects/kof-mut/EXECPLAN.md
```

[Abrir o plano vigente](/home/renanfranca/projects/kof-mut/EXECPLAN.md). O [planejamento inicial](2026-10-15_FEATURE_kofmut-exec-plan.md) é histórico; a continuidade segue o EXECPLAN local vigente.

**Plano 2 — Sensores do SiFuture**

```text
/home/renanfranca/.agents/skills/_temporary/codex-skills-ai-context/2026-10-15_FEATURE_sifuture-quality-sensors-exec-plan.md
```

[Abri-lo](2026-10-15_FEATURE_sifuture-quality-sensors-exec-plan.md).

**Este guia**

```text
/home/renanfranca/.agents/skills/_temporary/codex-skills-ai-context/2026-10-15_kofmut-sensors-start.md
```

## O que cada plano entrega

| Plano | Diretório de trabalho futuro | Entrega |
| --- | --- | --- |
| KofMut | `/home/renanfranca/projects/kof-mut` | Ferramenta entregue na revisão consultada, lógica em Kof/JVM, `GPL-3.0-only`, documentação EN/PT, fonte utilizável e instalação local; repositório `renanfranca/kof-mut` |
| Sensores | `/home/renanfranca/projects/kof-sifuture` | Sensores Katacombs adaptados ao projeto e comprovados no Codex CLI, usando KofMut para mutação |

As mutações são alterações em cópias dos arquivos `.kf`. O mutador executa os testes que o projeto configura. Não há exigência de repetir cada mutação em JVM, JS e WASI. A execução do próprio KofMut na JVM é uma decisão independente desse comando de testes.

O piloto Luna high/xhigh já terminou. Não reexecutá-lo, não criar as tarefas antigas nem interpretar instruções históricas como ordem atual. A fonte está em [contexto do piloto](/home/renanfranca/projects/tmp/katacombs-pilot-results/katacombs-piloto-luna-contexto-completo.md).

## Pedidos curtos para o CLI

Depois de abrir o Codex na sessão/modelo desejados, pode-se referenciar somente o caminho do plano com um pedido curto:

```text
Leia o plano neste caminho e execute o primeiro marco ainda pendente.
```

Se quiser executar o plano inteiro, substituir a última parte por “execute o plano, mantendo-o atualizado nos limites dos marcos”. Não é necessário colar seu conteúdo. O executor deve ler o arquivo e as instruções locais antes de alterar qualquer projeto.

**Esse pedido curto, sozinho, não autoriza publicação.** Para publicar KofMut no GitHub, incluir explicitamente no pedido futuro as ações desejadas: criação do repositório público, commits e push. O plano prepara antes uma entrega local revisável. No SiFuture e na memória, não há autorização permanente de commits/push.

## Quando avançar para o segundo plano

A entrega do KofMut já registra comando por fonte/instalado, fixtures detectada/sobrevivente, isolamento, estados inconclusivos, limites de processo e JSON versão 1. Na futura sessão autorizada dos sensores, começar por M1 no `kof-sifuture`: reconferir essas evidências e registrar a revisão exata efetivamente consumida, sem tratar esta atualização documental como validação da integração.

A compatibilidade segue o Kof concreto selecionado no PATH em Linux/JVM, aprovada antes da avaliação por identidade de conteúdo e verificações comportamentais. Não fixar suporte por lista literal de versões nem atualizar/baixar Kof. Preservar a versão efetiva em `kofVersion` e manter a instalação concreta intacta enquanto houver chamadas ativas. Os contratos completos de preparação e recuperação estão na referência de CLI; o prazo próprio de preparação não substitui o teto externo do Stop.

O CLI usa `--report-dir` opcional, padrão `<project>/.kof-mut/reports`, e rejeita `--report`. Cada chamada reserva `<report-dir>/<SHA-256 do caminho canônico do projeto>/<run-id>-<sufixo-único>/report.json` e anuncia `reportPath=<string JSON absoluta>` antes dos comandos. O consumidor deve decodificar e validar o caminho anunciado por sua própria chamada, runId, schema, escopo, contagens e exit; não procurar o arquivo mais recente. Relatórios anteriores são preservados.

O JSON v1 inclui `discardedCandidates`. Rejeições coerentes do frontend/check são descartes fora das contagens e não são Killed; descartes esperados permitem `complete` quando há mutantes aplicáveis e não há erro ou inconclusão. Todos descartados resulta em `no_mutants/3` somente se não houver outra causa de erro ou inconclusão; sintaxe não suportada mantém `incomplete/3`. Descartes não aprovam a qualidade dos testes. Evidência inválida, timeout e erro da ferramenta nunca autorizam descarte ou aprovação. Tempo esgotado, zero testes, forma não suportada ou relatório inválido não são aprovação de qualidade. Um sobrevivente pode exigir melhorar um teste ou analisar equivalência; o plano não autoriza inventar testes sem comportamento diferente.

No Stop, os sensores reservam 85 segundos internos para o KofMut e 90 segundos externos desde o início da invocação completa, com teto de 25 arquivos. Ao esgotar, cancelar e apresentar resultados parciais atuais válidos e pendências; sem relatório válido, informar indisponibilidade sem reutilizar o anterior. No fechamento não há teto de arquivos nem prazo global de 90 s. O escopo explícito inclui toda a entrega sem filtro do ledger; avaliar os bytes finais, antes do commit os preparados para ele. Novos/renomeados usam caminhos finais; remoções ficam nos checks normais; sem produção, registrar ausência de escopo sem alegar rodada completa. `complete/1` conclui a avaliação, mas reprova qualidade por sobreviventes. Liberação de resposta com aviso no Stop não aprova fechamento. Provas S1–S3 do plano dos sensores continuam futuras. O plano dos sensores contém os passos para calibração, provas reais de hooks e encerramento com aviso ao esgotar tentativas.

## Estado e continuidade

O estado de implementação e as evidências do KofMut estão no EXECPLAN local e no índice interno, incluindo M6O, M7 e M7R; os contratos estão nos três guias públicos citados acima. Os guias ampliados M4 já foram entregues e reorganizados por M7. A instalação/ativação dos sensores continua futura; seu próximo passo é M1 no `kof-sifuture`, mediante solicitação explícita. Este guia não autoriza implementação, commits ou publicações.

Registro histórico de 2026-10-15: naquele dia os únicos artefatos eram estes três documentos e sua execução era futura. Esse registro foi substituído pelo estado datado acima, preservando a origem da preferência Luna/high.

Cada ExecPlan é autossuficiente: inclui contexto, decisões, marcos, progresso, comandos previstos e aceitação. As observações já feitas estão identificadas; verificações futuras não estão marcadas como concluídas. Atualizar o respectivo plano na fronteira de um marco ou mudança material, preservando pendências para a sessão seguinte.

**Conferência documental, 2026-10-25:** instruções comparadas com as referências atuais de CLI, JSON v1 e operação por LLM na revisão registrada; links locais e fragmentos conferidos, exemplos de comandos/configuração e escolhas de modelo preservados. Nenhum marco dos sensores foi marcado como executado. Esta conferência não executou sensores, novos benchmarks nem a suíte do KofMut.

**Nota de 31/10/2026:** o `EXECPLAN.md` da raiz do KofMut foi removido em `23c8964` e está arquivado no git: `git -C /home/renanfranca/projects/kof-mut show 6764595:EXECPLAN.md`. Os links acima para `/home/renanfranca/projects/kof-mut/EXECPLAN.md` são históricos. O índice vigente é `/home/renanfranca/projects/kof-mut/.agent/README.md`. O estado consolidado em 31/10 e a decisão de validar M2+ dos sensores com Kof 0.6.4 estão na última seção do plano dos sensores.
