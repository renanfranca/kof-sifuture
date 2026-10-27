# Aceitação dos sensores: M1

M1 executado localmente em 25/10/2026 na branch `sensor-calibration-m1`, base `82111142c85f98b970ccd65fbf044e492d017729` mais alterações não commitadas deste marco. Checkout inicialmente limpo. Não há um novo SHA de entrega porque o escopo proíbe commits. Os registros descrevem os bytes locais; não são evidência de CI ou publicação. Trabalho na sessão atual, sem subagentes, worktree, PR ou alteração do jogo. O modelo e o esforço efetivos da sessão não foram consultáveis por uma interface de execução; não se atribui esta prova ao piloto Luna histórico.

## Resultado e limites

Infraestrutura e medição do M1 demonstradas. O inventário completo, seis distribuições, propostas, locais afetados, 17 grupos CPD e triagem dos 15 findings de tamanho estão em [sensor-calibration.md](sensor-calibration.md). A dívida permanece visível; propostas de limites não a aprovam. Nenhum hook, severidade ou guia original foi alterado. M2–M5 e S1–S3 continuam pendentes, assim como a ativação dos sensores. Não há fechamento global da adoção.

## Identidade da execução

| Item | Identidade observada |
| --- | --- |
| SiFuture | `82111142c85f98b970ccd65fbf044e492d017729`, mais diff local do M1 |
| KofMut | checkout limpo `a40b20ac37afac302efc2a0dae7702e44720e166`, CLI `0.1.0` |
| Kof efetivo | `/home/renanfranca/.local/bin/kof` resolvido para `/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/bin/kof`, `kof 0.6.6` |
| Frontend carregado | `/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/lib/kof.jar` |
| SHA-256 do jar | `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58` |
| Fontes locais de pesquisa Kof | `7c237861a9035d84b1f7ec4cfddd89daef4c6ddd` |
| Java do módulo | `/home/renanfranca/.local/bin/java`, Temurin 25.0.2 |
| Maven | `/home/renanfranca/.sdkman/candidates/maven/current/bin/mvn`, 3.9.5 |
| Python | Python 3.10, `python3` no PATH; usuário efetivo UID 1000 na prova de permissão |
| CPD | PMD 7.17.0, tokens oficiais, 50 tokens/5 linhas |
| Katacombs | referência fixa `44cb39c916e9a05de561123d7b13554ee6e0a516`; guias/limiares consultados nessa revisão, sem copiar ou editar componentes |

Não se presume que a revisão das fontes Kof corresponda ao jar instalado. A identidade do frontend consta também no JSON de cada inventário. `KOF_JAR` e `-Dkof.jar` permitem seleção explícita; a seleção deve ser requalificada se mudar.

## Comandos executados e resultados

| Comando na raiz do SiFuture | Exit | Observação |
| --- | ---: | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 0 | 14 testes, preservando os oito existentes e acrescentando seis comportamentos de check |
| `mvn -f scripts/kof-sensors/pom.xml test` | 0 | 12 testes do adaptador; sem falhas ou skips |
| `python3 scripts/kof_project.py check --target jvm --json` | 0 | success true, filesChecked 1, errorCount 0, diagnostics vazio |
| `python3 scripts/kof_project.py check --target js --json` | 0 | mesmo resultado no alvo JS |
| `python3 scripts/kof_project.py test --target jvm` | 0 | 114 casos, zero falhas |
| `python3 scripts/kof_project.py test --target js` | 0 | 114 casos, zero falhas |
| `scripts/kof-sensors/run .` | 0 | 25 esperados, analisados e tokenizados; 321 unidades, 45.443 tokens, zero falhas e 17 grupos de clones |
| `scripts/kof-sensors/verify-kofmut /home/renanfranca/projects/kof-mut .agent/tmp/sensors-m1` | 0 | wrapper da prova qualifica detected/0 e survived/1, incluindo hashes |
| `git diff --check` | 0 | sem erros de whitespace |

Trechos essenciais dos resultados, preservados nos logs locais opcionais `.agent/tmp/sensors-m1/`:

```text
Ran 14 tests in 17.474s
OK
[INFO] Tests run: 12, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

Saída de ambos os checks, pelo wrapper real:

```json
{"success":true,"filesChecked":1,"errorCount":0,"diagnostics":[]}
```

`filesChecked` conta uma entrada, não 25 arquivos individualmente contabilizados. A prova de importação é o ciclo válido → erro SEM011 em Answer.kf importado → restauração dos bytes → válido, executado em ambos os alvos. [Training de CLI](../../../kof/training/tooling/cli.md:17) e [Learn Kof 32](../../../kof/learn/32-cli-tooling.md:70) descrevem o papel de check; o contrato concreto e o teste da distribuição instalada fundamentam esta aceitação. A implementação consultada de CmdCheck retorna a quantidade de entradas:

[CmdCheck.java](../../../kof/kof-cli/src/main/java/dev/kof/cli/CmdCheck.java:82):

```java
        int count = files.size();
