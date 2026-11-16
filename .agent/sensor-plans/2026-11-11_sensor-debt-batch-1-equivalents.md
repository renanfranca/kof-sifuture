# Dívida dos sensores: tirar os 5 equivalentes do lote 1

Plano mestre: `2026-11-05_FEATURE_sifuture-sensor-debt-payoff.md`, nesta mesma pasta.
As regras invioláveis dele continuam valendo: sem supressão, sem pular mutante.

## Onde estamos (11/11)

- Branch `refactor/sensor-debt-batch-1`, commit `af4e886`, já no `origin`, sem PR.
- O lote 1 deixou 5 mutantes equivalentes, com prova no aceite
  `.agent/validation/sensor-debt-payoff.md`, seção "R5 e R4, lote 1".
- O `npm run check` reprova em `mutation` por 3 deles (`Meteor` 2, `BossShot` 1).
  Os 2 do `Credits` só não aparecem porque o arquivo não mudou.

## A regra nova para equivalentes

Um mutante equivalente quase sempre aponta código redundante: um operador que pode
mudar sem mudar o comportamento. Antes de anotar um equivalente, tente uma
refatoração que preserve o comportamento e tire o operador redundante. Só anote o
equivalente quando essa refatoração não existir, e então pare e mostre.

## O que fazer, na mesma branch

Cada item é uma refatoração, com os testes verdes antes e depois. Nenhum teste muda
de expectativa.

1. **`Credits.kf:19`**: `firstY + secondY` vale sempre 176, porque um sobe 1 e o
   outro desce 1 a cada passo. Então `secondY > -CREDITS_BLOCK_HEIGHT` equivale a
   `firstY < 248`, que já está contido em `firstY < CREDITS_HEIGHT` (260). Remova a
   cláusula `|| secondY > -Rules.CREDITS_BLOCK_HEIGHT`. Confira antes se algum teste
   ou outro arquivo depende de `secondY` além da tela.
2. **`Credits.kf:16`**: troque o `if (x > MARGIN) { x = MARGIN }` depois de
   `x = x + 5` por `x = min(x + 5, Rules.CREDITS_MARGIN)`, do `kof.math`. Confirme
   que `min` compila em JVM e JS, no 0.7.0 e no 0.6.4. Se não compilar em algum
   deles, pare e mostre.
3. **`Meteor.kf:88-92`**: o `touchesShip(Int shipX, Int shipY)` continua público,
   com a mesma assinatura, e passa a delegar para o `ShipContact`. Para isso, o
   `ShipContact` recebe `shipX` e `shipY` em vez de `Ship`, e os chamadores atuais
   (`BossShot`, `BossSpecial`, `SubchiefShot`, `Item`) passam `ship.x` e `ship.y`.
   Com altura 18, a união das duas bordas do meteoro é contínua, então o resultado
   é o mesmo. Os mutantes passam a existir só no `ShipContact`, onde os testes do
   tiro do chefe já os matam.
4. **`BossShot.kf:34`**: remova `&& animationSteps < 5`. O único leitor é
   `spriteFrame()`, que devolve 2 para qualquer valor a partir de 5, e o tiro se
   desativa e zera o contador ao sair da tela, então o valor é limitado. Confira o
   teste `BossJourney.kf:1021`, que espera o contador em 0 depois da limpeza.

## Pare e mostre

- KofMut nos arquivos de produção alterados, incluindo o `Credits`: 0
  sobreviventes. Liste os ids que deixaram de existir e os novos.
- `npm run lint:sensor` e `npm run dup:sensor`: 0 achados.
- `npm run check` e `npm run check:task`: PASS, com as sete jornadas e os mesmos
  pixels do R0.
- A contagem de casos em JVM e JS, no 0.7.0 e no 0.6.4, que não pode cair de 212.
- Se algum dos 4 itens não preservar o comportamento, pare nele e mostre o motivo.

Atualize o `EXECPLAN.md`, a cópia do plano e o aceite: troque a lista de
equivalentes pela refatoração que tirou cada um.
