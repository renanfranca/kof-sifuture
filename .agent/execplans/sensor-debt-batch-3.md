# Dívida dos sensores, lote 3: `Subchief`, `Boss` e `Weapons`

## Purpose and success

O `npm run check` muta todo arquivo de produção alterado contra a `main`, e um
mutante sobrevivente reprova. Enquanto um arquivo tiver sobreviventes ou achados de
lint, qualquer mudança futura nele trava o `check`. Este lote paga a dívida de
três arquivos de `src/main/kof/sifuture/game/`: `Subchief.kf`, `Boss.kf` e
`Weapons.kf`. Ele também elimina o grupo de CPD (código duplicado) entre
`Boss.kf:114` e `Subchief.kf:91`.

Sucesso:
- o KofMut em todo arquivo de produção alterado sai com 0 sobreviventes;
- `npm run lint:sensor` nesses arquivos dá 0 achados;
- `npm run dup:sensor` não acusa mais o grupo `Boss.kf:114` ↔ `Subchief.kf:91`;
- o `npm run check` passa, com o passo `mutation` rodando de verdade (sem SKIP);
- o jogo se comporta igual: as sete jornadas de navegador passam e as capturas não
  mudam nenhum pixel.

## Context and limits

Plano mestre: `/home/renanfranca/.agents/skills/_temporary/codex-skills-ai-context/2026-11-05_FEATURE_sifuture-sensor-debt-payoff.md`.
Leia as "Regras invioláveis" dele antes de começar. Elas valem aqui:
- o jogo não muda de comportamento;
- a contagem de casos só sobe;
- nenhum limite, regra ou medidor muda;
- não há supressão;
- na produção, uma refatoração por vez, com os testes verdes.

Lotes anteriores, ambos na `main`:
- lote 1, PR #28 (`eb73913`);
- lote 2, PR #29 (`2f22f11`): `Shot`, `Blaster`, `Ship` e `SpecialBeam`, de 102
  sobreviventes para 0, com 55 testes novos, de 212 para 267 casos.

O método, os pares mutante e teste e as refatorações estão em
`.agent/validation/sensor-debt-payoff.md`, seções "R5 e R4, lote 1",
"Equivalentes eliminados por refatoração" e "R5 e R4, lote 2". Siga o mesmo
método, inclusive a automação de RED do lote 2 (`.agent/tmp/debt-batch2/`).

Linha de base, medida no planejamento em 12/11 na `main` `2f22f11`:

| Arquivo | Linhas não vazias | A1: sobreviventes de candidatos | Lint agora |
| --- | --- | --- | --- |
| `Subchief.kf` | 109 físicas | 18 de 71 | 5: `high-complexity` em `:41`; `deep-nesting` em `:74`; `high-complexity`, `deep-nesting` e `too-many-statements` em `:89` |
| `Boss.kf` | 129 físicas | 30 de 101 | 2 em `:111`: `high-complexity` e `too-many-statements` |
| `Weapons.kf` | 174 (limite 150) | 42 de 139 | 7: `long-file`; `high-complexity` e `deep-nesting` em `:32`; `deep-nesting` em `:52` e `:76`; `high-complexity` em `:89` e `:131` |

Os sobreviventes vêm do relatório A1, `.agent/tmp/debt-a1/kofmut-a1-report.json`,
de 09/11. Os lotes 1 e 2 podem ter matado parte deles, por isso o M0 mede de novo.

### Achados do planejamento que o executor deve conferir

1. **O `reaches()` do `SpecialBeam` não serve direto no `Weapons`.** Ele testa um
   alvo contra a faixa do raio (`x` a `x + 319`, `y` a `y + 32`). No `Weapons`, a
   faixa é a do alvo: a frente do laser dentro da largura do subchefe ou do chefe,
   e o laser na altura dele. O que se reaproveita é a ideia: "alguma borda dentro
   da faixa" vira "as duas faixas se sobrepõem", **só quando a união das bordas é
   contínua**. Isso exige que o objeto cujas bordas são testadas seja no máximo tão
   alto quanto a faixa. Por isso as regras de faixa se dividem em dois grupos:

   | Regra | Bordas testadas e faixa | União contínua? |
   | --- | --- | --- |
   | `Weapons.hitSubchiefLaser` | laser 12 na faixa do subchefe 26 | sim |
   | `Weapons.hitBossLaser` | laser 12 na faixa do chefe 51 | sim |
   | `Weapons.hitBossBlaster` | blaster 21 na faixa do chefe 51 | sim |
   | `Boss.absorbMeteors` | meteoro 18 na faixa do chefe 51 | sim |
   | `Boss.touchesShip` | nave 20 na faixa do chefe 51 | sim |
   | `Weapons.hitSubchiefBlaster` | subchefe 26 na faixa do blaster 21 | **não**: com `blaster.y - 4 <= chief.y <= blaster.y - 1`, nenhuma borda do subchefe cai na faixa e não há acerto |
   | `Subchief.touchesShip`, primeiro ramo | subchefe 26 na faixa da nave 20 | **não**: com `ship.y - 5 <= y <= ship.y - 1`, não há contato |

   Os dois "não" são buracos de verdade, como o do tiro do chefe no lote 1. Eles
   ficam como estão, e cada um ganha um teste que o fixe. Corrigi-los muda o jogo
   e é decisão do usuário, fora deste lote. O segundo ramo de `Subchief.touchesShip`
   (`x + 28` na largura da nave) testa só a borda de cima e também fica como está.

   Onde a união é contínua, uma função de sobreposição de faixas num lugar só deve
   tirar os equivalentes, como o `reaches()` fez no lote 2. Onde ela fica (arquivo
   novo com função de topo, como `ShipContact.kf`, ou método do `Shot` e do
   `Blaster`) se decide no R4.

