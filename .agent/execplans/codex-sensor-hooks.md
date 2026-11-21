# M3 dos sensores: hooks reais no Codex CLI

## Purpose and success

Hoje os sensores do SiFuture (lint, duplicação, segredos, tipos, testes Kof)
só rodam quando alguém chama `npm run check`. Este trabalho é o M3 do plano dos
sensores (`.agent/sensor-plans/2026-10-15_FEATURE_sifuture-quality-sensors-exec-plan.md`,
seção "M3 — Hooks reais no Codex CLI"): ligar esses sensores a hooks do Codex
CLI, para que uma sessão Codex receba feedback automático enquanto trabalha.

Depois dele, numa sessão Codex no SiFuture:

- **SessionStart** registra o estado do worktree antes da sessão;
- **PostToolUse**, depois de cada comando de shell ou patch, roda os sensores
  baratos só nos arquivos que mudaram e devolve os achados ao agente, com local
  e guia;
- **Stop**, no fim do turno, roda baratos → tipos → testes, nessa ordem, sobre
  os arquivos da sessão, e devolve o turno ao agente quando algo falha, com no
  máximo três devoluções por sessão.

Isso precisa funcionar nos três jeitos que o usuário abre o Codex: `codex` no
terminal, o app desktop e `codex exec` chamado de dentro de uma sessão Claude
Code (como faz o script `luna`).

Fora do escopo, por decisão do plano dos sensores: mutação no Stop e revisão de
design (M4); hooks do Claude Code (decisão do usuário em 20/11: primeiro Codex;
o Claude Code fica para depois dos testes dele).

## Definitions

- **Hook**: comando que o Codex executa num evento da sessão, declarado em
  `.codex/hooks.json`. Recebe um JSON (payload) no stdin e pode responder no
  stdout.
- **Ledger**: arquivo por sessão com os caminhos que a sessão mudou. O Stop usa
  o ledger para saber o escopo.
- **Devolução (push back)**: resposta do Stop `{"decision":"block","reason":…}`,
  que faz o Codex continuar o turno com a razão como instrução.
- **Teste de fumaça**: hooks mínimos que só registram que dispararam, usados
  para provar o mecanismo antes de pôr sensores neles.

## Context and limits

Estado medido no planejamento, em 20/11/2026, `main` `bd2453a`:

- Codex CLI `codex-cli 0.170.0` em `~/.local/bin/codex`; `codex features list`
  mostra `hooks  stable  true`. Modelo padrão do `~/.codex/config.toml`:
  `gpt-6.2-sol`, `high`. Luna é `gpt-6-luna` (script `~/.local/bin/luna`, que
  roda `codex exec -m "$LUNA_MODEL" -C <dir> …`).
