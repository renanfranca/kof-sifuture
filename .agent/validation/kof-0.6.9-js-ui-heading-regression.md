# Regressão de resolução de chamadas dentro de `Column`/`Row` no kof.ui, presente no Kof 0.6.9

Investigação de 31/10/2026, motivada pelo chat
`01a191b9-2551-7372-80d1-12e4fe8138ac`, revisada e aprofundada no mesmo dia.

Commit do SiFuture usado nas verificações:
`2ca8dce0b1ea0e200fd33f98f68582263f3ff3e8`.
SHA-256 de `src/main/kof/sifuture/ControlsGuide.kf`:
`bf7861e23ff92c149cd08a35795a05a58790fde4a8f932cc2b2579860aea0a37`.
Checkout de pesquisa do Kof: `ff6cb25227c63fa260e47050fc827a9b84769694`
(registro de release da 0.6.9). Navegador: Google Chrome `155.0.8059.39`.
Node `v24.16.0`.

## Conclusão

Dentro de uma classe, uma chamada nua a um método da própria classe deixa de
ser resolvida quando aparece no argumento de `Column(...)` ou `Row(...)` do
`kof.ui`. O compilador então a trata como função de topo:

- no JS, emite `heading(...)` em vez de `this.heading(...)`, e a execução
  falha com `ReferenceError: heading is not defined`;
- no JVM, emite chamada para `Default.Main.heading`, e a execução falha com
  `NoSuchMethodError`.

O build termina com exit 0 nos dois alvos. O defeito está no analisador
semântico, compartilhado pelos alvos, e não apenas na geração de JavaScript.

A causa foi demonstrada por intervenção. Restaurar a visita ao argumento em
`BuiltinUiCallTyper` corrige todos os reprodutores, em JS e JVM, e faz o
SiFuture original passar nos percursos de navegador. A visita foi removida pelo
commit Kof `5fb5b910a` ("Row()/Column() vazios baixam para o runtime"),
ancestral do registro de release da 0.6.5 e ainda presente no HEAD da 0.6.9.

## Evidência histórica