```

O significado de `count` explica por que a contagem positiva precisa ser combinada com a prova de diagnóstico importado. O wrapper valida tipos, contagem reconciliada de erros e exit, e conserva o JSON/diagnósticos originais. Aceita as quatro severidades oficiais ERROR, WARNING, NOTE e INFO; somente ERROR entra em errorCount.

## Qualificação do KofMut

Os relatórios preliminares encontrados em `.agent/tmp/sensors-m1-feasibility-61wtluq_/` tinham os estados esperados, mas não reuniam toda a prova de exit/preservação. Por isso foram mantidos e as duas fixtures foram repetidas em árvores descartáveis fora do projeto. O comando reproduzível é `scripts/kof-sensors/verify-kofmut`, cujo código conserva os argumentos exatos, reportPath anunciado e hashes num sumário próprio a cada execução.

Última prova registrada nesta entrega:

| Fixture | runId | Estado/exit da ferramenta | Counts |
| --- | --- | --- | --- |
| detected | `1e4ae10c-5f2e-44c7-aa13-c12fcb629395` | complete/0 | {'candidates': 1, 'executed': 1, 'killed': 1, 'survived': 0, 'compileError': 0, 'timeout': 0, 'testError': 0, 'pending': 0} |
| survived | `33079230-c1fa-45ca-901d-001afd009fbd` | complete/1 | {'candidates': 1, 'executed': 1, 'killed': 0, 'survived': 1, 'compileError': 0, 'timeout': 0, 'testError': 0, 'pending': 0} |

Cada baseline foi `passed`, check exit 0/filesChecked 1 e test exit 0/1 teste executado/0 falhas. Cada relatório anunciou exclusivamente seu reportPath; o script conferiu project-id SHA-256 do caminho canônico, UUID, schema 1, versão efetiva, escopo `src/math/Calc.kf`, um mutante, nenhuma limitação/descarte e todos os contadores. As fontes/suítes/configurações copiadas conservaram seus hashes; os temporários foram removidos pelo contexto mesmo com o resultado survived/1. Exits 0 e 1 são resultados distintos da ferramenta; o script de qualificação retorna 0 por ter observado ambos corretamente. Isso não qualifica a cobertura de todo o jogo nem encerra a meta histórica de 90 segundos.

Hashes essenciais das fixtures, iguais antes/depois: produção `5e99dc302811cf832272afd6bb02dbd3fad71dd3861e8fbd0888e4b02847b3b2`; teste detected `019235e466dc2bfec0149e56722a332bf80fb6443f70b6054e3aa5f9e1836796`; teste survived `6cd7220d2cbb78da52c5ce064560a429f2d3b920cde0e893d9babd23be513126`. Os cinco arquivos de cada cópia foram comparados, incluindo manifestos, config e scope.

## Auditoria por critério

A validade da expectativa é independente da suficiência da prova. A expectativa abaixo vem do M1 aprovado; limiares e exceções foram confrontados com o Katacombs na revisão fixa. Os testes anteriores fornecem regressão; as assertions indicadas verificam as novas obrigações, sem declarar que uma suíte verde prova todo o design.

| Critério e fonte da expectativa | Procedimento/observação | Assertion que distingue falha plausível | Situação e evidência |
| --- | --- | --- | --- |
| KofMut utilizável; contrato JSON/CLI atual e M1 | `verify-kofmut`, CLI real em duas cópias externas | Exits 0/1; complete; estados Killed/Survived; counts exatos, baseline, UUID, project-id, escopo e hashes | Comprovado nas fixtures; sumários/relatórios próprios em `.agent/tmp/sensors-m1/`, identidades e hashes acima |
| Check positivo/negativo JVM e JS; M1 | `CheckBehaviorTest.test_real_wrapper_import_error_restore_on_both_targets`, subprocesso do wrapper | Exit 0, filesChecked 1; depois não zero e SEM011 com nome da variável e caminho Answer.kf; restauração volta a exit 0; fonte preparada removida | Comprovado em JVM/JS pela interface real; checks completos do jogo também passaram |
| Evidência inválida; M1 proíbe falso verde | Executáveis controlados retornam JSON quebrado, arrays, campos inválidos, booleanos/números negativos, erros não reconciliados e exit contraditório | PreparationError em cada caso; nenhuma aprovação; comparação literal de JSON válido e mensagens/severidades | Comprovado por testes controlados, sem atribuir esses payloads à CLI oficial |
| Leitura e isolamento; contrato do wrapper | chmod 000 em arquivo de cópia, UID 1000; falha real de leitura; falha injetada para observar raiz temporária; oito testes anteriores preservados | PreparationError antes de invocar o compilador falso; bytes restaurados; temporários vazios em sucesso/falha; fonte ausente também falha | Comprovado; leitura negada real separada da injeção de falha; inventário não ignora arquivo esperado |
| Métricas corretas; definições do plano | `AnalyzerTest` via lexer/parser do jar oficial | Literais: complexidade 1 sem decisões; 5 parâmetros; nested/lambda com complexidade 2 e pai 1; controles com complexidade 11/profundidade 2/statements 17; strings e comentários não criam nodes | Comprovado por parsing/contagem na JVM; não se apresenta todo exemplo como programa executado |
| Localizações; M1 exige inventário localizado | Mesmos testes, cabeçalho multilinha e corpos de expressão | Linhas inicial/final/coluna literais, construtor 2–5, método 6–11, expressão 12; comentário multilinha e string contendo `}` não fecham o corpo | Comprovado nos formatos exercitados; sintaxe futura exige nova prova |
| Limites; regra menor inteiro com menos de 20 | Testes de Calibration e conferência do inventário completo | 25 == limite não gera; 26 > 25 gera; 19 valores acima mantêm 25; 20 exigem 26; proposta 30 com vinte valores 30; inteiro anterior é verificado na base | Comprovado: complexidade 16/19 findings, anterior 15/24; profundidade 3/5, anterior 2/20; statements 17/18, anterior 16/20 |
| Exceções de suítes; referência histórica | CLI Java real sobre cópia com 32 linhas e 30 statements de teste | Inventário conserva 32/30; população elegível exclui suíte apenas em functionLines/statements, demais quatro métricas incluem os dois arquivos/unidades | Comprovado; sem exclusão de tamanho de arquivo ou complexidade de testes |
| Duplicação real e fronteiras; 50 tokens/5 linhas | `Duplications` chama PMD real e CLI integra inventário/CPD | Clone exato de 50 tokens/5 linhas detectado; 49 tokens ou 4 linhas não; renomeação não normalizada; cada localização tem pelo menos 5 linhas | Comprovado, incluindo arquivos idênticos e sequências longas em uma linha; 17 grupos reais listados |
| Falha de tokenização não aprova; M1 | Lexer inválido + caminho inexistente; subprocesso Java com uma fonte inválida | Esperados 2, tokenizados 0 na prova direta; no comando integrado success false/exit 1 e falhas não vazias, esperados 2/tokenizado 1 | Comprovado; relatório parcial não vale como calibração |
| Avaliação de design; guia fixado e training | Inspeção dos 5 arquivos e 10 funções com finding de tamanho | Cada caso possui classificação, trecho, estado/chamadas/invariantes e custo de eventual extração; construtores C=1 continuam findings; GameJourney mantém incerteza | Triagem documentada; coesão e necessidade de extração não são teoremas do contador |
| Preservação; M1 e AGENTS | SHA-256 de todos os 44 arquivos originais em src/tests; comparação do prefixo histórico dos dois planos | Nenhum hash original alterado; `git diff -- src` e teste Python original vazios; bytes históricos dos planos preservados | Comprovado por comparação local; novos arquivos de infraestrutura não fazem parte do conjunto original |

## Evidência local e continuidade

Logs opcionais: `.agent/tmp/sensors-m1/python.log`, `maven.log`, `check-jvm.log`, `check-js.log`, `test-jvm.log`, `test-js.log`, `inventory.json`, `validation-results.json`, `preservation.json`, relatórios/sumários do KofMut e registros RED antes dos novos comportamentos. A exclusão local `/.agent/tmp/` consta exatamente uma vez no arquivo retornado por `git rev-parse --git-path info/exclude`; nenhuma evidência bruta foi incluída como arquivo de entrega.

A primeira expectativa do teste de função local foi conferida e ajustada antes do aceite: um `;` isolado após o bloco introduzia um statement vazio, sem relação com o comportamento de isolamento que se desejava verificar. A fixture passou a expressar somente a sequência pretendida. O contador não foi afrouxado: statements vazios explícitos continuam contados e documentados. Os testes adicionais de localização e de NOTE foram observados falhar antes das respectivas correções.

Não foram executadas jornadas de navegador neste marco porque apresentação e comportamento do jogo não foram modificados. Não houve nova medição do desempenho do KofMut no jogo nem prova de hooks reais. Esses itens pertencem aos marcos seguintes e às pendências históricas, não são gaps ocultos da medição entregue.

Recuperação: as fontes do jogo não precisam ser restauradas. Para descontinuar esta infraestrutura, reverter somente o diff autorizado de scripts/testes/documentação após revisão. `scripts/kof-sensors/target/` e `.agent/tmp/` são descartáveis, mas preservar os relatórios se forem necessários à investigação. Não apagar evidência anterior ou alterar limites para obter aprovação artificial.

## Continuidade: reparo das lacunas encontradas na revisão M1

Reparo local executado em 25/10/2026 sobre a base revisada `7798e7d6ec8aa31a9ebebe863f88b6bb17cf802d`, na branch `sensor-calibration-m1`. Este SHA identifica a base testada; as alterações abaixo ainda não foram commitadas. Os registros históricos do M1 acima foram preservados. As reproduções originais continuam em `.agent/tmp/sensors-m1-review-repro-xd9hf9kx/`.

| Lacuna | Expectativa e observação que distingue a falha | Resultado e evidência |
| --- | --- | --- |
| Tipo de retorno em cabeçalho multilinha | O método cujo tipo começa na linha 2 e cujo corpo fecha na 27 inicia na linha 2, mede 26 linhas e excede estritamente 25. Retirar uma chamada reduz a medição a 25 linhas e não excede o limite. | `AnalyzerTest.multilineReturnTypeBelongsToMethodSpanAndStrictSizeBoundary` verifica linhas e contagens literais nos dois lados da fronteira; antes da correção observou início 3 e 25 linhas para o caso que deve medir 26. O check oficial JVM aprovou o probe. |
| Construtor nomeado pela classe | Construtores `constructor()`/`constructor(Int)` e `ClassName()`/`ClassName(Int, Int)` medem uma linha, iniciam e terminam em suas linhas próprias e conservam 0/1/0/2 parâmetros. | `AnalyzerTest.namedAndExplicitConstructorsHaveIsolatedSpansAndParameterCounts` verifica as linhas 2, 5, 8 e 11 e seus parâmetros. O caso original atribuía o segundo construtor à primeira ocorrência de `constructor`; o teste distingue cada classe. O check oficial JVM aprovou os quatro formatos. |
| Coerência e faixa do protocolo JSON | `filesChecked` deve ser inteiro JSON em 1..2147483647; `errorCount`, em 0..2147483647. Aprovação exige `success=true`, exit 0 e zero ERROR. Rejeição exige `success=false`, exit 1 e ERROR positivo reconciliado. | Os testes públicos `check --json` preservam literalmente o relatório aprovado no máximo de `filesChecked`, rejeitam os dois campos em 2147483648 com campo inválido explícito, rejeitam `success=false` com zero ERROR e preservam uma rejeição coerente com exit 1. Booleanos, decimais, negativos e reconciliação continuam cobertos. |

O critério segue o contrato consumido pelo KofMut, [CLI §Baseline](../../../kof-mut/docs/cli.md:116):

> “A coherent rejection has `success: false`, exit 1 and a positive error count matching ERROR diagnostics.”

Na prova RED do contador `errorCount=2147483648`, o código da base rejeitou apenas depois, com “errorCount contradicts diagnostics”; a regressão agora exige o diagnóstico específico de faixa inválida antes dessa reconciliação. As reproduções anteriores continuam disponíveis e não foram sobrescritas.

Comandos e resultados desta continuidade, na raiz do repositório:

| Comando | Exit e resultado |
| --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 0; 16 testes, incluindo limites JSON e rejeição coerente |
| `mvn -f scripts/kof-sensors/pom.xml test` | 0; 14 testes, sem falhas ou skips |
| `python3 scripts/kof_project.py check --target jvm --json` | 0; aprovação, 1 entrada e zero ERROR |
| `python3 scripts/kof_project.py check --target js --json` | 0; aprovação, 1 entrada e zero ERROR |
| `python3 scripts/kof_project.py test --target jvm` | 0; 114 casos, zero falhas |
| `python3 scripts/kof_project.py test --target js` | 0; 114 casos, zero falhas |
| `scripts/kof-sensors/run .` | 0; 25 arquivos, 321 unidades, 45.443 tokens, zero falhas e 17 grupos CPD |
| `kof check SensorsProbe.kf --target jvm --json` em `/tmp` | 0; probe de tipo multilinha e quatro construtores aceito pelo frontend instalado |

O inventário refeito é estruturalmente idêntico ao inventário M1 previamente registrado: nenhum valor de arquivo ou função mudou neste projeto; a regressão foi demonstrada por probes focados. SHA-256 comparado contra a base: os 44 arquivos preexistentes em `src/` e `tests/`, exceto o teste Python intencionalmente atualizado `tests/test_kof_check.py`, permaneceram byte a byte iguais. O jogo e as suítes Kof não foram alterados.

Identidade da prova: SiFuture base `7798e7d6ec8aa31a9ebebe863f88b6bb17cf802d`; Kof `0.6.6`, executável `/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/bin/kof`; SHA-256 do `kof.jar` `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`; fontes locais Kof `7c237861a9035d84b1f7ec4cfddd89daef4c6ddd`; Java Temurin 25.0.2; Maven 3.9.5. KofMut permanece no checkout limpo `a40b20ac37afac302efc2a0dae7702e44720e166`; a qualificação anterior não foi repetida porque esta mudança não alterou KofMut nem sua dependência.

Logs completos, probe, inventário e hashes por arquivo estão opcionalmente em `.agent/tmp/sensors-m1-repair-20261025/`. Nenhum deles é necessário para entender este registro. M2–M5 e S1–S3 seguem pendentes. A política para findings de tamanho em código considerado coeso continua aguardando decisão do M2; este reparo não converte findings em avisos, aprova exceções, ativa sensores nem altera limites.

## Continuidade: tipos compostos e construtores com chamadas internas — 25/10/2026

Implementação local na branch existente `sensor-calibration-m1`, base revisada `0f8de0670a57027145019305220d10fe8964ef65`. Preserva os reparos anteriores de declaração multilinha com 26 linhas, construtores nomeados simples e protocolo JSON. O histórico e as reproduções anteriores foram preservados; nova evidência bruta está em `.agent/tmp/sensors-m1-repair-20261025-continuation/`.

| Critério | Expectativa independente da prova | Asserção e observação | Resultado |
| --- | --- | --- | --- |
| Tipos de retorno | Kof declara retorno `Int`, `List<Int>` ou `Int[]` antes do nome ou depois dos parâmetros; o cabeçalho pode ocupar uma ou duas linhas. A localização inclui o tipo e o corpo. | `AnalyzerTest.compoundReturnTypesLocateTwelveDeclarationShapes` enumera as 12 combinações e fixa linhas de início/fim, quantidade de linhas, complexidade 1, zero parâmetros, profundidade 0 e um statement. Antes da correção, `List<Int>` falhou com `Cannot locate declaration`. | Passou após correção; check oficial JVM/JS aprovou o mesmo probe. A CLI inventariou cada método uma vez com as métricas literais esperadas. |
| Construtor explícito recursivo | A declaração `constructor(Int depth)` na linha 2, chamada interna na 3 e fechamento na 4 inicia na linha 2, coluna 5, e termina na 4. Espera-se 3 linhas, um parâmetro, complexidade 2, profundidade 1 e dois statements. | `AnalyzerTest.constructorCallToItsClassDoesNotBecomeTheDeclarationStart` fixa cada valor e também espera `main` na linha 6, com fim na 6. Antes da correção, o começo era a chamada da linha 3. | Passou. CLI encontrou a assinatura, não a expressão `new Box(...)`; `main` reteve seu intervalo. |
| Construtor nomeado recursivo | `Box(Int depth)` possui a mesma localização e contagens do construtor explícito. | `AnalyzerTest.namedConstructorCallToItsClassDoesNotBecomeTheDeclarationStart` usa os mesmos literais de linha, coluna, linhas e métricas. Antes da correção, também começava na linha 3. | Passou. Check oficial JVM/JS também aceitou a forma nomeada e sua instanciação. |
| Inventário e reparos existentes | A mudança no localizador não altera métricas de arquivos/unidades não afetados, contadores, limites, exceções ou fontes do jogo. | Comparação do inventário JSON atual com `.agent/tmp/sensors-m1-repair-20261025/inventory.json`: conjuntos de arquivos iguais, 321 chaves de unidade iguais, zero chaves removidas/adicionadas e zero métricas alteradas. | Passou: 25 arquivos esperados/analisados/tokenizados, 45.443 tokens, 17 grupos CPD; limites 25/26 e testes de protocolo JSON continuam na suíte. |

Expectativa e força da prova foram conferidas separadamente. O contrato de tipo vem da referência Kof: arrays são `type-ref , "[]"`, e a forma genérica `Set<Int> all()` está documentada e ensinada. O check oficial prova aceitação sintática/semântica dos probes, não a correção do medidor. Essa correção é comprovada pelos valores literais do `Analyzer.measure` e pela saída da CLI com o arquivo explicitamente incluído no escopo. As formas testadas não garantem cobertura de sintaxe futura.

Resultados finais dos comandos na raiz SiFuture:

| Comando | Exit e resultado |
| --- | --- |
| `mvn -f scripts/kof-sensors/pom.xml test` | 0; 18 testes, zero falhas/erros/skips |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 0; 16 testes; os testes que verificam erros CLI os esperam, suíte encerrou `OK`; 114 casos Kof JVM executados dentro das verificações |
| `python3 scripts/kof_project.py check --target jvm --json` e `--target js --json` | 0 em ambos; `success=true`, uma entrada, zero ERROR/diagnósticos |
| `python3 scripts/kof_project.py test --target jvm` e `--target js` | 0 em ambos; 114/114 casos, zero falhas |
| `scripts/kof-sensors/run .` | 0; inventário estável conforme acima, sem falhas |
| `kof check /tmp/sifuture-sensors-official-signatures.kf --target jvm --json` e `--target js --json` | 0 em ambos; `success=true`, uma entrada, zero ERROR |

Identidade dos bytes: Kof 0.6.6, jar `/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/lib/kof.jar`, SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`; checkout de pesquisa Kof `7c237861a9035d84b1f7ec4cfddd89daef4c6ddd`. KofMut continuou limpo em `a40b20ac37afac302efc2a0dae7702e44720e166`; sua qualificação existente não foi repetida porque nenhuma dependência ou arquivo KofMut mudou. O plano externo canônico de sensores em `/home/renanfranca/.agents/skills/_temporary/codex-skills-ai-context/2026-10-15_FEATURE_sifuture-quality-sensors-exec-plan.md` foi atualizado em apêndice, com prefixo prévio preservado em `.agent/tmp/sensors-m1-repair-20261025-continuation/external-sensors-plan-before.md`. As fontes e suítes do jogo não mudaram. Nenhum worktree, subagente, commit ou publicação foi criado.

