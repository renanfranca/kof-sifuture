# Aceite: no exit 3, o relatório do KofMut precisa ser desta execução, e o SKIP mostra os descartes

Data: 10/11/2026 (America/Bahia). Branch `mutation-report-identity`, criada da `main` em `2956d0d` (PR #24). O commit que contém este registro é o commit testado; não houve mudança de código depois das execuções abaixo.

Ambiente: Linux x86_64 (WSL2), `kof 0.7.0`, Node.js do PATH, `kof-mut` instalado `KofMut 0.1.0`, imagem `0e89fbb3989e76d853f39d54f200a95341db0e49e9398e6ed3f5e5bf1f45d980` (o link instalado aponta para `releases/0e89fbb3…/launch.sh`, e o `image.json` dessa release traz `"id":"0e89fbb3…"` e `buildDependency.version` `0.7.0`).

## O que mudou

O procedimento do consumidor do KofMut pede:

> JSON-decode the remainder as a string; require an absolute path.
> …
> Compare runId to expectedRunId and scope to the normalized requested scope.

(`kof-mut/docs/report-format.md`, "Discover the current report")

e define `scope` como "Normalized, deduplicated, sorted production paths relative to project" (tabela "Top level fields"). O `check` já escolhia o `runId` e o escopo, mas não comparava nenhum dos dois.

Agora, só no exit 3, [`scripts/mutation-step.mjs`](../../scripts/mutation-step.mjs) confere nesta ordem:

1. relatório utilizável: uma linha `reportPath=`, caminho **absoluto**, arquivo, JSON, `status` string, `limitations` array de strings e `discardedCandidates` array;
2. identidade: `runId` igual ao `--run-id` que o `check` passou, depois `scope` igual ao escopo pedido deduplicado e ordenado;
3. o status, como no PR #24.

| Relatório no exit 3 | Linha do sumário |
| --- | --- |
| caminho relativo | `mutation  FAIL (KofMut exit 3 report unreadable: reportPath is not absolute; quality not approved)` |
| `discardedCandidates` ausente ou não array | `mutation  FAIL (KofMut exit 3 report unreadable: discardedCandidates is not an array; quality not approved)` |
| outro `runId` | `mutation  FAIL (KofMut exit 3 report is not from this run: runId <do relatório> instead of <pedido>; quality not approved)` |
| outro `scope` (inclusive `[]`) | `mutation  FAIL (KofMut exit 3 report is not from this run: scope <do relatório> instead of <pedido>; quality not approved)` |
| `no_mutants`, sem limitação, sem descarte | `mutation  SKIP (KofMut no_mutants: no applicable mutants)` (igual ao PR #24) |
| `no_mutants`, sem limitação, N > 0 descartes | `mutation  SKIP (KofMut no_mutants: no applicable mutants, N discarded)` |

Um descarte é uma troca que o compilador recusa, por exemplo `7 * 0` → `7 / 0` com `ARITH001`. Ela nem vira programa, então os testes não têm como detectá-la; por isso continua SKIP (opção b do plano), mas a contagem fica visível. Pelo contrato, "all discarded, with no other limitation, is `no_mutants/3`" (`report-format.md`, "Counts").

Exits 0, 1 e 2 não mudam.

## Evidência por critério

Testes em [`test/sensors/check.test.mjs`](../../test/sensors/check.test.mjs). O `kof-mut` falso (`withReportingKofMut`) virou um script Node que monta o relatório com o `--run-id` e o escopo do `--files` que **recebeu** (deduplicado e ordenado, como o KofMut) e `discardedCandidates: []`. `KOF_MUT_REPORT` sobrescreve campos (`runId`, `scope`, `discardedCandidates`, `status`, `limitations`), `KOF_MUT_OMIT` remove campos, e `KOF_MUT_ANNOUNCE` aceita `once`, `twice`, `missing`, `none` e `relative`. Os testes não copiam a lógica de produção: o valor certo vem do que o `check` entregou ao falso.

| Critério | Comando | Observado | Asserção |
| --- | --- | --- | --- |
| C1 relatório desta execução continua SKIP | `node --test test/sensors/check.test.mjs` | verde com o falso novo; `SKIP (KofMut no_mutants: no applicable mutants)`, `CHECK: PASS`, exit 0 | `KofMut no_mutants without limitations skips mutation without failing check` (linha 169), sem mudança no teste |
| C2 outro `runId` nunca vira SKIP | idem | verde; `FAIL (… not from this run: runId …)`, `CHECK: FAIL at mutation`, exit 1 | `a KofMut report from another run never skips mutation` (187) |
| C3 `scope` | idem | verde; (a) lista ordenada A, B → SKIP e exit 0; (b) só A → FAIL `scope`, exit 1; (c) `[]` → FAIL `scope`, exit 1 | `a KofMut report skips mutation only when its scope is the requested sorted scope` (195) |
| C4 caminho relativo | idem | verde; o teste confere que o caminho anunciado não é absoluto **e** que o arquivo existe nele; `FAIL (… unreadable: reportPath is not absolute …)`, exit 1 | `a relative reportPath fails mutation as unreadable even when the file exists there` (211) |
| C5 descartes no SKIP | idem | verde; 3 descartes → `SKIP (KofMut no_mutants: no applicable mutants, 3 discarded)`, `CHECK: PASS`, exit 0 | `KofMut no_mutants from discarded candidates still skips mutation and shows how many were discarded` (177) |
| C6 `discardedCandidates` ausente ou string | idem | verde nos dois casos novos; `FAIL (… unreadable: …)`, exit 1 | dois casos novos em `an unusable KofMut report on exit 3 fails mutation as unreadable, never as SKIP` (248) |
| C7 sem regressão do PR #24 | idem | `incomplete`, `no_scope`, contraditório, ilegível e exits 0 e 1 verdes, com as mesmas frases; os relatórios agora trazem a identidade certa pelo falso | testes das linhas 102, 221, 231, 238, 248 |
| C8 prova real | `npm run check` numa cópia, ver abaixo | (a) SKIP, `runId` igual; (b) SKIP com `1 discarded`; (c) PASS | relatórios reais abaixo |
| C9 documentação | `npm run docs:sensor` | `SENSOR docs: PASS (0 findings)` | [`SENSORS.md`](../../SENSORS.md), parágrafo do `check` |
| C10 não regressão | ver abaixo | tudo verde | ver abaixo |

### RED esperado e observado

| Ciclo | Esperado | Observado |
| --- | --- | --- |
| C2 | SKIP e exit 0 | `mutation SKIP (KofMut no_mutants: no applicable mutants)`, `CHECK: PASS` |
| C3 | (b) e (c) com SKIP | o caso (b) parou o teste com `mutation SKIP (KofMut no_mutants: no applicable mutants)`; (a) já dava SKIP, como esperado |
| C4 | arquivo lido e SKIP | anúncio `reportPath="../../../../tmp/sifuture-sensor-…/report.json"` e `mutation SKIP (KofMut no_mutants: no applicable mutants)` |
| C5 | frase sem `, 3 discarded` | `mutation SKIP (KofMut no_mutants: no applicable mutants)` |
| C6 | `discardedCandidates` ausente virando SKIP | o caso `discardedCandidates missing` parou o teste com `mutation SKIP (KofMut no_mutants: no applicable mutants)` |

Antes do C2, a troca do falso `#!/bin/sh` pelo script Node foi feita com a suíte verde (10/10), para que nenhum RED dependesse da troca.

### Ajuste em relação ao plano (C4)

O plano pedia o caminho relativo "à raiz do projeto", com o arquivo existindo "relativo à pasta em que o `check` roda". Nos testes essas pastas são diferentes: `runSensorWith` roda o `check` na raiz do repositório, e o projeto fica numa pasta temporária. Para manter a intenção (só a regra do caminho absoluto pode reprovar), o falso anuncia o caminho relativo a `KOF_MUT_RELATIVE_FROM`, que o teste fixa no cwd do `check`, e o teste confere `existsSync` nesse caminho antes de olhar o veredito.

### Mudanças de contrato

- Frases novas: `report unreadable: reportPath is not absolute`, `report unreadable: discardedCandidates is not an array`, `report is not from this run: runId …` e `… scope …`, e o sufixo `, N discarded` no SKIP.
- Um relatório no exit 3 sem `discardedCandidates` passou a ser FAIL. O contrato do KofMut marca o campo como obrigatório, e o KofMut real sempre o publica (ver C8).
- Nenhuma frase do PR #24 mudou; nenhum teste antigo foi alterado, além de dois casos novos no teste de C5 do PR #24 (C6) e da troca do falso.

### C8: KofMut real

Cópia do checkout da branch (arquivos rastreados e não ignorados, com as mudanças ainda não commitadas) em `/home/renanfranca/projects/sifuture-probe-0yLm`, commitada como `main`, com a branch `probe`. A cópia foi apagada no fim.

**(a)** Só `State.kf`: `enum MeteorMotion { Horizontal, Vertical, Diagonal }`.

```text
> kof-mut run … --run-id 0c84a0d5-5779-401d-ad0e-73b446b412ea
reportPath="/home/renanfranca/projects/sifuture-probe-0yLm/.agent/tmp/kof-mut-reports/d39d1904…/0c84a0d5-5779-401d-ad0e-73b446b412ea-8333122085195142161/report.json"
  mutation       SKIP (KofMut no_mutants: no applicable mutants)
CHECK: PASS
exit=0
```

Relatório real: `runId: "0c84a0d5-5779-401d-ad0e-73b446b412ea"` (igual ao do comando), `status: "no_mutants"`, `scope: ["src/main/kof/sifuture/game/State.kf"]`, `limitations: []`, `discardedCandidates: []`, 0 candidatos, baseline `passed`, `kofVersion: "0.7.0"`.

**(b)** `State.kf` restaurado e um arquivo novo `src/main/kof/sifuture/game/ProbeCalc.kf`:

```kof
package sifuture.game

class ProbeCalc {
    Int value() { return 7 * 0 }
}
```

O check do projeto deu exit 0 em JVM e JS antes. Para provar que ele cobre esse arquivo, `return "x"` temporário deu `SEM010 Return type mismatch: expected 'Int' but got 'String'` em `ProbeCalc.kf:4` e exit 1 nos dois alvos; o arquivo foi restaurado antes do `npm run check`.

```text
> kof-mut run … --run-id c15d0bd6-af57-4a9c-97d0-34e69cd08db8
  mutation       SKIP (KofMut no_mutants: no applicable mutants, 1 discarded)
CHECK: PASS
exit=0
```

Relatório real: `runId` igual ao do comando, `status: "no_mutants"`, `scope: ["src/main/kof/sifuture/game/ProbeCalc.kf"]`, `limitations: []`, 0 candidatos, baseline `passed`, e um descarte:

```json
{
  "id": "src/main/kof/sifuture/game/ProbeCalc.kf:68:/",
  "operator": "arithmetic",
  "original": "*",
  "replacement": "/",
  "location": {"line": 4, "column": 28, "offset": 68, "length": 1},
  "phase": "check",
  "evidence": "ARITH001: division by zero: constant / by zero is not allowed; stdout: …/0-check.stdout; stderr: …/0-check.stderr; process group cleanup confirmed"
}
```

O KofMut não gerou outro candidato para essa expressão, então não foi preciso procurar outra.

**(c)** `ProbeCalc.kf` removido; só `Background.kf` com uma linha em branco a mais no fim.

```text
> kof-mut run … --run-id be0429d2-0131-4976-9973-67fdd726c8de
  mutation       PASS
CHECK: PASS
exit=0
```

Relatório real: `status: "complete"`, `scope: ["src/main/kof/sifuture/game/Background.kf"]`, 1 candidato, 1 morto, 0 descartes. O exit 0 continua decidido só pelo exit code.

### C10: não regressão

- `node --test test/sensors/*.test.mjs`: 36 testes, 36 verdes, 0 falhas (eram 32; mais os 4 testes novos de C2, C3, C4 e C5).
- `scripts/kof-sensors/test`: `Tests run: 42, Failures: 0, Errors: 0, Skipped: 0`, exit 0. `git diff main -- scripts/kof-sensors` vazio.
- `git diff --check`: exit 0.
- `npm run check` na branch: `CHECK: PASS`, exit 0, com `mutation SKIP (no production Kof file changed against main)`. A branch não altera `.kf`; o caminho novo do exit 3 foi provado no C8.

## Lacunas

- No exit 0 (PASS), o `check` ainda não confere o relatório (identidade, status). É melhoria separada.
- Fora deste plano: reconciliar contagens, IDs e `baseline`; conferir `schemaVersion == 1`; conferir se o caminho anunciado fica dentro de `--report-dir`.
- `scope` com tipo errado (por exemplo, string) cai em "not from this run", e não em "unreadable", porque a comparação é feita sobre o JSON serializado. O efeito (FAIL) é o mesmo.
- O C3(a) aceita a lista ordenada, mas o escopo que o `check` pede já sai ordenado e sem repetição do Git. Por isso a deduplicação e a ordenação do lado do `check` não foram exercitadas com uma entrada fora de ordem.

Evidência local opcional (fora do Git): `.agent/tmp/report-identity/` com `red-c2.log` a `red-c6.log`, `c8a.log`, `c8b.log`, `c8c.log`, os três relatórios copiados, os checks de `ProbeCalc.kf`, `sensors-tests.log`, `meter.log` e `check-branch.log`.
