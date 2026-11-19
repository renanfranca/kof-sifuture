# `check`: KofMut `no_mutants` vira SKIP; `incomplete` e `no_scope` continuam FAIL

> **Para a sessão executora:** plano autorizado pelo usuário em 10/11/2026. Trabalhar em `/home/renanfranca/projects/kof-sifuture`, sem worktree e sem subagentes. **Desta vez commit, push, PR e merge estão autorizados**, nesta ordem e só com estes comandos, pelo Bash: `lc` (commit pelo Luna), `lp` (push) e `luna "…"` (PR, CI, merge e restaurar a `main`). Nada de `git commit` ou `git push` diretos.
>
> Antes de começar:
> - copiar este plano para `/home/renanfranca/.agents/skills/_temporary/codex-skills-ai-context/2026-11-10_FEATURE_sifuture-mutation-no-mutants-skip.md`;
> - ler o `AGENTS.md` do SiFuture e o training index do Kof;
> - **anotar a branch atual** (provavelmente `sensor-debt-payoff`) para voltar a ela no fim;
> - exigir `git status --porcelain` **vazio**. Se houver qualquer mudança, **parar e avisar**: outra sessão (a da dívida) trabalha neste checkout, e trocar de branch por cima do trabalho dela é proibido;
> - `git switch main && git pull --ff-only`; conferir `kof version` = `kof 0.7.0` e `kof-mut --version` com a imagem `0e89fbb3…` (que já tem o suporte a `enum`);
> - criar a branch `mutation-no-mutants-skip` com o skill `create-git-branch`;
> - invocar o skill `tdd-behavior-autonomous-quiet` pelo Skill tool. Sem comentários no código nem `[TEST]`.

## Context

O passo de mutação do `npm run check` decide só pelo exit code ([`scripts/mutation-step.mjs:7-12`](../../scripts/mutation-step.mjs)):

```js
3: { state: 'FAIL', detail: 'KofMut exit 3: incomplete, no_scope or no_mutants; quality not approved' },
```

No KofMut, o exit 3 junta três status diferentes (`/home/renanfranca/projects/kof-mut/docs/report-format.md:205-207`):

> | `incomplete` | `3` | Budget expiry, inconclusive mutant or unsupported scope/other limitation |
> | `no_scope` | `3` | Explicit empty scope; no baseline commands or quality approval |
> | `no_mutants` | `3` | No applicable mutants, including all candidates discarded; no quality approval |

