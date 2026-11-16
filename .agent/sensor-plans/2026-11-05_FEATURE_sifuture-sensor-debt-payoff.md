# Pagamento da dívida dos sensores antes do M3

> **Para a sessão executora:** plano decidido com o usuário em 05/11/2026. Trabalhar em `/home/renanfranca/projects/kof-sifuture`. Sem worktree, sem subagentes, **sem commit nem push** (o usuário faz com Luna). O anexo no fim deste arquivo é o plano do M2, já executado; não executar o anexo.
>
> Antes de começar:
> - copiar este plano (até a linha do anexo) para `/home/renanfranca/.agents/skills/_temporary/codex-skills-ai-context/2026-11-05_FEATURE_sifuture-sensor-debt-payoff.md` e trabalhar a partir dessa cópia;
> - ler o `AGENTS.md` inteiro, o training index do Kof e, antes de mexer em testes, `training/tooling/cli.md`, `training/examples/testing.kf` e `learn/23-testing.md`; antes de cada refatoração Kof, os `training/idioms/` e `training/anti-patterns/` do tema;
> - conferir: `main` contém `6b17e1c` (o M2 já foi mergeado); checkout limpo na `main`; `kof version` = `kof 0.7.0`; 0.6.4 em `~/.local/share/kof/kof-0.6.4-linux-x86_64`; `npm run sensors:doctor` sem MISSING. **Se o M2 não estiver na `main`, parar e avisar.**
> - criar a branch `sensor-debt-payoff` (validar com `git check-ref-format --branch` e conferir que não existe local nem remota; usar o skill `create-git-branch`);
> - comportamento novo (matar mutantes) usa o skill `tdd-behavior-autonomous-quiet`; refatoração sem mudança de comportamento usa o skill `refactor-design`. Os dois pelo Skill tool. Sem comentários no código (AGENTS vence os skills).
>
> Marco grande, para várias sessões. Ao fim de cada etapa (R0 a R7), atualizar o `EXECPLAN.md` e a cópia do plano, para outra sessão poder retomar.

## Context

O M2 entregou os sensores baratos e o `check`. A revisão de 05/11 mediu a dívida: a única suíte, `src/test/kof/sifuture/game/GameJourney.kf` (2903 linhas), tem 334 achados (207 `looping-test`, 52 `branching-test`, 38 `high-complexity`, 28 `unnamed-arrange`, 8 `deep-nesting`, 1 `long-file`); 13 arquivos de produção têm 70 achados; há 19 grupos CPD em `src/` e mais 3 nas fixtures; as fixtures `tests/*.kf` têm 17 achados; o `Meteor.kf` tem 4 mutantes sobreviventes. A regra decidida analisa o arquivo tocado **inteiro**, e o Stop do M3 bloqueia no máximo 3 vezes por sessão. Com essa dívida, o primeiro toque esgotaria o bloqueio. **Decisão do usuário (05/11): pagar toda a dívida antes do M3, inclusive fixtures e sobreviventes, mantendo a regra do arquivo inteiro.** Resultado esperado: `npm run sensors:debt` sem nenhum achado, e o KofMut sem sobreviventes na produção alterada.

## Regras invioláveis

- **O jogo não muda de comportamento.** As únicas mudanças de comportamento permitidas são testes novos para matar mutantes. Guardas a cada passo: `kof_project.py check` JVM e JS, testes Kof JVM e JS e os 16 testes Python. Ao fim de cada etapa, rodar também as sete jornadas de navegador.
- **Nenhum teste existente é apagado sem que o caso dele continue coberto.** A contagem de casos só pode subir. Hoje são 114; dividir um teste com ramificação gera dois. Registrar a contagem em cada etapa.
- **Não alterar limites, regras ou o medidor para fazer achados sumirem.** Também não criar supressão, allowlist nem exceção nova. A única exceção existente continua: `long-function` e `too-many-statements` não valem para as suítes. Se uma regra parecer errada para algum caso, **parar e perguntar ao usuário**.
- **Produção:** uma refatoração por vez, sempre com os testes verdes. Usar os nomes do domínio (Kof idioms), sem extrair "metade de baixo" de uma função.

## Pontos de parada (perguntar ao usuário com dados, não decidir sozinho)

