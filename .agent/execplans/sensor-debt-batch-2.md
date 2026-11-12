# Dívida dos sensores, lote 2: `Shot`, `Blaster`, `Ship` e `SpecialBeam`

## Purpose and success

O `npm run check` muta todo arquivo de produção alterado contra a `main`, e um
mutante sobrevivente reprova. Enquanto um arquivo tiver sobreviventes ou achados de
lint, qualquer mudança futura nele trava o `check`. Este lote paga a dívida de
quatro arquivos de `src/main/kof/sifuture/game/`: `Shot.kf`, `Blaster.kf`,
`Ship.kf` e `SpecialBeam.kf`.

Sucesso:
- o KofMut nos quatro arquivos sai com 0 sobreviventes;
- `npm run lint:sensor` nos quatro dá 0 achados;
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

Lote 1 (PR #28, na `main` em `eb73913`): 7 arquivos, de 56 sobreviventes para 0,
com 31 testes novos e 181 casos para 212. Ele criou `ShipContact.kf`, que agora
guarda a regra de contato com a nave. O método e as evidências estão em
`.agent/validation/sensor-debt-payoff.md`, seções "R5 e R4, lote 1" e
"Equivalentes eliminados por refatoração". Siga o mesmo método.

Linha de base, medida no planejamento em 12/11 na `main` `eb73913`:

| Arquivo | Linhas | Sobreviventes no A1 (de candidatos) | Lint agora |
| --- | --- | --- | --- |
| `Shot.kf` | 58 | 17 de 48 | 0 |
| `Blaster.kf` | 55 | 17 de 40 | 1: `too-many-statements` em `:40` |
| `Ship.kf` | 97 | 16 de 55 | 4 em `:46`: `deep-nesting`, `high-complexity`, `long-function`, `too-many-statements` |
| `SpecialBeam.kf` | 86 | 52 de 101 | 1: `high-complexity` em `:63` |

Os sobreviventes vêm do relatório A1, `.agent/tmp/debt-a1/kofmut-a1-report.json`,
de 09/11. Os testes do lote 1 podem ter matado parte deles, por isso o M0 mede de
novo. Nenhum dos quatro arquivos está em grupo de CPD.

Limites:
- **Não altere produção fora do lote.** O `check` muta todo arquivo alterado, e
  `Weapons` (42 sobreviventes), `Game` (42), `Boss` (30) e `Subchief` (18) ficam
  para os próximos lotes. Se uma refatoração exigir mudar um deles, pare e mostre o
  motivo. O `ShipContact.kf` pode mudar, desde que continue com 0 sobreviventes e 0
  achados.
- **Não altere arquivos de UI:** `GameControls.kf`, `GameView.kf`,
  `ControlsGuide.kf` e `GuideDisclosure.kf`.
- **Testes novos vão em arquivos novos por assunto**, em `src/test/kof/sifuture/game/`.
  Não aumente `BossJourney.kf` nem `SubchiefJourney.kf`. Outro arquivo existente só
  pode crescer quando o assunto for exatamente o dele, e precisa continuar com 0
  achados de lint.
- **Classe ou arquivo novo em `src/main/kof`:** importe explicitamente onde usar. Sem
  o `import`, o check de tipos passa e a suíte falha com `SEM015`.
- **Sem comentários** em código, testes ou fixtures (`AGENTS.md`).
- **`kof.math.min` com uma constante `static final`** direto como argumento dá
  `SEM025` no 0.7.0 e no 0.6.4. Passe a constante antes por uma variável local
  tipada, como no `Credits.kf`.

## Decisions

Regra para mutante equivalente, decidida em 11/11 depois do lote 1. Um mutante
equivalente é aquele que nenhum teste de comportamento consegue matar, porque o
jogo fica igual com ele. Quase sempre ele aponta código redundante. Antes de chamar
um mutante de equivalente:

1. procure uma refatoração que preserve o comportamento e tire o operador
   redundante. Exemplos do lote 1: remover uma cláusula implicada por outra, trocar
   `if (x > M) { x = M }` por `min`, mover uma regra repetida para uma função que
   outros chamadores exercitam;
2. só quando essa refatoração não existir, anote a prova e **pare antes do commit**
   (ponto de parada 2 do plano mestre). Sem supressão, o `check` reprovaria.

## Milestones

### M0. Medir a linha de base

Rode o KofMut só nos quatro arquivos. O escopo é uma lista JSON, no mesmo formato de
`.agent/tmp/debt-a1/mut-scope.json`:

```bash
mkdir -p .agent/tmp/debt-batch2
printf '%s\n' '["src/main/kof/sifuture/game/Shot.kf", "src/main/kof/sifuture/game/Blaster.kf", "src/main/kof/sifuture/game/Ship.kf", "src/main/kof/sifuture/game/SpecialBeam.kf"]' > .agent/tmp/debt-batch2/mut-scope.json
uptime
kof-mut run --project . --files .agent/tmp/debt-batch2/mut-scope.json \
  --config kof-mut.json --report-dir .agent/tmp/debt-batch2/m0 --run-id "$(uuidgen)"
```

Registre no aceite os candidatos, mortos e sobreviventes por arquivo, comparados com
o A1. Os ids dos sobreviventes no M0 são a lista de trabalho de M1 a M3. Se a rodada
passar de 1 hora, registre o `uptime` e siga.

### M1. `Shot` e `Blaster`

Para cada arquivo, nesta ordem:
1. **R5.** Para cada sobrevivente, um teste de comportamento que o mate, com o skill
   `tdd-behavior-autonomous-quiet`. O RED se observa como no lote 1: o teste nasce
   verde com o produto correto; aplique o mutante à mão, rode a suíte JVM, veja o
   teste nomeado falhar por asserção e restaure o arquivo. Registre o par mutante e
   teste.
2. **R4.** Com o skill `refactor-design`, refatore até
   `npm run lint:sensor -- <arquivo>` dar 0, uma refatoração por vez.
3. KofMut só nesse arquivo: 0 sobreviventes.

O `Shot` e o `Blaster` são usados pelo `Weapons.kf`, que não pode mudar. Observe-os
pelo que o jogo ou a API pública deles mostra.

### M2. `Ship`

O mesmo ciclo do M1. A função em `Ship.kf:46` tem os 4 achados de lint. Os
sobreviventes `boolean` das linhas 10 a 16 são valores iniciais de campos: confira
primeiro se algum método os reinicia (o caso `expanded` do piloto da UI) e aplique a
regra de equivalentes.

### M3. `SpecialBeam`

O mesmo ciclo do M1. É o arquivo com mais sobreviventes. Observação do
planejamento: `hitsMeteor`, `beginsSubchiefContact` e `beginsBossContact` repetem a
mesma regra, "alguma borda do alvo dentro da faixa vertical do raio, de `y` a
`y + 32`", com 2 ou 3 bordas. É a mesma situação do lote 1 com o `ShipContact`: uma
regra num lugar só pode tirar os equivalentes da união de intervalos. Decida isso no
R4, pelos testes, sem mudar o `ShipContact` além do que ele já garante.

### M4. Registros e validação final

- Uma seção nova "R5 e R4, lote 2" em `.agent/validation/sensor-debt-payoff.md`,
  com:
  - o M0;
  - sobreviventes antes e depois, por arquivo;
  - os pares mutante e teste;
  - as refatorações que tiraram equivalentes;
  - o tempo gasto, para estimar os lotes 3 (`Subchief`, `Boss`, `Weapons`) e 4
    (`Game`).
- Uma linha no `EXECPLAN.md` da raiz.
- Corrija o texto "sem commit" do item do lote 1, no `EXECPLAN.md` e no aceite. O
  lote 1 entrou pelo PR #28.

## Progress

- [x] M0. Linha de base do KofMut nos quatro arquivos (12/11, 10:10 a 10:45):
  `complete`, 244 candidatos, 142 mortos, 102 sobreviventes, 0 timeout; os mesmos
  ids do A1. Relatório em `.agent/tmp/debt-batch2/m0-report.json`.
- [x] M1. `Shot` e `Blaster`: R5 (testes em `PlayerFireJourney.kf`), RED de cada
  sobrevivente em `.agent/tmp/debt-batch2/red-m1.txt`; R4 com lint 0.
- [x] M2. `Ship`: R5 (`ShipMotionJourney.kf`), RED em `red-m2.txt`; R4 com lint 0.
- [x] M3. `SpecialBeam`: R5 (`SpecialBeamJourney.kf`), RED em `red-m3.txt`; R4
  com `reaches()` e lint 0. KofMut final nos quatro arquivos (A1): 164/164
  mortos, `complete`, 0 timeout.
- [x] M4. Registros: seção "R5 e R4, lote 2" no aceite, linha no `EXECPLAN.md`
  da raiz, "sem commit" do lote 1 corrigido para o PR #28. Validação final em
  `.agent/tmp/debt-batch2/final/`; resultado na seção "Fechamento do lote" do aceite.

## Validation

Critérios de aceite. A coluna "Verificação" é o planejado; registre o observado no
aceite.

| # | Contexto, ação e resultado esperado | Verificação |
| --- | --- | --- |
| A1 | KofMut nos quatro arquivos alterados, depois do M3: `candidates = killed`, 0 sobreviventes, 0 timeouts, `status` `complete` | comando do M0 com outro `--report-dir`; registrar os números |
| A2 | Cada teste novo mata um mutante nomeado: com o mutante aplicado à mão, o teste falha por asserção, e nenhum teste fora da lista falha | tabela mutante e teste no aceite |
| A3 | Nenhum equivalente fica anotado. Se sobrar um, ele tem prova e a entrega para antes do commit | seção de equivalentes do aceite |
| A4 | `npm run lint:sensor -- <os quatro arquivos>` dá `PASS (0 findings)`, e o mesmo vale para qualquer arquivo de teste novo ou alterado | rodar |
| A5 | Só arquivos permitidos mudam em `src/main`: `git diff --name-only main -- src/main` lista apenas os quatro arquivos do lote, `ShipContact.kf` ou arquivos novos | rodar |
| A6 | A contagem de casos sobe de 212, em JVM e JS, no 0.7.0 e no 0.6.4 | `node scripts/kof-tests.mjs --target jvm` e `--target js`, depois com `KOF=~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof` |
| A7 | O comportamento não muda: as sete jornadas passam, e as capturas ficam iguais às do R0 pixel a pixel | `npm run check:task` e a mesma comparação de pixels do lote 1 (seção "R5 e R4, lote 1" do aceite) |
| A8 | `npm run check` mostra `mutation  PASS`, com os quatro arquivos no escopo, e `CHECK: PASS` | validação final |

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
  está certa. Isso é separado de conferir se os testes a demonstram.
- Para cada critério de A1 a A8, registrar no aceite o comando, o resultado
  observado e onde está a evidência. Uma suíte verde sozinha não prova cada
  critério.
- Registrar antes da entrega qualquer critério não verificado, cobertura que faltou
  ou falha, sem apresentá-los como atendidos.
