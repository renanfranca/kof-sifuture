# Piloto da UI: separar a lógica do `ControlsGuide`

Destino deste plano no repositório: `.agent/execplans/ui-pilot-controls-guide.md`
(repositório `/home/renanfranca/projects/kof-sifuture`). Guia de origem:
`~/.agents/skills/_temporary/codex-skills-ai-context/2026-11-10_ui-pilot-controls-guide.md`.
Plano mestre: `~/.agents/skills/_temporary/codex-skills-ai-context/2026-11-05_FEATURE_sifuture-sensor-debt-payoff.md`
(regras invioláveis e pontos de parada continuam valendo).

## Purpose and success

`GameControls`, `GameView` e `ControlsGuide` somam 199 mutantes sobreviventes e 0
mortos, porque na JVM o `kof.ui` não desenha nem dispara eventos. Este piloto move
as decisões do `ControlsGuide` para código que a JVM executa e mede quantos
mutantes sobram na parte de tela (a casca). O resultado decide se `GameControls`
(118) e `GameView` (75) seguem o mesmo caminho.

Sucesso, observável:

- o KofMut em `ControlsGuide.kf` + `GuideDisclosure.kf` termina `complete`, exit 0,
  0 sobreviventes, e os 6 mutantes da linha de base morrem ou deixam de existir
  com a prova registrada;
- `npm run check` e `npm run check:task` em PASS, com mutação em **PASS** (não SKIP);
- o jogo não muda: a jornada do guia em `tests/browser.py` passa sem alteração;
- `GameControls.kf` sem diff;
- relatório final com os quatro itens de "Pare e mostre" do guia.

Sem commit e sem push (pedido do usuário em 10/11). O executor para ao fim e mostra
o relatório.

## Context and limits

Fatos verificados no planejamento (somente leitura, 10/11):

- `src/main/kof/sifuture/ControlsGuide.kf` (100 linhas). Os 6 sobreviventes do A1
  (`.agent/tmp/debt-a1/kofmut-a1-report.json`), todos `boolean false -> true`:
  `8:25` `Bool discardClick = false`; `10:29` `private Bool expanded = false`;
  `59:58`, `64:74`, `66:67` `this.discardClick = false` (clique descartado,
  `pointerdown`, `blur`); `95:20` `expanded = false` em `close()`.
- O `GameControls.kf` usa só `guide.root` (150), `guide.discardClick = true/false`
  (311, 323), `guide.toggle()` (314), `guide.show()` (381), `guide.close()` (390, 398).
- **O Kof não tem getter/setter**: "No getters/setters — direct field"
  (`~/projects/kof/docs/language-reference/classes.md:38`). Então
  `guide.discardClick = true` é escrita direta num campo, e `discardClick` precisa
  continuar sendo um campo `Bool` do `ControlsGuide`. Campos e métodos sem
  modificador são públicos (`classes.md:76-94`).
- **`kof.ui` na JVM** (`~/projects/kof/kof-compiler/src/main/java/dev/kof/compiler/jvm/JvmRuntimeUi.java`):
  todo construtor devolve o handle `1`; `setStyle`, `setId` e `on(...)` têm corpo
  vazio (125, 157, 159); o lambda de `Button(text, action)` é descartado (420-426);
  `button.text` sempre lê `""` (428-433). Nenhuma API Kof dispara clique ou evento
  (`KofUi.java:270-530`). Logo, na JVM, **nenhum handler roda**, mas o objeto
  `ControlsGuide()` é construído e seus campos e métodos Kof comuns funcionam.
- **`kof.ui` no JS** dos testes: roda no GraalJS embutido com um DOM falso
  (`JsRuntimeCore.java:39`, `179-196`); `button.text` é lido de volta
  (`JsRuntimeUiWidgets.java:245-256`). Isso **não** mata mutantes, porque o
  `testCommand` do `kof-mut.json` roda só `--target jvm`.
- O KofMut muta só `boundary`, `equality`, `logical`, `boolean` e `arithmetic`
  (`~/projects/kof-mut/docs/operators.md`). O `!` unário, strings e chamadas não
  geram mutante.
- `npm run check` muta todo `src/main/kof` alterado contra `main` e reprova com
  qualquer sobrevivente (`scripts/check.mjs`, `scripts/mutation-step.mjs`).