1. **Tempo das suítes.** O `kof_project.py test` prepara e compila cada suíte separadamente (`scripts/kof_project.py:148-155`). O `kof-mut.json` tem `commandTimeoutMs: 30000` e roda todas as suítes a cada mutante. Antes de dividir a suíte (R1), medir o tempo de `kof_project.py test --target jvm` com a suíte única e estimar o tempo com a divisão proposta. Se a divisão passar de cerca de 20 s ou mudar o veredito do KofMut, parar e apresentar as alternativas: menos arquivos; aumentar o timeout; ou o wrapper compilar todas as suítes num só `Main`, o que contraria o isolamento testado em `tests/test_kof_project.py:115-122`.
2. **Mutante equivalente.** Se um sobrevivente do `Meteor.kf` (`5:19 true->false`, `13:21 false->true`, `85:17 >= -> >`, `86:75 <= -> <`) não puder ser morto por nenhum teste de comportamento observável, mostrar a prova e perguntar. Não existe supressão.
3. **Regra que contradiz uma prática do Kof.** Exemplo: um laço que o training do Kof recomenda e que nem `testRows` nem uma função `given…` resolvem.
4. **Tamanho real da dívida de mutação.** Até hoje o KofMut só rodou sobre `Background.kf` e `Meteor.kf`. O `npm run check` do R7 roda a mutação sobre **toda a produção alterada**, e um sobrevivente reprova. Ao fim do R0, apresentar o número de sobreviventes de toda a produção, por arquivo, antes de começar o R1, porque esse número define o tamanho do R5.

## Decisões de 07/11/2026

1. Executar R1, R2 e R3 agora.
2. O suporte a `enum` no KofMut foi autorizado e será feito em outro plano, no repositório `kof-mut`.
3. A decisão sobre a UI (`GameControls`, `GameView`, `ControlsGuide`) continua pendente.
4. R4 e R5 esperam as frentes 2 e 3.
5. A1 depois do R3: a rodada completa do KofMut sai `incomplete` por causa do `enum`; comparar só os conjuntos de mortos e de sobreviventes pelo `id` do mutante.
6. **Exceção de regra aprovada pelo usuário:** no código de teste (`src/test/kof/` e `tests/*.kf`), `long-file` vale 1000 linhas não vazias, para ainda avisar arquivo gigante; o CPD não analisa código de teste (testes DAMP). A produção continua com 150 e CPD de 50 tokens. Os limites por função não mudam. Esta é a única exceção nova à regra "não alterar limites".
7. `kof.toml [sources]` só para os testes nesta etapa. O `kof test` compila um programa por arquivo (`kof/kof-cli/src/main/java/dev/kof/cli/CmdTest.java:192-208`), então antes do R1 o executor mede numa cópia (JVM, JS e KofMut no `Meteor.kf`) e para no ponto de parada 1. Build, check de tipos e jornadas continuam no `kof_project.py`.

Plano detalhado desta continuação: `~/.local/share/ccam/profiles/principal/plans/continue-o-plano-home-renanfranca-agents-iridescent-jellyfish.md`.

## Decisões de 09/11

Do usuário, em 09/11/2026, respondendo ao ponto de parada 1 (registro completo em
`.agent/tmp/debt-stop-point-1-handoff.md`):

1. Dividir o `GameJourney.kf` em 9 arquivos por assunto, como no probe, com
   `kof.toml [sources]` e um import por módulo (`import sifuture.game.*` dá `PKG007`).
2. Os testes Kof passam a rodar por `scripts/kof-tests.mjs`: descobre os `.kf` de
   `src/test/kof` sem lista à mão, gera uma entrada temporária que importa todos,
   roda `kof test <entrada> --module-root src/test/kof --target <jvm|js>` uma vez e
   apaga a entrada no fim.
3. É uma ponte temporária até o Kof ter o modo nativo (rascunho de issue em
   `.agent/tmp/kof-test-grouped-suite-issue.md`); documentar isso.
4. Aposentar o `kof_project.py test`; os testes Python desse comportamento viram
   testes Node equivalentes. O Python fica só com `check` e `build`.
5. Continua em `.mjs`, sem TypeScript (migração planejada à parte em
   `.agent/tmp/typescript-migration-plan.md`).

Critérios E1 a E10 do handoff entram no aceite. Chamadores do script: `check.mjs`,
`testCommand` do `kof-mut.json`, CI (`.github/workflows/kof-ci-and-pages.yml:78`) e
a documentação que cita `kof_project.py test`.

## Etapas

