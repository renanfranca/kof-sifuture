# Dívida dos sensores: R5 e R4, lote 1 (arquivos pequenos)

Plano mestre: `2026-11-05_FEATURE_sifuture-sensor-debt-payoff.md`, nesta mesma pasta.
As regras invioláveis e os pontos de parada dele continuam valendo.

## Onde estamos (11/11)

- O R0 ao R3 e o A1 estão na `main`, pelo PR #23 (`d790bbd`).
- A `main` está em `2c2e532`. Depois do PR #23 entraram:
  - PRs #24 e #25: quando o KofMut sai com exit 3, o passo de mutação do `check` lê
    o relatório. `no_mutants` sem limitações vira SKIP, com conferência de `runId`,
    escopo e caminho absoluto.
  - PR #26: piloto da UI. O `ControlsGuide` passou a delegar para a classe nova
    `GuideDisclosure`; os 6 sobreviventes dele morreram. Os casos foram para 181.
  - PR #27: o `check` ganhou o passo `types:fixtures`. Ele checa cada
    `tests/*.kf` como entrada no alvo JS e pega um `import` faltando que a entrada
    `import sifuture.*` esconde. Se você criar uma classe nova em `src/main/kof` no
    R4, importe-a explicitamente nos arquivos que a usam.
- As suítes estão sem dívida, com 181 casos.
- Falta pagar a dívida da produção:
  - 64 achados de lint e 3 grupos de CPD;
  - 483 sobreviventes do KofMut. Destes, 193 são de UI (`GameControls` 118,
    `GameView` 75) e ficam fora deste lote;
  - nas fixtures `tests/*.kf`, 14 achados.
- Sobreviventes por arquivo fora da UI, no A1
  (`.agent/tmp/debt-a1/kofmut-a1-report.json`):
  - `BossWeapons` 1, `Credits` 2, `Meteor` 4, `SubchiefShot` 11, `Item` 12,
    `BossSpecial` 12, `BossShot` 14;
  - `Ship` 16, `Shot` 17, `Blaster` 17, `Subchief` 18, `Boss` 30, `Weapons` 42,
    `Game` 42, `SpecialBeam` 52.

## O que fazer agora: só o lote 1

Crie uma branch nova a partir da `main` atualizada com o skill `create-git-branch`.
Não faça commit nem push.

Arquivos do lote 1, nesta ordem: `BossWeapons`, `Credits`, `Meteor`, `SubchiefShot`,
`Item`, `BossSpecial`, `BossShot`. Juntos, eles têm 56 sobreviventes.

Para cada arquivo:
1. **R5 primeiro.** Para cada sobrevivente, escreva um teste de comportamento que o
   mate, com o RED esperado anotado antes. Use o skill `tdd-behavior-autonomous-quiet`.
   Os testes novos vão para arquivos novos por assunto em `src/test/kof/sifuture/game/`.
   Não aumente `BossJourney.kf` (960 linhas) nem `SubchiefJourney.kf` (883).
2. **Mutante equivalente** (nenhum teste de comportamento consegue matar): não
   suprima e não pule. Anote a prova e siga para o próximo. Liste todos no fim
   (ponto de parada 2).
3. **R4 depois.** Refatore até `npm run lint:sensor -- <arquivo>` dar 0, uma
   refatoração por vez, com os testes verdes. Use o skill `refactor-design`. O CPD
   `BossShot.kf:25` ↔ `SubchiefShot.kf:14` entra aqui.
4. **KofMut só nesse arquivo.** Ele precisa sair sem sobreviventes, exceto os
   equivalentes anotados.

## Pare ao fim do lote 1 e mostre

- Por arquivo: os sobreviventes antes e depois, os testes novos e os equivalentes
  com a prova.
- O tempo gasto, para estimar os lotes seguintes (`Ship` ao `SpecialBeam`, 232
  sobreviventes).
- A contagem de casos em JVM e JS no 0.7.0 e no 0.6.4, que só pode subir.
- `git diff --stat` de `src/main`. Comportamento do jogo igual: rode as sete jornadas
  ao fim.

Atualize o `EXECPLAN.md`, a cópia do plano e o aceite
`.agent/validation/sensor-debt-payoff.md`.
