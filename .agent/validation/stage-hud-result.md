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

## Combate com o subchefe — ciclo 1 de 3 (04/10/2026)

Esta seção acrescenta o ciclo e preserva os registros anteriores. Os contratos anteriores de passagem sem combate e fim em 1710 passos descrevem a base histórica; o contrato vigente está na [especificação](../specifications/port-sifuture-to-kof.md#approved-browser-cycle-subchief-combat-04102026) e no [EXECPLAN](../../EXECPLAN.md#combate-com-o-subchefe--ciclo-aprovado-de-04102026).

Revisão de código e testes: `6c79a062b1b23765935a22aea539a3968e48cee8`, branch `subchief-combat`, base `95895ee23ac470b798f958994c1514c0f2632ce0`. Produção foi registrada em `5864df41438affb45b6fabd5ad3276fbc2a21549`; o segundo commit reforça somente testes. O commit deste aceite altera documentação. O inventário será repetido no head final e seu SHA/links específicos ficarão no PR e ledger, sem tratar evidência de outro head como final. Referências persistentes: [workflow da branch](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml?query=branch%3Asubchief-combat) e [PRs da branch](https://github.com/renanfranca/kof-sifuture/pulls?q=is%3Apr+head%3Asubchief-combat).

### Ambiente e execução

Linux x86_64; Python, Playwright, Pillow; Chrome `139.0.7258.154`; Kof `0.5.0-beta` em `/home/renanfranca/.local/bin/kof`, JVM embarcada Eclipse Adoptium `25.0.4.1`. Fontes Kof consultadas em `317d9f6b1c3e27032cc955a05f859f6c627d9338`; esse SHA não é atribuído à distribuição instalada, que não o informa. Identidade do JAR: SHA-256 `78e5ab9b65994889b8e593378aeabfbb6d5d71862e28a96f186085cabe404334`.

Worker `primary`, chat `01a1079d-8a58-7f73-a732-acce78ff1b98`, título `sifuture-subchief-primary`, `gpt-6.1-sol`/`medium`. Implementação, validação e revisão compartilham contexto; revisão não independente. Sonar, Habit e runner de mutação excluídos por ausência de configuração, sem alegação de aprovação. CI selecionado: Resolve verified Kof e Kof tests (jvm/js). Pages continua após merge.

| Comando local | Resultado na revisão de código/testes indicada acima |
| --- | --- |
| `python3 scripts/kof_project.py test --target jvm` | 73/73 cenários; 1 arquivo aprovado |
| `python3 scripts/kof_project.py test --target js` | 73/73 cenários; 1 arquivo aprovado |
| `python3 tests/browser.py` | menu, Enter/Espaço, pausa, resultado e retorno aprovados |
| `python3 tests/browser_controls.py` | teclado, foco, pointer e toque aprovados |
| `python3 tests/browser_meteor.py` | movimento, três impactos e relançamento aprovados |
| `python3 tests/browser_weapons.py` | coleta, evolução, especial, solturas, multitouch, pausa e camadas aprovados |
| `python3 tests/browser_stage.py` | fase com combate, verticais, HUD, resultado e duas confirmações aprovados em 320/1200 |
| `python3 tests/browser_subchief.py` | entrada, combate, tiros, especial real, dez quadros, pausa, retomada, derrota e nova partida aprovados em 320/1200 |
| `python3 -m unittest discover -s tests -p 'test_kof_project.py'` | 8 casos, `OK`; diagnósticos PARSE pertencem ao teste de build deliberadamente inválido |
| `PATH=/tmp/kof-ci-tools:$PATH bash tests/ci-contract.sh` | resolução, integridade, comandos dos jobs, empacotamento e publicação aprovados |

Executor `implement-approved-plan/scripts/run_validation.py`: dez selecionados, dez executados, zero bloqueados, todas as coleções completas. O primeiro gate em `5864df4` aprovou 72 cenários e todos os dez checks; a revisão encontrou uma lacuna de cobertura, reforçada no segundo commit, antes de repetir o gate completo com 73 cenários.

Saída de ambos os comandos Kof (JVM e JS):

```text
0 failed of 73 tests
1 passed, 0 failed
```

`73` conta os cenários; `1 passed` conta o arquivo da suíte. Ambos executaram o comportamento, sem confundir compilação com prova de execução.

### Matriz de critérios, origem e evidência

Todos os critérios abaixo usam o SHA de código/testes e os comandos acima. Interações visuais usam Chrome `139.0.7258.154` nas larguras 320 e 1200. A coluna de evidência identifica testes/interações persistentes; os trechos seguintes mostram os resultados esperados realmente verificados. Os exemplos do agente são testes executados, separados das citações históricas.

| Critério | Exemplo e resultado observado | Origem da expectativa | Evidência demonstrada e lacuna |
| --- | --- | --- | --- |
| Entrada e trilha | Passo 829: posição 87, inativo. Passo 830: ativo, posição 89. Combate e 30 passos de explosão mantêm 89; dez passos posteriores levam a 90; encontro não retorna. | `StageCount.java:209–215` e `:276–287`; plano aprovado. | `midpoint enters once…`, `subchief explosion freezes…`, `full stage completes…`; browser observa entrada/retomada. Sem lacuna de regra identificada. |
| Movimento e tiros | Semente repetida reproduz início/destinos; um passo muda os dois eixos em uma unidade. Tentativas 12/24/36 ocupam os três slots; a 48 não sobrescreve o primeiro. Ao liberar o primeiro, a próxima tentativa o reutiliza. Tiros movem quatro unidades. | `Subchief.java:115–130`, `:172–199`, `:298–307`, `:355–362`; `SubchiefShoot.java:60–78`; dimensões 28×26 e 30×4. | `subchief seeded destinations…`, `subchief moves one unit…`; browser compara nave e tiro e observa 1/2/3 slots. Sem lacuna de regra identificada. |
| Dano e invulnerabilidade | Laser 30→29; blaster intacto 30→28/lives 0, parcial 30→29. Contato normal explode nave/retira 1; reinício muda nenhum dos dois. Bordas inclusivas, contato por pontos e golpe simultâneo conservam nave→laser→blaster→especial antes das armas contra meteoros. | `AirShip.java:335–348`, `ShootLaser.java:172–209`, `ShootBlaster.java:163–197`, `GameCanvas.java:208–241`; invulnerabilidade é exceção explicitamente aprovada. | `subchief laser and body…`, `subchief blaster spends…`, `subchief corner geometry…`, `simultaneous fatal contacts…`, `enemy shot historical…`; browser corpo/reinício. Não se usa mera sobreposição de retângulos como oráculo. |
| Especial histórico | Primeiros três contatos: 30→29→27→24. Feixes marcados reaplicam quando outra cor entra; intervalo seis; offscreen limpa marcador. Feixe esgotado ainda marcado reaplica enquanto ativo; fatal encerra dano ao subchefe mas consome todos os marcados. | `AirShipEspecialShoot.java:244–252`, `:308–345`; `AirShipAllShoots.java:331–377`; `AirShip.java:594–602`. | `special subchief markers…`, `marked exhausted special beam…`, `fatal subchief hit…`; browser dispara tecla 1 repetida pelo controle real, compara HUD e pausa. Sem lacuna de regra identificada. |
| Recompensa | lifeTime 30/31/60/61: 600/300/300/150, por corpo/laser/blaster/especial. Quadros e golpes posteriores não repetem prêmio. Permanecem dois itens, avançando de x10000 para 9999, sem reposicionamento ou benefício imediato. | `Subchief.java:157–165`, `:298–307`; `GameCanvas.java:209–237`; `ItemArray.java:62–82` e `Item.java:129–136`. | `fatal subchief hit rewards once…` (quatro fronteiras × quatro armas); browser prêmio 600 estável durante toda explosão. lifeTime conta blocos de 36 passos normais, não segundos. |
| Transições | Pausa congela combate, projéteis, especial e explosão; continuar retoma. Derrota mantém movimento/tiros e explosão sem dano, pontos ou novas perdas. Nova partida retorna a posição 5, resistência 30, relógios zero e projéteis inativos. | Plano aprovado; contrato de resultado já aceito; históricos de restart em `Subchief.java:115–130`. | `defeat during subchief encounter…`, `enemy shot historical…`, `subchief explosion freezes…`; browser controles Pausar/Continuar, derrota, menu e Novo Jogo. Sem lacuna de regra identificada. |
| Apresentação | Dois assets idênticos à fonte; dez sprites de explosão em três passos/quadro, offsets 0/1/4/7/10/16/22/31/40/55 no início dos quadros; HUD sobreposto ao especial. Três redesenhos preservam bitmap e todo estado observado. | `Subchief.java:235–288`; `sifuture/res`; HUD aceito; `GameView.render` somente leitura. | `browser_subchief.py`: pixels, capturas e controles reais em 320/1200; capturas inspecionadas pelo agente. Vídeo histórico indisponível: não há fidelidade visual demonstrada por vídeo. |

### Trechos que sustentam o aceite

Entrada, em [GameJourney.kf](../../src/test/kof/sifuture/game/GameJourney.kf#L1287), executada nos dois alvos:

```kof
    assert(g.stagePosition() == 87 && g.subchief.phase == SubchiefPhase.Inactive)

    g.step()
    assert(g.stagePosition() == 89 && g.subchief.phase == SubchiefPhase.Normal)
```

O contador de passos da partida e o da trilha têm ritmos diferentes durante o encontro. [Game.stagePosition](../../src/main/kof/sifuture/game/Game.kf#L221) deriva a posição de `stageSteps`, evitando guardar outra posição sincronizada. O [training de estado duplicado](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/anti-patterns/duplicate-state.md#L73) orienta:

> If a value can be derived from another, derive it (method or function).

Capacidade cheia, em [GameJourney.kf](../../src/test/kof/sifuture/game/GameJourney.kf#L1332):

```kof
    var shotX = chief.shots[2].x
    var firstShotX = chief.shots[0].x
    for (var i = 0; i < 12; i++) { g.step() }
    assert(chief.shots[2].x == shotX - 48 && chief.shots.size == 3)
    assert(chief.shots[0].x == firstShotX - 48)
```

O primeiro e o terceiro tiros conservam o avanço de 12×4; uma tentativa com capacidade cheia não substitui nenhum deles. O cenário libera o primeiro slot e comprova sua reutilização. O teste de chegada também observa ambos os eixos e a reprodução do novo destino.

Dano e invulnerabilidade, em [GameJourney.kf](../../src/test/kof/sifuture/game/GameJourney.kf#L1363), com omissão explícita das preparações intermediárias:

```kof
    assert(g.subchief.lives == 29 && laser.impact && laser.x == 121 && laser.y == 100)
    assert(!g.meteors[0].collided && g.score == 0)
```

```kof
    assert(g.ship.phase == ShipPhase.Restart && g.subchief.lives == 30)
```

O primeiro trecho mostra o laser consumido pelo subchefe antes de reclamar o meteoro. O segundo demonstra a exceção aprovada: contato corporal no reinício não explode a nave nem retira resistência do subchefe. O novo teste simultâneo observa quais armas permanecem intactas quando uma família anterior produz o golpe fatal.

Especial, em [GameJourney.kf](../../src/test/kof/sifuture/game/GameJourney.kf#L1410):

```kof
    assert(g.subchief.lives == 29 && g.weapons.beams[0].lives == 9)
    assert(g.weapons.beams[1].lives == 10 && g.weapons.beams[2].lives == 10)
    g.step()
    assert(g.subchief.lives == 27 && g.weapons.beams[0].lives == 8 && g.weapons.beams[1].lives == 9)
    g.step()
    assert(g.subchief.lives == 24 && g.weapons.beams[0].lives == 7 && g.weapons.beams[1].lives == 8 && g.weapons.beams[2].lives == 9)
```

O dano 1/2/3 preserva a busca por uma nova cor seguida do consumo de todos os marcadores. A expiração impede reaplicação sem nova entrada, e o cenário separado de esgotamento verifica que resistência zero não apaga antecipadamente o marcador histórico.

Recompensa, em [GameJourney.kf](../../src/test/kof/sifuture/game/GameJourney.kf#L1449):

```kof
    var lifetimes = listOf(30, 31, 60, 61)
    var rewards = listOf(600, 300, 300, 150)
```

O teste aplica o golpe fatal com cada família e percorre os quadros seguintes, verificando estabilidade dos pontos e dos dois itens. A fórmula histórica em `/home/renanfranca/projects/sifuture/src/Subchief.java:157` é:

```java
if(this.lifeTime <= 30) {
    return VALUE*2;
}
if(this.lifeTime <= 60) {
    return VALUE;
}
return VALUE/2;
```

`VALUE = 300`; comparações inclusivas explicam por que 30 ainda vale 600 e 60 ainda vale 300.

Transições, em [GameJourney.kf](../../src/test/kof/sifuture/game/GameJourney.kf#L1554):

```kof
    assert(g.subchief.lives == 1 && g.score == 17 && g.ship.lives == 0 && g.stagePosition() == 89)
    assert(g.steps == steps && g.weapons.level == 3 && g.weapons.charges == 0 && g.displayedScore == 17)
```

O cenário observa que a cena se move durante resultado, enquanto estes valores permanecem estáveis. A perda de carga ocorreu na morte antes da entrada do resultado; não se repete durante a animação. A nova partida limpa encontro, tiros e relógios.

Apresentação e percurso, saída de `python3 tests/browser_subchief.py`:

```text
PASS full seeded encounter journey at 320px: 4228 steps, score 350, position 176
PASS full seeded encounter journey at 1200px: 4228 steps, score 350, position 176
PASS midpoint combat, three shots, invulnerability, real special controls, ten explosion sprites, resumed track, defeat and new game
PASS Chrome 139.0.7258.154 at 320 and 1200 pixels; pause and repaint preserve simulation
```

4228 é o resultado observado da semente 902, não um novo prazo fixo. A fixture usa Game/GameView/GameControls reais e relógio controlado; a aplicação normal também foi montada e capturada em ambas as larguras. Não se atribui esse resultado a dispositivos físicos.

O [idioma de classes](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/idioms/classes.md#L35) orienta:

> for **mutable state** use explicit fields + `constructor(...)`.

O [Learn Kof, capítulo 07](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/07-classes-and-objects.md#L65) reforça:

> To **mutate**, use explicit public fields:

Subchief e seus tiros usam essa forma: os campos são alterados pela simulação; GameView apenas os consulta. A [composição de imagens no training de UI](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/idioms/ui.md) usa:

```kof
c.drawImage(logo, 5, 5)
```

O desenho reaproveita Image/Canvas existentes, sem código host escrito à mão. O Learn Kof UI distingue execução de regra em JVM/JS de desenho efetivo no navegador; o percurso Chrome fornece a prova visual no alvo JS.

### Revisão e limites

Revisão estrutural sobre o código alterado e os colaboradores adjacentes: estado temporal pertence às entidades; prioridade/prêmio pertencem a Game/Weapons; não há campos UI no domínio nem contador duplicado de disponibilidade. Marcadores do especial são estado de protocolo histórico, não cache derivável. O snapshot local `chiefNormal` detecta a transição fatal e protege prêmio único. A ordem de desenho/colisão está coberta por comportamento, sem testes para impor organização interna.

Oportunidades de manutenção: centralizar dimensões/cadências numéricas e extrair o bloco de encontro em Game poderia reduzir repetição; classificados como oportunidades, sem defeito demonstrado e sem refactor de produção neste ciclo. A lacuna de precedência simultânea/capacidade cheia foi encaminhada ao Implementer e corrigida nos testes, repetindo os gates.

Os assets novos foram comparados byte a byte com a fonte: `subchief.png`, SHA-256 `3829891b36a1af47da09297bd4547d29d7708a5b43dca18c5f361aab432ed8d2`; `laser0.png`, SHA-256 `737b3c56bac52c595a60d640bd36ff1cc62c75bacdf597a89ab50b03e08bcace`. NOTICE permanece igual. Dez explosões existentes reutilizadas.

Fonte histórica foi conferida estaticamente; o JAR histórico não foi executado. Vídeo não acessado: fidelidade visual baseada nele permanece aberta. Chefe final, música, Android, menus completos e controles reformulados seguem pendentes. Capturas 320/1200 verificam a composição existente; não fecham a reformulação global de layout.

Evidências locais opcionais: `.agent/tmp/subchief-browser/` (capturas), `.agent/tmp/subchief-assets.json` (hashes), `.agent/tmp/subchief-combat.initial-summary.json` (primeiro gate), `.agent/tmp/subchief-combat.coverage-summary.json` (gate repetido), `.agent/tmp/subchief-combat.final-summary.json` (head final), `.agent/tmp/subchief-combat.structural-review.md` e `.agent/tmp/validation/` (logs/entradas). Resultados essenciais estão registrados aqui; links finais de CI ficam no PR/ledger.

### Avaliação prospectiva em três ciclos

| Momento/achado | Classificação | Correção/antecipação e esforço aproximado |
| --- | --- | --- |
| Executor, antes da entrega: expectativa do tiro em y+9, em vez de y+13 | Expectativa incorreta | Dimensões/fórmula histórica conferidas antes de finalizar movimento; corrigido no teste. Cerca de 1 min. |
| Executor: borda direita inclusiva do laser tratada como exclusão | Expectativa incorreta | Caso limite corrigido com a expressão histórica e deslocamento do passo. Cerca de 1 min. |
| Executor: espera de 20 passos para feixe atingir subchefe móvel | Expectativa incorreta | O destino avançava enquanto o feixe entrava; aguardar 36 passos demonstrou contato. Cerca de 1 min. |
| Executor: leitura imediata do Label da fixture após concluir contagem | Expectativa incorreta | O Label atualiza no relógio da fixture; avançar um passo antes da leitura. Cerca de 1 min. |
| Executor na revisão: prova isolada das armas não demonstrava fatal simultâneo; capacidade cheia não verificava preservação do primeiro slot | Cenário não coberto | Acrescentar precedência com resistências 1–5 e posição do primeiro tiro; código passou sem alteração. Cerca de 2 min de teste/conferência, mais um gate completo de aproximadamente 2 min. |
| Executor: corpo do commit de documentação excedeu 100 caracteres e sequência tentou validar antes do commit | Cenário não coberto na execução do fluxo | Commit recusado antes de Git; validação prematura cancelada e não aceita. Mensagem refluída, sequência passou a abortar em falhas, nova tentativa e gate completo após commit real. Cerca de 2 min. |
| Planejador, depois da entrega: prêmio no passo de incremento de lifeTime (R1) | Cenário não coberto | Reproduzido em JVM/JS: 300 em vez de 600, e 150 em vez de 300. Conferência/reprodução estimada em 2–3 min; correção pendente. |
| Planejador: colisão dos tiros antes/depois de seu avanço (R2) | Requisito esquecido | Ordem temporal histórica não preservada: tiro novo e tiro ainda fora da nave explodem no mesmo passo. Conferência/reprodução estimada em 2–3 min; correção pendente. |
| Planejador: reaplicação em feixe esgotado não reinicia sua animação (R3) | Expectativa incorreta | O teste existente aceita término antecipado em relação ao original. Conferência/reprodução estimada em 2–3 min; correção de produção e expectativa pendente. |
| Ciclos 2 e 3 | Ainda não executados | Registrar aqui achados e esforços quando esses ciclos ocorrerem; sem avaliações antecipadas. |

Preparação adicional de matriz/retrieval: aproximadamente 6–8 min; conferência das fontes e composição visual: 4–6 min; registro de aceite/revisão: 5–7 min; correções de expectativa: aproximadamente 4 min. Estimativas de esforço do executor, não medições de uma comparação controlada. Execução automatizada do primeiro gate mediu 130,92 s; não se confunde duração do comando com esforço humano/agente.

Sinal observado neste ciclo: a revisão detectou uma lacuna antes da entrega e a fechou sem mudar produção. Ainda não há medida de redução de correção posterior: falta a revisão do planejador e os dois próximos ciclos. O total de testes e a ausência de falhas nos gates, isoladamente, não demonstram benefício.

### Conferência posterior do planejador — 04/10/2026

Revisão comparada ao plano aprovado no SHA `44195b03ff1f9bc3a112bb5e1608af21c76bb7f2`, branch `subchief-combat`, [PR #11](https://github.com/renanfranca/kof-sifuture/pull/11). O delta de `6c79a06` para esse head contém somente documentação. Fontes históricas consultadas no SHA `6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f`; consulta estática ao JAR, sem executá-lo. Kof instalado `0.5.0-beta`; checkout consultado `317d9f6b1c3e27032cc955a05f859f6c627d9338`, sem atribuir esse SHA à distribuição instalada.

**Resultado: o ciclo ainda não atende integralmente à preservação histórica aprovada.** Os critérios de recompensa, colisão temporal e esgotamento do especial têm desvios reproduzidos abaixo. As afirmações anteriores de ausência de lacuna descrevem a revisão do executor; esta conferência posterior acrescenta os contrapontos.

Os dez comandos da tabela deste ciclo foram reexecutados no head acima, todos com exit 0: 73/73 regras em JVM e JS, seis percursos Chrome, oito testes Python e contrato CI. O Chrome `139.0.7258.154` repetiu o percurso do subchefe em 320/1200 pixels; a sequência completa terminou em 4228 passos, score 350 e posição 176 em ambas as larguras. Capturas de combate em 320, especial/HUD em 1200 e explosão/quadro 9 em 320 foram inspecionadas. Os dois assets continuam byte a byte iguais à fonte e `/.agent/tmp/` aparece exatamente uma vez no exclude local.

O [run 37217086848](https://github.com/renanfranca/kof-sifuture/actions/runs/37217086848) confirmou `Resolve verified Kof`, `Kof tests (jvm)` e `Kof tests (js)` com SUCCESS no mesmo head. Os jobs Pages foram SKIPPED; não se infere publicação. Vídeo histórico continua como lacuna de evidência.

#### R1 — prêmio reduzido quando o golpe fatal coincide com o incremento do relógio

Em [Game.kf](../../src/main/kof/sifuture/game/Game.kf#L141), `subchief.advance()` ocorre antes do bloco de colisões/recompensa. Em [Subchief.kf](../../src/main/kof/sifuture/game/Subchief.kf#L93):

```kof
if (normalSteps == 36) { lifeTime = lifeTime + 1; normalSteps = 0 }
```

No histórico, a recompensa do golpe aparece em `GameCanvas.java:217–221`, antes de `subchiefUpdate` em `:245`. Trechos separados, na ordem em que aparecem:

```java
this.stagecount.score += this.stagecount.subChief.reward();
```

```java
this.stagecount.subchiefUpdate(g);
```

O golpe muda o subchefe para explosão, portanto `Subchief.fire()` deixa de incrementar o contador nesse passo. Com lifeTime 30/60 e relógio normal 35, o port incrementa para 31/61 antes de avaliar a morte e entrega o prêmio menor. A prova existente fixa lifeTime, mas não exercita simultaneamente a fronteira do relógio.

#### R2 — tiro recém-criado ou ainda fora da nave causa colisão um passo antes

No histórico `GameCanvas.java:241–245`, o contato do tiro é verificado antes de mover/disparar o subchefe. Trechos separados:

```java
this.stagecount.subChief.laserCollision(airship);
```

```java
this.stagecount.subchiefUpdate(g);
```

O port faz o avanço em `Game.kf:141` e só verifica tiros em [Game.kf](../../src/main/kof/sifuture/game/Game.kf#L183):

```kof
for (var shot in subchief.shots) {
    if (shot.touchesShip(ship)) { ship.explode(); shot.active = false; break }
}
```

Exemplos: subchefe em x101/y100, relógio 11 e nave em x40/y100 produzem um tiro em x90 que já explode a nave no mesmo passo. Um tiro existente em x51/y113, fora da nave x0–50, avança a x47 e também explode nesse passo. O original só testa essas posições na chamada seguinte. Preservar a ordem entre famílias de armas não preserva, por si só, a ordem entre contato e movimento/disparo.

#### R3 — reaplicação não reinicia a animação de um feixe esgotado

Em `AirShipEspecialShoot.java:223–238`, conferido também com `javap -classpath /home/renanfranca/projects/sifuture/deployed/Sifuture.jar -c -p AirShipEspecialShoot`:

```java
public void changeToDead() {
    this.state = DEAD;
    this.especialTime = 0;
    this.especialDraw = 0;
}
```

```java
if (this.lives <= 0) {
    changeToDead();
}
```

Cada reaplicação com resistência zero ou negativa reinicia a animação. Em [SpecialBeam.kf](../../src/main/kof/sifuture/game/SpecialBeam.kf#L63), o port reinicia apenas ao alcançar exatamente zero:

```kof
if (lives == 0) { deathSteps = 0 }
```

Com resistência inicial 1, os contatos sucessivos deixam o laranja em 0, -1 e -2. O contador de morte continua, em vez de reiniciar; no sétimo passo o feixe já está inativo, enquanto o histórico ainda o manteria animando e marcado. [GameJourney.kf](../../src/test/kof/sifuture/game/GameJourney.kf#L1628) aceita exatamente esse término antecipado. A consequência inclui remover cedo o marcador que participa de reaplicações posteriores.

#### Provas direcionadas e lacunas restantes

Foram criados somente artefatos locais de diagnóstico com a implementação real copiada pelo helper existente. Comandos executados: `python3 .agent/tmp/planner-subchief-review/run_audit.py --target jvm` e `--target js`. Ambos retornam exit 1: quatro casos em `SubchiefAudit.kf` e um em `SpecialDeathAudit.kf` falham contra as expectativas históricas. Saída essencial, igual nos dois alvos:

```text
lifetime30 score=300 lifetimeAfter=31
lifetime60 score=150 lifetimeAfter=61
newShot shipNormal=false shotActive=false
movingShot shipNormal=false shotX=47
4 failed of 4 tests
afterThirdContact lives=-2 deathSteps=2
afterSevenSteps active=false frame=0
1 failed of 1 tests
```

Os exemplos acima foram executados em JVM e JS; não são resultados somente de compilação. Os arquivos/logs em `.agent/tmp/planner-subchief-review/` são apoio opcional: configuração, expectativas e resultados essenciais estão neste registro. Código da aplicação e suíte versionada permaneceram intactos nesta conferência.

Estimativa de esforço adicional do planejador: aproximadamente 10–15 min para fontes, cinco cenários direcionados, conferência dos checks e registro; sem cronômetro de esforço. Tempo futuro de correção ainda não observado. Os três desvios foram encontrados após a entrega, apesar dos gates existentes verdes. Este ciclo ainda não demonstra redução de trabalho posterior; corrigir R1–R3, ampliar as provas de transição e medir a correção, mantendo ciclos 2/3 pendentes.


### Reparação das divergências R1–R3 — 04/10/2026

Esta seção complementa a conferência posterior sem apagar os registros anteriores. Branch `subchief-combat`, PR #11 existente; base da reparação `44195b03ff1f9bc3a112bb5e1608af21c76bb7f2`. Execução `subchief-repair-primary`, `gpt-6.1-sol`/`medium`, implementação, validação e revisão no mesmo contexto. Ledger original preservado. Fontes históricas: `GameCanvas.java:213–245`, `Subchief.java:157–164,204–206,297–309,367–373`, `AirShipEspecialShoot.java:223–238,445–510`. Consulta estática, sem executar o jogo Java ME nem acessar o vídeo.

As cinco provas foram incorporadas a `GameJourney.kf`, pelo caminho público `Game.step()`, antes de modificar produção. `python3 scripts/kof_project.py test --target jvm` e `--target js` retornaram exit 1 com os mesmos cinco casos falhos em 77 testes:

```text
lifetime30 score=300 lifetimeAfter=31
lifetime60 score=150 lifetimeAfter=61
newShot shipNormal=false shotActive=false
movingShot shipNormal=false shotX=47
FAIL marked exhausted special beam still reapplies when next color enters contact: each nonpositive hit restarts the historical death animation
5 failed of 77 tests
```

Os testes não dependem da existência dos novos métodos internos de avanço. A expectativa anterior de término no sétimo passo foi substituída pelo reinício a cada dano não positivo. Após a correção, os dois alvos executaram 79 casos com `0 failed of 79 tests`. Logs locais opcionais: `.agent/tmp/subchief-repair.red-{jvm,js}.log` e `.agent/tmp/subchief-repair.green-{jvm,js}.log`.

| Critério | Exemplo reproduzível e expectativa histórica | Evidência executada |
|---|---|---|
| R1: relógio/prêmio, quatro famílias | `normalSteps=35`, `lifeTime=30/60`, posição 120/100 e fatal por corpo/laser/blaster/especial: score 600/300, vida/relógio/posição sem avanço, nenhum disparo; prêmio único e quadro zero | Dois testes de fronteira, quatro armas por teste em JVM/JS; oito cenas Chrome por largura, estado real, sprite e dígitos do HUD |
| R1: não fatal | Mesma fronteira e quatro famílias: score zero, relógio 0, `lifeTime+1`, posição 121/101 e tiro x110 | Teste `nonfatal contacts still move fire and increment the lifetime clock at thirty and sixty`, JVM/JS |
| R2: tiro novo | Subchefe 101/100, relógio 11, nave 40/100: primeiro passo tiro x90 e nave normal; seguinte explode e remove tiro | Teste `new enemy shot cannot collide before its historical first update`, JVM/JS; Chrome, sprite real e pausa/repaint entre contatos |
| R2: existente/reutilização | Tiro 51/113, nave x0: primeiro x47 sem colisão, seguinte explosão. Slot 0 liberado por contato retorna com tiro x90; slots 1/2 avançam uma vez para 146/156, sem segunda colisão | Dois testes em JVM/JS, incluindo reutilização; três cenas Chrome por largura |
| R3: reaplicação | Laranja 1→0→−1→−2, `deathSteps=0` após cada dano; ativo/marcado no passo 7 (`deathSteps=4`); contatos nos passos 8/9 reiniciam em −3/−4 | Teste `marked exhausted special beam still reapplies when next color enters contact`, JVM/JS; Chrome, sprites e1/e2 e valores reais |
| R3: seis passos sem novo dano | Após o último dano, mover o subchefe para fora e retirar os outros feixes da fixture: ativo até passo 5, desaparece no sexto e marcador zero | Mesmo teste em JVM/JS, bloqueando novos contatos pela fase; Chrome com posição fora, desenho real até passo 5 e remoção visual no sexto |
| Explosão, trilha, pausa e reinício | Fatal em x120 começa quadro 0; 30 passos/10 quadros, deslocamentos 0/1/4/7/10/16/22/31/40/55, fim x65; trilha 89, retoma depois; pausa congela; reinício não recebe dano | Testes existentes reconciliados com posição anterior ao movimento; Chrome compara todos os dez sprites, pausa/repaint, invulnerabilidade |
| Derrota/resultado e nova partida | Animação permanece sem contato/prêmio; score17/vidas0 e trilha89; nova partida limpa fases, tiros, relógios e score | Teste existente JVM/JS e percurso Chrome de derrota/reinício |

A mudança da posição inicial da explosão de 121 para 120 decorre do golpe antes do movimento, não altera os deslocamentos aceitos. As coordenadas dos testes de borda do laser foram deslocadas um pixel para medir a mesma geometria contra a posição anterior do subchefe; `laser.x=120` agora registra a posição de contato, enquanto o não fatal ainda move o subchefe a121 depois. A nave, armas e meteoros conservam seus próprios contratos de atualização e a prioridade dos contatos.

Percurso preliminar `python3 tests/browser_subchief.py`: Chrome `139.0.7258.154`, larguras 320/1200; oito fatais, três cenários de tiro, reaplicação/limpeza e desenho dos dez quadros. A jornada completa com seed902 terminou em 4515 passos, score350 e posição176 nos dois tamanhos (antes, 4228 passos): a ordem corrigida muda os contatos do encontro e sua duração, mantendo o fim da trilha e o resultado observados. Capturas e logs ficam em `.agent/tmp/subchief-browser/` e `.agent/tmp/subchief-repair.browser-checkpoint2.log`; os gates completos em commits identificados serão registrados abaixo.

Esforço adicional estimado nesta reparação: preparação/retrieval e registro inicial, cerca de 5–7 min; conferência da fonte e das expectativas de movimento/desenho, 3–5 min; correção de código, testes e fixture, cerca de 8–12 min. O primeiro checkpoint de navegador detectou uma máscara de oclusão insuficiente para `laser03.png` (5×25); a máscara passou a usar seus limites reais, sem alterar produção. Esses valores são estimativas de trabalho, separadas das durações automatizadas dos gates.

Classificação preservada: R1, cenário não coberto; R2, requisito esquecido; R3, expectativa incorreta. Os três achados surgiram depois da entrega original e exigiram correção posterior; neste reparo as provas versionadas anteciparam o diagnóstico antes da mudança de produção. Ainda não há comparação controlada que demonstre redução de retrabalho. Ciclos 2/3 permanecem pendentes; vídeo histórico segue como lacuna. Sonar, mutação e Habit excluídos por ausência de configuração, sem alegação de aprovação.


#### Fechamento por commit e comandos — reparação R1–R3

Todas as linhas da matriz de reparação acima correspondem ao SHA de código/suíte/fixture `c9ea48bfad8d8a3420cd168a68f2219c9d058855`. Os dez comandos abaixo foram executados no mesmo SHA, em JVM/JS e Chrome `139.0.7258.154` nas larguras 320/1200. Pelo executor determinístico: gate inicial 151,40 s e repetição final 151,75 s, dez selecionados/executados, zero bloqueados e todas as coletas completas. São execuções reais, não somente compilação.

| Comando | Resultado no SHA acima |
|---|---|
| `python3 scripts/kof_project.py test --target jvm` | `0 failed of 79 tests`; `1 passed, 0 failed` |
| `python3 scripts/kof_project.py test --target js` | `0 failed of 79 tests`; `1 passed, 0 failed` |
| `python3 tests/browser.py` | Menu, confirmação, pausa, resultado e menu |
| `python3 tests/browser_controls.py` | Teclado isolado, foco, pointer e toque |
| `python3 tests/browser_meteor.py` | Movimento, três quadros de impacto, relançamento |
| `python3 tests/browser_weapons.py` | Fundo/coleta/evolução/especial, solturas, multitouch, repetição e HUD |
| `python3 tests/browser_stage.py` | HUD/fase/resultado, verticais e nave, 320/1200 |
| `python3 tests/browser_subchief.py` | Oito fatais por largura; três cenários de tiros; reaplicação/limpeza; sprites, pausa/repaint, invulnerabilidade, derrota/nova partida, 320/1200 |
| `python3 -m unittest discover -s tests -p 'test_kof_project.py'` | `Ran 8 tests`, `OK`; PARSE esperado da entrada deliberadamente inválida |
| `PATH=/tmp/kof-ci-tools:$PATH bash tests/ci-contract.sh` | Exit 0; resolução, integridade, publicação e exclusão de artefatos inválidos |

O [CI do mesmo SHA, run 37223086619](https://github.com/renanfranca/kof-sifuture/actions/runs/37223086619) concluiu com sucesso:

- [Resolve verified Kof](https://github.com/renanfranca/kof-sifuture/actions/runs/37223086619/job/111497172478) — SUCCESS.
- [Kof tests (jvm)](https://github.com/renanfranca/kof-sifuture/actions/runs/37223086619/job/111497528174) — SUCCESS.
- [Kof tests (js)](https://github.com/renanfranca/kof-sifuture/actions/runs/37223086619/job/111497527420) — SUCCESS.

Os dois alvos CI também executaram 79 casos. Build/Publish Pages foram SKIPPED, sem publicação inferida. Matriz, SHA, comandos, resultados, navegador e links dos jobs ficam juntos neste registro versionado. Este complemento só atualiza documentação; código/suíte/fixture permanecem exatamente os do SHA acima.

Em [Game.kf](../../src/main/kof/sifuture/game/Game.kf#L172), os contatos precedem o avanço:

```kof
for (var shot in subchief.shots) {
    if (shot.touchesShip(ship)) { ship.explode(); shot.active = false; break }
}
if (chiefPhaseBeforeContacts == SubchiefPhase.Explosion) { subchief.advanceExplosion() }
subchief.advanceNormal()
subchief.advanceShots()
```

A fase anterior decide se a explosão pode avançar: a recém-iniciada permanece no zero. O avanço normal consulta a fase atual, portanto o fatal impede movimento, relógio e disparo. Os tiros restantes se movem uma vez depois da colisão; os novos aguardam o próximo passo. Em [SpecialBeam.kf](../../src/main/kof/sifuture/game/SpecialBeam.kf#L63):

```kof
if (lives <= 0) { deathSteps = 0 }
```

O teste inclui zero e negativos; cada reaplicação reinicia a contagem. Sem outro dano, o avanço alcança seis e o reset remove feixe/marcador. O estado usa a classe mutável com campos explícitos já existente, segundo a orientação consultada localmente em `kof/training/idioms/classes.md`; as execuções nos alvos demonstram o comportamento atual.

Revisão estrutural no SHA acima, no mesmo contexto da implementação: nenhum defeito ou risco material que justificasse refactor. Ordem temporal é o protocolo aprovado, a fase anterior é um snapshot local ao passo, não há nova duplicação de estado persistente e as partes do avanço são todas usadas em produção. Capturas inspecionadas: prêmio 600 em 320, prêmio 300 em 1200, tiro novo em 320, feixe no sétimo passo em 320, limpeza e quadro 9 em 1200. Comparações automatizadas de pixels cobriram as duas larguras. Assets `subchief.png`/`laser0.png` permanecem idênticos à fonte; exclude local contém `/.agent/tmp/` uma vez.

Evidências locais opcionais: `.agent/tmp/subchief-repair.{initial,final}-summary.json`, `.agent/tmp/subchief-repair.ci.log`, `.agent/tmp/subchief-repair.structural-review.md` e `.agent/tmp/subchief-browser/`. Essenciais e links persistentes estão neste documento, sem depender desses arquivos.

Esforço de fechamento/conferência estimado: 3–5 min para interpretar gates, revisar estrutura/capturas e vincular CI; complemento documental 2–3 min, além dos gates repetidos. O executor marcou o checkpoint pronto antes do complemento; sua máquina de estados não admite reabrir essa fase. O registro terminal foi preservado e o complemento segue em `.agent/tmp/subchief-repair-acceptance.workflow.json`, com o mesmo worker/inventário e repetição completa dos gates. A recuperação não altera produção nem fabrica aprovação.

R1 cenário não coberto, R2 requisito esquecido e R3 expectativa incorreta foram reparados no ciclo atual. Não houve achado adicional de produção após a correção. Tempo automatizado é separado das estimativas de esforço. O sinal de benefício é antecipar desvios/reduzir correção posterior; este ciclo ainda não oferece comparação controlada. Ciclos 2/3, execução Java ME histórica e vídeo permanecem pendentes; os três desvios originais foram encontrados depois da entrega anterior.

A primeira mensagem do complemento excedeu 100 caracteres por linha e o executor recusou o commit antes de Git. A validação iniciada após essa recusa foi cancelada e excluída dos gates; a sequência passou a abortar em falhas antes de iniciar o executor. Mensagem refluída e nova tentativa identificada, sem amend/rebase. Esforço de recuperação estimado em 1–2 min, além da repetição dos gates.

#### Conferência do planejador após a reparação — 04/10/2026

**Resultado: R1–R3 atendem ao planejamento aprovado; nenhum novo desvio de implementação encontrado nesta conferência.** Head testado `bef987ef297474996e1508c2e13843ff94054cd2`, branch `subchief-combat`, [PR #11](https://github.com/renanfranca/kof-sifuture/pull/11) aberto no mesmo SHA. O delta desde `c9ea48bfad8d8a3420cd168a68f2219c9d058855` contém somente `EXECPLAN.md` e este aceite; código, suíte e fixture são os mesmos da reparação.

A matriz de reparação acima foi reconferida com o plano, implementação e fontes originais no SHA `6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f`: `GameCanvas.java:208–245` resolve contatos/prêmios antes de atualizar o subchefe; `Subchief.java:157–164,297–307` define os limites do prêmio e restringe o relógio ao estado normal; `AirShipEspecialShoot.java:223–238` reinicia os contadores após cada dano com resistência não positiva. A consulta foi estática; não se executou o jogo Java ME. Kof instalado `0.5.0-beta`; checkout consultado `317d9f6b1c3e27032cc955a05f859f6c627d9338`, sem atribuir esse SHA à distribuição instalada.

Os dez comandos da tabela de fechamento foram reexecutados no head acima, todos com exit 0: 79/79 cenários em cada alvo, seis percursos Chrome, oito testes de infraestrutura e contrato CI. Os dois comandos adicionais `python3 .agent/tmp/planner-subchief-review/run_audit.py --target jvm` e `--target js` também retornaram exit 0, repetindo as mesmas cinco provas que falhavam na primeira entrega. Saída essencial, igual nos dois alvos:

```text
lifetime30 score=600 lifetimeAfter=30
lifetime60 score=300 lifetimeAfter=60
newShot shipNormal=true shotActive=true
movingShot shipNormal=true shotX=47
0 failed of 4 tests
afterThirdContact lives=-2 deathSteps=0
afterSevenSteps active=true frame=2
0 failed of 1 tests
```

O fatal conserva prêmio e relógio nas duas fronteiras. O primeiro passo dos tiros deixa a nave normal, e o feixe esgotado reinicia a animação após reaplicações, permanecendo ativo no sétimo passo. A suíte versionada também demonstra o contato dos tiros no passo seguinte, as quatro famílias de golpes fatais e não fatais, reutilização do slot, novos reinícios da animação e limpeza seis passos após o último dano. Não depende apenas da contagem de testes.

O percurso `python3 tests/browser_subchief.py`, em Chrome `139.0.7258.154`, repetiu as duas larguras 320/1200 com modelo, desenho e controles reais:

```text
PASS R1 eight fatal boundaries; R2 new/existing/reused shots; R3 reapplication and six-step cleanup at 320px
PASS R1 eight fatal boundaries; R2 new/existing/reused shots; R3 reapplication and six-step cleanup at 1200px
PASS midpoint combat, three shots, invulnerability, real special controls, ten explosion sprites, resumed track, defeat and new game
```

A jornada com seed902 voltou a terminar em 4515 passos, score350 e posição176 nas duas larguras. Capturas do fatal/600 em 320, tiro novo em 320, feixe no sétimo passo em 1200 e limpeza em 1200 foram inspecionadas; comparações automatizadas de sprites cobriram ambas as larguras. Assets `subchief.png` e `laser0.png` continuam byte a byte iguais ao original, NOTICE não mudou, e o exclude local contém `/.agent/tmp/` exatamente uma vez.

O [CI 37224091222](https://github.com/renanfranca/kof-sifuture/actions/runs/37224091222) confirmou o mesmo head testado:

- [Resolve verified Kof](https://github.com/renanfranca/kof-sifuture/actions/runs/37224091222/job/111500056720): SUCCESS.
- [Kof tests (jvm)](https://github.com/renanfranca/kof-sifuture/actions/runs/37224091222/job/111500420620): SUCCESS, `0 failed of 79 tests`.
- [Kof tests (js)](https://github.com/renanfranca/kof-sifuture/actions/runs/37224091222/job/111500420634): SUCCESS, `0 failed of 79 tests`.

Build/Publish Pages foram SKIPPED; não se infere publicação. Logs locais opcionais e resumo estão em `.agent/tmp/planner-subchief-repair-review/`. Os doze comandos, executados com até quatro processos simultâneos, consumiram 52,09 s de tempo automatizado; essa duração não mede esforço de preparação/conferência.

Esforço adicional estimado do planejador: 5–8 min para comparar plano/fontes/código, interpretar provas/gates, inspecionar capturas e registrar resultados. Nenhuma correção adicional de produção foi necessária. R1 continua classificado como cenário não coberto, R2 como requisito esquecido e R3 como expectativa incorreta, todos encontrados depois da entrega original e agora fechados. A ausência de novos achados neste reparo não demonstra, isoladamente, benefício; ciclos 2/3 e medição de redução de correção posterior continuam pendentes. Vídeo histórico permanece como lacuna de evidência visual.

Esta conferência modifica somente os registros versionados; o SHA testado acima identifica a implementação, sem atribuir validação a um futuro commit documental.


### Merge e confirmação do GitHub Pages — 04/10/2026

[PR #11](https://github.com/renanfranca/kof-sifuture/pull/11) integrado em `main` em 04/10/2026 às 19:47:28 UTC, SHA `567f6d032523fe02a0c45eebdbf345f51d70b600`. Merge realizado com `gh pr merge 11 --merge --match-head-commit bef987ef297474996e1508c2e13843ff94054cd2`, após confirmar os checks do head. `gh pr view 11 --json state,mergedAt,mergeCommit,url` retornou `MERGED`; a referência remota de `main` foi conferida no mesmo SHA após a publicação.

[Workflow 37229615413](https://github.com/renanfranca/kof-sifuture/actions/runs/37229615413), disparado pelo merge, concluiu os cinco jobs com SUCCESS no mesmo SHA:

- [Resolve verified Kof](https://github.com/renanfranca/kof-sifuture/actions/runs/37229615413/job/111516332456) — SUCCESS.
- [Kof tests (jvm)](https://github.com/renanfranca/kof-sifuture/actions/runs/37229615413/job/111516767176) — SUCCESS.
- [Kof tests (js)](https://github.com/renanfranca/kof-sifuture/actions/runs/37229615413/job/111516767189) — SUCCESS.
- [Build complete Pages site](https://github.com/renanfranca/kof-sifuture/actions/runs/37229615413/job/111516842216) — SUCCESS.
- [Publish current main](https://github.com/renanfranca/kof-sifuture/actions/runs/37229615413/job/111516914816) — SUCCESS.

Os alvos JVM e JS executaram, cada um, `0 failed of 79 tests`. A publicação utilizou `pages-37229615413-1`. Com `gh run download 37229615413 --name pages-37229615413-1 --dir .agent/tmp/subchief-repair-pages`, o artefato foi recuperado; `python3 .agent/tmp/subchief-repair-pages/check_published.py` comparou SHA-256 de todos os 95 arquivos do artefato com respostas HTTP 200 de [Pages ao vivo](https://renanfranca.github.io/kof-sifuture/). Comparação integral, incluindo HTML, módulos JS e assets; todos iguais byte a byte ao build publicado. Trecho de execução:

```text
PASS all live site files match the exact deployed Pages artifact: 95 files
PASS Chrome 139.0.7258.154 live Pages at 320/1200: start, keyboard, pause/resume, no JS or HTTP errors
```

No Chrome `139.0.7258.154`, em 320/1200, a página real carregou com HTTP 200, iniciou por Novo Jogo, exibiu o Canvas de 176 pixels e o jogo em movimento. A entrada ArrowRight por dois passos foi verificada pelos pixels da nave: Middle.png em x0/y100, Middle2.png em x10/y100 enquanto pressionada, Middle.png em x10/y100 após soltura. Pausa manteve o desenho idêntico por dez passos; Continuar retomou o jogo. Nenhum erro JavaScript ou resposta HTTP de erro nos dois percursos. Capturas das duas larguras foram inspecionadas.

A conferência ao vivo prova distribuição, carregamento, movimento da nave e pausa; não repete o encontro completo/R1–R3 no site remoto. Os 95 arquivos iguais vinculam a publicação ao build do SHA testado, enquanto as provas comportamentais detalhadas do encontro continuam registradas nas seções anteriores. Vídeo histórico e ciclos 2/3 permanecem pendentes.

Evidências locais opcionais em `.agent/tmp/subchief-repair-pages/`: `workflow-status.json`, `workflow.log`, `artifacts.json`, `artifact.tar`, `published-checksums.json`, `acceptance.json`, `acceptance.log` e `live-{320,1200}.png`. Resultado essencial e links persistentes constam acima. A confirmação foi acrescentada preservando as alterações locais da conferência do planejador; nenhum registro anterior foi removido.