- `~/.codex/config.toml` só marca `/tmp` como `trusted`; o `kof-sifuture` não
  aparece. **Não se sabe** se o Codex 0.170 carrega `.codex/hooks.json` de um
  projeto sem `trust_level`, nem se pede aprovação na primeira execução de um
  hook. O `INSTALL.md` do Katacombs afirma que pede ("Codex asks for a one-time
  approval the first time a hook fires. Until you approve it, nothing runs and
  nothing says so"), mas isso é afirmação de terceiro, para outra versão. Tratar
  como hipótese do M0.
- Ambiente dos processos (lido em `/proc/<pid>/environ` em 20/11): o app desktop
  do Codex (`/usr/lib/chatgpt`) tem `PATH` só com `~/.local/bin` e pastas do
  sistema. Para isso funcionar, o usuário autorizou e foram criados em 20/11,
  fora do repositório:
  `~/.local/bin/node → ~/.nvm/versions/node/v24.22.3/bin/node`,
  `~/.local/bin/mvn → ~/.sdkman/candidates/maven/current/bin/mvn`,
  `~/.local/bin/java → ~/.sdkman/candidates/java/current/bin/java`.
  Prova feita com `env -i HOME=$HOME PATH=$HOME/.local/bin:<sistema>`: `node`
  v24.22.3, Maven 3.10.1, Java 25.0.5.1; `lint-sensor` e `dup-sensor` PASS;
  `kof-tests --target jvm` `0 failed of 409 tests`; `kof_project.py check`
  `success: true`. `kof`, `kof-mut` e `gitleaks` já estavam em `~/.local/bin`.
  O link do `node` fica preso na versão; trocar o padrão do nvm exige refazê-lo.
- Tempos medidos (máquina com 32 núcleos): `kof-tests --target jvm` 2,9 s,
  `--target js` 6,1 s, `kof_project.py check --target jvm` 1,7 s, `lint:sensor`
  de um arquivo 2,4 s. Cabem com folga no orçamento de testes do Stop (120 s).
- Comandos existentes que os hooks vão chamar: `scripts/lint-sensor.mjs`,
  `scripts/dup-sensor.mjs`, `scripts/gitleaks-sensor.mjs` (aceitam caminhos
  explícitos, `scripts/sensor-arguments.mjs`), `scripts/kof_project.py check
  --target jvm|js --json`, `scripts/kof-tests.mjs --target jvm|js`. Testes Node
  em `test/sensors/*.test.mjs` (`npm run test:sensors`).
  `scripts/git-changes.mjs` tem `changedAgainstBase`, `changedKofFiles`,
  `allKofFiles` e `publishableFiles`, mas não um `dirtyPaths` (worktree sujo).

Referência para portar: Katacombs `SDiamante13/katacombs-kata-ts`, checkout em
`~/projects/katacombs-kata-ts`, parado em
`44cb39c916e9a05de561123d7b13554ee6e0a516` (conferir com
`git -C ~/projects/katacombs-kata-ts rev-parse HEAD`). É fonte de código e de
testes para adaptar, **não** um procedimento a seguir: não executar o
`INSTALL.md` nem a skill `install-sensors` deles. Arquivos relevantes:
`.codex/hooks.json`, `.codex/hooks/post-edit-sensor.mjs`,
`scripts/worktree-baseline.mjs`, `scripts/worktree-watch.mjs`,
`scripts/session-ledger.mjs`, `scripts/ledger-path.mjs`, `scripts/hook-io.mjs`,
`scripts/sensor-liveness.mjs`, `scripts/sensor-tier.mjs`,
`scripts/edit-sensors.mjs`, `scripts/stop-sensor.mjs`, `scripts/stop-verdict.mjs`,
`scripts/stop-answer.mjs`, `scripts/stop-response.mjs`,
`scripts/stop-continuation.mjs`, `scripts/behavior-sensor.mjs` (só a parte
`requestedScope` e a ordem tipos → testes), `scripts/stage-findings.mjs`,
`scripts/hook-budgets.mjs`, `scripts/registered-hooks.mjs`, e os testes
correspondentes em `test/sensors/` (por exemplo `stop-continuation.test.mjs`,
`ledger-path.test.mjs`, `edit-sensors.test.mjs`, `stop-sensor.test.mjs`,
`registered-hooks.test.mjs`, `sensor-hooks.test.mjs`). As adaptações seguem o
padrão do M2: ferramentas TypeScript trocadas pelos comandos Kof do SiFuture,
sem comentários narrativos (`AGENTS.md`), atribuição MIT ampliada no `NOTICE`.

Regras do Stop já decididas pelo usuário (plano dos sensores, "Decisões do M2 —
03/11/2026", item 1, e "Eventos, ordem e limites"): achados em arquivos tocados
pela sessão bloqueiam; escopo = ledger da sessão ∩ arquivos ainda sujos, com
fallback para o worktree sujo se o ledger estiver vazio; deduplicação por
conjunto de achados; no máximo três devoluções por sessão, depois só reporta;
`stop_hook_active` respeitado quando vier; testes caros não começam se os
baratos ou os tipos falharem. Orçamento de testes 120 s; timeout do Stop 300 s.

### Limites

- Não mudar `src/`, os testes Kof, `tests/*.kf`, `tests/browser*.py`,
  `kof-mut.json` nem as regras e limites dos sensores.
- Não mudar `~/.codex/config.toml` nem aprovar nada em nome do usuário. Se o
  Codex exigir `trust_level`, aprovação ou clique, parar e pedir.
- Não executar mutação no Stop (M4).
- Probes ficam fora de pastas que começam com ponto (KofLang/Kof4j#999), são
  removidos ao fim de cada prova e nunca entram no commit.
- Toda sessão Codex de prova é Luna `high`:
  `codex exec -m gpt-6-luna -c model_reasoning_effort="high" -C <repo> "<prompt>"`.

## Decisions

**Ledger e marcas em `.sensors/`, ignorado pelo Git.** O Katacombs grava em
`reports/ledger/`. Aqui fica em `.sensors/ledger/`, com `.sensors/` acrescentado
ao `.gitignore`. Precisa estar ignorado, porque o `worktree-watch` compara o
worktree sujo: arquivos de ledger dentro de uma pasta não ignorada apareceriam
como mudança da própria sessão. Alternativa descartada: `.agent/tmp/`, que só
está no `.git/info/exclude` desta máquina.

**Sensores baratos do PostToolUse e do cheap tier do Stop.** `lint-sensor`,
`dup-sensor` e `gitleaks-sensor` com os caminhos mudados que forem `.kf` (lint e
dup) ou publicáveis (gitleaks). Sem formatação automática: o plano dos sensores
só permite `kof fmt` automático depois de provar idempotência, o que não foi
feito. Tipos e testes do Stop: `kof_project.py check --target jvm` e `js`, depois
`kof-tests.mjs --target jvm` e `js`. Mudança só em arquivos que não são Kof (por
exemplo um `.md`) roda só gitleaks no PostToolUse e não roda tipos nem testes no
Stop.

**Teste de fumaça antes de qualquer sensor (usuário, 20/11).** O M0 prova os três
eventos com hooks que só registram o payload. Mesmo que o Codex não peça
aprovação, o executor só segue depois de ver os três eventos disparando.

## Risks

- **Hooks silenciosos.** O Codex pode não carregar os hooks (projeto sem
  `trust_level`) ou esperar aprovação sem avisar. Controle: o M0 registra cada
  disparo num arquivo; ausência de registro é falha, nunca "edição limpa".
- **`codex exec` diferente da sessão interativa.** O modo não interativo pode
  não disparar algum evento ou não mostrar a aprovação. Controle: as provas são
  feitas nos três contextos e registradas separadamente.
- **`lc` e `lp` passam a disparar hooks.** Eles rodam `codex exec` no
  repositório. Com worktree limpo depois do commit, o Stop sai em SKIP; durante o
  commit, um Stop vermelho pode devolver o turno ao Luna. Controle: a P8 prova o
  caminho do `luna` com worktree limpo; o relatório final descreve o que os hooks
  fizeram durante o `lc` da entrega; documentar `SENSORS=git`
  (desliga o tier do agente, como no Katacombs `scripts/sensor-tier.mjs`) como
  saída.
- **Payload diferente do Katacombs.** Nomes de ferramenta e campos podem ter
  mudado no Codex 0.170. Controle: o matcher e a leitura do payload saem do que
  o M0 registrou, não do manifesto deles.

## Milestones

### M0. Teste de fumaça dos hooks

Objetivo: provar, antes de escrever sensor, que o Codex 0.170 dispara
SessionStart, PostToolUse e Stop neste projeto, **e que a resposta do hook chega
ao agente**. Disparar sem entregar a resposta não serve: o PostToolUse e o Stop
dependem de o agente ler o que o hook devolve.

1. Criar `.codex/hooks.json` provisório com os três eventos chamando
   `scripts/hook-canary.mjs`, que acrescenta uma linha JSON a
   `.sensors/canary.jsonl` com: evento, hora, `session_id`, `tool_name`, os
   nomes das chaves do payload, o comando do `tool_input` cortado em 200
   caracteres, `cwd`, `PATH`, `process.execPath` e `process.version`. Matcher do
   PostToolUse provisório: `.*`. Acrescentar `.sensors/` ao `.gitignore`.
   Respostas do canário, para testar a entrega:
   - PostToolUse, só na primeira chamada de cada sessão: `{"decision":"block","reason":"CANARY-POST-<session_id>"}`;
   - Stop, só na primeira chamada de cada sessão: `decision: block`, com uma
     instrução para manter `CANARY-POST-<session_id>` e incluir a linha
     `CANARY-STOP-OK` na resposta final;
   - nas demais chamadas, nada no stdout.
2. Antes de cada contexto, apagar `.sensors/canary.jsonl` e anotar a hora de
   início. Rodar uma sessão Luna:
   `codex exec -m gpt-6-luna -c model_reasoning_effort="high" -C . "Crie o arquivo probe-canary.txt com o texto ok usando o shell, depois apague-o. Se algum hook enviar uma mensagem começando com CANARY, copie-a literalmente na sua resposta final."`
3. Ler `.sensors/canary.jsonl` e a saída do `codex exec`. O contexto passa só
   se tudo isto valer:
   - há linhas de SessionStart, PostToolUse e Stop, todas com hora depois do
     início anotado e com o **mesmo `session_id`**, diferente do de qualquer
     contexto anterior (assim um arquivo velho ou outra sessão não passam);
   - pelo menos um PostToolUse tem no comando registrado o `probe-canary.txt`
     (prova que o hook viu a edição pedida, e não só uma leitura);
   - a resposta final do agente contém `CANARY-POST-<session_id>` (o
     PostToolUse chegou ao agente) e `CANARY-STOP-OK`, e há **dois** Stop no log
     (o bloqueio do Stop fez o agente continuar e parar de novo). Registrar se o
     segundo Stop traz `stop_hook_active`.
   Anotar os nomes de ferramenta vistos no PostToolUse e os campos do payload.
   Se faltar qualquer item, ou aparecer aviso de aprovação ou de confiança:
   **ponto de parada 1**. Reportar ao usuário o que apareceu e pedir que ele
   aprove (terminal ou app) ou marque o projeto como confiável. Não editar
   `~/.codex/config.toml`.
4. **Ponto de parada 2**, mesmo que o passo 3 passe: pedir ao usuário que abra o
   Codex interativo no terminal e depois o app desktop no projeto, rode o mesmo
   prompt em cada um (o executor apaga o `canary.jsonl` antes de cada um) e
   avise. Aplicar a mesma checagem do passo 3 e registrar por contexto o `PATH`
   e o `process.execPath` que o hook recebeu.

Aceite do M0: os três contextos (`codex exec`, terminal, app) passam na checagem
do passo 3. No app, `process.execPath` resolve para `~/.local/bin/node` ou para
o alvo dele (`~/.nvm/versions/node/v24.22.3/bin/node`). Qualquer contexto que
não passe para a entrega e é reportado.

### M1. Núcleo dos hooks, por TDD

Portar, com testes `node --test` em `test/sensors/` (por comportamento público,
adaptados dos testes do Katacombs):

- `scripts/ledger-path.mjs` (raiz `.sensors/ledger`, nome seguro de sessão),
  `scripts/session-ledger.mjs`, `scripts/hook-io.mjs`,
  `scripts/sensor-liveness.mjs`, `scripts/sensor-tier.mjs`;
- `dirtyPaths(root)` em `scripts/git-changes.mjs` (modificados, novos e
  apagados no worktree, sem os ignorados) e `scripts/worktree-watch.mjs`;
- `scripts/edit-sensors.mjs`: recebe caminhos, filtra os do projeto e roda os
  sensores baratos da decisão acima; devolve `null` sem escopo, `passed` e um
  relatório com a linha `EDIT SENSORS: lint … · dup … · gitleaks …` e os achados;
- `scripts/stop-continuation.mjs` (deduplicação e três devoluções),
  `scripts/stop-response.mjs`, `scripts/stop-verdict.mjs` (baratos antes) e o
  verificador do Stop (`requestedScope`, depois tipos JVM e JS, depois testes JVM
  e JS com orçamento de 120 s), sem mutação e sem design.

Casos que os testes precisam cobrir. O valor esperado vem da regra citada, não
do código:

- função de 26 linhas → `long-function` com `arquivo:linha` e o guia
  `long-function`; a mesma função com 25 → nenhum achado. Fonte:
  `.agent/validation/sensor-calibration.md`, tabela de métricas (`functionLines`
  conta da declaração ao fim do corpo, com delimitadores, sem linhas vazias ou só
  de comentário; limite 25). O caso de 25 é o que distingue `>` de `>=`;
- sessão que editou `a.kf` e depois só lê: o ledger tem `a.kf` uma vez depois da
  edição e continua com uma entrada depois da leitura. O mesmo cenário mostra as
  duas coisas: um watcher que nunca registra falha na primeira asserção, e um que
  registra leituras falha na segunda;
- `b.kf` mudado por fora entre dois olhares → aparece no segundo
  `changedSinceLastLook`, e não no primeiro;
- ledger com `a.kf` e `b.kf`, só `a.kf` ainda sujo → escopo do Stop `[a.kf]`;
  ledger vazio com `c.kf` sujo → escopo `[c.kf]`. Fonte: plano dos sensores,
  "Dependência e contrato com KofMut" (ledger ∩ alterações ainda existentes,
  fallback para as alterações reais);
- ledger da sessão A não muda o escopo da sessão B (o ledger é por
  `session_id`);
- ordem dos tiers, com comandos falsos injetados que gravam a própria chamada:
  baratos falham → só os baratos foram chamados; baratos passam e tipos falham →
  baratos e tipos chamados, testes não; tudo passa → os quatro na ordem
  baratos, tipos JVM e JS, testes JVM e JS;
- devoluções, com a sequência do plano dos sensores (M4, cenário S2): achados A,
  A, B, C, D numa sessão → devolve em A, não devolve na repetição de A, devolve
  em B e em C, não devolve em D (limite de três), e o veredicto de D continua
  reprovado. Fonte: `scripts/stop-continuation.mjs` do Katacombs
  (`MOST_PUSHBACKS = 3`, impressão `regra@local`);
- `stop_hook_active: true` com achado novo → não devolve, e reporta;
- orçamento de testes: com orçamento injetado de 1 s e um comando falso que dorme
  2 s → reprovado com a mensagem de tempo; o mesmo comando com orçamento de 5 s →
  passa. O valor real continua 120 s (plano dos sensores, "Eventos, ordem e
  limites"); o teste não espera 120 s.

### M2. Manifesto, adaptador e doctor

- `.codex/hooks.json` definitivo: SessionStart → `scripts/worktree-baseline.mjs`
  (timeout 10), PostToolUse → `.codex/hooks/post-edit-sensor.mjs` (timeout 60;
  matcher com os nomes de ferramenta vistos no M0), Stop →
  `scripts/stop-sensor.mjs` (timeout 300). O comando resolve a raiz do
  repositório como no Katacombs (`$(git rev-parse --show-toplevel)`), salvo se o
  M0 mostrar que o `cwd` do hook já é a raiz. Remover o `hook-canary.mjs`.
- `sensors:doctor`: acrescentar as linhas dos hooks: manifesto presente, cada
  script citado existe, último disparo de cada evento (uma marca de
  `sensor-liveness` por evento, e não por runtime como no Katacombs), e o `node` que o hook usaria (`~/.local/bin/node` e versão).
  Teste em `test/sensors/sensors-doctor.test.mjs`.
- `NOTICE`: listar os arquivos novos adaptados do Katacombs e as adaptações.

### M3. Provas reais nos três contextos

Probes temporários, removidos ao fim de cada contexto: produção em
`src/main/kof/sifuture/probe/Probe.kf` e teste em
`src/test/kof/sifuture/probe/ProbeJourney.kf` (é de `src/test/kof` que o
`kof-tests.mjs` descobre os testes). Primeiro com `codex exec` Luna; depois, no
**ponto de parada 3**, com o usuário no terminal e no app. O executor escreve os
prompts de cada prova e lê o resultado. P1 a P3 e P5 a P7 acontecem na mesma
sessão, nessa ordem, para que cada prova parta do estado deixado pela anterior.

| # | Ação | Resultado esperado | Por que distingue |
| --- | --- | --- | --- |
| P1 | o agente cria `Probe.kf` com uma função de 30 linhas | o PostToolUse dessa edição devolve `long-function` em `Probe.kf:<linha>` com guia, e a resposta do agente cita o achado | o achado precisa aparecer na **primeira** chamada depois da edição, não só no Stop |
| P2 | o agente reduz a função para 20 linhas | o PostToolUse dessa edição não traz achado; o ledger tem `Probe.kf` | um hook que nunca acha nada passaria aqui, mas já falhou na P1 |
| P3 | o agente roda `ls` e `cat Probe.kf` | o ledger continua com as mesmas entradas | combinada com a P1, separa "não registra leitura" de "não registra nada" |
| P4 | só no terminal (ponto de parada 3): com a sessão aberta, o usuário muda `Probe.kf` em outro terminal e manda um novo prompt | o próximo olhar inclui `Probe.kf` no escopo | é a edição externa do plano dos sensores; `codex exec` não tem intervalo entre turnos para isso |
| P5 | o agente cria `ProbeJourney.kf` com `test` que falha por asserção, sem erro de tipo, e tenta terminar | o Stop devolve o turno citando o nome do teste; o log do Stop mostra baratos PASS e tipos PASS antes dos testes | o escopo do Stop inclui o teste porque a sessão o criou; se o ledger falhasse, o Stop sairia em SKIP e não citaria o teste |
| P6 | o agente corrige o teste e põe em `Probe.kf` um erro só de tipo (por exemplo `Int x = "texto"`), e tenta terminar | o Stop devolve com o erro de tipo; o log mostra baratos PASS e nenhuma execução de testes | o erro precisa passar no lint: o executor confere antes, com `node scripts/lint-sensor.mjs src/main/kof/sifuture/probe/Probe.kf`, que dá PASS. Senão o bloqueio viria dos baratos e não provaria a ordem |
| P7 | o agente corrige o tipo e termina | o Stop deixa terminar, com a mensagem dos tiers em PASS | um Stop que nunca bloqueia passaria, mas já falhou na P5 e na P6 |
| P8 | worktree limpo, sem probes: `luna "rode git status e termine"` chamado do Bash do executor | as marcas de último disparo (`sensor-liveness`) de SessionStart, PostToolUse e Stop ficam com hora depois da chamada, e existe um arquivo de ledger para o `session_id` novo; o Stop sai em SKIP, sem `decision` | prova o caminho do `luna` sob o `PATH` do Claude Code |

Registrar em cada prova: contexto, `session_id`, linhas do ledger antes e
depois, saída do hook e se foi callback real ou chamada direta do script.
Chamada direta com payload sintético nunca recebe o rótulo de callback real.

### M4. Documentação e registros

- `docs/desenvolvimento.pt_BR.md` e `docs/desenvolvimento.md`: seção nova sobre
  os hooks do Codex (o que cada evento faz, como aprovar ou confiar no projeto,
  conforme o M0 mostrar; `SENSORS=git` para desligar; o requisito de `node`,
  `mvn` e `java` em `~/.local/bin` para o app; o link do `node` preso na versão).
- `.agent/validation/sensors-adoption.md`: seção "M3 — hooks reais no Codex
  CLI" com versões, payloads do M0, as provas P1 a P8 por contexto e as
  pendências.
- `EXECPLAN.md`: entrada do M3 com links. Não editar `.agent/sensor-plans/`.

## Progress

- [x] M0. Teste de fumaça nos três contextos (pontos de parada 1 e 2).
  - 21/11/2026: branch `feat/codex-sensor-hooks`. Começou num worktree irmão
    `~/projects/kof-sifuture-codex-hooks`; por decisão do usuário, o trabalho
    voltou ao checkout principal `~/projects/kof-sifuture` e o worktree foi
    removido, porque a confiança do Codex foi gravada para o checkout principal.
    Criados `scripts/hook-canary.mjs`, `.codex/hooks.json` provisório e
    `.sensors/` no `.gitignore`.
  - 21/11/2026 10:33:41Z, contexto `codex exec` (Luna `high`, sessão
    `01a1fdab-438b-7062-9ffc-db0fea0bc22c`): **ponto de parada 1**. Nenhum hook
    disparou (`.sensors/canary.jsonl` não existe; a resposta diz que nenhum hook
    retornou `CANARY`). O Codex avisou:
    `Untrusted project-local configuration is disabled. Run codex exec --trust to allow project configuration and MCP servers for this and future chats in the project`.
    A configuração do projeto estava desabilitada por falta de confiança.
  - 21/11/2026 10:37Z, incidente: o usuário rodou
    `codex exec --trust -C <worktree> "termine"`, sugerido pelo executor. A
    confiança foi gravada como `[projects."/home/renanfranca/projects/kof-sifuture"]`
    (o checkout principal, não o caminho do worktree). O prompt ambíguo fez a
    sessão (`01a1fdae-bcde-7c83-89f9-d8df439eedce`, modelo padrão `gpt-6.2-sol`,
    não Luna) retomar este plano sozinha: rodou outra `codex exec` (sessão
    `01a1fdaf-2b41-7490-8b73-2fa75c5a617d`, sem aviso de confiança e ainda sem
    `canary.jsonl`), baixou fontes do Codex 0.170 para
    `.agent/tmp/codex-sensor-hooks/`, editou o canário, o registro de aceite e
    este Progress, e criou `~/projects/kof-sifuture/.codex/hooks.json`. Com
    autorização do usuário, o executor apagou esse arquivo do checkout principal
    e desfez as edições no canário e em `sensors-adoption.md`.
  - Afirmações daquela sessão, **não conferidas pelo executor**: o Codex 0.170
    resolve o manifesto de um worktree vinculado a partir do checkout principal;
    com o manifesto lá, `hooks/list` mostrou os três eventos com
    `trustStatus: untrusted`; cada definição de hook precisa de revisão em
    `/hooks` além da confiança no projeto. Precisam virar evidência própria antes
    de entrar no registro de aceite. Lição: prompts de `codex exec` para o
    usuário rodar nunca podem ser abertos como "termine".
  - 21/11/2026, conferido pelo executor no checkout principal, com
    `codex app-server --stdio` e o método `hooks/list` (`cwds:
    ["/home/renanfranca/projects/kof-sifuture"]`): `postToolUse`,
    `sessionStart` e `stop` aparecem com `trustStatus: untrusted`, origem
    `/home/renanfranca/projects/kof-sifuture/.codex/hooks.json`, sem warnings nem
    errors. A confiança no projeto não basta: cada hook precisa de aprovação.
    Pelo teste `hooks_list.rs` do Codex 0.170, a aprovação guarda um hash da
    declaração (`hooks.state."<key>".trusted_hash`) e uma definição alterada
    volta como `Modified`. Consequência para o M2: trocar o canário pelo
    manifesto definitivo exige nova aprovação do usuário.
  - 21/11/2026: o usuário aprovou os três hooks em `/hooks`; `hooks/list`
    passou a mostrar os três `trusted`. O Codex se atualizou sozinho para
    `codex-cli 0.171.0` (link `~/.local/bin/codex` refeito às 11:11Z); as provas
    daqui em diante são nessa versão.
  - **Contexto `codex exec` PASSA**, callback real. Início anotado
    `2026-11-21T11:20:24.520Z`, `canary.jsonl` apagado antes, sessão
    `01a1fdd6-0762-78a2-a275-dfc2d8449cc7` (nova). Linhas, todas com esse
    `session_id`: SessionStart 11:20:27.058Z; PostToolUse 11:20:32.126Z e
    11:20:37.612Z, ambos com `tool_name: "Bash"`, `tool_input` só com
    `command`, e o comando contém `probe-canary.txt`; Stop 11:20:40.864Z
    (`stop_hook_active: false`) e Stop 11:20:45.225Z (`stop_hook_active: true`).
    A resposta final contém `CANARY-POST-01a1fdd6-0762-78a2-a275-dfc2d8449cc7`
    e terminou em `CANARY-STOP-OK`. Sem aviso de aprovação ou confiança.
  - Achados do payload para o M1/M2: chaves vistas `cwd`, `hook_event_name`,
    `last_assistant_message`, `model`, `permission_mode`, `session_id`,
    `source`, `stop_hook_active`, `tool_input`, `tool_name`, `tool_response`,
    `tool_use_id`, `transcript_path`, `turn_id`. O `cwd` do payload e o
    `process.cwd()` do hook são a raiz do repositório. `process.execPath`
    `~/.nvm/versions/node/v24.22.3/bin/node`, `v24.22.3`; o `PATH` herdou o do
    Claude Code (sdkman, nvm, `~/.local/bin`). Nenhum `apply_patch` apareceu:
    o agente só usou o shell, então o nome da ferramenta de patch ainda não foi
    observado. Um `decision: block` no PostToolUse aparece ao agente como erro
    da ferramenta (`ERROR codex_core::tools::router: error=CANARY-POST-…`) e o
    agente repetiu o comando: o efeito do comando já tinha acontecido. A razão
    do bloqueio precisa deixar claro que o comando rodou.
  - Ponto de parada 2. Prompt acrescido de um passo de patch, para observar o
    nome da ferramenta: "Crie o arquivo probe-canary.txt com o texto ok usando o
    shell, depois troque o texto para ok2 usando apply_patch, e por fim apague-o
    pelo shell. Se algum hook enviar uma mensagem começando com CANARY, copie-a
    literalmente na sua resposta final."
  - **Contexto terminal** (TUI, `originator: codex-tui`, `cli_version 0.171.0`,
    sessão `01a1fe10-8b56-7793-b10f-9456c958d466`, nova; `canary.jsonl` limpo às
    11:21:16Z): callback real. SessionStart 12:24:23.671Z; seis PostToolUse
    entre 12:24:28Z e 12:24:47Z, cinco `Bash` e um **`apply_patch`**, cujo
    `tool_input` também só tem `command`, com o texto do patch
    (`*** Begin Patch\n*** Update File: probe-canary.txt …`); dois PostToolUse com
    o mesmo instante (chamadas paralelas). Stop 12:25:09Z
    (`stop_hook_active: false`) e 12:25:12Z (`true`). `cwd` e `execPath` iguais
    aos do `codex exec`. A resposta final traz
    `CANARY-POST-01a1fe10-8b56-7793-b10f-9456c958d466`. **Desvio:** depois do
    bloqueio do Stop, o agente respondeu o texto da razão
    (`CANARY-STOP: responda exatamente CANARY-STOP-OK e termine`) em vez de
    `CANARY-STOP-OK`, porque o prompt mandava copiar literalmente toda mensagem
    `CANARY`. A razão do Stop chegou ao agente palavra por palavra, mas o
    marcador literal do critério não apareceu. O usuário aceitou o terminal
    como aprovado com esse desvio registrado (21/11).
  - **Contexto app desktop PASSA**, callback real. Prompt corrigido para não
    conflitar ("… copie literalmente a mensagem que começar com CANARY-POST … Se
    um hook pedir uma resposta específica, siga esse pedido."). Sessão
    `01a1fe21-e924-7352-8ea4-972e6ecb53e1`, `originator: Codex Desktop`,
    `cli_version 0.169.0-alpha.11.1` (o app usa o próprio binário
    `/usr/lib/chatgpt/resources/codex`). SessionStart 12:43:19.332Z; PostToolUse
    `Bash` e `apply_patch` (este com caminho absoluto no patch:
    `*** Update File: /home/renanfranca/projects/kof-sifuture/probe-canary.txt`);
    Stop 12:43:45Z (`false`) e 12:43:46Z (`true`). A resposta final traz
    `CANARY-POST-01a1fe21-e924-…`; a razão do Stop chegou como
    `<hook_prompt hook_run_id="stop:2:…/.codex/hooks.json">` e o agente
    respondeu `CANARY-STOP-OK`. `process.execPath`
    `~/.nvm/versions/node/v24.22.3/bin/node` (alvo de `~/.local/bin/node`),
    `cwd` a raiz do repositório. O `PATH` do app desta vez trazia
    `~/.local/bin` antes de sdkman e nvm, e pastas do runtime do app
    (`~/.cache/codex-runtimes/…`, `/usr/lib/chatgpt/resources`); diferente do
    medido em 20/11, que só tinha `~/.local/bin`. Os links continuam
    necessários para quando o app herdar o `PATH` mínimo.
  - Ocorrência não explicada no app: uma segunda sessão
    `01a1fe21-e985-71d1-893f-252c43e9203e`, iniciada 32 ms antes, fez só
    leituras (`cat` do ExecPlan e do canário, `rg`) e chamou
    `mcp__codex_apps__notion__search` e `__fetch`; não chegou ao Stop e não tem
    transcrição em `~/.codex/sessions` nem entrada no `session_index.jsonl`.
    Consequência para o desenho: o matcher `.*` pega ferramentas MCP; o
    definitivo deve ser `Bash|apply_patch`, e o ledger por `session_id` mantém
    sessões paralelas separadas.
  - Aceite do M0: os três contextos passam (terminal com o desvio aceito).
- [x] M1. Núcleo dos hooks com testes.
  - 21/11/2026: `npm run test:sensors` 64 de 64 (22 novos, em
    `test/sensors/edit-hook.test.mjs` e `test/sensors/stop-hook.test.mjs`).
    Todos os casos listados no M1 estão cobertos: 26 linhas → `long-function`
    com local e guia, 25 → silêncio; ledger depois de edição e de leitura;
    mudança externa no segundo olhar; escopo ledger ∩ sujos, fallback e
    separação por sessão; ordem dos tiers com comandos falsos; A, A, B, C, D →
    devolve, não, devolve, devolve, não (payload sintético); `stop_hook_active`;
    orçamento de 1 s e 5 s com comando que dorme 2 s. Desvio de TDD: os seis
    testes do PostToolUse foram escritos juntos e o primeiro vermelho foi
    módulo ausente; os do Stop seguiram um ciclo por comportamento, com
    vermelho de asserção antes do verde. O teste de `session_id` inseguro passou
    de primeira, porque `ledger-path` foi portado inteiro.
  - Decisões de desenho tomadas no M1: os scripts aceitam `--root` como os
    sensores existentes (os testes usam projetos temporários); estado em
    `<root>/.sensors/ledger/`, que o watcher ignora mesmo sem `.gitignore`; os
    tiers do Stop param entre si, mas todos os passos de um tier rodam (um
    achado de lint não esconde um de gitleaks); a razão do PostToolUse começa
    dizendo que o comando já rodou, por causa do achado do M0; tipos chamam
    `kof_project.py check --target <alvo>` sem `--json`, para o agente ler
    `arquivo:linha:coluna: ERROR código: mensagem`; um tier que lança exceção
    vira `STOP SENSORS: UNAVAILABLE`, nunca PASS.
  - Risco aberto: os caminhos dos diagnósticos do `kof_project.py` podem vir da
    árvore temporária que ele monta, e não de `src/main/kof`. Conferir na P6.
- [x] M2. Manifesto, adaptador, doctor e `NOTICE`.
  - 21/11/2026: `.codex/hooks.json` definitivo (SessionStart 10 s, PostToolUse
    60 s com matcher `Bash|apply_patch`, Stop 300 s; raiz por
    `$(git rev-parse --show-toplevel)`, mantida porque o M0 mostrou `cwd` na
    raiz, mas a sessão pode mudar de pasta). `scripts/hook-canary.mjs`
    removido. `sensors:doctor` ganhou a seção `Codex hooks` (manifesto,
    script de cada evento, último disparo por evento, `~/.local/bin/node` e
    versão); "never fired" aparece como `UNAVAILABLE` sem derrubar o exit,
    porque é vivacidade e não configuração; script citado e ausente é
    `MISSING` e derruba. O teste antigo do doctor passou a montar um manifesto,
    porque manifesto ausente agora é `MISSING`. `NOTICE` lista os arquivos
    adaptados. `npm run test:sensors` 66 de 66.
  - `hooks/list` depois da troca: os três hooks `modified`, como previsto. A
    nova aprovação em `/hooks` é do usuário.
  - Chamada direta (payload sintético, **não** é callback real) de
    `scripts/stop-sensor.mjs` no repositório com o diff desta branch:
    `STOP SENSORS: lint SKIP · dup SKIP · gitleaks PASS · types:jvm SKIP · …`
    e resposta `{"continue":true,"systemMessage":…}` sem `decision`.
  - 21/11/2026, achado antes da P6: `kof_project.py check` monta `Main.kf` com
    `import sifuture.*`, que não alcança um subpacote novo. Prova: um
    `src/main/kof/sifuture/probe/Probe.kf` com `Int x = "texto"` deu
    `checked 1 entry file(s)` e exit 0. Correção no Stop: o tier de tipos passa
    `--fixture .sensors/ledger/types-entry.kf`, uma entrada com `import
    sifuture.*` mais `import <módulo>` de cada arquivo de produção alterado; com
    ela o mesmo probe deu `Probe.kf:4:5: ERROR SEM021` e exit 1 em JVM e JS. O
    diagnóstico traz só o nome do arquivo, então o Stop troca `Probe.kf` pelo
    caminho do escopo quando há um único dono. `npm run test:sensors` 68 de
    68. O `kof_project.py` e o `check` não mudaram: o `npm run check` continua
    sem ver um módulo de produção que nada importa (pendência registrada, fora
    do escopo deste plano).
- [x] M3. Provas P1 a P8 (ponto de parada 3).
  - Contexto `codex exec` (Luna `high`, `codex-cli 0.171.0`), callback real,
    sessão `01a1fe4e-6ce4-7410-8515-396b763c9d07`; P1 a P3 e P5 a P7 na mesma
    sessão com `codex exec resume`. Evidência local em
    `.agent/tmp/codex-sensor-hooks/m3/` (logs e o `.stop.log` da sessão).
    Primeira tentativa travou em `Reading additional input from stdin...`;
    os comandos passaram a usar `< /dev/null`.
  - **P1 PASSA.** A função criada tinha 29 linhas (o heredoc juntou `}` à
    última linha de operando), acima de 25. O PostToolUse dessa escrita
    bloqueou com `src/main/kof/sifuture/probe/Probe.kf:3:1 ERROR long-function`,
    `` `probeTotal` has 29 lines; the limit is 25. `` e o guia; a resposta do
    agente citou a linha.
  - **P2 PASSA.** A reescrita com 20 linhas não trouxe resposta do hook; o
    ledger tem `src/main/kof/sifuture/probe/Probe.kf`.
  - **P3 PASSA.** `ls` e `cat`: ledger igual antes e depois (`diff` vazio).
    O Stop desse turno: os sete passos PASS.
  - Observação: cada `codex exec resume` dispara SessionStart de novo, e o
    baseline é refeito. Uma mudança externa entre dois `resume` entra no
    baseline e não no ledger. No TUI não há SessionStart entre prompts; é o
    que a P4 testa.
  - **P5, primeira tentativa: FALHA.** O Stop devolveu (`stop_hook_active=false`,
    `answer=block`) com baratos e tipos PASS e `tests:jvm FAIL · tests:js FAIL`,
    mas o relatório tinha 62.427 caracteres com as 410 linhas `PASS`, e a
    linha `FAIL probe total sums the operands` estava no caractere 31.038,
    depois do corte de 6.000 do motivo. O agente só acertou o nome porque
    tinha escrito o teste. A impressão do achado também mudava a cada execução,
    por causa do nome aleatório `KofTestsEntry<hex>`. Correção por TDD: as
    linhas `PASS` saem do relatório (`(409 passing tests left out)`) e cada
    `FAIL <nome>:` vira o achado `failing-test@<nome>`, deduplicado entre
    alvos. `npm run test:sensors` 71 de 71.
  - **P5, repetição: PASSA.** Sem nenhum comando no turno, o agente copiou do
    motivo do Stop `FAIL probe total sums the operands: assertion failed`. O
    Stop seguinte (`stop_hook_active=true`) só reportou.
  - **P6 PASSA.** Antes, `lint-sensor` e `dup-sensor` deram PASS no arquivo
    com o erro. O Stop devolveu com
    `STOP SENSORS: lint PASS · dup PASS · gitleaks PASS · types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN`
    e `src/main/kof/sifuture/probe/Probe.kf:23:5: ERROR SEM021`.
  - **P7 PASSA.** Com `Int x = 7`, o Stop deixou terminar
    (`answer=continue`), os sete passos PASS. O marcador de devoluções da
    sessão ficou com três entradas (P5, repetição da P5, P6).
  - Probes removidos depois da P7 (`git status` sem `probe`).
  - **P8 PASSA com desvio.** `luna "rode git status e termine"` no Bash do
    executor, sessão `01a1fe55-fae7-70b0-8302-d7ffae7d715d`: SessionStart,
    PostToolUse e Stop com marca depois da chamada; a sessão tem
    `.worktree.json` e `.stop.log` no ledger (o `.txt` só nasce quando algo
    muda). Desvio: o worktree não estava limpo, porque o trabalho desta branch
    ainda não foi commitado; com o ledger vazio, o fallback olhou essas
    mudanças e o Stop saiu `answer=continue` com
    `lint SKIP · dup SKIP · gitleaks PASS · types:jvm SKIP · …`, não SKIP.
    Sem `decision`, como pedido.
  - Contexto terminal (TUI, sessão `01a1ff3f-1e5a-7ea0-a77e-523cb93acf77`),
    callback real. **P1 e P2 PASSAM**: o agente citou
    `src/main/kof/sifuture/probe/Probe.kf:3:1 ERROR long-function` da primeira
    escrita; a reescrita não teve resposta; ledger com `Probe.kf`; Stop do
    turno com os sete passos PASS. **P3 PASSA**: `ls` e `cat`, ledger igual.
  - P4, primeira tentativa: foi mandada numa sessão nova
    (`01a1ff51-e7c9-7bf3-8a37-a9a32f973863`), aberta depois de o usuário criar
    `External.kf`. O SessionStart incluiu o arquivo no baseline, o PostToolUse
    do `ls` ficou calado, e o Stop (ledger vazio, fallback para o worktree)
    devolveu com `External.kf:3:1 ERROR long-function`. Correto, mas não mede a
    P4.
  - P4, segunda tentativa, na sessão `01a1ff3f` retomada: **FALHA**. Ao
    retomar, o Codex dispara SessionStart de novo no primeiro prompt
    (19:30:53Z), e `worktree-baseline.mjs` sobrescrevia o baseline; o
    `External.kf` já existia e entrou nele, então o PostToolUse do `ls` não viu
    mudança. Defeito de desenho, o mesmo notado no `codex exec resume`.
    Correção por TDD: o SessionStart só grava o baseline quando a sessão ainda
    não tem um; ao retomar, vale o último olhar. Teste novo em
    `edit-hook.test.mjs`; `npm run test:sensors` 72 de 72.
  - P4, terceira tentativa, mesma sessão `01a1ff3f`: **PASSA**. Arquivo
    criado pelo usuário em outro terminal com a sessão aberta; a saída do `ls`
    já trouxe `src/main/kof/sifuture/probe/External.kf:3:1 ERROR long-function`
    e o agente citou; o ledger ganhou `External.kf`; o Stop devolveu uma vez
    (`answer=block`) e o seguinte, com `stop_hook_active=true`, só reportou.
    Limitação observada: o ledger dessa sessão também recebeu arquivos que o
    executor editou enquanto ela estava aberta (ExecPlan, `worktree-watch.mjs`,
    `edit-hook.test.mjs`). O watcher atribui à sessão qualquer mudança no
    worktree durante ela, como no Katacombs.
  - **P5 PASSA** (terminal): Stop `answer=block` com
    `… types:js PASS · tests:jvm FAIL · tests:js FAIL`; o `hook_prompt`
    entregue ao agente contém `FAIL probe total sums the operands: assertion failed`
    e `(409 passing tests left out)`; o agente citou o teste.
  - **P6 PASSA** (terminal): Stop `answer=block` com
    `lint PASS · dup PASS · gitleaks PASS · types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN`
    e `src/main/kof/sifuture/probe/Probe.kf:25:5: ERROR SEM021`. Marcador de
    devoluções da sessão com três entradas (P4, P5, P6).
  - **P7 PASSA** (terminal): `answer=continue`, os sete passos PASS.
  - Contexto terminal completo: P1 a P7 passam, P4 na terceira tentativa.
  - Contexto app desktop (Codex Desktop `0.169.0-alpha.11.1`, sessão
    `01a1ffcc-599b-7c01-89fe-b58600b9cc57`), callback real, sem P4 (só no
    terminal). **P1 e P2 PASSAM**: o agente citou
    `src/main/kof/sifuture/probe/Probe.kf:3:1 ERROR long-function`; reescrita
    sem resposta; Stop com sete PASS, o que também prova que o hook achou
    `node`, `python3`, `kof`, `mvn` e `java` sob o `PATH` do app. **P3 PASSA**:
    ledger igual depois de `ls` e `cat`. **P5 PASSA**: `answer=block`,
    `tests:jvm FAIL · tests:js FAIL` depois de tipos PASS, `hook_prompt` com
    `FAIL probe total sums the operands`. **P6 PASSA**: `answer=block` com
    `types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN` e
    `Probe.kf:25:5: ERROR SEM021`.
  - P7 no app, primeira tentativa: **FALHA por causa do prompt**. "Só 17
    operandos" foi lido no app como `a + 1 … + 17` (`probeTotal(0)` = 153) e no
    terminal como `a + 1 … + 16` (136); o `136` da P6 só batia no terminal. O
    Stop reportou `tests:jvm FAIL · tests:js FAIL` com `answer=continue`, sem
    devolver, porque `failing-test@probe total sums the operands` já tinha sido
    devolvido na P5 (deduplicação, como decidido). Efeito a registrar: quando o
    mesmo teste continua vermelho, o Stop só reporta e o agente pode terminar.
  - **P7 no app, repetição: PASSA.** Com `136` trocado por `153`, o Stop deixou
    terminar com os sete passos PASS.
  - Aceite do M3: P1 a P8 passam nos contextos pedidos (P4 só no terminal, P8
    só pelo `luna`), com as tentativas e correções acima.
- [x] M4. Documentação, registros e validação final (21/11/2026).
  - Seção "Hooks do Codex" em `docs/desenvolvimento.pt_BR.md` e "Codex hooks"
    em `docs/desenvolvimento.md`; parágrafo no `SENSORS.md`; seção
    "M3 — hooks reais no Codex CLI" em `.agent/validation/sensors-adoption.md`;
    entrada no `EXECPLAN.md`. `npm run docs:sensor` PASS.
  - Validação final, nesta ordem, todas com exit 0:
    `python3 -m unittest discover -s tests -p 'test_*.py'` (20 testes OK);
    `npm run test:sensors` (72 de 72); `npm run sensors:doctor` (seção
    `Codex hooks` toda `ok`); `npm run check` (`CHECK: PASS`; lint, dup e
    mutação SKIP porque nenhum `.kf` mudou contra a `main`); `npm run check:task`
    (`CHECK:TASK: PASS`, sete jornadas); `git diff --check`.
  - A5: `git diff --name-only main -- src tests kof-mut.json scripts/kof-sensors .agent/sensor-plans`
    vazio; nenhum arquivo novo nessas pastas; probes removidos; `.sensors/`
    ignorado pelo Git.

## Validation

Critérios de aceite. "Verificação" é o planejado; o observado vai para
`.agent/validation/sensors-adoption.md`.

| # | Fonte | Contexto → ação → resultado esperado | Verificação | Evidência esperada |
| --- | --- | --- | --- | --- |
| A1 | plano dos sensores, M3; decisão de 20/11 (três contextos) | em `codex exec`, terminal e app, os três eventos disparam como callback real e a resposta do PostToolUse e do Stop chega ao agente. Distingue: `canary.jsonl` apagado antes, `session_id` novo e hora depois do início separam disparo real de arquivo velho; os marcadores `CANARY-*` na resposta separam "disparou" de "entregou" | M0, passo 3, por contexto | `canary.jsonl` e resposta final de cada contexto |
| A2 | plano dos sensores, "Eventos, ordem e limites" e M3 | PostToolUse acha na primeira chamada após a edição (P1) e deixa de achar após a correção (P2); leitura não muda o ledger (P3); edição externa entra no escopo (P4) | M3 e testes do M1 | saídas dos hooks e ledger antes e depois |
| A3 | idem; "Decisões do M2 — 03/11", item 1 | Stop roda baratos → tipos → testes e para no primeiro que falha (P5, P6), e deixa terminar quando tudo passa (P7) | M3, e a ordem também nos testes do M1 com comandos falsos | logs do Stop por prova |
| A4 | "Decisões do M2 — 03/11", item 1; cenário S2 do M4 do plano dos sensores | sequência A, A, B, C, D → devolve, não, devolve, devolve, não; D continua reprovado; `stop_hook_active` não devolve | testes do M1 (payload sintético, registrado assim); no M0, o registro de `stop_hook_active` no segundo Stop real | saída do `test:sensors` e linha do M0 |
| A5 | Limites | nenhuma mudança em `src/`, testes Kof, fixtures, jornadas, `kof-mut.json` ou limites; nenhum probe nem `.sensors/` no commit | `git diff --name-only main`; `git status --porcelain --untracked-files=all` | lista no aceite |
| A6 | M2 | `sensors:doctor` mostra o manifesto, cada script citado, o último disparo de cada evento com hora depois do início do M3 e o `node` do hook. Distingue: com `.codex/hooks.json` citando um script inexistente (teste do doctor), ele acusa | teste em `test/sensors/sensors-doctor.test.mjs` e uma execução real no fim do M3 | saída do doctor |

Validação final, nesta ordem. O commit só acontece se todos passarem:

    python3 -m unittest discover -s tests -p 'test_*.py'
    npm run test:sensors
    npm run sensors:doctor
    npm run check
    npm run check:task
    git diff --check

Esperado: todos com exit 0; `check` com `CHECK: PASS` (`mutation` em SKIP,
porque nada de produção muda); `check:task` com `CHECK:TASK: PASS` e as sete
jornadas; o doctor sem linha `UNAVAILABLE` para hooks.

Obrigações do executor antes de entregar:

- Conferir de novo cada expectativa contra a fonte citada, separado de conferir
  se a prova a demonstra.
- Para cada critério de A1 a A6, registrar o comando ou procedimento, o
  resultado observado e onde está a evidência. Suíte verde sozinha não prova
  callback real.
- Registrar qualquer critério não verificado, contexto sem prova ou falha, sem
  apresentá-los como atendidos.

Recuperação: se os hooks atrapalharem o trabalho, `SENSORS=git` desliga o tier
do agente; para tirar de vez, apagar `.codex/hooks.json`. Nada fora do
repositório precisa ser desfeito, exceto os três links em `~/.local/bin`, que
são do ambiente e independem deste plano.