M2–M5 e S1–S3 permanecem pendentes; sensores não ativados. O M2 ainda decidirá a política para findings de tamanho. Os testes cobrem exatamente as formas acima, não todas as extensões futuras do frontend.

## Continuidade: compilador e medição da matriz de construtores — 25/10/2026

Execução na branch `sensor-calibration-m1`, base revisada `47854206fab1c8868b3294062b1a198bf81e0f67`, com as alterações locais do reparo preservadas. O compilador efetivo foi Kof 0.6.6, jar `/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/lib/kof.jar`, SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`. KofMut permanece limpo em `a40b20ac37afac302efc2a0dae7702e44720e166`; a qualificação anterior foi reutilizada porque dependência e checkout não mudaram.

Os bytes testados das fontes de teste são identificados por SHA-256: `AnalyzerTest.java` `dfc1704ca84a3059fefcce159ea2477f857dbd19194c4bf12aa9d74e02f82c07`; `Spans.java` `391f05274352cc80be3ee938687646a07027e8a8e1de30627d37ed3a15bc6d8d`. O inventário atual usa 25 fontes SiFuture esperadas/analisadas/tokenizadas. A fonte da matriz é montada uma vez e a mesma String é gravada para o compilador e enviada ao medidor:

[Trecho de `AnalyzerTest.java` (assertions de métricas omitidas)](../../scripts/kof-sensors/src/test/java/sifuture/sensors/AnalyzerTest.java:347):

```java
String body = switch (bodyShape) {
    case 0 -> "{}";
    case 1 -> "{\n        println(1)\n    }";
    default -> "{\n        var child = new Box(" + (parameterized ? "value" : "")
            + ")\n        if (true) { println(child) }\n    }";
};
String source = "class Box {\n    " + signature + " " + body + "\n}\n";
assertAll(context, () -> {
    checkWithOfficialCompiler(source, "jvm");
    checkWithOfficialCompiler(source, "js");
    var constructor = measure(source).functions().getFirst();
    ...
});
```

O construtor parametrizado agora recebe `new Box(value)`; o caso sem parâmetros produz `new Box()`. A ordem dentro de `assertAll` verifica primeiro o frontend oficial nos dois alvos e depois as métricas sobre exatamente a mesma fonte. O helper exige exit 0, JSON com `success=true`, `filesChecked > 0`, `errorCount=0` e nenhum diagnóstico ERROR.

Saída real do probe inválido antes do reparo e da fonte corrigida depois dele:

```text
$ kof check /tmp/kof-matrix-red-20261025/constructor-True-2.kf --target jvm --json
exit 1
{"success":false,"filesChecked":1,"errorCount":1,"diagnostics":[{"code":"SEM023","file":"constructor-True-2.kf","line":3,"column":21,"length":3,"severity":"ERROR","message":"no constructor of 'Box' with 0 argument(s) (expected 1)"}]}

$ kof check /tmp/kof-matrix-green-20261025/constructor-True-2.kf --target jvm --json
exit 0
{"success":true,"filesChecked":1,"errorCount":0,"diagnostics":[]}
```

Os outros alvos e combinações estão no registro completo `.agent/tmp/sensors-m1-measurement-closeout-20261025/red-results.json` e `matrix-green-results.json`.

A forma escolhida segue a documentação local de classes: `new` permanece sintaxe válida para instanciar uma classe, e a referência gradual de Learn Kof ensina classes mutáveis com campos e `constructor(...)` explícito. O check dos 12 exemplos é a evidência de implementação atual para estes argumentos concretos.

[Trecho do idiom de classes](../../../../projects/kof/training/idioms/classes.md:58):

```text
`new User("Mel", 30)` remains valid, but `User("Mel", 30)` is the
recommended form — the compiler treats both as instance construction.
```

[Trecho do capítulo de classes em Learn Kof](../../../../projects/kof/learn/07-classes-and-objects.md:83):

```kof
class Conta {
    String titular
    Double saldo

