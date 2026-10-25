# Calibração medida dos sensores: M1

Execução local em 25/10/2026, base `82111142c85f98b970ccd65fbf044e492d017729` mais alterações não commitadas do M1, branch `sensor-calibration-m1`. Fontes e suítes do jogo preservadas. Este registro contém o inventário completo e a triagem; não depende dos logs locais para ser compreendido.

Comando: `scripts/kof-sensors/run . > .agent/tmp/sensors-m1/inventory.json`. Escopo completo: `src/main/kof` e `src/test/kof`, 25 arquivos esperados, 25 analisados e 25 tokenizados pelo CPD, sem falhas; 45.443 tokens oficiais; 321 unidades: funções, métodos, construtores, lambdas e 114 casos `test`. Os corpos locais possuem contas próprias. O token EOF não entra na contagem.

Frontend efetivamente carregado: `/home/renanfranca/.local/share/kof/kof-0.6.6-linux-x86_64/lib/kof.jar`, versão `kof 0.6.6`, SHA-256 `198bb211dbcefe60bd02f703dff991e82ba55c94f805b1b2b863362757289e58`. Pesquisa local do Kof em `7c237861a9035d84b1f7ec4cfddd89daef4c6ddd`; a evidência de execução usa o jar instalado, não presume que checkout e distribuição sejam iguais. Maven 3.9.5 e Temurin Java 25.0.2. CPD fixado em 7.17.0.

## Definições e fontes

Contrato de adaptação preservado do plano externo aprovado, seção “Calibração e formatação”. Referência histórica: Katacombs `44cb39c916e9a05de561123d7b13554ee6e0a516`, `eslint.config.mjs:17` e `:60`. Trecho fiel:

```javascript
  complexity: ['error', 5],
  'max-params': ['error', 4],
  'max-depth': ['error', 2],
  'max-statements': ['error', 15],
```

