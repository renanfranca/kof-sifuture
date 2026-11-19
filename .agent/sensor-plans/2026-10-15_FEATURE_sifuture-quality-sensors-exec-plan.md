# Adotar sensores Katacombs no SiFuture com KofMut

**Transição revisada em 2026-10-25:** documentação e registros consultados no KofMut revisão `a40b20ac37afac302efc2a0dae7702e44720e166`. A entrega atual inclui CLI por fonte e instalação local, aprovação de compatibilidade por conteúdo e comportamento, avaliação preparada em uma JVM de trabalho e documentação EN/PT com guia operacional para LLMs. M4, M5, M6/M6R/M6O e M7/M7R estão concluídos nos respectivos registros; a atribuição forense M6L conserva questões parciais. Esta revisão documental não executa novamente essas provas. A integração dos sensores permanece futura em `/home/renanfranca/projects/kof-sifuture`; **M1 é o primeiro marco pendente** e M1–M5 e S1–S3 dos sensores não estão executados.

Os contratos atuais são a [referência de CLI](/home/renanfranca/projects/kof-mut/docs/cli.pt_BR.md), a [referência JSON v1](/home/renanfranca/projects/kof-mut/docs/report-format.pt_BR.md) e o [guia operacional para LLMs](/home/renanfranca/projects/kof-mut/docs/llm-guide.pt_BR.md). O [EXECPLAN](https://github.com/renanfranca/kof-mut/blob/67645951a4dbe91246fba400e30a83d97d9ce7ae/EXECPLAN.md) e o [índice interno](/home/renanfranca/projects/kof-mut/.agent/README.md) registram decisões, evidências e limitações históricas; não substituem os contratos públicos atuais. A revisão acima é a fonte consultada nesta transição, não prova de adoção ou execução dos sensores no SiFuture.

**Evidência histórica M3F, 2026-10-22:** KofMut baseado em `3b1e0be6a69a30765dc6dcef7cef34e890131bb7`, identificado pelo [manifesto M3F](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m3f.sha256). Check principal e cópia limpa sem Python passaram em 21 contratos/44 testes/15 grupos. Uma rodada conjunta Background.kf + Meteor.kf, SiFuture `82111142c85f98b970ccd65fbf044e492d017729`, commandTimeoutMs=10000/budgetMs=0/maxParallelMutants=4, sem encerramento externo aos 90 s, concluiu em 96.456 s: complete/1, 42 candidatos, 29 Killed, 13 Survived e nenhuma pendência, timeout, erro, descarte ou limitação. Baseline de 114 casos e preservação do original comprovadas. Execução completa aceita, qualidade reprovada pelos sobreviventes. Ver [relatório M3P, seção M3F](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m3p.md). S1–S3 e instalação dos sensores continuam futuros; a meta histórica de 90 s está adiada e não atingida. Naquela rodada, nenhuma otimização adicional foi iniciada.

**Aceitação externa histórica M3, 2026-10-17:** revisão SiFuture `82111142c85f98b970ccd65fbf044e492d017729`, 114 casos canônicos JVM, check detectando erro importado e checkout original preservado. Background: 10.082–10.434 s quentes e 15.242 s com cache vazio, complete/0. Meteor: 85.773–85.777 s, incomplete/3, com Timeout/Pending após 85 s internos, ainda abaixo dos 90 s externos. Não há prontidão geral para ativação diária do tier nesse escopo representativo. Consultar o [relatório M3](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m3.md). A árvore avaliada naquele marco era local, baseada em `37b72ca` mais o manifesto M3; nenhum commit novo foi autorizado naquela execução. Implementação/ativação dos sensores continua no plano próprio.

**Limites da evidência histórica:** as medições M3/M3P/M3F descrevem suas árvores e ambientes datados, não o desempenho da revisão consultada acima. O [incidente de preservação](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m3p.md#preservation-incident-during-the-first-focused-run) perdeu cópias históricas autônomas de JSON/stdout e reutilizou arquivos de observação; seus bytes originais não foram recuperados. O relatório distingue as observações independentes sobreviventes. As otimizações posteriores de [M6O](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m6o.md) foram medidas em fixtures sintéticas e não repetem nem encerram a meta histórica de 90 segundos no projeto real, que continua adiada e não atingida.

**Origem da reconciliação, 2026-10-17 (histórico):** naquele marco, M1/M1R/M1P/M2 do KofMut estavam entregues e M3 validado localmente, com limitação de custo medida em Meteor.kf. O estado atual do KofMut é o da revisão consultada acima. Esta atualização não implementa nem ativa sensores.

**Política M3F, 2026-10-22:** o registro M3 acima é histórico. A meta de Meteor em 90 segundos está adiada e não atingida. Stop mantém 85 s internos/90 s externos; fechamento exige nova rodada com `budgetMs: 0`, sem orçamento global, sobre toda a entrega. A instalação continua futura. O [EXECPLAN vigente](https://github.com/renanfranca/kof-mut/blob/67645951a4dbe91246fba400e30a83d97d9ce7ae/EXECPLAN.md) e o [relatório M3P](/home/renanfranca/projects/kof-mut/.agent/validation/kofmut-m3p.md) registram implementação/evidências; esta reconciliação não as antecipa.

## Purpose and success

Integrar ao **SiFuture** os sensores de qualidade do Katacombs: estrutura, duplicação, segredos, tipos, testes, mutação e revisão inferencial de design. O agente de implementação será `gpt-6-luna` com esforço `high`, no Codex CLI, com feedback automático e limites de continuação por sessão.

O sucesso observável é uma alteração real provocar o sensor adequado, receber finding com localização e guia, permitir correção e produzir um resultado válido na execução seguinte. O Stop deve executar as verificações na ordem original e solicitar revisão de design quando devida. Sensor configurado, script executado, callback disparado e resultado válido são evidências diferentes e devem permanecer identificadas.

**Estado em 2026-10-25:** plano elaborado em 2026-10-15; nenhum marco dos sensores executado nesta transição e nenhuma instalação iniciada conforme os registros deste plano. M1 é o primeiro marco pendente, em `/home/renanfranca/projects/kof-sifuture`. Este arquivo foi autorizado apenas como documento. Sua execução depende de solicitação explícita futura e do KofMut cumprir o contrato abaixo. Ler o guia ou encontrar estes arquivos não autoriza implementar, criar worktree, fazer commits ou publicar.

## Context and limits

### Repositórios e ambiente

A tabela preserva observações do planejamento de 2026-10-15; versões, revisões e estado limpo do alvo não foram reconfirmados nesta atualização documental. O KofMut entregue foi consultado em `a40b20ac37afac302efc2a0dae7702e44720e166`; M1 deverá conferir o ambiente real do SiFuture antes de implementar.

| Papel | Caminho e revisão observada |
| --- | --- |
| Alvo | `/home/renanfranca/projects/kof-sifuture`, HEAD `82111142c85f98b970ccd65fbf044e492d017729`, limpo |
| Referência | `/home/renanfranca/projects/katacombs-kata-ts`, commit fixado `44cb39c916e9a05de561123d7b13554ee6e0a516` |
| Ferramenta de mutação | `/home/renanfranca/projects/kof-mut`; revisão consultada nesta transição `a40b20ac37afac302efc2a0dae7702e44720e166`, repositório `renanfranca/kof-mut` |
| Kof para pesquisa | `/home/renanfranca/projects/kof`, HEAD `284358f43db885ccd8b52b11f897ac0defec10de`, fonte 0.6.5 |
| Kof instalado | 0.6.4, JVM embutida; não confundir com a revisão das fontes |
| Outros executáveis observados | Node 24.16.0, Codex CLI 0.162.1, Gitleaks 8.30.1 em `/home/renanfranca/.local/bin/gitleaks` |

Termux é o acesso ao Linux, sem requisito de execução no Android. Não reinstalar ferramentas existentes nem atualizar Kof automaticamente. Confirmar novamente versões e PATH, também dentro dos processos reais dos hooks.

O piloto original do Katacombs **já terminou**. O registro exportado (`/home/renanfranca/projects/tmp/katacombs-pilot-results/katacombs-piloto-luna-contexto-completo.md`, não preservado) contém as provas controladas e as execuções high/xhigh. É fonte histórica, não ordem para repetir o piloto. O usuário escolheu Luna high para implementação diária. A comparação foi exploratória, com uma execução por esforço; não prova superioridade geral. A execução high deixou duplicação semântica residual, e os sensores não demonstram que todo teste foi escrito antes do código.

Ler integralmente o [AGENTS.md do SiFuture](/home/renanfranca/projects/kof-sifuture/AGENTS.md) e o [training index do Kof](/home/renanfranca/projects/kof/training/README.md). Antes de decisões Kof, abrir tópicos pertinentes de training, linguagem, learn, implementação e testes. Preferir inglês nas fontes; não inferir Kof de Java/Kotlin/JS. O AGENTS do alvo exige evidências visíveis nas explicações, veda comentários que narrem comportamento/organização e restringe worktrees a pedido explícito.

No Katacombs, ler `AGENTS.md`, `INSTALL.md`, `SENSORS.md`, `.agents/skills/install-sensors/SKILL.md`, `.agents/skills/design-sensor/SKILL.md`, `.codex/hooks.json`, `context/design-charter.md`, `context/mutation-scope.md`, `scripts/` e `test/sensors/`. Usar o commit fixado, não uma versão remota nova. Preservar atribuições MIT dos componentes copiados. O install-sensors orienta a calibração e os primeiros tiers; seu procedimento não instala por si só mutação e design, que este plano inclui explicitamente depois de provar os tiers anteriores.

### Aplicação e evidência prévia

As quantidades, comandos e resultados desta seção são observações históricas do planejamento, a reconferir em M1; não são medições atuais nem marcos dos sensores executados.

Há 24 arquivos de produção em `src/main/kof` e uma suíte canônica de 114 testes em `src/test/kof/sifuture/game/GameJourney.kf`. Os seis maiores arquivos têm 412, 337, 235, 191, 129 e 109 linhas físicas. Linhas físicas **não** equivalem às métricas sem linhas em branco/comentários: não usar esses números como calibração concluída.

Os comandos canônicos vêm de [scripts/kof_project.py](/home/renanfranca/projects/kof-sifuture/scripts/kof_project.py) e [docs/desenvolvimento.md](/home/renanfranca/projects/kof-sifuture/docs/desenvolvimento.md). O wrapper cria uma árvore temporária sem `kof.toml` ancestral, copia as fontes atuais e usa um entrypoint de importação. Preservar esse contrato e a precedência de compilador `--kof` > `KOF` > PATH. Não migrar o layout das fontes neste trabalho.

Durante o planejamento passaram: oito testes Python do wrapper, 114 testes Kof no destino JVM, os mesmos 114 no destino JS e sete jornadas completas de navegador. A soma observada das jornadas foi aproximadamente 3 min 11 s; não é garantia de tempo futuro. Os scripts usaram Chrome 155 e argumentos headless; não inferir necessidade de sessão gráfica apenas de `headless=False`.

Foi observado um falso verde de escopo: `kof check src/main/kof --target js --json` retornou exit 0 com `filesChecked: 0`. Na árvore preparada pelo wrapper, o check retornou `filesChecked: 1`; isso conta a entrada, não prova por si só todos os imports. A nova integração deverá provar rejeição de erro em arquivo importado.

WASI está presente e existe a decisão de torná-lo padrão do frontend, mas a matriz do Kof 0.6.4 instalado ainda recusa seu uso como frontend. Não migrar SiFuture nem presumir que o padrão foi trocado. Essa questão não cria uma exigência de mutação multidestino.

### Fronteiras

Trabalhar no checkout atual, preservando alterações preexistentes e sem worktree/subagentes automáticos. Não invocar implement-approved-plan nem executar uma segunda rotina completa de qualidade em paralelo aos hooks. TDD continua sendo a orientação de implementação; os sensores dão feedback e não comprovam retrospectivamente a ordem teste/código.

Não criar controlador geral, máquina de papéis, automação de commits/PR/CI, pacote compartilhado ou alteração das skills globais. Adaptadores ficam no SiFuture primeiro. A extração reutilizável e a comparação com refactor-design ficam para um planejamento posterior baseado nos resultados; não ampliar o charter nesta instalação.

Não refatorar o jogo inteiro para tornar um relatório verde. Findings preexistentes são dívida visível e não podem ser suprimidos nem aprovados automaticamente. Se impedirem uma etapa de aceitação, registrar a pendência e não chamar essa etapa de concluída. Remover somente probes criados pelo próprio experimento. Segredos usados em probes serão exclusivamente sintéticos.

## Decisions

### Dependência e contrato com KofMut

As referências atuais de [CLI](/home/renanfranca/projects/kof-mut/docs/cli.pt_BR.md), [JSON v1](/home/renanfranca/projects/kof-mut/docs/report-format.pt_BR.md) e [operação por LLM](/home/renanfranca/projects/kof-mut/docs/llm-guide.pt_BR.md) definem o contrato consumido pelos sensores. O [planejamento inicial do KofMut](2026-10-15_FEATURE_kofmut-exec-plan.md) é histórico. O resumo abaixo mantém este plano autossuficiente, sem substituir essas referências.

O KofMut atual é um CLI em Kof/JVM, independente dos sensores, com `toolVersion: "0.1.0"`, utilizável por fonte ou instalação local. A compatibilidade segue o Kof concreto selecionado no PATH em Linux/JVM, aprovada por identidade de conteúdo e verificações comportamentais antes da avaliação, sem lista literal de versões. Preservar a versão efetiva em `kofVersion`; não baixar, modificar nem atualizar Kof. Manter a instalação concreta intacta enquanto houver chamadas ativas. O prazo próprio de preparação do CLI não substitui o teto externo do Stop nem impõe esse teto ao fechamento. Fixar no SiFuture o caminho/configuração e a revisão realmente validada; não consumir um `main` remoto móvel. A revisão consultada nesta transição é `a40b20ac37afac302efc2a0dae7702e44720e166`; sua adoção e provas locais permanecem em M1. Invocação:

```bash
/home/renanfranca/projects/kof-mut/bin/kof-mut run --project /home/renanfranca/projects/kof-sifuture --config kof-mut.json --files /caminho/escopo.json --report-dir /caminho/relatorios --run-id UUID_DA_EXECUCAO
```

O arquivo de escopo é um array JSON de caminhos relativos explícitos, com os arquivos de produção Kof atuais alterados pela sessão. Mutar arquivos inteiros sob `src/main/kof`, incluindo UI e arquivos novos. Não restringir a `sifuture/game`. Arquivos removidos não são mutados, mas continuam na revisão do diff. Caminho ilegível/malformado ou construção não suportada não desaparece do resultado.

Somente no Stop, o escopo segue o original: ledger da sessão intersectado com alterações ainda existentes no worktree; se o ledger não tiver caminhos, usar o fallback de alterações reais do repositório. Arquivos revertidos não ficam pendurados no escopo. Mudança apenas em testes executa testes, mas não remuta automaticamente produção inalterada: registrar essa limitação original; não inventar mapeamento de cobertura.

No fechamento, `check` e `check:task` recebem todo o escopo explícito da entrega, incluindo sessões anteriores, sem redução pelo ledger e sem teto de 25 arquivos. Começar nova execução sobre o estado final; antes do commit, avaliar os bytes preparados para esse commit (inclusive quando worktree e índice diferirem). Novos e renomeados usam caminhos finais; remoções são registradas e verificadas pelos checks normais. Sem produção aplicável, informar ausência de escopo, sem alegar mutação completa. Mudança apenas de testes conserva a limitação de ausência de mapeamento de cobertura.

Configuração Stop do SiFuture em `kof-mut.json`:

```json
{
  "schemaVersion": 1,
  "sourceRoots": ["src/main/kof"],
  "testRoots": ["src/test/kof"],
  "inputs": ["kof.toml", "src", "scripts/kof_project.py"],
  "checkCommand": ["python3", "scripts/kof_project.py", "check", "--target", "jvm", "--json"],
  "testCommand": ["python3", "scripts/kof_project.py", "test", "--target", "jvm"],
  "commandTimeoutMs": 10000,
  "budgetMs": 85000
}
```

No perfil de fechamento, usar a mesma configuração com `budgetMs: 0`. O campo é obrigatório e aceita somente inteiro JSON zero ou positivo; ausente, null, negativo, decimal, exponencial ou tipo incompatível (inclusive `0.0`) é erro. `commandTimeoutMs: 10000` continua positivo e individual; `maxParallelMutants` opcional em 1..4 tem padrão 1. Não aplicar cancelamento externo de 90 s ao fechamento. Todos os candidatos são avaliados salvo erro impeditivo; timeout individual com limpeza confirmada permite continuar. `complete/1` é execução completa com sobreviventes e reprova qualidade, assim como inconclusão reprova o fechamento.

O subcomando `check` do wrapper acima era pendente no planejamento e é requisito a conferir e, se ainda ausente, implementar em M1. O mutador executará somente esse comando de testes configurado; não acrescentará execução em JS/WASI. Os testes normais do projeto em JVM e JS continuam no tier de testes e no fechamento, conforme os comandos canônicos existentes. As sete jornadas de navegador ficam no fechamento da tarefa, não a cada Stop nem a cada mutante.

O JSON do KofMut usa `schemaVersion: 1`, `toolVersion`, `kofVersion`, `runId`, `status`, `scope`, `baseline`, `counts`, `mutants`, `discardedCandidates`, `limitations`, `startedAt` e `durationMs`. Estados de mutante: `Killed`, `Survived`, `CompileError`, `Timeout`, `TestError`, `Pending`; cada item tem id, arquivo, operador, original/substituição, localização, fase, duração e evidência. Em `location`, `line`/`column` começam em 1, `offset` começa em 0 e `length` é positivo; offsets/comprimentos usam unidades UTF-16 da JVM, não bytes UTF-8. Estados gerais: `complete`, `baseline_failed`, `error`, `incomplete`, `no_scope`, `no_mutants`. Exit 0 exige avaliação completa, mutantes presentes, todos detectados por testes e nenhuma limitação; 1 significa avaliação completa com sobreviventes; 2 significa erro/baseline vermelha; 3 significa incompleto ou nada avaliado. Não emitir `NoCoverage` sem instrumentação.

O adaptador fornece um UUID por `--run-id` e seleciona a raiz por `--report-dir` (padrão `<project>/.kof-mut/reports`). Projeto, escopo e raiz relativos são resolvidos pelo cwd; configuração relativa pertence ao projeto. A flag antiga `--report` foi removida e retorna 2 antes de efeitos. Cada chamada reserva exclusivamente `<report-dir>/<project-id>/<run-id>-<sufixo-único>/report.json`, com project-id igual ao SHA-256 hexadecimal completo do caminho absoluto canônico do projeto, sem depender de Git. Antes do primeiro comando do projeto, stdout contém exatamente uma linha `reportPath=<string JSON absoluta>`. Decodificar a string com parser JSON, usar somente o caminho anunciado pela própria invocação e validar arquivo final, igualdade de `runId`, versão do schema, escopo e reconciliação das contagens. O anúncio é uma reserva, não comprovação de conclusão. Não usar arquivo fixo, busca pelo relatório mais recente ou último resultado compartilhado; duas chamadas com o mesmo UUID têm diretórios distintos. O JSON final é publicado atomicamente no mesmo filesystem; ausência/falha de publicação é erro, com relatórios anteriores preservados. `scope` é array de caminhos relativos. `counts` contém inteiros não negativos `candidates`, `executed`, `killed`, `survived`, `compileError`, `timeout`, `testError`, `pending`: `candidates` corresponde ao tamanho de `mutants`, `executed` à soma dos estados exceto `Pending`, e cada outra contagem ao estado correspondente. `baseline` contém `status` (`passed|failed|error`), fases `check`/`test`, códigos, durações e resumo; check traz `filesChecked`, teste traz `executedTests`/`failedTests`. `location` de cada mutante é `{line, column, offset, length}`. `limitations` é array de strings. Conferir campos/tipos obrigatórios e coerência com o exit code. `discardedCandidates` é array obrigatório e separado de `mutants`, com `id`, `file`, `operator`, `original`, `replacement`, `location`, `phase` (`parse|check`), `durationMs` e `evidence`. Rejeições coerentes do lexer/parser/check e alterações indevidas dos demais tokens são descartes documentados e ficam fora de counts; não provam qualidade dos testes. Rejeição de check exige JSON válido, success=false, exit 1 e errorCount positivo reconciliado com os diagnósticos ERROR, com inteiros originais dentro da faixa documentada pelo KofMut. Falha de infraestrutura, evidência inválida/contraditória ou timeout não autoriza descarte. `counts.compileError` continua presente por compatibilidade, zero nas novas execuções. Descartes esperados permitem `complete` com mutantes aplicáveis e sem erro ou inconclusão; todos descartados resulta em `no_mutants/3` somente se não houver outra causa de erro ou inconclusão. Sintaxe não suportada mantém `incomplete/3`. Descartes não aprovam a qualidade dos testes. Qualquer `CompileError` legado, `Timeout`, `TestError` ou `Pending` impede aprovação completa. Não converter erro da ferramenta, timeout, falta de relatório, zero testes ou saída inconclusiva em qualidade aprovada. Descartes coerentes seguem exclusivamente a regra acima. Sobrou sobrevivente? Mostrar local e guia. Possível equivalência fica explícita para análise, sem supressão automática nem teste artificial.

### Arquitetura dos adaptadores locais

Preservar wrappers Node e protocolos do Katacombs; substituir as ferramentas específicas de TypeScript pelas integrações do projeto. Manter `scripts/sensor-guides.mjs` e IDs canônicos, mapeando IDs locais para guias existentes. Novos estados de indisponibilidade precisam de mensagem própria; não falsificar um ID existente com outro significado.

Para Kof, implementar analisador local JVM em `scripts/kof-sensors/`, usando o lexer/parser oficiais para métricas e **PMD CPD 7.17.0 com lexer adaptado aos tokens oficiais de Kof** para duplicação. O adaptador JVM é parte do SiFuture, não do KofMut. Ele não conterá uma segunda gramática. Fixar dependências e instruções de build, incluindo a versão de Kof. PMD em cache não prova o detector: exigir uma prova de duplicação real antes de ativar o tier. Se a API do CPD não viabilizar o adaptador, registrar o resultado e parar esse marco em vez de usar detecção genérica silenciosamente.

A primeira implementação desses adaptadores pode ser Java na fronteira das bibliotecas JVM; a preferência por lógica escrita em Kof é requisito do **KofMut**. Não publicar um novo pacote de análise nesta adoção. Scripts Python continuam na validação existente. Gitleaks executa como ferramenta já disponível.

Não usar jscpd com a configuração original de formatos JS/TS como se cobrisse Kof. Não aceitar relatório de duplicação ausente como zero clones. Cada execução deve registrar arquivos esperados, arquivos efetivamente tokenizados, identificador e resultado; escopo não vazio com zero arquivos analisados é indisponibilidade.

### Calibração e formatação

Antes de fixar thresholds, medir o checkout que será instalado. Gerar inventário por arquivo e função, incluindo métodos, construtores e lambdas, com localização e contagem. Definir explicitamente:

| Métrica | Definição para a porta Kof | Referência original |
| --- | --- | --- |
| Linhas por função | Intervalo da declaração/corpo, sem linhas vazias ou somente comentários; lexer define comentários e strings | 25 |
| Linhas por arquivo | Linhas não vazias, incluindo comentários, como `skipComments: false` da referência | 150 |
| Complexidade | 1 por função + decisões if/loops/catch/case não default/expressão condicional e `&&`/`||`; funções aninhadas têm sua própria conta | 5 |
| Parâmetros | Parâmetros declarados da função/método/construtor/lambda; não contar receiver implícito | 4 |
| Profundidade | Maior aninhamento de estruturas de controle; corpo da função é nível zero; `else if` mantém o nível da cadeia | 2 |
| Statements | Statements do corpo, inclusive estruturas de controle, sem contar blocos delimitadores; função aninhada é medida separadamente | 15 |

Confrontar esses números com `eslint.config.mjs` do commit fixado, que é a fonte normativa da referência. As contagens Kof são definições da adaptação, não uma promessa de equivalência perfeita com AST JavaScript. Em suítes de especificação, preservar as duas exceções originais: linhas por função e statements não são limitados; as demais métricas continuam visíveis. Não criar exclusões automáticas por arquivo problemático.

Regra para o limite inicial de cada métrica: o menor inteiro **não menor que a referência** que deixe menos de vinte findings naquela métrica na base medida. Registrar o valor, contagem com a referência, contagem com o proposto e funções/arquivos afetados. Essa regra define a decisão sem inventar uma distribuição não medida. Manter o limite da referência como direção futura, sem apertá-lo automaticamente a cada execução. Findings existentes permanecem reportáveis; não gerar baseline de supressão.

Duplicação: começar com 50 tokens e 5 linhas, os limiares do detector de referência, usando tokens sem comentários/espaços e sem renomear identificadores. Registrar a distribuição real; não mudar esses valores para esconder clones. Segredos usam a configuração de referência adaptada a caminhos locais, com probes sintéticos e sem valores reais no relatório versionado.

O caminho original de inspeção pode reformatar arquivos. Nesta adoção, manter `kof fmt` como comando explícito até provar validade, idempotência e preservação de comportamento do formatter sobre cópia descartável de todos os arquivos relevantes. Não ativar escrita automática de Kof por um formatter apenas porque o comando existe. A falta dessa prova não permite afirmar que formatação automática foi instalada.

### Eventos, ordem e limites

Manter o manifesto Codex como referência: SessionStart chama `scripts/worktree-baseline.mjs`; PostToolUse chama `.codex/hooks/post-edit-sensor.mjs`; Stop chama **diretamente** `scripts/stop-sensor.mjs`. Não inventar um adaptador Stop ausente no original. Mesclar configuração existente em vez de sobrescrevê-la.

PostToolUse observa depois da edição e fornece findings; não desfaz a ferramenta. Preservar identificação de ferramentas do manifesto e ajustar somente com evidência do CLI real. SessionStart não significa criar um novo Git worktree: apenas registra a referência do checkout atual.

No Stop: baratos → tipos → testes → mutação → revisão de design quando devida. Não iniciar testes caros se os baratos/tipos falharem; não iniciar mutação com testes vermelhos. Manter até três bloqueios comportamentais distintos por sessão, deduplicação por conjunto de findings, até dois pedidos de revisão de design e tratamento de `stop_hook_active` quando fornecido. Ao esgotar, encerrar com aviso e pendências; o resultado não se torna PASS.

Preservar orçamento de testes de 120 s e orçamento externo da mutação de 90 s. KofMut recebe 85 s para reservar finalização e limpeza dentro do teto externo. Preservar teto de 25 arquivos de produção somente no Stop e timeout Stop de 300 s. Não truncar escopo acima do teto: avisar que a avaliação não foi realizada. No Stop, ao esgotar o prazo, cancelar. Havendo relatório atual válido, expor resultados conhecidos e pendências. Sem relatório válido, informar indisponibilidade; preservar o anterior sem usá-lo como atual. A política de fechamento com zero é uma decisão explícita, independente das medições históricas.

Liveness/doctor devem informar configuração e sinais de execução, não emitir certificado de qualidade de todo o código. Não atribuir à instalação atual a evidência de callbacks do piloto no app. Provar o CLI nesta instalação. A aprovação/confiança de hooks segue o mecanismo efetivamente disponível no Codex instalado, sem contorno automático.

### Revisão inferencial preservada

Manter as doze perguntas originais: localização; responsabilidades; duplicação semântica; mudança espalhada; nomes; invariantes escondidas em primitivos; testes como especificação; dificuldade de testar; comentários sobre o quê; decisões e seus motivos; documentação falsa; documentação que repete código.

Aplicar os filtros originais antes de reportar: complexidade essencial, restrição externa, pressão real de evolução e questão decidível pelo tier barato. Priorizar impacto/esforço e registrar no máximo cinco findings. Validar cobertura dos arquivos do escopo, categoria 1–12, local existente e conteúdo de `what`, `why`, `instead`. Isso valida o registro, não a qualidade do julgamento do modelo.

Registrar antes de corrigir. Não retirar ferramentas de edição durante a revisão e não acrescentar exigência de hashes dos arquivos: o charter adia essa exigência por risco de deadlock após correção legítima. Não exigir outro modelo revisor; Luna high realiza a revisão dentro do protocolo existente.

## Milestones

### M1 — Conferir dependência, medir e preparar proposta local

**Primeiro marco pendente; não executado.** Trabalhar em `/home/renanfranca/projects/kof-sifuture`, após solicitação explícita para implementar sensores. A atualização documental de 2026-10-25 não executou nenhuma etapa abaixo.

Confirmar instruções, checkout e ferramentas. Ler os resultados do piloto sem executá-lo de novo. Conferir versão/revisão do KofMut e executar suas fixtures detectada/sobrevivente; ausência de ferramenta ou contrato incompleto impede ativar a mutação, sem substituir por outro motor.

Preparar em `scripts/kof-sensors/` o leitor do frontend e o adaptador CPD, com testes de métricas e tokens por exemplos comportamentais mínimos. Registrar o inventário e a tabela de calibração em `.agent/validation/sensor-calibration.md`; dados detalhados ficam em `.agent/tmp/`. O inventário medido e os valores calculados devem acompanhar a entrega antes de qualquer declaração de calibração concluída.

Adicionar ao wrapper o subcomando `check --target jvm|js --json`, preservando comandos e precedence existentes. Usar árvores temporárias como as atuais, executar o check oficial e validar seu JSON. Provar erro em fonte importada, entrada ilegível e zero arquivos. `filesChecked: 1` não pode ser descrito como 24 arquivos individualmente contabilizados. Estender os testes do wrapper para as novas condições e preservar os oito testes existentes.

Validação futura: `python3 -m unittest discover -s tests -p 'test_*.py'`, checks do analisador local e `python3 scripts/kof_project.py check --target jvm --json`. Nenhum finding deve desaparecer por supressão ou caminho não analisado.

### M2 — Sensores baratos e guias

Copiar somente os módulos e guias necessários do Katacombs para `scripts/` e as referências locais do design-sensor. Manter atribuição e anotar alterações de linguagem/runtime. Criar comandos estáveis em `package.json`: `lint:sensor`, `dup:sensor`, `secret:sensor`, `docs:sensor`, `behavior:sensor`, `behavior:report`, `design:scope`, `design:review`, `design:report`, `sensors:doctor`, `check` e `check:task`.

O `npm run check` executará os sensores baratos, check de tipos, testes do wrapper, testes Kof JVM/JS, mutação completa com `budgetMs: 0` para todo o escopo explícito da entrega e relatório do estado de design. Fora de sessão, sem escopo de mutação, informar SKIP e não alegar avaliação completa; permitir fornecer escopo pelo comando behavioral. A revisão inferencial continua sendo realizada/registrada pelo modelo, não simulada pelo comando.

`npm run check:task` acrescentará as sete jornadas de navegador ao fechamento. Não instalar Vitest/Stryker/TypeScript apenas para manter comandos fictícios. Usar `node --test` para os testes dos wrappers de sensores, com asserções sobre comportamento público. Testes dos adaptadores JVM ficam junto de `scripts/kof-sensors/` e não entram no catálogo de testes do jogo.

Provar individualmente cada regra estrutural, clone com pelo menos 50 tokens/5 linhas e segredo sintético, observando detector, localização, ID canônico, guia e desaparecimento do finding depois de remover o probe. Quando houver dívida preexistente, comparar findings específicos do probe; não declarar o projeto inteiro verde. Não avançar um tier indisponível ou uma prova inconclusiva como se estivesse concluída.

### M3 — Hooks reais no Codex CLI

Adicionar/mesclar `.codex/hooks.json`, baseline/ledger e adaptador PostToolUse, preservando os scripts e protocolos originais. Iniciar uma nova sessão Codex CLI no checkout com Luna high para que SessionStart possa ser observado. Registrar modelo/esforço efetivos, versão do CLI e PATH efetivo de Node/Kof/Gitleaks no processo do hook.

Fazer edição de probe e observar callback real PostToolUse. Corrigir/remover somente o probe e observar nova execução. Demonstrar que um comando de leitura não produz modificação e que edição externa coberta pelo watcher aparece no escopo. Separar a invocação real do CLI de testes que apenas alimentam payloads sintéticos nos scripts.

Depois observar Stop com baratos/tipos/testes vermelhos e confirmar a ordem. Provar testes JVM/JS verdes antes de integrar mutação. Não mudar o runtime para o app nem substituir sessões por subagentes se a observação no CLI falhar; registrar o que ocorreu e a etapa não verificada.

### M4 — KofMut, revisão de design e limites

Adicionar `kof-mut.json` e o adaptador de chamada/relatório, com revisão fixa da ferramenta e metadados por execução. Usar o contrato deste documento, mapear sobreviventes para `mutant-survived` e expor estados inconclusivos como indisponibilidade/pendência. Não transformar timeout em detecção por teste, mesmo que a referência Stryker agrupe timeout em sua contagem de detectados; essa distinção foi escolhida explicitamente para esta porta.

Provar, em cópia descartável quando necessário, mutação detectada, sobrevivente, descarte coerente do compilador, evidência inválida sem descarte, falta de relatório, relatório anterior preservado e esgotamento de orçamento. O original não deve receber mutações. Incluir prova num arquivo fora de `game`, sem exigir uma afirmação de cobertura inexistente: se os testes não distinguirem a variante da UI, o resultado correto é sobrevivente ou limitação documentada, nunca exclusão silenciosa desse arquivo.

Provar revisão ausente, registro inválido e válido, cobertura do escopo, categorias e máximo de cinco findings. Exercitar deduplicação, três bloqueios comportamentais, dois pedidos de design e aviso final. S1: Stop com prazo esgotado cancela e distingue relatório parcial atual válido de indisponibilidade sem reutilizar resultado antigo. S2: em sessão isolada, findings A, A, B, C, D bloqueiam A, liberam repetição de A com aviso, bloqueiam B e C e liberam D com aviso; o veredicto permanece reprovado e não libera a qualidade do fechamento. Fazer testes determinísticos dos limites em sessão descartável para não gastar o orçamento da sessão de aceitação; quaisquer limites observados somente por payload sintético ficam assim identificados.

### M5 — Fechamento e documentação de uso diário

Documentar comandos, configuração por projeto, evidências por sensor, limites e recuperação em `SENSORS.md` e `docs/desenvolvimento.md`. Ajustar AGENTS apenas nas orientações necessárias para o uso local, preservando seu contrato de pesquisa Kof e sem introduzir outro controlador. Não criar uma segunda rotina completa concorrente de validação.

Executar `npm run check:task`: checks dos sensores/adaptadores, testes Python, testes Kof, nova mutação com `budgetMs: 0` de todo o escopo explícito da entrega, sem teto de 25 arquivos nem encerramento externo aos 90 segundos, revisão registrada quando devida e as sete jornadas abaixo. Registrar estado real de cada tier; se houver dívida ou avaliação incompleta, a aceitação correspondente fica pendente. Não publicar código nem criar commits/PRs neste plano sem pedido explícito.

S3: preparar 26 arquivos de produção incluindo alteração de outra sessão, novo e renomeado; exigir todos os caminhos finais e bytes correspondentes à entrega, nova execução sobre o estado final, sem redução pelo ledger nem cancelamento de 90 s. Remoções devem aparecer nos checks normais. Comprovar primeiro nos testes dos adaptadores e depois nos hooks reais; payloads sintéticos não comprovam integração. S1–S3 continuam pendentes até essas provas.

Atualizar `.agent/validation/sensors-adoption.md` com SHA inicial e estado final do checkout, versões, modelo/esforço, comandos, resultados, exemplos falha → feedback → ação → resultado, provas reais/sintéticas e pendências. Não registrar transcrições integrais, respostas geradas de modelo ou segredo sintético como se fosse credencial utilizável. Evidência bruta em `.agent/tmp/`, com exclusão local exatamente uma vez conforme AGENTS.

## Progress

M1–M5 dos sensores permanecem pendentes. As entregas registradas do KofMut e as medições históricas citadas não concluem marcos deste plano.

- [x] Escopo, runtime, modelo, limites e contrato KofMut definidos no plano.
- [x] Fatos de ambiente e provas anteriores separados de verificações futuras.
- [ ] M1 — Dependência pronta, métricas medidas e check confiável.
- [ ] M2 — Sensores baratos com probes e guias comprovados.
- [ ] M3 — Callbacks reais do Codex CLI comprovados.
- [ ] M4 — Mutação, design e limites comprovados.
- [ ] M5 — Fechamento, documentação e aceitação reconciliados.

## Validation

Os comandos a seguir são verificações futuras da instalação; os resultados observados durante o planejamento constam em Context e não validam código ainda inexistente.

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/kof_project.py check --target jvm --json
python3 scripts/kof_project.py check --target js --json
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
npm run check
npm run check:task
node --test test/sensors/*.test.mjs
```

O script `check:task` deverá executar, no fechamento e sem duplicar sua execução dentro de cada mutante:

```bash
python3 tests/browser.py
python3 tests/browser_controls.py
python3 tests/browser_meteor.py
python3 tests/browser_weapons.py
python3 tests/browser_stage.py
python3 tests/browser_subchief.py
python3 tests/browser_boss.py
```

| Critério | Prova necessária e resultado esperado |
| --- | --- |
| Calibração | Seis distribuições, definições e limites calculados; dívida existente enumerada, sem supressão |
| Estrutura | Probe por métrica recebe finding localizado e guia correto; exclusões de testes são as documentadas |
| Duplicação | Clone Kof real é detectado pelo CPD; metadados reconciliam escopo; relatório ausente não vira PASS |
| Segredos | Credencial exclusivamente sintética é detectada; ferramentas estão no PATH real do hook |
| Tipos | Erro deliberado em fonte importada impede avanço; zero arquivos/JSON inválido falham explicitamente |
| Testes | Caso vermelho impede mutação; zero testes não conta como verde |
| Mutação | Escopo é produção alterada, inclusive fora de game; KofMut preserva original e fornece estados válidos |
| Design | Ausência solicita revisão; registro inválido não é aceito; registro válido cobre o escopo e respeita o charter |
| Callbacks | Evidência de SessionStart, PostToolUse e Stop reais no CLI; execução direta não recebe esse rótulo |
| Ordem e limites | Tiers caros só avançam após os anteriores; deduplicação e limites evitam repetição infinita; aviso mantém pendências |
| Relatórios | Resultado pertence à execução atual; schema/contagens/escopo inválidos impedem aprovação |
| Fechamento | Jornadas completas rodam uma vez no fechamento; revisão, resultados e lacunas ficam no registro de aceitação |

Conferir a correção da expectativa de cada critério separadamente da suficiência de sua prova. Cada linha recebe comando/procedimento, resultado observado e arquivo de evidência ou lacuna; não substituir essa auditoria pela frase “testes passaram”. Não chamar a adoção inteiramente verificada se um callback ou tier requerido não foi comprovado.

Atualizar o plano somente na criação, nos limites de marco, em mudança material de direção e antes do handoff. Recuperação: desativar apenas as entradas dos hooks adicionadas por esta instalação se ela impedir trabalho, preservar configuração anterior, relatórios e causa; não apagar probes/arquivos que pertençam ao usuário, não afrouxar sensores para produzir verde.

**Conferência documental, 2026-10-25:** instruções comparadas com as referências atuais de CLI, JSON v1 e operação por LLM na revisão registrada; links locais e fragmentos conferidos, exemplos de comandos/configuração e escolhas de modelo preservados. Nenhum marco dos sensores foi marcado como executado. Esta conferência não executou sensores, novos benchmarks nem a suíte do KofMut.


## Continuidade executada: M1 dos sensores em 2026-10-25

Esta seção atualiza o progresso e a validação após autorização explícita para executar apenas o M1 no checkout atual. Todo o conteúdo anterior foi conservado byte a byte como histórico; as declarações anteriores de M1 pendente descrevem os momentos ali datados. Não se declara M2–M5 ou S1–S3 executado.

### Progress do M1

- [x] Checkout SiFuture inicialmente limpo, base `82111142c85f98b970ccd65fbf044e492d017729`, branch `sensor-calibration-m1`, sem worktree/subagentes/commit/PR/publicação.
- [x] KofMut limpo na revisão prevista `a40b20ac37afac302efc2a0dae7702e44720e166`, Kof instalado 0.6.6 e jar SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`; detected e survived repetidos em cópias externas com complete/0/Killed e complete/1/Survived, baseline e hashes comprovados.
- [x] `check --target jvm|js --json` implementado no wrapper, com validação de schema/contagens/exits, diagnósticos originais, import com erro e isolamento comprovados.
- [x] Módulo Maven em `scripts/kof-sensors/`: lexer/parser do jar oficial, CPD 7.17.0, inventário e testes de métricas/localizações/limites/clones/falhas.
- [x] M1 — Dependência pronta, métricas medidas e check confiável. Escopo medido integralmente: 25 arquivos, 321 unidades, 45.443 tokens, sem falhas de tokenização; 17 grupos CPD a 50 tokens/5 linhas. Propostas mínimas: linhas/arquivo 150, linhas/função 25, complexidade 16, parâmetros 4, profundidade 3, statements 17. Há 5 findings de arquivo e 10 de função, todos com triagem e evidência de design, sem refatoração para cumprir contagens.
- [ ] M2–M5 e S1–S3: permanecem pendentes. Sensores não ativados; dívida não suprimida nem aprovada; guias e referência Katacombs preservados.

### Validation observada do M1

Comandos na raiz do SiFuture, sobre a base acima mais diff local não commitado: `python3 -m unittest discover -s tests -p 'test_*.py'` (14 testes, exit 0); `mvn -f scripts/kof-sensors/pom.xml test` (12 testes, exit 0); checks JSON JVM e JS (exit 0, success true, filesChecked 1, errorCount 0); testes Kof JVM e JS (114 casos por alvo, zero falhas, exit 0); `scripts/kof-sensors/run .` (exit 0, 25/25 arquivos); `scripts/kof-sensors/verify-kofmut` (exit 0 do qualificador, verificando exits 0 e 1 da ferramenta). Limites CPD exatos 50 tokens/5 linhas detectam; 49 tokens ou 4 linhas não. Proposta de calibração admite 19 findings, não 20, e o inteiro anterior foi conferido quando acima da referência.

Os [registros de adoção](/home/renanfranca/projects/kof-sifuture/.agent/validation/sensors-adoption.md) associam cada critério a procedimento, resultado, assertion e limites da prova. O [inventário e calibração](/home/renanfranca/projects/kof-sifuture/.agent/validation/sensor-calibration.md) inclui distribuições completas, todos os locais afetados e a triagem de cada finding de tamanho, distinguindo contagem de decisão de separação. Os três construtores longos têm complexidade 1 e continuam findings; nenhuma fórmula condiciona tamanho à complexidade. GameJourney mantém incerteza explícita de design.

Preservação: hashes dos 44 arquivos originais em src/tests inalterados; histórico do EXECPLAN do SiFuture e deste plano externo preservado como prefixo; exclusão local de `/.agent/tmp/` exatamente uma vez. Logs, inventário JSON e relatórios individuais ficam em `.agent/tmp/sensors-m1/` como apoio opcional, sem substituir os sumários preparados para versionamento. Nenhuma jornada de navegador ou meta de desempenho do jogo foi reexecutada, pois o M1 não modificou comportamento/apresentação nem ativou tiers. A qualificação do KofMut é limitada às duas fixtures e à instalação concreta identificada.

## Continuidade do reparo de localização do M1 — 25/10/2026

Após a revisão da base `0f8de0670a57027145019305220d10fe8964ef65`, duas regressões do adaptador foram reproduzidas: a declaração de métodos com retorno `List<Int>`/`Int[]` não era localizada, e uma chamada a `new Box(...)` dentro do construtor podia ser escolhida como o início da declaração. Esta continuação mantém os resultados do M1 e corrige essas localizações no SiFuture. As declarações anteriores de M1 pendente são registros históricos; M1 continua concluído, com este reparo de aceitação associado.

`Spans.declarationStart` agora acumula tokens oficiais em ordem inversa e compara cada fragmento com o sufixo do tipo de retorno completo; isso cobre genéricos e sufixos de array sem enumerar tipos permitidos. `constructorName` associa candidatos ao nome, às posições dos parâmetros do AST oficial e ao bloco de corpo balanceado que termina antes da posição do node. A chamada interna não tem a forma delimitada de uma declaração e deixa de ser confundida com a assinatura. A regra operacional está coberta para retorno antes/depois dos parâmetros e cabeçalho em uma/duas linhas, e para construtor explícito/nomeado, incluindo sobrecarga na mesma classe.

Prova RED/GREEN: contra `Spans.java` da revisão, quatro testes falharam como esperado: tipo genérico sem localização e início de construtores na linha da chamada. Com a implementação corrigida, os 18 testes Maven passaram. O check oficial Kof 0.6.6 aceitou os 12 formatos de assinatura e os dois construtores recursivos em JVM/JS. As assertions do `Analyzer.measure` fixam linhas, coluna, fim, contagem de linhas, complexidade, parâmetros, profundidade e statements; a CLI explicitamente escopada encontrou os exemplos sem falhas e conservou o intervalo de `main`.

Validação atual do SiFuture na branch `sensor-calibration-m1`, base revisada `0f8de0670a57027145019305220d10fe8964ef65`: 16 testes Python; 18 Maven; checks wrapper aprovados nos dois alvos; 114 testes Kof sem falhas em cada alvo. A nova medição completa mantém 25/25 arquivos analisados/tokenizados, 321 unidades, 45.443 tokens e 17 grupos CPD. Comparação por arquivo e unidade com o inventário M1 preservado encontrou zero alterações. KofMut permaneceu limpo na revisão `a40b20ac37afac302efc2a0dae7702e44720e166`; nenhuma validação de produto KofMut foi refeita.

Detalhes do critério e da suficiência das provas estão no [registro de aceitação do SiFuture](/home/renanfranca/projects/kof-sifuture/.agent/validation/sensors-adoption.md) e na [calibração](/home/renanfranca/projects/kof-sifuture/.agent/validation/sensor-calibration.md). Evidência bruta e o snapshot pré-continuidade deste arquivo estão em `/home/renanfranca/projects/kof-sifuture/.agent/tmp/sensors-m1-repair-20261025-continuation/`; o sumário versionado permanece suficiente sem esses logs.

M2–M5 e S1–S3 continuam pendentes. Sensores não ativados, decisão de bloqueio por tamanho aguardando M2, limites e exceções preservados. Não houve alteração de fontes ou suítes do jogo, implementação KofMut, worktree, subagente, commit ou publicação. Formas futuras do frontend continuam exigindo prova própria.

## Continuidade: associação de construtores sem parâmetros — 25/10/2026

Na base SiFuture `47854206fab1c8868b3294062b1a198bf81e0f67`, a lacuna restante de M1 foi corrigida em `Spans.constructorName`: a busca aceita somente a assinatura cujos parâmetros casam com o AST e cujo corpo balanceado termina exatamente no token imediatamente anterior à posição final do node oficial. Uma chamada `new Box()` no corpo deixa de ser confundida com a assinatura vazia; chamadas com argumentos e blocos internos também não deslocam o fechamento do construtor. O RED observou a linha 3 em vez da linha 2 para o construtor vazio com chamada interna e bloco posterior.

A matriz API fixa literalmente os dois estilos (`constructor` e nome da classe), zero e um parâmetro, e corpos vazio, chamada isolada e chamada seguida de `if` (12 combinações). Os dois probes principais também exercitam `new Box()` e `new Box(1)`: esperado e observado para a declaração é linha 2, coluna 5, fim 5, quatro linhas, zero parâmetros, complexidade 2, profundidade 1 e três statements. A CLI com arquivo incluído explicitamente publica o mesmo intervalo; o auxiliar e `main` mantêm linhas 6 e 8. Os checks oficiais Kof 0.6.6 aceitam o probe em JVM e JS.

Validação na branch atual: Python 16 testes OK; Maven 21 testes, zero falhas/erros/skips; check wrapper JVM/JS aprovado; testes Kof JVM/JS, 114 casos por alvo sem falhas; CLI dos sensores sucesso. A medição integral permaneceu em 25 arquivos, 321 unidades, 45.443 tokens e 17 grupos CPD. Comparação arquivo/unidade com `.agent/tmp/sensors-m1-repair-20261025-continuation/inventory.json`: nenhum arquivo adicionado/removido e zero métricas alteradas. Identidade do Kof: versão 0.6.6, jar SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`. KofMut e dependência não mudaram; a qualificação anterior foi reutilizada.

Registros de aceitação e calibração atualizados no checkout SiFuture. Evidência de execução opcional em `.agent/tmp/sensors-m1-zero-arg-constructor-review/`. O escopo de M1 preserva jogo, limites, guias, exceções e decisão de bloqueio por tamanho. M2–M5 e S1–S3 continuam pendentes; nenhum worktree, subagente, commit ou publicação foi criado.

## Continuidade: validação do compilador na matriz de construtores — 25/10/2026

Na revisão SiFuture `47854206fab1c8868b3294062b1a198bf81e0f67`, ampliei `AnalyzerTest` para que cada uma das 12 fontes da matriz passe pelo `kof check --target jvm --json` e `--target js --json` antes de ser medida. Uma só String é gravada para o compilador e fornecida ao `Analyzer.measure`. Chamadas internas correspondem à assinatura: `new Box(value)` para `(Int value)` e `new Box()` para `()`.

RED: antes da correção, as duas combinações parametrizadas com chamada interna sem argumento falharam nos dois alvos com `SEM023`, zero argumentos recebidos e um esperado; outras dez fontes passaram. GREEN: corrigidas as chamadas, as 12 fontes passaram em JVM e JS com exit 0, `success=true`, zero erros e nenhum ERROR. A expectativa de medição permanece linha 2/coluna 5, fim e contagens literais conforme corpo, parâmetros 0/1, complexidade 1/2, profundidade 0/1 e statements 0/1/3. A fixture com dois construtores e `main` exige exatamente três unidades com intervalos 2–5, 6–6 e 8–8.

Validação: Python 16 testes; Maven 21; checks gerais Kof aprovados nos dois alvos; 114 testes Kof por alvo; inventário de sensores aprovado. Comparação por arquivo e unidade: 25 arquivos, 321 unidades, 45.443 tokens e 17 grupos CPD, sem alterações. Jar Kof 0.6.6 SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`. KofMut permanece na revisão limpa `a40b20ac37afac302efc2a0dae7702e44720e166`, qualificação anterior reutilizada. Registros detalhados: [aceitação do SiFuture](/home/renanfranca/projects/kof-sifuture/.agent/validation/sensors-adoption.md#continuidade-compilador-e-medição-da-matriz-de-construtores--25102026) e [calibração](/home/renanfranca/projects/kof-sifuture/.agent/validation/sensor-calibration.md#continuidade-da-verificação-oficial-da-matriz-de-construtores--25102026); evidência opcional em `.agent/tmp/sensors-m1-measurement-closeout-20261025/`.

A gramática atual exige bloco no construtor explícito. Construtores explícitos sem corpo seguem fora do escopo; classe sem construtor declarado mantém a síntese padrão zero-argumento. Este marco fecha a confiabilidade da medição, não decide a política de avisos/bloqueios. Nenhum gatilho foi instalado, sensores não foram ativados e contagens não se tornaram bloqueios. M2–M5 e S1–S3 permanecem pendentes.

### Retificação documental: construtor explícito sem corpo

Esta retificação substitui a afirmação imediatamente acima de que a gramática local exige bloco e de que construtores explícitos sem corpo seguem fora da sintaxe implementada. A produção em `grammar.md` inclui `block`, mas o documento se identifica como descrição do parser, não como especificação que o parser deva seguir. A evidência registrada em `.agent/tmp/sensors-measurement-closeout-review-2v71lv9r/documentation-discrepancy.txt` mostra `kof check` aceitando `constructor()` sem corpo em JVM e JS (`success=True`, `errorCount=0`); o medidor rejeita o exemplo com `Cannot locate constructor body end for Box`. O check demonstra aceitação e checagem, não execução do programa. A intenção dessa aceitação pelo Kof permanece em aberto. Versão 0.6.6 e SHA-256 do jar permanecem iguais aos registrados. A documentação oficial do Kof não foi alterada.

## Continuidade aprovada: uso manual do KofMut no SiFuture — 26/10/2026

Esta decisão executa o recorte manual solicitado para o checkout SiFuture, preservando o histórico dos marcos do plano. Criar a configuração e o escopo explícito, usar o KofMut existente sem atualização automática e chamar o wrapper do projeto pelo `PATH`. Checks e testes manuais cobrem JVM e JS; a mutação do KofMut usa JVM e concorrência 1. Nenhum gatilho intercepta edições ou commits. O medidor de linhas/complexidade continua manual. Não adicionar adaptador de relatórios: usar diretamente o CLI e o caminho `reportPath` anunciado pela execução corrente.

A nova configuração fixa `commandTimeoutMs=10000` e `budgetMs=0`. Qualidade só é aprovada quando KofMut termina `complete/0` para o escopo explícito. `complete/1` com sobrevivente reprova; baseline/ferramenta reprovados retornam 2; incompleto, sem escopo ou sem mutantes retorna 3 e não aprova. Identidade de execução, relatório corrente, scope, baseline, contagens, exit e hashes precisam concordar.

Validação em `sensor-calibration-m1`, base `373ad9eaf99dbb3171a6503f630c23d2124a17bc`: Kof 0.6.6; KofMut 0.1.0 limpo em `a40b20ac37afac302efc2a0dae7702e44720e166`. Checks JVM/JS JSON e testes 114/114 passaram nos dois alvos; 16 testes Python passaram. As fixtures descartáveis detectada/sobrevivente produziram `complete/0` com `Killed` e `complete/1` com `Survived`. Erro de fonte e teste falho produziram `baseline_failed/2`, sem mutantes. `Background.kf` inteiro executou com baseline aprovado, 114 testes, um candidato `Killed` e `complete/0`. Vinte e cinco hashes de fontes/testes `.kf` ficaram idênticos antes/depois.

Os resultados e a auditoria de expectativa versus suficiência estão em `/home/renanfranca/projects/kof-sifuture/.agent/validation/sensors-adoption.md#continuidade-kofmut-manual--26102026` e `EXECPLAN.md#continuidade-uso-manual-do-kofmut--26102026` no SiFuture. O aceite é limitado ao arquivo real avaliado e ao catálogo atual de uma suíte. O wrapper emite um resumo final por arquivo de suíte; o leitor atual do KofMut rejeita um segundo resumo. Não omitir suítes se o catálogo crescer: refazer a prova de compatibilidade. M2–M5 e S1–S3 continuam pendentes; nenhum sensor ou gatilho foi ativado.


## Continuidade: receita manual corrigida e aceite completado — 26/10/2026

Entrega documental no SiFuture, base `4e7d03f9f2f3fa5ef9e3e5549a5be9f06616ba51`, branch `sensor-calibration-m1`, preservando integralmente o histórico acima. Os guias inglês/português agora executam da raiz SiFuture, invocam o KofMut externo, persistem stdout/stderr/código nativo em arquivos por UUID e devolvem esse código depois da apresentação. O identificador permanece no shell pai; execução e inspeção encerram somente seus subshells; falhas próprias de evidência devolvem 2. A inspeção consulta apenas o relatório anunciado pela chamada, com `runId` correspondente, sem apagar arquivos anteriores.

Blocos extraídos literalmente dos dois guias: retornos 0/1/2/3 e arquivo `.exit` conferidos nas duas receitas e idiomas; também 42/130/143. Permissão negada, `/dev/full`, leitura/apresentação e registros/relatórios inválidos devolvem 2. Oito sessões com pseudoterminal real comprovam retorno, identificador e terminal disponível. Verificador local: 138 observações aprovadas (96 verificações e 42 preparações). Sete controles defeituosos confirmam a capacidade de distinguir a falha: trecho antigo/ausência do `exit` final retorna 0 para nativo 1; falhas ignoradas de evidência produzem falso verde; `exit` no pai impede consulta posterior. `bash -n`: 16 blocos aprovados; links locais e novos fragmentos conferidos; 21 destinos externos dos guias com HTTP 200 e linhas existentes; `git diff --check` exit 0. Nenhuma suíte nova foi versionada.

Provas reais reutilizadas após conferir configuração, saídas, UUIDs, relatórios, contagens e logs: detecção `0da16a7a-4738-42ff-a196-611c0c9761b4` complete/0/1 Killed e sobrevivência `51a4b838-0692-4fae-8857-560d2f49a564` complete/1/1 Survived, ambos com baseline 115/0; erro de fonte `9ef127fe-f978-4d92-9206-b7576ba007b5` e teste falho `048023bb-fcc7-476b-b747-c0d9c7f2519a`, baseline_failed/2 sem mutantes. Configuração real SHA-256 `2e24df1360b021bbf30d4cf4f7fdcdcf1cec202d601a45b018c61b65d8fda9bd`; KofMut 0.1.0 limpo em `a40b20ac37afac302efc2a0dae7702e44720e166`; Kof 0.6.6, jar SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`. Não foram repetidas avaliações de mutação.

Limitação confirmada, mantida para trabalho separado: duas suítes executam 115 testes/0 falhas e retornam 0, mas KofMut rejeita os resumos com “Invalid or incomplete test protocol”, baseline_failed/2, UUID `27732709-5293-4cf9-bb99-16d10b5371b4`. Não omitir suítes; o futuro reparo exige prova ponta a ponta com catálogo completo.

O [aceite do SiFuture](/home/renanfranca/projects/kof-sifuture/.agent/validation/sensors-adoption.md#kofmut-manual-recipe-acceptance) e a continuidade de seu `EXECPLAN.md` conservam os resultados essenciais, identidades, hashes individuais dos cinco relatórios e limites das provas. Evidência nova opcional: `/home/renanfranca/projects/kof-sifuture/.agent/tmp/kof-mut-recipe-fix-20261026/`. Configuração, wrapper, fontes e testes permanecem byte a byte iguais: 49 arquivos protegidos, manifesto SHA-256 `3aa5364846a284d6741d73e75677cb26a11e8be7d4b93a46cf8a285256d3396f`; 200 arquivos rastreados fora dos quatro arquivos documentais autorizados inalterados. Os históricos dos dois planos e do aceite foram preservados; exclusão local de temporários exatamente uma vez. Entrega documental encerrada; compatibilidade de várias suítes e M2–M5/S1–S3 permanecem abertos. Sem worktree, subagentes, commit, PR, publicação ou ativação de sensores.

## Continuidade: leitura de execuções concatenadas no KofMut — 26/10/2026

O plano aprovado de reparo está em execução no checkout KofMut, base a40b20ac37afac302efc2a0dae7702e44720e166, branch multiple-test-invocations; SiFuture dc96b0366eee67b3417d58dbe14a06c66e6651aa em sensor-calibration-m1. O leitor valida os resumos de cada execução contra suas próprias suítes e acumula casos/falhas, preservando JSON v1, configuração, estados, retornos e rejeição de evidência inválida. Testes públicos escritos primeiro reproduziram o problema; prova isolada do leitor corrigido passa seis formas válidas e catorze inválidas, e a mesma prova contra o leitor anterior falha na forma válida.

As provas pelo executável público ainda não passaram da preparação, por prazo de compilação ou orçamento de compatibilidade sob carga elevada. A causa de todo o atraso não está estabelecida. Nenhum limite foi ampliado e nenhuma dependência foi modificada. O check completo foi iniciado. Na primeira cópia SiFuture, Extra.kf + GameJourney.kf executaram 115 casos, zero falhas e exit 0; a receita manual retornou 2 sem relatório corrente porque a preparação excedeu 10000 ms. Isso não demonstra Background com o leitor corrigido.

Permanecem pendentes a regressão pública corrigida, o check completo, a avaliação Background e os três cenários reais do cálculo em segundo arquivo de suíte. A limitação nos guias SiFuture continua até a prova completa. Os históricos anteriores foram preservados; wrapper, configuração, escopo e catálogo permanente não mudaram. Aceite detalhado em /home/renanfranca/projects/kof-mut/.agent/validation/multiple-invocations.md e na continuidade de /home/renanfranca/projects/kof-sifuture/.agent/validation/sensors-adoption.md. M2–M5 e S1–S3 não são encerrados por este reparo.

Fechamento da tentativa do leitor concatenado: check KofMut exit 1, CLI 18/13 de 31; demais suítes não atingidas. Tag corrigida exit 1 antes dos cenários por preparação; prova isolada do leitor 2/0 (seis formatos válidos e catorze inválidos) contra controle anterior 1/1. SiFuture normal 115/0/exit 0; mutação real indisponível por preparação e sem reportPath corrente. Causas de todas as assertions CLI não foram demonstradas. Correção implementada, plano e aceite continuam incompletos. Guias mantêm a limitação; configuração, wrapper, escopo, catálogo e 202 arquivos protegidos continuam iguais. Prefixos históricos e exclusão local foram preservados; diff check passou. Nenhum limite, compilador, dependência, gatilho ou instalação mudou, e não houve commit/publicação. Retomar provas públicas e reais sob os mesmos limites quando a preparação puder concluir.

## Recuperação conferida e retomada dos aceites — 26/10/2026

Recuperados e aplicados os dez arquivos anteriores ao Luna, todos iguais ao manifesto histórico antes de aplicar. Leitor corrigido 5e46e9ce8c6a7f8f951b1a46108eb44442d0bdcde624fdc8aa24d71d6a22fc46, base a40b20ac37afac302efc2a0dae7702e44720e166. Manifesto e aceite originais preservados; suplemento KofMut .agent/validation/multiple-invocations-recovery.md e novo manifesto separado. As oito cópias da comparação Luna continham o leitor da base: comparação inválida, logs retidos. Novas rodadas verificaram inventários e leitores distintos antes das medições, em ordem alternada, com Kof 0.6.6 e todos os limites preservados. Registraram prazos excedidos, sem estabelecer causalidade da carga.

Tag final multiple-invocations aprovada, 3/3 grupos, exit 0. Prova isolada corrigida 2/0; base 1/1 com falha esperada. Compatibilidade final exit 1, 7/8 falhas; check completo exit 1 no CLI 19/12 de 31; Run inteira 34/13 de 47, incluindo os três grupos novos aprovados; Install 16/15 de 31; frontend 15 grupos aprovados. Todas as suítes foram tentadas. Cinco das treze falhas históricas não têm etapa individual estabelecida; os demais diagnósticos de preparação tampouco provam todos os motivos internos.

Quatro novas cópias SiFuture com dois arquivos e 115 casos executaram a receita aprovada sem mudar configuração/wrapper/catálogo. Normais: 115/0/exit0 nos três primeiros, 115/1/exit1 na baseline deliberadamente falha. Todos os KofMut: incomplete/3 por timeout no teste da baseline aos 10000 ms, exit137, nenhum candidato/mutante. Tempos sequenciais do próprio CLI somam 11985/15400/15641/13825 ms, excluindo preparação/startup, já acima do limite do comando completo. UUIDs próprios, relatórios anunciados, escopos, contagens, exits e preservação dos 190/191 arquivos conferidos no aceite SiFuture .agent/validation/sensors-adoption.md. Não reinterpretar os timeouts como detecção, sobrevivência ou baseline_failed/2.

Recuperação e comportamento do leitor comprovados, aceite global ainda pendente. Guias mantêm a limitação. A próxima decisão é sobre condições controladas capazes de cumprir os prazos ou revisão explícita dos limites/restrições da receita; nenhuma ampliação foi feita. Históricos continuam como prefixos, dependência e fontes Kof preservadas, sem hooks, commit, publicação, agentes ou worktrees. M2–M5 e S1–S3 continuam abertos. Novos manifestos e conferência final de preservação documentam a entrega sem substituir o selo anterior.


## Continuidade: sobreviventes de Meteor e escopo manual — 26/10/2026

Implementação concluída no checkout SiFuture sensor-calibration-m1, base
fc74cb777c602f9745551d3a39f697a2b4a26652 mais diff local. Quatro cenários
existentes reforçados, catálogo preservado em 114 casos, fixture visual usando
collide()/impactFrame(), escopo permanente Background/Meteor e guias bilíngues
atualizados. Código de produção, KofMut, wrapper e limites preservados.

JVM/JS: 114 casos, zero falhas, exit 0 nos dois alvos; browser_meteor.py exit 0
no Chrome 155.0.8059.39, seis instantes dos impactos e relançamento. Receita
manual literal e inspeção da mesma chamada: native/recipe/inspection exit 1/1/1,
complete. UUID 05f9192d-a6fe-47f2-a524-aeecaf451152, JSON SHA-256
3f3561d2f144cb9eac693455e26b97f3b305379f0f30a58ad2eb8073ef370b58.
42/42 candidatos executados, 38 Killed, quatro Survived, zero compileError,
timeout, testError ou pending, sem descartes/limitações. Todos os 28 Killed
anteriores permanecem detectados; nove dos treze sobreviventes anteriores
passaram a falhar por assertions.

Quatro equivalências demonstradas, sem exclusão ou supressão: estados iniciais
de active/collided são sobrescritos por reset antes de observação na partida,
com equivalência limitada ao fluxo Game, não à classe geral; duas fronteiras
verticais ficam cobertas pela outra cláusula com alturas 18/20 e sem overflow.
Prova JVM/JS comparou 673740 resultados por alvo para os dois edits geométricos
e verificou convergência dos estados após reset em ambas as direções. Cada
mutante inicial também executou 114/0 em ambos os alvos. Expectativas conferidas
contra Java histórico 50fc40d e especificação; auditoria separada das provas
rejeitou 21 controles adulterados e reconciliou todos os IDs/logs atuais.

KofMut limpo 338c7b3501d2ec91a9072f1e68ac827aae7f5d36 coincide com os 44
inputs congelados da qualificação anterior, reutilizada sem alterar ferramenta.
Kof 0.6.6 e jar SHA-256 198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58
preservados. Aceite autossuficiente e matriz por mutante em
/home/renanfranca/projects/kof-sifuture/.agent/validation/sensors-adoption.md,
âncora meteor-survivor-acceptance; continuidade do EXECPLAN no mesmo repositório.
Históricos preservados como prefixos; evidência local opcional em
.agent/tmp/meteor-acceptance-20261026/. Sem sobrevivente inexplicado no escopo
avaliado. Resultado bruto continua complete/1, sem conversão para aprovação.
Sem commit, CI novo, publicação, worktree, subagente, hook ou instalação.
M2–M5/S1–S3 permanecem fora desta continuidade.

## Continuidade documental: regressão JS no Kof 0.6.7 — 27/10/2026

Sobre SiFuture 53e9626b19ad5740dd2b250b2f167932c892e364, branch
sensor-calibration-m1, entregue diagnóstico e relato para revisão com o título
“[Bug]: JS no Kof 0.6.7 ignora break em for-in dentro de if”. Não publicado.
O mínimo histórico foi reexecutado em 0.6.6/0.6.7 × JVM/JS; uma variante
observa 11/12/24/36. Oito runs e dois builds JS retornaram 0; somente
0.6.7/JS ocupa os três slots no passo 12. No 24 também diverge; no 36 todos
os caminhos já ocupam os três, por isso esse instante sozinho não discrimina.
JavaScript gerado perde o break em 0.6.7. Contrato Kof, training, Learn e regra
Java histórica foram conferidos independentemente dos resultados. A alteração
específica responsável não foi determinada. Jar coincide com digest oficial;
formulário e buscas por duplicatas atualizados, incluindo issues fechadas.

Aceite e matriz acrescentados sem apagar o histórico em
/home/renanfranca/projects/kof-sifuture/.agent/validation/sensors-adoption.md,
âncora kof067-js-break-regression. Relato autossuficiente em
/home/renanfranca/projects/kof-sifuture/.agent/validation/kof-0.6.7-js-break-issue.md;
continuidade no EXECPLAN.md do mesmo checkout. Evidência bruta opcional em
.agent/tmp/kof067-break-report-20261027/, fora do versionamento. Fontes,
testes, guias e ferramentas preservados. Aceite anterior continua sendo de
Kof 0.6.6. Sem correção do compilador, workaround no jogo, publicação,
commit, CI, navegador novo, subagentes ou worktree. Revisão do rascunho e
eventual publicação continuam posteriores; M2–M5/S1–S3 não são encerrados.

## Continuidade: publicação da issue de `break` no JS 0.6.7 — 27/10/2026

Publicada KofLang/Kof4j #975, por renanfranca, em 27/10/2026 às
12:33:27 UTC: https://github.com/KofLang/Kof4j/issues/975.
Título final: “[Bug]: break em for-in não encerra o laço no JS 0.6.7”.
Base SiFuture 53e9626b19ad5740dd2b250b2f167932c892e364, branch
sensor-calibration-m1. Título e abertura aprovados aplicados, campos mantidos,
evidências adicionais em seção expansível. Programas e saídas comparados
às oito execuções preservadas; trechos JS e hashes conferidos. Expectativa
Kof e distinção nos passos 12/24 reconferidas separadamente. Busca atualizada
incluiu issues fechadas, sem equivalente. Não houve nova execução do jogo.

A tentativa pelo conector recebeu 403. Após confirmar ausência de issue pelo
título, gh CLI autenticado como renanfranca publicou uma única issue, conforme
instrução do usuário. Consulta posterior confirmou repositório, autoria,
título e corpo integral, com código, links e details; sem responsáveis ou
marco. SHA-256 do corpo público:
0f919ccd7c7d6f09a208f2eae5750baad687e739f724338a759439485b0072ab.

Aceite acrescentado em
/home/renanfranca/projects/kof-sifuture/.agent/validation/sensors-adoption.md,
âncora kof067-js-break-published. Rascunho identificado como publicado em
/home/renanfranca/projects/kof-sifuture/.agent/validation/kof-0.6.7-js-break-issue.md;
continuidade acrescentada ao EXECPLAN.md. Verificação documental por
python3 .agent/tmp/kof067-break-publication-20261027/check_publication.py
e git diff --check, ambos com retorno 0. Evidência local opcional no mesmo
diretório, fora do versionamento. Históricos preservados como prefixos.
Publicação concluída; a alteração específica responsável pela regressão
continua indeterminada. Sem correção do compilador, alteração do jogo,
commit ou CI novo; os aceites 0.6.6 e M2–M5/S1–S3 continuam históricos.

## Continuidade documental: estado em 31/10/2026

Reconciliação documental feita em 31/10/2026, sem executar sensores, testes, mutação ou builds. O histórico acima foi preservado como prefixo.

**SiFuture:** branch `sensor-calibration-m1`, HEAD `0e18275` (“docs: record Kof 0.6.9 UI regression findings”), checkout limpo. Esse commit, posterior à última continuidade acima, acrescenta dois registros: `.agent/validation/kof-0.6.9-js-ui-heading-regression.md`, que descreve a investigação (uma chamada nua a um método da própria classe dentro do argumento de `Column(...)`/`Row(...)` do kof.ui não é resolvida, e `ControlsGuide.kf` falha em JS com `ReferenceError` e em JVM com `NoSuchMethodError`, embora o build termine com exit 0), e `.agent/validation/kof-0.6.9-ui-column-method-issue.md`, rascunho de issue **ainda não publicado**.

**KofMut:** branch `multiple-test-invocations`, HEAD `6fc5df4` (“perf: parallelize check suites”), dez commits à frente de `main`, ainda sem merge. Inclui leitura de várias suítes, suporte ao Kof 0.6.8 e check paralelizado, com check completo exit 0 em 31/10. Há um diff não commitado em `.agent/validation/check-parallel.md`, com a regressão refeita usando Kof 0.6.4. O `EXECPLAN.md` da raiz foi removido em `23c8964` e só existe no git: `git -C /home/renanfranca/projects/kof-mut show 6764595:EXECPLAN.md`. Os links acima para `/home/renanfranca/projects/kof-mut/EXECPLAN.md` são históricos e não abrem mais um arquivo.

**Kof:** o `kof` do PATH agora é 0.6.9 (`kof info --json`). Todos os aceites registrados acima usaram 0.6.6.

**Decisão do usuário, 31/10/2026:** os próximos marcos dos sensores (M2 em diante) serão validados com **Kof 0.6.4**, colocando `/home/renanfranca/.local/share/kof/kof-0.6.4-linux-x86_64/bin` primeiro no PATH. Segundo o usuário, o SiFuture funciona integralmente com 0.6.4; isso é coerente com o rascunho de issue de 31/10 (“Com 0.6.4, o mesmo código funciona”). Esta reconciliação registra a afirmação, sem nova execução.

**Pendências antes do M2 criadas pela troca, separadas do jogo:**

- `scripts/kof-sensors/pom.xml` fixa o jar 0.6.6 (`kof.jar` em `kof-0.6.6-linux-x86_64` e `<version>0.6.6</version>`). O analisador usa a API do lexer/parser oficiais, que pode mudar entre versões; a calibração do M1 (25 arquivos, 321 unidades, 45.443 tokens, 17 grupos CPD) e o subcomando `check` do wrapper precisam ser repetidos com o jar 0.6.4 antes de servirem de base.
- Fixar qual revisão do KofMut o SiFuture consome: os registros citam `a40b20ac37afac302efc2a0dae7702e44720e166` e `338c7b3501d2ec91a9072f1e68ac827aae7f5d36`; o checkout atual está em `6fc5df4`, sem merge em `main`.
- Decidir se o rascunho da issue do 0.6.9 será publicado; isso não bloqueia M2 com 0.6.4.

M2–M5 e S1–S3 continuam pendentes. Sem alteração de fontes, testes, `pom.xml`, KofMut, commits, worktrees ou publicação.

## Continuidade: revalidação com Kof 0.6.4 e KofMut do PATH — 01/11/2026

Decisão do usuário: Kof e KofMut vêm do PATH. Executado o plano
`2026-11-01_FEATURE_sifuture-kof064-path-revalidation.md` no SiFuture `0e18275`
(diff local sem commit). KofMut `main` `9f9bb06` instalado com 0.6.4 (imagem
`b5401898…`); a imagem de 25/10 foi recusada como defasada pelo novo
`verify-kofmut` (exit 1, 13 fontes divergentes). Com 0.6.4, todos os passos
1–8 coincidiram com o esperado: 114/0 em jvm e js, sensores 21/0, sete
jornadas de navegador PASS, fixtures KofMut complete/0 e complete/1, receita
Background + Meteor complete/1 com 42/38/4 e os mesmos estados por mutante de
26/10. O frontend 0.6.4 reproduz a calibração de 25/10 na mesma árvore; a
árvore atual mede 45.988 tokens e 19 grupos CPD por causa do commit `53e9626`.
A pendência “pom.xml fixa 0.6.6” e a de revisão do KofMut estão resolvidas pelo
PATH. Pendentes: `./scripts/check` opcional do KofMut, CI em 0.6.9, M2–M5 e S1–S3.
Registro completo no `sensors-adoption.md` do SiFuture, âncora
`kof064-path-revalidation`.

Passo 9 opcional, 01/11/2026: o `./scripts/check` do KofMut `9f9bb06`, com 0.6.4
primeiro no PATH e 0.6.8 como Kof alternativo, retornou 0 em 732 s com as nove
filas passando. Uma rodada anterior retornou 1 por erro do operador (variável
apontando para o executável, não para o diretório `bin`); ambas estão
registradas no `sensors-adoption.md` do SiFuture.

## Continuidade: produção calibra, testes são medidos; regras de testes no M2 — 01/11/2026

O registro de 01/11 acima foi escrito sobre `0e18275` com diff local; o usuário
o publicou no SiFuture em `ba8739d`. Na revisão desse commit, o usuário decidiu:

1. **Complexidade, profundidade e parâmetros: a produção calibra e os testes
   são medidos.** O limite de cada uma é calculado só com `src/main/kof`; as
   suítes são avaliadas contra esse limite e aparecem como dívida separada.
   Linhas por função e statements mantêm a exceção das suítes; linhas por
   arquivo continuam com tudo (150). Motivo: os testes inflavam o limite da
   produção (complexidade 17 com testes, 10 sem).
2. **As seis regras de desenho de testes do Katacombs entram no M2**, que até
   aqui não as cobria.
3. **O medidor muda agora**, para o M2 partir dos limites corretos.

Executado no SiFuture `ba8739d` com Kof 0.6.4 do PATH, sem commit. O medidor
ganhou `SuitePolicy` (`EXEMPT`/`MEASURED`) e inventário `schemaVersion` 2, com
RED registrado e 22/0 depois. Limites na árvore atual: complexidade 10 (18
findings de produção, 38 de testes), profundidade 2 (12 e 8), parâmetros 4
(2 e 0); 150/25/17 inalterados. A divergência 16 → 17 de complexidade com
testes entre 25/10 e hoje vem do teste `GameJourney.kf:794` (complexidade 18,
commit `53e9626`). `verify-kofmut` agora recusa `kof-mut` sem `image.json` ao
lado e pede `./install.sh` (provado com `kof-mut/bin` primeiro no PATH, exit 1).
A prova com o PATH normal ficou pendente: retornou 1 porque o checkout KofMut
tinha um arquivo não rastreado alheio à sessão
(`.agent/validation/kof-0610-revalidation.md`).

**Acréscimo ao M2: regras de desenho de testes.** Referência fixada Katacombs
`44cb39c916e9a05de561123d7b13554ee6e0a516`, `SENSORS.md:387-396` (tabela em
390–396) e guias em `scripts/guides/tests.mjs`: `no-assertion-free-test`,
`no-mystery-guest`, `no-branching-test`, `no-looping-test`, `named-arrange` e
`no-interaction-assertion`. Portar para Kof as que fizerem sentido no modelo de
`test "nome" { }` com `assert`, cada uma com probe individual (detector,
localização, ID, guia e desaparecimento do finding ao remover o probe) e guia
adaptado com atribuição. Justificar por escrito as que não se aplicarem; por
exemplo, `no-interaction-assertion` depende de dublês com verificação de
chamadas, e a existência de algo equivalente em Kof precisa ser verificada
antes de portar ou descartar. Achados existentes nas suítes ficam como dívida,
sem supressão. Antes de recomendar `testRows` do Learn como alternativa a
laços e ramificações em testes, verificar no M2 se ele existe e funciona no
Kof 0.6.4.

Registros: `sensor-calibration.md`, `sensors-adoption.md` e `EXECPLAN.md` do
SiFuture, seções datadas de 01/11/2026 sobre calibração por produção.

Fechamento da prova de B, 02/11/2026: com o checkout KofMut limpo em `64c85f8`
(commit só documental), `verify-kofmut` com o PATH normal retornou 0, com
detected complete/0 e survived complete/1 em Kof 0.6.4.

## Continuidade documental: Kof 0.7.0 adotado — 03/11/2026

Decisão do usuário: o SiFuture e o KofMut passam a usar o **Kof 0.7.0** do PATH; o **0.6.4** fica como Kof de compatibilidade. O merge de `sensor-calibration-m1` na `main` só acontece quando a versão nova do Kof estiver funcionando; o PR fica para depois.

Evidência: `.agent/validation/kof-0.7.0-revalidation.md` (SiFuture `58478aa`, KofMut `77dfa58`). Com 0.7.0, passam check e 114 testes em JVM e JS, build, as sete jornadas de navegador (regressão Column/Row corrigida, #991), o check completo do KofMut (com `LC_ALL=C.UTF-8`) e a mutação real (42 candidatos, 38 Killed, 4 Survived, iguais ao 0.6.4).

Pendência que bloqueia o M2: o medidor dos sensores falha no 0.7.0 (`scripts/kof-sensors/test` exit 1; `run .` exit 1, 14 falhas). `Spans.java` ainda supõe que a posição de `ConstructorDeclarationNode` fica depois do corpo; desde o 0.6.7 ela é o início da declaração. A correção é do SiFuture. Depois dela, a calibração precisa ser medida de novo com 0.7.0.

## Decisões do M2 — 03/11/2026

Decisões do usuário, tomadas antes de planejar o M2:

1. **Bloqueio por tamanho:** os achados de tamanho (linhas por arquivo e por função, complexidade, profundidade, parâmetros, statements) **bloqueiam no Stop quando estão em arquivos tocados pela sessão**, como no Katacombs: escopo do ledger, deduplicação por conjunto de achados e no máximo três bloqueios por sessão. Depois disso o sensor continua reportando, sem bloquear. A dívida existente em arquivos não tocados não bloqueia; em arquivos tocados, bloqueia.
2. **Comandos:** `package.json` só com scripts (`npm run lint:sensor`, `check`, `check:task` e demais nomes do plano), sem dependências npm. Os hooks do M3 já serão Node.
3. **Regras de desenho de testes portadas no M2:** sem asserção (`assert`, `assertEqual*`, `assertThrows`, `fail` contam como asserção), `if` e laço no corpo do teste, arrange longo (mais de 8 statements antes da primeira asserção) e mystery guest (teste que depende de estado preenchido por `setup`). Todas usando o AST oficial do Kof, com probes e guias adaptados de `scripts/guides/tests.mjs` do Katacombs `44cb39c`.
4. **Asserção de interação não é portada:** a busca na documentação local do Kof (`training/`, `learn/`, `docs/language-reference/`), na stdlib `kof.test` e nos testes do SiFuture não encontrou biblioteca de mock nem spies. Contadores escritos à mão ficam para a pergunta 7 da revisão inferencial (M4). Reavaliar se surgir uma biblioteca de mock.
5. `testRows` aparece no código da stdlib dos jars 0.6.4 e 0.7.0; ainda falta provar que executa antes de recomendá-lo nos guias das regras de laço.

Pré-requisito do M2: corrigir o medidor para a posição de construtor do Kof 0.7.0 e medir de novo a calibração com 0.7.0.

## Continuidade: medidor dos sensores no Kof 0.7.0 — 03/11/2026

O pré-requisito do M2 está cumprido, como diff local sobre `58478aa` (sem commit). `Spans.constructorName` aceita a posição do nó de construtor no início da declaração (0.7.0) ou depois do corpo (0.6.4). `scripts/kof-sensors/test`: 23/0 com 0.7.0 e com 0.6.4 (um teste novo para construtor com cláusula `throw`). `scripts/kof-sensors/run .` com as duas versões: exit 0, inventários idênticos entre si e ao de 01/11. Calibração com 0.7.0: complexidade 10 (18 produção, 38 testes), profundidade 2 (12, 8), parâmetros 4 (2, 0), arquivo/função/statements 150/25/17, 19 grupos CPD, 45.988 tokens. Evidência no SiFuture: `.agent/validation/sensors-adoption.md`, `sensor-calibration.md` e `kof-0.7.0-revalidation.md`, seções de 03/11/2026. O M2 está desbloqueado.

## Decisões do M2 — 04/11/2026

Decisões do usuário, tomadas ao fechar o plano de execução do M2 (plano da sessão em `~/.claude/plans/implementado-revise-de-acordo-atomic-sprout.md`):

1. **Regras de comentário:** portar as **quatro do Katacombs**, `long-comment`, `stale-comment`, `commented-out-code` e `deferred-work`. Elas não substituem o `AGENTS.md` do SiFuture, que continua mais rígido (nenhum comentário explicativo).
2. **Escopo fora do Stop:** `lint:sensor` e `dup:sensor` analisam os arquivos `.kf` **alterados em relação à `main`**, inteiros, incluindo os novos; caminhos explícitos também são aceitos. O comando `sensors:debt` aplica as mesmas regras ao repositório inteiro, só para relatório.
3. **Escopo do M2:** só o tier barato (`lint:sensor`, `dup:sensor`, `secret:sensor`, `docs:sensor`, `sensors:debt`, `sensors:doctor`) e `check`/`check:task`. Os comandos `design:*` e o adaptador behavioral ficam para o **M4**. Isso substitui a lista de comandos do M2 acima nesse ponto.

Execução iniciada em 04/11/2026 na branch `cheap-quality-sensors` do SiFuture, a partir de `main` `f483b91`, Kof 0.7.0 e 0.6.4 de compatibilidade.

## Continuidade: M2 executado — 04/11/2026

Executado no SiFuture, branch `cheap-quality-sensors` sobre `f483b91`, diff local sem commit. Comandos: `lint:sensor`, `dup:sensor`, `secret:sensor`, `docs:sensor`, `sensors:debt`, `sensors:doctor`, `check`, `check:task` e `test:sensors` (`package.json` só com scripts). Medidor ganhou `Main --findings` (achados estruturais, cinco regras de teste, quatro de comentário e CPD), Java 40/0 com 0.7.0 e 0.6.4; testes Node 21/21. `sensors:debt` reproduz o M1 em `src/` (19 grupos CPD). Dívida nova das suítes: 207 `looping-test`, 52 `branching-test`, 28 `unnamed-arrange`; nenhum achado de comentário.

Adaptações registradas no `NOTICE` e no aceite: links `caminho:linha` no `docs:sensor`; Gitleaks sobre os arquivos publicáveis (o `.agent/tmp/` local dava 52 falsos achados); `commented-out-code` exige que todos os statements sejam código, por causa da declaração `Tipo nome` do Kof; `mystery-guest` olha campos `static`, porque Kof recusa `var` de topo. `testRows` provado em 0.7.0 e 0.6.4, JVM e JS, antes de entrar no guia.

`npm run check` na branch: `FAIL at docs:sensor`, pelo único link quebrado real, `.agent/validation/controls-guide.md:127` → `BitmapFont.kf` (removido em `fbe2029`; corrigido depois, ver a próxima seção). Tudo antes dele passou. A mutação real pelo passo do `check` foi provada em cópia (`Background.kf`, 1/1 morto). Pendências: decisão do usuário sobre o link, commit/push, CI com sensores e M3 (hooks). Aceite: `.agent/validation/sensors-adoption.md#m2-tier-barato-e-check`.

## Continuidade: commit do M2 e link corrigido — 04/11/2026

O usuário fez o commit do M2 como `236f8b4` (sem push). Depois, o link de `controls-guide.md:127` foi corrigido para `BitmapFont.kf` em `3829df1` (o arquivo existiu e foi removido em `fbe2029`; a busca anterior usou glob errado). Com isso, `npm run check` e `npm run check:task` passam na branch, com lint, dup e mutação em SKIP porque nenhum `.kf` mudou. Aceite: `sensors-adoption.md#m2-revalidacao-apos-link`. Pendente: commit desta correção, push, CI com sensores e M3.

## Decisão de 05/11/2026: pagar a dívida antes do M3

Decisão do usuário: a dívida inteira (suítes, produção, CPD, fixtures `tests/*.kf` e sobreviventes do KofMut) é paga **antes do M3**, e a regra do arquivo tocado inteiro fica mantida. Sem supressão, allowlist ou mudança de limite. Execução na branch `sensor-debt-payoff` (a partir de `f4af07a`), com o plano em `2026-11-05_FEATURE_sifuture-sensor-debt-payoff.md` e o aceite em `.agent/validation/sensor-debt-payoff.md` do SiFuture.

Progresso em 05/11: R0 medido em `f4af07a`. KofMut sobre toda a produção: 1167 candidatos, 678 mortos, 489 sobreviventes, `incomplete` (exit 3) por `enum` não suportado em cinco arquivos; `GameControls`, `GameView` e `ControlsGuide` sem nenhum morto. Parado no ponto de parada 4, aguardando o usuário.
