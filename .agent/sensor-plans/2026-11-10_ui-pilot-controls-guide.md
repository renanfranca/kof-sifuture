# Piloto da UI: separar a lógica do `ControlsGuide`

Plano mestre: `2026-11-05_FEATURE_sifuture-sensor-debt-payoff.md`, nesta mesma pasta.
As regras invioláveis e os pontos de parada dele continuam valendo.

## Por que

Os arquivos `GameControls`, `GameView` e `ControlsGuide` têm 199 mutantes
sobreviventes e nenhum morto. O motivo é que o `kof.ui` não faz nada na JVM: ele
cria os objetos, mas não desenha nem dispara evento.

A ideia é mover as decisões para uma classe sem `kof.ui`, que a JVM consegue testar,
e deixar na tela só a ligação (a casca). O KofMut só muta operadores: literal
booleano, comparação, `&&`/`||` e contas. Uma casca sem operador não gera mutante.

O piloto mede quantos mutantes sobram na casca. O resultado decide se o `GameControls`
e o `GameView` seguem pelo mesmo caminho e se vai ser preciso uma regra de exclusão.

## Linha de base (A1, 10/11)

O `src/main/kof/sifuture/ControlsGuide.kf` tem 100 linhas e 6 sobreviventes, todos
`boolean false -> true`:

| Linha:coluna | Código | Palpite |
| --- | --- | --- |
| 8:25 | `Bool discardClick = false` | morre por teste |
| 10:29 | `private Bool expanded = false` | **provável equivalente**: o construtor chama `close()`, que zera de novo |
| 59:58 | `this.discardClick = false` no clique descartado | morre por teste |
| 64:74 | `this.discardClick = false` no `pointerdown` | morre por teste |
| 66:67 | `this.discardClick = false` no `blur` | morre por teste |
| 95:20 | `expanded = false` no `close()` | morre por teste: depois de `close()`, o próximo `toggle()` precisa abrir |

O `GameControls.kf` usa o guia nas linhas 150, 311, 314, 323, 381, 390 e 398, pelos
membros `root`, `discardClick`, `toggle()`, `show()` e `close()`. As jornadas Python
cobrem o guia em `tests/browser.py:538-614` e `:765-777`.

## Restrição importante

**Não altere o `GameControls.kf`.** O `check` muta todo arquivo de produção que foi
mudado. Os 118 sobreviventes dele reprovariam o piloto. Mantenha a API pública do
`ControlsGuide`: `root`, `disclosure`, `discardClick`, `toggle()`, `show()` e
`close()`.

Se a separação não couber sem mexer no `GameControls`, pare e mostre o motivo.

## Passos

Branch nova a partir da `main` (`84a5dbf`). Sem commit nem push. Se o lote 1
(`2026-11-10_sensor-debt-r4-r5-batch-1.md`) estiver rodando no mesmo checkout, use a
mesma branch: duas branches não convivem num checkout só.

### 0. Prova rápida

Num teste JVM, crie `ControlsGuide()` e veja o que dá para ler de volta depois de
`toggle()` e `close()`, por exemplo `disclosure.text` e `discardClick`.

- Se os handles do `kof.ui` guardam o texto na JVM, parte dos mutantes morre **sem
  separar nada**. Registre isso, porque muda o plano do `GameControls` e do `GameView`.
- Se não guardam, siga para o passo 1.

### 1. R5 antes de mexer

Com o skill `tdd-behavior-autonomous-quiet`, escreva os testes de comportamento do
guia num arquivo novo, `src/test/kof/sifuture/game/ControlsGuideJourney.kf` (ou um
nome por assunto). Exemplos de comportamento:

- o guia começa fechado;
- `toggle()` abre e o seguinte fecha;
- `close()` sempre volta para fechado, mesmo se estava aberto;
- um clique marcado para descartar não alterna e limpa a marca;
- `pointerdown` e `blur` limpam a marca.

Anote o RED esperado antes de cada teste. Se o passo 0 mostrar que a tela não pode
ser lida, estes testes nascem contra a classe nova (passo 2), num TDD normal.

### 2. Separar

Com o skill `refactor-design`, crie uma classe sem `import kof.ui`, por exemplo
`GuideDisclosure` no pacote `sifuture`. Ela guarda `expanded` e o descarte do clique,
com métodos com nome do domínio: `toggle`, `close`, `click` (que diz se alterna),
`pointerDown` e `blur`. O `ControlsGuide` delega para ela e só aplica `setStyle`, o
texto e os eventos.

### 3. Medir

- KofMut só em `ControlsGuide.kf` e no arquivo novo. Registre:
  - os mutantes que sobram na casca, cada um com a linha e o motivo;
  - os mortos na classe nova;
  - os equivalentes, com a prova (ponto de parada 2).
- `npm run lint:sensor` nos dois arquivos: 0 achados.
- `npm run check`: PASS.
- A jornada de navegador do guia (`tests/browser.py`) continua passando, porque o
  comportamento na tela não muda.
- A contagem de casos sobe, em JVM e JS, no 0.7.0 e no 0.6.4.

## Pare e mostre

1. O resultado do passo 0.
2. A tabela antes e depois dos 6 mutantes, mais os mutantes novos.
3. **Quantos mutantes sobram na casca** e quais são.
4. A sua estimativa para aplicar o mesmo no `GameControls` (118) e no `GameView` (75).

Atualize o `EXECPLAN.md`, a cópia do plano mestre e o aceite
`.agent/validation/sensor-debt-payoff.md`.
