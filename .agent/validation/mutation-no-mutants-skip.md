# Aceite: `no_mutants` do KofMut vira SKIP no `check`

Data: 10/11/2026 (America/Bahia). Branch `mutation-no-mutants-skip`, criada da `main` em `d790bbd`. O commit que contém este registro é o commit testado; não houve mudança de código depois das execuções abaixo.

Ambiente: Linux x86_64 (WSL2), `kof 0.7.0`, Node.js do PATH, `kof-mut` instalado `KofMut 0.1.0`, imagem `0e89fbb3989e76d853f39d54f200a95341db0e49e9398e6ed3f5e5bf1f45d980` (lida em `image.json` da release, porque `kof-mut --version` não mostra o hash). Essa imagem já traz o suporte a `enum` (renanfranca/kof-mut#3).

## O que mudou

O passo `mutation` do `check` decidia só pelo exit code. O exit 3 do KofMut junta três status:

> | `incomplete` | `3` | Budget expiry, inconclusive mutant or unsupported scope/other limitation |
> | `no_scope` | `3` | Explicit empty scope; no baseline commands or quality approval |
> | `no_mutants` | `3` | No applicable mutants, including all candidates discarded; no quality approval |

(`kof-mut/docs/report-format.md`, tabela "Overall status and process exit")

Agora, só no exit 3, [`scripts/mutation-step.mjs`](../../scripts/mutation-step.mjs) lê o relatório anunciado na única linha `reportPath=` do stdout, decodifica o caminho com `JSON.parse` e decide:

| Relatório no exit 3 | Linha do sumário |
| --- | --- |
| `no_mutants`, `limitations: []` | `mutation  SKIP (KofMut no_mutants: no applicable mutants)` |
| `incomplete` ou `no_scope` | `mutation  FAIL (KofMut <status>[: <limitações>]; quality not approved)` |
| `no_mutants` com limitações, ou status fora dos três | `mutation  FAIL (KofMut exit 3 contradicts report: …; quality not approved)` |
| sem linha, duas linhas, arquivo ausente, JSON inválido, `status`/`limitations` com forma errada | `mutation  FAIL (KofMut exit 3 report unreadable: …; quality not approved)` |

Exits 0, 1 e 2 não mudam. SKIP não aprova a qualidade: diz que nada foi avaliado, como o SKIP sem arquivo de produção alterado.

## Evidência por critério

Testes em [`test/sensors/check.test.mjs`](../../test/sensors/check.test.mjs). O `kof-mut` falso (`withReportingKofMut`) grava `KOF_MUT_REPORT` em `<report-dir>/run/report.json`, anuncia a linha conforme `KOF_MUT_ANNOUNCE` (`once`, `twice`, `missing`, `none`) e sai com `KOF_MUT_EXIT`.

| Critério | Comando | Observado | Asserção |
| --- | --- | --- | --- |
| C1 `no_mutants` sem limitação → SKIP, `check` passa | `node --test test/sensors/check.test.mjs` | verde; estado, frase, `CHECK: PASS` e exit 0 conferidos | teste `KofMut no_mutants without limitations skips mutation without failing check` |
| C2 `incomplete` → FAIL com motivo | idem | verde; `FAIL (KofMut incomplete: src/main/kof/Game.kf: Unsupported AST node: X; quality not approved)`, exit 1 | `KofMut incomplete still fails check and shows its limitation` |
| C3 `no_scope` → FAIL | idem | verde; `FAIL (KofMut no_scope; quality not approved)`, exit 1 | `KofMut no_scope still fails check even without limitations` |
| C4 relatório contraditório nunca vira SKIP | idem | verde nos dois casos (`no_mutants` com limitação; `complete`), exit 1 | `a KofMut report that contradicts exit 3 never skips mutation` |
| C5 sem relatório utilizável → FAIL | idem | verde nos cinco casos, exit 1, detalhe `report unreadable` | `an unusable KofMut report on exit 3 fails mutation as unreadable, never as SKIP` |
| C6 exits 0, 1 e 2 sem mudança | idem | asserções de exit 1 (`at least one mutant survived`) e exit 0 (`PASS`) intactas e verdes | `mutation runs on changed production Kof files and its verdict decides check` |
| C7 prova real | `npm run check` numa cópia, ver abaixo | (a) SKIP/PASS, (b) FAIL `incomplete`, (c) PASS | relatórios reais abaixo |
| C8 documentação | `npm run docs:sensor` | `SENSOR docs: PASS (0 findings)` | [`SENSORS.md`](../../SENSORS.md), parágrafo do `check` |
| C9 não regressão | ver abaixo | tudo verde | ver abaixo |

### RED esperado e observado

| Ciclo | Esperado | Observado |
| --- | --- | --- |
| C1 | `mutation FAIL (KofMut exit 3: incomplete, no_scope or no_mutants; quality not approved)`, `CHECK: FAIL at mutation` | exatamente isso, na primeira asserção (a do SKIP) |
| C2 | FAIL sem o status nem a limitação no detalhe | `FAIL (KofMut exit 3: incomplete, no_scope or no_mutants; quality not approved)` |
| C3 | sem RED: o GREEN do C2 já tratava `no_scope` como FAIL | verde na primeira execução. Para provar que o teste distingue, troquei temporariamente a condição do SKIP por "`limitations` vazia": o teste do C3 ficou vermelho e os outros, verdes; código restaurado e 8/8 verdes |
| C4 | `no_mutants` com limitação virando SKIP | `mutation SKIP (KofMut no_mutants: no applicable mutants)`, o caso perigoso |
| C5 | `check` quebrando sem sumário | `TypeError: Cannot read properties of undefined (reading 'slice')` no stderr; stdout sem linha `mutation` |

### Mudança de contrato (C6)

O teste `mutation runs on changed production Kof files and its verdict decides check` perdeu só a parte do exit 3, que esperava `FAIL (KofMut exit 3: incomplete, no_scope or no_mutants; quality not approved)` com um falso que não anuncia relatório. Essa frase deixou de existir de propósito: o exit 3 agora depende do relatório. O mesmo cenário (exit 3 sem `reportPath=`) é coberto pelo C5 e continua FAIL, agora com `report unreadable: expected one reportPath= line, found 0`. As asserções de exit 0 e exit 1 não mudaram.

### C7: KofMut real

Cópia do checkout da branch (arquivos rastreados e não ignorados) em `/home/renanfranca/projects/sifuture-probe-245O`, commitada como `main`, com a branch `probe`. Desvio do plano: a primeira cópia ficou em `/tmp`, e o `docs:sensor` reprovou com 41 `broken-link`, porque registros como `.agent/validation/kof-0.6.9-js-ui-heading-regression.md` apontam para `../../../kof/…`, que só resolve ao lado de `~/projects/kof`. A cópia foi movida para `~/projects`, que também não tem pastas com ponto (KofLang/Kof4j#999). A cópia foi apagada no fim.

**(a)** Só `State.kf`: `enum MeteorMotion { Horizontal, Vertical, Diagonal }`. Nenhum `switch`/`when` usa os enums. Check do projeto em JVM e JS com exit 0 antes de rodar.

```text
  mutation       SKIP (KofMut no_mutants: no applicable mutants)
CHECK: PASS
exit=0
```

Relatório real: `reportPath=".../.agent/tmp/kof-mut-reports/2eab388a…/35192474-201f-410e-9789-314be040c1b3-15284132969751780803/report.json"`, `status: "no_mutants"`, `limitations: []`, `scope: ["src/main/kof/sifuture/game/State.kf"]`, baseline `passed`, 0 candidatos, 0 descartes, `kofVersion: "0.7.0"`.

**(b)** Mais um arquivo de produção `src/main/kof/sifuture/game/ProbePoint.kf` com `record ProbePoint(Int x, Int y)` e outra constante em `State.kf` (`Direction … Still`). O `kof check` avulso do arquivo não serve (`PKG004`: o pacote é resolvido pela raiz do projeto). Por isso usei o check do projeto, com exit 0 em JVM e JS. Para provar que ele cobre esse arquivo, um erro de tipo temporário no mesmo arquivo deu `SEM010 Return type mismatch` em `ProbePoint.kf:6` e exit 1; o arquivo foi restaurado antes do commit.

```text
  mutation       FAIL (KofMut incomplete: src/main/kof/sifuture/game/ProbePoint.kf: Unsupported AST node: dev.kof.compiler.RecordDeclarationNode; quality not approved)
CHECK: FAIL at mutation
exit=1
```

Relatório real: `status: "incomplete"`, `limitations: ["src/main/kof/sifuture/game/ProbePoint.kf: Unsupported AST node: dev.kof.compiler.RecordDeclarationNode"]`, `scope` com `ProbePoint.kf` e `State.kf`, 0 candidatos.

**(c)** `probe` voltou para a `main` da cópia; só `Background.kf` com uma linha em branco a mais no fim.

```text
  mutation       PASS
CHECK: PASS
exit=0
```

Relatório real: `status: "complete"`, `limitations: []`, `scope: ["src/main/kof/sifuture/game/Background.kf"]`, 1 candidato, 1 executado, 1 morto, 0 sobreviventes.

### C9: não regressão

- `node --test test/sensors/*.test.mjs`: 32 testes, 32 verdes, 0 falhas.
- `scripts/kof-sensors/test`: `Tests run: 42, Failures: 0, Errors: 0, Skipped: 0`, exit 0. `git diff main -- scripts/kof-sensors` vazio.
- `git diff --check`: exit 0.
- `npm run check` na branch: `CHECK: PASS`, exit 0, com `mutation SKIP (no production Kof file changed against main)`. É o SKIP antigo, porque a branch não altera `.kf`; o caminho novo do exit 3 foi provado no C7.

## Lacunas

- O consumidor não confere `runId` e `scope` do relatório contra a execução, nem exige caminho absoluto, como recomenda o procedimento de `report-format.md`. Fica fora deste plano, junto com validar o JSON nos exits 0, 1 e 2.
- O C5 tem um quinto caso além dos quatro do plano: JSON válido sem `limitations` como array. Sem ele, o `check` quebraria com `TypeError` em vez de dar FAIL.
- `no_mutants` também cobre "todos os candidatos descartados" (por exemplo, `ARITH001`). Esse caso vira SKIP, como manda a decisão do plano; ele não foi provado com o KofMut real.
- O RED do C3 não existiu na ordem dos ciclos; o poder de distinção foi mostrado pela mutação manual descrita acima.

Evidência local opcional (fora do Git): `.agent/tmp/no-mutants-skip/` com `c7a.log`, `c7b.log`, `c7c.log`, os três relatórios copiados, `meter.log` e `check-branch.log`.
