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


## Interromper disparos após a última vida — 05/10/2026

Commit de código, suíte e fixture testado: `ee6d7209755f1d352cf71299942e54bbefb54b7b`.
Base aprovada: `b84398c70e26cce63618586447c35f71d6800466`. Kof `0.5.0-beta` do PATH.

A derrota deixa de criar projéteis quando as vidas chegam a zero. A conclusão da fase
com vidas restantes conserva o disparo visual. Em [Game.kf](../../src/main/kof/sifuture/game/Game.kf#L130):

```kof
ship.advanceVisual()
if (ship.lives > 0 && (ship.phase == ShipPhase.Normal || ship.phase == ShipPhase.Hidden)) { weapons.attemptFire(ship) }
weapons.advance()
```

A conjunção exige vidas positivas e uma das duas fases permitidas. Ela restringe a
criação em `attemptFire`; `advance` permanece fora da condição e conclui tiros e efeitos
ativos. A permissão usa as próprias vidas, conforme
[duplicate-state.md](../../../kof/training/anti-patterns/duplicate-state.md#rule):

> If a value can be derived from another, derive it (method or function).
> Do not store projections.

Não há flag adicional a sincronizar. O idioma de condição vem de
`kof/training/idioms/control-flow.md`; a referência `docs/language-reference/expressions.md`
§5 documenta `&&`/`||`, e `learn/05-control-flow.md` explica condicionais. A implementação
`ExpressionLowerer.java` e `BackendParityTest.parityShortCircuitAndOr` foram consultadas
no checkout Kof; as execuções abaixo demonstram o comportamento desta construção em JVM/JS.

Antes da correção, o teste ampliado falhou por assertion nos dois alvos, com a produção
original e apenas a regressão adicionada. Comandos `python3 scripts/kof_project.py test
--target jvm` e `--target js`:

```text
FAIL defeat ends explosion without new projectiles or another loss at every weapon level: assertion failed
1 failed of 85 tests
```

Após a correção, [GameJourney.kf](../../src/test/kof/sifuture/game/GameJourney.kf#L1278)
verifica os critérios separadamente por `Game.step()`:

| Critério | Evidência e resultado no commit testado |
|---|---|
| Nenhum novo disparo | Uma vida, explosão 29, armas inicialmente inativas, cadência 12; níveis 0–3, incluindo nível 2 com seis tentativas. Todos os lasers, blaster e feixes inativos na entrada e antes/depois de cada um dos 100 passos. Score 5, vidas 0 e relógio da partida preservados. |
| Tiros existentes concluem | Três lasers, blaster e três feixes permanecem ativos na entrada; primeiro passo do resultado move lasers/blaster/feixes externos +5 e feixe central +6. Todos terminam até 170 passos e permanecem inativos nos 52 seguintes, verificados em cada passo. |
| Efeitos concluem | Impacto de laser ativo na entrada e inativo após 1 passo. Blaster esgotado com quadros intermediários ativo até o passo 3, inativo no 4. Feixe esgotado com quadros 1/2 ativo até o passo 5, inativo no 6. |
| Conclusão da fase preservada | Teste existente conserva vidas, cargas, evolução, escore, cenário e disparos visuais com a nave oculta. Chrome confirma laser/blaster ativos após a conclusão. |
| Reinício | Jornada existente retorna ao menu, inicia partida e restaura três vidas/escore zero. Piscar de 45 passos, nenhum laser nos 12 seguintes e laser no 13º; confirmado também no Chrome. |

Gate inicial, com coleta completa e exit 0 para os dez comandos:

| Comando | Resultado |
|---|---|
| `python3 scripts/kof_project.py test --target jvm` | `0 failed of 87 tests`; `1 passed, 0 failed` |
| `python3 scripts/kof_project.py test --target js` | `0 failed of 87 tests`; `1 passed, 0 failed` |
| `python3 tests/browser_stage.py` | Fase/HUD/resultado, disparos, efeitos, contagem, retorno/reinício; Chrome 139.0.7258.154, 320/1200 |
| `python3 tests/browser_weapons.py` | Evolução, especial, teclado, solturas, seis ordens de multitouch, HUD |
| `python3 tests/browser_subchief.py` | Combate, tiros existentes/novos, especiais, explosão, pausa, derrota/reinício; 4515 passos, score 350, posição 176 em 320/1200 |
| `python3 tests/browser.py` | Menu, Enter/Espaço, confirmação, pausa, resultado e retorno |
| `python3 tests/browser_controls.py` | Teclado, foco, pointer, toque simultâneo, drag e cancelamento |
| `python3 tests/browser_meteor.py` | Movimento, três quadros de impacto e relançamento |
| `python3 -m unittest discover -s tests -p 'test_kof_project.py'` | `Ran 8 tests`; `OK`; PARSE pertence à entrada deliberadamente inválida |
| `PATH=/tmp/kof-ci-tools:$PATH bash tests/ci-contract.sh` | Resolução/integridade, workflow e publicação sob lock; exit 0 |

O primeiro gate executou 10 checks em 172,25 s: nove passaram, e o contrato CI parou
com exit 127 por `yq` fora do PATH. O `yq v4.54.1` já existente em `/tmp/kof-ci-tools`
foi disponibilizado por PATH; o executor repetiu apenas esse check, que passou em 17,45 s
no mesmo SHA. Nenhuma instalação ou alteração de produção foi necessária. O gate final
no SHA `68f760b145c1153f55af0a13b967e3b67410101d` repetiu os dez comandos com esse PATH:
10/10 aprovados em 181,74 s, zero bloqueados e todas as coletas completas. JVM/JS 87/87;
seis percursos Chrome, oito testes Python e contrato CI com exit 0.

Trecho de `python3 tests/browser_stage.py`:

```text
PASS defeat projectiles finish without respawn, effects finish at 1/4/6 steps, and restart restores fire
PASS Chrome 139.0.7258.154 at 320 and 1200 pixels; repaint does not advance simulation
```

A fixture [stage.kf](../../tests/stage.kf) usa modelo/desenho/controles reais. Os disparos
já lançados são posicionados em faixas visíveis apenas na fixture; a suíte do modelo
conserva as coordenadas originais de lançamento. Pixels de lasers/blaster/três feixes
são comparados na entrada e após movimento. Os efeitos são comparados em todos os
quadros; `ylwBlaster07.png` é semitransparente, comparado por composição sobre o fundo
real com tolerância de um valor por canal para arredondamento. A atividade de todos os
slots complementa as capturas e impede considerar uma comparação sem amostras como prova.

As primeiras tentativas de ampliar o percurso expuseram label atualizada apenas no tick,
sobreposição do texto de resultado e ausência de pixels opacos no último quadro do blaster.
O teste passou após esperar o tick, reposicionar efeitos e verificar composição alfa;
essas tentativas foram preservadas nos logs locais. Foram inspecionadas capturas de entrada
dos disparos (320), blaster semitransparente (1200), efeitos terminados (320) e disparos
terminados (1200). Esta aceitação é automatizada em Chrome de desktop nas duas larguras;
não equivale a uma interação manual em Android.

Revisão estrutural no mesmo contexto da implementação: sem defeito ou risco material que
justificasse refactor. Não há nova API, tipo ou estado persistente; autorização e avanço
continuam com responsabilidades distintas. Assertions conferidas por critério. Sonar,
mutation runner e Habit excluídos por ausência de configuração, sem alegar execução verde.

O [PR #13](https://github.com/renanfranca/kof-sifuture/pull/13) está aberto. O
[CI 37357041630](https://github.com/renanfranca/kof-sifuture/actions/runs/37357041630)
concluiu com sucesso no mesmo SHA `68f760b145c1153f55af0a13b967e3b67410101d` do gate final:

| Check CI | Resultado e link persistente |
|---|---|
| Resolve verified Kof | [SUCCESS](https://github.com/renanfranca/kof-sifuture/actions/runs/37357041630/job/111921974128) |
| Kof tests (jvm) | [SUCCESS, 87/87](https://github.com/renanfranca/kof-sifuture/actions/runs/37357041630/job/111922707741) |
| Kof tests (js) | [SUCCESS, 87/87](https://github.com/renanfranca/kof-sifuture/actions/runs/37357041630/job/111922707767) |

Trecho dos logs de `Run complete Kof suite`, igual em JVM/JS:

```text
0 failed of 87 tests
1 passed, 0 failed
```

Build/Publish Pages foram SKIPPED, conforme o workflow para PR; não houve publicação.
Este complemento só incorpora evidência disponível, sem alterar produção, suíte ou fixture.
Ele repetirá os gates locais/CI antes da entrega; os resultados do novo head documental
ficarão no ledger e na descrição do PR. Nenhum critério deste ajuste ficou sem prova.
Lacunas gerais do port, incluindo vídeo histórico e aceitação Android, permanecem fora
deste ajuste.
Evidências locais opcionais: `.agent/tmp/sifuture-defeat.{red-jvm,red-js}.log`,
`.agent/tmp/sifuture-defeat.{initial-summary,initial-ci-recheck}.json`,
`.agent/tmp/sifuture-defeat.structural-review.md`, `.agent/tmp/sifuture-defeat.ci-first.log`,
`.agent/tmp/sifuture-defeat.final-summary.json`, `.agent/tmp/stage-browser/` e
`.agent/tmp/validation/`. Os resultados essenciais estão acima, sem depender desses arquivos.

## Boss final — 06/10/2026

Execução aprovada no chat `sifuture-boss-primary`, worker `primary`, modelo `gpt-6.1-sol` / `medium`; implementação, validação e revisão compartilham contexto. Base `8f8f0710c3d440888aec27226e1ee87d25c54d97`; branch `sifuture-boss`. Fontes históricas consultadas diretamente em `6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f`, sem executar o JAR. Checkout Kof consultado: `317d9f6b1c3e27032cc955a05f859f6c627d9338`.

Compilador executado: instalação Linux Kof `0.5.0-beta`, JVM embarcada Eclipse Adoptium `25.0.4.1`. `kof info --json` não informa commit do pacote; sua identidade verificável inclui SHA-256 do `lib/kof.jar`: `78e5ab9b65994889b8e593378aeabfbb6d5d71862e28a96f186085cabe404334`. Não atribuir o SHA do checkout consultado ao binário instalado. Chrome `139.0.7258.154`, Python 3, Playwright e Pillow; yq `4.54.1` preparado com autorização em `.agent/tmp/tools/yq` para `tests/ci-contract.sh`.

### Auditoria das expectativas (separada das assertions)

As expectativas foram relidas contra `StageCount.java`, `BosStage1.java`, `BosStage1AllShoots.java`, `BosStage1Shoot1/2.java`, `AirShip.java`, `ShootLaser.java`, `ShootBlaster.java`, `AirShipEspecialShoot.java` e `GameCanvas.java`. Dimensões foram obtidas dos PNGs: boss 40 × 51, tiro normal 40 × 25, preparação especial 15 × 26, especial final 48 × 26. Isso produz spawn/destino y 30–168, destino x 88–135, tiro normal x −10/y +0 e especial x −3/y +38.

O quarto disparo contado é uma tentativa, inclusive com os slots ocupados; o gatilho histórico fica ligado entre a quarta e a quinta tentativa e desliga na quinta, mesmo com slots ocupados. Níveis 2/3 exigem esse gatilho; nível 4 depende apenas do relógio anterior >4. O relógio anterior >10 do nível 2 não pode ser substituído pelo posterior ao incremento. Evolução de arma não reinicia esse relógio; os `if` históricos permitem atravessar vários níveis em um contato.

Para explosão, o desenho histórico usa o quadro atual e depois desloca/incrementa. Separando atualização e desenho, a entrada mostra quadro 0 na posição depois do movimento fatal, e a atualização seguinte aplica seu deslocamento de −1 antes de mostrar quadro 1. Os deslocamentos acumulados nos passos 1–27 são `1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,22,25,28,31,34,37,40,45,50,55,60,65`. Quadro 9 ocupa 25–27; o passo 28 encerra. Uma expectativa inicial de deslocamento aplicava −2 um passo cedo; foi corrigida pela releitura dos quadros históricos, sem alterar o modelo para satisfazê-la.

Exceção aprovada: o contato corporal exige nave normal; durante reinício invulnerável não muda nenhuma entidade. Continua restrito ao boss normal, sem evolução de ataque. A geometria histórica impossível do terceiro termo corporal (`y >= boss.y` e `y + altura <= boss.y`) não acrescenta área de contato para altura positiva. Laser e blaster usam seu ponto direito; especial do jogador também usa o ponto central vertical do boss.

### Auditoria das assertions e evidência por critério

Os cenários novos foram acrescentados à suíte comportamental existente por `Game.start/step`, com colaboradores reais. Casos incluem limites exatos e vizinhos, resistência restante do blaster e sua exaustão, prioridade simultânea, reaplicação de feixes esgotados, posições anteriores ao movimento/disparo, contagem com slots ocupados e reset. Comparações dos slots ocupados exigem posições exatas, evitando que um relançamento indevido passasse apenas porque o tiro estava à esquerda. A fixture de partida completa passou de 100 vidas/10000 passos máximos para 1000/30000, permitindo concluir o combate mais longo; isso não altera as regras do jogo.

| Critério | Procedimento / assertion | Observação inicial |
|---|---|---|
| Entrada e trilha | Caso `final encounter enters…`; `boss explosion…resumes 290 steps`; `browser_boss.py` marcador e sprite | Entrada 146→147; congelamento; 289 passos em 175/Play; 290º em 176/Result. |
| Movimento e fases | Spawn/destino reproduzidos com seed; chegada por eixo; fronteiras 80/70/45/20 e vizinhos; corpo/fúria/frenesi/reinício; pixels bos/bos1/bos2 | Campos/destinos nos intervalos; movimento +1 por eixo; fúria 44, frenesi 19; corpo não evolui; reinício sem dano. |
| Cadência e capacidade | Cinco intervalos, primeiro slot livre, quarta tentativa e posições exatas com ocupação; relógio anterior >10/>4; seis quadros de preparação | 13/31/31/24/24; um/dois slots; quarta tentativa disponibiliza gatilho; quadro 6 somente após 18 avanços de preparação. |
| Colisões | Bordas inclusive/vizinha; corpo→laser→blaster→especial; centro do feixe; meteoro absorvido; tiro novo/existente/reutilizado; Chrome 5→6 | Um prêmio; blaster esgotado não aplica dano; absorção sem dano/pontos e sem segunda movimentação; tiros aguardam próximo passo. |
| Prêmio | Quatro famílias × lifeTime 30/31/60/61/120/121, clock 35 e tiro devido; score e sprites HUD no Chrome | 1650/1100/1100/550/550/275; relógio/fire congelados no golpe fatal; movimento fatal preservado e prêmio único. |
| Explosão | Todos os passos 0–28 e offsets explícitos; sprites Chrome em cada passo, pausa/redesenhos; remoção e retomada | Quadro zero na entrada; um/três passos; quadro 9 em 25–27; inatividade/limpeza em 28; capturas 320/1200 inspecionadas. |
| Encerramento/reinício | Derrota com chefe ativo; projéteis existentes terminam, nenhum novo da nave; resultado com vidas; confirmações e mesma seed | Score/vidas estáveis em derrota; resultado com tiro visual e duas confirmações; replay seed 909: 15272 passos, score 825 em ambas as larguras. |

Provas de desenvolvimento no delta sobre a base: `python3 scripts/kof_project.py test --target jvm`: `0 failed of 103 tests`, `1 passed, 0 failed`. Checkpoints JS intermediários também passaram. `python3 tests/browser_boss.py` terminou com exit 0 nas duas larguras, usando modelo, desenho e controles reais. As quatorze imagens copiadas foram comparadas byte a byte com o histórico; o inventário SHA-256 é evidência local opcional em `.agent/tmp/boss-browser/asset-sha256.txt`. `NOTICE` foi preservado. Capturas opcionais em `.agent/tmp/boss-browser/`: normal, fury, frenzy, shots, special, absorbed, explosion0, explosion-step1/25/27, defeat e result em 320/1200.

### Gates e limites

Validação completa do commit, revisão estrutural e CI ainda serão registrados abaixo. Sonar, Habit e mutação ficam excluídos por ausência de configuração; não foram aprovados artificialmente. Touch do percurso é simulado no Chrome; Android real permanece pendente. Comparação visual com o vídeo histórico, música, menus completos e apresentação integral continuam pendentes. Este aceite não encerra a v1.

Gate inicial no commit `980d0fdf91535e83e7702a28f8855bc5d66e9919`: 11 checks executados, dez aprovados e um bloqueado. JVM/JS: 103 testes cada; seis percursos Chrome, oito testes Python e contrato CI saíram com exit 0. `browser_stage.py` falhou em sua fixture Full journey, ainda limitada a 100 vidas/10000 passos antes do término do novo boss. A correção amplia o orçamento da fixture para 1000/30000 e conserva as assertions de 175→176/resultado; nenhuma regra foi alterada. Evidência local opcional: `.agent/tmp/validation/20261006T142614-82n7i_ha/summary.json`.

Gate inicial corrigido no SHA `2a594f863aca62b824fea25fb83ffd37140bb292`: os onze comandos selecionados terminaram com exit 0 em 212,32 s; zero bloqueados, coleta completa. JVM/JS 103/103, sete percursos Chrome nas duas larguras, oito testes Python e contrato CI. Os diagnósticos de compilação inválida no teste Python são casos negativos esperados; o resultado é `Ran 8 tests` / `OK`. Evidência local opcional: `.agent/tmp/validation/20261006T143118-dp26zyle/summary.json`.

Trecho de cada comando de regras (`--target jvm` e `--target js`):

```text
0 failed of 103 tests
1 passed, 0 failed
```

Trecho de `python3 tests/browser_boss.py`:

```text
PASS boss entry, phases, shots, special, damage, 28-step explosion, pause, result and seeded replay at 320px; 15272 steps, score 825
PASS boss entry, phases, shots, special, damage, 28-step explosion, pause, result and seeded replay at 1200px; 15272 steps, score 825
```

Revisão estrutural no SHA acima, compartilhando contexto: sem defeito ou risco material que justificasse refactor. O snapshot local de fase anterior explicita a ordem fatal/explosão; contadores pertencem ao ciclo das entidades e resetam; desenho não muta modelo; armamento e projéteis têm responsabilidades próprias. Repetir dimensões históricas fixas nas geometrias é oportunidade futura de manutenção, protegida pelos casos exatos de borda; não há troca de asset neste ciclo. Revisão local opcional: `.agent/tmp/sifuture-boss.structural-review.md`.

A releitura adicional de `BosStage1AllShoots.java:218–224` antes da entrega encontrou o `else` que desliga o gatilho nas tentativas não múltiplas de quatro. A primeira auditoria havia registrado sua permanência sem limite incorretamente. Uma assertion pela quinta tentativa falhou em JVM (`1 failed of 103 tests`) antes da correção. Foi acrescentado o ramo de desligamento, conservando a atividade dos tiros ocupados e a condição anterior ao incremento. O gate final iniciado em `562ef2e` foi interrompido e invalidado; seus resultados parciais não provam o código corrigido. Evidência local opcional: `.agent/tmp/boss-fifth-attempt-red-jvm.log`.

Outra conferência encontrou o primeiro quadro do especial encurtado pelo incremento no nascimento. O contrato exige seis quadros por três passos; `BosStage1Shoot2.java:141–156` desenha o quadro atual antes de incrementar seu contador. A prova pela entrada real de disparo passou a observar cada um dos 18 passos, com quadro esperado `passo / 3`, posição imóvel e movimento somente no passo seguinte ao quadro 6. Essa assertion falhou em JVM antes do reparo (`1 failed of 103 tests`). O avanço distingue especial já ativo do recém-lançado usando snapshot local, preservando avanço de tiros normais e prioridade de contatos. Chrome compara os sprites em todos os 18 passos. O gate `f3f2531` executou 11/11 comandos com exit 0, mas foi bloqueado pela lacuna de assertion; nenhum gate antigo é tratado como prova atual. Evidência local opcional: `.agent/tmp/boss-special-birth-red-jvm.log`.

Checkpoint após o reparo de nascimento: JVM/JS `0 failed of 103 tests`, `1 passed, 0 failed`; `browser_boss.py` exit 0 em 320/1200. Replay seed 909 do modelo corrigido: 14234 passos, score 820 nas duas larguras (substitui os 15272/825 observados antes do reparo). A igualdade entre duas partidas completas permanece verificada; não se trata de valor histórico fixado arbitrariamente. Capturas regeneradas no mesmo diretório opcional.

Gate inicial atual no SHA `052fc67b375bb6c9520bc6449397ccb5a24bb577`: onze comandos completos com exit 0 em 218,14 s, zero bloqueados. JVM/JS 103 testes cada; sete percursos Chrome, oito testes Python e contrato CI. Revisão complementar no mesmo SHA: o snapshot `existingSpecial` é local ao passo, passa explicitamente para o avanço e não retém estado redundante entre chamadas; conserva slots já ativos e a duração inicial. Sem refactor adicional. Evidência local opcional: `.agent/tmp/validation/20261006T144534-yx8t8boz/summary.json`.

Trecho atual de `python3 tests/browser_boss.py`:

```text
PASS boss entry, phases, shots, special, damage, 28-step explosion, pause, result and seeded replay at 320px; 14234 steps, score 820
PASS boss entry, phases, shots, special, damage, 28-step explosion, pause, result and seeded replay at 1200px; 14234 steps, score 820
```

O [PR #14](https://github.com/renanfranca/kof-sifuture/pull/14) foi aberto pronto para revisão no SHA `36695c7cf8f414a492a45101569af068ece09c98`. Gate final local nesse SHA: onze comandos com exit 0, coleta completa e zero bloqueados em 222,29 s; JVM/JS 103 testes cada, sete percursos Chrome em 320/1200, oito testes Python e contrato CI. Evidência local opcional: `.agent/tmp/validation/20261006T145009-2g4zknjx/summary.json`.

O [workflow CI](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml) não havia criado execução para o primeiro head quando este complemento foi preparado. Checks Resolve verified Kof / Kof tests (jvm/js) permanecem pendentes, sem atribuir aprovação local ao GitHub. O PR foi confirmado OPEN, não draft e mergeável; workflow active e Actions habilitado. O complemento documental repete os gates antes da atualização do PR. Links de execução serão incorporados quando disponíveis.

O [CI 37483308217](https://github.com/renanfranca/kof-sifuture/actions/runs/37483308217) terminou SUCCESS para o head `36695c7cf8f414a492a45101569af068ece09c98`. O checkout efetivamente testado foi o merge de validação do PR `384b3ce35bed6dc1fe5c86dc87772be98504576a`, registrado no manifest como `sifuture_sha`; a base é `8f8f0710c3d440888aec27226e1ee87d25c54d97`.

| Check CI | Resultado e link persistente |
|---|---|
| Resolve verified Kof | [SUCCESS](https://github.com/renanfranca/kof-sifuture/actions/runs/37483308217/job/112336824839) |
| Kof tests (jvm) | [SUCCESS, 103/103](https://github.com/renanfranca/kof-sifuture/actions/runs/37483308217/job/112337704693) |
| Kof tests (js) | [SUCCESS, 103/103](https://github.com/renanfranca/kof-sifuture/actions/runs/37483308217/job/112337704724) |

Trecho dos dois jobs `Run complete Kof suite`:

```text
0 failed of 103 tests
1 passed, 0 failed
```

O manifest do resolve verifica Kof `0.5.0-beta`, tag `kof-0.5.0-beta-linux-x86_64`, commit de origem `317d9f6b1c3e27032cc955a05f859f6c627d9338`, arquivo `kof-0.5.0-beta-linux-x86_64.tar.gz` SHA-256 `f93f02eb62af584ea49ffb44efdbf54f970bdb9570f16fdc48ccc28242798ca9`. Ambos os jobs instalaram a mesma distribuição e usaram a JVM embarcada `25.0.4.1`. A identidade CI é separada do hash do JAR instalado localmente. Build/Publish Pages foram SKIPPED por ser PR; não houve publicação.

Este complemento consolida links disponíveis antes do último commit e repete os gates locais/CI no novo head antes da entrega. Resultados atuais ficarão no ledger e na descrição do PR; os links acima conservam a evidência exata do SHA indicado. Não há critério local do boss sem prova; vídeo histórico e Android real permanecem pendentes. Logs CI opcionais em `.agent/tmp/boss-ci-first.log`.

### Conferência do planejador após a implementação — 06/10/2026

Comparação solicitada pelo usuário no head `b1989d082952aad16eef9e336a649630d1dbd482`, branch `sifuture-boss`, inicialmente limpa. O contrato comparado é o ciclo final do [EXECPLAN](../../EXECPLAN.md#próximo-ciclo-boss-final-de-sifuture) e a [especificação aprovada](../specifications/port-sifuture-to-kof.md#approved-browser-cycle-final-boss-06-october-2026). Não foi identificado desvio funcional do recorte aprovado. Esta conferência não altera produção ou testes versionados; acrescenta somente registros, sem commit ou publicação.

A correção das expectativas foi conferida separadamente da suficiência das assertions, como exige o plano preparado com `plan-behavioral-acceptance`. Fonte histórica permanece em `6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f`, checkout limpo: `StageCount`, `BosStage1`, `BosStage1AllShoots`, seus dois projéteis, `AirShip`, `ShootLaser`, `ShootBlaster`, `AirShipEspecialShoot`, `AirShipAllShoots` e `GameCanvas`. Foram relidos os ramos de entrada, movimento, evolução, geometria, prioridade, preparação e explosão; o JAR histórico não foi executado. A exceção de contato corporal durante reinício invulnerável permanece conforme a decisão aprovada.

| Critério do plano | Evidência inspecionada nesta conferência | Resultado observado |
|---|---|---|
| Entrada e trilha | `StageCount.java:180,276`; `GameJourney.kf:2123,2317`; `browser_boss.py:53,180` | 146→147 uma vez; trilha suspensa; 289 passos após explosão ainda em Play/175, 290º em Result/176. |
| Estado, movimento e evolução | `BosStage1.java:128,187,391`; `GameJourney.kf:2140,2213,2273,2556` | Resistência 100; spawn/destinos nos intervalos; movimento por eixo e no golpe fatal; limiares estritos 80/70/45/20; corpo não evolui; reinício não causa dano. |
| Cadência e capacidade | `BosStage1AllShoots.java:78,200`; `GameJourney.kf:2181,2238`; `browser_boss.py:82,99` | 13/31/31/24/24; um/dois slots; relógio preservado; quarta tentativa liga gatilho, quinta desliga inclusive com slots ocupados; seis quadros de três passos, movimento somente no quadro 6. |
| Colisões | `GameCanvas.java:158`; geometrias históricas dos projéteis; `GameJourney.kf:2348,2396,2426,2489,2511` | Prioridade preservada; tiros novos/reutilizados aguardam próximo passo; centro vertical do especial; reaplicação e limpeza em seis passos; absorção sem dano/pontos e sem segundo avanço; verticais existentes e itens continuam. |
| Prêmio e golpe fatal | `BosStage1.java:170,376`; `GameJourney.kf:2291`; `browser_boss.py:157` | Quatro famílias de dano × seis fronteiras: 1650/1100/1100/550/550/275; prêmio único; relógios/disparo não avançam; âncora após movimento fatal. |
| Explosão e desenho | `BosStage1.java:311`; `GameJourney.kf:2317,2464`; `browser_boss.py:168`; `GameView.kf:99` | Quadro 0 por um passo, demais por três; quadro 9 em 25–27; limpeza em 28; offsets históricos; fúria/frenesi corretos; pausa e três redesenhos mantêm estado e pixels. |
| Resultado e reinício | `GameJourney.kf:2527`; `browser_boss.py:180,196,206`; jornadas anteriores | Derrota anima com score/vidas/contatos encerrados; projéteis da nave terminam; resultado com vidas mantém tiro visual e duas confirmações; nova partida limpa estado; dois replays seed 909 iguais: 14234 passos, score 820. |

O mecanismo da explosão está em [Boss.kf:93](../../src/main/kof/sifuture/game/Boss.kf#L93):

```kof
    explosionFrame(): Int {
        if (explosionSteps == 0) { return 0 }
        return 1 + (explosionSteps - 1) / 3
    }
```

O quadro zero existe somente no contador zero. Os contadores 1–3 mostram quadro 1, e 25–27 mostram quadro 9; `advanceExplosion` chama `reset()` em 28. Com passos de 30 ms, o efeito dura `30 + 9 × 90 = 840 ms`. A assertion de cada passo confere também os 27 deslocamentos acumulados explícitos, e o navegador compara pixels dos sprites, evitando depender somente da fórmula de produção.

Reexecutados os onze comandos do plano no head acima:

| Comando | Observação |
|---|---|
| `python3 scripts/kof_project.py test --target jvm` | exit 0; 103/103 |
| `python3 scripts/kof_project.py test --target js` | exit 0; 103/103 |
| `python3 tests/browser.py` | exit 0; menu, confirmações, pausa e resultado |
| `python3 tests/browser_controls.py` | exit 0; teclado, pointer, touch, diagonais, opostos e cancelamento |
| `python3 tests/browser_meteor.py` | exit 0; movimento, impacto e respawn |
| `python3 tests/browser_weapons.py` | exit 0; itens, armas, especial e controles |
| `python3 tests/browser_stage.py` | exit 0; HUD, jornada completa, resultado e fim dos efeitos |
| `python3 tests/browser_subchief.py` | exit 0; combate, R1–R3 e jornada completa |
| `python3 tests/browser_boss.py` | exit 0; combate, pixels, explosão, pausa, derrota e replay em 320/1200 |
| `python3 -m unittest discover -s tests -p test_kof_project.py` | exit 0; 8/8, diagnósticos de compilação inválida esperados |
| `bash tests/ci-contract.sh` com `.agent/tmp/tools` no PATH | exit 0; contrato com fixtures; não prova publicação real |

Trechos observados de ambos os comandos JVM/JS e da nova jornada Chrome, respectivamente:

```text
0 failed of 103 tests
1 passed, 0 failed
PASS boss entry, phases, shots, special, damage, 28-step explosion, pause, result and seeded replay at 320px; 14234 steps, score 820
PASS boss entry, phases, shots, special, damage, 28-step explosion, pause, result and seeded replay at 1200px; 14234 steps, score 820
```

Inspecionadas visualmente capturas normal/320, fury/1200, frenzy/320, special/1200, explosion0/320, explosion-step1/1200, explosion-step27/320 e result/1200. Comparação byte a byte: 14/14 assets históricos idênticos; diff de NOTICE vazio. Chrome `139.0.7258.154`; automação em desktop, não interação manual Android. Kof local `0.5.0-beta`, Eclipse Adoptium `25.0.4.1`, JAR SHA-256 `78e5ab9b65994889b8e593378aeabfbb6d5d71862e28a96f186085cabe404334`; checkout consultado `317d9f6b1c3e27032cc955a05f859f6c627d9338`, sem atribuir sua origem ao pacote local.

Foram identificadas três oportunidades de cobertura permanente, sem desvio observado na implementação: nível inicial com slot 0 ocupado e slot 1 livre; níveis 2/3 com relógio elegível e gatilho desligado; meteoro absorvido também alinhado com nave normal. Provas temporárias por `Game.start/step`, com classes reais via `prepared_sources(fixture=BossReview.kf, model_only=True)`, foram executadas com `kof test <árvore temporária>/Main.kf --target jvm` e `--target js`. Em cada alvo:

```text
PASS initial boss capacity remains one with first slot occupied and second free
PASS boss levels two and three require the special trigger even with an eligible clock
PASS boss absorbed meteor cannot hit a normal ship at the same inclusive edge
0 failed of 3 tests
1 passed, 0 failed
```

No primeiro cenário, após 26 passos o tiro existente permanece ativo em x=896 e o slot 1 permanece vazio. No segundo, relógio 11→12 não lança especial sem gatilho. No terceiro, boss em Fury e nave normal x=70/y=100 compartilham a borda x=120 com o meteoro: ele é absorvido, nave continua normal com três vidas, resistência 100 e score zero. A primeira execução da prova adicional omitiu a configuração de nave normal e falhou nesse cenário por observar Restart; ela foi invalidada como erro da fixture, corrigida somente na prova e repetida nos dois alvos. Recomenda-se incorporar esses três cenários à suíte versionada para proteger futuras mudanças; esta revisão não os acrescenta nem aumenta artificialmente os 103 casos permanentes.

O [CI 37484705995](https://github.com/renanfranca/kof-sifuture/actions/runs/37484705995) concluiu SUCCESS para este head do [PR #14](https://github.com/renanfranca/kof-sifuture/pull/14). O manifest registra o merge de validação `c3e4b34d3e3568c2b9d490f6aa0c775c73ec9a7c`, distribuição oficial Kof `0.5.0-beta`, origem `317d9f6b1c3e27032cc955a05f859f6c627d9338` e arquivo SHA-256 `f93f02eb62af584ea49ffb44efdbf54f970bdb9570f16fdc48ccc28242798ca9`. [Resolve](https://github.com/renanfranca/kof-sifuture/actions/runs/37484705995/job/112341647743), [JVM](https://github.com/renanfranca/kof-sifuture/actions/runs/37484705995/job/112342665328) e [JS](https://github.com/renanfranca/kof-sifuture/actions/runs/37484705995/job/112342665503) aprovados; ambos os logs de regras mostram 103/103. Pages foi SKIPPED, sem publicação.

Lacunas preservadas: comparação com vídeo histórico, Android real, música, menus e apresentação completos; esta conferência aceita somente o ciclo do boss, sem encerrar a v1. Evidência local opcional consolidada em `.agent/tmp/boss-plan-review-20261006T153524Z/`: `summary.json`, logs dos onze comandos, `BossReview.kf`, logs das provas complementares, `ci-current.log` e `screenshots/`. A exclusão `/.agent/tmp/` foi conferida exatamente uma vez e não há arquivo dessa árvore rastreado pelo Git. Os resultados essenciais e limites estão neste registro, sem depender dos arquivos locais.


## Créditos, Controles e navegação da pausa — 06/10/2026

O ciclo implementa abertura única com créditos animados, menu Novo Jogo/Controles, explicação com Voltar e pausa com Continuar/Reiniciar/Menu principal. V1 continua aberta. Branch `credits-pause-navigation`, sem worktree; base fixa `main` `2322d90f6d98e1cdd4a9d209efeb216c1182b8e4`. Worker `primary`, chat `01a113e4-c500-76c1-850c-191a12bc6f41`, título `sifuture-navigation-primary`, `gpt-6.1-sol`/`medium`. Implementação, validação e revisão compartilham contexto; revisão não independente.

Gate inicial sobre `50affe515aeeec0f6ee9776a4d774feb8c7cf469`, checkout limpo: **11/11 checks selecionados/executados, zero bloqueados, 236.96 s**. Regras JVM/JS: 112 testes em cada alvo (seis novos casos de navegação/abertura e três provas complementares do boss, além dos 103 anteriores). As sete jornadas Chrome passaram. Infraestrutura: oito unittest Python OK e contrato CI completo. Os diagnósticos de compilação no unittest são produzidos pela fixture deliberadamente inválida de `test_real_compile_failure_does_not_publish`; seu resultado esperado é impedir publicação, não compilar a fixture.

Comandos executados no SHA acima, todos exit 0:

```bash
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
python3 tests/browser.py
python3 tests/browser_controls.py
python3 tests/browser_meteor.py
python3 tests/browser_weapons.py
python3 tests/browser_stage.py
python3 tests/browser_subchief.py
python3 tests/browser_boss.py
python3 -m unittest discover -s tests -p 'test_kof_project.py'
PATH="$PWD/.agent/tmp/tools:$PATH" bash tests/ci-contract.sh
```

Trechos observados dos comandos JVM/JS, browser.py e browser_stage.py, respectivamente:

```text
0 failed of 112 tests
1 passed, 0 failed
PASS historical credits pixels, 30ms steps, redraw purity, fifty-frame wait and natural completion at 320px
PASS credits skip, bounded menu, Controls and pause navigation at 1200px
PASS pause freezes active combat, navigation continues once, Restart resets and held input cannot leak through Main Menu at 320px
```

### Expectativas conferidas contra fontes

Fonte histórica: SiFuture `6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f`, `MenuCanvas.java:98–109,192–217`, inspecionada estaticamente, sem executar o JAR. A frequência por instância vem da especificação aprovada; o restart histórico que repetia créditos não é reproduzido. Os PNGs têm copyright0 134×31 e copyright1 134×30.

Trecho fiel de [MenuCanvas.java](/home/renanfranca/projects/sifuture/src/MenuCanvas.java:192), linhas194–210 (omissões marcadas):

```java
if (this.i < Midlet.width/4) {
// ...
this.i+=5;
// ...
if (this.delay < 50) {
// ...
if ((this.j1 >= -this.copyright0.getHeight()) || (this.j0 <= Midlet.height)) {
    this.j0+=1;
    this.j1-=1;
```

Incrementar x de cinco em cinco sob `x < 176/4` chega a46, não44. A espera dura cinquenta atualizações. O `||` conserva a saída enquanto qualquer imagem ainda atende à condição; y0=283/y1=-32 encerra a saída e o passo seguinte abre Menu. Posições iniciais -134/110/141 e menu no passo260 foram conferidos separadamente das assertions. O recorte de Opções/Música, as três opções da pausa, os bloqueios de entrada e as duas confirmações de resultado seguem a especificação e o plano deste ciclo.

Kof consultado: treinamento `language/classes.md`, `idioms/classes.md`, `idioms/functions.md`, `idioms/ui.md`, `anti-patterns/fake-idioms.md`, `anti-patterns/duplicate-state.md` e tooling/cli; referência classes/closures; Learn 07,23,35-kof-ui; registro KofUi e implementação/testes UI JS. Regra do [treinamento de classes](/home/renanfranca/projects/kof/training/idioms/classes.md:35), também explicada em [Learn Kof, capítulo07](/home/renanfranca/projects/kof/learn/07-classes-and-objects.md:55):

> for **mutable state** use explicit fields + `constructor(...)`.

`Credits` guarda posições e relógio em campos mutáveis e constructor explícito. `Game.step()` avança a animação; `GameView.render()` consulta esses campos. A classe expressa o estado que muda ao longo do tempo; renderizar novamente não executa outra atualização. O contrato de classes e os percursos JVM/JS/Chrome sustentam essa escolha; compilação isolada não foi tratada como prova de execução.

### Assertions e resultados por critério

| Critério | Resultado e prova permanente | Limite/CI |
|---|---|---|
| Créditos históricos e desenho puro | GameJourney: -134→-129; chegada46; espera50; y111/140 no primeiro passo de saída; menu260. browser.py em320/1200: observação Canvas quando fora da tela, pixels na chegada/saída e cinco redesenhos sem mudança. | Assets comparados, vídeo não comparado. JVM/JS no workflow; Chrome local. |
| Exibição única e confirmação | Abre antes do primeiro passo; Enter focado repetido abre somente Menu e evento seguinte não inicia. Touch no canvas pula. Controles, pausa, resultado e nova partida sem retorno dos créditos. | browser.py, GameJourney e retornos das jornadas existentes. |
| Navegação e toque direto | Clamp0..1/0..2; repetição mantida fica em Reiniciar, diferente do próximo índice2; setas de toque atualizam seleção imediatamente. Novo Jogo tocado executa mesmo após retorno de Controles selecionado. Carregar/Opções ausentes no DOM deste recorte. | browser.py em320/1200 e caso de contatos GameJourney. |
| Controles | Texto visível inclui Tab/foco, setas/Enter/1, diagonais, opostos, arrasto, soltura/cancelamento e especial. Voltar conserva seleção; screenshots sem scroll horizontal. | browser.py; interação desktop automatizada, não manual Android. |
| Continuar | Partida com lasers ativos/movimento pausa; clocks/posição congelados; navegação não altera combate; próximo passo exatamente+1 sem restaurar tecla mantida. | browser_stage.py e provas existentes de pausa JVM/JS/Chrome. |
| Reiniciar | Comando real Enter e toque limpa vidas/score/fase/arma/cargas/chefes/projéteis antes do primeiro passo; depois steps1/restartFrame1 sem movimento mantido. Seed injetável reproduz spawn através de Game.restart/confirm(seed). | GameJourney e browser_stage.py, ambos widths. |
| Menu principal | Sai de combate e seleciona Novo Jogo; step/resume não retomam tentativa. Nova partida limpa sem créditos; teclado e dois contatos CDP mantidos não movem a nave nova, inclusive depois da soltura. | GameJourney, browser_stage.py, browser_controls.py. |
| Regressões e três provas do boss | 112/112 JVM/JS e sete jornadas; slot0 ocupado não lança slot1 no nível inicial; níveis2/3 sem gatilho não lançam especial; meteoro absorvido preserva nave normal na borda inclusiva. | GameJourney permanente; vídeo/Android continuam pendentes. |

Trechos fiéis das assertions permanentes, que observam modelo e ações reais em vez da topologia dos arquivos:

```kof
assert(g.credits.x == -129 && g.credits.waitSteps == 0)
assert(g.credits.waitSteps == 50 && g.credits.firstY == 110 && g.credits.secondY == 141)
assert(g.screen == Screen.Menu && g.menuSelection == 1)
```

Fonte: [GameJourney no checkpoint](https://github.com/renanfranca/kof-sifuture/blob/50affe515aeeec0f6ee9776a4d774feb8c7cf469/src/test/kof/sifuture/game/GameJourney.kf). A primeira assertion mede um único passo; a segunda fixa o estado depois da espera, sem calcular expectativas usando a decisão de produção. A terceira demonstra seleção conservada na volta de Controles.

```python
assert continued["steps"] == frozen["steps"] + 1 and continued["shipX"] == frozen["shipX"]
assert {key: reset[key] for key in expected} == expected
assert first["steps"] == 1 and first["restartFrame"] == 1 and first["shipX"] == 0
```

Fonte: [browser_stage.py no checkpoint](https://github.com/renanfranca/kof-sifuture/blob/50affe515aeeec0f6ee9776a4d774feb8c7cf469/tests/browser_stage.py#L336). `expected` lista zero steps/score/displayed/level/charges/fireSteps/chefes/projéteis, três vidas, posição5 e nave(0,100). O botão Observe apenas lê/redesenha o estado antes do próximo tick; não chama step. Por isso a prova distingue reset correto de uma partida que já avançou silenciosamente. A terceira assertion fixa precisamente o primeiro passo após reinício.

```kof
assert(game.boss.weapons.shots[0].active && game.boss.weapons.shots[0].x == 896)
assert(!game.boss.weapons.shots[1].active)
assert(!game.boss.weapons.special.active && game.boss.weapons.fireSteps == 12)
assert(game.ship.phase == ShipPhase.Normal && game.ship.lives == 3)
```

As três oportunidades registradas na revisão anterior agora vivem em GameJourney. Passaram nos dois alvos, sem mudar comportamento do boss. Capacidades, gatilhos e prioridades são observados pelo Game.step com entidades reais.

Chrome `139.0.7258.154`, viewports320/1200, Playwright/CDP; não houve aceite manual Android. Kof local `0.5.0-beta`, JDK embarcado Temurin `25.0.4.1+1`, JAR SHA-256 `78e5ab9b65994889b8e593378aeabfbb6d5d71862e28a96f186085cabe404334`. Checkout consultado `317d9f6b1c3e27032cc955a05f859f6c627d9338`; não se atribui automaticamente essa origem ao pacote local.

Comparação byte a byte: **8/8** copyright0/1, menu0/1/4, 2lives/3lives e sifuture idênticos; diff de NOTICE vazio. Capturas credits-arrived, credits-exit, menu, Controls e pause em320/1200 inspecionadas visualmente. A fidelidade dos PNGs e esses quadros não substituem comparação com o vídeo completo.

### Revisão, falhas e lacunas

Revisão estrutural no mesmo contexto: consolidado somente o protocolo movimento→render→update dos quatro callbacks em `directionChanged`, preservando tipos/ordem de eventos, foco, IDs e bloqueios. Risco classificado: repetição podia omitir atualização de seleção num evento; a prova de toque imediato já havia revelado esse efeito durante implementação. Nenhum teste de helper interno criado. Estado de créditos permanece na classe; input físico, movimento ativo e navegação têm lifetimes distintos; start(seed) continua a única política de reset. Demais dimensões da rubrica avaliadas, sem ampliação do combate.

Falhas de preparação preservadas: fixture inicial chamou finish privado e foi corrigida antes do RED válido; comparação por pixels de imagem completamente fora da tela teve zero amostras e foi substituída por observação Canvas mais pixels visíveis. Um callback novo com update sem receptor capturado deixou seleção visual atrasada no JS emitido; this explícito e a consolidação do protocolo corrigiram a prova pública. Isso não foi transformado em regra geral da linguagem nem em alteração do compilador. Um checkpoint avulso de armas encerrou143/log vazio, sem resultado aproveitável; o gate completo posterior executou a jornada com exit0. RED de abertura confirmou1/104 antes da mudança; APIs novas e botões ausentes também produziram falhas esperadas antes da produção.

Inventário CI: [workflow configurado](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml), Resolve verified Kof e Kof tests(jvm/js), a serem associados ao PR após o gate final. Chrome e infraestrutura foram executados localmente; o CI configurado exercita a matriz Kof. Build/Publish Pages são condicionais a push emmain e não são gate de PR. Sonar, mutation runner e Habit não configurados e excluídos, sem alegação de pass/score. Não há nova medição de cobertura.

Pendentes para v1: comparação com vídeo histórico; Android físico; áudio, Opções e Música; pausa automática; escala adaptável; entrada fora da árvore de controles. Evidência gerada opcional: `.agent/tmp/navigation-browser/`, `stage-browser/navigation-reset-*`, `navigation-assets.json`, `navigation-kof-identity.json`, `navigation-acceptance-audit.md`, `credits-pause-navigation.structural-review.md` e `validation/20261007T011914-rj7fs1sh/`. Resumo, resultados e limites essenciais estão aqui; arquivos locais não são necessários para ler o aceite. Gate final repetirá os onze comandos no commit revisado/documentado.

### Ajuste complementar de estilos

O gate final do commit `d097c105b7612031826b62258fdcc1ceea8a587a` também concluiu11/11 comandos com exit0, 112/112 testes em JVM e JS. Revisão complementar do runtime revelou que Style registra cada criação em `window.__kofStyles`, usando o tamanho do registro para atribuir ID (`JsRuntimeUiWidgets.java`, checkout Kof consultado, linhas332–334). GameControls agora cria uma vez os quatro estilos de visibilidade, seleção e ajuda no construtor, reutilizando-os nas atualizações, como já fazia o Especial. CSS, eventos e comportamento permanecem os mesmos. A jornada principal Chrome passou novamente após esse ajuste. Os onze comandos serão repetidos no commit adicional; o gate anterior não é apresentado como validação da correção.

Sonda local complementar (não teste permanente de implementação): registro de estilos **19→19 em1000 ticks**, relógio Chrome controlado e estilos reutilizados. Script opcional `.agent/tmp/styles_probe.py`. Tentativa inicial da sonda usou modo headless antigo removido pelo Chrome e falhou antes de executar assertions; foi corrigida para a mesma configuração headless=new das jornadas permanentes. O resultado válido mede ausência de crescimento nesse percurso; as jornadas públicas continuam demonstrando visual, foco e navegação.

Gate completo após reutilização de estilos: commit `6daccf42529c19e5f69d1cef1b84b04959b1e193`, onze comandos selecionados/executados, zero bloqueados, todos exit0 e coleta completa,237,27s. JVM/JS:112/112 cada; sete jornadas Chrome; Python8OK e contrato CI passou. Fontes e assertions da tabela acima foram reconferidas após a correção; nenhum critério foi removido. Evidência opcional `validation/20261007T013408-d768qpoy/`. O gate final repetirá esses comandos após consolidar este registro. Resultados posteriores e links de jobs ficarão também no PR e ledger. [CI desta branch](https://github.com/renanfranca/kof-sifuture/actions?query=branch%3Acredits-pause-navigation) exercita modelo/combate; navegador permanece evidência local.