    public constructor(String titular, Double saldo) {
        this.titular = titular
        this.saldo = saldo
    }
```

| Critério | Expectativa independente da prova | Verificação e resultado | Limite da prova |
| --- | --- | --- | --- |
| Detecção da fonte inválida anterior | Quando a assinatura é `constructor(Int value)` ou `Box(Int value)`, o exemplo não pode construir `Box()` sem argumentos. | RED reproduzido antes da edição: as duas fontes com corpo chamando `new Box()` falharam em JVM e JS, exit 1, `success=false`, `errorCount=1`, diagnóstico `SEM023`: “no constructor of 'Box' with 0 argument(s) (expected 1)”. As outras dez combinações passaram nos dois alvos. Evidência local: `.agent/tmp/sensors-m1-measurement-closeout-20261025/red-results.json`. | O RED prova a detecção dessas duas formas inválidas pela versão e targets registrados; não prova detecção universal de qualquer erro Kof. |
| Fontes válidas da matriz | Duas formas de declaração × zero/um parâmetro × três formas de corpo devem ser aceitas no frontend JVM e JS. | `constructorSpanMatrixCoversParameterCountsDeclarationStylesAndBodies` usa a mesma `source` na verificação e na medição. Após a correção, as 12 fontes passaram nos dois alvos: exit 0, `success=true`, `errorCount=0`, sem ERROR. Prova integrada: `mvn -f scripts/kof-sensors/pom.xml test`, 21 testes aprovados. | `kof check` demonstra aceitação e checagem semântica da fonte nesses alvos; as assertions do medidor demonstram separadamente os spans e contagens. |
| Medição motivadora | O construtor sem parâmetros com chamada interna começa na linha 2, coluna 5, termina na linha 5 e conta quatro linhas. | `zeroParameterConstructorsStayAssociatedWithTheirOwnBodies` fixa cada valor para `constructor()` e `Box()`, chamadas `new Box()` e `new Box(1)`. | Os exemplos representam as duas chamadas e as duas grafias de construtor descritas; extensões futuras exigem casos próprios. |
| Unidades separadas | Duas declarações de construtor e `main` devem ser publicadas como exatamente três unidades, com intervalos independentes. | O mesmo teste exige `file.functions().size() == 3`; o construtor principal é 2–5, coluna 5 e quatro linhas; o auxiliar é 6–6, coluna 5 e uma linha; `main` é 8–8, coluna 1 e uma linha. | O teste fixa estes três nós; não conclui que todas as combinações possíveis de sobrecarga estão cobertas. |
| Compatibilidade | Assinaturas compostas, funções aninhadas/lambdas, erros e CPD devem conservar seus contratos. | Maven: 21 testes, zero falhas/erros/skips. Entre as assertions preservadas, `nestedFunctionsLambdasMethodsAndConstructorsOwnTheirCounts` fixa unidades e contagens aninhadas, `badSyntaxCannotProduceMetrics` exige rejeição de sintaxe inválida, e `cpdIncludesExactFiftyTokenFiveLineBoundary` fixa detecção e exclusão nos limites 50/49 tokens e cinco/quatro linhas. Python: 16 testes, exit 0. Kof: 114/114 em JVM e JS. | A saída de erro de uma fixture Kof negativa no suite Python é esperada; o comando terminou com `OK` e exit 0. |
| Preservação da calibração | Arquivos e unidades devem permanecer idênticos, sem ajustar expectativas ou regras. | Comparação estrutural contra `.agent/tmp/sensors-m1-repair-20261025-continuation/inventory.json`: 25 arquivos iguais, 321 unidades iguais, nenhum arquivo/unidade adicionado ou removido e nenhuma métrica alterada; 45.443 tokens, 17 grupos CPD, zero falhas. | A comparação descreve o inventário medido neste checkout contra a calibração guardada. |

Comandos finais na raiz SiFuture e resultados registrados: `python3 -m unittest discover -s tests -p 'test_*.py'` (exit 0, 16 testes); `mvn -f scripts/kof-sensors/pom.xml test` (exit 0, 21 testes); `python3 scripts/kof_project.py check --target jvm --json` e `--target js --json` (exit 0, ambos `success=true`, uma entrada e zero erros); `python3 scripts/kof_project.py test --target jvm` e `--target js` (exit 0, 114/114 cada); `scripts/kof-sensors/run .` (exit 0, medição aprovada e inventário preservado). Saídas completas e JSON de comparação estão em `.agent/tmp/sensors-m1-measurement-closeout-20261025/`; são evidência opcional, não requisito para interpretar este registro.

## Retificação: divergência entre gramática, compilador e medidor

A afirmação anterior deste registro, de que construtores explícitos sem corpo estão fora da sintaxe implementada, foi incorreta. O documento da gramática define expressamente seu papel:

> “Therefore the grammar below is presented in EBNF as an extractive description of the real parser — not as the specification the parser follows.”

[Racional da gramática Kof em `grammar.md`](../../../../projects/kof/docs/language-reference/grammar.md:15). Em outras palavras, a produção é uma descrição do parser, não um contrato que determine o comportamento que ele deveria ter. A produção consultada é:

[Gramática Kof em `grammar.md`](../../../../projects/kof/docs/language-reference/grammar.md:144):

```text
constructor-declaration = [ "constructor" ] , "(" , [ parameter-list ] , ")" ,
                          [ throws-clause ] , block ;
```

A evidência local `.agent/tmp/sensors-measurement-closeout-review-2v71lv9r/documentation-discrepancy.txt` registra os resultados distintos:

```text
constructor() sem corpo, check jvm: success=True, errorCount=0
constructor() sem corpo, check js: success=True, errorCount=0
constructor() sem corpo, sensor: success=False, Cannot locate constructor body end for Box
```

Portanto, `kof check` aceitou e checou o exemplo nos alvos JVM e JS, enquanto o medidor falhou ao localizar o fim do corpo. `check` não demonstra execução do programa. A intenção dessa aceitação pelo Kof ainda não foi determinada; não se conclui se é comportamento intencional ou discrepância do frontend. A identidade continua Kof 0.6.6, jar SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`; como versão e hash não mudaram, a prova curta existente foi reutilizada.

Não foram alteradas fontes/suítes do jogo, regras de contagem, limites, guias ou exceções. Não foram instalados gatilhos, ativados sensores ou convertidas contagens em bloqueios. M2–M5 e S1–S3 continuam pendentes; a próxima conversa decidirá quais resultados apenas informam e quais impedem avanço. Nenhum worktree, subagente, commit, PR ou publicação foi criado.

## Continuidade: associação do corpo em construtores sem parâmetros — 25/10/2026

Reparo executado sobre a base `47854206fab1c8868b3294062b1a198bf81e0f67`, branch `sensor-calibration-m1`, sem alterações prévias no checkout. `Spans.constructorName` agora exige que a assinatura candidata leve ao bloco cujo fechamento corresponde ao token imediatamente anterior à posição do node de construtor no AST oficial. Assim, `()` dentro de `new Box()` no corpo não pode satisfazer a busca como se fosse a assinatura; chamadas e blocos internos também não substituem o fechamento do construtor. Parâmetros continuam associados às posições dos nodes formais do AST.

O RED focado falhou como esperado: para `constructor()` com `new Box()` seguido de `if`, a linha inicial observada era 3, mas a declaração começa na linha 2. Depois da correção, a API `Analyzer.measure` confirmou literalmente, para `constructor()` e `Box()` com chamadas `new Box()` e `new Box(1)`, a linha 2, coluna 5, fim 5, quatro linhas, zero parâmetros, complexidade 2, profundidade 1 e três statements. Os construtores auxiliares e `main` conservaram seus próprios intervalos. A matriz adicional cobre ambos os estilos, zero/um parâmetro e corpos vazio, chamada isolada e chamada seguida de `if` (12 combinações), com expectativas literais.

| Prova | Resultado |
| --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | Exit 0; 16 testes, suíte `OK`; diagnósticos de compilação inválida pertencem às fixtures negativas esperadas |
| `mvn -f scripts/kof-sensors/pom.xml test` | Exit 0; 21 testes, zero falhas/erros/skips |
| Checks oficiais Kof 0.6.6 do probe de dois construtores em JVM e JS | Exit 0 em ambos; `success=true`, um arquivo, zero erros |
| `python3 scripts/kof_project.py check --target jvm --json` e `--target js --json` | Exit 0 em ambos; `success=true`, uma entrada, zero ERROR |
| `python3 scripts/kof_project.py test --target jvm` e `--target js` | Exit 0 em ambos; 114/114 casos, zero falhas |
| `scripts/kof-sensors/run .` | Exit 0; 25 arquivos, 321 unidades, 45.443 tokens, zero falhas, 17 grupos CPD |
| CLI do sensor com escopo explícito para o probe principal | `success=true`; construtor 2–5, coluna 5, quatro linhas, zero parâmetros, complexidade 2, profundidade 1, três statements; auxiliar na linha 6 e `main` na linha 8 |

Comparação estrutural com `.agent/tmp/sensors-m1-repair-20261025-continuation/inventory.json`: os 25 arquivos e 321 unidades são idênticos, sem arquivos adicionados/removidos e sem métrica alterada. O protocolo de falhas explícitas permanece protegido pelos cenários públicos existentes de fonte inválida e falha de análise. A identidade do compilador permanece Kof 0.6.6, jar SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`; KofMut não mudou e sua qualificação anterior foi reutilizada. Evidência bruta opcional: `.agent/tmp/sensors-m1-zero-arg-constructor-review/`.

Fontes e suítes do jogo, limites, guias, exceções e a política pendente de bloqueio por tamanho permaneceram intactos. Não houve worktree, subagente, commit ou publicação. M2–M5 e S1–S3 continuam pendentes.

## Continuidade KofMut manual — 26/10/2026

Este aceite cobre somente preparar o uso manual de check/test e mutação. “Bloquear” significa o comando terminar reprovado; nenhum hook ou gatilho intercepta edição ou commit. M2–M5 e S1–S3 não são concluídos por esta configuração. A decisão acrescentada ao [EXECPLAN](../../EXECPLAN.md#continuidade-uso-manual-do-kofmut--26102026) preserva o histórico anterior.

### Identidade

| Item | Identidade observada |
| --- | --- |
| SiFuture | Base `373ad9eaf99dbb3171a6503f630c23d2124a17bc`, branch `sensor-calibration-m1`, mais alterações locais deste marco |
| KofMut | `0.1.0`, checkout limpo em `a40b20ac37afac302efc2a0dae7702e44720e166` |
| Kof | `/home/renanfranca/.local/bin/kof`, `kof 0.6.6`; `--kof kof` escolhe o executável pelo PATH |
| Configuração e escopo | [`kof-mut.json`](../../kof-mut.json), [`kof-mut-scope.json`](../../kof-mut-scope.json) |

### Critérios e resultados

| Critério | Procedimento | Resultado | Auditoria da prova |
| --- | --- | --- | --- |
| Check JVM/JS | `python3 scripts/kof_project.py check --target ALVO --json --kof kof` | Ambos exit 0, `success=true`, um arquivo e zero erros | JSON aprovado pelo wrapper existente |
| Testes JVM/JS | `python3 scripts/kof_project.py test --target ALVO --kof kof` | Ambos exit 0, 114/114, zero falhas | Catálogo completo atual contém uma suíte |
| Testes Python | `python3 -m unittest discover -s tests -p 'test_*.py'` | 16 testes, OK, exit 0 | Log bruto opcional em `.agent/tmp/kof-mut-acceptance/logs/unittest.log` |
| Mutante detectado | Fixture oficial `detected`, `sum(2, 3) == 5` | Um candidato `Killed`; baseline passou; `complete/0`; UUID `4395f5d1-a0f9-462c-b883-6658a3cab362` | A assertion distingue `+` de `-`; prova restrita a um mutante aritmético |
| Mutante sobrevivente | Fixture oficial `survived`, `sum(5, 0) == 5` | Um candidato `Survived`; baseline passou; `complete/1`; UUID `98586243-38ab-4165-9c9a-3ddd1b459607` | Confirma reprovação de qualidade quando sobrevive um mutante; não exige teste artificial |
| Erro de fonte | Expressão incompleta em cópia descartável da fixture | `baseline_failed/2`, check 1, nenhuma mutação; UUID `411d1e33-d4d3-4e37-9ee6-fae65814a1ce` | Teste não iniciado e zero candidatos avaliados |
| Teste falho | Assertion falsa em cópia inicialmente aprovada | Check 0, teste 1, 1 executado/1 falho, `baseline_failed/2`, nenhuma mutação; UUID `1ea0d261-2a87-4255-b140-758c8903b25d` | Baseline reprovado impede mutantes |
| Integração real | Arquivo inteiro `src/main/kof/sifuture/game/Background.kf` | Baseline JVM passou com 114 testes; um candidato `Killed`; `complete/0`; UUID `3e698919-faaa-4ff4-9716-a62a09230bd3`; SHA-256 do JSON `9f3addc040deb5bc0a43176c0c6018ebbd14a12231ab75df7547756d7c50ca19` | Prova operação e aprovação somente desse arquivo nesta execução |
| Preservação e correspondência | Conferir stdout `reportPath`, `runId`, escopo, baseline, contagens, exit e SHA-256 | Tudo reconciliado; 25 hashes de fontes/testes Kof permaneceram iguais antes/depois; SHA-256 igual do manifesto ordenado antes/depois: `e3fe68ce7f029ad791bbf15253e17f4b285bbc6121b5179be042eec91e1a5676`; checkout KofMut permaneceu limpo | Cada saída foi conferida contra o relatório anunciado pela mesma execução; inventários, logs e relatórios individuais preservados opcionalmente em `.agent/tmp/` |

### Decisão e limite

Uso manual, KofMut fixado no SHA acima e wrapper existente via `PATH`; mutação JVM serial, timeout de 10 s por comando e sem orçamento total. `complete/0` aprova só o escopo avaliado; `complete/1` reprova por sobrevivente; erro/baseline com código 2 e inconclusivo/sem escopo/sem mutações com código 3 não aprovam qualidade. Não foi criado wrapper ou interpretador de relatórios. O medidor de linhas/complexidade continua disponível para consulta manual; não é bloqueio. Nenhum sensor ou gatilho foi ativado.

A limitação conhecida é que `scripts/kof_project.py` executa uma chamada Kof por arquivo encontrado no laço [do wrapper](../../scripts/kof_project.py#L151), enquanto o leitor KofMut aceita um único resumo final: `commandPassed >= 0` marca o segundo resumo como inválido em [`Evidence.kf`](https://github.com/renanfranca/kof-mut/blob/a40b20ac37afac302efc2a0dae7702e44720e166/src/main/kof/kofmut/Evidence.kf#L130). O trecho relevante é:

```kof
} else if (line.matches("[0-9]+ passed, [0-9]+ failed.*")) {
    if (commandPassed >= 0) { valid = false }
    var fields = line.split(" ")
    commandPassed = fields[0].toInt()
    commandFailed = fields[2].toInt()
}
```

Por isso, o aceite cobre o catálogo observado com uma suíte (`GameJourney.kf`); futuras suítes exigem prova de compatibilidade e não podem ser omitidas para contornar o problema. M2–M5 e S1–S3 continuam pendentes.

<a id="kofmut-manual-recipe-acceptance"></a>

## Continuidade: receita manual e aceite da configuração real — 26/10/2026

Correção documental sobre SiFuture `4e7d03f9f2f3fa5ef9e3e5549a5be9f06616ba51`, branch `sensor-calibration-m1`, mais o diff local desta entrega. Os registros anteriores permanecem históricos. Foram alterados apenas os dois guias, este aceite e as continuidades dos planos. Não há novo commit, publicação, suíte versionada ou avaliação de mutação nesta entrega.

### Resultado das receitas publicadas

As receitas em [inglês](../../docs/desenvolvimento.md#check-and-mutate-a-source-file-manually) e [português](../../docs/desenvolvimento.pt_BR.md#conferir-e-mutar-um-arquivo-manualmente) executam na raiz do SiFuture e chamam o executável externo `/home/renanfranca/projects/kof-mut/bin/kof-mut`. `run_id` é atribuído no shell que recebe os comandos, antes do subshell. Arquivos anteriores são preservados; cada chamada usa seu UUID e a inspeção lê somente o `reportPath=` anunciado naquela saída, decodificado como string JSON, com um único relatório e `runId` correspondente.

Trecho publicado na receita de execução, após a captura do processo:

```bash
    printf '%s\n' "$exit_code" > ".agent/tmp/kof-mut-runs/$run_id.exit" || exit 2
    cat ".agent/tmp/kof-mut-runs/$run_id.stdout" || exit 2
    cat ".agent/tmp/kof-mut-runs/$run_id.stderr" >&2 || exit 2
    printf 'exit=%s run_id=%s\n' "$exit_code" "$run_id" || exit 2
    exit "$exit_code"
```

O último comando do subshell determina seu retorno. Por isso, o `exit` explícito devolve o resultado capturado mesmo quando `cat` e `printf` passam. Os guardas `|| exit 2` tornam uma falha própria da receita uma reprovação de infraestrutura. A inspeção termina igualmente com `exit "$exit_code"`, após ler e validar `.exit` e apresentar o relatório. O arquivo `.exit` conserva o resultado nativo; uma apresentação que falhe pode fazer a receita terminar em 2 mesmo que esse arquivo contenha 0. Os parênteses limitam o `exit` ao subshell e deixam o terminal disponível.

### Auditoria das expectativas e das provas

Expectativas conferidas separadamente: os quatro retornos exigidos vêm do pedido desta entrega; as correspondências entre estado e código vêm do [contrato KofMut](https://github.com/renanfranca/kof-mut/blob/a40b20ac37afac302efc2a0dae7702e44720e166/docs/report-format.md#overall-status-and-process-exit). O contrato distingue `complete/0`, `complete/1`, falha de baseline/2 e resultados inconclusivos/3. Não se usa o sucesso do verificador como aprovação de uma mutação sobrevivente.

| Critério e expectativa | Prova dos blocos exatos publicados | Como a prova distingue o defeito |
| --- | --- | --- |
| Retorno nativo 0, 1, 2 ou 3 | Extração literal dos quatro blocos Markdown; função Bash controlada no caminho absoluto da CLI, em raízes descartáveis; verificação de argv, `.exit`, apresentação e retorno de execução/inspeção. Cada código foi observado nos dois idiomas. Também passaram 42, 130 e 143. | Expectativas literais por código; devolver sempre 0 ou sempre 2 falharia. Os dois trechos antigos devolveram 0 para código nativo 1. Retirar o `exit` final de cada receita corrigida também devolveu 0. |
| Apresentação bem-sucedida preserva reprovação | Comando controlado 1, `cat`, `printf` e `jq` bem-sucedidos; `.exit=1`, execução=1 e inspeção=1. | O valor esperado é 1 mesmo com apresentação aprovada; os controles defeituosos acima retornaram 0. |
| Falha ao preparar, salvar, ler ou apresentar devolve 2 | Falha controlada de UUID, caminho de diretório ocupado, stdout/stderr com permissão negada, `.exit` em `/dev/full`, evidências removidas antes de `cat`, falha de `cat` e apresentação em `/dev/full`. Na inspeção: `.exit` ausente, ilegível, vazio, texto, negativo, maior que 255 ou multilinha; stdout ausente/ilegível; anúncio ausente, duplicado, JSON inválido ou valor sem tipo string; relatório ausente, ilegível, vazio, JSON inválido, duplicado ou com `runId` divergente; identificador ausente. | Cada cenário usa resultado nativo 0 e exige retorno final 2. Falhas de execução não exibem `exit=0`. Ignorar a falha de `cat` ou aceitar relatório vazio com `jq -e` sem agregação devolveu 0 nos controles defeituosos. Negação de permissão foi exercitada como UID 1000. |
| O terminal continua disponível | Bash 5.1.16, modo interativo, pseudoterminal real: códigos 0/1/2/3 em cada idioma, oito sessões. Após cada receita, consultar `$?`, conferir o mesmo `run_id`, ler `.exit` e emitir o marcador `TERMINAL_AVAILABLE`. | Conferidos marcador, processo ainda vivo e leitura posterior. Um controle com `exit` no shell pai terminou antes do marcador, embora seu retorno numérico fosse 1. |
| Relatório corrente e preservação | Caminho anunciado com espaços e aspas, relatório antigo com nome fixo e data futura, arquivos antigos de saída/exit. Comparação dos bytes antigos após cada cenário. | Escolher o relatório mais recente ou fixo encontraria o `runId` antigo; remover o atual deve falhar, mesmo com o antigo disponível. Nenhum fallback é aceito. |

O verificador local registrou 138 observações: 96 verificações do contrato, incluindo oito sessões interativas, e 42 preparações aprovadas para os casos negativos de inspeção. Os blocos Bash correspondentes são idênticos nos dois idiomas. Os sete controles defeituosos acima confirmam a capacidade de detecção das provas, sem executar mutações Kof.

Identidade SHA-256 dos blocos extraídos, incluindo uma quebra de linha final: execução `f7df764e0dbece0acf698dbcdab2ad6c512563838dd9796d9a8e8832b0652695`; inspeção `11c97fb386e39860a69e87a1da1ad5422439f6e0c11711bc47fa28aac6353834`.

### Provas reais reutilizadas e identidades conferidas

Reutilizados os quatro resultados de `.agent/tmp/kof-mut-manual-review-2isv6v_u/results.json` e o resultado de duas suítes em `multi-suite-result.json`, sem repetir avaliações. O primeiro arquivo tem SHA-256 `bd904e4d58f88e6b584a9fea1623747c70510c5f3f351a18ac229c1225b61de1`; o segundo, `e8912b969c51cb3cd3f3acfe074bec1902d48fa77519cbeb2d5468ce6b4a588a`.

Conferidos: uma única linha `reportPath=` por saída; correspondência com o arquivo JSON existente; UUID do comando, nome reservado e `runId`; schema 1, KofMut 0.1.0, Kof 0.6.6; estado, contagens e baseline reconciliados com o sumário; logs de check/test referenciados pelo relatório. Nos quatro casos com argv preservado, o SHA-256 do caminho do projeto declarado no comando coincide com o identificador do diretório de relatórios. O registro de duas suítes não preserva argv completo; sua identidade foi conferida por saída, relatório anunciado, UUID e logs, sem afirmar reconstrução do comando original.

| Item | Identidade confirmada nesta continuidade |
| --- | --- |
| KofMut | Checkout limpo `a40b20ac37afac302efc2a0dae7702e44720e166`; `VERSION` 0.1.0 |
| Kof | `kof version`: 0.6.6; `/home/renanfranca/.local/bin/kof` resolve para `/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/bin/kof` |
| Frontend | `lib/kof.jar` da distribuição acima, SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58` |
| Fontes Kof consultadas | `7c237861a9035d84b1f7ec4cfddd89daef4c6ddd`; não se presume equivalência com o jar |
| Configuração real | `kof-mut.json`, SHA-256 `2e24df1360b021bbf30d4cf4f7fdcdcf1cec202d601a45b018c61b65d8fda9bd`, igual ao registrado nos quatro casos |
| Wrapper real preservado | `scripts/kof_project.py`, SHA-256 `a389cd1445afb4fd6ee19d895b572aa97d38007243fa43a7ff6c383ca67867b6` |