[Referência fixada](https://github.com/renanfranca/katacombs-kata-ts/blob/44cb39c916e9a05de561123d7b13554ee6e0a516/eslint.config.mjs#L17). Linhas por função usam 25 com `skipBlankLines: true, skipComments: true`; arquivo usa 150 com `skipComments: false`. Suítes preservam exceção somente para linhas por função e statements. Nenhum guia foi modificado ou traduzido em política de aviso.

| Métrica | Definição Kof |
| --- | --- |
| functionLines | Intervalo da declaração até o fim do corpo, inclusive delimitadores, sem linhas vazias ou somente comentários. Tokens oficiais distinguem strings/comentários; inclui linhas de corpos locais. |
| fileLines | Linhas não vazias, incluindo comentários. |
| complexity | Base 1 mais if statement/expressão, loops, catch, case não default e cada `&&`/`||`. Corpos locais não contribuem ao pai. |
| parameters | Parâmetros declarados, sem receiver implícito ou overload sintético. |
| depth | Corpo no nível zero; if, loops, switch e try acrescentam um nível. Catch/case não acrescentam outro; else if mantém o nível da cadeia. |
| statements | Nodes StatementNode, incluindo controles, inicializador de for, statement vazio e return sintético de corpo de expressão; exclui BlockStmt e função local no pai. |

A regra de corpo de expressão vem da [referência de funções](../../../kof/docs/language-reference/functions.md:28):

> **Body**: block `{ … }`, or `= expression` (expression body — becomes
> `return expression`), or `;` (abstract).

O parser expõe esse return no AST; por isso o contador vê um statement mesmo sem `return` escrito. [Training de funções](../../../kof/training/idioms/functions.md:1) e [Learn Kof 06](../../../kof/learn/06-functions.md:1) orientam a leitura. As fixtures Java exercitam parsing e contagem, não executam todos esses exemplos como programas. Os checks e os 114 testes do jogo foram executados em JVM/JS separadamente.

Localizações do AST nem sempre são o começo da declaração. O adaptador cruza os nodes com tokens oficiais e delimitadores balanceados, sem uma segunda gramática. Provas específicas cobrem cabeçalhos em várias linhas, construtores, lambdas e corpos de expressão. Novas formas sintáticas precisam de prova própria. As contagens não prometem equivalência perfeita com AST JavaScript.

## Limites propostos

A proposta é o menor inteiro não inferior à referência com menos de 20 findings. Finding exige valor estritamente maior que o limite. O limite anterior só é candidato admissível quando não fica abaixo da referência. A direção futura continua sendo a referência, sem aperto automático.

| Métrica | Referência | Findings na referência | Proposta | Findings na proposta | Findings no inteiro anterior |
| --- | ---: | ---: | ---: | ---: | ---: |
| fileLines | 150 | 5 | 150 | 5 | 5 |
| functionLines | 25 | 10 | 25 | 10 | 10 |
| complexity | 5 | 125 | 16 | 19 | 24 |
| parameters | 4 | 2 | 4 | 2 | 3 |
| depth | 2 | 20 | 3 | 5 | 20 |
| statements | 15 | 21 | 17 | 18 | 20 |

Complexidade 15 ainda produz 24 findings; profundidade 2 produz 20; statements 16 produz 20. Portanto 16, 3 e 17 são os mínimos admissíveis nessas métricas. As outras três referências já produzem menos de 20. Isso calibra o volume de feedback e não aprova a dívida nem demonstra adequação universal dos limites.

## Distribuições completas

Cada par é `valor: quantidade`. Linhas por função e statements excluem suítes somente nesta população elegível; seus valores permanecem no inventário.

**fileLines**: 5: 1, 6: 1, 10: 1, 18: 1, 21: 1, 23: 2, 28: 1, 32: 1, 43: 1, 48: 1, 51: 1, 53: 1, 54: 1, 76: 1, 83: 1, 90: 1, 92: 1, 97: 1, 113: 1, 174: 1, 223: 1, 307: 1, 391: 1, 2665: 1.

**functionLines**: 1: 43, 3: 18, 4: 14, 5: 30, 6: 20, 7: 12, 8: 5, 9: 8, 10: 8, 11: 8, 12: 3, 13: 6, 14: 3, 15: 3, 16: 4, 17: 1, 18: 2, 19: 2, 21: 1, 24: 2, 26: 1, 27: 1, 35: 1, 36: 1, 39: 1, 56: 1, 57: 1, 82: 1, 87: 1, 108: 1.

**complexity**: 1: 95, 2: 39, 3: 25, 4: 21, 5: 16, 6: 17, 7: 9, 8: 24, 9: 8, 10: 12, 11: 12, 12: 8, 13: 4, 14: 5, 15: 2, 16: 5, 17: 3, 19: 3, 20: 1, 21: 2, 22: 2, 23: 1, 26: 1, 27: 1, 28: 2, 33: 1, 43: 1, 55: 1.

**parameters**: 0: 220, 1: 79, 2: 13, 3: 6, 4: 1, 5: 1, 6: 1.

**depth**: 0: 135, 1: 125, 2: 41, 3: 15, 4: 4, 5: 1.

**statements**: 0: 10, 1: 44, 2: 18, 3: 18, 4: 19, 5: 14, 6: 14, 7: 12, 8: 7, 9: 7, 10: 3, 11: 3, 12: 5, 13: 2, 14: 2, 15: 4, 16: 1, 17: 2, 18: 1, 19: 1, 20: 3, 23: 1, 24: 1, 27: 2, 28: 1, 33: 1, 34: 1, 38: 1, 48: 1, 58: 1, 72: 1, 88: 1, 115: 1.

## Inventário completo

Cada unidade tem localização e fim físicos; L é linhas sem vazias/comentários, C complexidade, P parâmetros, D profundidade e S statements. A linha física pode abranger intervalos maiores que L. Não há supressão no inventário.

| Arquivo | Linhas não vazias | Tokens | Unidades |
| --- | ---: | ---: | ---: |
| [src/main/kof/sifuture/ControlsGuide.kf:1](../../src/main/kof/sifuture/ControlsGuide.kf:1) | 92 | 565 | 10 |
| [src/main/kof/sifuture/GameControls.kf:1](../../src/main/kof/sifuture/GameControls.kf:1) | 391 | 2977 | 46 |
| [src/main/kof/sifuture/GameView.kf:1](../../src/main/kof/sifuture/GameView.kf:1) | 223 | 2552 | 10 |
| [src/main/kof/sifuture/Main.kf:1](../../src/main/kof/sifuture/Main.kf:1) | 18 | 112 | 2 |
| [src/main/kof/sifuture/game/Background.kf:1](../../src/main/kof/sifuture/game/Background.kf:1) | 6 | 34 | 2 |
| [src/main/kof/sifuture/game/Blaster.kf:1](../../src/main/kof/sifuture/game/Blaster.kf:1) | 48 | 309 | 6 |
| [src/main/kof/sifuture/game/Boss.kf:1](../../src/main/kof/sifuture/game/Boss.kf:1) | 113 | 915 | 14 |
| [src/main/kof/sifuture/game/BossShot.kf:1](../../src/main/kof/sifuture/game/BossShot.kf:1) | 32 | 232 | 6 |
| [src/main/kof/sifuture/game/BossSpecial.kf:1](../../src/main/kof/sifuture/game/BossSpecial.kf:1) | 28 | 215 | 6 |
| [src/main/kof/sifuture/game/BossWeapons.kf:1](../../src/main/kof/sifuture/game/BossWeapons.kf:1) | 53 | 394 | 6 |
| [src/main/kof/sifuture/game/Credits.kf:1](../../src/main/kof/sifuture/game/Credits.kf:1) | 23 | 134 | 2 |
| [src/main/kof/sifuture/game/Game.kf:1](../../src/main/kof/sifuture/game/Game.kf:1) | 307 | 2409 | 25 |
| [src/main/kof/sifuture/game/Item.kf:1](../../src/main/kof/sifuture/game/Item.kf:1) | 54 | 327 | 4 |
| [src/main/kof/sifuture/game/Lasers.kf:1](../../src/main/kof/sifuture/game/Lasers.kf:1) | 10 | 66 | 2 |
| [src/main/kof/sifuture/game/MenuEntrance.kf:1](../../src/main/kof/sifuture/game/MenuEntrance.kf:1) | 21 | 114 | 3 |
| [src/main/kof/sifuture/game/Meteor.kf:1](../../src/main/kof/sifuture/game/Meteor.kf:1) | 83 | 482 | 8 |
| [src/main/kof/sifuture/game/Rules.kf:1](../../src/main/kof/sifuture/game/Rules.kf:1) | 43 | 255 | 0 |
| [src/main/kof/sifuture/game/Ship.kf:1](../../src/main/kof/sifuture/game/Ship.kf:1) | 90 | 619 | 6 |
| [src/main/kof/sifuture/game/Shot.kf:1](../../src/main/kof/sifuture/game/Shot.kf:1) | 51 | 308 | 6 |
| [src/main/kof/sifuture/game/SpecialBeam.kf:1](../../src/main/kof/sifuture/game/SpecialBeam.kf:1) | 76 | 585 | 9 |
| [src/main/kof/sifuture/game/State.kf:1](../../src/main/kof/sifuture/game/State.kf:1) | 5 | 48 | 0 |
| [src/main/kof/sifuture/game/Subchief.kf:1](../../src/main/kof/sifuture/game/Subchief.kf:1) | 97 | 657 | 10 |
| [src/main/kof/sifuture/game/SubchiefShot.kf:1](../../src/main/kof/sifuture/game/SubchiefShot.kf:1) | 23 | 156 | 4 |
| [src/main/kof/sifuture/game/Weapons.kf:1](../../src/main/kof/sifuture/game/Weapons.kf:1) | 174 | 1344 | 16 |
| [src/test/kof/sifuture/game/GameJourney.kf:1](../../src/test/kof/sifuture/game/GameJourney.kf:1) | 2665 | 29634 | 118 |

### src/main/kof/sifuture/ControlsGuide.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| ControlsGuide | constructor | [15:5 até 70](../../src/main/kof/sifuture/ControlsGuide.kf:15) | 56 | 1 | 0 | 0 | 28 |
| lambda | lambda | [58:46 até 61](../../src/main/kof/sifuture/ControlsGuide.kf:58) | 4 | 2 | 0 | 1 | 4 |
| lambda | lambda | [64:38 até 64](../../src/main/kof/sifuture/ControlsGuide.kf:64) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [65:32 até 65](../../src/main/kof/sifuture/ControlsGuide.kf:65) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [66:31 até 66](../../src/main/kof/sifuture/ControlsGuide.kf:66) | 1 | 1 | 1 | 0 | 2 |
| heading | method | [72:5 até 76](../../src/main/kof/sifuture/ControlsGuide.kf:72) | 5 | 1 | 1 | 0 | 3 |
| paragraph | method | [78:5 até 82](../../src/main/kof/sifuture/ControlsGuide.kf:78) | 5 | 1 | 1 | 0 | 3 |
| toggle | method | [84:5 até 88](../../src/main/kof/sifuture/ControlsGuide.kf:84) | 5 | 2 | 0 | 1 | 6 |
| show | method | [90:5 até 92](../../src/main/kof/sifuture/ControlsGuide.kf:90) | 3 | 1 | 0 | 0 | 1 |
| close | method | [94:5 até 99](../../src/main/kof/sifuture/ControlsGuide.kf:94) | 6 | 1 | 0 | 0 | 4 |

### src/main/kof/sifuture/GameControls.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| GameControls | constructor | [73:5 até 155](../../src/main/kof/sifuture/GameControls.kf:73) | 82 | 1 | 3 | 0 | 72 |
| lambda | lambda | [116:38 até 116](../../src/main/kof/sifuture/GameControls.kf:116) | 1 | 1 | 0 | 0 | 0 |
| lambda | lambda | [122:29 até 122](../../src/main/kof/sifuture/GameControls.kf:122) | 1 | 1 | 1 | 0 | 2 |
| lambda | lambda | [123:28 até 126](../../src/main/kof/sifuture/GameControls.kf:123) | 4 | 1 | 1 | 0 | 2 |
| lambda | lambda | [127:35 até 132](../../src/main/kof/sifuture/GameControls.kf:127) | 6 | 2 | 1 | 1 | 3 |
| lambda | lambda | [133:33 até 133](../../src/main/kof/sifuture/GameControls.kf:133) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [134:37 até 134](../../src/main/kof/sifuture/GameControls.kf:134) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [135:36 até 135](../../src/main/kof/sifuture/GameControls.kf:135) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [145:38 até 145](../../src/main/kof/sifuture/GameControls.kf:145) | 1 | 1 | 0 | 0 | 1 |
| lambda | lambda | [147:34 até 147](../../src/main/kof/sifuture/GameControls.kf:147) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [148:28 até 148](../../src/main/kof/sifuture/GameControls.kf:148) | 1 | 1 | 1 | 0 | 2 |
| lambda | lambda | [149:27 até 149](../../src/main/kof/sifuture/GameControls.kf:149) | 1 | 1 | 1 | 0 | 4 |
| lambda | lambda | [152:28 até 152](../../src/main/kof/sifuture/GameControls.kf:152) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [153:26 até 153](../../src/main/kof/sifuture/GameControls.kf:153) | 1 | 1 | 1 | 0 | 1 |
| keyboardSurface | method | [157:5 até 180](../../src/main/kof/sifuture/GameControls.kf:157) | 24 | 1 | 1 | 0 | 20 |
| lambda | lambda | [158:30 até 160](../../src/main/kof/sifuture/GameControls.kf:158) | 3 | 2 | 0 | 1 | 2 |
| configureOverlay | method | [182:5 até 192](../../src/main/kof/sifuture/GameControls.kf:182) | 11 | 1 | 0 | 0 | 5 |
| lambda | lambda | [185:35 até 185](../../src/main/kof/sifuture/GameControls.kf:185) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [186:29 até 186](../../src/main/kof/sifuture/GameControls.kf:186) | 1 | 1 | 1 | 0 | 2 |
| lambda | lambda | [187:28 até 191](../../src/main/kof/sifuture/GameControls.kf:187) | 5 | 1 | 1 | 0 | 3 |
| overlayStyle | method | [194:5 até 196](../../src/main/kof/sifuture/GameControls.kf:194) | 3 | 1 | 0 | 0 | 1 |
| updateSurfaceFocus | method | [198:5 até 210](../../src/main/kof/sifuture/GameControls.kf:198) | 13 | 7 | 0 | 2 | 12 |
| directionButton | method | [212:5 até 224](../../src/main/kof/sifuture/GameControls.kf:212) | 13 | 1 | 2 | 0 | 11 |
| lambda | lambda | [213:35 até 213](../../src/main/kof/sifuture/GameControls.kf:213) | 1 | 1 | 0 | 0 | 0 |
| lambda | lambda | [217:28 até 217](../../src/main/kof/sifuture/GameControls.kf:217) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [218:27 até 218](../../src/main/kof/sifuture/GameControls.kf:218) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [219:34 até 219](../../src/main/kof/sifuture/GameControls.kf:219) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [220:32 até 220](../../src/main/kof/sifuture/GameControls.kf:220) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [221:36 até 221](../../src/main/kof/sifuture/GameControls.kf:221) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [222:35 até 222](../../src/main/kof/sifuture/GameControls.kf:222) | 1 | 1 | 1 | 0 | 1 |
| directionChanged | method | [226:5 até 230](../../src/main/kof/sifuture/GameControls.kf:226) | 5 | 1 | 2 | 0 | 3 |
| menuOption | method | [232:5 até 255](../../src/main/kof/sifuture/GameControls.kf:232) | 24 | 1 | 6 | 0 | 9 |
| lambda | lambda | [233:35 até 233](../../src/main/kof/sifuture/GameControls.kf:233) | 1 | 1 | 0 | 0 | 1 |
| lambda | lambda | [236:34 até 236](../../src/main/kof/sifuture/GameControls.kf:236) | 1 | 1 | 1 | 0 | 1 |
| lambda | lambda | [237:28 até 245](../../src/main/kof/sifuture/GameControls.kf:237) | 9 | 3 | 1 | 2 | 7 |
| lambda | lambda | [246:27 até 251](../../src/main/kof/sifuture/GameControls.kf:246) | 6 | 1 | 1 | 0 | 4 |
| activateOption | method | [257:5 até 265](../../src/main/kof/sifuture/GameControls.kf:257) | 9 | 4 | 3 | 1 | 11 |
| optionAvailable | method | [267:5 até 271](../../src/main/kof/sifuture/GameControls.kf:267) | 5 | 6 | 1 | 1 | 5 |
| keyboardReceiver | method | [273:5 até 275](../../src/main/kof/sifuture/GameControls.kf:273) | 3 | 5 | 1 | 0 | 1 |
| optionTarget | method | [277:5 até 279](../../src/main/kof/sifuture/GameControls.kf:277) | 3 | 5 | 1 | 0 | 1 |
| activateAction | method | [281:5 até 289](../../src/main/kof/sifuture/GameControls.kf:281) | 9 | 2 | 0 | 1 | 6 |
| activateSpecial | method | [291:5 até 295](../../src/main/kof/sifuture/GameControls.kf:291) | 5 | 1 | 0 | 0 | 3 |
| keyChanged | method | [297:5 até 335](../../src/main/kof/sifuture/GameControls.kf:297) | 39 | 33 | 3 | 3 | 48 |
| updateSpecial | method | [337:5 até 345](../../src/main/kof/sifuture/GameControls.kf:337) | 9 | 9 | 0 | 1 | 10 |
| setOptionStyle | method | [347:5 até 353](../../src/main/kof/sifuture/GameControls.kf:347) | 7 | 3 | 4 | 2 | 7 |
| update | method | [355:5 até 411](../../src/main/kof/sifuture/GameControls.kf:355) | 57 | 19 | 0 | 2 | 58 |

### src/main/kof/sifuture/GameView.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| GameView | constructor | [41:5 até 75](../../src/main/kof/sifuture/GameView.kf:41) | 35 | 1 | 1 | 0 | 33 |
| render | method | [77:5 até 163](../../src/main/kof/sifuture/GameView.kf:77) | 87 | 43 | 1 | 3 | 88 |
| drawMenuLabel | method | [165:5 até 167](../../src/main/kof/sifuture/GameView.kf:165) | 3 | 1 | 2 | 0 | 1 |
| drawCredits | method | [169:5 até 172](../../src/main/kof/sifuture/GameView.kf:169) | 4 | 1 | 1 | 0 | 2 |
| drawCreditBlock | method | [174:5 até 180](../../src/main/kof/sifuture/GameView.kf:174) | 7 | 2 | 3 | 1 | 4 |
| drawText | method | [182:5 até 188](../../src/main/kof/sifuture/GameView.kf:182) | 7 | 1 | 5 | 0 | 5 |
| drawHud | method | [190:5 até 205](../../src/main/kof/sifuture/GameView.kf:190) | 16 | 5 | 1 | 1 | 19 |
| drawResult | method | [207:5 até 216](../../src/main/kof/sifuture/GameView.kf:207) | 10 | 6 | 1 | 1 | 13 |
| numberWidth | method | [218:5 até 223](../../src/main/kof/sifuture/GameView.kf:218) | 6 | 2 | 1 | 1 | 6 |
| drawNumber | method | [225:5 até 234](../../src/main/kof/sifuture/GameView.kf:225) | 10 | 3 | 3 | 1 | 8 |

### src/main/kof/sifuture/Main.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| main | function | [6:1 até 20](../../src/main/kof/sifuture/Main.kf:6) | 15 | 1 | 0 | 0 | 9 |
| lambda | lambda | [15:34 até 19](../../src/main/kof/sifuture/Main.kf:15) | 5 | 1 | 0 | 0 | 3 |

### src/main/kof/sifuture/game/Background.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| reset | method | [6:5 até 6](../../src/main/kof/sifuture/game/Background.kf:6) | 1 | 1 | 0 | 0 | 1 |
| advance | method | [8:5 até 8](../../src/main/kof/sifuture/game/Background.kf:8) | 1 | 1 | 0 | 0 | 1 |

### src/main/kof/sifuture/game/Blaster.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| reset | method | [11:5 até 16](../../src/main/kof/sifuture/game/Blaster.kf:11) | 6 | 1 | 0 | 0 | 4 |
| fire | method | [18:5 até 24](../../src/main/kof/sifuture/game/Blaster.kf:18) | 7 | 2 | 1 | 1 | 6 |
| spriteFrame | method | [26:5 até 30](../../src/main/kof/sifuture/game/Blaster.kf:26) | 5 | 3 | 0 | 1 | 5 |
| hitsMeteor | method | [32:5 até 36](../../src/main/kof/sifuture/game/Blaster.kf:32) | 5 | 8 | 1 | 0 | 1 |
| hit | method | [38:5 até 38](../../src/main/kof/sifuture/game/Blaster.kf:38) | 1 | 1 | 0 | 0 | 1 |
| advance | method | [40:5 até 54](../../src/main/kof/sifuture/game/Blaster.kf:40) | 15 | 9 | 0 | 2 | 18 |

### src/main/kof/sifuture/game/Boss.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Boss | constructor | [20:5 até 20](../../src/main/kof/sifuture/game/Boss.kf:20) | 1 | 1 | 0 | 0 | 0 |
| reset | method | [22:5 até 37](../../src/main/kof/sifuture/game/Boss.kf:22) | 16 | 1 | 0 | 0 | 14 |
| newDestination | method | [39:5 até 44](../../src/main/kof/sifuture/game/Boss.kf:39) | 6 | 1 | 0 | 0 | 4 |
| absorbMeteors | method | [46:5 até 53](../../src/main/kof/sifuture/game/Boss.kf:46) | 8 | 10 | 1 | 2 | 5 |
| touchesShip | method | [55:5 até 60](../../src/main/kof/sifuture/game/Boss.kf:55) | 6 | 8 | 1 | 0 | 1 |
| vulnerable | method | [62:5 até 64](../../src/main/kof/sifuture/game/Boss.kf:62) | 3 | 3 | 0 | 0 | 1 |
| damage | method | [66:5 até 70](../../src/main/kof/sifuture/game/Boss.kf:66) | 5 | 3 | 1 | 1 | 6 |
| reward | method | [72:5 até 77](../../src/main/kof/sifuture/game/Boss.kf:72) | 6 | 4 | 0 | 1 | 7 |
| evolveWeapons | method | [79:5 até 85](../../src/main/kof/sifuture/game/Boss.kf:79) | 7 | 10 | 0 | 1 | 12 |
| spriteFrame | method | [87:5 até 91](../../src/main/kof/sifuture/game/Boss.kf:87) | 5 | 4 | 0 | 1 | 5 |
| explosionFrame | method | [93:5 até 96](../../src/main/kof/sifuture/game/Boss.kf:93) | 4 | 2 | 0 | 1 | 3 |
| advanceExplosion | method | [98:5 até 107](../../src/main/kof/sifuture/game/Boss.kf:98) | 10 | 5 | 0 | 1 | 12 |
| advance | method | [109:5 até 109](../../src/main/kof/sifuture/game/Boss.kf:109) | 1 | 1 | 0 | 0 | 1 |
| advance | method | [111:5 até 128](../../src/main/kof/sifuture/game/Boss.kf:111) | 18 | 14 | 1 | 2 | 27 |

### src/main/kof/sifuture/game/BossShot.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| BossShot | constructor | [10:5 até 10](../../src/main/kof/sifuture/game/BossShot.kf:10) | 1 | 1 | 0 | 0 | 0 |
| reset | method | [12:5 até 12](../../src/main/kof/sifuture/game/BossShot.kf:12) | 1 | 1 | 0 | 0 | 3 |
| spriteFrame | method | [14:5 até 18](../../src/main/kof/sifuture/game/BossShot.kf:14) | 5 | 4 | 0 | 1 | 5 |
| fire | method | [20:5 até 25](../../src/main/kof/sifuture/game/BossShot.kf:20) | 6 | 1 | 2 | 0 | 4 |
| touchesShip | method | [27:5 até 31](../../src/main/kof/sifuture/game/BossShot.kf:27) | 5 | 8 | 1 | 0 | 1 |
| advance | method | [33:5 até 38](../../src/main/kof/sifuture/game/BossShot.kf:33) | 6 | 5 | 0 | 1 | 8 |

### src/main/kof/sifuture/game/BossSpecial.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| BossSpecial | constructor | [9:5 até 9](../../src/main/kof/sifuture/game/BossSpecial.kf:9) | 1 | 1 | 0 | 0 | 0 |
| reset | method | [11:5 até 11](../../src/main/kof/sifuture/game/BossSpecial.kf:11) | 1 | 1 | 0 | 0 | 2 |
| fire | method | [13:5 até 19](../../src/main/kof/sifuture/game/BossSpecial.kf:13) | 7 | 2 | 2 | 1 | 6 |
| frame | method | [21:5 até 21](../../src/main/kof/sifuture/game/BossSpecial.kf:21) | 1 | 1 | 0 | 0 | 1 |
| touchesShip | method | [23:5 até 27](../../src/main/kof/sifuture/game/BossSpecial.kf:23) | 5 | 9 | 1 | 0 | 1 |
| advance | method | [29:5 até 34](../../src/main/kof/sifuture/game/BossSpecial.kf:29) | 6 | 4 | 0 | 1 | 7 |

### src/main/kof/sifuture/game/BossWeapons.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| BossWeapons | constructor | [11:5 até 11](../../src/main/kof/sifuture/game/BossWeapons.kf:11) | 1 | 1 | 0 | 0 | 0 |
| reset | method | [13:5 até 20](../../src/main/kof/sifuture/game/BossWeapons.kf:13) | 8 | 2 | 0 | 1 | 7 |
| evolve | method | [22:5 até 25](../../src/main/kof/sifuture/game/BossWeapons.kf:22) | 4 | 2 | 0 | 1 | 3 |
| attemptFire | method | [27:5 até 47](../../src/main/kof/sifuture/game/BossWeapons.kf:27) | 21 | 17 | 2 | 3 | 24 |
| hitShip | method | [49:5 até 54](../../src/main/kof/sifuture/game/BossWeapons.kf:49) | 6 | 4 | 1 | 2 | 8 |
| advance | method | [56:5 até 59](../../src/main/kof/sifuture/game/BossWeapons.kf:56) | 4 | 3 | 1 | 1 | 4 |

### src/main/kof/sifuture/game/Credits.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Credits | constructor | [10:5 até 10](../../src/main/kof/sifuture/game/Credits.kf:10) | 1 | 1 | 0 | 0 | 0 |
| advance | method | [12:5 até 25](../../src/main/kof/sifuture/game/Credits.kf:12) | 14 | 7 | 0 | 2 | 13 |

### src/main/kof/sifuture/game/Game.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Game | constructor | [31:5 até 36](../../src/main/kof/sifuture/game/Game.kf:31) | 6 | 1 | 0 | 0 | 4 |
| clearMovement | method | [38:5 até 44](../../src/main/kof/sifuture/game/Game.kf:38) | 7 | 1 | 0 | 0 | 5 |
| clearKeyboard | method | [46:5 até 48](../../src/main/kof/sifuture/game/Game.kf:46) | 3 | 2 | 0 | 1 | 2 |
| rearmKeyboard | method | [50:5 até 56](../../src/main/kof/sifuture/game/Game.kf:50) | 7 | 2 | 0 | 1 | 6 |
| keyboard | method | [58:5 até 60](../../src/main/kof/sifuture/game/Game.kf:58) | 3 | 1 | 2 | 0 | 1 |
| keyboard | method | [62:5 até 75](../../src/main/kof/sifuture/game/Game.kf:62) | 14 | 15 | 3 | 1 | 23 |
| padPressed | method | [77:5 até 79](../../src/main/kof/sifuture/game/Game.kf:77) | 3 | 4 | 0 | 0 | 1 |
| movement | method | [81:5 até 107](../../src/main/kof/sifuture/game/Game.kf:81) | 27 | 26 | 2 | 2 | 34 |
| start | method | [109:5 até 125](../../src/main/kof/sifuture/game/Game.kf:109) | 17 | 3 | 1 | 1 | 17 |
| navigate | method | [127:5 até 136](../../src/main/kof/sifuture/game/Game.kf:127) | 10 | 11 | 1 | 2 | 12 |
| openControls | method | [138:5 até 140](../../src/main/kof/sifuture/game/Game.kf:138) | 3 | 2 | 0 | 1 | 4 |
| confirm | method | [142:5 até 148](../../src/main/kof/sifuture/game/Game.kf:142) | 7 | 5 | 0 | 1 | 4 |
| confirm | method | [150:5 até 167](../../src/main/kof/sifuture/game/Game.kf:150) | 18 | 11 | 1 | 2 | 20 |
| enterMenu | method | [169:5 até 175](../../src/main/kof/sifuture/game/Game.kf:169) | 7 | 2 | 1 | 1 | 6 |
| abandon | method | [177:5 até 181](../../src/main/kof/sifuture/game/Game.kf:177) | 5 | 2 | 0 | 1 | 2 |
| restart | method | [183:5 até 185](../../src/main/kof/sifuture/game/Game.kf:183) | 3 | 2 | 1 | 1 | 2 |
| pause | method | [187:5 até 189](../../src/main/kof/sifuture/game/Game.kf:187) | 3 | 2 | 0 | 1 | 4 |
| resume | method | [191:5 até 193](../../src/main/kof/sifuture/game/Game.kf:191) | 3 | 2 | 0 | 1 | 3 |
| step | method | [195:5 até 306](../../src/main/kof/sifuture/game/Game.kf:195) | 108 | 55 | 0 | 3 | 115 |
| canSpecial | method | [308:5 até 310](../../src/main/kof/sifuture/game/Game.kf:308) | 3 | 3 | 0 | 0 | 1 |
| trySpecial | method | [312:5 até 315](../../src/main/kof/sifuture/game/Game.kf:312) | 4 | 2 | 0 | 1 | 3 |
| finish | method | [317:5 até 321](../../src/main/kof/sifuture/game/Game.kf:317) | 5 | 1 | 0 | 0 | 3 |
| countComplete | method | [323:5 até 323](../../src/main/kof/sifuture/game/Game.kf:323) | 1 | 1 | 0 | 0 | 1 |
| stagePosition | method | [325:5 até 329](../../src/main/kof/sifuture/game/Game.kf:325) | 5 | 2 | 0 | 1 | 4 |
| resultIndex | method | [331:5 até 336](../../src/main/kof/sifuture/game/Game.kf:331) | 6 | 4 | 0 | 1 | 7 |

### src/main/kof/sifuture/game/Item.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Item | constructor | [15:5 até 15](../../src/main/kof/sifuture/game/Item.kf:15) | 1 | 1 | 1 | 0 | 1 |
| reset | method | [17:5 até 27](../../src/main/kof/sifuture/game/Item.kf:17) | 11 | 1 | 0 | 0 | 9 |
| collect | method | [29:5 até 39](../../src/main/kof/sifuture/game/Item.kf:29) | 11 | 9 | 1 | 1 | 7 |
| advance | method | [41:5 até 59](../../src/main/kof/sifuture/game/Item.kf:41) | 19 | 8 | 0 | 4 | 17 |

### src/main/kof/sifuture/game/Lasers.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| reset | method | [6:5 até 8](../../src/main/kof/sifuture/game/Lasers.kf:6) | 3 | 2 | 0 | 1 | 2 |
| advance | method | [10:5 até 12](../../src/main/kof/sifuture/game/Lasers.kf:10) | 3 | 2 | 0 | 1 | 2 |

### src/main/kof/sifuture/game/MenuEntrance.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| MenuEntrance | constructor | [9:5 até 9](../../src/main/kof/sifuture/game/MenuEntrance.kf:9) | 1 | 1 | 0 | 0 | 0 |
| advance | method | [11:5 até 20](../../src/main/kof/sifuture/game/MenuEntrance.kf:11) | 10 | 5 | 0 | 2 | 11 |
| finish | method | [22:5 até 25](../../src/main/kof/sifuture/game/MenuEntrance.kf:22) | 4 | 1 | 0 | 0 | 2 |

### src/main/kof/sifuture/game/Meteor.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| relocate | method | [15:5 até 27](../../src/main/kof/sifuture/game/Meteor.kf:15) | 13 | 2 | 0 | 1 | 9 |
| reset | method | [29:5 até 32](../../src/main/kof/sifuture/game/Meteor.kf:29) | 4 | 1 | 0 | 0 | 2 |
| resetAfterBottomExit | method | [34:5 até 40](../../src/main/kof/sifuture/game/Meteor.kf:34) | 7 | 1 | 0 | 0 | 5 |
| clearAnimation | method | [42:5 até 49](../../src/main/kof/sifuture/game/Meteor.kf:42) | 8 | 1 | 0 | 0 | 6 |
| advance | method | [51:5 até 76](../../src/main/kof/sifuture/game/Meteor.kf:51) | 26 | 12 | 0 | 3 | 27 |
| impactFrame | method | [78:5 até 81](../../src/main/kof/sifuture/game/Meteor.kf:78) | 4 | 2 | 0 | 1 | 3 |
| touchesShip | method | [83:5 até 87](../../src/main/kof/sifuture/game/Meteor.kf:83) | 5 | 6 | 2 | 0 | 1 |
| collide | method | [89:5 até 92](../../src/main/kof/sifuture/game/Meteor.kf:89) | 4 | 1 | 0 | 0 | 2 |

### src/main/kof/sifuture/game/Ship.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| reset | method | [18:5 até 27](../../src/main/kof/sifuture/game/Ship.kf:18) | 10 | 1 | 0 | 0 | 8 |
| clearInput | method | [29:5 até 37](../../src/main/kof/sifuture/game/Ship.kf:29) | 9 | 1 | 0 | 0 | 7 |
| direction | method | [39:5 até 44](../../src/main/kof/sifuture/game/Ship.kf:39) | 6 | 9 | 2 | 2 | 16 |
| advance | method | [46:5 até 81](../../src/main/kof/sifuture/game/Ship.kf:46) | 36 | 27 | 0 | 3 | 38 |
| advanceVisual | method | [83:5 até 91](../../src/main/kof/sifuture/game/Ship.kf:83) | 9 | 5 | 0 | 2 | 8 |
| explode | method | [93:5 até 96](../../src/main/kof/sifuture/game/Ship.kf:93) | 4 | 1 | 0 | 0 | 2 |

### src/main/kof/sifuture/game/Shot.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| reset | method | [11:5 até 16](../../src/main/kof/sifuture/game/Shot.kf:11) | 6 | 1 | 0 | 0 | 4 |
| fire | method | [18:5 até 26](../../src/main/kof/sifuture/game/Shot.kf:18) | 9 | 2 | 2 | 1 | 8 |
| advance | method | [28:5 até 38](../../src/main/kof/sifuture/game/Shot.kf:28) | 11 | 4 | 0 | 2 | 9 |
| spriteFrame | method | [40:5 até 44](../../src/main/kof/sifuture/game/Shot.kf:40) | 5 | 4 | 0 | 1 | 5 |
| hitsMeteor | method | [46:5 até 51](../../src/main/kof/sifuture/game/Shot.kf:46) | 6 | 8 | 1 | 0 | 1 |
| impactAt | method | [53:5 até 57](../../src/main/kof/sifuture/game/Shot.kf:53) | 5 | 1 | 1 | 0 | 3 |

### src/main/kof/sifuture/game/SpecialBeam.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| SpecialBeam | constructor | [13:5 até 13](../../src/main/kof/sifuture/game/SpecialBeam.kf:13) | 1 | 1 | 1 | 0 | 1 |
| reset | method | [15:5 até 21](../../src/main/kof/sifuture/game/SpecialBeam.kf:15) | 7 | 1 | 0 | 0 | 5 |
| fire | method | [23:5 até 30](../../src/main/kof/sifuture/game/SpecialBeam.kf:23) | 8 | 4 | 1 | 1 | 10 |
| advance | method | [32:5 até 44](../../src/main/kof/sifuture/game/SpecialBeam.kf:32) | 13 | 8 | 0 | 2 | 15 |
| hitsMeteor | method | [46:5 até 50](../../src/main/kof/sifuture/game/SpecialBeam.kf:46) | 5 | 8 | 1 | 0 | 1 |
| beginsSubchiefContact | method | [52:5 até 61](../../src/main/kof/sifuture/game/SpecialBeam.kf:52) | 10 | 10 | 1 | 1 | 6 |
| beginsBossContact | method | [63:5 até 73](../../src/main/kof/sifuture/game/SpecialBeam.kf:63) | 11 | 12 | 1 | 1 | 6 |
| hit | method | [75:5 até 79](../../src/main/kof/sifuture/game/SpecialBeam.kf:75) | 5 | 2 | 0 | 1 | 4 |
| spriteFrame | method | [81:5 até 85](../../src/main/kof/sifuture/game/SpecialBeam.kf:81) | 5 | 3 | 0 | 1 | 5 |

### src/main/kof/sifuture/game/Subchief.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Subchief | constructor | [18:5 até 18](../../src/main/kof/sifuture/game/Subchief.kf:18) | 1 | 1 | 0 | 0 | 0 |
| reset | method | [20:5 até 32](../../src/main/kof/sifuture/game/Subchief.kf:20) | 13 | 2 | 0 | 1 | 12 |
| newDestination | method | [34:5 até 39](../../src/main/kof/sifuture/game/Subchief.kf:34) | 6 | 1 | 0 | 0 | 4 |
| touchesShip | method | [41:5 até 48](../../src/main/kof/sifuture/game/Subchief.kf:41) | 8 | 12 | 1 | 0 | 1 |
| damage | method | [50:5 até 60](../../src/main/kof/sifuture/game/Subchief.kf:50) | 11 | 3 | 1 | 1 | 9 |
| reward | method | [62:5 até 66](../../src/main/kof/sifuture/game/Subchief.kf:62) | 5 | 3 | 0 | 1 | 5 |
| advance | method | [68:5 até 72](../../src/main/kof/sifuture/game/Subchief.kf:68) | 5 | 1 | 0 | 0 | 3 |
| advanceExplosion | method | [74:5 até 87](../../src/main/kof/sifuture/game/Subchief.kf:74) | 14 | 7 | 0 | 3 | 15 |
| advanceNormal | method | [89:5 até 104](../../src/main/kof/sifuture/game/Subchief.kf:89) | 16 | 12 | 0 | 4 | 20 |
| advanceShots | method | [106:5 até 108](../../src/main/kof/sifuture/game/Subchief.kf:106) | 3 | 2 | 0 | 1 | 2 |

### src/main/kof/sifuture/game/SubchiefShot.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| SubchiefShot | constructor | [8:5 até 8](../../src/main/kof/sifuture/game/SubchiefShot.kf:8) | 1 | 1 | 0 | 0 | 0 |
| fire | method | [10:5 até 14](../../src/main/kof/sifuture/game/SubchiefShot.kf:10) | 5 | 1 | 2 | 0 | 3 |
| touchesShip | method | [16:5 até 21](../../src/main/kof/sifuture/game/SubchiefShot.kf:16) | 6 | 8 | 1 | 0 | 1 |
| advance | method | [23:5 até 27](../../src/main/kof/sifuture/game/SubchiefShot.kf:23) | 5 | 3 | 0 | 1 | 5 |

### src/main/kof/sifuture/game/Weapons.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| reset | method | [12:5 até 20](../../src/main/kof/sifuture/game/Weapons.kf:12) | 9 | 2 | 0 | 1 | 8 |
| evolve | method | [22:5 até 25](../../src/main/kof/sifuture/game/Weapons.kf:22) | 4 | 2 | 0 | 1 | 3 |
| loseOnDeath | method | [27:5 até 30](../../src/main/kof/sifuture/game/Weapons.kf:27) | 4 | 3 | 0 | 1 | 4 |
| attemptFire | method | [32:5 até 50](../../src/main/kof/sifuture/game/Weapons.kf:32) | 19 | 11 | 1 | 4 | 15 |
| hitLaser | method | [52:5 até 63](../../src/main/kof/sifuture/game/Weapons.kf:52) | 12 | 7 | 1 | 3 | 7 |
| hitBlaster | method | [65:5 até 74](../../src/main/kof/sifuture/game/Weapons.kf:65) | 10 | 4 | 1 | 2 | 6 |
| hitSpecial | method | [76:5 até 87](../../src/main/kof/sifuture/game/Weapons.kf:76) | 12 | 5 | 1 | 3 | 7 |
| hitSubchiefLaser | method | [89:5 até 103](../../src/main/kof/sifuture/game/Weapons.kf:89) | 15 | 11 | 1 | 2 | 9 |
| hitSubchiefBlaster | method | [105:5 até 115](../../src/main/kof/sifuture/game/Weapons.kf:105) | 11 | 10 | 1 | 1 | 7 |
| hitSubchiefSpecial | method | [117:5 até 129](../../src/main/kof/sifuture/game/Weapons.kf:117) | 13 | 9 | 1 | 2 | 15 |
| hitBossLaser | method | [131:5 até 146](../../src/main/kof/sifuture/game/Weapons.kf:131) | 16 | 11 | 1 | 2 | 10 |
| hitBossBlaster | method | [148:5 até 158](../../src/main/kof/sifuture/game/Weapons.kf:148) | 11 | 10 | 1 | 1 | 7 |
| hitBossSpecial | method | [160:5 até 171](../../src/main/kof/sifuture/game/Weapons.kf:160) | 12 | 8 | 1 | 2 | 14 |
| canSpecial | method | [173:5 até 177](../../src/main/kof/sifuture/game/Weapons.kf:173) | 5 | 4 | 0 | 2 | 6 |
| fireSpecial | method | [179:5 até 184](../../src/main/kof/sifuture/game/Weapons.kf:179) | 6 | 3 | 1 | 1 | 6 |
| advance | method | [186:5 até 190](../../src/main/kof/sifuture/game/Weapons.kf:186) | 5 | 2 | 0 | 1 | 4 |

### src/test/kof/sifuture/game/GameJourney.kf

| Unidade | Tipo | Local e fim | L | C | P | D | S |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| menu and pause touch directions select once per contact without becoming ship movement | test | [4:1 até 23](../../src/test/kof/sifuture/game/GameJourney.kf:4) | 20 | 4 | 0 | 0 | 18 |
| pause main menu ends attempt clears contacts and selects a clean new game | test | [25:1 até 53](../../src/test/kof/sifuture/game/GameJourney.kf:25) | 29 | 10 | 0 | 0 | 27 |
| pause restart clears evolved combat and replays an injected seed | test | [55:1 até 88](../../src/test/kof/sifuture/game/GameJourney.kf:55) | 34 | 17 | 0 | 1 | 34 |
| menu navigation clamps repeats and controls return preserves selection | test | [90:1 até 112](../../src/test/kof/sifuture/game/GameJourney.kf:90) | 23 | 2 | 0 | 0 | 21 |
| credits enter exactly at twelve wait six seconds and leave one empty frame | test | [114:1 até 143](../../src/test/kof/sifuture/game/GameJourney.kf:114) | 30 | 28 | 0 | 1 | 36 |
| application opens with credits and confirmation skips only to menu once | test | [145:1 até 159](../../src/test/kof/sifuture/game/GameJourney.kf:145) | 15 | 1 | 0 | 0 | 13 |
| finishing with right held restores normal ship while score counts and position freezes | test | [161:1 até 182](../../src/test/kof/sifuture/game/GameJourney.kf:161) | 21 | 11 | 0 | 1 | 23 |
| vertical bottom exit uses full historical range and waits inactive with clean animation | test | [184:1 até 229](../../src/test/kof/sifuture/game/GameJourney.kf:184) | 44 | 13 | 0 | 0 | 42 |
| pause and lost keyboard focus clear right image without changing opposing direction priority | test | [231:1 até 259](../../src/test/kof/sifuture/game/GameJourney.kf:231) | 28 | 11 | 0 | 2 | 30 |
| vertical initial and impact resets keep reduced range while bottom exits include both full endpoints | test | [261:1 até 309](../../src/test/kof/sifuture/game/GameJourney.kf:261) | 47 | 23 | 0 | 2 | 47 |
| four pad arrows move by axis and stop on release | test | [311:1 até 327](../../src/test/kof/sifuture/game/GameJourney.kf:311) | 17 | 4 | 0 | 1 | 15 |
| pad owns movement until held keyboard keys are released and pressed again | test | [329:1 até 351](../../src/test/kof/sifuture/game/GameJourney.kf:329) | 23 | 5 | 0 | 0 | 21 |
| pause freezes ship lasers meteors and counters then resumes without movement | test | [353:1 até 373](../../src/test/kof/sifuture/game/GameJourney.kf:353) | 21 | 8 | 0 | 1 | 21 |
| held arrow cannot restart movement after resume without a release | test | [375:1 até 390](../../src/test/kof/sifuture/game/GameJourney.kf:375) | 16 | 1 | 0 | 0 | 14 |
| arrow observed outside canvas waits for release before moving | test | [392:1 até 406](../../src/test/kof/sifuture/game/GameJourney.kf:392) | 13 | 1 | 0 | 0 | 11 |
| canvas click rearms arrows after lost release and next press moves | test | [408:1 até 423](../../src/test/kof/sifuture/game/GameJourney.kf:408) | 14 | 1 | 0 | 0 | 12 |
| canvas click preserves active pad movement and rearms keyboard | test | [425:1 até 440](../../src/test/kof/sifuture/game/GameJourney.kf:425) | 14 | 2 | 0 | 0 | 12 |
| pause holds explosion and restart frames without consuming a life | test | [442:1 até 461](../../src/test/kof/sifuture/game/GameJourney.kf:442) | 20 | 6 | 0 | 2 | 20 |
| pausing and returning from result leave no directional movement | test | [463:1 até 480](../../src/test/kof/sifuture/game/GameJourney.kf:463) | 18 | 5 | 0 | 0 | 16 |
| same seed produces the same meteors | test | [483:1 até 490](../../src/test/kof/sifuture/game/GameJourney.kf:483) | 8 | 2 | 0 | 0 | 6 |
| ship moves five units and stops at bounds and release | test | [492:1 até 514](../../src/test/kof/sifuture/game/GameJourney.kf:492) | 23 | 1 | 0 | 0 | 21 |
| normal fire starts on thirteenth step and earns five points | test | [516:1 até 530](../../src/test/kof/sifuture/game/GameJourney.kf:516) | 15 | 3 | 0 | 1 | 15 |
| three meteor hits end the attempt and result persists | test | [532:1 até 562](../../src/test/kof/sifuture/game/GameJourney.kf:532) | 31 | 14 | 0 | 2 | 36 |
| all result boundaries select a message | test | [564:1 até 578](../../src/test/kof/sifuture/game/GameJourney.kf:564) | 15 | 1 | 0 | 0 | 13 |
| initial restart is invulnerable for fifteen three-step alternations | test | [580:1 até 594](../../src/test/kof/sifuture/game/GameJourney.kf:580) | 15 | 5 | 0 | 1 | 13 |
| restart ends before collision on step forty five but fire waits | test | [596:1 até 610](../../src/test/kof/sifuture/game/GameJourney.kf:596) | 15 | 6 | 0 | 1 | 15 |
| one ship collision marks every overlapping meteor and scores once | test | [612:1 até 629](../../src/test/kof/sifuture/game/GameJourney.kf:612) | 18 | 10 | 0 | 1 | 20 |
| last pressed opposite direction wins until released | test | [631:1 até 646](../../src/test/kof/sifuture/game/GameJourney.kf:631) | 16 | 3 | 0 | 0 | 14 |
| reversed opposing keys choose the latest and restore the held key on release | test | [648:1 até 667](../../src/test/kof/sifuture/game/GameJourney.kf:648) | 18 | 6 | 0 | 1 | 18 |
| basic laser allows only one active shot and retries each thirteen normal steps | test | [669:1 até 682](../../src/test/kof/sifuture/game/GameJourney.kf:669) | 14 | 6 | 0 | 1 | 18 |
| ship collision scores once and explosion blocks movement and fire for thirty steps | test | [684:1 até 701](../../src/test/kof/sifuture/game/GameJourney.kf:684) | 18 | 8 | 0 | 1 | 16 |
| laser hit holds meteor collision images for three pairs of steps | test | [703:1 até 721](../../src/test/kof/sifuture/game/GameJourney.kf:703) | 19 | 7 | 0 | 1 | 19 |
| ship image follows horizontal direction and last opposing key | test | [723:1 até 746](../../src/test/kof/sifuture/game/GameJourney.kf:723) | 24 | 1 | 0 | 0 | 22 |
| meteor sprite advances every two steps and returns through the historical frames | test | [748:1 até 762](../../src/test/kof/sifuture/game/GameJourney.kf:748) | 15 | 2 | 0 | 1 | 15 |
| ship collision takes priority when its laser reaches the same meteor | test | [764:1 até 775](../../src/test/kof/sifuture/game/GameJourney.kf:764) | 12 | 3 | 0 | 0 | 10 |
| ship meteor collision uses meteor left edge and inclusive ship bounds | test | [777:1 até 789](../../src/test/kof/sifuture/game/GameJourney.kf:777) | 13 | 3 | 0 | 0 | 11 |
| laser meteor collision uses historical tip and bottom conditions | test | [791:1 até 808](../../src/test/kof/sifuture/game/GameJourney.kf:791) | 18 | 3 | 0 | 0 | 16 |
| laser impact remains at meteor for one rendered step without scoring twice | test | [810:1 até 826](../../src/test/kof/sifuture/game/GameJourney.kf:810) | 17 | 6 | 0 | 0 | 15 |
| background moves five units wraps at sixty and pauses | test | [828:1 até 842](../../src/test/kof/sifuture/game/GameJourney.kf:828) | 15 | 2 | 0 | 1 | 15 |
| both items start offscreen reproduce their seed and relaunch after exit | test | [844:1 até 858](../../src/test/kof/sifuture/game/GameJourney.kf:844) | 15 | 7 | 0 | 0 | 13 |
| life collection adds one life above three and ten points exactly once | test | [860:1 até 875](../../src/test/kof/sifuture/game/GameJourney.kf:860) | 15 | 8 | 0 | 1 | 15 |
| evolution collections reach level three then add special charges | test | [877:1 até 892](../../src/test/kof/sifuture/game/GameJourney.kf:877) | 16 | 6 | 0 | 2 | 16 |
| evolution cycles five frames and life travels eleven frames forward and back | test | [894:1 até 909](../../src/test/kof/sifuture/game/GameJourney.kf:894) | 16 | 6 | 0 | 1 | 20 |
| evolved laser launches one per attempt into first free slot and animates | test | [911:1 até 926](../../src/test/kof/sifuture/game/GameJourney.kf:911) | 16 | 8 | 0 | 1 | 21 |
| second evolution blaster begins after six laser cycles and third begins on step six | test | [928:1 até 948](../../src/test/kof/sifuture/game/GameJourney.kf:928) | 20 | 8 | 0 | 1 | 26 |
| blaster destroys two meteors scores once each and finishes four impact frames | test | [950:1 até 976](../../src/test/kof/sifuture/game/GameJourney.kf:950) | 26 | 10 | 0 | 1 | 26 |
| special requires active normal charged idle ship consumes on start and launches three beams | test | [978:1 até 996](../../src/test/kof/sifuture/game/GameJourney.kf:978) | 19 | 11 | 0 | 1 | 19 |
| special resists ten meteor hits shows hit and death effects without duplicate rewards | test | [998:1 até 1021](../../src/test/kof/sifuture/game/GameJourney.kf:998) | 24 | 10 | 0 | 1 | 30 |
| explosion completion loses a charge before level exactly once and never below basic | test | [1023:1 até 1042](../../src/test/kof/sifuture/game/GameJourney.kf:1023) | 20 | 12 | 0 | 2 | 25 |
| launched weapons finish after downgrade and pause freezes every moving state | test | [1044:1 até 1078](../../src/test/kof/sifuture/game/GameJourney.kf:1044) | 35 | 14 | 0 | 1 | 39 |
| one blaster collision per step retains resistance for the next meteor | test | [1080:1 até 1096](../../src/test/kof/sifuture/game/GameJourney.kf:1080) | 17 | 6 | 0 | 1 | 17 |
| special resolves one historical beam contact per step in color order | test | [1098:1 até 1116](../../src/test/kof/sifuture/game/GameJourney.kf:1098) | 19 | 5 | 0 | 1 | 21 |
| invulnerable ship cannot collect until normal and collection uses inclusive left edge | test | [1118:1 até 1133](../../src/test/kof/sifuture/game/GameJourney.kf:1118) | 16 | 4 | 0 | 0 | 14 |
| laser then blaster then special claims a contested meteor exactly once | test | [1135:1 até 1162](../../src/test/kof/sifuture/game/GameJourney.kf:1135) | 28 | 8 | 0 | 1 | 30 |
| a newly fired basic laser stays basic after evolved projectiles finish | test | [1164:1 até 1175](../../src/test/kof/sifuture/game/GameJourney.kf:1164) | 12 | 5 | 0 | 1 | 16 |
| evolved laser holds its first two launch frames for two steps each | test | [1177:1 até 1194](../../src/test/kof/sifuture/game/GameJourney.kf:1177) | 18 | 3 | 0 | 1 | 20 |
| three evolved lasers circulate together and blocked attempts still drive blaster cadence | test | [1196:1 até 1214](../../src/test/kof/sifuture/game/GameJourney.kf:1196) | 19 | 8 | 0 | 1 | 28 |
| stage moves on each tenth active step including restart and pause | test | [1217:1 até 1234](../../src/test/kof/sifuture/game/GameJourney.kf:1217) | 18 | 8 | 0 | 1 | 22 |
| full stage completes both combat explosions and resumed track without second encounters | test | [1237:1 até 1251](../../src/test/kof/sifuture/game/GameJourney.kf:1237) | 15 | 10 | 0 | 1 | 19 |
| vertical pair unlocks above position thirty and falls one unit per step | test | [1254:1 até 1278](../../src/test/kof/sifuture/game/GameJourney.kf:1254) | 25 | 11 | 0 | 0 | 23 |
| vertical impact has three moving frames and pair relaunch waits for both inactive | test | [1281:1 até 1310](../../src/test/kof/sifuture/game/GameJourney.kf:1281) | 30 | 12 | 0 | 0 | 28 |
| result counts by five to exact total then confirms in two stages | test | [1313:1 até 1345](../../src/test/kof/sifuture/game/GameJourney.kf:1313) | 33 | 11 | 0 | 0 | 31 |
| result keeps scenery and pending effects moving with frozen gameplay | test | [1348:1 até 1381](../../src/test/kof/sifuture/game/GameJourney.kf:1348) | 34 | 13 | 0 | 1 | 34 |
| vertical contacts preserve ship laser blaster special priority and one reward | test | [1384:1 até 1412](../../src/test/kof/sifuture/game/GameJourney.kf:1384) | 29 | 17 | 0 | 2 | 40 |
| same seed replays entire stage including both bosses vertical relaunch and result | test | [1414:1 até 1433](../../src/test/kof/sifuture/game/GameJourney.kf:1414) | 20 | 12 | 0 | 1 | 26 |
| defeat ends explosion without new projectiles or another loss at every weapon level | test | [1435:1 até 1464](../../src/test/kof/sifuture/game/GameJourney.kf:1435) | 29 | 16 | 0 | 3 | 31 |
| projectiles launched before defeat keep moving until all finish and stay absent | test | [1467:1 até 1507](../../src/test/kof/sifuture/game/GameJourney.kf:1467) | 40 | 20 | 0 | 2 | 48 |
| laser blaster and special impacts finish after one four and six result steps | test | [1510:1 até 1546](../../src/test/kof/sifuture/game/GameJourney.kf:1510) | 36 | 16 | 0 | 3 | 38 |
| midpoint enters once and freezes track while match and scenery continue | test | [1549:1 até 1566](../../src/test/kof/sifuture/game/GameJourney.kf:1549) | 17 | 8 | 0 | 1 | 19 |
| subchief seeded destinations movement and three shot slots use normal step clocks | test | [1569:1 até 1610](../../src/test/kof/sifuture/game/GameJourney.kf:1569) | 42 | 28 | 0 | 1 | 51 |
| prepareSubchief | function | [1612:1 até 1623](../../src/test/kof/sifuture/game/GameJourney.kf:1612) | 12 | 3 | 1 | 1 | 13 |
| subchief laser and body damage precede meteor weapons and restart is invulnerable | test | [1625:1 até 1652](../../src/test/kof/sifuture/game/GameJourney.kf:1625) | 25 | 9 | 0 | 0 | 23 |
| subchief blaster spends remaining resistance before meteor contacts | test | [1654:1 até 1670](../../src/test/kof/sifuture/game/GameJourney.kf:1654) | 16 | 5 | 0 | 1 | 14 |
| special subchief markers reapply in color order and expire after six steps | test | [1672:1 até 1709](../../src/test/kof/sifuture/game/GameJourney.kf:1672) | 35 | 19 | 0 | 1 | 40 |
| fatal subchief hit rewards once at lifetime boundaries and leaves recurring items in place | test | [1711:1 até 1744](../../src/test/kof/sifuture/game/GameJourney.kf:1711) | 33 | 22 | 0 | 4 | 40 |
| enemy shot historical corner geometry explodes normal ship and ignores restart | test | [1746:1 até 1774](../../src/test/kof/sifuture/game/GameJourney.kf:1746) | 28 | 8 | 0 | 0 | 26 |
| subchief explosion freezes track for thirty steps with historical displacement and pause | test | [1776:1 até 1814](../../src/test/kof/sifuture/game/GameJourney.kf:1776) | 39 | 21 | 0 | 3 | 48 |
| defeat during subchief encounter animates without contacts rewards or life changes and restart clears it | test | [1816:1 até 1845](../../src/test/kof/sifuture/game/GameJourney.kf:1816) | 29 | 22 | 0 | 1 | 32 |
| subchief corner geometry retains inclusive edges and rejects mere rectangle overlap | test | [1847:1 até 1877](../../src/test/kof/sifuture/game/GameJourney.kf:1847) | 31 | 5 | 0 | 1 | 29 |
| marked exhausted special beam still reapplies when next color enters contact | test | [1879:1 até 1902](../../src/test/kof/sifuture/game/GameJourney.kf:1879) | 24 | 16 | 0 | 1 | 29 |
| subchief moves one unit on both axes and arrival selects reproducible new destination | test | [1904:1 até 1925](../../src/test/kof/sifuture/game/GameJourney.kf:1904) | 22 | 6 | 0 | 0 | 20 |
| simultaneous fatal contacts preserve ship laser blaster special precedence | test | [1928:1 até 1952](../../src/test/kof/sifuture/game/GameJourney.kf:1928) | 24 | 7 | 0 | 2 | 28 |
| prepareAudit | function | [1954:1 até 1966](../../src/test/kof/sifuture/game/GameJourney.kf:1954) | 13 | 3 | 1 | 1 | 14 |
| prepareFatalContact | function | [1968:1 até 1978](../../src/test/kof/sifuture/game/GameJourney.kf:1968) | 11 | 6 | 2 | 2 | 13 |
| fatal contact at historical lifetime thirty keeps six hundred reward before movement or fire | test | [1980:1 até 1999](../../src/test/kof/sifuture/game/GameJourney.kf:1980) | 18 | 8 | 0 | 2 | 17 |
| fatal contact at historical lifetime sixty keeps three hundred reward before movement or fire | test | [2001:1 até 2018](../../src/test/kof/sifuture/game/GameJourney.kf:2001) | 16 | 7 | 0 | 2 | 15 |
| new enemy shot cannot collide before its historical first update | test | [2020:1 até 2032](../../src/test/kof/sifuture/game/GameJourney.kf:2020) | 13 | 4 | 0 | 0 | 11 |
| existing enemy shot outside ship cannot hit until next historical step | test | [2034:1 até 2045](../../src/test/kof/sifuture/game/GameJourney.kf:2034) | 12 | 4 | 0 | 0 | 10 |
| nonfatal contacts still move fire and increment the lifetime clock at thirty and sixty | test | [2047:1 até 2066](../../src/test/kof/sifuture/game/GameJourney.kf:2047) | 18 | 8 | 0 | 2 | 15 |
| enemy contact frees first slot for one update without colliding with its replacement | test | [2068:1 até 2088](../../src/test/kof/sifuture/game/GameJourney.kf:2068) | 19 | 6 | 0 | 1 | 19 |
| independent pad arrows combine axes and release only their own direction | test | [2091:1 até 2110](../../src/test/kof/sifuture/game/GameJourney.kf:2091) | 19 | 6 | 0 | 1 | 18 |
| duplicate pad events preserve opposite priority and ignore unheld releases | test | [2113:1 até 2137](../../src/test/kof/sifuture/game/GameJourney.kf:2113) | 24 | 6 | 0 | 1 | 23 |
| four diagonals preserve either held axis in both press and release orders | test | [2140:1 até 2181](../../src/test/kof/sifuture/game/GameJourney.kf:2140) | 42 | 14 | 0 | 5 | 42 |
| last opposite pad press wins in either axis until its own release | test | [2183:1 até 2222](../../src/test/kof/sifuture/game/GameJourney.kf:2183) | 40 | 10 | 0 | 3 | 37 |
| pausing a diagonal clears every pad arrow and requires a new press | test | [2224:1 até 2249](../../src/test/kof/sifuture/game/GameJourney.kf:2224) | 26 | 8 | 0 | 1 | 25 |
| keyboard memory stays separate while both pad axes own movement | test | [2251:1 até 2278](../../src/test/kof/sifuture/game/GameJourney.kf:2251) | 28 | 6 | 0 | 1 | 27 |
| final encounter enters at 146 advances marker to 147 and suspends track once | test | [2280:1 até 2295](../../src/test/kof/sifuture/game/GameJourney.kf:2280) | 15 | 4 | 0 | 1 | 17 |
| boss seeded spawn and destination move one unit per axis including arrival | test | [2297:1 até 2322](../../src/test/kof/sifuture/game/GameJourney.kf:2297) | 25 | 15 | 0 | 1 | 25 |
| prepareBoss | function | [2324:1 até 2336](../../src/test/kof/sifuture/game/GameJourney.kf:2324) | 13 | 3 | 1 | 1 | 14 |
| boss normal fire uses five intervals and first free slot with four occupied attempts | test | [2338:1 até 2368](../../src/test/kof/sifuture/game/GameJourney.kf:2338) | 31 | 16 | 0 | 3 | 44 |
| nonfatal boss weapon contacts evolve only below each resistance threshold preserving fire clock | test | [2370:1 até 2393](../../src/test/kof/sifuture/game/GameJourney.kf:2370) | 24 | 7 | 0 | 2 | 24 |
| boss special checks previous fire clock and prepares six frames before moving | test | [2395:1 até 2428](../../src/test/kof/sifuture/game/GameJourney.kf:2395) | 34 | 9 | 0 | 1 | 32 |
| boss body contact requires normal entities never evolves weapons and respects inclusive edges | test | [2430:1 até 2446](../../src/test/kof/sifuture/game/GameJourney.kf:2430) | 17 | 10 | 0 | 2 | 20 |
| fatal boss damage rewards once before clock increment stops firing and captures moved explosion | test | [2448:1 até 2472](../../src/test/kof/sifuture/game/GameJourney.kf:2448) | 25 | 16 | 0 | 3 | 35 |
| boss explosion displays short first frame then three-step frames ends at 28 and resumes 290 steps | test | [2474:1 até 2503](../../src/test/kof/sifuture/game/GameJourney.kf:2474) | 30 | 13 | 0 | 1 | 30 |
| boss enemy contacts use previous positions new reused and special preparation shots wait a step | test | [2505:1 até 2551](../../src/test/kof/sifuture/game/GameJourney.kf:2505) | 44 | 12 | 0 | 0 | 42 |
| boss absorbs inclusive meteors before player contacts with one movement and suppresses vertical relaunch | test | [2553:1 até 2581](../../src/test/kof/sifuture/game/GameJourney.kf:2553) | 29 | 11 | 0 | 1 | 26 |
| boss blaster geometry uses right edge remaining resistance and special center reapplies marked colors | test | [2583:1 até 2619](../../src/test/kof/sifuture/game/GameJourney.kf:2583) | 37 | 13 | 0 | 2 | 41 |
| boss fury frenzy and evolved shots keep historical sprite cadence without drawing updates | test | [2621:1 até 2644](../../src/test/kof/sifuture/game/GameJourney.kf:2621) | 24 | 8 | 0 | 1 | 28 |
| simultaneous boss hits preserve body laser blaster special priority and reward only one claimant | test | [2646:1 até 2666](../../src/test/kof/sifuture/game/GameJourney.kf:2646) | 21 | 14 | 0 | 2 | 30 |
| boss laser corner geometry is inclusive and rejects mere overlap outside the sampled edge | test | [2668:1 até 2682](../../src/test/kof/sifuture/game/GameJourney.kf:2668) | 15 | 2 | 0 | 1 | 13 |
| defeat during boss fight animates without contacts score changes or new player fire and resets all clocks | test | [2684:1 até 2711](../../src/test/kof/sifuture/game/GameJourney.kf:2684) | 28 | 21 | 0 | 1 | 30 |
| boss evolution preserves a due clock uses first free slot and jumps crossed levels on nonfatal weapons | test | [2713:1 até 2738](../../src/test/kof/sifuture/game/GameJourney.kf:2713) | 26 | 11 | 0 | 0 | 24 |
| initial boss capacity remains one with first slot occupied and second free | test | [2740:1 até 2748](../../src/test/kof/sifuture/game/GameJourney.kf:2740) | 9 | 4 | 0 | 1 | 9 |
| boss levels two and three require the special trigger even with an eligible clock | test | [2750:1 até 2760](../../src/test/kof/sifuture/game/GameJourney.kf:2750) | 11 | 3 | 0 | 1 | 9 |
| boss absorbed meteor cannot hit a normal ship at the same inclusive edge | test | [2762:1 até 2774](../../src/test/kof/sifuture/game/GameJourney.kf:2762) | 13 | 4 | 0 | 0 | 11 |
| each main menu arrival restarts its selector while staying does not | test | [2777:1 até 2822](../../src/test/kof/sifuture/game/GameJourney.kf:2777) | 45 | 19 | 0 | 1 | 47 |
| repeated controls returns start entry and can leave before braking | test | [2825:1 até 2849](../../src/test/kof/sifuture/game/GameJourney.kf:2825) | 25 | 8 | 0 | 2 | 27 |

## Todos os locais afetados pelos limites

Listas na referência preservam a dívida que a proposta deixa abaixo do limite. “Sim” indica que o finding continua acima da proposta. Tamanho não depende de outra métrica estar elevada.

### fileLines

| Local | Unidade | Valor | Acima da proposta |
| --- | --- | ---: | --- |
| [src/main/kof/sifuture/GameControls.kf:1](../../src/main/kof/sifuture/GameControls.kf:1) | file | 391 | Sim |
| [src/main/kof/sifuture/GameView.kf:1](../../src/main/kof/sifuture/GameView.kf:1) | file | 223 | Sim |
| [src/main/kof/sifuture/game/Game.kf:1](../../src/main/kof/sifuture/game/Game.kf:1) | file | 307 | Sim |
| [src/main/kof/sifuture/game/Weapons.kf:1](../../src/main/kof/sifuture/game/Weapons.kf:1) | file | 174 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:1](../../src/test/kof/sifuture/game/GameJourney.kf:1) | file | 2665 | Sim |
### functionLines