O [registro anterior de controles](sifuture-controls.md#L778) enumera os sete
scripts de navegador executados e registra:

> Chrome 155.0.8059.39: os sete percursos completos passaram.

Esse trecho não informa a versão do Kof usada. O reteste abaixo, com 0.6.4, é
o que sustenta que o código atual passava em uma versão anterior.

```bash
python3 tests/browser_controls.py --kof /home/renanfranca/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof
```

Resultado: exit 0. Última linha:

```text
PASS isolated keyboard, focus, pointer and touch controls in Chrome
```

## Comparação dos pacotes instalados

O mesmo código do SiFuture foi compilado com
`/home/renanfranca/.local/share/kof/kof-<versão>-linux-x86_64/bin/kof`,
por meio de `scripts/kof_project.py::build`
(`<kof> build <fontes> --target js --output <saída>`). Cada resultado foi
aberto no Chrome via Playwright, com relógio pausado em
`2026-01-01 00:00:00` e `pageerror` coletado antes da navegação. Todos os
builds terminaram com exit 0.

| Kof | `#game-keyboard` | Canvases visíveis | Erro JavaScript na abertura |
|---|---:|---:|---|
| 0.5.0-beta | 1 | 1 | Nenhum observado |
| 0.6.3 | 1 | 1 | Nenhum observado |
| 0.6.4 | 1 | 1 | Nenhum observado |
| 0.6.5 | 0 | 2 | `ReferenceError: heading is not defined` |
| 0.6.6 | 0 | 2 | `ReferenceError: heading is not defined` |
| 0.6.7 | 0 | 2 | `ReferenceError: heading is not defined` |
| 0.6.8 | 0 | 2 | `ReferenceError: heading is not defined` |
| 0.6.9 | 0 | 2 | `ReferenceError: heading is not defined` |

Para o 0.6.6, havia a lembrança de que "tudo passava". O percurso completo foi
repetido com essa versão:

```bash
python3 tests/browser_controls.py --kof /home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/bin/kof
```

Resultado: exit 1, com o mesmo sintoma da tabela:

```text
playwright._impl._errors.Error: Locator.evaluate: Error: strict mode violation: locator("canvas:visible") resolved to 2 elements:
```

Os registros que usam 0.6.6 (`sensors-adoption.md`, `sensor-calibration.md`)
mostram suítes de regras e `check`, sem percurso de navegador. Essas suítes
não montam a interface. Isso explica a impressão de que o 0.6.6 passava.

## Código afetado no jogo

Trecho de [ControlsGuide.kf](../../src/main/kof/sifuture/ControlsGuide.kf#L25):

```kof
        var keyboardBlock = Column(listOf(
            heading("Teclado"),
            paragraph("Na abertura, use Tab ou clique em um controle. O foco do menu permite jogar sem clicar na área; ela continua disponível por clique ou Tab."),
            keyboard))
```

`heading` e `paragraph` são métodos privados de `ControlsGuide`. O Kof 0.6.4
gera `kofListAdd(__kof_t14, this.heading("Teclado"));`. A partir do 0.6.5, e
até o 0.6.9, gera `kofListAdd(__kof_t14, heading("Teclado"));`. O mesmo
acontece com as 11 chamadas a `paragraph`. A exceção interrompe o construtor:

```text
ReferenceError: heading is not defined
    at new sifuture_ControlsGuide
    at new sifuture_GameControls
    at main
```

O teclado do jogo nunca é criado e a visibilidade final dos canvases nunca é
configurada. Isso explica os elementos ausentes e os dois canvases visíveis.

## Isolamento da forma que dispara o defeito

Exemplos diagnósticos criados nesta investigação. Todos seguem este molde e
variam só a expressão do construtor:

```kof
import kof.ui.*
class Guide {
    Column root
    public constructor() {
        root = Column(listOf(heading("ok")))
    }
    private Label heading(String text) { return Label(text) }
}
main() {
    var guide = Guide()
    println("PASS A column-listOf-label")
}
```

Comandos por versão: `<kof> build <dir> --target js --output <saída>`,
seguido de `node <saída>/Default.mjs`. No JVM: `<kof> run Main.kf --target jvm`.

| Caso | Forma | 0.6.4 JS | 0.6.5 / 0.6.6 / 0.6.9 JS |
|---|---|---|---|
| A | `Column(listOf(heading("ok")))` | PASS | `ReferenceError` |
| B | `listOf(heading("ok"))` sem `Column` | PASS | PASS |
| C | `heading("ok")` direto | PASS | PASS |
| D | `Holder(listOf(heading("ok")))`, classe própria, retorno `String` | PASS | PASS |
| E | `Column(listOf(this.heading("ok")))` | PASS | PASS |
| F | `var items = listOf(heading("ok"))` e depois `Column(items)` | PASS | PASS (0.6.5, 0.6.9) |
| G | `Row(listOf(heading("ok")))` | PASS | `ReferenceError` (0.6.5, 0.6.9) |
| H | caso A dentro de um método comum, não do construtor | PASS | `ReferenceError` (0.6.5, 0.6.9) |
| I | `Column(listOf(Label("x"), heading("ok")))` | PASS | `ReferenceError` (0.6.5, 0.6.9) |

No JVM, o caso A passa no 0.6.4. No 0.6.5, 0.6.6 e 0.6.9 falha com:

```text
java.lang.NoSuchMethodError: 'java.lang.Object Default.Main.heading(java.lang.String)'
```

O caso E passa no JVM do 0.6.9.

O gatilho é a chamada nua aparecer na subárvore do argumento de `Column`/`Row`.
Os casos mostram que ele não depende do tipo `Label`, de `listOf`, do
construtor ou da posição na lista. A versão anterior deste registro concluía
que um controle com `String` "sem a composição de UI" passava, mas aquele
controle mudava duas variáveis ao mesmo tempo. O caso D separa as duas.

## Causa no compilador

Em [BuiltinUiCallTyper.java](../../../kof/kof-compiler/src/main/java/dev/kof/compiler/BuiltinUiCallTyper.java#L39),
o analisador semântico tipa `Column`/`Row` sem visitar o argumento:

```java
        if (mc.receiver() == null && ("Column".equals(mc.methodName()) || "Row".equals(mc.methodName()))
                && (mc.arguments().isEmpty() || mc.arguments().size() == 1)) {
            return "Column".equals(mc.methodName()) ? KofUi.COLUMN : KofUi.ROW;
        }
```

Os outros widgets visitam os argumentos. `Label` e `View`, por exemplo, chamam
`SemExpressionTyper.inferType(sa, mc.arguments().get(0), scope)` antes de
retornar. O commit `5fb5b910a` removeu exatamente essa visita no caso de
`Column`/`Row`:

```diff
         if (mc.receiver() == null && ("Column".equals(mc.methodName()) || "Row".equals(mc.methodName()))
-                && mc.arguments().size() == 1) {
-            SemExpressionTyper.inferType(sa, mc.arguments().get(0), scope);
+                && (mc.arguments().isEmpty() || mc.arguments().size() == 1)) {
             return "Column".equals(mc.methodName()) ? KofUi.COLUMN : KofUi.ROW;
```

Sem a visita, `heading(...)` não recebe método resolvido. No lowering,
[ExpressionBareCallLowerer.java](../../../kof/kof-compiler/src/main/java/dev/kof/compiler/ExpressionBareCallLowerer.java#L62)
só usa o receptor implícito quando `getResolvedMethod(mc)` existe. Caso
contrário, cai na emissão de função de topo
([linha 279](../../../kof/kof-compiler/src/main/java/dev/kof/compiler/ExpressionBareCallLowerer.java#L279)):

```java
                ops.add(new KofCall(CompilerTypes.mainClassType(driver.currentModule), mc.methodName(), argTypes, returnType, KofCallKind.FUNCTION));
```

No backend JS, `KofCallKind.FUNCTION` vira um identificador nu
([JsCallEmitter.java](../../../kof/kof-compiler/src/main/java/dev/kof/compiler/js/JsCallEmitter.java#L140)).
No JVM, vira uma chamada para `Default.Main`. O caso F passa porque o
`listOf` em uma declaração própria é visitado pelo analisador.

### Prova por intervenção

Uma cópia do Kof `ff6cb25` foi exportada com `git archive` para um diretório
temporário e compilada com `mvn -pl kof-cli -am clean package -DskipTests`.
O `lib/kof.jar` de uma cópia da distribuição 0.6.9 foi trocado pelo jar
resultante. O checkout do Kof não foi modificado.

1. **Controle, sem patch:** reproduz exatamente o pacote 0.6.9. Os casos A, G,
   H e I dão `ReferenceError`, os demais passam, e o caso A no JVM dá
   `NoSuchMethodError`.
2. **Com uma linha restaurada:**

   ```diff
   >             for (ExpressionNode arg : mc.arguments()) SemExpressionTyper.inferType(sa, arg, scope);
   ```

   Os casos A a I passam em JS e todos emitem `this.heading("ok")`. Os casos
   A, G, H e I passam em JVM. Com o compilador corrigido, o SiFuture **sem
   alterações** (hash acima) passou nos dois percursos:

   ```text
   tests/browser_controls.py: exit 0
   PASS isolated keyboard, focus, pointer and touch controls in Chrome
   tests/browser.py: exit 0
   PASS menu, Enter and Space, conservative confirmation, pause, result and menu in Chrome
   ```

Um primeiro build com patch, sem `clean`, gerou um jar do CLI ainda com a
classe antiga, e os reprodutores continuaram falhando. Isso foi detectado
comparando o bytecode com `javap`: 15 chamadas a `inferType` em vez de 16.
O resultado acima é do build com `clean`, já com as 16 chamadas.

A linha restaurada demonstra a causa. Ela não pretende ser a correção final:
a correção no Kof deve vir com teste próprio. Este registro não é o aceite de
uma correção.

## Contorno no SiFuture

Com `this.heading(...)` e `this.paragraph(...)` explícitos nas 14 chamadas de
`ControlsGuide.kf`, o Kof 0.6.9 publicado passou nos dois percursos:

```text
tests/browser_controls.py --kof <0.6.9>: exit 0
tests/browser.py --kof <0.6.9>: exit 0
```

A mudança foi temporária e revertida com `git checkout`. O hash voltou ao
valor acima. Ainda não houve decisão de adotar o contorno no código do jogo.

## O que os resultados verdes do chat comprovam

O chat anterior registrou, com Kof 0.6.9, 114 PASS e 0 FAIL nas suítes JVM e
JS de regras do jogo. Essas suítes não instanciam `ControlsGuide`. O
[percurso de meteoros](../../tests/browser_meteor.py#L43) usa
`model_only=True`, que copia apenas `sifuture/game`, e também não compila
`ControlsGuide`. Esses passes não contradizem o defeito. O caso de `break`
(registro `kof-0.6.7-js-break-issue.md`) é outro defeito.

O [Learn Kof](../../../kof/learn/35-kof-ui.md#L5) situa a renderização de
`kof.ui` no JS:

> `kof.ui` is Kof's UI platform. Rendering is **KofJS**: the same program
> compiles to JVM, Native and JS, but only the JS target draws (via a native
> webview with embedded WebKit, or in the browser).

A falha no JVM acontece antes de qualquer renderização, já na chamada do
método.

## Limites

- O commit causador foi identificado pelo histórico e confirmado por
  restauração da linha. Não foi feito bisect binário. A correspondência entre
  pacotes publicados e commits é aproximada: o pacote 0.6.5 inclui libs que
  não aparecem no diff entre os bumps 0.6.4 e 0.6.5.
- Native não foi testado.
- O defeito não consta em `docs/bugs-and-gaps/known-bugs.md` do checkout
  `ff6cb25`. Busca por `heading is not defined` e por `Column(listOf(`.
- Nenhum workflow novo foi executado.

## Evidências locais opcionais

- `.agent/tmp/kof-browser-proof-20261031-y_0pb6wy/`: comparação de pacotes
  (`application-comparison.json`, `application-<versão>/Default.mjs`),
  reprodutor original e logs da sessão anterior.
- `.agent/tmp/heading-review-20261031/`: reprodutores A a I (`repro/`),
  `patch.diff`, logs dos builds Maven de controle e com patch, percurso
  `controls-0.6.6.log`, percursos com `this.` explícito no 0.6.9 e percursos
  com o compilador corrigido.

Os resultados essenciais estão transcritos acima. Os arquivos locais não são
necessários para compreender a conclusão.