Os quatro casos usaram cópias descartáveis do SiFuture com a configuração real, via wrapper JVM e catálogo completo, acrescentando um probe à suíte existente. Os 115 casos correspondem aos 114 do jogo mais esse caso; não são uma alteração das fontes ou testes entregues. O escopo foi `src/main/kof/sifuture/ManualMutationProbe.kf`. O sumário original registra `inputsPreserved=true` nos quatro casos; como essas cópias já foram removidas, essa comparação histórica não foi refeita nem apresentada como nova medição de hashes das cópias.

| Caso | runId | Resultado essencial | SHA-256 do relatório |
| --- | --- | --- | --- |
| Detecção | `0da16a7a-4738-42ff-a196-611c0c9761b4` | `complete/0`; baseline check 0, teste 0, 115 executados/0 falhas; 1 candidato, 1 executado, 1 Killed, 0 Survived | `f6fe5ca7145faaa77dae75574c44d16f1285bd82e8fa738e1c4c11a84f4ea2be` |
| Sobrevivência | `51a4b838-0692-4fae-8857-560d2f49a564` | `complete/1`; baseline check 0, teste 0, 115/0; 1 candidato, 1 executado, 0 Killed, 1 Survived | `e25e3b96990c5c9490c91be7c4a0936efe86082ccfe8cdbfe995f6f530af6b5a` |
| Erro de fonte | `9ef127fe-f978-4d92-9206-b7576ba007b5` | `baseline_failed/2`; check 1 com PARSE041/PARSE009; testes não iniciados; todos os contadores de mutação em zero | `f80a94113b94ad8b98154e9d84c43cf1e06c69cdebdd40b43347f6559f774bf9` |
| Teste reprovado | `048023bb-fcc7-476b-b747-c0d9c7f2519a` | `baseline_failed/2`; check 0, teste 1, 115 executados/1 falha; todos os contadores de mutação em zero | `4397929889363d64cebf352e9e767d68405ea51490a571d629a156fb37945106` |
| Duas suítes | `27732709-5293-4cf9-bb99-16d10b5371b4` | `baseline_failed/2`; check 0, teste 0, 115 executados/0 falhas, protocolo rejeitado; todos os contadores de mutação em zero | `47130ab9f48dcd8ae70d9e1198b59ab3219603e4fa8fa6d68646f83fe3860eae` |

Nos casos de detecção/sobrevivência, os demais contadores são zero, não há limitações nem descartes, e o relatório registra a mutação aritmética `+` para `-` como `Killed`/`Survived`. Esses resultados demonstram os estados distintos com a configuração real; não ampliam a aprovação de qualidade para todo o jogo.

### Limitação confirmada e continuidade

Na cópia com `Extra.kf` e `GameJourney.kf`, o comando normal `python3 scripts/kof_project.py test --target jvm --kof kof` terminou com 0. Os logs normais e os logs da fase de teste do KofMut contêm:

```text
Suite: sifuture/game/Extra.kf
0 failed of 1 tests
1 passed, 0 failed
Suite: sifuture/game/GameJourney.kf
0 failed of 114 tests
1 passed, 0 failed
```

O relatório corrente registra `baseline.test.exitCode=0`, `executedTests=115`, `failedTests=0`, mas também:

```text
Invalid or incomplete test protocol
```

Um processo de teste aprovado não garante que seu protocolo seja aceito pelo consumidor. O segundo resumo final é rejeitado pelo trecho de `Evidence.kf` transcrito no aceite anterior; isso explica `baseline_failed/2` sem atribuir falhas aos 115 testes. A compatibilidade com vários arquivos de suíte permanece aberta para trabalho separado, incluindo uma nova prova ponta a ponta após o reparo. Não omitir suítes nem repetir avaliações apenas para contornar a limitação. M2–M5 e S1–S3 continuam pendentes.

### Verificações finais e preservação

Comandos executados na raiz do SiFuture: `python3 .agent/tmp/kof-mut-recipe-fix-20261026/verify_recipes.py` (138 observações, exit 0); `bash -n` sobre os blocos extraídos dos dois guias; verificador local de links Markdown dos dois guias; conferência dos destinos externos e das linhas citadas; `git diff --check`. Os resultados finais e a comparação de preservação estão registrados na continuidade dos planos.

Configuração, escopo, manifesto, wrapper, fontes e testes do jogo permanecem byte a byte iguais à base desta entrega: 49 arquivos protegidos, manifesto ordenado no formato `SHA-256  caminho\n`, SHA-256 `3aa5364846a284d6741d73e75677cb26a11e8be7d4b93a46cf8a285256d3396f`. Os outros 200 arquivos rastreados fora dos quatro arquivos desta entrega permaneceram iguais. Os prefixos históricos de `EXECPLAN.md`, deste aceite e do plano externo foram preservados; a exclusão `/.agent/tmp/` permanece exatamente uma vez em `.git/info/exclude`. As provas anteriores não foram removidas ou sobrescritas. Scripts, blocos extraídos, resultados, controles negativos, hashes e logs novos ficam opcionalmente em `.agent/tmp/kof-mut-recipe-fix-20261026/`; os arquivos de `.agent/tmp/` não entram no versionamento. Não foram repetidos testes do jogo ou navegador, pois somente guia e registros mudaram.

## Continuidade: leitor KofMut para várias execuções — 26/10/2026

O plano aprovado está em implementação no KofMut, base a40b20ac37afac302efc2a0dae7702e44720e166, branch multiple-test-invocations. O leitor anterior falha nos novos cenários públicos; o trecho corrigido passa numa prova isolada com seis formas válidas e catorze inválidas. Essa prova não demonstra a integração real. As tentativas pelo executável público pararam na preparação por prazo de compilação ou orçamento de compatibilidade, antes de aceitar a correção. O check completo está em execução.

As quatro provas SiFuture de 115 casos permanecem pendentes. Os guias ainda conservam a limitação histórica até a prova completa, e nenhum resultado anterior foi reinterpretado como aceite da árvore corrigida. Script descartável em .agent/tmp/multiple-invocations/prove_integration.py usa os blocos Bash existentes, configuração real e um segundo arquivo de suíte, e confere UUID, reportPath da chamada, escopo, retorno, contagens e hashes. Wrapper, configuração, escopo e catálogo permanente continuam iguais à base dc96b0366eee67b3417d58dbe14a06c66e6651aa.

Primeira tentativa real da continuidade: em cópia descartável com Extra.kf e GameJourney.kf, `python3 scripts/kof_project.py test --target jvm --kof kof` aprovou 1 + 114 = 115 casos e zero falhas, exit 0. Os arquivos da cópia e o hash da configuração permaneceram iguais. A receita manual retornou 2 durante preparação do KofMut, por compilação acima de 10000 ms; nenhum reportPath corrente foi anunciado, e a inspeção recusou a ausência em vez de ler um relatório anterior. O leitor corrigido ainda não chegou à avaliação real de Background. Logs e resumo opcionais: .agent/tmp/multiple-invocations/attempt-1/ e integration-blocked.json. Isso deixa a integração e a retirada da limitação pendentes.

Fechamento desta tentativa, sem concluir o aceite: `./scripts/check` do KofMut retornou 1 no CLI, 18 aprovados/13 reprovados de 31 (1308389 ms); as suítes posteriores não foram executadas. A tag final multiple-invocations retornou 1 antes dos cenários públicos, por falha de preparação; o probe interno teve baseline aprovada e mutante Timeout, 8536 ms. Causas de todas as assertions CLI não foram estabelecidas. A prova isolada do leitor corrigido passou os seis formatos válidos e rejeitou catorze inválidos; a mesma expectativa contra o leitor anterior falhou no grupo válido.

A integração real permanece pendente: houve somente testes normais 115/0/exit 0, sem relatório de mutação corrente. Não retirar a limitação dos guias nem reutilizar resultados históricos. Nenhum wrapper/configuração/escopo/fonte/teste permanente mudou: 202 arquivos rastreados protegidos permanecem iguais, e os históricos dos registros e dos planos são prefixos preservados. `git diff --check` passou nos dois repositórios. Identidade e matriz de pendências da implementação estão no novo registro KofMut .agent/validation/multiple-invocations.md e no manifesto correspondente, sobre base a40b20a. Temporários de retomada: .agent/tmp/multiple-invocations/; usar attempt-2 para não substituir evidência.

## Recuperação anterior ao Luna e nova validação — 26/10/2026

A implementação anterior ao Luna foi reconstruída no KofMut a partir da sessão `01a178d1-f353-7300-ad3f-22c8b5fbbb44`. Os dez arquivos coincidiram com o manifesto histórico antes de aplicar o conjunto. O manifesto e o aceite originais permanecem intactos; o novo suplemento é `.agent/validation/multiple-invocations-recovery.md`, no KofMut, sobre base `a40b20ac37afac302efc2a0dae7702e44720e166`; os bytes entregues serão identificados também pelo novo manifesto. A comparação do Luna foi inválida: as oito cópias usavam o leitor da base. Seus logs foram preservados, sem reutilizar sua comparação como prova.