| Local | Unidade | Valor | Acima da proposta |
| --- | --- | ---: | --- |
| [src/main/kof/sifuture/ControlsGuide.kf:15](../../src/main/kof/sifuture/ControlsGuide.kf:15) | ControlsGuide | 56 | Sim |
| [src/main/kof/sifuture/GameControls.kf:73](../../src/main/kof/sifuture/GameControls.kf:73) | GameControls | 82 | Sim |
| [src/main/kof/sifuture/GameControls.kf:297](../../src/main/kof/sifuture/GameControls.kf:297) | keyChanged | 39 | Sim |
| [src/main/kof/sifuture/GameControls.kf:355](../../src/main/kof/sifuture/GameControls.kf:355) | update | 57 | Sim |
| [src/main/kof/sifuture/GameView.kf:41](../../src/main/kof/sifuture/GameView.kf:41) | GameView | 35 | Sim |
| [src/main/kof/sifuture/GameView.kf:77](../../src/main/kof/sifuture/GameView.kf:77) | render | 87 | Sim |
| [src/main/kof/sifuture/game/Game.kf:81](../../src/main/kof/sifuture/game/Game.kf:81) | movement | 27 | Sim |
| [src/main/kof/sifuture/game/Game.kf:195](../../src/main/kof/sifuture/game/Game.kf:195) | step | 108 | Sim |
| [src/main/kof/sifuture/game/Meteor.kf:51](../../src/main/kof/sifuture/game/Meteor.kf:51) | advance | 26 | Sim |
| [src/main/kof/sifuture/game/Ship.kf:46](../../src/main/kof/sifuture/game/Ship.kf:46) | advance | 36 | Sim |
### complexity

