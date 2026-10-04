# Aceite da fase, HUD histórico e resultado

Data: 04/10/2026 (America/Bahia). Revisão de implementação testada e revisada: `2d5c4d6e807bd615eea90669ba9b97afb70c1275`, na branch `stage-hud-result`, a partir de `aea3b44ae5097ef9cadd9130cfede72022a2d055`. O commit deste registro acrescenta apenas documentação; o código permanece o checkpoint testado. A entrega reexecuta o inventário no head final e registra seu SHA e links dos runs na descrição do PR e no ledger. Os resultados podem ser consultados no [workflow Kof CI and GitHub Pages](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml?query=branch%3Astage-hud-result) e nos [PRs da branch](https://github.com/renanfranca/kof-sifuture/pulls?q=is%3Apr+head%3Astage-hud-result).

## Ambiente e escopo

Linux x86_64, Python/Playwright/Pillow e Chrome `139.0.7258.154`. Launcher `/home/renanfranca/.local/bin/kof`, Kof `0.5.0-beta`, JVM embarcada Eclipse Adoptium `25.0.4.1`. O pacote instalado não expõe seu SHA de origem; o JAR executado tem SHA-256 `78e5ab9b65994889b8e593378aeabfbb6d5d71862e28a96f186085cabe404334`. Documentação, testes e implementação foram consultados no checkout Kof `317d9f6b1c3e27032cc955a05f859f6c627d9338`; esse SHA não é atribuído ao pacote instalado.

Worker `primary`, chat `01a10698-3ee0-75b3-841c-791dcf9d1e7a`, título `stage-result-primary`, `gpt-6.1-sol`/`medium`. Implementação, validação e revisão compartilham contexto; a revisão não é independente. Sonar, Habit e runner de mutação estão excluídos por ausência de configuração; não são checks aprovados. Publicação Pages acontece em main após merge, fora desta entrega.

## Comandos e resultados no checkpoint

Os nove checks selecionados foram executados uma vez pelo `implement-approved-plan/scripts/run_validation.py` em `initial-validating`: 9 selecionados, 9 executados, 0 bloqueados; todas as coleções completas.

| Comando | Resultado observado |
| --- | --- |
| `python3 scripts/kof_project.py test --target jvm` | 56/56 casos, 1 arquivo aprovado |
| `python3 scripts/kof_project.py test --target js` | 56/56 casos, 1 arquivo aprovado |
| `python3 tests/browser.py` | menu, Enter/Espaço, pausa, resultado animado e retorno aprovados |
| `python3 tests/browser_controls.py` | origem/soltura de teclado, foco, pointer e toque aprovados |
| `python3 tests/browser_meteor.py` | movimento, impactos horizontais e relançamento aprovados |
| `python3 tests/browser_weapons.py` | coleta/vida 4, armas, especial, foco/solturas, multitouch, pausa e camadas do HUD aprovados |
| `python3 tests/browser_stage.py` | HUD, verticais, percurso completo, derrota, contagem, seis fronteiras, redesenho e duas confirmações aprovados em 320/1200 pixels |
| `python3 -m unittest discover -s tests -p 'test_kof_project.py'` | 8 casos aprovados |
| `PATH=/tmp/kof-ci-tools:$PATH bash tests/ci-contract.sh` | contrato de resolução, checks, empacotamento e publicação aprovado |

Saída dos dois comandos Kof, respectivamente nos alvos JVM e JS:

```text
0 failed of 56 tests
1 passed, 0 failed
```

O número 56 conta cenários dentro da suíte; `1 passed` conta seu arquivo. Compilação sem execução não seria suficiente; ambos os comandos executaram as regras. O check Python emite diagnósticos PARSE de propósito: [test_kof_project.py](../../tests/test_kof_project.py#L128) insere `invalid syntax @@@` numa cópia e verifica que build falho não publica saída. Seus oito casos terminaram em `OK`; esses diagnósticos não são defeitos deste checkpoint.

Saída do novo percurso no Chrome:

```text
PASS stage HUD, vertical impacts, full journey, moving result, exact count, boundaries and two confirmations
PASS Chrome 139.0.7258.154 at 320 and 1200 pixels; repaint does not advance simulation
```

## Mecanismos demonstrados

A [posição em Game.kf](../../src/main/kof/sifuture/game/Game.kf#L196) é uma projeção do relógio:

```kof
    stagePosition(): Int {
        var position = 5 + steps / 10
        if (position > Rules.WORLD_WIDTH) { return Rules.WORLD_WIDTH }
        return position
    }
```

Divisão inteira mantém a posição até completar dez passos; `steps = 1710` produz 176. Os testes observam o nono/décimo passo, pausa, explosão/reinício, pontos dos chefes atravessados, fim no extremo direito e reprodução completa da semente. O [training de estado duplicado](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/anti-patterns/duplicate-state.md#L73) orienta:

> If a value can be derived from another, derive it (method or function).

O escore exibido é estado temporal separado do total, enquanto a prontidão é derivada. A [confirmação em Game.kf](../../src/main/kof/sifuture/game/Game.kf#L97) conserva as duas ações:

```kof
        else if (screen == Screen.Result) {
            if (!countComplete()) { displayedScore = score }
            else { screen = Screen.Menu; clearMovement() }
        }
```

Uma confirmação durante a contagem altera apenas o escore exibido; a seguinte muda a tela. Foram observados `0 → 5 → 10 → 15 → 17`, zero já concluído, seis fronteiras (`1499/1500/2199/2200/3299/3300`), Enter mantido e seu clique nativo no botão principal, clique e toque. O bloqueio de Enter exige soltura observada antes de confirmar novamente.

O [training de classes](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/language/classes.md#L11) orienta:

> For **mutable state**, use fields + `constructor(...)`

O [Learn Kof, capítulo 07](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/07-classes-and-objects.md#L67) reforça:

> To **mutate**, use explicit public fields:

`displayedScore` e os campos das entidades pertencem à simulação. `GameView` só os consulta. O resultado avança os efeitos sem chamar coleta/colisões, sem incrementar `steps` e sem diminuir vidas. [Ship.advanceVisual](../../src/main/kof/sifuture/game/Ship.kf#L82) encerra a explosão de forma explícita:

```kof
        if (phase == ShipPhase.Explosion) {
            explosionSteps = explosionSteps + 1
            if (explosionSteps >= Rules.SHIP_EXPLOSION_STEPS) { phase = ShipPhase.Hidden }
        }
```

`Hidden` impede desenho após o décimo quadro (índices 0–9). O percurso de derrota e o término da fase com explosão pendente mantêm vidas, armas, score e progressão, enquanto fundo, meteoros, itens e tiros visuais continuam. Resultado permanece até confirmação.

Os verticais usam os índices 6/7; os horizontais continuam 0–5 e `Meteor()` continua horizontal. Foram verificados desbloqueio acima de 30, queda unitária, quadros 0/1/2 em três passos, espera pelo outro meteoro, saída/relançamento, ordem nave/laser/blaster/especial e prêmio único. A sequência completa de posições, itens, escore e vidas se reproduz ao reiniciar com a mesma semente.

A tentativa inicial de sobrecarregar o construtor foi diferente entre JVM e JS. O emissor consultado [JsClassEmitter.java](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/js/JsClassEmitter.java#L55) emite somente o construtor canônico:

```java
if (method == canonicalCtor) {
    methods.add(lowerConstructor(clazz, method));
}
```

Os 17 casos que falharam no JS passaram após preservar o construtor padrão e configurar os dois verticais por campos no construtor de Game. Não se conclui daí uma regra geral de ausência de sobrecarga em Kof. Nenhum compilador ou código gerado foi alterado.

## Aceite visual e limites

Capturas do Chrome foram inspecionadas pelo agente em 320 e 1200 pixels, na aplicação normal e na fixture com Game/GameView/GameControls reais. Comparações de pixels verificam trilha, miniaturas de uma/duas/três ou mais vidas, dígitos, multiplicador, escore à direita, especial `(50, 21)`, mensagem/contagem centralizadas e impactos verticais. Pausa mantém bitmap e estado; três redesenhos não avançam relógio nem contagem. Feixes passam sob os indicadores. Os 18 assets novos foram comparados byte a byte com `sifuture/res`; NOTICE não mudou.

A revisão estrutural cobriu os contratos alterados e seus colaboradores, sem defeito ou risco material que exigisse refactor de produção. A repetição curta do desbloqueio em Play/Result foi classificada como oportunidade de manutenção, sem alteração neste ciclo; ambos os caminhos pertencem a Game e estão cobertos. Estado da fase/prontidão não foi duplicado; domínio não recebeu dependência UI.

O vídeo histórico não foi aberto; não há aceite visual baseado nele. Fonte e dimensões dos assets sustentam a composição. Não foram aceitos Android, música, chefes, menus completos, controles reformulados, dispositivos físicos ou fullscreen/reescalonamento/centralização global da janela; a composição atual de 176 × 220 foi preservada.

Evidências opcionais: `.agent/tmp/stage-browser/` (capturas); `.agent/tmp/stage-assets.json` (checksums); `.agent/tmp/stage-constructor-gap.md` (observação de construtores); `.agent/tmp/stage-hud-result.structural-review.md` (revisão); `.agent/tmp/stage-hud-result.initial-summary.json` e `.agent/tmp/validation/20261004T113102-0zb8jl0t/` (executor). Este registro contém os resultados essenciais sem exigir esses arquivos locais. O CI selecionado é Resolve verified Kof e Kof tests (jvm/js); resultados finais e links específicos da entrega ficam no PR/ledger, sem autorizar merge.
