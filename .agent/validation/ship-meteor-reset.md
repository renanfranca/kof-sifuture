# Aceite do sprite da nave e relançamento dos meteoros

Data: 04/10/2026 (America/Bahia). Código testado e revisado: `c441eb05d80496cc29bc49a5a731888cfdbed839`. Correção na branch `stage-hud-result`, sobre o head anterior `6715fbaf76c30805c861f54abbf6eab978f86ae1`, continuando a entrega no [PR #10](https://github.com/renanfranca/kof-sifuture/pull/10), destinado a main. O commit posterior deste registro acrescenta somente documentação. A entrega repete os nove checks no head final e registra SHA, resultados e links específicos no PR e no ledger. O [workflow da branch](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml?query=branch%3Astage-hud-result) conserva os runs de CI.

## Ambiente e processo

Linux x86_64, Kof `0.5.0-beta` instalado em `/home/renanfranca/.local/share/kof/kof-0.5.0-beta-linux-x86_64`, JVM embarcada Eclipse Adoptium `25.0.4.1`, Node `24.16.0`, Python/Playwright/Pillow e Chrome `139.0.7258.154`. O contrato CI usa o `yq` local `4.54.1` em `/tmp/kof-ci-tools`; esse diretório deve integrar o PATH. Não foi instalado runner ou navegador neste ciclo. O checkout Kof consultado está em `317d9f6b1c3e27032cc955a05f859f6c627d9338`; esse SHA identifica as fontes consultadas, não a origem comprovada do binário instalado.

Worker `primary`, chat `01a106d8-8736-7e73-abcc-3ec6035199aa`, título `sifuture-sprites-primary`, modelo `gpt-6.1-sol`, esforço `medium`. Implementação, validação e revisão compartilham contexto; a revisão não é independente. Sonar, Habit e mutação foram excluídos por ausência de configuração; não são checks aprovados.

## Reprodução e mecanismos

Antes das correções, o comando completo `python3 scripts/kof_project.py test --target jvm` reproduziu o sprite persistente, com os demais casos aprovados:

```text
FAIL finishing with right held restores normal ship while score counts and position freezes: assertion failed
1 failed of 57 tests
```

O segundo defeito foi reproduzido nas suítes completas JVM e JS antes da alteração de Meteor:

```text
FAIL vertical bottom exit uses full historical range and waits inactive with clean animation: assertion failed
1 failed of 58 tests
```

Em [Ship.clearInput](../../src/main/kof/sifuture/game/Ship.kf#L29), a limpeza do comando também invalida seu quadro visual:

```kof
    clearInput() {
        rightFrame = false
        left = false
        right = false
        up = false
        down = false
        lastX = Direction.Left
        lastY = Direction.Up
    }
```

`rightFrame` permanece um campo mutável atualizado pela simulação. Ao encerrar a fase, pausar ou perder foco sem pad ativo, Game usa essa limpeza. GameView consulta o campo e desenha `Middle.png` quando ele é falso. Não depende de um novo passo de movimento no resultado. O [training de classes](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/idioms/classes.md#L56) explica:

> Here the fields are **public and mutable**

O [Learn Kof, capítulo 07](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/07-classes-and-objects.md#L67) reforça:

> To **mutate**, use explicit public fields:

Em [Meteor.resetAfterBottomExit](../../src/main/kof/sifuture/game/Meteor.kf#L34), o caminho de saída usa toda a faixa histórica:

```kof
    private resetAfterBottomExit() {
        Int width = Rules.WORLD_WIDTH
        Int verticalRange = Rules.METEOR_Y_RANGE
        x = rng.int(width)
        y = -rng.int(verticalRange)
        clearAnimation()
    }
```

`METEOR_Y_RANGE` vale 172; o reinício inicial ou após impacto mantém `METEOR_Y_RANGE - METEOR_HEIGHT`, isto é, 154. Ambos consomem somente dois sorteios, X antes de Y, e compartilham a limpeza de quadros, colisão e ativação. Os verticais ficam inativos até o par estar inativo. O limite exclusivo aparece no [runtime JS consultado](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/js/JsRuntimeUiRng.java#L47):

```javascript
export function kofRngInt(bound) {
    if (bound <= 0) return 0;
    return (kofRngNext() >>> 0) % bound;
}
```

O resto é menor que `bound`: após negar o sorteio, a saída produz −171 até 0 e os demais reinícios produzem −153 até 0. A semente 71 demonstra uma saída em `(70, −171)`; 142 demonstra Y = 0. Para reinício/impacto, 276 demonstra −153 e 303 demonstra 0. Quinhentas sementes verificam os limites das duas faixas. A comparação do terceiro sorteio verifica que os caminhos não consomem sorteios extras; a reprodução pelo Game verifica a mesma sequência com a mesma semente.

O [training de stdlib](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/idioms/stdlib.md#L160) recomenda `rng` para determinismo reproduzível; o [Learn Kof, testes](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/23-testing.md#L65) mostra testes com semente e laço. Os exemplos acima são trechos do código corrigido ou runtime consultado; os comportamentos foram executados em JVM e JS, não somente compilados.

## Comandos e resultados

Validação inicial pelo executor determinístico: nove checks selecionados e executados. O primeiro intento aprovou oito e bloqueou o contrato CI com `yq: command not found` (exit 127). Repetiu-se somente esse check no mesmo SHA com `/tmp/kof-ci-tools` no PATH: completo e aprovado. Os nove checks têm evidência válida no checkpoint.

| Comando | Resultado |
| --- | --- |
| `python3 scripts/kof_project.py test --target jvm` | 60/60 casos; 1 arquivo aprovado |
| `python3 scripts/kof_project.py test --target js` | 60/60 casos; 1 arquivo aprovado |
| `python3 tests/browser.py` | menu, confirmações, pausa e resultado aprovados |
| `python3 tests/browser_controls.py` | teclado, foco, pointer e toque aprovados |
| `python3 tests/browser_meteor.py` | movimento, impacto e reinício aprovados |
| `python3 tests/browser_weapons.py` | coleta, vida, armas, especial e controles aprovados |
| `python3 tests/browser_stage.py` | fase, HUD, resultado, sprite, pausa e foco em 320/1200 aprovados |
| `python3 -m unittest discover -s tests -p 'test_kof_project.py'` | 8 casos aprovados; diagnóstico PARSE intencional coberto |
| `bash tests/ci-contract.sh` com `PATH=/tmp/kof-ci-tools:$PATH` | contrato de resolução, integridade, testes, build e publicação aprovado |

Saída em cada alvo, JVM e JS:

```text
0 failed of 60 tests
1 passed, 0 failed
```

O navegador emitiu:

```text
PASS held right restores Middle.png on result entry and release, frozen ship and exact score at both widths
PASS pause and lost canvas focus immediately restore Middle.png at both widths
PASS Chrome 139.0.7258.154 at 320 and 1200 pixels; repaint does not advance simulation
```

O percurso usa Game, GameView e GameControls reais, relógio determinístico e comparação dos pixels opacos dos assets. Em cada largura, foi observado `Middle2.png` durante direita efetiva, depois `Middle.png` já na entrada do resultado e após soltura; X/Y ficaram congelados enquanto o escore contou `0 → 5 → 10 → 15 → 17`. Pausa e blur do canvas também restauraram o quadro normal. Capturas de entrada/soltura nas duas larguras, pausa em 320 e foco em 1200 foram inspecionadas visualmente pelo agente. Os testes do modelo preservam prioridade da última direção oposta, liberação da esquerda e bloqueios de teclado existentes.

A revisão estrutural não encontrou defeito ou risco material que exigisse refactor: invalidação permanece em Ship, sorteios em Meteor, ativação do par em Game e desenho sem mutação em GameView. Nenhuma abstração de produção foi adicionada somente para testes.

## Evidências e limites

Evidências locais opcionais: `.agent/tmp/ship-result-red-jvm.log`, `.agent/tmp/meteor-bottom-red-jvm.log`, `.agent/tmp/meteor-bottom-red-js.log`, `.agent/tmp/ship-meteor-reset.initial-summary.json`, `.agent/tmp/ship-meteor-reset.initial-ci-contract-summary.json`, `.agent/tmp/ship-meteor-reset.structural-review.md` e `.agent/tmp/stage-browser/right-*.png`. Este registro contém os resultados essenciais sem depender desses arquivos.

Checks de CI selecionados: Resolve verified Kof e Kof tests (jvm/js); seus resultados no head final serão vinculados no PR/ledger. A execução local não prova CI ou publicação Pages; Pages ocorre em main após merge. Subchefe, boss final, música, Android e dispositivos físicos continuam fora do aceite. Ciclo de animações, corações, progressão da fase, resultado animado, velocidade e meteoros horizontais foram preservados. A mudança amplia as posições possíveis de saída; não garante que cada sorteio individual fique mais distante do topo.