Depois do suporte a `enum` no KofMut (PR renanfranca/kof-mut#3), um arquivo só com `enum`, como `src/main/kof/sifuture/game/State.kf`, dá `no_mutants`. Assim, uma mudança que toque **só** esse arquivo reprova o `check` sem nenhum jeito de passar. A correção lê o relatório JSON da execução, que é anunciado na linha `reportPath=` do stdout, e decide pelo `status` e pelas `limitations`.

## Decisões

- `no_mutants` com `limitations: []` e exit 3 → **SKIP**. SKIP não é aprovação: o sumário diz que nada foi avaliado, como já acontece quando não há arquivo alterado (`SENSORS.md`: "prints SKIP and claims nothing").
- `incomplete` e `no_scope` → **FAIL**, como hoje. Continua valendo a regra do M2: um sensor que não conseguiu rodar não passou.
- **Escopo restrito:** só o exit 3 passa a ler o relatório. Os exits 0, 1 e 2 mantêm o comportamento atual. Validar o JSON também nesses casos é uma melhoria separada, fora deste plano.

## Contrato do relatório (fonte: `kof-mut/docs/report-format.md`)

- O stdout tem **exatamente uma** linha começando por `reportPath=`. O resto da linha é uma string JSON, que precisa ser decodificada com `JSON.parse` (linhas 12-24). Não é permitido procurar o relatório "mais recente" (`docs/cli.md:78`).
- O JSON final e o exit code precisam concordar (`report-format.md:211`).
- `limitations` é um array de strings, vazio quando não há limitação (linha 113).

## Critérios de aceitação

Isto é o **planejado**, e não o observado. Observação pública: o sumário do `check`, que imprime `  mutation  <ESTADO> (<detalhe>)` mais `CHECK: PASS|FAIL at <passo>` e o exit code do processo. Os testes usam o padrão existente em `test/sensors/check.test.mjs`: projeto temporário, passos substituídos e um `kof-mut` falso no PATH. O falso precisa passar a imprimir a linha `reportPath=` e gravar o JSON.

**C1. `no_mutants` sem limitação vira SKIP, e o `check` passa.**
- **Exemplo:** produção alterada (`src/main/kof/Game.kf`), todos os passos anteriores verdes, e o `kof-mut` falso sai com 3, com relatório `{"status":"no_mutants","limitations":[]}`.
- **Esperado:** linha `mutation  SKIP (KofMut no_mutants: no applicable mutants)`, `CHECK: PASS` e exit 0.
- **RED esperado antes da mudança:** `mutation  FAIL (KofMut exit 3: incomplete, no_scope or no_mutants; quality not approved)`, `CHECK: FAIL at mutation` e exit 1.
- **Por que distingue:** verificar o estado, a frase **e** o exit code. Um SKIP que ainda reprovasse o `check` seria pego pelo exit code.

**C2. `incomplete` continua FAIL e mostra o motivo.**
- **Exemplo:** exit 3 com `{"status":"incomplete","limitations":["src/main/kof/Game.kf: Unsupported AST node: X"]}`.
- **Esperado:** `mutation  FAIL (…)`, com `incomplete` e o texto da limitação no detalhe, e exit 1.
- **Por que distingue:** uma implementação que fizesse SKIP de todo exit 3 passaria no C1 e falharia aqui.

**C3. `no_scope` continua FAIL.** Exit 3 com `{"status":"no_scope","limitations":[]}` → `mutation  FAIL (…no_scope…)`, exit 1.
- **Por que distingue:** um SKIP decidido só por "`limitations` vazia" passaria no C1 e falharia aqui.

**C4. Relatório contraditório nunca vira SKIP.** Cada caso abaixo dá `mutation  FAIL` e exit 1:
- exit 3 com `status: "no_mutants"` e `limitations` **não vazia**;
- exit 3 com `status: "complete"`.

Os dois são incoerentes pelo contrato.

**C5. Sem relatório utilizável, o resultado é FAIL, nunca SKIP.** Cada caso abaixo dá FAIL, com detalhe que diga que o relatório não pôde ser lido:
- exit 3 sem a linha `reportPath=`;
- duas linhas `reportPath=`;
- caminho anunciado inexistente;
- JSON inválido.

**C6. Os exits 0, 1 e 2 não mudam.** As asserções atuais de exit 1 (FAIL "at least one mutant survived") e exit 0 (PASS) no teste `mutation runs on changed production Kof files and its verdict decides check` continuam passando. Só a asserção antiga do exit 3 muda, e essa troca precisa ficar registrada como mudança de contrato no aceite.

**C7. Prova real com o KofMut instalado**, numa cópia temporária do repositório fora de pastas com ponto (KofLang/Kof4j#999). A cópia é commitada como `main`, com uma branch `probe`.
- **(a)** Alterar **só** o `State.kf`, acrescentando uma constante a um `enum` que nenhum `switch` use. Conferir antes com `kof check`; se quebrar, usar uma linha em branco no fim. Rodar `npm run check`.
  - **Esperado:** `mutation SKIP (KofMut no_mutants…)` e `CHECK: PASS`.
  - Registrar `reportPath`, `status` e `limitations` do relatório real.
- **(b)** Na mesma cópia, acrescentar um arquivo de produção com uma construção que o KofMut não suporta, por exemplo um `record` válido para `kof check` (conferir em JVM e JS antes), mais uma alteração no `State.kf`. Rodar `npm run check`.
  - **Esperado:** `mutation FAIL (… incomplete …)`.
  - Se nenhum `record` passar no `kof check`, registrar a lacuna e cobrir o C2 só pelo teste com o falso.
- **(c)** Alterar `Background.kf`, que teve 1 de 1 morto no R0. **Esperado:** `mutation PASS`.
- Apagar a cópia no fim.

**C8. Documentação.**
- `SENSORS.md`, linha 39: trocar "KofMut exit 1 (a survivor), 2 or 3 fails the check" pela regra nova, dizendo que SKIP não aprova a qualidade.
- `docs/desenvolvimento.md:239` e o `.pt_BR`: só ajustar se o texto do `check` for afetado. Esse trecho descreve a receita manual, que continua correta.
- `npm run docs:sensor` com PASS.

**C9. Não regressão.**
- `node --test test/sensors/*.test.mjs` todo verde (registrar a contagem);
- `scripts/kof-sensors/test` 40/0 ou mais, sem mudança no medidor;
- `git diff --check` com exit 0;
- `npm run check` na própria branch: PASS, com mutação SKIP, porque a branch não altera `.kf`.

## Entrega (autorizada)

1. Registrar a evidência em `.agent/validation/mutation-no-mutants-skip.md` (novo), com:
   - para cada critério de C1 a C9: comando, resultado observado e onde está a asserção;
   - o RED esperado e o observado;
   - a mudança de contrato do C6;
   - as lacunas.

   Acrescentar uma linha no `EXECPLAN.md`, em seção datada.
2. Rodar `lc`. Conferir com `git log -1 --stat` que o commit tem só os arquivos deste plano.
3. Rodar `lp`.
4. Rodar `luna "abra um PR de mutation-no-mutants-skip para main em renanfranca/kof-sifuture com um resumo em pt-BR, espere a CI passar, faça o merge, atualize a main local com fast-forward e apague a branch local e remota mergeada"`. Se a CI falhar, o Luna **não** faz merge: parar e avisar.
5. Conferir:
   - `git log origin/main -1` contém o merge;
   - `main` local = `origin/main`;
   - a branch apagada local e remotamente;
   - o run da CI da `main` com sucesso (`gh run list --branch main -L 1`).
6. **Voltar para a branch anotada no início**, por exemplo `git switch sensor-debt-payoff`, e confirmar o checkout limpo. Avisar o usuário que a branch da dívida ainda não tem a correção, e que vai recebê-la quando incorporar a `main`. É provável um conflito pequeno em `test/sensors/check.test.mjs`, que a dívida também altera.

## Obrigações do executor

- Reconferir cada expectativa contra as fontes citadas (o contrato do KofMut, o `SENSORS.md` e este plano), **separado** de conferir se o teste a demonstra.
- Uma suíte verde não prova cada critério sozinha. Registrar a evidência de cada um.
- Uma lacuna aberta ou uma verificação que falhou não pode ser apresentada como critério satisfeito. Registrar antes de entregar e avisar no relatório final.