- **S. Sensores (decisão 6), antes do R1, por TDD:** `long-file` com 1000 para código de teste e 150 para o resto; CPD só sobre o que não é teste; `SENSORS.md` atualizado. Testes dos dois lados de cada fronteira.
- **P. Probe do ponto de parada 1 (decisão 7):** numa cópia fora de pastas com ponto, declarar `[sources]`, dividir a suíte por assunto com um módulo auxiliar para os `prepare…` compartilhados, medir e parar.

- **R0. Linha de base.** Registrar:
  - o SHA;
  - o `sensors:debt` completo, por regra, área e arquivo;
  - a contagem de casos: soma das linhas `failed of N tests` de cada suíte, 114 em JVM e em JS;
  - os tempos de teste;
  - a lista de arquivos do build (`kof_project.py build`);
  - o **KofMut sobre todos os `.kf` de `src/main/kof`** (relatório JSON salvo; referência parcial: `Background.kf` e `Meteor.kf` com 42 candidatos, 38 mortos e 4 sobreviventes);
  - as capturas das sete jornadas, rodadas **duas vezes**, para provar que são determinísticas.

  Depois, ponto de parada 4. Corrigir a linha desatualizada do `EXECPLAN.md` ("Pendente do usuário: commit desta correção e push", que já foi feito em `6b17e1c`).
- **R1. Dividir a suíte por comportamento** (por exemplo: nave, meteoros, armas, chefe, subchefe, fases, itens, controles), depois do ponto de parada 1. É só uma movimentação, sem mudar o conteúdo dos testes. Ajustar os testes Python que fixam `GameJourney.kf` (`tests/test_kof_project.py:44-61`), mantendo o que eles verificam, e o `kof-mut.json` se `testRoots` exigir. Contagem de casos igual.
- **R2. Regras de teste**, uma suíte por vez:
  - laços que preparam o cenário (`for … { g.step() }` e semelhantes) viram funções `given…`/`advance…` com nome, abaixo dos testes;
  - laços que percorrem casos viram `testRows`;
  - testes com ramificação viram um teste por caminho;
  - preparação longa vira funções `given…`;
  - `high-complexity` e `deep-nesting` dos testes caem junto.
- **R3. Preparação compartilhada nas suítes** (ajustado pela decisão 6): não há meta de zerar CPD nos testes. Extrair preparação compartilhada só quando ela melhora a leitura de mais de um arquivo.
- **R4. Produção**, um arquivo por vez, começando pelos menores (`Item`, `SpecialBeam`, `Blaster`, `ControlsGuide`) e terminando por `Game`, `GameControls`, `GameView` e `Weapons`. Inclui o CPD `Boss.kf:114` e `Subchief.kf:91`, `Game.kf:208` e `Game.kf:269`, `BossShot.kf:25` e `SubchiefShot.kf:14`. Depois de cada arquivo:
  - rodar `npm run lint:sensor -- <arquivo>`;
  - rodar o KofMut só nesse arquivo. Um sobrevivente novo exige teste novo (TDD) antes de seguir.
- **R5. Sobreviventes**, por TDD: um teste de comportamento por mutante, com o RED esperado anotado antes (ponto de parada 2). **Executar o R5 de cada arquivo antes de refatorá-lo no R4.** Primeiro a rede de testes, depois a refatoração; assim os mutantes ainda estão nas posições da linha de base.
- **R6. Fixtures `tests/*.kf`** (`boss`, `stage`, `subchief`, `weapons`, `meteor-motion`), com as funções `prepare…` divididas por intenção. A jornada correspondente precisa passar depois de cada uma.
- **R7. Fechamento:** `npm run sensors:debt` sem nenhum achado em todas as linhas; `npm run check` e `npm run check:task` em PASS. O `check` vai rodar o KofMut sobre toda a produção alterada, então registrar candidatos, mortos e duração. Repetir com o Kof 0.6.4: testes JVM e JS e `scripts/kof-sensors/test`.

## Registros

- `.agent/validation/sensor-debt-payoff.md` (novo), com uma tabela por etapa:
  - comandos, contagens antes e depois, contagem de casos, tempos e KofMut;
  - RED esperado e observado de cada teste novo;
  - uma lista "de → para" dos testes divididos (nome antigo → nomes novos).