2. **O `Bool` de `Subchief.damage` e de `Weapons.hitSubchief*` ninguém lê.** O
   `Game.kf:258-262` chama os quatro e ignora o retorno, e nenhum teste nem fixture
   o lê (`grep` em `src` e `tests`). Isso explica os sobreviventes `false → true` e
   `true → false` em `Subchief.kf:51` e `:57` e em `Weapons.kf:90`, `:102`, `:106`,
   `:114` e `:122`. O único leitor interno é o `fatal` de `hitSubchiefSpecial`, e
   ele também é redundante: depois do dano fatal, o subchefe está em `Explosion`, e
   `damage` retorna antes de mexer em qualquer coisa. Veja a decisão abaixo.

3. **`Boss.spriteFrame`, `frenzySteps > 0`.** Com `frenzySteps == 0`, a conta
   `((0 - 1) / 4) % 3` dá 0 se a divisão inteira truncar para zero, o mesmo que o
   `return 0`. Então a guarda seria redundante. Confirme como o Kof divide números
   negativos em JVM e em JS antes de tirá-la. Se os dois alvos divergirem, a guarda
   fica e o mutante precisa de outra saída.

4. **O CPD `Boss.kf:114` ↔ `Subchief.kf:91`** é o passo até o destino
   (`if (x < endX) x + 1 else if (x > endX) x - 1`, o mesmo para `y`, e o sorteio
   de destino novo quando chega). A diferença entre as cópias está só no dono,
   então cabe uma função extraída para os dois. Os sobreviventes `<` → `<=` e
   `>` → `>=` em `Subchief.kf:93-94` e `Boss.kf:116-117` caem nesse trecho.

5. **`Weapons.kf` passa do limite de linhas** (174 de 150 não vazias). Achatar o
   aninhamento e mover as regras de faixa sozinhos talvez não bastem. O guia do
   lint diz: se o arquivo tem mais de uma responsabilidade, separe pelo que muda
   junto. Não divida no meio de uma responsabilidade só para baixar a contagem.

### Limites

- **Arquivos de produção que podem mudar:** `Subchief.kf`, `Boss.kf`,
  `Weapons.kf` e arquivos novos. `Shot.kf`, `Blaster.kf`, `SpecialBeam.kf` e
  `ShipContact.kf` só podem mudar para receber uma regra movida do `Weapons`,
  continuando com 0 sobreviventes e 0 achados, porque o `check` também vai mutá-los.
- **Não altere `Game.kf`.** Ele é o lote 4. Toda chamada que o `Game` faz a
  `Weapons`, `Subchief` e `Boss` precisa continuar compilando sem mudar o `Game`.
- **Não altere arquivos de UI:** `GameControls.kf`, `GameView.kf`,
  `ControlsGuide.kf` e `GuideDisclosure.kf`. O `GameView` lê
  `game.weapons.lasers`, `game.weapons.blaster`, `game.weapons.beams`,
  `game.weapons.charges` e `game.boss.weapons`. Esses campos ficam.
- **Não altere `BossWeapons.kf`**, que já está sem dívida desde o lote 1, a menos
  que uma refatoração exija. Se exigir, pare e mostre o motivo.
- **Testes novos vão em arquivos novos por assunto**, em `src/test/kof/sifuture/game/`.
  Não aumente `BossJourney.kf` (1032 linhas físicas) nem `SubchiefJourney.kf`
  (928). `WeaponsJourney.kf` só cresce se o assunto for exatamente o dele, e
  continua com 0 achados de lint. Pode ajustar `JourneyScenarios.kf`, como no
  lote 2.