| Local | Unidade | Valor | Acima da proposta |
| --- | --- | ---: | --- |
| [src/main/kof/sifuture/GameControls.kf:198](../../src/main/kof/sifuture/GameControls.kf:198) | updateSurfaceFocus | 7 | Não |
| [src/main/kof/sifuture/GameControls.kf:267](../../src/main/kof/sifuture/GameControls.kf:267) | optionAvailable | 6 | Não |
| [src/main/kof/sifuture/GameControls.kf:297](../../src/main/kof/sifuture/GameControls.kf:297) | keyChanged | 33 | Sim |
| [src/main/kof/sifuture/GameControls.kf:337](../../src/main/kof/sifuture/GameControls.kf:337) | updateSpecial | 9 | Não |
| [src/main/kof/sifuture/GameControls.kf:355](../../src/main/kof/sifuture/GameControls.kf:355) | update | 19 | Sim |
| [src/main/kof/sifuture/GameView.kf:77](../../src/main/kof/sifuture/GameView.kf:77) | render | 43 | Sim |
| [src/main/kof/sifuture/GameView.kf:207](../../src/main/kof/sifuture/GameView.kf:207) | drawResult | 6 | Não |
| [src/main/kof/sifuture/game/Blaster.kf:32](../../src/main/kof/sifuture/game/Blaster.kf:32) | hitsMeteor | 8 | Não |
| [src/main/kof/sifuture/game/Blaster.kf:40](../../src/main/kof/sifuture/game/Blaster.kf:40) | advance | 9 | Não |
| [src/main/kof/sifuture/game/Boss.kf:46](../../src/main/kof/sifuture/game/Boss.kf:46) | absorbMeteors | 10 | Não |
| [src/main/kof/sifuture/game/Boss.kf:55](../../src/main/kof/sifuture/game/Boss.kf:55) | touchesShip | 8 | Não |
| [src/main/kof/sifuture/game/Boss.kf:79](../../src/main/kof/sifuture/game/Boss.kf:79) | evolveWeapons | 10 | Não |
| [src/main/kof/sifuture/game/Boss.kf:111](../../src/main/kof/sifuture/game/Boss.kf:111) | advance | 14 | Não |
| [src/main/kof/sifuture/game/BossShot.kf:27](../../src/main/kof/sifuture/game/BossShot.kf:27) | touchesShip | 8 | Não |
| [src/main/kof/sifuture/game/BossSpecial.kf:23](../../src/main/kof/sifuture/game/BossSpecial.kf:23) | touchesShip | 9 | Não |
| [src/main/kof/sifuture/game/BossWeapons.kf:27](../../src/main/kof/sifuture/game/BossWeapons.kf:27) | attemptFire | 17 | Sim |
| [src/main/kof/sifuture/game/Credits.kf:12](../../src/main/kof/sifuture/game/Credits.kf:12) | advance | 7 | Não |
| [src/main/kof/sifuture/game/Game.kf:62](../../src/main/kof/sifuture/game/Game.kf:62) | keyboard | 15 | Não |
| [src/main/kof/sifuture/game/Game.kf:81](../../src/main/kof/sifuture/game/Game.kf:81) | movement | 26 | Sim |
| [src/main/kof/sifuture/game/Game.kf:127](../../src/main/kof/sifuture/game/Game.kf:127) | navigate | 11 | Não |
| [src/main/kof/sifuture/game/Game.kf:150](../../src/main/kof/sifuture/game/Game.kf:150) | confirm | 11 | Não |
| [src/main/kof/sifuture/game/Game.kf:195](../../src/main/kof/sifuture/game/Game.kf:195) | step | 55 | Sim |
| [src/main/kof/sifuture/game/Item.kf:29](../../src/main/kof/sifuture/game/Item.kf:29) | collect | 9 | Não |
| [src/main/kof/sifuture/game/Item.kf:41](../../src/main/kof/sifuture/game/Item.kf:41) | advance | 8 | Não |
| [src/main/kof/sifuture/game/Meteor.kf:51](../../src/main/kof/sifuture/game/Meteor.kf:51) | advance | 12 | Não |
| [src/main/kof/sifuture/game/Meteor.kf:83](../../src/main/kof/sifuture/game/Meteor.kf:83) | touchesShip | 6 | Não |
| [src/main/kof/sifuture/game/Ship.kf:39](../../src/main/kof/sifuture/game/Ship.kf:39) | direction | 9 | Não |
| [src/main/kof/sifuture/game/Ship.kf:46](../../src/main/kof/sifuture/game/Ship.kf:46) | advance | 27 | Sim |
| [src/main/kof/sifuture/game/Shot.kf:46](../../src/main/kof/sifuture/game/Shot.kf:46) | hitsMeteor | 8 | Não |
| [src/main/kof/sifuture/game/SpecialBeam.kf:32](../../src/main/kof/sifuture/game/SpecialBeam.kf:32) | advance | 8 | Não |
| [src/main/kof/sifuture/game/SpecialBeam.kf:46](../../src/main/kof/sifuture/game/SpecialBeam.kf:46) | hitsMeteor | 8 | Não |
| [src/main/kof/sifuture/game/SpecialBeam.kf:52](../../src/main/kof/sifuture/game/SpecialBeam.kf:52) | beginsSubchiefContact | 10 | Não |
| [src/main/kof/sifuture/game/SpecialBeam.kf:63](../../src/main/kof/sifuture/game/SpecialBeam.kf:63) | beginsBossContact | 12 | Não |
| [src/main/kof/sifuture/game/Subchief.kf:41](../../src/main/kof/sifuture/game/Subchief.kf:41) | touchesShip | 12 | Não |
| [src/main/kof/sifuture/game/Subchief.kf:74](../../src/main/kof/sifuture/game/Subchief.kf:74) | advanceExplosion | 7 | Não |
| [src/main/kof/sifuture/game/Subchief.kf:89](../../src/main/kof/sifuture/game/Subchief.kf:89) | advanceNormal | 12 | Não |
| [src/main/kof/sifuture/game/SubchiefShot.kf:16](../../src/main/kof/sifuture/game/SubchiefShot.kf:16) | touchesShip | 8 | Não |
| [src/main/kof/sifuture/game/Weapons.kf:32](../../src/main/kof/sifuture/game/Weapons.kf:32) | attemptFire | 11 | Não |
| [src/main/kof/sifuture/game/Weapons.kf:52](../../src/main/kof/sifuture/game/Weapons.kf:52) | hitLaser | 7 | Não |
| [src/main/kof/sifuture/game/Weapons.kf:89](../../src/main/kof/sifuture/game/Weapons.kf:89) | hitSubchiefLaser | 11 | Não |
| [src/main/kof/sifuture/game/Weapons.kf:105](../../src/main/kof/sifuture/game/Weapons.kf:105) | hitSubchiefBlaster | 10 | Não |
| [src/main/kof/sifuture/game/Weapons.kf:117](../../src/main/kof/sifuture/game/Weapons.kf:117) | hitSubchiefSpecial | 9 | Não |
| [src/main/kof/sifuture/game/Weapons.kf:131](../../src/main/kof/sifuture/game/Weapons.kf:131) | hitBossLaser | 11 | Não |
| [src/main/kof/sifuture/game/Weapons.kf:148](../../src/main/kof/sifuture/game/Weapons.kf:148) | hitBossBlaster | 10 | Não |
| [src/main/kof/sifuture/game/Weapons.kf:160](../../src/main/kof/sifuture/game/Weapons.kf:160) | hitBossSpecial | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:25](../../src/test/kof/sifuture/game/GameJourney.kf:25) | pause main menu ends attempt clears contacts and selects a clean new game | 10 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:55](../../src/test/kof/sifuture/game/GameJourney.kf:55) | pause restart clears evolved combat and replays an injected seed | 17 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:114](../../src/test/kof/sifuture/game/GameJourney.kf:114) | credits enter exactly at twelve wait six seconds and leave one empty frame | 28 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:161](../../src/test/kof/sifuture/game/GameJourney.kf:161) | finishing with right held restores normal ship while score counts and position freezes | 11 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:184](../../src/test/kof/sifuture/game/GameJourney.kf:184) | vertical bottom exit uses full historical range and waits inactive with clean animation | 13 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:231](../../src/test/kof/sifuture/game/GameJourney.kf:231) | pause and lost keyboard focus clear right image without changing opposing direction priority | 11 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:261](../../src/test/kof/sifuture/game/GameJourney.kf:261) | vertical initial and impact resets keep reduced range while bottom exits include both full endpoints | 23 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:353](../../src/test/kof/sifuture/game/GameJourney.kf:353) | pause freezes ship lasers meteors and counters then resumes without movement | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:442](../../src/test/kof/sifuture/game/GameJourney.kf:442) | pause holds explosion and restart frames without consuming a life | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:532](../../src/test/kof/sifuture/game/GameJourney.kf:532) | three meteor hits end the attempt and result persists | 14 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:596](../../src/test/kof/sifuture/game/GameJourney.kf:596) | restart ends before collision on step forty five but fire waits | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:612](../../src/test/kof/sifuture/game/GameJourney.kf:612) | one ship collision marks every overlapping meteor and scores once | 10 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:648](../../src/test/kof/sifuture/game/GameJourney.kf:648) | reversed opposing keys choose the latest and restore the held key on release | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:669](../../src/test/kof/sifuture/game/GameJourney.kf:669) | basic laser allows only one active shot and retries each thirteen normal steps | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:684](../../src/test/kof/sifuture/game/GameJourney.kf:684) | ship collision scores once and explosion blocks movement and fire for thirty steps | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:703](../../src/test/kof/sifuture/game/GameJourney.kf:703) | laser hit holds meteor collision images for three pairs of steps | 7 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:810](../../src/test/kof/sifuture/game/GameJourney.kf:810) | laser impact remains at meteor for one rendered step without scoring twice | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:844](../../src/test/kof/sifuture/game/GameJourney.kf:844) | both items start offscreen reproduce their seed and relaunch after exit | 7 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:860](../../src/test/kof/sifuture/game/GameJourney.kf:860) | life collection adds one life above three and ten points exactly once | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:877](../../src/test/kof/sifuture/game/GameJourney.kf:877) | evolution collections reach level three then add special charges | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:894](../../src/test/kof/sifuture/game/GameJourney.kf:894) | evolution cycles five frames and life travels eleven frames forward and back | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:911](../../src/test/kof/sifuture/game/GameJourney.kf:911) | evolved laser launches one per attempt into first free slot and animates | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:928](../../src/test/kof/sifuture/game/GameJourney.kf:928) | second evolution blaster begins after six laser cycles and third begins on step six | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:950](../../src/test/kof/sifuture/game/GameJourney.kf:950) | blaster destroys two meteors scores once each and finishes four impact frames | 10 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:978](../../src/test/kof/sifuture/game/GameJourney.kf:978) | special requires active normal charged idle ship consumes on start and launches three beams | 11 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:998](../../src/test/kof/sifuture/game/GameJourney.kf:998) | special resists ten meteor hits shows hit and death effects without duplicate rewards | 10 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1023](../../src/test/kof/sifuture/game/GameJourney.kf:1023) | explosion completion loses a charge before level exactly once and never below basic | 12 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1044](../../src/test/kof/sifuture/game/GameJourney.kf:1044) | launched weapons finish after downgrade and pause freezes every moving state | 14 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1080](../../src/test/kof/sifuture/game/GameJourney.kf:1080) | one blaster collision per step retains resistance for the next meteor | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1135](../../src/test/kof/sifuture/game/GameJourney.kf:1135) | laser then blaster then special claims a contested meteor exactly once | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1196](../../src/test/kof/sifuture/game/GameJourney.kf:1196) | three evolved lasers circulate together and blocked attempts still drive blaster cadence | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1217](../../src/test/kof/sifuture/game/GameJourney.kf:1217) | stage moves on each tenth active step including restart and pause | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1237](../../src/test/kof/sifuture/game/GameJourney.kf:1237) | full stage completes both combat explosions and resumed track without second encounters | 10 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1254](../../src/test/kof/sifuture/game/GameJourney.kf:1254) | vertical pair unlocks above position thirty and falls one unit per step | 11 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1281](../../src/test/kof/sifuture/game/GameJourney.kf:1281) | vertical impact has three moving frames and pair relaunch waits for both inactive | 12 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1313](../../src/test/kof/sifuture/game/GameJourney.kf:1313) | result counts by five to exact total then confirms in two stages | 11 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1348](../../src/test/kof/sifuture/game/GameJourney.kf:1348) | result keeps scenery and pending effects moving with frozen gameplay | 13 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1384](../../src/test/kof/sifuture/game/GameJourney.kf:1384) | vertical contacts preserve ship laser blaster special priority and one reward | 17 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:1414](../../src/test/kof/sifuture/game/GameJourney.kf:1414) | same seed replays entire stage including both bosses vertical relaunch and result | 12 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1435](../../src/test/kof/sifuture/game/GameJourney.kf:1435) | defeat ends explosion without new projectiles or another loss at every weapon level | 16 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1467](../../src/test/kof/sifuture/game/GameJourney.kf:1467) | projectiles launched before defeat keep moving until all finish and stay absent | 20 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:1510](../../src/test/kof/sifuture/game/GameJourney.kf:1510) | laser blaster and special impacts finish after one four and six result steps | 16 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1549](../../src/test/kof/sifuture/game/GameJourney.kf:1549) | midpoint enters once and freezes track while match and scenery continue | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1569](../../src/test/kof/sifuture/game/GameJourney.kf:1569) | subchief seeded destinations movement and three shot slots use normal step clocks | 28 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:1625](../../src/test/kof/sifuture/game/GameJourney.kf:1625) | subchief laser and body damage precede meteor weapons and restart is invulnerable | 9 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1672](../../src/test/kof/sifuture/game/GameJourney.kf:1672) | special subchief markers reapply in color order and expire after six steps | 19 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:1711](../../src/test/kof/sifuture/game/GameJourney.kf:1711) | fatal subchief hit rewards once at lifetime boundaries and leaves recurring items in place | 22 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:1746](../../src/test/kof/sifuture/game/GameJourney.kf:1746) | enemy shot historical corner geometry explodes normal ship and ignores restart | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1776](../../src/test/kof/sifuture/game/GameJourney.kf:1776) | subchief explosion freezes track for thirty steps with historical displacement and pause | 21 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:1816](../../src/test/kof/sifuture/game/GameJourney.kf:1816) | defeat during subchief encounter animates without contacts rewards or life changes and restart clears it | 22 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:1879](../../src/test/kof/sifuture/game/GameJourney.kf:1879) | marked exhausted special beam still reapplies when next color enters contact | 16 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1904](../../src/test/kof/sifuture/game/GameJourney.kf:1904) | subchief moves one unit on both axes and arrival selects reproducible new destination | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1928](../../src/test/kof/sifuture/game/GameJourney.kf:1928) | simultaneous fatal contacts preserve ship laser blaster special precedence | 7 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1968](../../src/test/kof/sifuture/game/GameJourney.kf:1968) | prepareFatalContact | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1980](../../src/test/kof/sifuture/game/GameJourney.kf:1980) | fatal contact at historical lifetime thirty keeps six hundred reward before movement or fire | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2001](../../src/test/kof/sifuture/game/GameJourney.kf:2001) | fatal contact at historical lifetime sixty keeps three hundred reward before movement or fire | 7 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2047](../../src/test/kof/sifuture/game/GameJourney.kf:2047) | nonfatal contacts still move fire and increment the lifetime clock at thirty and sixty | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2068](../../src/test/kof/sifuture/game/GameJourney.kf:2068) | enemy contact frees first slot for one update without colliding with its replacement | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2091](../../src/test/kof/sifuture/game/GameJourney.kf:2091) | independent pad arrows combine axes and release only their own direction | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2113](../../src/test/kof/sifuture/game/GameJourney.kf:2113) | duplicate pad events preserve opposite priority and ignore unheld releases | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2140](../../src/test/kof/sifuture/game/GameJourney.kf:2140) | four diagonals preserve either held axis in both press and release orders | 14 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2183](../../src/test/kof/sifuture/game/GameJourney.kf:2183) | last opposite pad press wins in either axis until its own release | 10 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2224](../../src/test/kof/sifuture/game/GameJourney.kf:2224) | pausing a diagonal clears every pad arrow and requires a new press | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2251](../../src/test/kof/sifuture/game/GameJourney.kf:2251) | keyboard memory stays separate while both pad axes own movement | 6 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2297](../../src/test/kof/sifuture/game/GameJourney.kf:2297) | boss seeded spawn and destination move one unit per axis including arrival | 15 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2338](../../src/test/kof/sifuture/game/GameJourney.kf:2338) | boss normal fire uses five intervals and first free slot with four occupied attempts | 16 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2370](../../src/test/kof/sifuture/game/GameJourney.kf:2370) | nonfatal boss weapon contacts evolve only below each resistance threshold preserving fire clock | 7 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2395](../../src/test/kof/sifuture/game/GameJourney.kf:2395) | boss special checks previous fire clock and prepares six frames before moving | 9 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2430](../../src/test/kof/sifuture/game/GameJourney.kf:2430) | boss body contact requires normal entities never evolves weapons and respects inclusive edges | 10 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2448](../../src/test/kof/sifuture/game/GameJourney.kf:2448) | fatal boss damage rewards once before clock increment stops firing and captures moved explosion | 16 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2474](../../src/test/kof/sifuture/game/GameJourney.kf:2474) | boss explosion displays short first frame then three-step frames ends at 28 and resumes 290 steps | 13 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2505](../../src/test/kof/sifuture/game/GameJourney.kf:2505) | boss enemy contacts use previous positions new reused and special preparation shots wait a step | 12 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2553](../../src/test/kof/sifuture/game/GameJourney.kf:2553) | boss absorbs inclusive meteors before player contacts with one movement and suppresses vertical relaunch | 11 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2583](../../src/test/kof/sifuture/game/GameJourney.kf:2583) | boss blaster geometry uses right edge remaining resistance and special center reapplies marked colors | 13 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2621](../../src/test/kof/sifuture/game/GameJourney.kf:2621) | boss fury frenzy and evolved shots keep historical sprite cadence without drawing updates | 8 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2646](../../src/test/kof/sifuture/game/GameJourney.kf:2646) | simultaneous boss hits preserve body laser blaster special priority and reward only one claimant | 14 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2684](../../src/test/kof/sifuture/game/GameJourney.kf:2684) | defeat during boss fight animates without contacts score changes or new player fire and resets all clocks | 21 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:2713](../../src/test/kof/sifuture/game/GameJourney.kf:2713) | boss evolution preserves a due clock uses first free slot and jumps crossed levels on nonfatal weapons | 11 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2777](../../src/test/kof/sifuture/game/GameJourney.kf:2777) | each main menu arrival restarts its selector while staying does not | 19 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:2825](../../src/test/kof/sifuture/game/GameJourney.kf:2825) | repeated controls returns start entry and can leave before braking | 8 | Não |
### parameters