- `ControlsGuide.kf` tem 2 achados de lint hoje
  (`.agent/validation/sensor-debt-payoff.md:48`); o construtor tem 55 linhas
  (limites de produção: função 25 linhas, 17 instruções, arquivo 150).
- Testes Kof: `scripts/kof-tests.mjs` descobre `src/test/kof` e roda uma entrada
  única; 172 casos em JVM e JS hoje. `testRows` não compila nessa entrada
  (SEM015): um teste por caso. Sem comentários em código e testes (`AGENTS.md`).
- Kof do PATH: 0.7.0. Compatibilidade: 0.6.4 em
  `~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof`.

Limites:

- **Não alterar `GameControls.kf`.** Manter a API pública do `ControlsGuide`:
  `root`, `disclosure`, `discardClick`, `toggle()`, `show()`, `close()`. Métodos
  públicos novos são permitidos (só acrescentam).
- O comportamento na tela não muda. Nenhuma supressão, allowlist ou mudança de
  limite. Mutante sem teste possível: parar no ponto de parada 2 do plano mestre.
- Antes de cada decisão de Kof, ler o arquivo de `~/projects/kof/training/`
  correspondente (classes, testes, `kof.ui`), como exige o `AGENTS.md`.
- Evidência bruta em `.agent/tmp/ui-pilot/`. Probes fora de pastas com ponto
  (KofLang/Kof4j#999).

## Decisions

- **Desenho (usuário, 10/11, ao revisar este plano).** O guia pedia que a classe
  nova guardasse também a marca de descarte. Isso não cabe sem mexer no
  `GameControls`, por falta de propriedades no Kof. Escolha: a classe pura
  `GuideDisclosure` guarda só se os detalhes estão abertos (`expanded`, `toggle()`,
  `close()`). O `ControlsGuide` guarda `discardClick` e ganha os métodos públicos
  `clicked()`, `pointerDown()` e `blurred()`. Os handlers só chamam esses métodos e
  aplicam estilo e texto. Alternativa descartada: nenhuma classe nova e `expanded`
  público no `ControlsGuide` (menos código, mas não testa o padrão que serviria ao
  `GameControls`). Consequência: os testes da casca constroem `ControlsGuide()` na
  JVM e leem `discardClick` e o estado de `GuideDisclosure` por um campo público.
- **Local da suíte (usuário, 10/11):** `src/test/kof/sifuture/ControlsGuideJourney.kf`,
  `package sifuture`, igual à produção.
- **Passo 0 respondido pela fonte, confirmado por probe.** O texto não é legível na
  JVM, então o passo 1 do guia (R5 antes de mexer) não consegue matar os mutantes
  pelo código atual: os testes nascem junto da separação, num TDD normal, como o
  próprio guia prevê.

## Milestones

### M0. Branch e probe

Criar a branch nova a partir de `main` (`84a5dbf`) com o skill `create-git-branch`.

Probe descartável `src/test/kof/sifuture/ControlsGuideProbe.kf` (`package
sifuture`, `import sifuture.ControlsGuide`): um teste que cria `ControlsGuide()`,
chama `toggle()` e imprime `disclosure.text` e `discardClick`; depois `close()` e
imprime de novo. Rodar `kof test src/test/kof/sifuture/ControlsGuideProbe.kf
--target jvm` e `--target js`, salvar a saída em `.agent/tmp/ui-pilot/probe-*.log`
e **apagar o probe**.

Esperado: JVM imprime texto vazio e `false`; JS imprime `Menos detalhes`/`Mais
detalhes` e `false`; os dois compilam e passam. Se o JS falhar ao construir o
guia, ou o pacote `sifuture` não resolver no diretório de teste, parar e mostrar.

Linha de base: rodar o KofMut só em `ControlsGuide.kf` na `main` e confirmar os 6
`id`s acima (comando na seção Validation). Registrar contagem de casos (172).

### M1. `GuideDisclosure` por TDD

Invocar o skill `tdd-behavior-autonomous-quiet`. Anotar o RED esperado no aceite
antes de cada teste. Arquivo novo `src/main/kof/sifuture/GuideDisclosure.kf`, sem
`import kof.ui`, com `Bool expanded = false`, `toggle()` e `close()`.

Testes em `src/test/kof/sifuture/ControlsGuideJourney.kf`, um comportamento por
teste (exemplos: contexto → ação → resultado):

1. detalhes novos começam fechados: `GuideDisclosure()` → `expanded` é `false`
   (mata o `= false` inicial da classe nova);
2. `toggle()` abre e o seguinte fecha: `true`, depois `false`;
3. `close()` fecha detalhes abertos: `toggle()`, `close()` → `false`;
4. depois de `close()`, o próximo `toggle()` abre (o guia indica isso para `95:20`).

O primeiro RED é de compilação (classe inexistente); registrar e seguir.

### M2. `ControlsGuide` delega (casca)

Com o skill `refactor-design`, depois TDD para os métodos novos:

- campo público `GuideDisclosure` (nome do domínio, por exemplo `detailsState`);
  `expanded` privado some do `ControlsGuide`;
- `toggle()`: `detailsState.toggle()` e aplica estilo e texto conforme
  `detailsState.expanded`; `close()`: `detailsState.close()`, mesma aplicação e
  `root` escondido; `show()` igual;
- `clicked()`: se `discardClick`, limpa e não alterna; senão `toggle()`.
  `pointerDown()` e `blurred()` limpam `discardClick`;
- os lambdas de `Button`, `pointerdown` e `blur` só chamam esses métodos (o `blur`
  também aplica o estilo `idle`), sem literal booleano;
- dividir o construtor em construtores de bloco com nome do domínio (teclado,
  toque, especial, detalhes) até zerar os 2 achados de lint, sem mudar CSS, ids,
  textos nem ordem dos filhos.

Testes novos na mesma suíte (cada um com o mutante que deve matar):

5. guia novo: `clicked()` abre os detalhes (mata `8:25`);
6. guia novo começa fechado e `close()` depois de `toggle()` volta a fechado;
7. clique marcado para descartar não alterna e limpa a marca: `discardClick =
   true`, `clicked()` → fechado e `discardClick` `false`; outro `clicked()` abre
   (mata o reset do clique);
8. `pointerDown()` limpa a marca: `discardClick = true`, `pointerDown()` →
   `false`, e o `clicked()` seguinte abre;
9. `blurred()` limpa a marca, igual ao 8.

Cada asserção que distingue: "fechado" sozinho passaria com um mutante que nunca
abre; por isso os testes 7 a 9 checam também que o clique seguinte abre.

### M3. Medir e registrar

KofMut só nos dois arquivos; lint; `npm run check`; `npm run check:task`;
contagens no 0.7.0 e 0.6.4 (comandos em Validation). Atualizar `EXECPLAN.md`
(seção datada no fim), a cópia do plano mestre (continuidade datada, sem reescrever
o histórico) e `.agent/validation/sensor-debt-payoff.md` (seção "Piloto da UI").

## Progress

- [x] M0. Branch `refactor/ui-pilot-controls-guide`, probe JVM/JS, linha de base KofMut (6 sobreviventes confirmados) e contagem (172). (10/11)
- [x] M1. `GuideDisclosure` com testes 1 a 4 (176 casos JVM e JS). (10/11)
- [x] M2. `ControlsGuide` delegando, testes 5 a 9, lint 0 (181 casos JVM e JS). (10/11)
- [x] M3. Medições, registros e relatório (10/11). A primeira rodada do
  `npm run check:task` falhou em `browser:browser` (`SEM011`/`SEM015`:
  `GuideDisclosure` indefinido no build JS do app, porque o `ControlsGuide.kf` não a
  importava e a suíte Kof importa as duas classes). Com a aprovação do usuário,
  entrou `import sifuture.GuideDisclosure`; a segunda rodada deu `CHECK:TASK: PASS`
  com as sete jornadas. Desvio do probe: `kof test` direto no arquivo dá `PKG004`;
  o probe rodou por uma entrada em `src/test/kof`. Evidência em
  `.agent/validation/sensor-debt-payoff.md`, seção "Piloto da UI".

## Validation

Comandos (na raiz do repositório):

```
mkdir -p .agent/tmp/ui-pilot
echo '["src/main/kof/sifuture/ControlsGuide.kf","src/main/kof/sifuture/GuideDisclosure.kf"]' > .agent/tmp/ui-pilot/scope.json
kof-mut run --project . --files .agent/tmp/ui-pilot/scope.json --config kof-mut.json --report-dir .agent/tmp/ui-pilot/kof-mut-reports --run-id "$(node -e 'console.log(crypto.randomUUID())')"
npm run lint:sensor -- src/main/kof/sifuture/ControlsGuide.kf src/main/kof/sifuture/GuideDisclosure.kf
node scripts/kof-tests.mjs --target jvm
node scripts/kof-tests.mjs --target js
KOF=$HOME/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof node scripts/kof-tests.mjs --target jvm
KOF=$HOME/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof node scripts/kof-tests.mjs --target js
npm run check
npm run check:task
git diff --exit-code main -- src/main/kof/sifuture/GameControls.kf
git diff --check
```

Na linha de base (M0), o escopo do KofMut é só `ControlsGuide.kf`.

Critérios de aceite (planejado; o observado vai para o aceite):

- **C1. Mutação.** Fonte: guia, passo 3, e A4 do plano mestre. Esperado: exit 0,
  `status: complete`, 0 sobreviventes, 0 limitações. Tabela antes → depois dos 6
  `id`s: cada um morto (com o nome do teste) ou inexistente (por exemplo, `10:29`
  some porque `expanded` saiu do `ControlsGuide`; mostrar que deixou de existir,
  não que foi suprimido). Listar os mutantes novos de `GuideDisclosure.kf` e o
  teste que mata cada um. Distingue: um teste que só confere "fechado" passaria
  com o mutante; a mutação prova que a asserção pega a troca.
- **C2. Casca.** Esperado: 0 mutantes gerados nas linhas de handler, estilo e texto
  do `ControlsGuide`; os únicos candidatos dele são os literais de `discardClick`,
  todos mortos. Registrar cada candidato restante com linha e motivo.
- **C3. Sensores.** `lint:sensor` nos dois arquivos com `0 findings`; `npm run
  check` com `CHECK: PASS` e mutação em PASS; `npm run check:task` com
  `CHECK:TASK: PASS` (inclui as sete jornadas, entre elas o guia em
  `tests/browser.py`, sem alteração nesse arquivo).
- **C4. Casos.** 172 + N novos em JVM e JS, no 0.7.0 e no 0.6.4 (`0 failed of M
  tests`); nenhum teste existente alterado.
- **C5. Limites.** `GameControls.kf` sem diff; API pública do `ControlsGuide`
  mantida (conferir pelo diff); nenhum comentário novo; `git diff --check` exit 0.

Obrigações do executor antes de entregar:

- Reconferir cada expectativa contra a fonte citada, separado de conferir se o
  teste a demonstra.
- Para C1 a C5, registrar no aceite: comando, resultado observado e onde está a
  asserção ou o artefato. Suíte verde sozinha não prova C1.
- Registrar lacunas e critérios não verificados; um critério com lacuna não é
  apresentado como satisfeito.

Relatório final (pare e mostre, em pt-BR, com trechos de evidência como o
`AGENTS.md` pede):

1. o resultado do probe (M0), JVM e JS;
2. a tabela antes e depois dos 6 mutantes, mais os novos;
3. quantos mutantes sobram na casca, e quais;
4. a estimativa para `GameControls` (118) e `GameView` (75), dizendo o que no
   código deles é decisão testável na JVM e o que é só tela;
5. arquivos alterados, `git status`, e a confirmação de que não houve commit nem push.

## Risks

- **Equivalente inesperado.** Se um mutante não puder ser morto por comportamento
  observável, parar no ponto de parada 2 com a prova. Não suprimir.
- **Tempo do KofMut.** Cada mutante roda a suíte inteira (`commandTimeoutMs`
  30000). Se aparecer `Timeout`, parar e mostrar o tempo da suíte.
- **JS dos testes.** Construir `ControlsGuide` no DOM falso pode falhar numa
  versão (0.6.4). O M0 prova no 0.7.0; o M3 confere no 0.6.4. Se falhar, parar.
- **Campo público para teste.** O estado de `GuideDisclosure` fica legível de fora.
  É contrato novo e aceito na decisão de desenho; não usar esse campo no
  `GameControls`.
