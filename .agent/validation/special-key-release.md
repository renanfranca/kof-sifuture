# Aceite da soltura das teclas do especial

Data local: 03/10/2026 (America/Bahia). Revisão de implementação testada: `f2938f3201f210e0bdf1bfcc0b73406b00c0729e`, na branch `background-items-weapons`. O commit deste registro acrescenta apenas documentação. A reexecução final e o CI do head são registrados na descrição do [PR #9](https://github.com/renanfranca/kof-sifuture/pull/9); os [checks do PR](https://github.com/renanfranca/kof-sifuture/pull/9/checks) oferecem os links persistentes para os workflows da entrega.

## Ambiente e procedência

Linux x86_64; launcher `/home/renanfranca/.local/bin/kof`; `kof version` retorna `kof 0.5.0-beta`. `kof info --json` identifica a JVM embarcada Eclipse Adoptium `25.0.4.1`. Chrome `139.0.7258.154`, com Playwright e Pillow. As interações foram automatizadas no navegador real; as capturas foram inspecionadas visualmente pelo agente, sem aceite em dispositivo físico.

O SHA-256 do JAR executado, medido por `sha256sum /home/renanfranca/.local/share/kof/kof-0.5.0-beta-linux-x86_64/lib/kof.jar`, é `78e5ab9b65994889b8e593378aeabfbb6d5d71862e28a96f186085cabe404334`. O pacote local não expõe seu SHA de origem em `kof info`; não se atribui a ele o SHA do checkout consultado. Código, documentação e treinamento foram consultados no checkout Kof `317d9f6b1c3e27032cc955a05f859f6c627d9338`. O workflow de resolução no PR registra separadamente a procedência da distribuição oficial usada pelo CI.

Execução no worker `primary`, `gpt-6.1-sol` / `medium`, chat `01a10488-97a6-7430-8a7c-3ce23ab1cdc8`. Implementação, validação e revisão estrutural compartilham contexto; a revisão não é independente. Sonar, Habit e mutação foram excluídos por ausência de configuração local. Os testes de infraestrutura Python/Bash não foram selecionados neste ciclo de controles.

## Regressões e mecanismo

Antes da correção, `python3 tests/browser_weapons.py` falhou na comparação do foco imediatamente após disparar com `1`, antes de qualquer soltura:

```text
assert special.evaluate("button => button === document.activeElement"), key
AssertionError: 1
```

Depois de corrigir o foco, a regressão de Espaço solto em outro controle ainda falhou na segunda tentativa:

```text
assert status(page)["charges"] == 0, destination
AssertionError: Ativar teclado do jogo
```

A exceção aprovada é **preservar foco até registrar a soltura; depois desabilitar normalmente**. A decisão visual está em [GameControls.kf](../../src/main/kof/sifuture/GameControls.kf#L169):

```kof
    private updateSpecial() {
        var available = game.canSpecial()
        var preserveFocus = specialFocused && (oneHeld || enterHeld || spaceHeld)
        if (available) { special.setStyle(specialAvailableStyle) }
        else { special.setStyle(specialUnavailableStyle) }
        special.setDisabled(!available && !preserveFocus)
    }
```

`preserveFocus` adia somente a desabilitação nativa. A opacidade acompanha a disponibilidade real; `Game.trySpecial()` continua recusando tentativas indisponíveis. Os eventos `focus`/`blur` acompanham o foco do botão. Cada tecla registra seu estado antes de uma possível tentativa; a soltura observada em qualquer controle libera o bloqueio e recalcula a disponibilidade. A última soltura ou o blur termina a exceção imediatamente. Nenhuma tentativa fica pendente e nenhum campo do modelo de armas foi alterado.

O [treinamento de UI](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/idioms/ui.md#L386) descreve os eventos existentes:

> Works on any DOM widget via `.on(type, handler)`.

O [Learn Kof](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/35-kof-ui.md#L191) descreve a aplicação do estilo:

> `setStyle(style)` applies a style to **any DOM widget**, not only `View`:

Os dois estilos são criados na montagem e preservam a geometria. O runtime JS consultado aplica `setDisabled` à propriedade nativa `disabled` e o estilo ao elemento DOM; a prova de foco e soltura foi executada no Chrome, além da compilação JS.

## Validação do checkpoint

Os seis comandos selecionados concluíram com exit 0, coleta completa e nenhum bloqueio. Duração do executor: 56,02 s.

| Comando | Resultado |
| --- | --- |
| `python3 scripts/kof_project.py test --target jvm` | 47 testes; zero falhas |
| `python3 scripts/kof_project.py test --target js` | 47 testes; zero falhas |
| `python3 tests/browser.py` | Menu, Enter/Espaço, confirmação conservadora, pausa, resultado e menu: PASS |
| `python3 tests/browser_controls.py` | Teclado, foco, pointer e touch: PASS |
| `python3 tests/browser_meteor.py` | Movimento, três quadros de impacto e respawn: PASS |
| `python3 tests/browser_weapons.py` | Foco/soltura, evolução, sprites, teclado, dois contatos, pausa e layout: PASS |

Excertos dos comandos Kof em ambos os alvos:

```text
0 failed of 47 tests
1 passed, 0 failed
```

JVM e JS exercitam as regras do modelo. O aceite da interface ocorreu nos quatro percursos de navegador. O percurso de armas usa os controles reais e verifica consumo de carga, foco, estado nativo e opacidade. Para `1`, Enter e Espaço, dispara com duas cargas e solta durante os feixes sem restaurar foco antes da primeira soltura; verifica desabilitação imediata, recuperação da disponibilidade e uma segunda pressão que consome a carga restante.

Excertos de `python3 tests/browser_weapons.py`:

```text
PASS special focus retained until last release, cross-control keyup, simultaneous keys and outside-release lock
PASS key 1 and button keyboard repeat suppression, no queued attempts and native click deduplication
```

Também foram verificados: tecla mantida além do término dos feixes sem repetição; três ordens de última soltura com teclas simultâneas; tentativa recusada durante feixes sem fila; Espaço solto na área do jogo e no direcional; blur desabilitando imediatamente; soltura fora dos controles conservando o bloqueio; origem da pressão limitando a ação; setas + `1` no overlay; confirmação por Enter/Espaço no botão principal e os dois dedos existentes.

## Aparência e limites

Capturas inspecionadas em larguras de 320 e 1200 pixels: Especial focado e indisponível (`0.5`), após soltura/desabilitado e disponível novamente (`1`). Bounding boxes iguais nos três estados confirmaram dimensões de 72 × 64 e posição preservada; o percurso existente verificou separação de 16 pixels e centralização no direcional. A aplicação normal também foi aberta nas duas larguras.

Evidências locais opcionais: `.agent/tmp/special-key-release-red-focus.log`, `.agent/tmp/special-key-release-red-cross-control.log`, `.agent/tmp/special-key-release-red-origin.log`, `.agent/tmp/validation/20261004T014808-qnxo_30k/`, `.agent/tmp/special-key-release/held-{320,1200}.png`, `released-{320,1200}.png` e `available-{320,1200}.png`. Os logs, capturas e ledger não são necessários para compreender os resultados acima e não entram em commits. O registro de revisão estrutural está em `.agent/tmp/special-key-release.review.md`; não foi necessário refatorar a produção.

Este aceite cobre a correção local no Chrome informado. Solturas fora da árvore de controles continuam invisíveis e conservam o bloqueio. Eventos gerais da página, pausa automática e reformulação dos controles ficam para outro ciclo. Não houve merge nem publicação Pages; o site existente não foi usado para comprovar esta correção.