| Local | Unidade | Valor | Acima da proposta |
| --- | --- | ---: | --- |
| [src/main/kof/sifuture/GameControls.kf:232](../../src/main/kof/sifuture/GameControls.kf:232) | menuOption | 6 | Sim |
| [src/main/kof/sifuture/GameView.kf:182](../../src/main/kof/sifuture/GameView.kf:182) | drawText | 5 | Sim |
### depth

| Local | Unidade | Valor | Acima da proposta |
| --- | --- | ---: | --- |
| [src/main/kof/sifuture/GameControls.kf:297](../../src/main/kof/sifuture/GameControls.kf:297) | keyChanged | 3 | Não |
| [src/main/kof/sifuture/GameView.kf:77](../../src/main/kof/sifuture/GameView.kf:77) | render | 3 | Não |
| [src/main/kof/sifuture/game/BossWeapons.kf:27](../../src/main/kof/sifuture/game/BossWeapons.kf:27) | attemptFire | 3 | Não |
| [src/main/kof/sifuture/game/Game.kf:195](../../src/main/kof/sifuture/game/Game.kf:195) | step | 3 | Não |
| [src/main/kof/sifuture/game/Item.kf:41](../../src/main/kof/sifuture/game/Item.kf:41) | advance | 4 | Sim |
| [src/main/kof/sifuture/game/Meteor.kf:51](../../src/main/kof/sifuture/game/Meteor.kf:51) | advance | 3 | Não |
| [src/main/kof/sifuture/game/Ship.kf:46](../../src/main/kof/sifuture/game/Ship.kf:46) | advance | 3 | Não |
| [src/main/kof/sifuture/game/Subchief.kf:74](../../src/main/kof/sifuture/game/Subchief.kf:74) | advanceExplosion | 3 | Não |
| [src/main/kof/sifuture/game/Subchief.kf:89](../../src/main/kof/sifuture/game/Subchief.kf:89) | advanceNormal | 4 | Sim |
| [src/main/kof/sifuture/game/Weapons.kf:32](../../src/main/kof/sifuture/game/Weapons.kf:32) | attemptFire | 4 | Sim |
| [src/main/kof/sifuture/game/Weapons.kf:52](../../src/main/kof/sifuture/game/Weapons.kf:52) | hitLaser | 3 | Não |
| [src/main/kof/sifuture/game/Weapons.kf:76](../../src/main/kof/sifuture/game/Weapons.kf:76) | hitSpecial | 3 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1435](../../src/test/kof/sifuture/game/GameJourney.kf:1435) | defeat ends explosion without new projectiles or another loss at every weapon level | 3 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1510](../../src/test/kof/sifuture/game/GameJourney.kf:1510) | laser blaster and special impacts finish after one four and six result steps | 3 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:1711](../../src/test/kof/sifuture/game/GameJourney.kf:1711) | fatal subchief hit rewards once at lifetime boundaries and leaves recurring items in place | 4 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:1776](../../src/test/kof/sifuture/game/GameJourney.kf:1776) | subchief explosion freezes track for thirty steps with historical displacement and pause | 3 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2140](../../src/test/kof/sifuture/game/GameJourney.kf:2140) | four diagonals preserve either held axis in both press and release orders | 5 | Sim |
| [src/test/kof/sifuture/game/GameJourney.kf:2183](../../src/test/kof/sifuture/game/GameJourney.kf:2183) | last opposite pad press wins in either axis until its own release | 3 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2338](../../src/test/kof/sifuture/game/GameJourney.kf:2338) | boss normal fire uses five intervals and first free slot with four occupied attempts | 3 | Não |
| [src/test/kof/sifuture/game/GameJourney.kf:2448](../../src/test/kof/sifuture/game/GameJourney.kf:2448) | fatal boss damage rewards once before clock increment stops firing and captures moved explosion | 3 | Não |
### statements