A recuperação preserva o leitor SHA-256 `5e46e9ce8c6a7f8f951b1a46108eb44442d0bdcde624fdc8aa24d71d6a22fc46`, distinto da base `be118bd66eab68887315bba54f119676ae8f9c31d13a3745e821874b95aafded`. Os inventários completos foram verificados antes de novas rodadas sequenciais, com o mesmo Kof 0.6.6, jar SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`. Os limites de 10000 ms por comando, 8500 ms por ensaio interno e 90000 ms para preparação foram preservados. A comparação correta também encontrou prazos excedidos; não estabeleceu regressão de desempenho nem causalidade pela carga.

Resultados públicos finais do KofMut: tag `multiple-invocations` aprovada, 3/3 grupos, exit 0; controle isolado corrigido 2/0 contra controle da base 1/1, com falha esperada no grupo válido. Compatibilidade final exit 1, 7/8 reprovados. O check completo retornou 1 no CLI, 19 aprovados/12 reprovados de 31; Run foi então executada inteira, 34/13 de 47, incluindo os três grupos novos aprovados; Install 16/15 de 31; contratos frontend 15 aprovados, exit 0. Todas as suítes foram tentadas, mas isso não aprova o check que parou no CLI. As treze falhas históricas anteriores foram classificadas: oito têm etapa de preparação identificada, cinco não têm etapa individual estabelecida; as causas internas dos diagnósticos antigos não foram todas comprovadas. Nenhuma causa foi atribuída à carga apenas por observação.

### Quatro provas reais com dois arquivos de suíte

As novas cópias partiram do SiFuture `a451d311fe3beb7f37cbfd517aa96bbbb102a14b`. Usaram as receitas Bash existentes e a configuração real SHA-256 `2e24df1360b021bbf30d4cf4f7fdcdcf1cec202d601a45b018c61b65d8fda9bd`, sem omitir suítes. Background usa Extra + GameJourney; os três cálculos usam GameJourney + ZProbe, acrescentados somente às cópias. O catálogo permanente continua com 114 casos.

| Cenário | Testes normais, casos/falhas/exit | Resultado da própria chamada de mutação | Baseline check/test ms | Arquivos da cópia preservados |
| --- | --- | --- | --- | --- |
| background | 115/0/0 | incomplete/3, zero mutantes | 7307/10033 | 190, bytes e modos iguais |
| detected | 115/0/0 | incomplete/3, zero mutantes | 7572/10032 | 191, bytes e modos iguais |
| survived | 115/0/0 | incomplete/3, zero mutantes | 7304/10037 | 191, bytes e modos iguais |
| baseline-failed | 115/1/1 | incomplete/3, zero mutantes | 6231/10033 | 191, bytes e modos iguais |

| Cenário | UUID próprio | SHA-256 do relatório anunciado |
| --- | --- | --- |
| background | 68f9e38e-99ed-40c3-b33d-d11626d36874 | 27cfa3620ffee7fa7b6927e120ac2bf8b35caf496a786209d4ab1957f3f6bcf4 |
| detected | b15ef54a-c1cd-468e-b080-5e165f5c657b | eb4e5cab69cdd891d3a6affcafb728e5f5030936f1a8d6618035955ad7440502 |
| survived | f2304068-4a33-45cc-8cef-cff679c0bc9a | ce9faeaab2f428fbf9c88ae4da4a792afa018d04a7b99942f5c9f4ff4047c4d2 |
| baseline-failed | d12f6354-fad8-4098-a3ef-d052ce17b17f | d78e851f17658dd5df9ddcca08a8d9e447d2e0955e45a5a3afcccbe849d94dda |

Conferidos UUID, esquema/versões, namespace canônico, único `reportPath=` anunciado pela chamada, escopo e retornos da ferramenta/receita/inspeção. Background tem escopo `src/main/kof/sifuture/game/Background.kf`; os demais usam `src/main/kof/sifuture/game/ManualMutationProbe.kf`. Todos os relatórios registram check exit 0/filesChecked 1, teste da baseline exit 137 com `test timeout`, nenhum candidato ou mutante e todos os contadores de mutação em zero. Isso não equivale a detectar/sobreviver nem à baseline_failed/2 exigida para o controle inicialmente falho: a fase de teste não terminou. O contador timeout dos mutantes fica zero porque o prazo foi excedido antes de gerar mutantes.

Tempos informados pelo CLI nos comandos normais, em chamadas sequenciais: Background 4165+7820=11985 ms; detectado 9472+5928=15400 ms; sobrevivente 9776+5865=15641 ms; baseline falha 8384+5441=13825 ms. Essas somas já excedem os 10000 ms do comando completo do wrapper, antes de contar preparação e inicialização. Trecho real do log Background:

```text
time: 4165ms total, slowest /tmp/sifuture-kof-4_tdaj9w/source/Main.kf (4165ms)
time: 7820ms total, slowest /tmp/sifuture-kof-ldl44t_v/source/Main.kf (7820ms)
```

O [laço do wrapper](../../scripts/kof_project.py#L152) chama `_run` de forma síncrona para cada arquivo. Não há sobreposição que invalide a soma. Os logs das baselines mostram o segundo arquivo iniciado quando o processo foi encerrado. O prazo foi demonstrado; a causa completa da demora continua desconhecida. Os 10032–10037 ms medidos incluem o encerramento do grupo de processos, sem ampliar o limite de espera.

O aceite completo permanece pendente. É necessária uma decisão entre repetir em condições controladas que cumpram os prazos existentes ou rever explicitamente os limites e restrições da receita. Nenhuma ampliação foi aplicada, e nenhum relatório anterior substituiu o da chamada. Os guias mantêm a limitação até a aprovação pública e dos quatro resultados reais exigidos. Configuração, wrapper, escopo e catálogo permanentes continuam iguais; M2–M5 e S1–S3 não são encerrados. Não houve commit, publicação, worktree, subagente ou alteração do Kof.

Evidência local opcional: `.agent/tmp/recovery-20261026/integration/`, com quatro cópias preservadas, stdout/stderr/exits, inventários e relatórios próprios. O suplemento KofMut contém comandos, resultados, fontes do mecanismo, lacunas e o novo manifesto; este registro conserva os resultados essenciais sem depender desses arquivos locais.

Conferência final: 202 arquivos rastreados protegidos mantêm bytes e modos iniciais; configuração/escopo/manifesto/wrapper/src/tests (49 arquivos), os dois guias e os blocos Bash aprovados permanecem iguais. Prefixos históricos deste plano/aceite e do plano externo preservados. Kof permanece limpo e o jar tem o mesmo SHA-256; exclusão Git local aparece uma vez. O verificador de links do histórico completo sinaliza 51 ocorrências já presentes na base; comparação contra os textos de HEAD produz exatamente as mesmas mensagens e nenhuma aponta para a continuidade nova. `git diff --check` passou. O [novo manifesto](kofmut-recovery.sha256) identifica esta continuidade e os arquivos protegidos, sem substituir o manifesto anterior do KofMut. O aceite continua pendente; nenhuma limitação foi retirada dos guias.


<a id="kofmut-timeout-acceptance"></a>

## Aceite dos limites autorizados e de duas suítes — 26/10/2026

Continuidade aprovada sobre SiFuture `54c317b52d010fbfa94e28499b05610d3ee62077` e KofMut `e8a08b6478d02bfd6d8e1158c2c9e9c913bc82b6`, com alterações sem commit desta sessão. Kof 0.6.6 Linux/JVM, jar SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`. Os fracassos e manifestos anteriores permanecem históricos; esta seção registra uma rodada nova, sem substituir seus relatórios.

O plano fornecido pelo usuário autoriza `commandTimeoutMs: 30000` no SiFuture, 30000 ms por compilação/ensaio da preparação e 25000 ms por ensaio interno de mutação no KofMut. Mantidos: comandos internos em 10000 ms, preparação inteira em 90000 ms desde o início incluindo espera, limpeza compartilhada em 2000 ms, `budgetMs: 0`, concorrência 1, wrapper, escopo e catálogo permanente. Não houve aumento automático, modificação/atualização do Kof, commit, publicação, worktree, subagente ou instalação de sensores.

