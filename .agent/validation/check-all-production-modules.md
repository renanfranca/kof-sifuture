# Aceite: o check de tipos cobre todos os módulos de produção

Plano: [`.agent/execplans/check-all-production-modules.md`](../execplans/check-all-production-modules.md).
Issue #44. Branch `fix/44-check-all-production-modules`, a partir de `5923c7b`.
Kof do `PATH`; regra conferida no checkout `24c99bd31` de `~/projects/kof`.
Execução em 21/11/2026.

## Conferência das expectativas pelas fontes

- Issue #44: um módulo de produção que nada importa passava pelo check com exit
  0. O valor esperado dos testes novos (exit diferente de 0 e `ERROR` em
  `Probe.kf`; exit 0 sem o erro) vem daí, não do código.
- `~/projects/kof/docs/language-reference/modules.md`, seção 3.1, item 3
  ("Directory expansion"): `import a.b`, quando `a/b/` é uma pasta da raiz do
  módulo, puxa todos os `.kf` dessa pasta. Logo, `import sifuture.*` não alcança
  `sifuture/probe/`, e uma linha por pasta de produção alcança.
- Antes da mudança, o `Main.kf` preparado pelo `check` era só
  `import sifuture.*` (`scripts/kof_project.py`, `prepared_sources`). Depois,
  sem `--fixture`, ele lista `import sifuture.*` e `import sifuture.game.*` no
  projeto real; o build continua com `import sifuture.*`.

## Critérios

| # | Comando | Resultado observado | Evidência |
| --- | --- | --- | --- |
| A1 | `python3 -m unittest discover -s tests -p 'test_*.py'`, teste `test_check_reports_a_type_error_in_a_production_module_nothing_imports` | Antes da mudança: `AssertionError: 0 == 0` nos subtestes `target='jvm'` e `target='js'` (21 testes, 2 falhas). Depois: OK. Na chamada direta do Stop (A4), o diagnóstico é `Probe.kf:4:5: ERROR SEM021: type mismatch: cannot assign String to 'x: Int'`, exit 1. | `tests/test_kof_project.py`; seção "Vermelho do A1" |
| A2 | mesmo comando, testes `test_check_accepts_a_well_typed_production_module_nothing_imports` e `test_check_accepts_the_unchanged_project` | OK em JVM e JS. Para provar que distinguem uma entrada quebrada, a entrada foi trocada de propósito por `import <pacote>.missing.*`: os dois testes falharam nos dois alvos (4 falhas); o arquivo foi restaurado em seguida. | `tests/test_kof_project.py` |
| A3 | mesmo comando; `git diff main -- scripts/kof_project.py tests/test_kof_project.py` | Os dois testes de fixture passam sem edição (o diff do arquivo de testes tem 0 linhas removidas). No wrapper, `build` e o ramo `if fixture is not None` ficaram iguais; `prepared_sources` ganhou `entry` com padrão `"import sifuture.*\n"`, que o build continua usando. | diff abaixo |
| A4 | `npm run test:sensors`; chamada direta de `scripts/stop-sensor.mjs` numa cópia completa do projeto | `test:sensors` 72 de 72. O teste que fixava o conteúdo de `types-entry.kf` virou `the type tier runs the normal project check for each target, without an entry of its own`, vermelho antes (`--fixture .../types-entry.kf` nos dois alvos) e verde depois. Na cópia, com `src/main/kof/sifuture/probe/Probe.kf` contendo `Int x = "texto"`: `types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN`, `decision: block`, e `.sensors/ledger` só com `probe-a4.pushbacks.json` e `probe-a4.stop.log`. | seção "Stop na cópia" |
| A5 | `git diff --name-only main`; `git status --short`; `git diff --exit-code main -- .codex/hooks.json` | Mudados: `SENSORS.md`, `docs/desenvolvimento.md`, `docs/desenvolvimento.pt_BR.md`, `scripts/kof_project.py`, `scripts/stop-verdict.mjs`, `test/sensors/stop-hook.test.mjs`, `tests/test_kof_project.py`; novos: este plano, este registro e a entrada no `EXECPLAN.md`. `.codex/hooks.json` sem diff. | lista acima |