| Local | Unidade | Valor | Acima da proposta |
| --- | --- | ---: | --- |
| [src/main/kof/sifuture/ControlsGuide.kf:15](../../src/main/kof/sifuture/ControlsGuide.kf:15) | ControlsGuide | 28 | Sim |
| [src/main/kof/sifuture/GameControls.kf:73](../../src/main/kof/sifuture/GameControls.kf:73) | GameControls | 72 | Sim |
| [src/main/kof/sifuture/GameControls.kf:157](../../src/main/kof/sifuture/GameControls.kf:157) | keyboardSurface | 20 | Sim |
| [src/main/kof/sifuture/GameControls.kf:297](../../src/main/kof/sifuture/GameControls.kf:297) | keyChanged | 48 | Sim |
| [src/main/kof/sifuture/GameControls.kf:355](../../src/main/kof/sifuture/GameControls.kf:355) | update | 58 | Sim |
| [src/main/kof/sifuture/GameView.kf:41](../../src/main/kof/sifuture/GameView.kf:41) | GameView | 33 | Sim |
| [src/main/kof/sifuture/GameView.kf:77](../../src/main/kof/sifuture/GameView.kf:77) | render | 88 | Sim |
| [src/main/kof/sifuture/GameView.kf:190](../../src/main/kof/sifuture/GameView.kf:190) | drawHud | 19 | Sim |
| [src/main/kof/sifuture/game/Blaster.kf:40](../../src/main/kof/sifuture/game/Blaster.kf:40) | advance | 18 | Sim |
| [src/main/kof/sifuture/game/Boss.kf:111](../../src/main/kof/sifuture/game/Boss.kf:111) | advance | 27 | Sim |
| [src/main/kof/sifuture/game/BossWeapons.kf:27](../../src/main/kof/sifuture/game/BossWeapons.kf:27) | attemptFire | 24 | Sim |
| [src/main/kof/sifuture/game/Game.kf:62](../../src/main/kof/sifuture/game/Game.kf:62) | keyboard | 23 | Sim |
| [src/main/kof/sifuture/game/Game.kf:81](../../src/main/kof/sifuture/game/Game.kf:81) | movement | 34 | Sim |
| [src/main/kof/sifuture/game/Game.kf:109](../../src/main/kof/sifuture/game/Game.kf:109) | start | 17 | Não |
| [src/main/kof/sifuture/game/Game.kf:150](../../src/main/kof/sifuture/game/Game.kf:150) | confirm | 20 | Sim |
| [src/main/kof/sifuture/game/Game.kf:195](../../src/main/kof/sifuture/game/Game.kf:195) | step | 115 | Sim |
| [src/main/kof/sifuture/game/Item.kf:41](../../src/main/kof/sifuture/game/Item.kf:41) | advance | 17 | Não |
| [src/main/kof/sifuture/game/Meteor.kf:51](../../src/main/kof/sifuture/game/Meteor.kf:51) | advance | 27 | Sim |
| [src/main/kof/sifuture/game/Ship.kf:39](../../src/main/kof/sifuture/game/Ship.kf:39) | direction | 16 | Não |
| [src/main/kof/sifuture/game/Ship.kf:46](../../src/main/kof/sifuture/game/Ship.kf:46) | advance | 38 | Sim |
| [src/main/kof/sifuture/game/Subchief.kf:89](../../src/main/kof/sifuture/game/Subchief.kf:89) | advanceNormal | 20 | Sim |

## Duplicação

PMD CPD 7.17.0, mínimo 50 tokens e 5 linhas por ocorrência, sem renomear identificadores/literais. Esperados e tokenizados: 25/25, falhas: zero. Foram medidos 17 grupos, listados abaixo. Grupos podem se sobrepor ou ocorrer dentro de um mesmo arquivo; não se somam como uma porcentagem de código duplicado. Semelhança de tokens não demonstra a mesma responsabilidade ou autoriza unificação.

