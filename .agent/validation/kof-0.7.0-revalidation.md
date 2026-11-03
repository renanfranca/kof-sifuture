# Revalidação com Kof 0.7.0 (SiFuture e KofMut)

Data: 2026-11-03 (UTC). Repete a matriz do registro
[Kof 0.6.10](../../../kof-mut/.agent/validation/kof-0610-revalidation.md) e
executa a parte do KofMut que ficou de fora naquela ocasião. Nenhum commit,
download ou alteração de distribuição Kof foi feito; os dois checkouts ficaram
limpos antes e depois.

Evidência local opcional:
`.agent/tmp/kof-070/56e99392-da69-4674-b9e0-906d6e585000/` (abreviada **E**).
Cada comando tem `<nome>.{json,stdout,stderr}` com argv, cwd, PATH, início e
fim UTC, duração e exit nativo, gravados por `.agent/tmp/kof-070/record`.
Inventário SHA-256: `E/raw-evidence.sha256` (182 arquivos).

## Identidade

| Item | Valor |
| --- | --- |
| Kof 0.7.0 | `~/.local/share/kof/kof-0.7.0-linux-x86_64`, `kof.jar` `fda317b89bb05ffdb068c2d4ff80be71ecfa5dee821b7b322bfe296acb24ae17`, JDK embutido 25.0.5, primeiro no PATH (`~/.local/bin/kof`) |
| Kof 0.6.4 (alternativa de compatibilidade e controle) | `kof.jar` `137a838d38757e317545474d55ad6a3ad291fb86d263ae77d9197cf705829c62` |
| SiFuture | `0995046477c87736b54e959506e50a45d418f609`, branch `sensor-calibration-m1`, limpo |
| KofMut | checkout `64c85f886fe117b80440bea22da60dc13865f369` (`main`), limpo; imagem instalada `b5401898d74f18086fa29ed8f59f55f3e51a84a1608a5b4a23278f6282735d79`, fontes de execução iguais ao checkout |
| Pesquisa Kof | `~/projects/kof` em `30dde745c`, somente leitura |
| Navegador | Google Chrome 155.0.8059.39 (WSLg, `DISPLAY=:0`), Python 3.10.12 |

## SiFuture com 0.7.0

| Passo | Comando | Exit | Resultado |
| --- | --- | ---: | --- |
| check | `python3 scripts/kof_project.py check --target jvm\|js --json --kof kof` | 0 / 0 | `success: true`, 0 erros |
| test | `python3 scripts/kof_project.py test --target jvm\|js --kof kof` | 0 / 0 | `0 failed of 114 tests` nos dois alvos |
| build | `python3 scripts/kof_project.py build --output E/sf-build-out` | 0 | 113 arquivos, com `index.html` e `Default.mjs` |
| Python | `python3 -m unittest discover -s tests -p 'test_*.py'` | 0 | 16 testes OK |
| CI | `bash tests/ci-contract.sh` | 0 | 28 PASS, 0 FAIL (ripgrep do opencode acrescentado ao PATH temporário) |
| sensores | `scripts/kof-sensors/test` | **1** | 22 testes, 1 falha, 8 erros |
| sensores | `scripts/kof-sensors/run .` | **1** | `success: false`, 14 falhas |
| sensores | `scripts/kof-sensors/verify-kofmut ~/projects/kof-mut E/verify-kofmut-out` | 0 | `detected` 1 Killed, `survived` 1 Survived, fixtures preservadas |
| navegador | sete `python3 tests/browser*.py` | 0 em todos | `browser`, `boss`, `controls`, `meteor`, `stage`, `subchief`, `weapons` |
| mutação real | receita manual: `kof-mut run --project "$PWD" --files kof-mut-scope.json --config kof-mut.json ...` | 1 | `complete`, 42 candidatos, 38 Killed, 4 Survived |

### Bloqueio 1 do 0.6.10 resolvido: regressão `Column`/`Row` (#991)

