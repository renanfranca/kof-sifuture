# Dívida dos sensores, lote 4: `Game`

## Purpose and success

O `npm run check` muta todo arquivo de produção alterado contra a `main`, e um
mutante sobrevivente reprova. Enquanto o `Game.kf` tiver sobreviventes ou achados
de lint, qualquer mudança nele trava o `check`. Ele é o centro do jogo: quase toda
funcionalidade nova passa por ele. Este lote paga a dívida dele e elimina o grupo
de CPD interno `Game.kf:208` ↔ `Game.kf:269`. Com isso, sobra só a UI
(`GameControls`, `GameView`) e as fixtures.

Sucesso:
- o KofMut em todo arquivo de produção alterado sai com 0 sobreviventes;
- `npm run lint:sensor` nesses arquivos dá 0 achados;
- `npm run dup:sensor` não acusa mais o grupo `Game.kf:208` ↔ `:269`;
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

Este lote parte da `main` com o lote 3 já mergeado (branch
`refactor/sensor-debt-batch-3`, commit `943f956`). Se `src/main/kof/sifuture/game/Overlap.kf`
não existir na `main`, o lote 3 ainda não entrou: pare e avise.

Lotes anteriores: 1 (PR #28), 2 (PR #29) e 3. O método, a automação de RED
(`.agent/tmp/debt-batch2/tools/redcheck.py`), a comparação de pixels
(`debt-tools/journeys.sh` e `debt-tools/pixels.py` contra `debt-r0/journeys-1/png`)
e os registros estão em `.agent/validation/sensor-debt-payoff.md`, seções
"R5 e R4, lote 1", "lote 2" e "lote 3". Siga o mesmo método.

Linha de base, medida no planejamento em 13/11 (o `Game.kf` é igual na `main`
`2f22f11` e na branch do lote 3):

| Medida | Valor |
| --- | --- |
| Linhas não vazias | 307 (limite 150) |
| A1 | 42 sobreviventes de 188 candidatos |
| Lint | 13: `long-file`; `keyboard` (`:62`) `high-complexity` e `too-many-statements`; `movement` (`:81`) `long-function`, `high-complexity` e `too-many-statements`; `navigate` (`:127`) `high-complexity`; `confirm(Int)` (`:150`) `high-complexity` e `too-many-statements`; `step` (`:195`, 108 linhas) `long-function`, `high-complexity`, `deep-nesting` e `too-many-statements` |
| CPD | `Game.kf:208` ↔ `:269`: a liberação dos meteoros verticais 6 e 7, repetida na tela de resultado e na de jogo |

Os sobreviventes vêm do relatório A1, `.agent/tmp/debt-a1/kofmut-a1-report.json`,
de 09/11. Os lotes anteriores podem ter matado parte deles, por isso o M0 mede de
novo.

### Achados do planejamento que o executor deve conferir

1. **O R4 domina este lote.** O arquivo precisa cair de 307 para no máximo 150
   linhas não vazias. Não dá para chegar lá só achatando funções. O guia do lint
   diz: separe pelo que muda junto, e não divida no meio de uma responsabilidade só
   para baixar a contagem. O `Game` hoje tem pelo menos três responsabilidades:
   - **entrada de direção** (`:20-29`, `:38-107`): teclado e direcional, com as
     flags `held*`, `pad*` e `navigation*Held`. Nenhum código fora do `Game` lê
     essas flags; os testes usam só os métodos (`keyboard`, `movement`,
     `padPressed`, `clearKeyboard`, `rearmKeyboard`);
   - **telas e menus** (`navigate`, `confirm`, `enterMenu`, `pause`, `resume`,
     `restart`, `abandon`, `finish`);
   - **o passo da partida** (`step`, `:218-305`): avançar o estágio, resolver os
     contatos com subchefe, chefe e meteoros e somar a pontuação.

   Um caminho que respeita os limites abaixo:
   - a entrada de direção vira uma classe nova que guarda as flags, e os métodos
     públicos do `Game` delegam para ela;
   - o passo da partida vira funções nomeadas. As regras de contato podem ir para
     funções de topo num arquivo novo, como `ShipContact.kf`, `Overlap.kf` e
     `Course.kf` fizeram, recebendo as entidades por parâmetro (no máximo 4, pelo
     lint) e devolvendo os pontos ganhos.

   Decida no R4 com o skill `refactor-design`. O que não pode mudar está em
   "Limites".

2. **O CPD é a liberação dos meteoros 6 e 7**, igual nas duas cópias. Uma função
   extraída resolve. Os sobreviventes em `:209-211` caem nela.

3. **Valores iniciais `false` sobrevivem** em `:22-26` (campos `pad*` e
   `heldLeft`), `:33` e `:35` (`meteors[6].active = false` no construtor), `:51-54`
   (`rearmKeyboard`), `:63` e `:95` (`var held = false`). Confira primeiro se outro
   código já os define antes da leitura (o caso `expanded` do piloto da UI e o
   `rightFrame` do lote 2). Exemplo: o `Meteor.reset()` chamado por `start()` pode
   já desligar os meteoros 6 e 7. Se for redundante, a refatoração tira a
   atribuição; se não for, um teste a cobre.

4. **`confirm()` sorteia a semente com `random.int`** (`:143-147`), e ela só é
   usada se a ação for iniciar ou reiniciar. Os 7 sobreviventes de `:143` vêm
   daí: um teste não enxerga qual semente saiu. `random` não é semeado nem usado
   em mais nenhum lugar (`grep` em `src/main`). Sortear sempre e deixar o
   `confirm(Int)` decidir tira a condição. O comportamento visível fica igual,
   porque a semente só importa em `start`. Confirme isso de novo antes de aplicar.
   Se não houver saída sem mudar a API, aplique a regra de equivalentes.

5. **Limites que repetem `min`:** `:215` (`displayedScore` não passa de `score`) e
   `:327` (`stagePosition` não passa de `WORLD_WIDTH`). Com `>` trocado por `>=`,
   o resultado é igual na igualdade. É o mesmo caso do `Credits` no lote 1:
   `math.min`, com a constante `static final` passada antes por uma variável local
   tipada.

### Limites

- **Arquivos de produção que podem mudar:** `Game.kf` e arquivos novos. Outro
  arquivo de `src/main/kof/sifuture/game/` só muda para receber uma regra movida
  do `Game`, continuando com 0 sobreviventes e 0 achados, porque o `check` também
  vai mutá-lo.
- **Não altere a UI nem o `Main.kf`:** `GameControls.kf`, `GameView.kf`,
  `ControlsGuide.kf`, `GuideDisclosure.kf` e `Main.kf`. Por isso, tudo o que eles
  usam do `Game` fica com o mesmo nome e a mesma assinatura:
  - `GameControls`: `screen`, `menuSelection`, `pauseSelection`, `confirm()`,
    `keyboard`, `movement`, `clearKeyboard`, `rearmKeyboard`, `canSpecial`,
    `trySpecial` e `countComplete`;
  - `GameView`: `screen`, `credits`, `menuEntrance`, `menuSelection`,
    `pauseSelection`, `background`, `ship`, `items`, `meteors`, `subchief`,
    `boss`, `weapons`, `score`, `displayedScore`, `countComplete`,
    `stagePosition` e `resultIndex`;
  - `Main.kf`: `step`.
- **Os testes não mudam de expectativa.** Os campos e métodos que eles usam
  continuam no `Game`: além dos acima, `steps`, `stageSteps`, `start`, `pause`,
  `resume`, `restart`, `abandon`, `navigate`, `padPressed` e `confirm(Int)`. Se
  algum membro precisar sair do `Game`, pare e mostre.
- **Testes novos vão em arquivos novos por assunto**, em
  `src/test/kof/sifuture/game/`. Não aumente `BossJourney.kf` nem
  `SubchiefJourney.kf`. Os arquivos de jornada existentes (`ControlsJourney`,
  `MenuJourney`, `StageJourney`, `ResultJourney`) só crescem se o assunto for
  exatamente o deles, e continuam com 0 achados de lint. Pode ajustar
  `JourneyScenarios.kf`.
- **Classe, função ou arquivo novo em `src/main/kof`:** importe explicitamente
  onde usar, inclusive nos testes. Sem o `import`, o check de tipos passa e a suíte
  falha com `SEM015`.
- **Sobrecarga:** no lote 3, chamar uma sobrecarga sem `this.` deu `SEM015`. Use
  `this.` como o `Game` já faz em `keyboard` e `confirm`.
- **`kof.math.min` com uma constante `static final`** direto como argumento dá
  `SEM025` no 0.7.0 e no 0.6.4. Passe a constante antes por uma variável local
  tipada.
- **A ordem dos efeitos dentro do passo não muda.** Contatos, pontuação, explosões
  e avanço das entidades acontecem na mesma ordem de hoje. As capturas pixel a
  pixel e as jornadas pegam boa parte disso, mas não tudo: confira a ordem no diff.
- **Sem comentários** em código, testes ou fixtures (`AGENTS.md`).

## Decisions

**Equivalentes.** Regra decidida em 11/11 depois do lote 1. Um mutante
equivalente é aquele que nenhum teste de comportamento consegue matar, porque o
jogo fica igual com ele. Quase sempre ele aponta código redundante. Antes de chamar
um mutante de equivalente:

1. procure uma refatoração que preserve o comportamento e tire o operador
   redundante: remover uma cláusula implicada por outra, trocar
   `if (x > M) { x = M }` por `min`, mover uma regra repetida para uma função que
   outros chamadores exercitam, remover uma atribuição que outro código já faz;
2. só quando essa refatoração não existir, anote a prova e **pare antes do commit**
   (ponto de parada 2 do plano mestre). Sem supressão, o `check` reprovaria.

**A API pública do `Game` não muda.** O `Game` pode delegar para classes e funções
novas, mas cada membro listado em "Limites" continua nele com o mesmo nome e a
mesma assinatura. Alternativa descartada: mover entidades (`ship`, `weapons` etc.)
para uma classe nova e mudar a UI, que é dívida de outro lote e quebraria o limite
"não altere a UI".

## Milestones

### M0. Medir a linha de base

```bash
mkdir -p .agent/tmp/debt-batch4
printf '%s\n' '["src/main/kof/sifuture/game/Game.kf"]' > .agent/tmp/debt-batch4/mut-scope.json
uptime
kof-mut run --project . --files .agent/tmp/debt-batch4/mut-scope.json \
  --config kof-mut.json --report-dir .agent/tmp/debt-batch4/m0 --run-id "$(uuidgen)"
```

Registre no aceite os candidatos, mortos e sobreviventes, comparados com o A1. Os
ids dos sobreviventes no M0 são a lista de trabalho. Se a rodada passar de 1 hora,
registre o `uptime` e siga.

### M1. R5: matar os sobreviventes

Para cada sobrevivente, um teste de comportamento que o mate, com o skill
`tdd-behavior-autonomous-quiet`. O RED se observa como nos lotes anteriores: o
teste nasce verde com o produto correto; aplique o mutante à mão (ou com o
`redcheck.py`), rode a suíte JVM, veja o teste nomeado falhar por asserção e
restaure o arquivo. Registre o par mutante e teste.

Observe pelo que o jogador vê ou pela API pública do `Game`: tela atual, seleção
do menu, posição e direção da nave, pontuação, meteoros ativos.

Ao fim do M1, os sobreviventes que restam são os candidatos a equivalente, cada um
com o motivo.

### M2. R4: refatorar até 0 achados

Com o skill `refactor-design`, uma refatoração por vez, com a suíte verde em JVM e
JS depois de cada uma:
1. CPD dos meteoros 6 e 7 (achado 2);
2. limites com `min` (achado 5) e a semente do `confirm()` (achado 4);
3. valores iniciais redundantes (achado 3);
4. separação das responsabilidades (achado 1), até `npm run lint:sensor --
   src/main/kof/sifuture/game/Game.kf` dar 0 e todo arquivo novo também.

Depois, KofMut em todo arquivo de produção alterado: 0 sobreviventes.

### M3. Registros e validação final

- Uma seção nova "R5 e R4, lote 4" em `.agent/validation/sensor-debt-payoff.md`,
  com:
  - o M0;
  - sobreviventes antes e depois;
  - os pares mutante e teste;
  - as refatorações que tiraram equivalentes, com a prova de cada uma;
  - a nova divisão de responsabilidades, com o que foi para onde;
  - o tempo gasto, para estimar a UI (`GameControls`, `GameView`).
- Uma linha no `EXECPLAN.md` da raiz.

## Progress

- [x] M0. Linha de base do KofMut no `Game.kf` (13/11, 09:02 a 09:31): 188
  candidatos, 146 mortos, 41 sobreviventes e 1 timeout por carga (`82:22`); os
  mesmos 42 `id`s do A1. A `main` partiu de `a6ee1fb` (PR #30, lote 3).
- [x] M1. R5: 13 testes em quatro arquivos novos; 24 sobreviventes caem só por
  testes novos, sempre por asserção; os outros 18 ficam para o M2.
- [x] M2. R4: CPD, `min`, semente, valores iniciais e separação; lint 0; KofMut 0.
  `Game` com 150 linhas não vazias; `DirectionFlags`, `DirectionInput`, `Match` e
  `Encounters` novos; KofMut nos 5 arquivos 119/119 (09:37 a 09:52).
- [x] M3. Registros e validação final: seção "R5 e R4, lote 4" do aceite e linha
  no `EXECPLAN.md`; validação final de 09:59 a 10:34, todos com exit 0,
  `mutation` PASS (119/119) e sete jornadas PASS.

## Validation

Critérios de aceite. A coluna "Verificação" é o planejado; registre o observado no
aceite.

| # | Contexto, ação e resultado esperado | Verificação |
| --- | --- | --- |
| A1 | KofMut em todo arquivo de produção alterado, depois do M2: `candidates = killed`, 0 sobreviventes, 0 timeouts, `status` `complete` | comando do M0 com a lista de `git diff --name-only main -- src/main` e outro `--report-dir`; registrar os números |
| A2 | Cada teste novo mata um mutante nomeado: com o mutante aplicado, o teste falha por asserção, e nenhum teste fora da lista falha | tabela mutante e teste no aceite |
| A3 | Nenhum equivalente fica anotado. Se sobrar um, ele tem prova e a entrega para antes do commit | seção de equivalentes do aceite |
| A4 | `npm run lint:sensor -- <arquivos de produção alterados>` dá `PASS (0 findings)`, com o `Game.kf` em até 150 linhas não vazias; o mesmo vale para todo arquivo de teste novo ou alterado | rodar |
| A5 | O grupo `Game.kf:208` ↔ `:269` some, e nenhum grupo novo aparece | `npm run dup:sensor` com o diff contra a `main`: 0 achados |
| A6 | Só arquivos permitidos mudam: `git diff --name-only main -- src/main` não lista a UI nem o `Main.kf`; cada arquivo existente além do `Game.kf` tem o motivo no aceite | rodar |
| A7 | A API do `Game` usada pela UI, pelo `Main` e pelos testes continua igual: a UI e o `Main` compilam sem mudança, e nenhum teste existente muda de expectativa | `git diff main -- src/test` só com arquivos novos, `JourneyScenarios.kf` e crescimentos por assunto, sem expectativa alterada; `npm run check` com `types` PASS |
| A8 | A contagem de casos sobe em relação à `main` de partida, em JVM e JS, no 0.7.0 e no 0.6.4 | `node scripts/kof-tests.mjs --target jvm` e `--target js`, depois com `KOF=~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof`; registrar o número antes e depois |
| A9 | O comportamento não muda: as sete jornadas passam, e as capturas ficam iguais às do R0 pixel a pixel | `npm run check:task` e a mesma comparação de pixels dos lotes anteriores |
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
  está certa, inclusive os achados 3 e 4. Isso é separado de conferir se os testes
  a demonstram.
- Para cada critério de A1 a A10, registrar no aceite o comando, o resultado
  observado e onde está a evidência. Uma suíte verde sozinha não prova cada
  critério.
- Registrar antes da entrega qualquer critério não verificado, cobertura que faltou
  ou falha, sem apresentá-los como atendidos.
