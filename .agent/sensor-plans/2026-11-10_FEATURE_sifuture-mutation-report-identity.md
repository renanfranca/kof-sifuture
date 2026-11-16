# `check`: no exit 3, conferir que o relatório do KofMut é desta execução e mostrar descartes no SKIP

> **Para a sessão executora:** plano autorizado pelo usuário em 10/11/2026. Trabalhar em `/home/renanfranca/projects/kof-sifuture`, sem worktree e sem subagentes. **Commit, push, PR e merge estão autorizados**, nesta ordem e só com estes comandos, pelo Bash: `lc` (commit pelo Luna), `lp` (push) e `luna "…"` (PR, CI, merge e restaurar a `main`). Nada de `git commit` ou `git push` diretos.
>
> Antes de começar:
> - copiar este plano para `/home/renanfranca/.agents/skills/_temporary/codex-skills-ai-context/2026-11-10_FEATURE_sifuture-mutation-report-identity.md`;
> - ler o `AGENTS.md` do SiFuture e o training index do Kof;
> - **anotar a branch atual** para voltar a ela no fim;
> - exigir `git status --porcelain` **vazio**. Se houver qualquer mudança, **parar e avisar**: outra sessão pode estar trabalhando neste checkout;
> - `git switch main && git pull --ff-only`; conferir que a `main` contém `2956d0d` (PR #24); conferir `kof version` = `kof 0.7.0` e a imagem do `kof-mut` `0e89fbb3…` (em `image.json` da release, como no registro anterior);
> - criar a branch `mutation-report-identity` com o skill `create-git-branch`;
> - invocar o skill `tdd-behavior-autonomous-quiet` pelo Skill tool. Sem comentários no código nem `[TEST]`.

## Context

O PR #24 fez o `check` ler o relatório do KofMut no exit 3: `no_mutants` sem limitação vira SKIP ([`scripts/mutation-step.mjs`](scripts/mutation-step.mjs), registro [`.agent/validation/mutation-no-mutants-skip.md`](.agent/validation/mutation-no-mutants-skip.md)). Na revisão ficaram dois pontos, decididos pelo usuário em 10/11/2026:

1. **Conferir a identidade do relatório (decisão: fazer).** O procedimento do consumidor em `kof-mut/docs/report-format.md:20-30` exige:
   > JSON-decode the remainder as a string; require an absolute path.
   > …
   > Compare runId to expectedRunId and scope to the normalized requested scope.

   e `report-format.md:108` define `scope` como "Normalized, deduplicated, sorted production paths relative to project". O `check` já escolhe o `runId` (`randomUUID()` em `mutate`) e o escopo (`scope` vindo de `scripts/check.mjs:40`), mas não compara nenhum dos dois, nem exige caminho absoluto. Hoje essa é a lacuna 1 do registro anterior.
2. **Descartes no SKIP (decisão: opção b, manter SKIP e mostrar a contagem).** Pelo contrato (`report-format.md:187`), "all discarded, with no other limitation, is `no_mutants/3`". Um candidato descartado é uma troca que o compilador recusa, por exemplo `7 * 0` → `7 / 0` com `ARITH001` (`kof-mut/docs/operators.md:21-27`). Como ele nem vira programa, os testes não têm como detectá-lo, e por isso o SKIP continua. Mas a linha passa a mostrar quantos foram descartados, para que um SKIP vindo de descartes fique visível.

## Decisões

- **Só o exit 3 muda.** Os exits 0, 1 e 2 continuam decidindo só pelo exit code. Conferir o relatório também no PASS do exit 0 é melhoria separada, fora deste plano; registrar como lacuna.
- **Ordem de checagem no exit 3:**
  1. relatório utilizável: a linha `reportPath=`, o caminho absoluto, o arquivo, o JSON e as formas de `status`, `limitations` e `discardedCandidates`;
  2. identidade: `runId` e depois `scope`;
  3. o status, como no PR #24.

  Assim, um relatório de outra execução nunca vira SKIP, nem mostra um status que não é desta execução.
- **Escopo esperado:** o escopo pedido, deduplicado e ordenado, comparado como lista com o `scope` do relatório. Um relatório de escopo vazio também é FAIL, porque o pedido nunca é vazio: o `check` dá SKIP antes, quando não há arquivo de produção alterado (`report-format.md:30-31`: "treat it as an error").
- **Texto do SKIP:**
  - sem descarte, continua `KofMut no_mutants: no applicable mutants`, igual ao PR #24;
  - com N > 0 descartes, vira `KofMut no_mutants: no applicable mutants, N discarded`.

  N é o tamanho de `discardedCandidates` (`report-format.md:112`).
- **Fora do escopo:** reconciliar contagens, IDs e `baseline` (`report-format.md:29`); conferir `schemaVersion`; conferir se o caminho fica dentro de `--report-dir`. Registrar como lacunas.

## Critérios de aceitação

Isto é o **planejado**, e não o observado.

**Ponto de observação:** o mesmo do PR #24, a linha `  mutation  <ESTADO> (<detalhe>)` do sumário, a linha `CHECK: …` e o exit code de `check.mjs`.

**Testes:** no padrão de [`test/sensors/check.test.mjs`](test/sensors/check.test.mjs). O `kof-mut` falso (`withReportingKofMut`) precisa passar a montar o relatório com o `--run-id` e o escopo do `--files` que **recebeu**, para que os testes não dependam de um valor copiado da lógica de produção. Os testes também precisam poder sobrescrever:
- `runId`;
- `scope`;
- `discardedCandidates`;
- caminho relativo na linha `reportPath=`.

Hoje o falso é `#!/bin/sh`; trocar por um script Node é aceitável.

**C1. O relatório desta execução continua dando SKIP, agora com a identidade conferida.**
- **Exemplo:** `Game.kf` alterado, exit 3 e relatório com `no_mutants`, `limitations: []`, `discardedCandidates: []`, `runId` igual ao recebido e `scope: ["src/main/kof/Game.kf"]`.
- **Esperado:** `mutation  SKIP (KofMut no_mutants: no applicable mutants)`, `CHECK: PASS` e exit 0.
- **Reuso:** o teste `KofMut no_mutants without limitations skips mutation without failing check` continua passando, com o falso novo.
- **Por que distingue:** garante que a checagem nova não reprova o caso bom. Uma comparação errada de `runId`, como comparar com outro UUID, faria este teste falhar.

**C2. `runId` diferente nunca vira SKIP.**
- **Exemplo:** mesmo cenário do C1, mas o relatório traz outro UUID válido no `runId`.
- **Esperado:** `mutation  FAIL (KofMut exit 3 report is not from this run: runId …; quality not approved)`, `CHECK: FAIL at mutation` e exit 1.
- **RED esperado:** hoje dá SKIP e exit 0.
- **Por que distingue:** o relatório é `no_mutants` perfeito. Só a identidade pode reprovar.

**C3. `scope` diferente nunca vira SKIP.** Dois arquivos de produção alterados, `src/main/kof/A.kf` e `src/main/kof/B.kf`, e exit 3 `no_mutants`. Cada caso abaixo é medido pela linha `mutation` e pelo exit code:
- (a) o relatório traz `scope: ["src/main/kof/A.kf", "src/main/kof/B.kf"]`, a lista ordenada. **Esperado:** SKIP e exit 0. Esta é a fronteira que prova que a comparação aceita o escopo normalizado.
- (b) o relatório traz `scope: ["src/main/kof/A.kf"]`, faltando um arquivo. **Esperado:** `FAIL (KofMut exit 3 report is not from this run: scope …; quality not approved)` e exit 1.
- (c) o relatório traz `scope: []`. **Esperado:** FAIL "not from this run: scope" e exit 1.
- **RED esperado:** (b) e (c) dão SKIP hoje.
- **Por que distingue:** (a) impede uma comparação rígida que reprovasse o caso certo, e (b) e (c) impedem aceitar qualquer escopo.

**C4. Caminho relativo na linha `reportPath=` é FAIL.**
- **Exemplo:** o falso anuncia `reportPath="<caminho relativo à raiz do projeto>/report.json"`. O arquivo **existe** nesse caminho relativo à pasta em que o `check` roda, de modo que só a regra do caminho absoluto pode reprovar.
- **Esperado:** `FAIL (KofMut exit 3 report unreadable: reportPath is not absolute; quality not approved)` e exit 1.
- **RED esperado:** hoje o arquivo é lido e dá SKIP.

**C5. Descartes aparecem no SKIP.**
- **Exemplo:** exit 3 `no_mutants`, `limitations: []`, identidade certa e `discardedCandidates` com 3 itens (o falso pode usar objetos mínimos).
- **Esperado:** `mutation  SKIP (KofMut no_mutants: no applicable mutants, 3 discarded)`, `CHECK: PASS` e exit 0.
- **RED esperado:** a frase sem `, 3 discarded`.
- **Por que distingue:** a frase exata separa "mostra a contagem" de "ignora os descartes". O exit 0 separa a opção b da opção c, que reprovaria.

**C6. `discardedCandidates` ausente ou com forma errada é relatório ilegível.** Exit 3 `no_mutants` sem `discardedCandidates`, ou com ele como string, dá `FAIL (KofMut exit 3 report unreadable: …)` e exit 1, nunca SKIP. O contrato marca o campo como obrigatório (`report-format.md:112`). Entra no teste de C5 do PR #24 (`an unusable KofMut report on exit 3 fails mutation as unreadable, never as SKIP`) como mais um caso.

**C7. Não regride o que o PR #24 garantiu.** Os testes de `incomplete`, `no_scope`, relatório contraditório, relatório ilegível e exits 0 e 1 continuam verdes, com as mesmas frases. Os relatórios desses testes agora carregam a identidade certa, para que continuem testando o status, e não a identidade. Qualquer frase que mudar precisa ser registrada como mudança de contrato.

**C8. Prova real com o KofMut instalado**, como no PR #24: cópia rastreada do checkout em `~/projects/sifuture-probe-*`, porque em `/tmp` os links do `docs:sensor` quebram. A cópia é commitada como `main`, com uma branch `probe`, e apagada no fim.
- **(a)** Só `State.kf` alterado. **Esperado:** `mutation SKIP (KofMut no_mutants: no applicable mutants)` e `CHECK: PASS`. Registrar o `runId` impresso no `> kof-mut … --run-id <uuid>` e o do relatório, que precisam ser iguais.
- **(b)** Um arquivo novo `src/main/kof/sifuture/game/ProbeCalc.kf`, com `package sifuture.game` e uma classe com método `Int value() { return 7 * 0 }`, como em `kof-mut/fixtures/invalid/src/math/Calc.kf`. O check do projeto precisa dar exit 0 em JVM e JS antes. **Esperado:** `mutation SKIP (KofMut no_mutants: no applicable mutants, 1 discarded)` e `CHECK: PASS`.
  - Registrar o `discardedCandidates` real, com operador e evidência `ARITH001`.
  - Se o KofMut gerar candidatos que não são descartados, por exemplo de literais, e o status não for `no_mutants`, registrar o que saiu. Depois procurar outra expressão em que todo candidato seja descartado. Se não achar, registrar a lacuna e cobrir o C5 só pelo teste.
- **(c)** Repetir o caso `Background.kf`: `mutation PASS`, para mostrar que o exit 0 não mudou.

**C9. Documentação.** Atualizar o parágrafo do `check` em `SENSORS.md` (linhas 38-42), dizendo:
- que no exit 3 o relatório só vale se for desta execução (caminho absoluto, `runId` e `scope`);
- que o SKIP mostra a contagem de descartes.

Depois, `npm run docs:sensor` com PASS.

**C10. Não regressão.**
- `node --test test/sensors/*.test.mjs` todo verde, com contagem registrada (era 32);
- `scripts/kof-sensors/test` 42/0, sem mudança no medidor;
- `git diff --check` com exit 0;
- `npm run check` na branch com PASS.

## Entrega (autorizada)

1. Registrar a evidência em `.agent/validation/mutation-report-identity.md` (novo), com:
   - para cada critério de C1 a C10: comando, resultado observado e onde está a asserção;
   - o RED esperado e o observado;
   - as mudanças de contrato;
   - as lacunas.

   No registro anterior, `.agent/validation/mutation-no-mutants-skip.md`, acrescentar à lacuna 1 uma frase dizendo que, no exit 3, ela foi fechada pelo registro novo (com link). Acrescentar uma linha no `EXECPLAN.md`, em seção datada.
2. Rodar `lc`. Conferir com `git log -1 --stat` que o commit tem só os arquivos deste plano.
3. Rodar `lp`.
4. Rodar `luna "abra um PR de mutation-report-identity para main em renanfranca/kof-sifuture com um resumo em pt-BR, espere a CI passar, faça o merge, atualize a main local com fast-forward e apague a branch local e remota mergeada"`. Se a CI falhar, o Luna **não** faz merge: parar e avisar.
5. Conferir:
   - `git log origin/main -1` contém o merge;
   - `main` local = `origin/main`;
   - a branch apagada local e remotamente;
   - o run da CI da `main` com sucesso (`gh run list --branch main -L 1`).
6. Voltar para a branch anotada no início e confirmar o checkout limpo. Se ela não for a `main`, avisar que ela ainda não tem a mudança.

## Obrigações do executor

- Reconferir cada expectativa contra as fontes citadas (`report-format.md`, `operators.md`, `SENSORS.md` e este plano), **separado** de conferir se o teste a demonstra.
- Uma suíte verde não prova cada critério sozinha. Registrar a evidência de cada um.
- Uma lacuna aberta ou uma verificação que falhou não pode ser apresentada como critério satisfeito. Registrar antes de entregar e avisar no relatório final.