| Grupo | Tokens | Ocorrências com linhas físicas |
| --- | ---: | --- |
| 1 | 121 | [src/test/kof/sifuture/game/GameJourney.kf:1720:13 até 1727:99](../../src/test/kof/sifuture/game/GameJourney.kf:1720); [src/test/kof/sifuture/game/GameJourney.kf:1969:5 até 1976:91](../../src/test/kof/sifuture/game/GameJourney.kf:1969) |
| 2 | 117 | [src/test/kof/sifuture/game/GameJourney.kf:1452:32 até 1460:10](../../src/test/kof/sifuture/game/GameJourney.kf:1452); [src/test/kof/sifuture/game/GameJourney.kf:1498:27 até 1506:6](../../src/test/kof/sifuture/game/GameJourney.kf:1498) |
| 3 | 114 | [src/test/kof/sifuture/game/GameJourney.kf:952:16 até 963:57](../../src/test/kof/sifuture/game/GameJourney.kf:952); [src/test/kof/sifuture/game/GameJourney.kf:1082:16 até 1092:57](../../src/test/kof/sifuture/game/GameJourney.kf:1082) |
| 4 | 69 | [src/main/kof/sifuture/game/Boss.kf:114:9 até 118:57](../../src/main/kof/sifuture/game/Boss.kf:114); [src/main/kof/sifuture/game/Subchief.kf:91:13 até 95:61](../../src/main/kof/sifuture/game/Subchief.kf:91) |
| 5 | 63 | [src/test/kof/sifuture/game/GameJourney.kf:524:5 até 528:24](../../src/test/kof/sifuture/game/GameJourney.kf:524); [src/test/kof/sifuture/game/GameJourney.kf:708:5 até 712:24](../../src/test/kof/sifuture/game/GameJourney.kf:708) |
| 6 | 63 | [src/test/kof/sifuture/game/GameJourney.kf:1141:29 até 1145:29](../../src/test/kof/sifuture/game/GameJourney.kf:1141); [src/test/kof/sifuture/game/GameJourney.kf:1392:33 até 1396:33](../../src/test/kof/sifuture/game/GameJourney.kf:1392) |
| 7 | 62 | [src/test/kof/sifuture/game/GameJourney.kf:1000:16 até 1005:37](../../src/test/kof/sifuture/game/GameJourney.kf:1000); [src/test/kof/sifuture/game/GameJourney.kf:1100:16 até 1105:37](../../src/test/kof/sifuture/game/GameJourney.kf:1100) |
| 8 | 60 | [src/main/kof/sifuture/game/Game.kf:208:28 até 212:14](../../src/main/kof/sifuture/game/Game.kf:208); [src/main/kof/sifuture/game/Game.kf:269:30 até 273:10](../../src/main/kof/sifuture/game/Game.kf:269) |
| 9 | 60 | [src/test/kof/sifuture/game/GameJourney.kf:1166:16 até 1170:46](../../src/test/kof/sifuture/game/GameJourney.kf:1166); [src/test/kof/sifuture/game/GameJourney.kf:1179:16 até 1183:46](../../src/test/kof/sifuture/game/GameJourney.kf:1179) |
| 10 | 60 | [src/test/kof/sifuture/game/GameJourney.kf:2626:5 até 2630:19](../../src/test/kof/sifuture/game/GameJourney.kf:2626); [src/test/kof/sifuture/game/GameJourney.kf:2718:5 até 2722:19](../../src/test/kof/sifuture/game/GameJourney.kf:2718) |
| 11 | 58 | [src/main/kof/sifuture/game/BossShot.kf:25:5 até 30:18](../../src/main/kof/sifuture/game/BossShot.kf:25); [src/main/kof/sifuture/game/SubchiefShot.kf:14:5 até 20:18](../../src/main/kof/sifuture/game/SubchiefShot.kf:14) |
| 12 | 58 | [src/test/kof/sifuture/game/GameJourney.kf:793:15 até 798:34](../../src/test/kof/sifuture/game/GameJourney.kf:793); [src/test/kof/sifuture/game/GameJourney.kf:812:15 até 817:34](../../src/test/kof/sifuture/game/GameJourney.kf:812) |
| 13 | 55 | [src/test/kof/sifuture/game/GameJourney.kf:184:96 até 193:14](../../src/test/kof/sifuture/game/GameJourney.kf:184); [src/test/kof/sifuture/game/GameJourney.kf:1281:90 até 1290:14](../../src/test/kof/sifuture/game/GameJourney.kf:1281) |
| 14 | 55 | [src/test/kof/sifuture/game/GameJourney.kf:2091:81 até 2099:7](../../src/test/kof/sifuture/game/GameJourney.kf:2091); [src/test/kof/sifuture/game/GameJourney.kf:2224:75 até 2231:7](../../src/test/kof/sifuture/game/GameJourney.kf:2224) |
| 15 | 54 | [src/test/kof/sifuture/game/GameJourney.kf:2148:59 até 2154:68](../../src/test/kof/sifuture/game/GameJourney.kf:2148); [src/test/kof/sifuture/game/GameJourney.kf:2189:69 até 2195:60](../../src/test/kof/sifuture/game/GameJourney.kf:2189) |
| 16 | 53 | [src/test/kof/sifuture/game/GameJourney.kf:1980:101 até 1987:30](../../src/test/kof/sifuture/game/GameJourney.kf:1980); [src/test/kof/sifuture/game/GameJourney.kf:2001:102 até 2008:30](../../src/test/kof/sifuture/game/GameJourney.kf:2001) |
| 17 | 50 | [src/test/kof/sifuture/game/GameJourney.kf:1905:18 até 1913:23](../../src/test/kof/sifuture/game/GameJourney.kf:1905); [src/test/kof/sifuture/game/GameJourney.kf:1916:98 até 1924:23](../../src/test/kof/sifuture/game/GameJourney.kf:1916) |

## Triagem de design de todos os findings de tamanho

Análise humana assistida, baseada nas chamadas, estado e invariantes visíveis; não é inferência de coesão feita pelo contador. As classificações não aprovam nem suprimem findings. Há 5 findings de arquivo e 10 de função, todos tratados abaixo. Fontes e suítes ficaram intactas.

O guia fixado de Katacombs, `scripts/guides/structural.mjs:8`, estabelece:

> Not this: splitting mid-responsibility to duck the count. Two half-files that only work together are worse than one long file.