- **Classe, função ou arquivo novo em `src/main/kof`:** importe explicitamente
  onde usar, inclusive nos testes. Sem o `import`, o check de tipos passa e a suíte
  falha com `SEM015`.
- **Sem comentários** em código, testes ou fixtures (`AGENTS.md`).
- **`kof.math.min` com uma constante `static final`** direto como argumento dá
  `SEM025` no 0.7.0 e no 0.6.4. Passe a constante antes por uma variável local
  tipada, como no `Credits.kf` e no `Ship.kf`.

## Decisions

**Equivalentes.** Regra decidida em 11/11 depois do lote 1. Um mutante
equivalente é aquele que nenhum teste de comportamento consegue matar, porque o
jogo fica igual com ele. Quase sempre ele aponta código redundante. Antes de chamar
um mutante de equivalente:

1. procure uma refatoração que preserve o comportamento e tire o operador
   redundante. Exemplos: remover uma cláusula implicada por outra, trocar
   `if (x > M) { x = M }` por `min`, mover uma regra repetida para uma função que
   outros chamadores exercitam, juntar bordas numa sobreposição quando a união é
   contínua;
2. só quando essa refatoração não existir, anote a prova e **pare antes do commit**
   (ponto de parada 2 do plano mestre). Sem supressão, o `check` reprovaria.

**Retornos que ninguém lê.** `Subchief.damage` e `Weapons.hitSubchiefLaser`,
`hitSubchiefBlaster` e `hitSubchiefSpecial` passam a não devolver valor, como
`Boss.damage` e `Weapons.hitBoss*` já fazem. Em `hitSubchiefSpecial`, o `fatal`
sai: cada raio em contato chama `chief.damage(1)`. Isso só muda a assinatura
interna: o `Game` ignora o retorno hoje e compila igual. Antes de aplicar,
confirme de novo com `grep` que nenhum chamador em `src` ou `tests` lê o valor.
Se algum ler, pare e mostre.

## Milestones

### M0. Medir a linha de base

Rode o KofMut só nos três arquivos. O escopo é uma lista JSON, no mesmo formato de
`.agent/tmp/debt-a1/mut-scope.json`:

```bash
mkdir -p .agent/tmp/debt-batch3
printf '%s\n' '["src/main/kof/sifuture/game/Subchief.kf", "src/main/kof/sifuture/game/Boss.kf", "src/main/kof/sifuture/game/Weapons.kf"]' > .agent/tmp/debt-batch3/mut-scope.json
uptime
kof-mut run --project . --files .agent/tmp/debt-batch3/mut-scope.json \
  --config kof-mut.json --report-dir .agent/tmp/debt-batch3/m0 --run-id "$(uuidgen)"
```

Registre no aceite os candidatos, mortos e sobreviventes por arquivo, comparados com
o A1. Os ids dos sobreviventes no M0 são a lista de trabalho de M1 a M3. Se a rodada
passar de 1 hora, registre o `uptime` e siga.

### M1. `Subchief` e `Boss`, com o CPD

Para cada arquivo, nesta ordem:
1. **R5.** Para cada sobrevivente, um teste de comportamento que o mate, com o skill
   `tdd-behavior-autonomous-quiet`. O RED se observa como nos lotes 1 e 2: o teste
   nasce verde com o produto correto; aplique o mutante à mão, rode a suíte JVM,
   veja o teste nomeado falhar por asserção e restaure o arquivo. Registre o par
   mutante e teste. Os buracos de `Subchief.touchesShip` do achado 1 ganham testes
   que fixem "sem contato".
2. **R4.** Com o skill `refactor-design`, refatore até
   `npm run lint:sensor -- <arquivo>` dar 0, uma refatoração por vez. Aqui entram
   o CPD do achado 4, a decisão dos retornos para `Subchief.damage` e a guarda do
   achado 3.
3. KofMut só nesse arquivo: 0 sobreviventes.

### M2. `Weapons`

O mesmo ciclo do M1, com estes pontos:
- cubra cada regra de faixa nas bordas: o último pixel que acerta e o primeiro que
  não acerta, de cima e de baixo, e o buraco de `hitSubchiefBlaster`;
- cubra as guardas `return false` de `canSpecial` e `fireSpecial` pelo que o jogo
  mostra: com 0 cargas, o especial não sai e as cargas não ficam negativas;
- no R4, aplique a decisão dos retornos, junte as regras de faixa contínuas e
  resolva o `long-file` pelo achado 5. A API que o `Game` e o `GameView` usam fica
  igual.

### M3. Registros e validação final