No 0.6.10 seis dos sete percursos de navegador falhavam. No 0.7.0 os sete
passam. A correção `7ec75f531` ("a method of the owning class inside
Column/Row resolves again") é ancestral do commit de release `1b7a07abb`
(`git merge-base --is-ancestor` retornou verdadeiro). O JS gerado confirma:
`E/sf-build-out/Default.mjs` tem 6 ocorrências de `this.heading(` e nenhuma de
`kofListAdd(__kof_tN, heading(`, a chamada nua que quebrava no 0.6.10.

### Bloqueio 2 continua: posição do nó de construtor

Os sensores falham pelo mesmo motivo registrado desde o 0.6.7. Trecho de
`E/sf-sensors-test.stdout`:

```text
AnalyzerTest.constructorCallToItsClassDoesNotBecomeTheDeclarationStart:226->measure:16 » IllegalArgument Cannot locate constructor body end for Box at Token[type=IDENTIFIER, value=constructor, file=Probe.kf, line=2, column=5, offset=16, length=11]
```

`Spans.java` ainda espera que `ConstructorDeclarationNode.position()` aponte
para depois do corpo; desde o 0.6.7 a posição é o início da declaração. A
correção cabe ao SiFuture e independe da versão do Kof.

### Mutação real igual à referência 0.6.4

Relatório `kofVersion: 0.7.0`, `status: complete`, contagens
`candidates=42 executed=42 killed=38 survived=4 compileError=0 timeout=0 testError=0 pending=0`.
Os sobreviventes são os mesmos registrados com 0.6.4 em
[sensors-adoption.md](sensors-adoption.md) (passo 8):

```text
Survived src/main/kof/sifuture/game/Meteor.kf:5:19 true -> false
Survived src/main/kof/sifuture/game/Meteor.kf:13:21 false -> true
Survived src/main/kof/sifuture/game/Meteor.kf:85:17 >= -> >
Survived src/main/kof/sifuture/game/Meteor.kf:86:75 <= -> <
```

Exit 1 é o código documentado para avaliação completa com sobrevivente.
Duração total 236 s (0.6.4: motor 211 s).

## KofMut com 0.7.0

Comando: `PATH=<0.7.0>/bin:$PATH KOF_MUT_COMPATIBILITY_OTHER=<0.6.4>/bin ./scripts/check`
no checkout do KofMut.

| Tentativa | Locale | Exit | Resultado |
| --- | --- | ---: | --- |
| 1 | herdado (`LANG=en_US.UTF-8`, locale não instalado) | 1 | 4 filas falharam, 5 testes |
| 2 | `LC_ALL=C.UTF-8` | 0 | as 9 filas passaram em 803 s |

Os cinco testes da tentativa 1 verificam argumentos Unicode, por exemplo
`launcher preserves argv cwd environment and application exit status: expected: observed.arguments[2] == "ação 😀"`.
A causa é do ambiente, não do 0.7.0: `locale -a` lista somente `C`, `C.utf8`
e `POSIX`, e a JVM decodifica argv como ASCII. Probe mínimo fora de qualquer
`kof.toml`, `kof run Main.kf --target jvm "ação 😀"`, imprimindo
`json.encode` dos argumentos e `System.getProperty("sun.jnu.encoding")`:

| Kof | Locale herdado | `LC_ALL=C.UTF-8` |
| --- | --- | --- |
| 0.6.4 | `{"arguments":["a????o ????"]}`, `ANSI_X3.4-1968` | `{"arguments":["ação 😀"]}` |
| 0.6.10 | `{"arguments":["a????o ????"]}`, `ANSI_X3.4-1968` | não executado |
| 0.7.0 | `{"arguments":["a????o ????"]}`, `ANSI_X3.4-1968` | `{"arguments":["ação 😀"]}` |

O comportamento é idêntico em 0.6.4 e 0.7.0, portanto não é regressão. A
tentativa 1 não foi repetida com 0.6.4 primeiro; a atribuição vem do probe e
da tentativa 2. O SiFuture rodou com o locale herdado e não depende disso.

## Conclusão

O Kof 0.7.0 pode ser adotado no SiFuture e no KofMut. Compilação, 114 testes
em JVM e JS, build, os sete percursos de navegador, a checagem completa do
KofMut e a mutação real passam, com o mesmo resultado de mutação do 0.6.4.
Continua pendente somente a adaptação dos sensores à posição do nó de
construtor, defeito do SiFuture já conhecido.

Lacunas: a CI do SiFuture ainda resolve a release que o script escolher e
não foi executada aqui; a checagem do KofMut só passa com um locale UTF-8
disponível no shell.