[Fonte histórica](https://github.com/renanfranca/katacombs-kata-ts/blob/44cb39c916e9a05de561123d7b13554ee6e0a516/scripts/guides/structural.mjs#L8). Isso impede tratar uma divisão no ponto 150 como correção de design. O [training contra abstração desnecessária](../../../kof/training/anti-patterns/unnecessary-abstraction.md:48) acrescenta:

> Add a layer only when it solves a concrete problem:
> - tested swappability (interface + multiple implementations);
> - cross-cutting transaction/cleanup;
> - real shared state.

Logo, cada extração proposta abaixo precisa de um problema e de um custo de coordenação explícitos. Faltando essa justificativa, a conclusão fica limitada. O estado mutável e o construtor explícito seguem o [idioma de classes](../../../kof/training/idioms/classes.md:38); não se propõe substituir entidades mutáveis por records para satisfazer o contador.

### Correlação das dez funções com outras métricas

| Local | Linhas | Complexidade | Parâmetros | Profundidade | Statements |
| --- | ---: | ---: | ---: | ---: | ---: |
| [ControlsGuide](../../src/main/kof/sifuture/ControlsGuide.kf:15) | 56 | 1 | 0 | 0 | 28 |
| [GameControls](../../src/main/kof/sifuture/GameControls.kf:73) | 82 | 1 | 3 | 0 | 72 |
| [keyChanged](../../src/main/kof/sifuture/GameControls.kf:297) | 39 | 33 | 3 | 3 | 48 |
| [update](../../src/main/kof/sifuture/GameControls.kf:355) | 57 | 19 | 0 | 2 | 58 |
| [GameView](../../src/main/kof/sifuture/GameView.kf:41) | 35 | 1 | 1 | 0 | 33 |
| [render](../../src/main/kof/sifuture/GameView.kf:77) | 87 | 43 | 1 | 3 | 88 |
| [movement](../../src/main/kof/sifuture/game/Game.kf:81) | 27 | 26 | 2 | 2 | 34 |
| [step](../../src/main/kof/sifuture/game/Game.kf:195) | 108 | 55 | 0 | 3 | 115 |
| [advance](../../src/main/kof/sifuture/game/Meteor.kf:51) | 26 | 12 | 0 | 3 | 27 |
| [advance](../../src/main/kof/sifuture/game/Ship.kf:46) | 36 | 27 | 0 | 3 | 38 |

Os três construtores longos têm complexidade 1. `Game.step` tem 108 linhas e complexidade 55. Ambos continuam findings de tamanho: não foi criada uma fórmula exigindo tamanho e complexidade simultâneos. A diferença orienta a leitura e não elimina resultados.

### Arquivo GameControls.kf, 391 linhas

**Classificação:** responsabilidades distintas, com evidência da fronteira.

[Trecho de src/main/kof/sifuture/GameControls.kf:145](../../src/main/kof/sifuture/GameControls.kf:145):

```kof
        action = Button("Novo Jogo", () -> { this.activateAction() })
        action.setId("game-action")
        action.on("pointerdown", (e: Event) -> { this.discardEnterClick = false })
        action.on("focus", (e: Event) -> { this.actionFocused = true; action.setStyle(focusedActionStyle) })
        action.on("blur", (e: Event) -> { game.clearKeyboard(); this.actionFocused = false; this.discardEnterClick = false; action.setStyle(actionStyle) })
        root = Column(listOf(movementControls, guide.root, action))
        root.setStyle(rootStyle)
        root.on("keydown", (e: Event) -> { this.keyChanged(e.key(), e.target(), true) })
        root.on("keyup", (e: Event) -> { this.keyChanged(e.key(), e.target(), false) })
        update()
```

O arquivo compõe widgets/estilos e também implementa o protocolo temporal de entrada. O trecho liga a árvore visual a keyChanged; este altera enterHeld, oneHeld, spaceHeld e descarta clicks na transição, enquanto update projeta Screen nos mesmos widgets. A fronteira candidata é composição/apresentação versus memória de contatos, mantendo o protocolo de uma ação por pressão num só dono. Ela resolveria a necessidade de revisar retenção de teclas ao mudar apenas layout, evidenciada pelos campos de estilos e pelo fluxo separado em keyChanged. O custo seria um contrato explícito entre foco, alvos e ações; fragmentar os campos entre duas classes sem esse contrato aumentaria acoplamento. É uma candidata de design, não extração obrigatória nesta medição. As jornadas de teclado/foco são verificadas por tests/browser.py e browser_controls.py, que não foram reexecutadas neste M1; os testes de modelo JVM/JS foram.

### Arquivo GameView.kf, 223 linhas

**Classificação:** responsabilidade aparentemente coesa, sem separação justificada.

[Trecho de src/main/kof/sifuture/GameView.kf:190](../../src/main/kof/sifuture/GameView.kf:190):

```kof
    private drawHud(Game game) {
        canvas.clearRect(0, 0, Rules.WORLD_WIDTH, Rules.HEADER_HEIGHT)
        for (var x = 8; x < Rules.WORLD_WIDTH; x = x + 18) { canvas.drawImage(stageTrack, x, 0) }
        var lifeFrame = 2
        if (game.ship.lives == 1) { lifeFrame = 0 }
        if (game.ship.lives == 2) { lifeFrame = 1 }
        canvas.drawImage(lifeShips[lifeFrame], game.stagePosition(), 9)
        canvas.drawImage(stageStart, 0, 0)
        var scoreX = Rules.WORLD_WIDTH - numberWidth(game.score)
        drawNumber(game.score, scoreX, 0)
        canvas.drawImage(scoreLabel, scoreX - 24, 7)
        canvas.drawImage(lifeShips[1], 146, 21)
        canvas.drawImage(timesLabel, 140, 21)
        drawNumber(game.ship.lives, 142 - numberWidth(game.ship.lives), 21)
        if (game.weapons.charges > 0) { canvas.drawImage(specialIcon, 50, 21) }
```

O arquivo reúne assets e desenho; drawHud lê score, vidas, posição e cargas e desenha no mesmo canvas do render. drawText isola save/restore; drawNumber e drawResult são chamados para compor o quadro. A invariável é o quadro coerente com um snapshot de Game e a ordem de camadas. Ser grande não demonstra que assets e desenho precisam de donos independentes. Um catálogo de assets só seria útil com reutilização/gestão de recursos comprovada; aqui exigiria repassar referências e coordenar índices sem resolver um problema demonstrado. Mantém-se o finding e não se recomenda partir o arquivo ao meio.

### Arquivo Game.kf, 307 linhas

**Classificação:** responsabilidades distintas, com evidência da fronteira.

[Trecho de src/main/kof/sifuture/game/Game.kf:81](../../src/main/kof/sifuture/game/Game.kf:81):

```kof
    movement(Direction direction, Bool pressed) {
        if (!pressed && direction == Direction.Up) { navigationUpHeld = false }
        if (!pressed && direction == Direction.Down) { navigationDownHeld = false }
        if (screen == Screen.Menu || screen == Screen.Pause) {
            if (direction == Direction.Up && pressed && !navigationUpHeld) {
                navigationUpHeld = true
                navigate(direction)
            }
            if (direction == Direction.Down && pressed && !navigationDownHeld) {
                navigationDownHeld = true
                navigate(direction)
            }
            return
        }
```

O arquivo coordena seleção de menus, arbitragem de entrada e simulação dos encontros. movement distingue navegação de contatos da nave; step usa clocks e snapshots de combate. Uma fronteira possível é o protocolo de entrada, com dono único para navigationUpHeld/navigationDownHeld, pad e teclado. Isso reduziria o conjunto de estados que uma mudança no protocolo precisa considerar durante revisão de combate. Custo: preservar clearMovement, prioridade do pad e transições Screen de start/pause/resume/finish por uma interface explícita. Não há autorização de implementação; mover metade dos métodos e compartilhar todos os campos seria pior.

### Arquivo Weapons.kf, 174 linhas

**Classificação:** responsabilidade aparentemente coesa, sem separação justificada.

[Trecho de src/main/kof/sifuture/game/Weapons.kf:173](../../src/main/kof/sifuture/game/Weapons.kf:173):

```kof
    canSpecial(): Bool {
        if (charges == 0) { return false }
        for (var beam in beams) { if (beam.active) { return false } }
        return true
    }

    fireSpecial(Ship ship): Bool {
        if (!canSpecial()) { return false }
        for (var beam in beams) { beam.fire(ship) }
        charges = charges - 1
        return true
    }

    advance() {
        lasers.advance()
        blaster.advance()
        for (var beam in beams) { beam.advance() }
```

Weapons já compõe Lasers, Blaster e três SpecialBeam. canSpecial e fireSpecial usam o mesmo conjunto de beams e charges: a checagem de atividade e o consumo devem permanecer coerentes. attemptFire depende de level e clocks; hits compartilham os projéteis que advance move. Geometria contra Boss e Subchief tem semelhanças, mas alvos, dimensões e efeitos diferem, inclusive evolveWeapons no Boss. A contagem não prova uma nova classe necessária; uma extração que quebrasse a relação canSpecial/fireSpecial introduziria coordenação de consumo e reset. O finding permanece como dívida visível, com análise de duplicação separada.

### Arquivo GameJourney.kf, 2665 linhas

**Classificação:** informação insuficiente para concluir.

[Trecho de src/test/kof/sifuture/game/GameJourney.kf:4](../../src/test/kof/sifuture/game/GameJourney.kf:4):

```kof
test "menu and pause touch directions select once per contact without becoming ship movement" {
    var g = Game()
    g.confirm()
    g.movement(Direction.Down, true)
    assert(g.menuSelection == 1 && !g.padPressed())
    g.movement(Direction.Down, true)
    assert(g.menuSelection == 1)
    g.movement(Direction.Down, false)
```

Cada test cria seu Game local; há 114 casos e quatro helpers parametrizados (prepareSubchief, prepareAudit, prepareFatalContact, prepareBoss). A suíte contém navegação, combate e regressões de ordem. Há agrupamentos temáticos plausíveis, mas a inspeção não examinou histórico de mudanças suficiente para provar uma divisão que reduza coordenação. A interface atual do wrapper isola uma suíte por invocação e copia um arquivo selecionado, de modo que mover helpers para outra suíte pode alterar resolução/isolamento e multiplicar setup. Antes de propor separação, seria necessário definir helpers importáveis e provar as mesmas jornadas e isolamento. A exceção não cobre tamanho de arquivo, por isso o finding continua. Nenhum teste foi extraído.

### Construtor ControlsGuide, 56 linhas

**Classificação:** responsabilidade aparentemente coesa, sem separação justificada.

[Trecho de src/main/kof/sifuture/ControlsGuide.kf:58](../../src/main/kof/sifuture/ControlsGuide.kf:58):

```kof
        disclosure = Button("Mais detalhes", () -> {
            if (this.discardClick) { this.discardClick = false; return }
            this.toggle()
        })
        disclosure.setId("game-details")
        disclosure.setStyle(idle)
        disclosure.on("pointerdown", (e: Event) -> { this.discardClick = false })
        disclosure.on("focus", (e: Event) -> { disclosure.setStyle(focused) })
        disclosure.on("blur", (e: Event) -> { this.discardClick = false; disclosure.setStyle(idle) })
        root = Column(listOf(keyboardBlock, touchBlock, special, disclosure, details))
        root.setId("game-help")
        close()
```

A responsabilidade é construir um guia e instalar os handlers do disclosure. Os callbacks compartilham discardClick, disclosure e estilos; o construtor fecha o guia após ligar a árvore. A complexidade própria é 1 porque decisões dos callbacks têm conta própria. O conteúdo e a ligação dos widgets explicam o tamanho sem provar outra responsabilidade. Extrair metade da montagem apenas repassaria referências e exigiria ordenar inicialização/close; não há problema concreto demonstrado que justifique esse custo.

### Construtor GameControls, 82 linhas

**Classificação:** responsabilidade aparentemente coesa, sem separação justificada.

[Trecho de src/main/kof/sifuture/GameControls.kf:136](../../src/main/kof/sifuture/GameControls.kf:136):

```kof
        gameColumn = Column(listOf(surface, pad))
        gameColumnStyle = Style("width: 176; align-items: center; padding: 0")
        guideColumnStyle = Style("width: 248; align-items: center; padding: 0")
        gameColumn.setStyle(gameColumnStyle)
        specialColumn = Column(listOf(special))
        specialColumnStyle = Style("display: flex; width: 56; height: 220; justify-content: center; padding: 0")
        specialColumn.setStyle(specialColumnStyle)
        movementControls = Row(listOf(gameColumn, specialColumn))
        movementControls.setStyle(movementStyle)
```

A função monta e liga a árvore de controles; gameColumn, surface, pad e special são relacionados pela composição. As callbacks têm contagens próprias e capturam o mesmo estado do objeto. A responsabilidade é inicializar uma instância utilizável e chamar update depois de todos os widgets existirem. A mistura de responsabilidades do arquivo não torna este construtor automaticamente divisível: um objeto intermediário exigiria preservar a ordem de inicialização e passar widgets/estilos. Separar direcional ou apresentação pode ser avaliado junto à fronteira do arquivo, mas a análise não demonstrou pressão independente suficiente para exigir isso aqui.

### GameControls.keyChanged, 39 linhas

**Classificação:** responsabilidade aparentemente coesa, sem separação justificada.

[Trecho de src/main/kof/sifuture/GameControls.kf:305](../../src/main/kof/sifuture/GameControls.kf:305):

```kof
        if (key == " " || key == "Enter") {
            var held = enterHeld
            if (key == " ") { held = spaceHeld; spaceHeld = pressed }
            else { enterHeld = pressed }
            var freshPress = pressed && !held
            if (target == "game-action" && (pressed || key == " ")) { discardEnterClick = true }
            if (target == "game-details" && (pressed || key == " ")) { guide.discardClick = true }
            if (pressed && optionTarget(target)) { discardOptionClick = target }
            if (freshPress) {
                if (target == "game-details" && game.screen == Screen.Controls) { guide.toggle() }
```

A função arbitra um evento de tecla conforme alvo, frescor da pressão e estado retido. O trecho mostra que atualizar held e marcar descarte faz parte da mesma transição antes de confirmar. O caminho da tecla 1 e as setas usam o mesmo protocolo de origem/foco. A complexidade 33 pede revisão do protocolo, mas extrair ramos sem um contrato de atualização compartilhada pode duplicar ou reordenar consumo de eventos. Não foi demonstrado que partir keyChanged isoladamente resolveria uma responsabilidade distinta; o teste de uma ação por pressão deve orientar eventual desenho.

### GameControls.update, 57 linhas

**Classificação:** responsabilidades distintas, com evidência da fronteira.

[Trecho de src/main/kof/sifuture/GameControls.kf:355](../../src/main/kof/sifuture/GameControls.kf:355):

```kof
    update() {
        var playing = game.screen == Screen.Play
        updateSpecial()
        var menu = game.screen == Screen.Menu
        var pause = game.screen == Screen.Pause
        var navigating = menu || pause
        north.setDisabled(!playing && !navigating)
        west.setDisabled(!playing)
        east.setDisabled(!playing)
        south.setDisabled(!playing && !navigating)
        setOptionStyle(newGame, "game-new", "Novo Jogo", menu)
        setOptionStyle(controlsOption, "game-controls", "Controles", menu)
        setOptionStyle(continueOption, "game-continue", "Continuar", pause)
        setOptionStyle(restartOption, "game-restart", "Reiniciar", pause)
        setOptionStyle(mainMenu, "game-menu", "Menu principal", pause)
        if (actionFocused) { action.setStyle(focusedActionStyle) }
        else { action.setStyle(actionStyle) }
```

O início atualiza disponibilidade e opções; a segunda parte, a partir de creditsBitmap.setStyle, projeta o layout de Credits/Controls/partida. Uma separação por projeções nomeadas de tela resolveria a necessidade de percorrer estilos de todas as telas ao alterar um layout e tornaria visível a matriz de estados. Custo: manter numa única sequência updateSpecial, retenção do foco e setOptionStyle antes de aplicar o layout, sem apagar o botão focado durante uma pressão. A fronteira é disponibilidade/protocolo versus projeção visual, não o ponto da linha 25; precisa dos testes de foco retido antes de qualquer refactor.

### Construtor GameView, 35 linhas

**Classificação:** responsabilidade aparentemente coesa, sem separação justificada.

[Trecho de src/main/kof/sifuture/GameView.kf:60](../../src/main/kof/sifuture/GameView.kf:60):

```kof
        lasers = listOf(Image("assets/laser00.png"), Image("assets/laser01.png"), Image("assets/laser02.png"))
        blasters = listOf(Image("assets/ylwBlaster00.png"), Image("assets/ylwBlaster01.png"), Image("assets/ylwBlaster02.png"), Image("assets/ylwBlaster03.png"), Image("assets/ylwBlaster04.png"), Image("assets/ylwBlaster05.png"), Image("assets/ylwBlaster06.png"), Image("assets/ylwBlaster07.png"), Image("assets/ylwBlaster08.png"))
        specialFrames = listOf(Image("assets/e0.png"), Image("assets/e1.png"), Image("assets/e2.png"), Image("assets/e3.png"), Image("assets/e4.png"), Image("assets/e5.png"), Image("assets/e6.png"), Image("assets/e7.png"), Image("assets/e8.png"))
        laserImpact = Image("assets/laser03.png")
        stageStart = Image("assets/StageBeginer.png")
        stageTrack = Image("assets/StageMiddle.png")
        lifeShips = listOf(Image("assets/1lives.png"), Image("assets/2lives.png"), Image("assets/3lives.png"))
        digits = listOf(Image("assets/0.png"), Image("assets/1.png"), Image("assets/2.png"), Image("assets/3.png"), Image("assets/4.png"), Image("assets/5.png"), Image("assets/6.png"), Image("assets/7.png"), Image("assets/8.png"), Image("assets/9.png"))
```

É um catálogo de imagens atribuído uma vez à instância que desenha. Os índices de digits e lifeShips são consumidos pelo desenho e os demais arrays mantêm sequência dos sprites. Complexidade 1 e 33 statements correspondem a carregamento, não decisões ocultas. Uma classe apenas para armazenar as mesmas imagens acrescentaria acesso indireto e coordenação de índices sem problema demonstrado; tamanho sozinho não a justifica.

### GameView.render, 87 linhas

**Classificação:** responsabilidades distintas, com evidência da fronteira.

[Trecho de src/main/kof/sifuture/GameView.kf:94](../../src/main/kof/sifuture/GameView.kf:94):

```kof
            canvas.drawImage(selector, game.menuEntrance.x, 120 + game.menuSelection * 19)
            return
        }
        if (game.screen == Screen.Controls) { return }
        for (var y = Rules.HEADER_HEIGHT; y < Rules.WORLD_HEIGHT; y = y + 60) {
            for (var x = -game.background.offset; x < Rules.WORLD_WIDTH; x = x + 60) {
                canvas.drawImage(background, x, y)
            }
        }
        for (var item in game.items) {
            if (item.collected) { canvas.drawImage(itemEffects[item.effectSteps / 2], item.x, item.y) }
            else if (item.kind == ItemKind.Evolution) { canvas.drawImage(evolutionItems[item.frame], item.x, item.y) }
```

Os retornos de Menu/Controls delimitam apresentação de telas; depois há cena de combate, HUD e overlays de resultado/pausa. Helpers nomeados por camada ou tela poderiam tornar explícita a ordem de desenho e reduzir a necessidade de revisar combate ao mudar créditos/menu. Esse é o problema concreto; o custo é compartilhar assets/canvas e preservar a ordem item → inimigos → meteoros → armas → nave → HUD/overlay, incluindo clearRect e estilos. Não se propõe um renderer por entidade com novo estado mutável: a invariável continua um quadro coerente, com transformação isolada. A prova de comportamento visual permanece fora do M1, pois nenhum desenho foi alterado.

### Game.movement, 27 linhas

**Classificação:** responsabilidade aparentemente coesa, sem separação justificada.

[Trecho de src/main/kof/sifuture/game/Game.kf:95](../../src/main/kof/sifuture/game/Game.kf:95):

```kof
        var held = false
        if (direction == Direction.Left) { held = padLeft }
        if (direction == Direction.Right) { held = padRight }
        if (direction == Direction.Up) { held = padUp }
        if (direction == Direction.Down) { held = padDown }
        if (held == pressed || (pressed && screen != Screen.Play)) { return }
        if (pressed && !padPressed()) { ship.clearInput() }
        if (direction == Direction.Left) { padLeft = pressed }
        if (direction == Direction.Right) { padRight = pressed }
        if (direction == Direction.Up) { padUp = pressed }
        if (direction == Direction.Down) { padDown = pressed }
        ship.direction(direction, pressed)
```

A função converte contato do pad em uma única ação de navegação ou atualização de direção. held == pressed evita repetição; ao assumir prioridade do teclado, ship.clearInput precisa ocorrer antes da direção. Há duas telas de interpretação, mas compartilham a fronteira de pressão/soltura e os flags. A extração pode ajudar junto a um futuro dono do protocolo de entrada; não foi demonstrado benefício em dividir só estas 27 linhas. O custo seria coordenar limpeza e prioridade entre rotinas.

### Game.step, 108 linhas

**Classificação:** responsabilidades distintas, com evidência da fronteira.

[Trecho de src/main/kof/sifuture/game/Game.kf:255](../../src/main/kof/sifuture/game/Game.kf:255):

```kof
        var chiefPhaseBeforeContacts = subchief.phase
        if (subchief.touchesShip(ship)) {
            ship.explode()
            subchief.damage(1)
        }
        weapons.hitSubchiefLaser(subchief)
        weapons.hitSubchiefBlaster(subchief)
        weapons.hitSubchiefSpecial(subchief)
        if (chiefPhaseBeforeContacts == SubchiefPhase.Normal && subchief.phase == SubchiefPhase.Explosion) { score = score + subchief.reward() }
        for (var shot in subchief.shots) {
            if (shot.touchesShip(ship)) { ship.explode(); shot.active = false; break }
        }
        if (chiefPhaseBeforeContacts == SubchiefPhase.Explosion) { subchief.advanceExplosion() }
```

O método avança apresentação no resultado, clocks de fase e contatos de combate. A fronteira mais clara é o bloco Screen.Result (linhas 201–218), que avança animação sem os contatos de Play. Uma rotina para essa fase resolveria a necessidade de distinguir atualização visual de simulação ativa. Dentro do combate, chiefPhaseBeforeContacts e bossPhaseBeforeContacts preservam a fase anterior para recompensa/explosão; shipCanCollide/shipCollision preservam dano único. Extrair por quantidade de linhas quebraria facilmente a ordem corpo → laser → blaster → especial e recompensa única. Custo de qualquer separação: transportar snapshots e explicitar quais fases podem alterar vida, score, targets e clocks. Não se declara cada bloco uma classe independente; as relações de ordem são parte do domínio e os testes de contatos simultâneos precisam continuar como contrato.

### Meteor.advance, 26 linhas

**Classificação:** responsabilidade aparentemente coesa, sem separação justificada.

[Trecho de src/main/kof/sifuture/game/Meteor.kf:51](../../src/main/kof/sifuture/game/Meteor.kf:51):

```kof
    advance() {
        if (!active) { return }
        if (motion == MeteorMotion.Vertical) {
            y = y + Rules.METEOR_SPEED
            if (y > Rules.WORLD_HEIGHT) { resetAfterBottomExit(); return }
        } else { x = x - Rules.METEOR_SPEED }
        if (x < Rules.METEOR_LEFT_BOUND) {
            if (collided) {
                relocate()
            } else { reset() }
        }
        if (collided) {
            collisionSteps = collisionSteps + 1
            var hitSteps = Rules.METEOR_HIT_STEPS
            if (motion == MeteorMotion.Vertical) { hitSteps = 3 }
            if (collisionSteps == hitSteps) { reset() }
```

O passo do mesmo meteoro resolve movimento, saída/reset e animação conforme collided e motion. resetAfterBottomExit e relocate já nomeiam transições diferentes; collisionSteps/frameSteps pertencem à mesma instância e são reiniciados conjuntamente. Complexidade 12 e profundidade 3 não demonstram outra responsabilidade. Uma extração mecânica de animação obrigaria coordenar reset ocorrido durante movimento e poderia usar estado antigo. Falta problema concreto que justifique essa separação; mantém-se o finding de 26 linhas.

### Ship.advance, 36 linhas

**Classificação:** responsabilidade aparentemente coesa, sem separação justificada.

[Trecho de src/main/kof/sifuture/game/Ship.kf:46](../../src/main/kof/sifuture/game/Ship.kf:46):

```kof
    advance() {
        var exploding = phase == ShipPhase.Explosion
        var restarting = phase == ShipPhase.Restart
        if (exploding) {
            explosionSteps = explosionSteps + 1
            if (explosionSteps == Rules.SHIP_EXPLOSION_STEPS) {
                lives = lives - 1
                if (lives == 0) { phase = ShipPhase.Hidden; return }
                phase = ShipPhase.Restart
                restartFrame = 0
                x = Rules.SHIP_RESPAWN_X
                y = Rules.SHIP_START_Y
                rightFrame = false
            }
```

exploding e restarting capturam a fase no começo do passo. A mudança de fase dentro do bloco não deve automaticamente executar o próximo estágio no mesmo frame; depois movimento e limites dependem desses snapshots. Essa é a invariável temporal que conecta morte, respawn e posição. Separar “animação” e “movimento” apenas para reduzir tamanho esconderia o motivo de passar a fase anterior. Há um candidato a explicitar transições no futuro, mas sem requisitos adicionais não se demonstrou ganho que pague o custo de coordenação. O finding permanece, apoiado também pelos testes de morte/retorno do GameJourney.

## Limites da análise

As classificações são hipóteses fundamentadas para orientar M2 e revisão posterior, sem refactor do jogo, baseline de supressão, aprovação automática da dívida ou mudança de severidade. Não foi feito estudo de evolução por histórico para cada fronteira. Os testes comprovam adaptadores, contagens, limites e comportamentos exercitados; não comprovam coesão nem legitimam toda extração sugerida. Guias originais, M2–M5 e S1–S3 permanecem preservados/pendentes.