Configuração avaliada, [`kof-mut.json`](../../kof-mut.json#L14):

```json
"commandTimeoutMs": 30000,
"budgetMs": 0,
"maxParallelMutants": 1
```

SHA-256 da configuração: `a0303c0cd6fa65cb2e7d33e056a4e642a1f8dda00a1432b7d8b7bb3df6027f65`. Esse limite cobre o comando completo do wrapper, incluindo as chamadas sequenciais dos dois arquivos; cada arquivo não recebe um novo prazo. `budgetMs: 0` remove somente o orçamento total da avaliação, sem remover o timeout de cada comando.

| Prova nova | UUID | Estado/retorno | Killed/Survived | Segundos externos |
| --- | --- | --- | --- | ---: |
| background | `5edef194-8273-4eec-ac36-5554e9955b8f` | `complete/0` | 1/0 | 14.757 |
| detected | `660fb933-dfd0-45ae-9e29-61ea54e4b595` | `complete/0` | 1/0 | 15.538 |
| survived | `11984982-2786-4c42-b093-d32382099039` | `complete/1` | 0/1 | 15.543 |
| baseline-failed | `3612b9e3-4b33-49f7-8f95-ef33481848da` | `baseline_failed/2` | 0/0 | 8.912 |

Cada chamada usa sua própria receita Bash documentada e sua própria inspeção, sem buscar o relatório mais recente. Foram conferidos `reportPath=`, UUID, namespace canônico, escopo, schema v1, Kof 0.6.6, baseline, contagens e os retornos nativo/receita/inspeção. Background usa o arquivo completo de produção; os cálculos usam apenas `ManualMutationProbe.kf` nas cópias descartáveis. As três primeiras baselines têm 115 casos/zero falhas e um mutante avaliado; a quarta tem 115 casos/uma falha e nenhum candidato ou mutante. Todos os outros contadores são zero, sem descartes ou limitações. As cópias preservam os 190/191/191/191 arquivos de entrada em bytes e modos. O comando normal do wrapper também foi executado separadamente: 115 casos, falhas 0/0/0/1, retornos 0/0/0/1.

| Relatório da própria chamada | SHA-256 |
| --- | --- |
| background | `738d5a24dece97084fb9107dab8ba6a23b586e3e64a807d76edfa4803ae18340` |
| detected | `9d8be817f01facbb158c96ef75aba4f2353e5d309fe0cef7cade12152614213f` |
| survived | `c3bff6ccc1cf91d6a298621109e578c636615bfe65a2238c829c95ca1715534b` |
| baseline-failed | `9708097c19bdfcfec8da0e7a2b39c80495d28404ce94cb4c0edefdb83778eae0` |

A auditoria das expectativas confirma: `(2 + 3)` e `(2 - 3)` distinguem detecção; com segundo argumento zero a alteração deve sobreviver; esperar 6 quando o cálculo retorna 5 reprova a situação original e impede toda mutação. O teste real de Background verifica deslocamento de cinco unidades. A auditoria separada da capacidade da prova rejeitou 58 controles com identidade, escopo, estado, contagem ou relatório de outra chamada incorretos. No cálculo detectado, o stdout do mutante mostra que a falha veio do segundo arquivo:

```text
Suite: sifuture/game/GameJourney.kf
0 failed of 114 tests
Suite: sifuture/game/ZProbe.kf
FAIL probe contract: assertion failed
1 failed of 1 tests
```

Isso demonstra o acúmulo dos 115 casos e a preservação da falha após uma primeira suíte aprovada. O resultado Survived/1 é esperado nessa prova e reprova qualidade; não é convertido em aprovação de testes.

Na raiz do KofMut, validação nova e sequencial:

| Comando | Retorno | Segundos externos |
| --- | --- | ---: |
| `kof test src/test/kof/kofmut/Cli.kf --tag compatibility` | 0 | 296.540 |
| `kof test src/test/kof/kofmut/Run.kf --tag multiple-invocations` | 0 | 86.363 |
| `./scripts/check` | 0 | 2822.044 |

Compatibilidade: 9/0; várias execuções: 3/0; check completo: CLI 32/0, ciclo 47/0, instalação 31/0, frontend 15/0. O compilador controlado atrasado em 11 s falha com o limite antigo e conclui com o novo. Os ensaios reais lentos de detecção/sobrevivência levam 10008/9608 ms, acima de 8500 e abaixo de 25000. Bloqueio retorna 2 após cerca de 30 s, sem aprovação nem avaliação do projeto, com limpeza e recuperação normal. O check completo inclui a prova de interrupção da preparação aos 90 s e a preservação das recusas por evidência inválida ou falha real. [Suplemento completo do KofMut](../../../kof-mut/.agent/validation/multiple-invocations-recovery.md#authorized-timeout-integration-acceptance-2026-10-26).

Aceite desta continuidade concluído: preparação, check completo e quatro provas reais aprovados. A ressalva obsoleta sobre rejeição de um segundo resumo pode ser retirada dos dois guias. A prova cobre a árvore avaliada e JVM; não promete duração universal, não instala gatilhos e não encerra M2–M5/S1–S3. Evidências locais opcionais em `.agent/tmp/timeouts-20261026/`, com logs, tempos, receitas, relatórios, inventários e auditorias; os resultados essenciais acima permitem compreender o aceite sem esses arquivos.


Conferência final: `git diff --check` retorna 0 nos dois repositórios. O check completo mede a interrupção da preparação em 90026 ms monotônicos/90027 ms de relógio; uma avaliação já confirmada com orçamento zero executa 94097 ms no motor, 95220 ms externos. São prazos distintos: uma avaliação longa não reinicia nem prolonga a preparação.

Preservação independente: 205 arquivos rastreados iniciais no SiFuture, cinco alterações autorizadas e 200 iguais em bytes/modos; 145 no KofMut, onze alterações autorizadas e 134 iguais. Planos e aceites anteriores são prefixos intactos; todos os manifestos SHA-256 históricos, wrapper, escopo, catálogo, receitas Bash bilíngues, os 44 inputs congelados do check e o jar instalado permanecem preservados. Kof de pesquisa continua limpo. A exclusão Git local aparece exatamente uma vez em cada repositório. O verificador de links mantém exatamente os diagnósticos dos textos de HEAD: 51 no conjunto Markdown alterado do SiFuture e 14 no KofMut, nenhum novo; esses problemas históricos não foram apresentados como links globalmente aprovados. Links novos passam. Inventários e auditorias novos ficam em `.agent/tmp/timeouts-20261026/`, fora de commits. Não resta lacuna obrigatória para este aceite dos limites e de várias execuções.

<a id="meteor-survivor-acceptance"></a>

## Aceite: sobreviventes de Meteor e escopo manual — 26/10/2026

Árvore testada: base SiFuture `fc74cb777c602f9745551d3a39f697a2b4a26652`
mais o diff local desta entrega, na branch `sensor-calibration-m1`. Produção,
assets, wrapper, KofMut e limites não foram modificados. O catálogo permanece
com 114 casos: quatro cenários existentes foram ampliados, sem duplicar suítes.
A fixture visual usa `collide()` e `impactFrame()`. O escopo explícito contém
os arquivos inteiros Background e Meteor.

### Expectativas: auditoria do contrato

A [especificação aprovada](../specifications/port-sifuture-to-kof.md#historical-gameplay)
exige preservar regras históricas, com seed injetável nos testes e uma recompensa
por contato da nave. A revisão histórica é `50fc40d04acd0f3f2a6dd103c0fc3121608bd4e3`
em `/home/renanfranca/projects/sifuture`. O código histórico foi lido, não
executado nesta entrega. Em [Meteor.java](../../../sifuture/src/Meteor.java#L111):

```java
this.y = Math.abs(random.nextInt() % BACK_GROUND_HEIGHT) + StageCount.stage1.getHeight();
```

Essa expressão soma o cabeçalho ao sorteio. Em Kof, o cenário com seed 71 foi
executado e exige y=201; outros cem resets exigem x entre 176 e 375 e y entre
30 e 201. A equivalência de seeds entre Java histórico e Kof não é alegada.
O [idioma de stdlib](../../../kof/training/idioms/stdlib.md#rng--determinism-you-can-test-x8-slices-12)
mostra a intenção de usar seed explícita:

```kof
rng.seed(42)
```

A seed fixa torna a expectativa reproduzível. O resultado exato de seed 71
vem da execução atual nos dois alvos, sem depender da versão antiga do corpus.
O limite histórico em [Meteor.java](../../../sifuture/src/Meteor.java#L149) é:

```java
this.x --;
if (this.x < INVISIBLE_LEFT_POSITION){
```

Portanto sair de -24 para -25 ainda não relança. O passo seguinte deve
relançar. O cenário ampliado verifica os dois lados do limite estrito.

A animação histórica em [Meteor.java](../../../sifuture/src/Meteor.java#L190)
usa `timing=2` no reset horizontal e avança `collisionDraw` até três imagens.
A expectativa permanente lê a API usada pelo desenho, em
[GameJourney.kf](../../src/test/kof/sifuture/game/GameJourney.kf#L722):

```kof
assert(g.meteors[0].impactFrame() == 0)
var expectedFrames = listOf(0, 1, 1, 2, 2)
```

Cada avanço consulta `impactFrame()`, cobrindo 0/0/1/1/2/2; no sexto passo
o impacto termina e o meteoro relança. A divisão por dois não é repetida
na assertion nem na fixture. O browser também compara pixels dos três sprites.

O contato histórico em [AirShip.java](../../../sifuture/src/AirShip.java#L374)
usa a borda esquerda do meteoro, com limites inclusivos nos dois eixos. A
[expressão Kof](../../src/main/kof/sifuture/game/Meteor.kf#L83) preservada é:

```kof
return x >= shipX && x <= shipX + Rules.SHIP_WIDTH &&
    ((y >= shipY && y <= shipY + Rules.SHIP_HEIGHT) ||
     (y + Rules.METEOR_HEIGHT >= shipY && y + Rules.METEOR_HEIGHT <= shipY + Rules.SHIP_HEIGHT))
```

Com nave (60,100), x=60/110 toca e x=59/111 não toca em y=105;
em x=80, y=82/120 toca e y=81/121 não toca. O teste verifica a função
isoladamente e a consequência em Game. O meteoro começa em x+1 porque Game
move antes de testar o contato. Os demais meteoros ficam inativos; armas
recém resetadas não têm projéteis ativos e não chegam ao intervalo de disparo
nos dois passos observados. Exige colisão, explosão e cinco pontos, conservados
no passo posterior aos contatos. O caso x=111 só é ausência no primeiro passo:
no segundo ele entra em x=110; não se exige ausência artificial nesse ponto.

A regra Kof de classe mutável usa campos públicos e atribuição direta. A
[referência de classes](../../../kof/docs/language-reference/classes.md#1-classes-mutable-state)
registra:

> **Fields are public by default** (no `private`); direct write.

O [idioma de classes](../../../kof/training/idioms/classes.md#explicit-constructor--mutable-state-the-real-class-form)
e [Learn Kof 07](../../../kof/learn/07-classes-and-objects.md#3-mutable-state--class-with-fields--constructor)
orientam esse uso. As fixtures alteram campos para posicionar entidades e
consultam métodos para observar comportamento. Learn 23 define o teste:

> Inside the test, `assert(cond[, "msg"])` marks the failure with a clear message.

Fonte: [Learn Kof 23](../../../kof/learn/23-testing.md#23--testing).
O contrato atual também é exercitado por
[StructuredTestE2ETest](../../../kof/kof-compiler/src/test/java/dev/kof/compiler/StructuredTestE2ETest.java#L146),
que exige exit 1 e a mensagem da assertion falha. Aqui as provas foram
executadas nos alvos JVM e JS, não apenas compiladas.

### Equivalências: condições e prova

Os offsets abaixo pertencem aos bytes preservados de `Meteor.kf`; o ID completo
é `src/main/kof/sifuture/game/Meteor.kf:<offset>:<replacement>`.

**106:false e 255:true, somente no fluxo Game.** O estado inicial da classe
é observável e diferente antes de reset. Não há equivalência geral de Meteor.
O [início da partida](../../src/main/kof/sifuture/game/Game.kf#L109) sempre faz:

```kof
for (var m in meteors) { m.reset() }
```

O reset chama `relocate()` e depois `clearAnimation()`, que contém:

```kof
active = motion == MeteorMotion.Horizontal
frame = 0
frameDirection = 1
frameSteps = 0
collisionSteps = 0
collided = false
```

Fonte: [Meteor.clearAnimation](../../src/main/kof/sifuture/game/Meteor.kf#L42).
Nenhum dos dois valores iniciais é lido por `relocate()`. Após reset, todos
os campos coincidem para ambas as direções com a mesma seed. O fluxo de
[Game.step](../../src/main/kof/sifuture/game/Game.kf#L195) retorna em Credits,
Menu e Controls antes de avançar meteoros; a
[renderização](../../src/main/kof/sifuture/GameView.kf#L77) também retorna nessas
telas antes de ler meteoros. Pause/Result normais são alcançados depois de start.
Assim os valores iniciais não influenciam a partida válida; acesso externo
antes de start, escrita arbitrária de `screen` ou uso direto de Meteor não
pertencem a essa prova. Cada um desses dois mutantes exatos também executou
a suíte ampliada de 114 casos, sem falhas, em JVM e JS.

**2526:> e 2647:<, com as dimensões do jogo e sem overflow.**
São alterações individuais, mantendo a outra cláusula do `||` original.
No primeiro caso a única diferença possível é y=shipY. Nesse ponto,
y+18 fica dentro de [shipY,shipY+20], logo a segunda cláusula continua verdadeira.
No segundo caso a única diferença possível é y+18=shipY+20, isto é,
y=shipY+2. A primeira cláusula continua verdadeira. Se x não satisfaz o limite
horizontal, ambas as versões já retornam falso. Isso prova a redundância,
sem depender de não encontrar um contraexemplo. Alturas diferentes ou aritmética
fora do domínio válido não são abrangidas.

Como confirmação executável, cópias das classes com os quatro edits exatos
foram criadas somente na preparação temporária. Para os limites, foram
comparados original e cada mutante para shipY=30..200, meteorY=-172..221
e x=59/60/80/110/111, nave x=60. A condição horizontal comum e a dependência
vertical apenas da diferença entre coordenadas sustentam a análise dos demais
x válidos. Resultado de `kof run <preparação>/Main.kf --target jvm` e do mesmo
comando com `--target js`, ambos exit 0:

```text
equivalent boundary comparisons=673740
initial values differ before reset and converge after reset for both motions
```

Cada alvo realizou 673740 comparações entre o resultado original e o mutante.
O domínio inclui as fronteiras verticais válidas sem overflow. A primeira
tentativa do harness passou um diretório a `kof run` e foi recusada com COMP001;
foi corrigida para o arquivo Main.kf, sem mudar Kof ou limites. Somente as
execuções corrigidas são evidência. Scripts e logs locais opcionais ficam
em `.agent/tmp/meteor-acceptance-20261026/`; as condições e a demonstração
matemática acima tornam a justificativa compreensível sem esses temporários.

### Capacidade das provas: auditoria separada

A rodada final confirma que os nove casos não equivalentes falham por
assertion no teste correspondente, sem classificar erro de compilação como
detecção. O verificador local conferiu identidade, caminho anunciado, escopo,
versões, baseline, unicidade e composição dos IDs, localização/tokens atuais,
contadores, resultados e logs. Rejeitou 21 controles alterados: UUID de outra
chamada, escopo antigo, versões, estado, limitações, descartes, cada contador,
resumo de baseline, ID e classificação. Uma primeira versão da auditoria não
rejeitou um ID adulterado do candidato de Background; a conferência foi
corrigida para exigir `file:offset:replacement` em todos os IDs antes do aceite.
O parser de logs também foi ajustado para distinguir a linha FAIL do arquivo
das linhas FAIL de assertions. Essas correções do instrumento local não
modificaram o jogo nem o relatório.

Os treze sobreviventes anteriores estão classificados abaixo. Todos tinham
resultado anterior `Survived`; a coluna final preserva a classificação bruta.
Cada contato discriminatório também exige a consequência de Game descrita
acima, e não apenas uma chamada sem falha.

| Offset:replacement | Linha e edit | Regra, teste discriminatório ou prova | Final |
| --- | --- | --- | --- |
| `106:false` | 5: `true` → `false` | Equivalência no fluxo Game: reset sobrescreve active antes do uso. | `Survived` |
| `255:true` | 13: `false` → `true` | Equivalência no fluxo Game: reset limpa collided antes do uso. | `Survived` |
| `715:-` | 25: `+` → `-` | Soma do cabeçalho: seed 71 exige y=201; faixa 30..201. | `Killed` |
| `1512:<=` | 57: `<` → `<=` | Saída estrita: -24 avança para -25 sem relançar; só depois relança. | `Killed` |
| `2364:*` | 80: `/` → `*` | impactFrame(): 0/0/1/1/2/2; a multiplicação erra já no passo 1. | `Killed` |
| `2465:>` | 84: `>=` → `>` | Contato horizontal inclusivo: x=60 deve tocar. | `Killed` |
| `2526:>` | 85: `>=` → `>` | Equivalência geométrica: em y=shipY a segunda cláusula cobre o contato. | `Survived` |
| `2540:<` | 85: `<=` → `<` | Contato vertical inclusivo: y=120 deve tocar. | `Killed` |
| `2589:-` | 86: `+` → `-` | Base do meteoro usa +18: y=82 deve tocar. | `Killed` |
| `2611:>` | 86: `>=` → `>` | Contato vertical inclusivo: y+18=100 deve tocar. | `Killed` |
| `2625:-` | 86: `+` → `-` | Limite da base usa +18: y=121 deve ficar fora. | `Killed` |
| `2647:<` | 86: `<=` → `<` | Equivalência geométrica: em y=shipY+2 a primeira cláusula cobre o contato. | `Survived` |
| `2656:-` | 86: `+` → `-` | Limite da nave usa +20: y=82 deve tocar. | `Killed` |

Os 28 IDs antes detectados continuam `Killed`. A tabela inclui também o
candidato de Background, ausente da medição anterior de Meteor. O nome do
caso abaixo foi extraído da falha real de assertion; linha e edit identificam
a expressão da regra preservada. Para Meteor, o prefixo do ID é o mesmo
explicitado acima; Background usa `src/main/kof/sifuture/game/Background.kf`.

| Arquivo, offset:replacement | Linha e edit da regra | Antes → final | Assertion que detectou |
| --- | --- | --- | --- |
| `Background.kf:123:-` | 8: `+` → `-` | não avaliado → Killed | background moves five units wraps at sixty and pauses |
| `Meteor.kf:390:!=` | 18: `==` → `!=` | Killed → Killed | vertical initial and impact resets keep reduced range while bottom exits include both full endpoints |
| `Meteor.kf:513:+` | 20: `-` → `+` | Killed → Killed | vertical initial and impact resets keep reduced range while bottom exits include both full endpoints |
| `Meteor.kf:657:-` | 24: `+` → `-` | Killed → Killed | same seed reproduces meteors and horizontal resets stay below the header |
| `Meteor.kf:1089:!=` | 43: `==` → `!=` | Killed → Killed | vertical bottom exit uses full historical range and waits inactive with clean animation |
| `Meteor.kf:1230:true` | 48: `false` → `true` | Killed → Killed | vertical bottom exit uses full historical range and waits inactive with clean animation |
| `Meteor.kf:1310:!=` | 53: `==` → `!=` | Killed → Killed | vertical bottom exit uses full historical range and waits inactive with clean animation |
| `Meteor.kf:1356:-` | 54: `+` → `-` | Killed → Killed | vertical bottom exit uses full historical range and waits inactive with clean animation |
| `Meteor.kf:1395:>=` | 55: `>` → `>=` | Killed → Killed | boss absorbs inclusive meteors before player contacts with one movement and suppresses vertical relaunch |
| `Meteor.kf:1475:+` | 56: `-` → `+` | Killed → Killed | laser hit holds meteor collision images for three pairs of steps |
| `Meteor.kf:1705:-` | 63: `+` → `-` | Killed → Killed | vertical initial and impact resets keep reduced range while bottom exits include both full endpoints |
| `Meteor.kf:1782:!=` | 65: `==` → `!=` | Killed → Killed | vertical initial and impact resets keep reduced range while bottom exits include both full endpoints |
| `Meteor.kf:1856:!=` | 66: `==` → `!=` | Killed → Killed | one ship collision marks every overlapping meteor and scores once |
| `Meteor.kf:1934:-` | 68: `+` → `-` | Killed → Killed | meteor sprite advances every two steps and returns through the historical frames |
| `Meteor.kf:1965:!=` | 69: `==` → `!=` | Killed → Killed | meteor sprite advances every two steps and returns through the historical frames |
| `Meteor.kf:2057:-` | 71: `+` → `-` | Killed → Killed | meteor sprite advances every two steps and returns through the historical frames |
| `Meteor.kf:2100:!=` | 72: `==` → `!=` | Killed → Killed | meteor sprite advances every two steps and returns through the historical frames |
| `Meteor.kf:2123:+` | 72: `-` → `+` | Killed → Killed | meteor sprite advances every two steps and returns through the historical frames |
| `Meteor.kf:2178:!=` | 73: `==` → `!=` | Killed → Killed | meteor sprite advances every two steps and returns through the historical frames |
| `Meteor.kf:2282:!=` | 79: `==` → `!=` | Killed → Killed | laser hit holds meteor collision images for three pairs of steps |
| `Meteor.kf:2474:||` | 84: `&&` → `||` | Killed → Killed | finishing with right held restores normal ship while score counts and position freezes |
| `Meteor.kf:2479:<` | 84: `<=` → `<` | Killed → Killed | ship meteor contact includes each boundary and excludes adjacent positions |
| `Meteor.kf:2488:-` | 84: `+` → `-` | Killed → Killed | three meteor hits end the attempt and result persists |
| `Meteor.kf:2507:||` | 84: `&&` → `||` | Killed → Killed | normal fire starts on thirteenth step and earns five points |
| `Meteor.kf:2535:||` | 85: `&&` → `||` | Killed → Killed | normal fire starts on thirteenth step and earns five points |
| `Meteor.kf:2549:-` | 85: `+` → `-` | Killed → Killed | ship meteor contact includes each boundary and excludes adjacent positions |
| `Meteor.kf:2570:&&` | 85: `||` → `&&` | Killed → Killed | ship meteor contact includes each boundary and excludes adjacent positions |
| `Meteor.kf:2620:||` | 86: `&&` → `||` | Killed → Killed | normal fire starts on thirteenth step and earns five points |
| `Meteor.kf:2720:false` | 90: `true` → `false` | Killed → Killed | vertical initial and impact resets keep reduced range while bottom exits include both full endpoints |

### Execução e identidade finais

Kof 0.6.6, jar SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`;
fontes de pesquisa `7c237861a9035d84b1f7ec4cfddd89daef4c6ddd`. KofMut 0.1.0,
checkout limpo `338c7b3501d2ec91a9072f1e68ac827aae7f5d36`. A qualificação do
[aceite anterior](#kofmut-timeout-acceptance) foi reutilizada: todos os 44
inputs congelados do check anterior coincidem em SHA-256, incluindo os seis
inputs alterados naquela entrega. SHA-256 do inventário histórico desses
44 inputs: `c338f8fb4498c15c08ad351fc0c767717263efadafefb6cb5abf90a15a28af22`.
A ferramenta e seus limites não foram modificados nem requalificados nesta
entrega. Fontes locais de Kof e o jar também permaneceram iguais.

| Comando no checkout SiFuture | Retorno | Resultado |
| --- | ---: | --- |
| `python3 scripts/kof_project.py test --target jvm --kof kof` | 0 | 114 casos, zero falhas |
| `python3 scripts/kof_project.py test --target js --kof kof` | 0 | 114 casos, zero falhas |
| `python3 tests/browser_meteor.py --kof kof` | 0 | Chrome 155.0.8059.39, sprites/posição nos seis instantes e relançamento, sem pageerror |
| Receita Bash manual do guia | 1 | complete, 42 executados, 38 Killed, 4 Survived |
| Inspeção Bash da mesma chamada | 1 | Mesmo UUID, baseline, escopo, contagens e estado |
| `git diff --check` | 0 | Sem erro de whitespace |

Saídas essenciais dos comandos de teste e navegador:

```text
0 failed of 114 tests
1 passed, 0 failed
PASS moving meteor, three impact frames, and respawn in Chrome
```

O primeiro resumo aparece em cada alvo. O navegador foi automatizado, não uma
aceitação manual de conforto. O percurso clica Next step cinco vezes e compara
as posições 100..95 e os três sprites, depois verifica relançamento no sexto
clique. Outros browsers e Android físico não foram avaliados nesta entrega.

A receita e a inspeção são os blocos literais dos dois guias, sem mudanças.
UUID novo: `05f9192d-a6fe-47f2-a524-aeecaf451152`. Somente o `reportPath=` anunciado
por essa chamada foi lido; seu namespace coincide com o SHA-256 do caminho
canônico do projeto. Schema 1, toolVersion 0.1.0, kofVersion 0.6.6.
SHA-256 do JSON final: `3f3561d2f144cb9eac693455e26b97f3b305379f0f30a58ad2eb8073ef370b58`.
Duração registrada pelo motor: 217821 ms. Baseline check/test:
exit 0/0, filesChecked 1, 114 casos e zero falhas. Resultado bruto:

```text
candidates=42 killed=38 survived=4 compileError=0 timeout=0 testError=0 pending=0
```

Executados 42/42, sem descartes ou limitações. Background: 1 Killed de 1;
Meteor: 37 Killed e 4 Survived de 41. Os 28 Killed anteriores foram
reconciliados por ID e permanecem detectados. Nove dos treze sobreviventes
anteriores agora são Killed por assertions; quatro têm prova e limite de
equivalência acima. Os retornos nativo/receita/inspeção são 1/1/1. Não houve
exclusão, supressão nem conversão do relatório para complete/0.

A medição anterior tinha UUID `101c64fe-d24d-4edc-85e0-ebb1882950d9`,
41/41 executados, 28 Killed e 13 Survived, baseline 114/0. Seu relatório foi
preservado e conferido pelo SHA-256
`13da3e3f9dcb5534b3119fccd964b74d1f7d3603e9e8786659850f164d5e7dc1`.

Árvore efetivamente avaliada, identificada além do SHA base:

| Arquivo | SHA-256 |
| --- | --- |
| `src/test/kof/sifuture/game/GameJourney.kf` | `dae75a75b698a2a8cf511ddf42348d85036480f70856316ab9ba11de02f4acdc` |
| `tests/meteor-motion.kf` | `6c8d34e454ade14fec184f29971ad6b53df20df88e72ef926f8b3db977f1bc99` |
| `kof-mut-scope.json` | `7e8bb7355756433158856fd993719c0ad075d167b1efff6ab673338f203e7f0d` |
| `kof-mut.json` | `a0303c0cd6fa65cb2e7d33e056a4e642a1f8dda00a1432b7d8b7bb3df6027f65` |
| `src/main/kof/sifuture/game/Meteor.kf` | `e8c61d89c178f3ffcd98c1b871d9de1ab0a89e5895ffe425dee5d02852ccf9c6` |
| `src/main/kof/sifuture/game/Background.kf` | `d917f9e661f1988b682ecac9779a93870757e8b1fd890b77908652ad45e88706` |

Os históricos deste aceite, do EXECPLAN e do plano externo foram preservados
como prefixos. Produção/assets, KofMut, limites e receitas permanecem iguais;
a exclusão local `/.agent/tmp/` aparece uma vez. A auditoria final identifica
os sete arquivos rastreados autorizados e verifica todos os demais por bytes
e modos. Evidências geradas permanecem fora de commits. Não houve commit,
worktree, subagente, publicação, hooks ou instalação de sensores. Não há nova
execução CI nem workflow de entrega para este diff local; a prova é local.
Este aceite fecha as lacunas identificadas de Meteor e justifica todos os
sobreviventes desse escopo. Não amplia a conclusão para outras mutações,
classes ou domínios, nem encerra M2–M5/S1–S3 históricos.

Conferência final da entrega: dos 205 arquivos rastreados iniciais, sete têm
alterações autorizadas e os outros 198 preservam bytes e modos. Os vinte links
novos do aceite/guias foram conferidos contra arquivos e âncoras locais;
nenhuma aprovação global dos links históricos é alegada. Blocos Bash de
execução/inspeção são idênticos aos de HEAD em ambos os idiomas. Os históricos
dos dois planos e do aceite permanecem como prefixos, KofMut/Kof estão limpos
e `git diff --check` retorna 0. Os hashes da suíte, fixture, escopo e configuração
acima identificam os mesmos bytes usados na rodada de mutação e nos testes.
