# Desenvolvimento

[Voltar à apresentação do projeto](../README.md) ·
[Como jogar](jogar.md) ·
[Comportamento esperado](regras-do-jogo.md) ·
[CI e publicação](ci-e-publicacao.md)

Este guia concentra requisitos, comandos locais e a explicação da preparação
temporária das fontes. Execute as receitas na raiz do checkout de SiFuture.

## Requisitos

Use Python 3 e uma instalação de Kof acessível no `PATH`. Confirme:

```bash
kof version
```

O ambiente examinado em 09/10/2026 informa `kof 0.5.0-beta`, Linux x86_64,
Eclipse Adoptium 25.0.4.1 e JDK embarcado. A versão identifica a distribuição;
não identifica sozinha seu commit de origem. O checkout consultado para a
linguagem é `317d9f6b1c3e27032cc955a05f859f6c627d9338`; não se presume que esse
SHA seja metadado da instalação no `PATH`. Os resultados anteriores permanecem
em [EXECPLAN.md](../EXECPLAN.md) e nos registros de validação.

O [training de instalação](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/distribution/install.md#L13)
descreve o pacote:

> The official package contains: compiler, CLI, runtime, stdlib, tooling, editor
> support, embedded OpenJDK and documentation.

A JVM necessária ao launcher acompanha o pacote oficial. O checkout do
código de Kof serve à consulta de implementação e documentação; não é um
pré-requisito para compilar este jogo. Para obter e verificar a mesma
distribuição de uma execução do CI, use a [receita de reprodução](ci-e-publicacao.md#reproduzir-uma-distribuição).

## Compilador escolhido

`--kof CAMINHO` prevalece sobre a variável `KOF`; depois vem `kof` do `PATH`.
O [script canônico](../scripts/kof_project.py#L30) expressa a ordem:

```python
def kof_executable(override=None):
    return override or os.environ.get("KOF") or shutil.which("kof") or "kof"
```

O primeiro valor disponível ganha. Passe `--kof /caminho/para/kof` a `build`
ou `test` para uma escolha explícita. Se uma sessão ainda tiver `KOF` definido
por um procedimento anterior, execute `unset KOF` para voltar ao `PATH`.

## Compilar e abrir a aplicação

`build --output` recebe o diretório da página pronta:

```bash
python3 scripts/kof_project.py build --output /tmp/sifuture-game
python3 -m http.server 8766 --directory /tmp/sifuture-game
```

Depois do build sem erro, visite `http://127.0.0.1:8766/`. O servidor HTTP é
necessário porque a página carrega módulos JS e sprites de `assets/`.
Encerre-o com `Ctrl+C`. Use o [percurso de jogo](jogar.md#começar-uma-partida)
para verificar abertura, movimento, pausa e retorno.

O [Learn Kof JS](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/37-kofjs.md#L54)
descreve a entrega:

> `kof build --target=js` generates `index.html` + modules: serve the
> folder as a static web application (any HTTP server).

O wrapper produz esse conjunto e copia os assets do jogo. Compilar com sucesso
não prova a apresentação gráfica ou os comandos no navegador; são verificações
separadas.

## Executar os testes de regras

Uma **suíte** é um arquivo com casos de teste que exercitam comportamento.
As suítes Kof canônicas ficam em `src/test/kof`; atualmente
[GameJourney.kf](../src/test/kof/sifuture/game/GameJourney.kf) usa a implementação
real de `src/main/kof`.

```bash
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
python3 scripts/kof_project.py test --target jvm --suite sifuture/game/GameJourney.kf
```

Na revisão examinada `e38f5e0ccb98bfd443a0d57833b6be0b6bed6aee`, cada execução
completa deve mostrar 114 testes aprovados. Essa contagem pertence à revisão;
novos casos podem aumentá-la. Texto e geometria são verificados no navegador.
`--suite` seleciona um arquivo relativo à raiz de testes. Sem essa opção,
o wrapper descobre `.kf` recursivamente e executa em ordem de caminho, usando
uma árvore temporária nova para cada suíte. Uma falha não impede as seguintes;
o comando devolve a primeira falha observada. Em
[scripts/kof_project.py](../scripts/kof_project.py#L146):

```python
first_failure = 0
for path in suites:
    print(f"Suite: {path.relative_to(tests)}", flush=True)
    with prepared_sources(suite=path, root=root) as source:
        code = _run([str(kof_executable(kof)), "test", str(source / "Main.kf"), "--target", target])
        if code and not first_failure:
            first_failure = code
return first_failure
```

Cada chamada usa o runner oficial. O [Learn Kof, Testing](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/23-testing.md#L42)
ensina:

> Each test runs **in isolation** (one failing does not interrupt the others).

Essa regra cobre os casos dentro de uma invocação Kof; o laço Python conserva
também a independência entre arquivos. O [training do CLI](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/tooling/cli.md)
documenta `kof test` e `--target`; o wrapper organiza as fontes antes de chamar
essa ferramenta.

**Experimento didático preservado:** altere temporariamente `SHIP_SPEED` de
`5` para `4` em uma cópia de validação de `Rules.kf`, observe o teste de
movimento falhar e restaure `5`. O histórico em [EXECPLAN.md](../EXECPLAN.md)
registra esse tipo de prova; este guia não atribui uma execução nova ao
experimento. Uma mudança controlada que faz o teste falhar demonstra que ele
observa a velocidade esperada, além de simplesmente aceitar um processo sem erro.

## Raiz de fontes e workaround

Um **workaround** é um contorno provisório para uma limitação das ferramentas.
Uma **raiz de fontes** é o diretório a partir do qual pacotes e imports
localizam os arquivos. O projeto mantém aplicação em `src/main/kof`, testes
em `src/test/kof` e [kof.toml](../kof.toml) na raiz, com `name = "sifuture"`.

O [Learn Kof, Packages and Modules](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/19-packages-and-modules.md#L25)
mostra imports de arquivo e diretório. A [referência de módulos](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/docs/language-reference/modules.md#L18)
define:

> Kof's "module" is the **root directory** passed to the compiler (module root),
> used to expand directory imports.

Assim, `import sifuture.game.GameJourney` localiza a suíte relativa à raiz
preparada; a própria suíte importa `sifuture.game.*` para alcançar as regras.

**WORKAROUND de organização/build:** na instalação 0.5.0-beta examinada, os
comandos do projeto preparam uma árvore descartável fora do checkout e sem
`kof.toml` ancestral. Copiam os bytes das fontes canônicas, geram uma pequena
entrada de import e chamam o CLI oficial. O build inclui somente a aplicação,
com entrada `import sifuture.*`. Cada suíte recebe a aplicação e somente seu
arquivo de testes, com uma entrada específica. A árvore é removida após o
comando, inclusive em falha. Não é preciso preparar fontes ou assets à mão.

O wrapper verifica `index.html` e `Default.mjs` antes de copiar a saída e os
assets para `--output`. Em [build](../scripts/kof_project.py#L109):

```python
if code:
    return code
missing = [item for item in ("index.html", "Default.mjs") if not (web / item).is_file()]
if missing:
    raise PreparationError(f"Kof build returned success without required artifacts: {', '.join(missing)}")
_publish(web, output)
```

Essa verificação detecta um retorno zero sem produto de compilação. O
[training de workarounds](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/anti-patterns/runtime-workarounds.md#L9)
explica por que a preparação não é uma regra da linguagem:

> The detour is legitimate — but it is **not an idiom**.

A [investigação das fontes](../.agent/specifications/reorganizar-fontes-e-testes-kof.md)
conserva os reproduzers executados em JVM/JS. Na distribuição daquele snapshot,
o build direto podia informar `no .kf/.kof files found`, retornar zero e não
gerar o módulo. Testes com raiz inadequada falhavam com `PKG004`; um import
não resolvido apresentava `PKG006`. Esses são resultados de ferramentas
daquela revisão, não restrições da sintaxe de pacotes.

### Diagnosticar TMPDIR

Se aparecer um erro sobre `TMPDIR` ou `kof.toml` ancestral, escolha um
diretório temporário fora de qualquer projeto Kof e repita a receita.
O [script](../scripts/kof_project.py#L34) recusa preparação dentro do projeto
ou sob manifesto ancestral:

```python
if directory == project or project in directory.parents:
    raise PreparationError("temporary source is inside the project; set TMPDIR outside the project")
if any((ancestor / "kof.toml").exists() for ancestor in (directory, *directory.parents)):
    raise PreparationError("temporary source has an ancestral kof.toml; set TMPDIR outside a Kof project")
```

Um manifesto encontrado acima da preparação pode mudar a raiz usada para
resolver os imports. Preparar em uma subpasta do checkout não oferece a
mesma condição da árvore externa.

### Evolução da issue Kof #708

A [issue #708](https://github.com/KofLang/Kof4j/issues/708) está fechada.
Seu histórico registra em `lab` as correções de `moduleRoot`, raiz de testes
e falha explícita sem fontes, seguidas da interface de duas raízes. A decisão
[D-CLI-SOURCE-ROOTS](https://github.com/KofLang/Kof4j/blob/0e6a02f23d295d89e2ce4975b6d8b177240f5222/docs/development/DECISIONS.md#L4528)
no commit `0e6a02f23d295d89e2ce4975b6d8b177240f5222` registra:

> **State:** DECIDED (maintainer) + IMPLEMENTED (30/09) — tracker `#708` (case `renanfranca`/SiFuture #2).

O [teste upstream](https://github.com/KofLang/Kof4j/blob/0e6a02f23d295d89e2ce4975b6d8b177240f5222/kof-cli/src/test/java/dev/kof/cli/TwoRootsCliE2ETest.java#L45)
declara, dentro do manifesto do projeto de teste:

```toml
[sources]
app = "src/main/kof"
test = "src/test/kof"
```

Esse é um excerto da configuração do teste upstream, não uma configuração já
aplicada a SiFuture. O teste chama `kof build`/`kof test` sem argumento
posicional e verifica os alvos JVM, Native e JS. As fontes dessa revisão
upstream foram consultadas; esse teste não foi executado nesta reorganização.
O checkout Kof local consultado permanece em `317d9f6`; o objeto mais novo
não estava disponível nele e foi lido na revisão pública fixada acima.

O manifesto atual do jogo ainda não declara `[sources]`. Os comandos deste
guia conservam a preparação comprovada com a instalação examinada. Migrar
esse fluxo requer verificar a distribuição com o suporte novo e validar
build, testes e entradas de navegador antes de retirar o wrapper; a reorganização da
documentação não realiza essa migração. Verificar os artefatos produzidos
continua necessário após qualquer atualização do compilador.

## Modelo, desenho e controles

O **modelo** é o estado e as regras que mudam a cada passo. O **desenho**
consulta esse estado para apresentar a cena. Os **controles** traduzem as
entradas do jogador em comandos do modelo. Em
[Main.kf](../src/main/kof/sifuture/Main.kf#L15):

```kof
time.interval(Rules.STEP_MS, () -> {
    game.step()
    drawing.render(game)
    controls.update()
})
```

`step()` avança o estado antes de `render()`. Desenhar novamente sem `step()`
não avança a partida. `Event.key()` e `Event.target()` distinguem origem e
tecla na árvore de controles; estilos e widgets são montados uma vez e
reutilizados. A geometria atual e as regras de foco estão no
[guia de jogo](jogar.md); a [tipografia](../fonts/README.md) tem seu próprio dono.

O [training de UI](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/language/ui.md#L73)
e o [Learn Kof, UI](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/35-kof-ui.md#L5)
delimitam o alvo do desenho:

> On the other targets the
> handles are no-ops — the program runs without rendering.

Na implementação JS, [kofUiCanvasNew](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/js/JsRuntimeUiWidgets.java#L384)
cria a superfície:

```javascript
export function kofUiCanvasNew(w, h) {
    if (typeof document === "undefined") return -1;
    const canvas = document.createElement("canvas");
    canvas.width = w;
    canvas.height = h;
```

Esse excerto JavaScript é código do runtime Kof, não aplicação escrita à mão.
Ele exige o documento do navegador. Na implementação
[JVM](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/jvm/JvmRuntimeUi.java#L472),
o mesmo construtor retorna apenas um identificador:

```java
public static int kof_ui_canvas_new(int width, int height) {
    return 1;
}
```

A [realização Native](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/runtime/RuntimeUi.java#L536)
também retorna um handle sem criar superfície. A decisão
[D-UI-SCOPE](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/docs/development/DECISIONS.md#L1675)
delimita esse escopo. Compilar ou testar regras em JVM/JS não demonstra uma
janela gráfica nesses outros alvos.

## Organização do código

| Caminho | Responsabilidade |
| --- | --- |
| [Main.kf](../src/main/kof/sifuture/Main.kf) | Cria a janela e agenda o relógio. |
| [Game.kf](../src/main/kof/sifuture/game/Game.kf) | Coordena cada passo, telas, colisões, fase e pontuação. |
| [Ship.kf](../src/main/kof/sifuture/game/Ship.kf) | Movimento, explosão, reinício e quadro da nave. |
| [Weapons.kf](../src/main/kof/sifuture/game/Weapons.kf) | Nível, cargas, cadência e projéteis; Lasers, Shot e demais classes cuidam de seus estados. |
| [Meteor.kf](../src/main/kof/sifuture/game/Meteor.kf) | Posições, contadores, movimentos e quadros dos meteoros. |
| [Rules.kf](../src/main/kof/sifuture/game/Rules.kf) | Limites, durações, intervalos e limite do sorteio inicial. |
| [State.kf](../src/main/kof/sifuture/game/State.kf) | Tipos das telas, estados e direções. |
| [GameView.kf](../src/main/kof/sifuture/GameView.kf) | Desenha as telas consultando o modelo. |
| [GameControls.kf](../src/main/kof/sifuture/GameControls.kf) e [ControlsGuide.kf](../src/main/kof/sifuture/ControlsGuide.kf) | Montam controles, foco e guia dentro do jogo. |

### Entrada no menu e apresentação do guia

Cada chegada real ao menu cria uma nova entrada animada da nave. Ela começa
em `x = -30`, avança dez unidades por passo com propulsão e freia recuando
três até `x = 18`. A troca para o sprite normal acontece na frenagem.
Permanecer no menu ou redesenhar não reinicia a sequência; selecionar e
confirmar continua possível durante a entrada. Voltar de Controles conserva
a seleção; pausa e resultado retornam com Novo Jogo selecionado.
Em [MenuEntrance.advance](../src/main/kof/sifuture/game/MenuEntrance.kf#L12):

```kof
if (phase == MenuEntrancePhase.Entry) {
    if (x < 80) { x = x + 10; return }
    x = x + 10
    phase = MenuEntrancePhase.Braking
}
x = x - 3
if (x <= 18) { finish() }
```

Somente a atualização avança esses valores. O [documento de tipografia](../fonts/README.md)
concentra textos, cores, margens e a animação dos créditos, incluindo a espera
de seis segundos e o quadro vazio antes do menu.

O [painel Controles](../src/main/kof/sifuture/ControlsGuide.kf#L19) usa 248 pixels
de largura, margem interna de 16 e conteúdo de 216, texto sans-serif de 14,
entrelinha de 20 e títulos de 16. Seu cabeçalho de 44 pixels substitui a área
desenhada; direcional e Especial ficam recolhidos. A seção Especial precede
Mais detalhes. A janela acompanha o conteúdo, sem instrução fixa no rodapé.
Os [comandos do painel](jogar.md) e a [prova de apresentação](../.agent/validation/controls-guide.md)
ficam vinculados às mesmas regras, sem duplicar suas receitas neste guia.

### Classes e estados em Kof

Uma **classe mutável** possui campos que mudam ao longo da partida. Um
**enum** representa um conjunto fechado de estados ou direções, permitindo
comparar valores do mesmo tipo. [State.kf](../src/main/kof/sifuture/game/State.kf#L3)
usa, por exemplo:

```kof
enum Screen { Credits, Menu, Controls, Play, Pause, Result }
enum ShipPhase { Normal, Explosion, Restart, Hidden }
enum Direction { Left, Right, Up, Down }
```

`Ship.lastX` e `Ship.lastY` guardam a última direção pressionada como
`Direction`, escolhendo entre setas opostas. `ship.phase` é um campo explícito
da classe. O [idioma de classes](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/idioms/classes.md#L45)
ensina campos e construtor para esse estado; o
[Learn Kof 07](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/07-classes-and-objects.md#L65)
explica a diferença em relação aos dados imutáveis.

Existe uma divergência documental no snapshot consultado. O
[training de tipos](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/language/types.md#L106)
ainda registra:

> Runtime representation: the constant name itself (String-backed).

A [referência de classes](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/docs/language-reference/classes.md#L149)
estabelece:

> **An enum value is a real instance (D-ENUM207, issue #207)**

[EnumIdentityE2ETest](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/test/java/dev/kof/compiler/EnumIdentityE2ETest.java#L69)
confirma comparação entre valores do mesmo enum. As jornadas do jogo também
exercitam essas comparações em JVM e JS; o guia não ensina a descrição antiga
de strings como comportamento atual.

### Semente

Uma **semente** inicializa a sequência de números pseudoaleatórios.
`Game.start(seed)` chama `rng.seed(seed)` para repetir partidas em testes;
o jogo normal escolhe uma semente variável com `random.int(...)`.
**Experimento didático preservado:** troque a semente passada a `Game.start()`
no teste e compare as posições iniciais; repetir a mesma semente repete a
sequência. O experimento é uma orientação, sem nova execução atribuída aqui.

## Verificar o navegador

Uma **fixture** é uma entrada de teste que prepara uma situação determinística
usando modelo, desenho e controles reais.

Instale Python Playwright e Pillow. Os scripts atuais abrem Chrome gráfico
em `/usr/bin/google-chrome`; é necessário esse executável e uma sessão
gráfica disponível. Uma instalação apenas do pacote Playwright não garante
essas condições.

```bash
python3 tests/browser.py
python3 tests/browser_controls.py
python3 tests/browser_meteor.py
python3 tests/browser_weapons.py
python3 tests/browser_stage.py
python3 tests/browser_subchief.py
python3 tests/browser_boss.py
```

Cada script compila, serve em `127.0.0.1` numa porta livre e limpa navegador,
servidor e temporários. A aplicação e as fixtures são Kof. JavaScript e CSS da saída são gerados por Kof.
Playwright envia interações e Pillow confere sprites.

`python3 tests/browser.py URL` aceita uma aplicação já servida. Os scripts
que oferecem `--kof CAMINHO` conservam essa opção: `browser.py`,
`browser_controls.py`, `browser_meteor.py` e `browser_weapons.py`.

| Percurso | Observações |
| --- | --- |
| `browser.py` | Aplicação normal em 320/1200 px: créditos, espera/saída/quadro vazio, entrada no menu, textos, guia fechado/aberto, foco, teclado, clique/toque e pausa; capturas em densidades 1/2. Para derrota, resultado e nova partida usa fixture com três colisões determinísticas. |
| `browser_controls.py` | Contextos novos com ciclos de 30 ms: posição, sprites, quatro diagonais, opostos, foco, clique/Tab, soltura e identidade do botão/contato. |
| `browser_meteor.py` | Fixture do modelo real com um passo por clique: posição e quadros do meteoro atingido. |
| `browser_weapons.py` | Pixels de itens, efeitos, lasers, blaster e nove quadros do especial; vida 4, indicador, pausa, teclas mantidas, recusas, cancelamento e ordens de soltura. Também abre a aplicação normal. |
| `browser_stage.py` | Trilha, indicadores, sprites, percurso completo, resultado e redesenhos sem avanço. |
| `browser_subchief.py` | Encontro, tiros, especial, explosão, pausa/retomada e repetição. |
| `browser_boss.py` | Entrada, níveis, tiros, contatos, explosão, resultado e repetição. |

Esperar uma derrota espontânea não é um critério determinístico: coleta de
vida e evolução podem prolongar a tentativa. As três colisões preparadas
permitem verificar o encerramento e as duas confirmações do resultado.
Redesenhos sem avanço verificam a separação entre modelo e apresentação.

A automação Python pode ser verificada com:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

O contrato local de infraestrutura de publicação fica no
[guia de CI](ci-e-publicacao.md#verificações-locais-de-infraestrutura).

## O que as verificações demonstram

O [registro de controles](../.agent/validation/sifuture-controls.md)
associa o checkpoint `cedf4875abe101d8fd85012dbfb30ef20bf5406c` ao gate com
114 testes por alvo, oito testes Python, sete percursos completos de navegador
e contrato CI. No Chrome 155.0.8059.39, os percursos exercitaram o alvo JS;
Vivaldi 8.2.4133.84 teve verificações específicas de apresentação e navegação,
sem executar os sete percursos completos. O registro também distingue o
relato manual “Resolvido” do usuário de um controle automatizado do Windows.

Os [registros de fase](../.agent/validation/stage-hud-result.md),
[armas](../.agent/validation/background-items-weapons.md),
[soltura do especial](../.agent/validation/special-key-release.md),
[reinício de sprites](../.agent/validation/ship-meteor-reset.md) e
[créditos e guia](../.agent/validation/controls-guide.md) preservam provas
anteriores e suas revisões. Publicação real e diferenças entre a aplicação
remota e fixtures locais estão no [guia de CI](ci-e-publicacao.md#evidência-da-revisão-publicada).

Testes do modelo não demonstram UI gráfica em JVM/Native. Toque via CDP não
encerra o [aceite Android](jogar.md#android-e-limites-do-aceite). Comparação
com o vídeo histórico e aprovações visuais humanas ainda pendentes nos
respectivos registros continuam separadas de inspeção do agente e automação.

A [validação desta reorganização](../.agent/validation/documentacao.md)
registra os comandos repetidos e as provas apenas consultadas. Logs,
capturas e arquivos intermediários locais ficam em `.agent/tmp/`; os resumos
versionados contêm os resultados essenciais sem depender desses arquivos.