## Vermelho do A1

```text
FAIL: test_check_reports_a_type_error_in_a_production_module_nothing_imports (...) (target='jvm')
    self.assertNotEqual(code, 0)
AssertionError: 0 == 0
FAIL: test_check_reports_a_type_error_in_a_production_module_nothing_imports (...) (target='js')
    self.assertNotEqual(code, 0)
AssertionError: 0 == 0
Ran 21 tests in 7.801s
FAILED (failures=2)
```

## A3: diff do wrapper

```diff
-def prepared_sources(*, fixture=None, model_only=False, root=ROOT):
+def prepared_sources(*, fixture=None, model_only=False, root=ROOT, entry="import sifuture.*\n"):
...
-            (source / "Main.kf").write_text("import sifuture.*\n")
+            (source / "Main.kf").write_text(entry)
...
+def _production_entry(main):
+    """Import every production package directory so modules nothing imports are still checked."""
+    packages = sorted({".".join(path.parent.relative_to(main).parts) for path in main.rglob("*.kf")} - {""})
+    return "".join(f"import {package}.*\n" for package in packages)
+
 def check(*, target="jvm", json_output=False, kof=None, root=ROOT, fixture=None):
-    with prepared_sources(fixture=fixture, root=root) as source:
+    entry = _production_entry(Path(root).resolve() / "src/main/kof")
+    with prepared_sources(fixture=fixture, root=root, entry=entry) as source:
```

## Stop na cópia

A cópia foi feita com `rsync` do checkout (sem `.git`, `node_modules` e
`.sensors`), seguida de `git init` e um commit base. O `kof_project.py` resolve
as fontes pela própria localização, por isso a cópia leva os scripts junto.
Payload sintético: `{"session_id":"probe-a4","stop_hook_active":false,"hook_event_name":"Stop"}`,
passado por stdin a `node scripts/stop-sensor.mjs --root <cópia>`.

```text
STOP SENSORS: lint PASS · dup PASS · gitleaks PASS · types:jvm FAIL · types:js FAIL · tests:jvm NOT RUN · tests:js NOT RUN

src/main/kof/sifuture/probe/Probe.kf:4:5: ERROR SEM021: type mismatch: cannot assign String to 'x: Int'
src/main/kof/sifuture/probe/Probe.kf:4:5: ERROR SEM021: type mismatch: cannot assign String to 'x: Int'
```

O Kof traz só o nome curto: `python3 scripts/kof_project.py check --target jvm`
na cópia imprime `Probe.kf:4:5: ERROR SEM021: ...` e sai com 1. A troca pelo
caminho do escopo (`relocated` em `scripts/stop-verdict.mjs`) continua
necessária e ficou.

## Tempos do check

| Alvo | Antes | Depois |
| --- | --- | --- |
| JVM | 1,63 s | 1,62 s |
| JS | 0,74 s | 0,75 s |

## Validação final

| Comando | Resultado |
| --- | --- |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 23 testes, OK, exit 0 |
| `npm run test:sensors` | 72 de 72, exit 0 |
| `npm run check` | `types:jvm`, `types:js`, `types:fixtures`, `docs:sensor` PASS; `mutation` SKIP (nenhum `.kf` de produção mudou); `CHECK: PASS`, exit 0, 27 s |
| `npm run check:task` | as sete jornadas PASS; `CHECK:TASK: PASS`, exit 0, 233 s |
| `git diff --check` | exit 0 |

Depois deste registro e da entrada no `EXECPLAN.md`, `npm run docs:sensor` e
`git diff --check` rodaram de novo; o resultado está no Progress do plano.

## Limites que ficam

- Um `.kf` direto em `src/main/kof`, fora de qualquer pasta, não entra na lista
  de imports (o pacote vazio é descartado). Hoje não existe nenhum, e o
  comportamento é o mesmo de antes.
- Uma segunda pasta de produção com `main()` daria `PKG002` no check. Não existe
  hoje; se aparecer, o check falha com erro explícito.
