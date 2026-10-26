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