- Uma seção nova "R5 e R4, lote 3" em `.agent/validation/sensor-debt-payoff.md`,
  com:
  - o M0;
  - sobreviventes antes e depois, por arquivo;
  - os pares mutante e teste;
  - as refatorações que tiraram equivalentes, com a prova de cada uma;
  - os buracos preservados, com o teste que fixa cada um;
  - o tempo gasto, para estimar o lote 4 (`Game`).
- Uma linha no `EXECPLAN.md` da raiz.

## Progress

- [x] M0. Linha de base do KofMut nos três arquivos (12/11, 12:23 a 12:59): 311
  candidatos, 221 mortos, 90 sobreviventes, os mesmos `id`s do A1.
- [x] M1. `Subchief` e `Boss`: R5, R4 com o CPD, KofMut com 0.
- [x] M2. `Weapons`: R5, R4, KofMut com 0. RED: 68 sobreviventes mortos por
  testes novos, 22 eliminados por refatoração; pré-checagem do KofMut na cópia
  com 265/265 mortos nos 7 arquivos de produção.
- [x] M3. Registros e validação final (13:35 a 14:31): `check` e `check:task`
  PASS com `mutation` 265/265; aceite na seção "R5 e R4, lote 3" de
  `.agent/validation/sensor-debt-payoff.md`; linha no `EXECPLAN.md` da raiz.

## Validation

Critérios de aceite. A coluna "Verificação" é o planejado; registre o observado no
aceite.

| # | Contexto, ação e resultado esperado | Verificação |
| --- | --- | --- |
| A1 | KofMut em todo arquivo de produção alterado, depois do M2: `candidates = killed`, 0 sobreviventes, 0 timeouts, `status` `complete` | comando do M0 com a lista de `git diff --name-only main -- src/main` e outro `--report-dir`; registrar os números |
| A2 | Cada teste novo mata um mutante nomeado: com o mutante aplicado à mão, o teste falha por asserção, e nenhum teste fora da lista falha | tabela mutante e teste no aceite |
| A3 | Nenhum equivalente fica anotado. Se sobrar um, ele tem prova e a entrega para antes do commit | seção de equivalentes do aceite |
| A4 | `npm run lint:sensor -- <arquivos de produção alterados>` dá `PASS (0 findings)`, e o mesmo vale para todo arquivo de teste novo ou alterado | rodar |
| A5 | O grupo de CPD `Boss.kf:114` ↔ `Subchief.kf:91` some, e nenhum grupo novo aparece | `npm run dup:sensor` com o diff contra a `main`: 0 achados |
| A6 | Só arquivos permitidos mudam: `git diff --name-only main -- src/main` lista apenas `Subchief.kf`, `Boss.kf`, `Weapons.kf`, arquivos novos e, se receberam uma regra, `Shot.kf`, `Blaster.kf`, `SpecialBeam.kf` ou `ShipContact.kf`. `Game.kf`, `BossWeapons.kf` e a UI não aparecem | rodar |
| A7 | Os dois buracos preservados continuam: o subchefe com `y` de `ship.y - 5` a `ship.y - 1`, na largura da nave, não a atinge; o blaster não acerta o subchefe com `chief.y` de `blaster.y - 4` a `blaster.y - 1` | testes nomeados no aceite |
| A8 | A contagem de casos sobe de 267, em JVM e JS, no 0.7.0 e no 0.6.4 | `node scripts/kof-tests.mjs --target jvm` e `--target js`, depois com `KOF=~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof` |
| A9 | O comportamento não muda: as sete jornadas passam, e as capturas ficam iguais às do R0 pixel a pixel | `npm run check:task` e a mesma comparação de pixels dos lotes 1 e 2 |
| A10 | `npm run check` mostra `mutation  PASS`, com os arquivos alterados no escopo, e `CHECK: PASS` | validação final |

Validação final, nesta ordem. O commit só acontece se todos passarem:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
npm run test:sensors
npm run check
npm run check:task
git diff --check
```

Esperado:
- todos com exit 0;
- `npm run check` com `mutation  PASS`, e não SKIP;
- `npm run check:task` com as sete jornadas em PASS.

Obrigações do executor antes de entregar:
- Conferir de novo, pelo código atual e pelo relatório do M0, se cada expectativa
  está certa, inclusive a tabela de uniões contínuas do achado 1. Isso é separado de
  conferir se os testes a demonstram.
- Para cada critério de A1 a A10, registrar no aceite o comando, o resultado
  observado e onde está a evidência. Uma suíte verde sozinha não prova cada
  critério.
- Registrar antes da entrega qualquer critério não verificado, cobertura que faltou
  ou falha, sem apresentá-los como atendidos.
