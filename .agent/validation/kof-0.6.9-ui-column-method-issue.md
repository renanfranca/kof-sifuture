# [Bug]: método da própria classe chamado dentro de Column()/Row() falha em JS e JVM desde 0.6.5

Rascunho preparado em **31/10/2026**, ainda não publicado. Corpo proposto abaixo.

### Summary

Ao testar o SiFuture com o Kof 0.6.9, a ajuda de controles deixou de abrir no navegador, com `ReferenceError: heading is not defined` no construtor de [`ControlsGuide.kf`](https://github.com/renanfranca/kof-sifuture/blob/2ca8dce0b1ea0e200fd33f98f68582263f3ff3e8/src/main/kof/sifuture/ControlsGuide.kf#L25). Com 0.6.4, o mesmo código funciona. Separei o exemplo abaixo para facilitar a reprodução fora do jogo.

Poderiam verificar esse comportamento?

### Target

JS e JVM

### Kof version

Distribuições oficiais Linux x86_64: `kof 0.6.5`, `kof 0.6.6` e `kof 0.6.9`. Controle: `kof 0.6.4`.

### Operating system

Ubuntu 22.04.5 LTS, x86_64, WSL2.

### Minimal reproduction

Em um diretório vazio, sem `kof.toml` nos ancestrais, salve como `Main.kf`:

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
    println("ok")
}
```

### Command used

```sh
kof build . --target js --output out
node out/Default.mjs
kof run Main.kf --target jvm
```

### Expected behavior

Imprimir `ok` nos dois alvos, como acontece com 0.6.4.

### Actual behavior

O build retorna 0 em todas as versões. A execução:

| Versão | JS | JVM |
| --- | --- | --- |
| 0.6.4 | `ok` | `ok` |
| 0.6.5, 0.6.6, 0.6.9 | `ReferenceError: heading is not defined` | `java.lang.NoSuchMethodError: 'java.lang.Object Default.Main.heading(java.lang.String)'` |

No JS gerado, a chamada aparece como `heading("ok")`; no 0.6.4, como `this.heading("ok")`. Com `Row` acontece o mesmo. Estas formas passam no 0.6.9:

- `listOf(heading("ok"))` fora de `Column`;
- guardar a lista em uma variável antes de passar para `Column`;
- `this.heading("ok")` explícito, que funciona como contorno.

Talvez ajude: a mudança aparece entre 0.6.4 e 0.6.5, quando entrou a correção da #827. Num build local de `ff6cb25`, voltar a inferir o argumento de `Column`/`Row` em `BuiltinUiCallTyper` fez o exemplo passar nos dois alvos. Não sei se essa é a correção adequada.

### Kof intent and existing idiom

Montar uma ajuda com métodos auxiliares privados da própria classe (`heading`, `paragraph`) passados para `Column(listOf(...))`. É uma chamada comum de método da classe, sem API nova; a mesma forma funciona fora de `Column` e funcionava dentro dele no 0.6.4.

### Kof contract source

[`docs/language-reference/expressions.md`](https://github.com/KofLang/Kof4j/blob/ff6cb25227c63fa260e47050fc827a9b84769694/docs/language-reference/expressions.md#L22), §2 e §10:

> `this` — receiver of the current method/constructor.

> `f(args)` — function/method.

### Classification (D-KOF-FIRST Gate 4)

Real bug — valid Kof diverges from Kof's own contract

### Checklist

- [x] I searched existing issues and this is not a duplicate. Buscas de 31/10/2026 em `KofLang/Kof4j` por `ReferenceError Column`, `NoSuchMethodError Main` e `BuiltinUiCallTyper` não encontraram relato equivalente.
- [x] I reproduced this against the latest build. Distribuição oficial 0.6.9, a release mais recente em 31/10/2026.
- [x] The reproducer is valid Kof — I checked `docs/language-reference/` and `training/anti-patterns/fake-idioms.md`, and this is not syntax imported from another language (KOF-first, external-second).
- [x] I read `docs/philosophy.md` ("What Kof Is NOT"). This is a deviation from Kof's documented behavior — not a request to import another language/stack's syntax (Java/Kotlin idioms, HTML/CSS into `kof.ui`, framework layers); those are closed with a pointer to the docs, not fixed.
