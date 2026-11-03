# [Bug]: break em for-in não encerra o laço no JS 0.6.7

Publicado em **27/10/2026**, por **renanfranca**, como [KofLang/Kof4j #975](https://github.com/KofLang/Kof4j/issues/975). Corpo público preservado abaixo.

### Summary

Encontrei uma diferença de comportamento após atualizar para o Kof 0.6.7, enquanto testava os disparos do subchefe do SiFuture. Separei o exemplo abaixo para facilitar a reprodução fora do jogo.

Esperava que apenas o primeiro item fosse ativado e o `break` encerrasse o laço. Foi o resultado observado com 0.6.6 em JVM e JS, e com 0.6.7 em JVM. Em 0.6.7 para JS, os três itens foram ativados na mesma tentativa.

Poderiam verificar esse comportamento? Ainda não identifiquei qual alteração causou a diferença.

### Target

JS

### Kof version

`kof 0.6.7`, distribuição oficial Linux x86_64 de [27/10/2026, 06:01:18 UTC](https://github.com/KofLang/Kof4j/releases/tag/kof-0.6.7-linux-x86_64). Controle: `kof 0.6.6`.

Comandos de identificação executados:

```sh
/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/bin/kof version
/home/renanfranca/.local/share/kof/kof-0.6.7-linux-x86_64/bin/kof version
```

```text
kof 0.6.6
kof 0.6.7
```

Usei `version`: `--version`, sugerido pelo formulário, respondeu `unknown: --version` nesta instalação.

### Operating system

Ubuntu 22.04.5 LTS, x86_64, WSL2. `uname -srmo`:

```text
Linux 6.18.54.1-microsoft-standard-WSL2 x86_64 GNU/Linux
```

### Minimal reproduction

Em um diretório vazio fora de projetos Kof, sem `kof.toml` nos ancestrais, salve este programa completo como `Main.kf`. Exemplo reduzido criado para o diagnóstico e executado nas quatro combinações abaixo:

```kof
class Slot {
    Bool active = false
    fire() { active = true }
}

class Rack {
    Int steps = 0
    List<Slot> slots = listOf(Slot(), Slot(), Slot())
    tick() {
        steps = steps + 1
        if (steps % 12 == 0) {
            for (var slot in slots) {
                if (!slot.active) { slot.fire(); break }
            }
        }
    }
}

main() {
    var rack = Rack()
    for (var i = 0; i < 12; i++) { rack.tick() }
    println(rack.slots[0].active)
    println(rack.slots[1].active)
    println(rack.slots[2].active)
}
```

### Command used

Comandos executados no diretório que contém somente `Main.kf`; ajuste o prefixo absoluto se as distribuições estiverem instaladas em outro lugar:

```sh
/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/bin/kof run Main.kf --target jvm
/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/bin/kof run Main.kf --target js
/home/renanfranca/.local/share/kof/kof-0.6.7-linux-x86_64/bin/kof run Main.kf --target jvm
/home/renanfranca/.local/share/kof/kof-0.6.7-linux-x86_64/bin/kof run Main.kf --target js
```

### Expected behavior

Após 12 passos, somente o primeiro slot ativo, com retorno 0:

```text
true
false
false
```

`tick()` tenta disparar nos múltiplos de 12. Após ativar o primeiro slot livre, o `break` deve encerrar o laço dos slots; o `if` apenas condiciona essa saída.

### Actual behavior

Kof 0.6.7/JS, stdout completo:

```text
true
true
true
```

| Versão | Alvo | stdout, na ordem dos três slots | Retorno | stderr |
| --- | --- | --- | ---: | --- |
| 0.6.6 | JVM | `true`, `false`, `false` | 0 | vazio |
| 0.6.6 | JS | `true`, `false`, `false` | 0 | vazio |
| 0.6.7 | JVM | `true`, `false`, `false` | 0 | vazio |
| 0.6.7 | JS | `true`, `true`, `true` | 0 | vazio |

### Kof intent and existing idiom

A intenção é ativar o primeiro slot livre e encerrar a busca. O idioma existente é `for (var slot in slots)` com `if` e `break`. Não é necessário acrescentar uma API ou mudar a regra do programa.

O [training de controle de fluxo, linha 142](https://github.com/KofLang/Kof4j/blob/df27d89fc94b56344984ac42579bc8bb40809150/training/idioms/control-flow.md#L142) diz:

> `break`/`continue` remain required in loops (to exit/skip).

Em paráfrase: são os controles que encerram o laço ou pulam a iteração. O [Learn Kof, capítulo 05, linha 83](https://github.com/KofLang/Kof4j/blob/df27d89fc94b56344984ac42579bc8bb40809150/learn/05-control-flow.md#L83) também mostra `break` condicionado por `if` dentro de um `for`:

```kof
for (var i = 0; i < 100; i++) {
    if (i == 50) break;
    if (i % 2 == 0) continue;
    print(i);
}
```

Esse bloco é uma citação didática do livro, não uma execução adicional. O programa mínimo acima foi executado em JVM e JS, nas duas versões.

No [SiFuture, `Subchief.kf:98`](https://github.com/renanfranca/kof-sifuture/blob/53e9626b19ad5740dd2b250b2f167932c892e364/src/main/kof/sifuture/game/Subchief.kf#L98), a mesma intenção aparece como:

```kof
                for (var shot in shots) {
                    if (!shot.active) { shot.fire(x, y); break }
                }
```

O impacto inferido pela leitura do jogo é ativar todos os tiros disponíveis na mesma tentativa. A matriz executa a redução independente; não constitui nova aceitação integral do SiFuture com 0.6.7.

### Kof contract source

[Referência da linguagem, `statements.md`, §5.4 e §5.5](https://github.com/KofLang/Kof4j/blob/df27d89fc94b56344984ac42579bc8bb40809150/docs/language-reference/statements.md#L110). O §5.4 admite `for-in` sobre `List<T>`; o §5.5, linha 134, estabelece:

> End/skip the iteration of the **innermost loop** (or `switch`).

Aplicação ao exemplo: `break` encerra o laço dos slots, o contexto de laço mais interno nesse ponto. A expectativa vem do contrato Kof, conferido separadamente da saída do reproducer e do resultado de versões anteriores.

### Classification (D-KOF-FIRST Gate 4)

Target divergence — same valid Kof, different behavior across targets

Regressão no alvo JavaScript entre as distribuições 0.6.6 e 0.6.7. A perda do `break` no artefato está demonstrada. A alteração específica responsável continua indeterminada; JVM/JS foram os únicos alvos executados.

### Checklist

- [x] I searched existing issues and this is not a duplicate. Não encontrei equivalente nas buscas de 27/10/2026: `repo:KofLang/Kof4j is:issue break JS` (28 resultados), `repo:KofLang/Kof4j is:issue "for-in" "break"` (17), `repo:KofLang/Kof4j is:issue "0.6.7" "break"` (0), incluindo abertas e fechadas, reconferidas antes desta publicação. Os relatos próximos [#101](https://github.com/KofLang/Kof4j/issues/101), [#587](https://github.com/KofLang/Kof4j/issues/587) e [#962](https://github.com/KofLang/Kof4j/issues/962) tratam, respectivamente, de `return` após guarda com `throw`, escopo de `break` em `switch` e reconstrução de `do-while`.
- [x] I reproduced this against the latest build. Reprodução na distribuição oficial 0.6.7; a consulta de [release mais recente](https://api.github.com/repos/KofLang/Kof4j/releases/latest) em 27/10/2026 também aponta para 0.6.7, SHA `df27d89fc94b56344984ac42579bc8bb40809150`. Não foi compilado um novo `main`.
- [x] The reproducer is valid Kof — I checked [`docs/language-reference/`](https://github.com/KofLang/Kof4j/tree/df27d89fc94b56344984ac42579bc8bb40809150/docs/language-reference) and [`training/anti-patterns/fake-idioms.md`](https://github.com/KofLang/Kof4j/blob/df27d89fc94b56344984ac42579bc8bb40809150/training/anti-patterns/fake-idioms.md), and this is not syntax imported from another language (KOF-first, external-second).
- [x] I read [`docs/philosophy.md`](https://github.com/KofLang/Kof4j/blob/df27d89fc94b56344984ac42579bc8bb40809150/docs/philosophy.md#what-kof-is-not) ("What Kof Is NOT"). This is a deviation from Kof's documented behavior — not a request to import another language/stack's syntax (Java/Kotlin idioms, HTML/CSS into `kof.ui`, framework layers); those are closed with a pointer to the docs, not fixed.

<details>
<summary>Evidências adicionais: instantes intermediários, JavaScript gerado e identidade dos artefatos</summary>

Para conferir também os instantes intermediários, mantenha `Slot` e `Rack` e substitua somente `main()` por esta variante, igualmente executada nas quatro combinações com os mesmos comandos:

```kof
main() {
    var rack = Rack()
    for (var i = 0; i < 36; i++) {
        rack.tick()
        if (rack.steps == 11 || rack.steps == 12 || rack.steps == 24 || rack.steps == 36) {
            println(rack.steps + ":" + rack.slots[0].active + ":" + rack.slots[1].active + ":" + rack.slots[2].active)
        }
    }
}
```

Saída esperada, também observada em 0.6.6/JVM, 0.6.6/JS e 0.6.7/JVM:

```text
11:false:false:false
12:true:false:false
24:true:true:false
36:true:true:true
```

Saída completa de 0.6.7/JS:

```text
11:false:false:false
12:true:true:true
24:true:true:true
36:true:true:true
```

Todas as quatro execuções dessa variante também retornaram 0 e stderr vazio. Os passos 12 e 24 distinguem o defeito. O passo 11 confirma ausência de disparo antes da primeira tentativa; no passo 36, a execução correta também já ocupou os três slots. Observar apenas o estado final esconderia o erro. Nesta redução os slots permanecem ativos, sem movimento ou reciclagem.

Também gerei os módulos JS a partir do programa mínimo original. Para repetir a inspeção, use destinos de saída locais:

```sh
/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/bin/kof build Main.kf --target js --output out-0.6.6
/home/renanfranca/.local/share/kof/kof-0.6.7-linux-x86_64/bin/kof build Main.kf --target js --output out-0.6.7
```

Os dois builds executados retornaram 0; os destinos acima substituem apenas os caminhos absolutos de saída da coleta local. Trecho fiel de `Default.mjs:49`, gerado por 0.6.6:

```javascript
            for (; (_idx < kofListSize(_coll)); _idx = ((_idx + 1) | 0)) {
                _forInVar = kofListGet(_coll, _idx);
                if ((_forInVar.active ? 0 : 1)) {
                    _forInVar.fire();
                    break;
                }
            }
```

Trecho correspondente de `Default.mjs:49`, gerado por 0.6.7:

```javascript
            for (; (_idx < kofListSize(_coll)); _idx = ((_idx + 1) | 0)) {
                _forInVar = kofListGet(_coll, _idx);
                if (((!!(_forInVar.active ? 0 : 1)) !== (!!false))) {
                    _forInVar.fire();
                }
            }
```

A saída 0.6.7 mantém o percurso dos slots e a chamada `fire()`, mas não contém a interrupção desse laço. Isso explica os três slots ativos na mesma tentativa. Não determinei qual alteração do compilador removeu o `break`; não fiz bisect nem estabeleci uma causa em um passe específico.

#### Identidade das distribuições e dos programas

| Distribuição | SHA-256 de `lib/kof.jar` | JDK embutido usado pelo launcher |
| --- | --- | --- |
| 0.6.6 | `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58` | Temurin 25.0.4.1+1 |
| 0.6.7 | `e9940afbb8db4a38f17b57a071fe039602454bdff78e99f8c3c095618489de76` | Temurin 25.0.5+8 |

O hash do jar 0.6.7 coincide com o digest do asset oficial `kof-cli-0.6.7.jar` na [API da release Linux](https://api.github.com/repos/KofLang/Kof4j/releases/tags/kof-0.6.7-linux-x86_64). A release aponta para `df27d89fc94b56344984ac42579bc8bb40809150`. A comparação usa as distribuições completas, cada uma com seu JDK; não isola uma alteração específica do compilador.

SHA-256 dos programas executados:

- Programa mínimo completo: `2b5309215b5bf58ca2d3d897429ba619d780a31984740e43b5530ea2cecfedbc`.
- Variante temporal completa, com as mesmas classes: `6cd1692be594c4926d69656de8a85b62b1b6e90a17673f174730f0ff3341bf42`.

</details>