- `EXECPLAN.md`, a cópia do plano e o plano externo dos sensores: progresso. **Na primeira atualização**, gravar no plano externo e na memória `m2-decisions` (`/home/renanfranca/.claude/projects/-home-renanfranca-projects-kof-sifuture/memory/m2-decisions.md`) a decisão de 05/11: a dívida inteira (suítes, produção, CPD, fixtures e sobreviventes) é paga antes do M3, e a regra do arquivo inteiro fica mantida.
- Evidência bruta em `.agent/tmp/debt-*/`. Probes ficam fora de pastas que começam com ponto (KofLang/Kof4j#999).

## Critérios de aceitação

Cada critério diz a fonte, um exemplo (contexto → ação → resultado observável), a verificação planejada, a evidência esperada e por que a prova distingue o resultado certo de um errado plausível. **Isto é o planejado, não o observado**: o executor registra o observado no aceite.

**A1. Os testes não ficaram mais fracos (R1–R3).**
- **Fonte:** a regra "o jogo não muda" e "nenhum caso perde cobertura".
- **Exemplo:** com a produção idêntica à linha de base, rodar o KofMut sobre todo `src/main/kof` depois do R3 → todo mutante morto no R0 continua morto, e os sobreviventes são um subconjunto dos do R0.
- **Verificação:** comparar os dois relatórios JSON pelo `id` do mutante (`arquivo:offset:substituto`). Ajuste de 07/11: a rodada sai `incomplete` (exit 3) por causa do `enum`; isso não reprova. Comparar só os conjuntos: os mortos do R3 contêm os 678 do R0, os sobreviventes do R3 são subconjunto dos 489, e os 1167 `id`s existem nos dois. Isso só vale se a produção não mudou: conferir com `git diff <R0> -- src/main` vazio.
- **Por que distingue:** um teste dividido ou convertido para `testRows` que perdeu uma asserção continua verde e mantém a contagem de casos. Só a mutação mostra que o mutante voltou a sobreviver. "Suíte verde" e "contagem maior ou igual a 114" sozinhas **não** provam este critério.

**A2. Nenhum caso de teste sumiu.**
- **Exemplo:** depois do R1, a soma de `failed of N tests` de todas as suítes é 114 em JVM e em JS. Depois do R2, é 114 ou mais, e cada teste dividido aparece na lista "de → para".
- **Verificação:** somar as linhas por suíte da saída de `kof_project.py test`, que imprime `Suite: …` e roda cada uma em separado (`scripts/kof_project.py:152-155`).
- **Por que distingue:** uma suíte nova que o wrapper não encontra, por pacote ou pasta errados, reduz a soma, mesmo com tudo verde.

**A3. A dívida zerou de verdade.**
- **Fonte:** decisão de 05/11.
- **Exemplo:** `npm run sensors:debt` imprime `SENSORS DEBT (report only, N Kof files)`, em que N é o total de `git ls-files '*.kf'`, mais `SENSOR lint: PASS (0 findings)` e `SENSOR dup: PASS (0 findings)`. Ajuste de 07/11: o CPD espera e tokeniza só os arquivos que não são de teste.
- **Verificação:** **ler a saída.** O `sensors:debt` sai com exit 0 mesmo com achados (`scripts/sensors-debt.mjs`), então o exit code não prova nada.
- **Por que distingue:** se o analisador falhar, a saída é `UNAVAILABLE`, nunca PASS. Se faltar algum arquivo, N não bate com o total do `git ls-files`.

**A4. Produção sem sobreviventes (R4, R5 e R7).**
- **Exemplo:** depois de cada arquivo refatorado, o KofMut só nesse arquivo sai com exit 0 e `survived=0`. No R7, o passo de mutação do `npm run check` mostra PASS, e não SKIP.
- **Verificação:** cada teste novo precisa ter **RED observado com o mutante aplicado**: no relatório do KofMut, aquele mutante deixa de sobreviver e passa a morrer. Registrar o identificador do mutante.
- **Observação somente leitura do planejamento:**
  - `Meteor.kf:5` (`Bool active = true`) e `:13` (`Bool collided = false`) são sobrescritos por `clearAnimation()` (`Meteor.kf:42-48`), que `Game.start` chama via `m.reset()` (`Game.kf:121`). Por isso nenhum teste que passe por `Game` consegue matar esses mutantes.
  - Eles podem ser mortos pelo comportamento público de um `Meteor()` recém-construído. Por exemplo: um meteoro novo, ao chamar `advance()`, anda para a esquerda em `Rules.METEOR_SPEED`. Com o mutante `active = false`, ele fica parado.
  - Outra saída é eliminar o valor inicial redundante numa refatoração de construção. Nesse caso, mostrar que o mutante deixou de existir, e não que foi suprimido.
  - `:85` e `:86` são limites de `touchesShip` (`x >= shipX`, `y + METEOR_HEIGHT <= shipY + SHIP_HEIGHT`), e o teste de borda os mata: `x == shipX` toca a nave e `x == shipX - 1` não toca.

**A5. A aparência e o estado das jornadas não mudaram (R4 e R6).**
- **Exemplo:** as sete jornadas passam, e as capturas em `.agent/tmp/{boss-browser,stage-browser,subchief-browser,background-items-weapons}/` e das demais jornadas têm **os mesmos pixels** que no R0.
- **Verificação:** comparar os pixels decodificados, e não os bytes do PNG. Essa comparação só vale se o R0 provou que duas execuções iguais dão os mesmos pixels. Se não der, registrar a lacuna e cair só nas asserções das jornadas.
- **Por que distingue:** as jornadas verificam alguns campos de estado, como `x == 121` e `hp`, mas não tudo. Uma fixture `prepare…` refatorada que deixa de definir um campo, como `game.ship.y = 200` em `tests/boss.kf`, pode continuar verde e mudar a imagem. Uma refatoração do `GameView` também.

**A6. A compatibilidade e os sensores continuam valendo.**
- Testes Kof JVM e JS também com o 0.6.4, porque `testRows` foi provado nas duas versões no M2.
- `scripts/kof-sensors/test` com 40/0 nas duas versões, e `node --test test/sensors/*.test.mjs` com 21/21, porque os sensores não mudam.
- 16 testes Python OK, com os testes de `tests/test_kof_project.py` ajustados verificando o mesmo de antes: seleção de suíte, falha propagada e isolamento entre suítes.
- `git diff <R0> -- scripts/kof-sensors scripts/*.mjs package.json SENSORS.md kof-mut.json` contém **somente** as mudanças das decisões 6 e 7 de 07/11, listadas no aceite com a fonte "usuário, 07/11". `git diff --check` com exit 0.

**A7. `check` e `check:task` aprovam a branch inteira.** `npm run check` com `CHECK: PASS`, com os passos lint, dup e mutação em **PASS** (e não SKIP), já que a branch altera `.kf`. `npm run check:task` com `CHECK:TASK: PASS`.

### Obrigações do executor antes de entregar
- Reconferir se cada expectativa está correta contra a fonte citada, **separado** de conferir se o teste a demonstra.
- Para cada critério de A1 a A7, registrar no aceite: comando ou procedimento, resultado observado e onde está a asserção ou o artefato.
- Registrar lacunas, verificações que falharam e critérios não verificados antes de entregar. Um critério com lacuna aberta **não** é apresentado como satisfeito.

## Progresso

- [x] R0. Linha de base, em `f4af07a`: dívida 415 lint + 23 CPD em 31
  arquivos; 114 casos em JVM e JS; build com 113 arquivos; sete jornadas
  determinísticas (186 PNG, 0 diferença de pixels entre duas execuções).
  KofMut nos 20 `.kf` de produção: 1167 candidatos, 678 mortos, 489
  sobreviventes, exit 3 `incomplete` por `EnumDeclarationNode` em `Boss`,
  `Item`, `MenuEntrance`, `State` e `Subchief`; 2h48. `GameControls`,
  `GameView` e `ControlsGuide` com 0 mortos (199 sobreviventes; `kof.ui` é
  no-op no JVM). Linha "Pendente do usuário" corrigida.
- [x] Ponto de parada 4: respondido em 07/11 (ver "Decisões de 07/11").
- [x] S. Sensores com a exceção aprovada: 42/0 e 21/21 no 0.7.0 e no 0.6.4; `sensors:debt` 412 lint + 3 CPD (só produção).
- [x] P. Probe: 9 arquivos com `[sources]` dão 114/114, mas um programa por arquivo custa 2,6 a 2,8 vezes e o KofMut no `Meteor.kf` teve 11 timeouts; entrada única custa o mesmo que hoje. Exige import por módulo (`PKG007`). Detalhes em `.agent/validation/sensor-debt-payoff.md`.
- [x] Ponto de parada 1: respondido em 09/11.
- [x] E. `scripts/kof-tests.mjs`: E1 a E10 verificados; entrada em `src/test/kof/KofTestsEntry*.kf` (decisão de 09/11, 0.6.4 sem `--module-root`); KofMut no `Meteor.kf` igual ao R0; Python 16 → 13, Node 21 → 27.
- [x] CI real no PR em rascunho #23 ([run 42675189498](https://github.com/renanfranca/kof-sifuture/actions/runs/42675189498)): JVM e JS verdes com Node.js 24.22.2, 114 casos cada.
- [x] R1. 9 arquivos por assunto + `JourneyScenarios.kf`; 118 blocos idênticos; 114 casos em JVM e JS no 0.7.0 e no 0.6.4.
- [x] R2. Uma suíte por vez, verde a cada passo: 0 achado de regra de teste em `src/test/kof`; casos 114 → 172 (JVM e JS, 0.7.0 e 0.6.4); lista "de → para" no aceite. Desvio: o `testRows` não compila num módulo importado pela entrada única (`SEM015`, 0.7.0 e 0.6.4); laços de casos viraram um teste por caso ou casos escritos um a um.
- [x] R3. Preparação usada por mais de um arquivo foi para `JourneyScenarios.kf`; `sensors:debt` sem achado em `src/test/kof`.
- [x] A1. KofMut completo depois do R3: mesmos 1167 `id`s, 678 mortos e 489 sobreviventes do R0; produção sem diff; `complete`/exit 1 com 0 limitações porque o `kof-mut` já tem o suporte a `enum` (PR #3). R4 e R5 esperam só a decisão da UI.
- [x] R5 e R4, lote 1 (11/11, branch `refactor/sensor-debt-batch-1`, sem commit):
  `BossWeapons`, `Credits`, `Meteor`, `SubchiefShot`, `Item`, `BossSpecial`,
  `BossShot`. 56 sobreviventes → 0; a primeira passada deixou 5 equivalentes
  (`Credits` 2, `Meteor` 2, `BossShot` 1); 31 testes novos em `EnemyFireJourney`,
  `ShipContactJourney` e `StageDriftJourney`, RED observado com cada mutante
  aplicado; 181 → 212 casos (JVM e JS, 0.7.0 e 0.6.4). R4: lint 0 nos sete
  arquivos; CPD `BossShot` ↔ `SubchiefShot` resolvido com `ShipContact.kf`
  (`edgeTouchesShip`), que também serve `BossSpecial` e `Item` e eliminou 4
  equivalentes. Estimativa do resto no aceite.
- [x] Lote 1, segunda passada (11/11, mesma branch, sem commit): os 5
  equivalentes deixaram de existir por refatoração, sem supressão e sem teste
  mudado. `Credits`: saiu a cláusula `|| secondY > -CREDITS_BLOCK_HEIGHT`
  (`firstY + secondY` vale sempre 176) e o teto virou `math.min` (com local `Int`
  tipada: `math.min` com `Rules.X` direto dá `SEM025` no 0.7.0 e no 0.6.4).
  `Meteor`: `touchesShip(Int, Int)` com a mesma assinatura delega ao
  `ShipContact` (`withinShipWidth`, `edgesWithinShipHeight`, com `Int`;
  `edgeTouchesShip(..., Ship)` mantido para não passar de 4 parâmetros).
  `BossShot`: saiu `&& animationSteps < 5`. KofMut nos 4 arquivos: 64/64 mortos.
  `check` e `check:task` PASS, com `mutation` 141/141; jornadas 7/7 com os mesmos
  pixels do R0; 212 casos em JVM e JS, no 0.7.0 e no 0.6.4.
- [x] R4 e R5 do resto: lotes 2 a 4 (`Ship` ao `Game`, PRs #29 a #31) e o lote da
  UI (16/11, branch `refactor/sensor-debt-ui`): `GameControls` e `GameView`
  viraram casca; a cena e as decisões dos controles foram para classes Kof puras.
  M0 193 sobreviventes → A1 166/166 mortos em 14 arquivos, 0 candidatos nas
  cascas; 323 → 409 casos; jornadas com os mesmos pixels do R0. Falta só o R6
  (fixtures) e o R7 (fechamento). Aceite em `.agent/validation/sensor-debt-payoff.md`.
- [x] Piloto da UI (10/11, branch `refactor/ui-pilot-controls-guide`): `ControlsGuide` delega a `GuideDisclosure` e ganha `clicked()`, `pointerDown()`, `blurred()`; KofMut 6/6 mortos, 0 mutantes na parte de tela; 172 → 181 casos (JVM e JS, 0.7.0 e 0.6.4); `check` e `check:task` PASS. Estimativa: `GameControls` cerca de 90% matável; `GameView` entre um terço e metade (o resto é coordenada de desenho). Aceite em `.agent/validation/sensor-debt-payoff.md`.
