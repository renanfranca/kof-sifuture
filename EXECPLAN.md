# Construir o primeiro ciclo jogável de SiFuture em Kof

## Execução da issue #2 — workaround de raízes de fontes

### Purpose and success

Separar aplicação e suítes sem duplicar regras. `scripts/kof_project.py` prepara árvores temporárias sem manifesto ancestral para o CLI Kof 0.5.0-beta, compila JS e executa cada suíte em JVM e JS. Os testes Chrome passam a preparar e servir sua própria saída.

### Context and limits

WORKAROUND: o CLI atual descobre uma raiz de módulo por manifesto ou ancestral comum, enquanto este projeto usa árvores canônicas separadas. A solução temporária fica apenas no SiFuture; não modifica Kof nem as regras do jogo. A validação original usou `/home/renanfranca/projects/kof/bin/kof` no SHA `317d9f6b1c3e27032cc955a05f859f6c627d9338`. Para uso e validações atuais, o padrão é a instalação `kof` do `PATH`; o checkout local serve para consulta e investigações específicas.

### Milestones

1. Migrar `src/Main.kf`, `src/GameView.kf`, `src/game/*.kf` e `src/tests/GameJourney.kf` para `src/main/kof/sifuture` e `src/test/kof/sifuture/game`; mover `src/kof.toml` à raiz. Conferir ausência de duplicatas e diff lógico restrito a pacotes/imports.
2. Criar `scripts/kof_project.py` com build, test, preparação isolada, validação de artefatos e publicação sem apagar arquivos alheios. Validar 19 cenários em cada alvo e build com `index.html`, `Default.mjs` e assets.
3. Integrar `tests/browser.py` e `tests/browser_meteor.py` ao mesmo módulo para build, servidor de porta livre e limpeza. Executar ambos sem servidor prévio.
4. Criar testes comportamentais Python, atualizar README e `.gitignore`, exercitar falhas, isolamento e alteração de fonte; reconciliar os resultados neste plano.

### Progress

- [x] Migração: arquivos Kof movidos; comparação com `HEAD` confirmou conteúdo idêntico após remover apenas pacotes/imports novos.
- [x] Automação: preparação isolada, 19/19 em JVM e JS, build com entrada, módulo e assets.
- [x] Navegador: percursos principal e meteoros passaram sem servidor manual; URL opcional também passou.
- [x] Testes e documentação: oito testes Python passaram; README e `.gitignore` atualizados.

### Validation

`python3 -m unittest discover -s tests -p 'test_kof_project.py'`; `python3 scripts/kof_project.py test --target jvm`; idem `js`; `python3 scripts/kof_project.py build --output /tmp/sifuture-game`; `python3 tests/browser.py`; `python3 tests/browser_meteor.py`. Por padrão, esses comandos escolhem `kof` do `PATH`; `--kof` e `KOF` permitem escolher outro executável. Registrar resultados observados ao fechar cada marco.

Resultado em 30/09/2026 no Kof `317d9f6b1c3e27032cc955a05f859f6c627d9338`: os seis comandos da validação original, com `KOF` apontando ao checkout, saíram com código 0; `unittest` executou oito casos; a suíte Kof teve 19/19 em cada alvo; o build produziu `index.html`, `Default.mjs` e 29 assets. O teste principal com URL de servidor já iniciado também passou. Uma suíte deliberadamente falha foi observada na execução geral sem contaminar a seleção de `GameJourney.kf`; o primeiro código de falha é preservado. Na cópia de validação, `SHIP_SPEED = 4` gerou três falhas conhecidas; restaurar `5` devolveu 19/19. Os testes cobriram bytes copiados, seleção inválida, ausência de suítes, manifesto ancestral, limpeza temporária, falha de compilação, build que retorna zero sem artefatos e preservação de arquivo alheio no destino. As versões antigas dos arquivos Kof foram comparadas byte a byte com os novos após descontar apenas declarações de pacote/import; nenhuma regra ou apresentação mudou. Nenhum JavaScript ou CSS gerado foi editado manualmente.

Validação do uso padrão pela instalação em 30/09/2026: com `KOF` desativado, `kof` do `PATH` informou `0.5.0-beta`; os oito testes Python, o build, os 19 cenários em JVM e JS e os dois testes de navegador saíram com código 0. A saída contém `index.html`, `Default.mjs` e 29 assets. As instruções atuais do README não exigem compilar Kof a partir do código-fonte; os caminhos do checkout nas seções históricas abaixo permanecem como registro dos comandos usados naquela época.

## Purpose and success

Entregar o percurso de navegador menu → Novo Jogo → partida com nave, tiros e meteoros → resultado após três vidas → menu, em Kof. Cada etapa deve ter código Kof executável, um comando de execução e um experimento pequeno para o leitor. Se a API de entrada impedir o percurso, deixar reproducer e evidência precisa, mantendo as regras e a cena executáveis onde possível.

## Context and limits

O projeto inicia apenas com `AGENTS.md` e a especificação `.agent/specifications/port-sifuture-to-kof.md`. A fonte histórica é `/home/renanfranca/projects/sifuture`; a implementação Kof está em `/home/renanfranca/projects/kof`, versão `0.4.10-beta`, SHA `ebd11a1af42b525c583c28ab444e060fae8a9c6a`. A branch de trabalho limpa `port-sifuture-to-kof` já corresponde ao pedido. Consulte os documentos Kof listados em `AGENTS.md` antes de atribuir capacidades. Este recorte omite os recursos reservados a ciclos posteriores no pedido; não declara a especificação integral concluída. Nenhum JavaScript, CSS ou DOM escrito à mão, nem alterações em `.mjs` gerado.

## Milestones

1. **Provar ferramentas, desenho e entrada.** Incluir sprites históricos mínimos em `assets/` e verificar no navegador real que `Window`, `Canvas`, `Image`, `time.interval` e eventos exibem imagem, atualizam quadros e recebem pressionamento/soltura de teclas. Aceite: desenho e evento comprovados, ou limitação documentada.
2. **Construir regras isoladas.** Criar `src/Game.kf` com testes Kof no próprio arquivo (blocos `test`, ignorados pelo build normal), mundo 176 × 220, passo 30 ms, nave 5 unidades, tiro normal automático a cada 13 passos, seis meteoros horizontais, colisões, pontos, três vidas, reinício e resultado. Preservar regras relevantes do histórico e aceitar semente injetada com `rng.seed`. Validar com `bin/kof test src/Game.kf --target jvm` e `--target js`. Aceite: testes de semente, limites, tiro, colisão, vidas, pontuação, reinício e seis fronteiras de resultado verdes.
3. **Conectar o percurso.** Criar `src/Main.kf`, copiar sprites históricos usados e incluir instruções de execução e lições por etapa no `README.md`. Validar `bin/kof build src --target=js`, servir a saída gerada por HTTP local e exercitar menu, setas com soltura, derrota, resultado persistente e Enter para voltar no Chrome. Aceite: percurso completo observado, ou bloqueio documentado sem esconder as partes executáveis.

## Progress

- [x] Fontes locais, branch, especificação e SHA identificados.
- [x] Ferramentas e prova de UI concluídas: build JS; Chrome real mostrou sprite, 30 quadros, `keydown`/`keyup` no `Input` focado.
- [x] Regras e testes concluídos: 5 testes verdes em JVM e JS; `test` fica no arquivo da regra para compilar o código real sem duplicação.
- [x] Percurso no navegador e documentação concluídos: menu, movimento/soltura, três vidas, resultado persistente e retorno testados no Chrome; instruções e limite de foco registrados.

## Validation

Correção aprovada do mesmo ciclo em Kof `0.4.10-beta` (`ebd11a1af42b525c583c28ab444e060fae8a9c6a`): 18 testes Kof JVM/JS e build JS passaram. Testes RED cobriram o 45º passo do reinício, dois meteoros simultâneos e retorno do sprite normal após soltar direita; ficaram GREEN. O percurso Chrome passou quatro vezes na porta isolada 8767 com o build atualizado, incluindo sprite, setas opostas, soltura e resultado após três vidas.

Revisão visual no Kof `0.4.10-beta` (`ebd11a1af42b525c583c28ab444e060fae8a9c6a`): 16 testes Kof passaram tanto em JVM quanto em JS; o build JS passou. O percurso Chrome passou duas vezes, inclusive a troca `Middle.png`/`Middle2.png` com teclas opostas. O fixture Kof `tests/meteor-motion.kf` também passou duas vezes no Chrome: um clique por passo confirmou o movimento horizontal durante os três quadros de impacto e o reaparecimento. O estado avança em `step()` e `render()` apenas lê os quadros.

Ampliação do ciclo em Kof `0.4.10-beta` (`ebd11a1af42b525c583c28ab444e060fae8a9c6a`): 15 testes de comportamento em JVM e JS, build JS e percurso Chrome passaram. As regras agora incluem laser básico único, precedência histórica da colisão da nave, explosão e reinício temporizados no `step()`, meteoros animados e pontuação nas duas colisões, suas fórmulas históricas e o quadro `laser03.png` de impacto. O teste de navegador espera a mudança observável da posição da nave e estabilização após `keyup`.

Comandos observados no SHA acima: `mvn -q package -DskipTests` (exit 0, Maven 3.9.11 local em `/tmp`); Chrome real servido por HTTP mostrou canvas 176 × 220, sprite não vazio, contador de quadros e `keydown`/`keyup` após clique no Input. `bin/kof test src/Game.kf --target jvm` e `--target js`: ambos exit 0, 5 testes aprovados. `bin/kof build src --target js --output /tmp/sifuture-game` (exit 0); `python3 tests/browser.py` (exit 0, percurso integral observado no Chrome real). Auditoria: a aplicação contém apenas `.kf`; Python é somente automação de teste, e não há JS/CSS nem `.mjs` escrito ou editado. `LICENSE` e `NOTICE` distinguem código e sprites históricos.

## Risks

- `Canvas` não oferece `.on(...)` na implementação inspecionada; uma composição de eventos em widget vizinho ainda precisa de prova de foco e keyup.
- O checkout Kof não tem distribuição empacotada e não há `mvn` no PATH atual. Isso pode atrasar a validação, mas o compilador deve ser preparado antes de assumir um bloqueio da linguagem.
- Recursos históricos têm direitos incertos segundo `/home/renanfranca/projects/sifuture/NOTICE`; copiar apenas os necessários e preservar aviso explícito.
- O teclado requer foco explícito no `Input`; a composição funciona depois do clique, mas não recebe Enter logo na abertura. O README orienta o jogador a selecionar o campo.

## Refatoração aprovada após o primeiro ciclo

O plano adicional em `.agent/tmp/sifuture-refactor.md` reorganiza o código sem mudar as regras: `src/game/` contém o modelo, `src/GameView.kf` contém o desenho e `src/Main.kf` contém janela/eventos. Os 18 cenários observáveis vivem em `src/tests/GameJourney.kf`; `src/kof.toml` fixa a raiz de importação para `kof test` por arquivo. `Game.step()` coordena as fases: estado anterior decide disparo; estado posterior decide colisão. A entrada de teclado vira `Direction` em Main.

Validação da refatoração em Kof `0.4.10-beta` (`ebd11a1af42b525c583c28ab444e060fae8a9c6a`):

```bash
/home/renanfranca/projects/kof/bin/kof test src/tests --target jvm
/home/renanfranca/projects/kof/bin/kof test src/tests --target js
/home/renanfranca/projects/kof/bin/kof build src --target js --output /tmp/sifuture-game
python3 tests/browser.py http://127.0.0.1:8766/
python3 tests/browser_meteor.py
```

O curso de testes ensina separar suítes; a referência de módulos e `ProjectModuleResolutionTest` fundamentam a raiz com manifesto. `training/language/types.md` descreve enums como strings, divergindo de `docs/language-reference/classes.md` e `EnumIdentityE2ETest`; JVM/JS foram provados com um módulo pequeno antes da migração.

## Conclusão da refatoração de estado e constantes

No Kof `0.5.0-beta` (`317d9f6b1c3e27032cc955a05f859f6c627d9338`), `Ship.lastX/lastY` passaram de 0/1 para `Direction`; limites da nave derivam das dimensões e os intervalos de quadros e limite da semente têm nomes em `Rules`. Um novo cenário cobre setas opostas na ordem inversa e soltura; o cenário de bordas cobre também o limite inferior. Os 19 testes passaram em JVM e JS. Durante a conversão, a mistura temporária de enum e inteiro falhou no JVM (`VerifyError`); uma fórmula temporária com `-1` falhou no cenário de bordas. Após as correções, as duas suítes ficaram verdes. Referência de classes e `EnumIdentityE2ETest` sustentam a comparação entre valores de enum, apesar da descrição antiga em `training/language/types.md`.

Validação final: `/home/renanfranca/projects/kof/bin/kof test src/tests --target jvm` e `--target js` (19/19 cada), `/home/renanfranca/projects/kof/bin/kof build src --target js --output /tmp/sifuture-game` (exit 0), `python3 tests/browser.py http://127.0.0.1:8774/` (duas passagens no build servido por HTTP), e `python3 tests/browser_meteor.py` (passou no Chrome). O checkpoint Chrome após os dois primeiros ciclos também passou. Nenhuma regra ou coordenada visual foi alterada.


## Próximo ciclo — fundo, coleta e evolução do armamento (03/10/2026)

### Purpose and acceptance

Concluir o recorte aprovado de navegador com fundo estrelado, dois itens recorrentes, vida sem teto de três, quatro níveis de armamento e especial por pressão. A [especificação](.agent/specifications/port-sifuture-to-kof.md) registra cadências, geometria, efeitos e prioridades. Chefes, música, Android e reformulação completa dos controles continuam fora deste ciclo.

### Context and decisions

Base `main` em `ac9bc1a65dced6d72f49fab06ad749c3fd21bb40`; branch `background-items-weapons`. Execução confirmada em um worker `primary`, neste chat, com `gpt-6.1-sol` / `medium`. Implementação, validação e revisão compartilham contexto; não são revisão independente. Os papéis e leases permanecem separados. Fontes Kof consultadas em `317d9f6b1c3e27032cc955a05f859f6c627d9338`; execução usa a instalação Kof `0.5.0-beta` do PATH. A versão local não informa commit em `kof info`; o registro distingue a consulta do checkout da distribuição executada e identifica o JAR por SHA-256.

O desenho lê o modelo. `Weapons` concentra nível, cargas, relógio de disparo, tentativas de laser e todos os projéteis. Itens e fundo têm estado próprio; `Game.step()` coordena avanço e colisões. A vida e a penalidade de armamento mudam juntas ao terminar a explosão. Cada família de arma procura no máximo um contato por passo, como o histórico, com prioridade nave → laser → blaster → especial e bloqueio de prêmio duplicado.

A cadência da segunda evolução usa a sexta tentativa de laser, inclusive quando os três espaços estão ocupados; o teste do blaster ocorre antes do incremento do relógio. A terceira evolução permite tentativas mais frequentes. As animações de lançamento conservam o primeiro quadro visível. Tiros já lançados continuam independentemente do nível atual.

O especial usa `e0`–`e2`, `e3`–`e5`, `e6`–`e8`; corrige caminhos inexistentes `especial*.png` e índices fora do vetor histórico. Os assets foram copiados sem transformação de `sifuture/res`; NOTICE preservado. Cabeçalho recomposto após entidades protege texto e ícone dos feixes. Botão visível à direita, 72 × 64, 16 pixels de separação; centro do direcional vazio. Pressão e teclado acionam `Game.trySpecial()`; clique nativo do botão não adiciona uma tentativa.

### Progress

- [x] TDD: fundo; spawn e relançamento; coleta única; vida 4; evolução e cargas; animações; cadência; resistência, impacto e pontuação; morte; pausa e reinício; prioridade; projéteis após regressão.
- [x] Integração Kof: cena, ícone, controles, pressão simultânea e tecla 1, repetição e tentativas recusadas sem fila.
- [x] Navegador determinístico: quadros `iten`, `life`, `effect`, laser, blaster e nove `e`; alfa parcial no último impacto do blaster; cabeçalho protegido; ordens de soltura e cancelamento de dois dedos.
- [x] Capturas em 320 e 1200 pixels da aplicação normal e da fixture; inspeção visual local.
- [x] Especificação e README atualizados, histórico anterior conservado.
- [x] Checkpoint `ab72af72471236fb336270a3b6ec8d7812dab6c4`, oito comandos iniciais aprovados e revisão estrutural sem delta de produção.
- [x] Validação final em `69301d86d915ecc2ce15f1e30a02566fa71ba7d9`: oito checks locais aprovados.
- [x] Registro versionado com SHA, ambiente, comandos, resultados e inspeção visual.
- [x] [PR #9](https://github.com/renanfranca/kof-sifuture/pull/9) aberto; [CI 37152371521](https://github.com/renanfranca/kof-sifuture/actions/runs/37152371521) aprovou resolução e 47/47 em JVM/JS.

### Validation

Inventário confirmado: `python3 scripts/kof_project.py test --target jvm` e `--target js`; `python3 tests/browser.py`; `python3 tests/browser_controls.py`; `python3 tests/browser_meteor.py`; `python3 tests/browser_weapons.py`; `python3 -m unittest discover -s tests -p 'test_kof_project.py'`; `bash tests/ci-contract.sh`, com o `yq` v4 já existente em `/tmp/kof-ci-tools` no PATH. Executor: `implement-approved-plan/scripts/run_validation.py`, com inventário e collectors em `.agent/tmp/`. CI: Resolve verified Kof e Kof tests (jvm/js). Sonar, runner de mutação e Habit excluídos por ausência de configuração; não são relatados como checks aprovados. Publicação Pages ocorre após merge, fora da entrega deste ciclo.

Durante implementação: 47/47 regras em JVM; 46/46 em JS antes do último teste de capacidade/cadência; percurso completo do novo navegador passou com Chrome `139.0.7258.154`. Cada dois ciclos houve checkpoint de controles; evidências RED/GREEN e diagnósticos ficaram em `.agent/tmp/`. O registro de fechamento substituirá estes resultados intermediários pelos resultados do executor sobre commits identificados.

Diagnóstico de validação inicial: a mensagem de checkpoint excedeu o limite de linha e o commit não ocorreu; o registro prematuro da revisão base foi invalidado por nota no fluxo, sem aceitar gate. A execução diagnóstica teve 47/47 em ambos os alvos e sete checks concluídos, mas o percurso antigo esgotou a espera por derrota espontânea. Esse critério não controla as novas coletas de vida/evolução. O percurso mantém a aplicação normal para menu, entrada e pausa e usa colisões determinísticas da fixture Kof real para morte, resultado, menu e nova partida. A validação completa será repetida após o checkpoint real.

Checkpoint real validado em 03/10/2026: `ab72af72471236fb336270a3b6ec8d7812dab6c4`, oito comandos aprovados pelo executor, 47/47 em JVM e JS, quatro percursos de Chrome, oito testes Python e contrato CI. Inspeção visual e revisão estrutural registradas em `.agent/validation/background-items-weapons.md`; nenhum refactor de produção necessário. A documentação do registro é o único delta posterior ao checkpoint.

Entrega registrada: revisão final local `69301d86d915ecc2ce15f1e30a02566fa71ba7d9`, oito comandos aprovados em 65,94 s; PR #9 e CI verde. O complemento de documentação com links repete os gates locais e CI antes de encerrar; não muda produção. Nenhum merge ou publicação foi realizado.


## Fase completa, HUD histórico e encerramento — ciclo aprovado de 04/10/2026

Base imutável: `aea3b44ae5097ef9cadd9130cfede72022a2d055`, `main`. Branch: `stage-hud-result`. Plano aprovado preservado em `.agent/tmp/stage-hud-result.md`; ledger v6 e inventário confirmado no mesmo diretório. Worker `primary`, chat `01a10698-3ee0-75b3-841c-791dcf9d1e7a`, título `stage-result-primary`, `gpt-6.1-sol`/`medium`, concentra os sete papéis. Validação e revisão compartilham contexto; Sonar, Habit e mutação estão excluídos por ausência de configuração.

- [x] Progressão derivada de `steps`: posição 5–176, 1710 passos, pausa e avanço durante explosão/reinício; percurso sem chefes.
- [x] Dois verticais nos índices 6–7, desbloqueio acima de 30, movimento, impactos de três passos, desativação, relançamento do par, colisões e reprodução por semente.
- [x] Resultado com entrada única, contagem limitada ao total exato, cenário animado e gameplay congelado; explosão concluída oculta e confirmação em duas etapas.
- [x] Dezoito assets históricos copiados byte a byte, HUD completo e resultado centralizado, NOTICE preservado.
- [x] TDD e checkpoints: 56 cenários verdes em JVM/JS; percursos de menu, controles, meteoros, armas e fase/resultado exercitados no Chrome. O novo percurso compara sprites nas larguras 320/1200 e cobre as seis fronteiras de avaliação.
- [x] Checkpoint `2d5c4d6e807bd615eea90669ba9b97afb70c1275`, nove checks iniciais aprovados e revisão estrutural concluída; nenhum refactor de produção necessário.
- Entrega após este registro: reexecutar os nove checks no head final, criar PR pronto para revisão e observar o CI terminal. SHA, comandos/resultados e links finais ficam no ledger e na descrição do PR; não fazer merge ou excluir a branch.

Inventário local confirmado: `python3 scripts/kof_project.py test --target jvm`; idem `js`; `python3 tests/browser.py`; `python3 tests/browser_controls.py`; `python3 tests/browser_meteor.py`; `python3 tests/browser_weapons.py`; `python3 tests/browser_stage.py`; `python3 -m unittest discover -s tests -p 'test_kof_project.py'`; `PATH=/tmp/kof-ci-tools:$PATH bash tests/ci-contract.sh`. CI: Resolve verified Kof e Kof tests (jvm/js). Executor e coletores preservam logs em `.agent/tmp/validation/`.

A declaração de dois construtores de `Meteor` divergiu entre JVM e JS: o emissor JS consultado escolhe apenas o construtor de maior aridade. O parâmetro default de construtor também foi rejeitado com `SEM023` nesta instalação. A implementação preserva `Meteor()` e configura os campos públicos dos dois verticais no construtor de `Game`, mantendo o estado mutável idiomático. Os 56 cenários foram executados nos dois alvos após essa decisão; não se estabelece uma regra geral de ausência de sobrecarga em Kof. Dossiê e logs locais ficam em `.agent/tmp/`.

O vídeo histórico não foi acessível. A composição foi comparada com fonte e dimensões dos assets; as capturas do Chrome foram inspecionadas. Música, Android, chefes e menus completos continuam fora deste ciclo.

Fechamento do checkpoint: `.agent/validation/stage-hud-result.md` registra comandos, 56/56 em JVM e JS, cinco percursos Chrome, oito testes Python, contrato CI e aceite visual em Chrome 139.0.7258.154 nas larguras 320/1200. O registro e este fechamento são o único delta posterior ao código validado.


## Combate com o subchefe — ciclo aprovado de 04/10/2026

Base imutável `95895ee23ac470b798f958994c1514c0f2632ce0`; branch `subchief-combat`; worker primary, chat `01a1079d-8a58-7f73-a732-acce78ff1b98`, título `sifuture-subchief-primary`, `gpt-6.1-sol`/`medium`. Implementação, validação e revisão compartilham contexto. Inventário confirmado: dez checks locais (JVM/JS, seis percursos Chrome, infraestrutura Python e contrato CI), Resolve verified Kof e Kof tests (jvm/js). Sonar/Habit/mutação excluídos por ausência de configuração.

O contrato vigente separa passos da partida e da trilha; o histórico de 1710 passos e passagem sem combate acima permanece como registro do ciclo anterior.

## Purpose and success

Adicionar o subchefe ao percurso atual: entrada na metade da fase → combate → recompensa → explosão → retomada da trilha → resultado.

Atualizar a especificação, o `EXECPLAN.md` e o aceite existente, preservando seus registros anteriores. Cada critério terá exemplos concretos, origem da expectativa, evidência demonstrada e eventuais lacunas.

## Context and limits

A base revisada é `95895ee23ac470b798f958994c1514c0f2632ce0`. Nesta sessão, os testes atuais passaram em JVM e JS:

```text
0 failed of 60 tests
1 passed, 0 failed
```

O percurso existente de fase/resultado também passou:

```text
PASS Chrome 139.0.7258.154 at 320 and 1200 pixels; repaint does not advance simulation
```

Esses resultados comprovam a base atual. O subchefe ainda não foi implementado.

A entrada histórica avança o marcador uma posição, em [StageCount.java](/home/renanfranca/projects/sifuture/src/StageCount.java:209):

```java
if (this.x == SUB_CHIEF_TIME) {
    this.subChief.activate();
    this.x ++;
}
```

Como `SUB_CHIEF_TIME` é metade da largura 176, a entrada ocorre em 88 e o marcador passa para 89. Durante combate e explosão, o histórico suspende o avanço normal da trilha. Portanto, o término fixo em 1710 passos deixa de ser o contrato deste ciclo.

Decisões confirmadas:

- Preservar a interação histórica do especial, incluindo reaplicação de dano de feixes ainda marcados quando outro inicia contato.
- Ignorar contato corporal durante o reinício invulnerável da nave. Registrar isso como exceção explícita ao original.
- Incluir somente o subchefe. Chefe final, música, Android, menus completos e reformulação dos controles continuam pendentes.

## Milestones

1. **Reconciliar os documentos existentes.** Acrescentar o ciclo à [especificação](.agent/specifications/port-sifuture-to-kof.md) e ao [EXECPLAN.md](EXECPLAN.md), substituindo apenas os contratos afetados: passagem sem combate pela metade da fase e duração fixa. Registrar a exceção de invulnerabilidade e os exemplos de aceite abaixo.

2. **Implementar entidade e progressão.** Criar uma entidade `Subchief` com estados inativo, normal e explosão, e três projéteis próprios. Separar o contador de passos da partida do avanço da trilha; manter `Game.stagePosition()` como consulta derivada. Ativar uma única vez por partida em 88, avançar para 89 e suspender a trilha até terminar a explosão. Meteoros horizontais e itens continuam; verticais já ativos terminam seu percurso, mas o par não relança enquanto o subchefe estiver ativo.

   Usar classes com campos mutáveis para posição, resistência e animação. O [idioma de classes]( /home/renanfranca/projects/kof/training/idioms/classes.md:35) orienta:

   > for **mutable state** use explicit fields + `constructor(...)`.

   O [Learn Kof]( /home/renanfranca/projects/kof/learn/07-classes-and-objects.md:65) reforça:

   > To **mutate**, use explicit public fields:

   Essa forma permite que a entidade avance seu estado e que o desenho apenas o consulte.

3. **Implementar movimento, ataques e recompensa históricos.** Adotar resistência 30; posição inicial x entre 220 e 419; y entre 30 e 193; destinos x entre 88 e 147; deslocamento de uma unidade por eixo. Tentar disparar a cada 12 passos normais, usando o primeiro dos três espaços livres; tiros avançam quatro unidades à esquerda.

   Preservar geometria e ordem das colisões conferidas no original: nave → laser → blaster → especial, antes das colisões dessas armas com meteoros. Laser e contato normal retiram uma unidade; blaster aplica sua resistência restante e a esgota. Reproduzir os marcadores históricos do especial, com intervalo de seis passos e prioridade das cores.

   A recompensa usa o contador histórico de [Subchief.java](/home/renanfranca/projects/sifuture/src/Subchief.java:157):

   ```java
   if(this.lifeTime <= 30) {
       return VALUE*2;
   }
   if(this.lifeTime <= 60) {
       return VALUE;
   }
   return VALUE/2;
   ```

   Aplicar 600, 300 ou 150 pontos uma única vez no golpe fatal. `lifeTime` avança a cada 36 passos normais; não interpretá-lo como segundos. Manter os dois itens recorrentes: o pedido histórico de lançamento não duplica nem reposiciona um item já ativo.

4. **Integrar desenho e transições.** Copiar `subchief.png` e `laser0.png` sem transformação, preservar NOTICE e reutilizar os dez sprites de explosão. Conservar os três passos por quadro e o deslocamento histórico da explosão. `GameView.render()` continua sem avançar estado. Pausa congela todos os relógios; nova partida reinicia o encontro. Na derrota do jogador, a cena continua animada, com colisões, recompensas e alterações de vidas desativadas.

## Progress

Exploração, conferência estática do original e baseline executável concluídos. Fonte e bytecode consultados concordam nas regras examinadas; o JAR histórico não foi executado.

Nenhuma fonte ou documento versionado foi alterado neste planejamento.

## Validation

Acrescentar ao [aceite de fase existente](.agent/validation/stage-hud-result.md) uma seção deste ciclo com a seguinte matriz:

| Critério | Exemplo concreto e resultado esperado |
| --- | --- |
| Entrada e trilha | Antes de 88, subchefe inativo; ao alcançar 88, ativa e marcador passa para 89. Combate e explosão mantêm 89; depois a trilha retoma, sem segundo encontro. |
| Movimento e tiros | Semente repetida reproduz posições e destinos. Tentativas nos passos 12/24/36 ocupam espaços livres; capacidade cheia impede tiro adicional. |
| Dano e invulnerabilidade | Laser: 30 → 29. Blaster intacto: 30 → 28 e resistência esgotada. Contato normal explode a nave; contato durante reinício não altera nenhum dos dois. |
| Especial histórico | Primeiro contato retira uma unidade. Outro feixe entrando enquanto o anterior permanece marcado reaplica os danos previstos pelo original; conferir também expiração, esgotamento e golpe fatal. |
| Recompensa | Contadores 30/31/60/61 produzem 600/300/300/150. Golpes posteriores e quadros da explosão não repetem pontos ou benefícios. |
| Transições | Pausar durante combate, tiros e explosão congela estado; continuar retoma. Derrota durante o encontro inicia resultado sem novo dano; nova partida limpa encontro e projéteis. |
| Apresentação | Conferir sprites, tiros, explosão, HUD sobreposto e redesenhos sem avanço, em Chrome nas larguras 320 e 1200. |

Executar testes comportamentais em JVM e JS, os cinco percursos de navegador existentes e um novo percurso determinístico do subchefe com modelo, desenho e controles reais. Atualizar os cenários que pressupõem passagem sem combate ou término em 1710 passos. Reexecutar os checks existentes de infraestrutura e CI antes da entrega.

Para cada critério, registrar teste/interação, resultado observado, SHA testado, comando, navegador e evidência persistente. Evidências geradas ficam em `.agent/tmp/`. Comparação com o vídeo histórico depende de acesso; sua ausência deve permanecer como lacuna, sem declarar fidelidade visual comprovada por ele.

Durante **três ciclos, incluindo este**, registrar brevemente no aceite:

- Divergências encontradas pelo executor antes da entrega.
- Divergências encontradas pelo chat planejador depois.
- Classificação: requisito esquecido, cenário não coberto, expectativa incorreta ou mudança de escopo.
- Esforço adicional aproximado de preparação, conferência e correção.

Avaliar antecipação dos achados e redução da correção posterior. Quantidade de testes e ausência de achados, isoladamente, não serão tratadas como demonstração de benefício.

### Execução

- [x] Inventário/distribuição confirmados, título verificado e ledger v6 criado.
- [x] Entidade, progressão e TDD: 73 cenários executados em JVM e JS.
- [x] Geometria histórica, prioridade, marcadores do especial e prêmio único.
- [x] Desenho/transições; checkpoints Chrome de controles, armas, fase e subchefe aprovados. Os seis percursos serão executados pelos gates formais.
- [x] Aceite por critério e revisão estrutural; lacuna de precedência/capacidade encontrada antes da entrega e fechada em testes.
- [x] Checkpoints `5864df41438affb45b6fabd5ad3276fbc2a21549` e `6c79a062b1b23765935a22aea539a3968e48cee8`; dez checks locais aprovados em ambos, 72 e 73 cenários respectivamente.
- Entrega: repetir os dez checks no commit final de documentação, abrir PR pronto para revisão e acompanhar Resolve verified Kof e Kof tests (jvm/js). Os SHAs finais e links específicos ficarão no PR/ledger. Não realizar merge.

A seção deste ciclo em `.agent/validation/stage-hud-result.md` preserva o histórico e associa cada critério à origem, exemplos executados, SHA e evidência persistente. A avaliação de três ciclos começa aqui; conferência posterior do planejador e ciclos 2/3 permanecem pendentes. Vídeo histórico não foi acessado.

### Conferência posterior do planejador — 04/10/2026

Head conferido `44195b03ff1f9bc3a112bb5e1608af21c76bb7f2`, PR #11. Os dez checks locais e os três checks CI selecionados passam, mas cinco cenários direcionados falham em JVM e JS contra a fonte histórica. O [aceite existente](.agent/validation/stage-hud-result.md#conferência-posterior-do-planejador--04102026) registra R1 (prêmio calculado após incremento de lifeTime), R2 (colisão dos tiros após movimento/disparo) e R3 (animação do especial não reiniciada em resistência negativa), com expectativas, resultados, classificação e esforço estimado. A conferência do planejador foi concluída; ciclos 2/3 permanecem pendentes.

- [x] Corrigir R1–R3 preservando as decisões aprovadas, incluir provas das transições na suíte versionada e repetir os checks afetados antes de fechar o aceite do ciclo. Concluído na reparação abaixo e confirmado na conferência posterior do planejador.


### Reparação R1–R3 do ciclo atual — 04/10/2026

Plano aprovado em `.agent/tmp/subchief-repair.md`; execução `subchief-repair-primary`, modelo/esforço efetivos `gpt-6.1-sol`/`medium`, todos os papéis no mesmo chat. Base imutável `44195b03ff1f9bc3a112bb5e1608af21c76bb7f2`; branch `subchief-combat`, PR #11 existente. O ledger original foi preservado e os dois deltas locais da conferência foram incorporados sem apagar seus registros.

- [x] Incorporar as cinco provas à suíte existente e observar cinco falhas em 77 testes em JVM/JS antes de alterar produção; corrigir a expectativa histórica do feixe esgotado.
- [x] Separar avanço normal, explosão e tiros; contatos precedem avanço/disparo e meteoros. Golpe fatal mantém posição, relógio e quadro zero, com prêmio único. `advance()` compõe as partes no resultado e na transição de derrota.
- [x] Reiniciar `deathSteps` após cada dano com resistência não positiva; conservar valores negativos, marcadores e cores. Sem nova reaplicação, limpar após seis passos.
- [x] Ampliar os exemplos por corpo/laser/blaster/especial, não fatal, novo/existente/reutilizado e retomada da animação. Suíte de 79 casos verde em JVM/JS durante implementação.
- [x] Confirmar desenho/modelo em Chrome 320/1200, dez checks pelo executor, revisão estrutural, evidências por SHA/CI no aceite e entrega no PR existente.

R1 permanece classificado como cenário não coberto; R2, requisito esquecido; R3, expectativa incorreta. São reparos do ciclo atual. Ciclos 2/3 e vídeo histórico continuam pendentes. Registrar preparação, conferência e correção separadamente no aceite; número de testes e gates verdes não demonstram redução do retrabalho.


Fechamento da reparação: código/suíte/fixture `c9ea48bfad8d8a3420cd168a68f2219c9d058855`, 79/79 em JVM/JS e dez checks nos gates inicial/final (151,40/151,75 s). Chrome `139.0.7258.154`, 320/1200, R1–R3, HUD e sprites reais. Revisão estrutural sem refactor adicional. [CI 37223086619](https://github.com/renanfranca/kof-sifuture/actions/runs/37223086619) verde no mesmo SHA; PR #11 atualizado, sem merge. O aceite associa os critérios a SHA/comando/resultado/navegador/jobs, preservando a conferência anterior. Complemento documental no ledger `subchief-repair-acceptance`, mesmo worker/inventário: repetirá todos os gates locais/CI antes do encerramento, porque o ledger de produção foi marcado pronto antes de incorporar os links e não admite reabertura.

Conferência posterior do planejador concluída no head `bef987ef297474996e1508c2e13843ff94054cd2`: R1–R3 atendem ao plano, sem novo desvio de implementação identificado. Reexecutados os dez checks e as cinco provas originais em ambos os alvos, todos com exit 0; 79/79 cenários em JVM/JS e Chrome 320/1200. [CI 37224091222](https://github.com/renanfranca/kof-sifuture/actions/runs/37224091222) confirmado no mesmo head, PR #11 aberto, Pages SKIPPED. O [aceite existente](.agent/validation/stage-hud-result.md#conferência-do-planejador-após-a-reparação--04102026) associa resultados, comandos, SHA, fontes, capturas e esforço estimado; vídeo e avaliação dos ciclos 2/3 continuam pendentes. Esta conferência altera somente registros, sem novo código ou commit.


Merge/publicação confirmados em 04/10/2026: PR #11 integrado como `567f6d032523fe02a0c45eebdbf345f51d70b600`. [Workflow 37229615413](https://github.com/renanfranca/kof-sifuture/actions/runs/37229615413) com os cinco jobs SUCCESS, incluindo Build/Publish Pages; JVM/JS 79/79. [Site ao vivo](https://renanfranca.github.io/kof-sifuture/) conferido em Chrome `139.0.7258.154`, 320/1200, início, movimento pelos sprites e pausa/retomada, sem erros JS/HTTP. Todos os 95 arquivos servidos correspondem ao artefato publicado. Registro completo no aceite existente, preservando os deltas locais do planejador; vídeo histórico e ciclos 2/3 permanecem pendentes.


## Ciclo aprovado: melhorar os controles no Chrome do Android — 04/10/2026

### Plano aprovado

## Resultado desejado

Usar **quatro setas em cruz**, removendo os botões diagonais. Cada botão poderá permanecer pressionado independentemente dos demais.

A decisão final desta conversa é: **entre direções opostas, vence a última pressionada**. Soltar essa direção retoma a outra ainda mantida. Direita + cima forma uma diagonal. Deslizar o dedo conserva a seta inicial até soltura ou cancelamento.

## Base verificada e implementação

Hoje, o modelo impede uma segunda direção. Em [Game.kf](/home/renanfranca/projects/kof-sifuture/src/main/kof/sifuture/game/Game.kf:65):

```kof
if (screen != Screen.Play || zone == Zone.Neutral || activeZone != Zone.Neutral) { return }
```

`activeZone` representa somente um botão ativo. Substituir esse estado por pressões independentes permite combinar os dois eixos.

A prova de planejamento compilou a fixture existente e executou touch simulado no Chrome `139.0.7258.154`: os botões → e ↑ receberam contatos distintos; as duas ordens de soltura foram conferidas. Isso demonstra a entrega dos eventos, ainda sem implementar diagonais por dois dedos.

- **Modelo:** mudar a interface para `Game.movement(Direction direction, Bool pressed)`, reutilizando as quatro direções existentes. Guardar as pressões do direcional separadamente da memória do teclado e encaminhar somente transições reais à nave. Pressões repetidas e solturas duplicadas não podem alterar a prioridade.
- **Prioridade:** reutilizar a regra atual da nave para opostos. O direcional continua prevalecendo sobre o teclado enquanto qualquer seta estiver pressionada. Soltar o último botão para o movimento; uma tecla já mantida não assume automaticamente.
- **Interface:** quatro botões de **56 × 56 px**, cruz de **168 × 168 px**, sem espaçamento interno, com centro e cantos vazios. Disposição histórica deste ciclo: Especial à direita do direcional, **72 × 64 px**, centralizado verticalmente e separado por **16 px**; essa posição foi substituída explicitamente pelo ciclo de alinhamento com o canvas abaixo. Usar janela de **296 px** de largura na aplicação e nas fixtures com esses controles para caber em viewport de 320 px.
- **Gestos:** conservar os eventos atuais de pressão, soltura, cancelamento e saída do mouse. Manter o arrasto ligado ao botão inicial; a captura implícita de touch é descrita pelo [padrão W3C](https://www.w3.org/TR/pointerevents3/#implicit-pointer-capture).
- **Documentação:** incorporar este ciclo ao `EXECPLAN.md`, preservar suas alterações pendentes e atualizar a especificação e as instruções do jogo para quatro botões com combinações.

Usar os componentes Kof existentes. A orientação de estado derivado, em [duplicate-state.md](/home/renanfranca/projects/kof/training/anti-patterns/duplicate-state.md:73), é:

> If a value can be derived from another, derive it (method or function).

Portanto, consultar se alguma direção está pressionada em vez de manter outra variável sincronizada para representar “direcional ativo”.

## Aceitação e provas planejadas

As novas expectativas vêm das escolhas desta conversa. As regressões preservam os contratos existentes de teclado, pausa e Especial.

Nos testes determinísticos, começar em `(60, 100)`, sem obstáculos próximos. Cada passo conserva o deslocamento atual de cinco unidades por eixo.

| Critério | Ação e resultado esperado | Prova planejada |
|---|---|---|
| Diagonal | → por um passo: `(65,100)`; acrescentar ↑: `(70,95)`; soltar ↑: `(75,95)`; soltar →: posição estável. | Modelo JVM/JS e dois contatos reais no Chrome; repetir as quatro diagonais e inverter a ordem das pressões e solturas. |
| Opostos | → leva a `(65,100)`; acrescentar ← leva a `(60,100)`; soltar ← retoma →. Em cenário separado, soltar → mantém ←. | Modelo e navegador, nos dois eixos e nas duas ordens. Conferir também a imagem de propulsão correspondente. |
| Eventos simultâneos | Direções de eixos diferentes sempre combinam. Para opostos iniciados juntos, vale a última pressão entregue pelo navegador. | Conferir eventos recebidos, movimento e solturas; não exigir uma ordem física entre dedos simultâneos. |
| Arrasto e cancelamento | Arrastar → sobre ↑ mantém direita. Soltar ou cancelar encerra aquela pressão. Soltar um botão não apaga outro ainda mantido. | Ampliar o percurso de touch existente; repetir cancelamento total e nova pressão. |
| Diagonal + Especial | Dois dedos mantêm a diagonal; um terceiro tenta Especial uma vez. Soltar Especial conserva a diagonal; soltar uma seta conserva a outra. | Ampliar o percurso existente de armas, conferindo posição e consumo de exatamente uma carga. |
| Pausa e teclado | Pausar limpa todas as direções; continuar exige nova pressão. Foco, Enter, tecla `1` e prioridade do direcional conservam seus contratos. | Reutilizar regressões existentes e acrescentar pausa com dois dedos mantidos. |
| Layout e conforto | Exatamente quatro setas; dimensões previstas; controles abaixo do canvas, sem sobreposição ou rolagem horizontal em 320 px. | Medições e capturas em 320/1200 px; jogar no Chrome do Android real, incluindo o combate com subchefe. |

Ampliar a observação de [browser_controls.py](/home/renanfranca/projects/kof-sifuture/tests/browser_controls.py:23) para reconhecer **posição horizontal e vertical**: hoje ela procura a nave somente em `y = 100`, o que não comprova diagonais. Conferir qual botão recebeu cada soltura simulada.

## Validação e entrega

Executar as suítes Kof em JVM e JS e os seis percursos existentes de navegador: jogo, controles, meteoros, armas, fase e subchefe. Acrescentar os novos casos aos percursos correspondentes, evitando duplicar cobertura.

Antes da entrega, o executor deverá:

- Revalidar a expectativa de cada critério contra esta conversa e os contratos citados, separadamente da qualidade das assertions.
- Registrar comando ou procedimento, resultado observado e evidência por critério em `.agent/validation/`, com SHA testado, navegador/versão e links de CI quando disponíveis.
- Guardar logs e capturas em `.agent/tmp/`, mantendo sua exclusão local exatamente uma vez.
- Declarar falhas, cobertura ausente e critérios não verificados. Touch simulado não encerra o aceite de conforto no aparelho real.

O multitouch deste ciclo cobre dedos em **botões distintos**. A dificuldade, velocidade e regras do combate permanecem as atuais. A imagem apresentada serve como referência de disposição; o aceite visual será feito sobre a interface implementada.

### Execução e evidências

- [x] Preservar os deltas documentais anteriores em commit separado (`b99cc62`); branch `android-multitouch-controls` a partir de `origin/main` `567f6d032523fe02a0c45eebdbf345f51d70b600`.
- [x] TDD: diagonal e eventos duplicados falharam por comportamento; implementação independente, quatro setas e regressões JVM/JS. Layout falhou com largura observada 48; passou com 56 e cruz 168.
- [x] Ampliar observação 2D, registrar alvo/identidade das solturas, testar matrizes de diagonais/opostos, eventos simultâneos e pausa.
- [x] Fechar regressões de Especial, gate inicial e revisão estrutural; registrar SHA e dez comandos no [aceite](.agent/validation/sifuture-controls.md). Gate inicial em `45b49487f242f7addd5243c800b7e9716c7474ad`: JVM/JS 85/85, seis percursos Chrome, infraestrutura 8/8 e contrato CI, 173,54 s. Sem refactor adicional. Gate final repete os dez checks após este complemento documental; resultado e CI serão associados à entrega no ledger/PR.
- [x] Entregar [PR #12](https://github.com/renanfranca/kof-sifuture/pull/12), sem merge. Gate final em `e358df6444e90158c96efc9e8b1f96f73682c5ca`: 10/10, 183,89 s. [CI 37237869943](https://github.com/renanfranca/kof-sifuture/actions/runs/37237869943): Resolve/JVM/JS SUCCESS, Pages SKIPPED. Este complemento documental incorpora links disponíveis e exige repetir gates locais/CI, sem mudanças de produção; resultados posteriores ficam no ledger e no PR.
- [ ] Aceite de conforto no Android real, incluindo combate com subchefe. Touch simulado não encerra este critério.

Worker `primary`: chat `01a108c9-623d-7f10-a9f5-a49eba70b808`, `gpt-6.1-sol`/`medium`; título `sifuture-controls-primary`. Implementação, validação e revisão compartilham contexto, sem independência de revisão. Dez checks locais e três checks CI confirmados; Sonar/mutação/Habit não configurados e excluídos. Plano/ledger/inventário/coletores/logs em `.agent/tmp/`, excluído localmente exatamente uma vez.


# Interromper novos disparos após a última vida

## Comportamento definido

Conforme seus esclarecimentos: ao chegar a zero vidas, a nave deixa de criar disparos. Lasers, blaster e especial já lançados continuam até terminar seu movimento ou efeito. O resultado de fase concluída com vidas restantes conserva o comportamento atual.

A causa está em [Game.kf](/home/renanfranca/projects/kof-sifuture/src/main/kof/sifuture/game/Game.kf:130):

```kof
ship.advanceVisual()
if (ship.phase == ShipPhase.Normal || ship.phase == ShipPhase.Hidden) { weapons.attemptFire(ship) }
weapons.advance()
```

A condição permite disparar com a nave oculta. `attemptFire` cria projéteis; `advance` movimenta os existentes. A correção deve restringir a primeira operação e preservar a segunda.

## Implementação

- No ramo de resultado de `Game.step()`, acrescentar `ship.lives > 0` à condição atual de `weapons.attemptFire(ship)`.
- Manter `weapons.advance()` em cada passo do resultado para concluir projéteis e efeitos existentes.
- Preservar disparos durante a partida, perda de evolução na morte, animação do cenário, tiros do subchefe e contagem do escore.
- Atualizar README e especificação do port para distinguir derrota de conclusão da fase. Incorporar estes critérios ao plano existente.
- Manter APIs e tipos atuais. A permissão depende diretamente das vidas, seguindo o [training de estado duplicado](/home/renanfranca/projects/kof/training/anti-patterns/duplicate-state.md:73):

  > If a value can be derived from another, derive it (method or function).

## Aceitação e provas planejadas

As expectativas de derrota vêm dos seus esclarecimentos; a preservação da conclusão da fase foi confirmada por você.

| Critério | Cenário e resultado esperado | Verificação |
|---|---|---|
| Nenhum novo disparo | Uma vida, explosão no passo 29, armas inativas e cadência no passo 12. Após a vida chegar a zero, nenhum projétil surge em 100 passos, nos níveis 0–3; incluir nível 2 com seis tentativas de laser. | Ampliar o teste existente de derrota e verificar todos os projéteis após cada passo. |
| Tiros lançados terminam | Entrar na derrota com lasers, blaster e três feixes ativos. Permanecem ativos na entrada, avançam normalmente e ficam inativos até 170 passos; permanecem inativos nos 52 seguintes. | Cenário pela entrada estável `Game.step()`, observando posições e atividade. |
| Efeitos terminam | Entrar com impacto de laser, blaster esgotado e feixe esgotado. Seus efeitos concluem respectivamente após 1, 4 e 6 passos do resultado. | Verificar presença na entrada, quadros intermediários e desativação no término. |
| Compatibilidade e reinício | Concluir fase com vidas restantes mantém disparos visuais; depois da derrota, voltar ao menu e iniciar nova partida restaura tiros na cadência normal. | Reutilizar o teste de resultado existente e ampliar a jornada de reinício. |

Estender a fixture e o percurso de navegador de fase/resultado existentes. Em Chrome nas larguras 320 e 1200, observar sprites lançados, conclusão dos efeitos e ausência de reaparecimento durante o resultado. Conferir também escore preservado, contagem e retorno ao menu.

## Validação e evidências

Base inspecionada: `b84398c70e26cce63618586447c35f71d6800466`. Durante o planejamento, os comandos abaixo passaram em ambos os alvos:

```bash
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
```

```text
0 failed of 85 tests
```

Esse resultado descreve a suíte atual; a observação de novos projéteis após a derrota ainda precisa ser acrescentada.

Na execução:

- Demonstrar a falha da regressão antes da correção; depois executar JVM, JS e os percursos de navegador de fase, armas e subchefe.
- Conferir separadamente a expectativa de cada critério e se suas assertions realmente a demonstram.
- Complementar o registro existente de fase/resultado em `.agent/validation/` com SHA testado, comandos, resultados por critério, navegador/versão e links de workflow quando disponíveis. Guardar logs e capturas em `.agent/tmp/`.
- Registrar qualquer falha ou critério não verificado antes da entrega.

### Execução — 05/10/2026

- [x] Regressão antes da correção: JVM/JS, `1 failed of 85 tests`, somente ausência de novos projéteis na derrota.
- [x] Restringir a tentativa de disparo a vidas positivas no resultado; preservar `weapons.advance()`.
- [x] Provas pelo `Game.step()`: quatro níveis, nível 2 com seis tentativas, tiros ativos na entrada, movimento, término em 170 passos, ausência nos 52 seguintes; efeitos em 1/4/6 passos; conclusão com vidas e reinício na cadência. JVM/JS: 87/87.
- [x] Provas Chrome 139.0.7258.154, 320/1200: tiros/efeitos, ausência de reaparecimento, resultado com vidas, contagem e reinício. Gate inicial no código `ee6d7209755f1d352cf71299942e54bbefb54b7b`: dez checks aprovados, contrato CI repetido com `yq` preexistente no PATH. Revisão estrutural no mesmo contexto sem refactor adicional. Registro por critério em [stage-hud-result.md](.agent/validation/stage-hud-result.md#interromper-disparos-após-a-última-vida--05102026).

- [x] Gate final em `68f760b145c1153f55af0a13b967e3b67410101d`: 10/10 checks, 181,74 s, sem bloqueios. [PR #13](https://github.com/renanfranca/kof-sifuture/pull/13) aberto; [CI 37357041630](https://github.com/renanfranca/kof-sifuture/actions/runs/37357041630) no mesmo SHA com Resolve/JVM/JS SUCCESS e 87/87 em cada alvo. Pages SKIPPED. Nenhum critério do ajuste sem prova.

Este complemento incorpora links disponíveis e repete os gates da skill antes da entrega; o código permanece em `ee6d720`. Resultados do head documental seguinte serão associados no ledger e no PR. Sem merge ou limpeza do trabalho não mesclado.


## Próximo ciclo: boss final de SiFuture

## Purpose and success

Implementar o combate completo com o boss final no navegador: entrada na fase, evolução dos ataques, dano, pontuação, explosão e chegada ao resultado.

Decisões desta conversa:

- Preservar a explosão histórica de **28 passos**: primeiro quadro por um passo, demais quadros por três.
- Durante o reinício invulnerável da nave, contato corporal não altera nenhuma das entidades; registrar essa exceção ao original.
- Música permanece para outro ciclo.

## Context and limits

Base conferida: `8f8f0710c3d440888aec27226e1ee87d25c54d97`, checkout limpo. A implementação existente passou **87 testes em JVM, 87 em JS e os seis percursos Chrome**. Ambos os comandos de regras terminaram com:

```text
0 failed of 87 tests
1 passed, 0 failed
```

Comandos observados: `python3 scripts/kof_project.py test --target jvm` e `--target js`, usando Kof instalado `0.5.0-beta`. Isso valida a base atual; os critérios do boss ainda precisam de implementação e provas.

A fonte histórica consultada está em `6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f`. Fonte e bytecode foram inspecionados estaticamente, sem executar o JAR.

A entrada histórica usa a largura da miniatura:

```java
this.BOS_TIME = MAX_RIGHT - this.smallAirship3.getWidth();
```

Fonte: [StageCount.java, linha 91](/home/renanfranca/projects/sifuture/src/StageCount.java:91). Com largura lógica 176 e miniatura de 30 pixels, o encontro começa em **146**, avança o marcador para **147** e suspende a trilha.

A cadência curta do primeiro quadro vem desta atribuição:

```java
this.timeDraw = (byte)(this.timing - 1);
```

Fonte: [BosStage1.java, linha 316](/home/renanfranca/projects/sifuture/src/BosStage1.java:316). O incremento da mesma chamada encerra esse quadro após uma atualização.

O ciclo conserva o mundo 176 × 220, passos de 30 ms, controles atuais e resultado existente. Android, música, menus completos e reformulação de apresentação permanecem pendentes.

## Milestones

1. **Registrar o novo contrato.** Acrescentar este ciclo ao `EXECPLAN.md` e à especificação existente, preservando os registros anteriores. Atualizar o README e complementar o aceite de fase/resultado.

2. **Implementar entidade e progressão.** Adicionar `Boss`, com estados inativo, normal, fúria, frenesi e explosão, e classes próprias para armamento e os dois tipos de projétil. Usar campos mutáveis e manter `Game.start()`, `Game.step()` e `Game.stagePosition()` como entradas estáveis. O treinamento Kof orienta:

   > “for **mutable state** use explicit fields + `constructor(...)`.”

   Fonte: [idioma de classes](/home/renanfranca/projects/kof/training/idioms/classes.md:35). Isso permite que cada entidade seja responsável pelos seus contadores e transições, seguindo a organização já usada pelo subchefe.

   No reset, usar resistência 100, posição inicial x 220–419/y 30–168 e destinos x 88–135/y 30–168; avançar uma unidade por eixo. Ativar uma vez em 146, marcar 147 e congelar a trilha durante combate e explosão. Depois, retomar até 176.

3. **Implementar ataques e contatos históricos.**
   - Evoluir o armamento abaixo de 80, 70, 45 e 20 de resistência, após contatos não fatais de armas. Preservar a ausência dessa evolução no contato corporal e o contato corporal restrito ao boss normal.
   - Usar intervalos de tiro normal de 13/31/31/24/24 passos nos cinco níveis; capacidade inicial de um tiro e posterior de dois. Preservar o relógio entre mudanças de nível e evoluir também os tiros normais já lançados.
   - Liberar o gatilho do especial a cada **quatro tentativas**, contando tentativas com slots ocupados. Preservar as condições históricas de cada nível: relógio anterior ao incremento `>10`, gatilho sem esse limite e, no último nível, relógio `>4`.
   - Tiros normais avançam quatro unidades à esquerda. O especial apresenta seis quadros de preparação, três passos cada; somente o quadro 6 permite movimento de dez unidades e colisão.
   - Preservar geometria e prioridade: corpo → laser → blaster → especial do jogador → contatos do boss com meteoros → tiros inimigos. Contatos usam posições do boss e dos seus tiros anteriores ao movimento/disparo; tiros novos ou reutilizados só podem colidir no passo seguinte.
   - Meteoros absorvidos pelo boss não retiram resistência nem rendem pontos. Meteoros avançam uma vez por passo; excluir os absorvidos dos contatos posteriores do jogador. Impedir relançamento dos verticais enquanto qualquer chefe estiver ativo, mantendo os já lançados e os itens recorrentes.
   - Reutilizar o protocolo verificado dos feixes do jogador, acrescentando a geometria do boss, inclusive seu ponto vertical central.

   O contador real do especial confirma quatro tentativas:

   ```java
   this.shoot1Count++;
   if (this.shoot1Count == SHOOT1_QUANTITY * 2) {
       this.allShootOn = true;
       this.shoot1Count = 0;
   }
   ```

   Fonte: [BosStage1AllShoots.java, linha 218](/home/renanfranca/projects/sifuture/src/BosStage1AllShoots.java:218); `SHOOT1_QUANTITY` vale 2.

4. **Integrar desenho, explosão e encerramento.** Copiar sem transformação `bos0` **não existe como nome de asset**: usar os arquivos históricos `bos.png`, `bos1.png`, `bos2.png`, `shoot0`–`shoot3.png` e `esp0`–`esp6.png`. Preservar NOTICE e reutilizar as dez explosões existentes.

   Fúria usa `bos1.png`; frenesi alterna os três sprites a cada quatro passos. Preservar o movimento histórico do boss enquanto ativo, inclusive no passo fatal; capturar a posição da explosão após esse movimento. O golpe fatal interrompe disparos e incremento de `lifeTime`, concede o prêmio uma única vez e apresenta o quadro zero.

   A explosão mostra quadro 0 na entrada, quadro 1 após um passo, quadro 9 nos passos 25–27 e fica inativa no passo 28. Preservar seu deslocamento histórico e limpar os projéteis do boss ao terminar. Desenho apenas consulta estado. Pausa congela todos os relógios; derrota conserva animação da cena com contatos e recompensas encerrados.

## Progress

- [x] Conferir especificação, implementação, testes e reparos anteriores.
- [x] Confirmar recorte, invulnerabilidade e explosão de 28 passos.
- [x] Implementar e verificar os critérios abaixo. Gate inicial completo no SHA `2a594f863aca62b824fea25fb83ffd37140bb292`: 11/11 comandos com exit 0, JVM/JS 103 testes cada e sete percursos Chrome.
- [x] Registrar evidências por critério no aceite existente; revisão estrutural concluída sem refactor. Entrega e CI serão registrados no mesmo aceite e no ledger após os gates finais.

## Validation

Acrescentar casos à suíte comportamental existente e um percurso `tests/browser_boss.py`, com fixture Kof e modelo, desenho e controles reais. Reutilizar as provas existentes de controles, armas e resultado.

| Critério e origem | Cenário e resultado esperado | Prova planejada |
|---|---|---|
| Entrada e trilha — `StageCount.java:180–186,276–285` | Cruzar 146 ativa uma vez e marca 147. Combate e explosão mantêm 147. Após o término, 289 passos ainda não concluem; o 290º chega a 176 e entra no resultado. | JVM/JS por `Game.step()`; navegador com marcador e sprites. |
| Movimento e fases — `BosStage1.java:128–143,187–225,391–409` | Mesma seed reproduz posições/destinos. Armas cruzam 80→79, 70→69, 45→44 e 20→19; valores exatos dos limites ainda não evoluem. Corpo não evolui o ataque; reinício não causa dano corporal. | Casos de fronteira e movimento em ambos os alvos; sprites normal/fúria/frenesi no Chrome. |
| Cadência e capacidade — `BosStage1AllShoots.java:78–139,200–225` | Conferir os cinco intervalos, primeiro slot livre e quarta tentativa. Com slots ocupados, o contador avança sem substituir tiros existentes. | Assertions de lançamento, contadores e posições; confirmação visual dos dois tipos. |
| Colisões — `GameCanvas.java:158–200` e métodos históricos de cada projétil | Conferir bordas inclusivas, ponto central do especial, prioridades simultâneas, blaster esgotado, tiro novo/existente/reutilizado e transição do especial 5→6. | JVM/JS com resultado exato; Chrome com quadros antes/depois. |
| Prêmio — `BosStage1.java:170–180,376–384` | Golpes fatais em `lifeTime` 30/31/60/61/120/121 dão 1650/1100/1100/550/550/275 pontos, inclusive quando o relógio está prestes a incrementar. Prêmio não se repete. | Quatro famílias de dano; verificar score, relógio, disparos e HUD. |
| Explosão — `BosStage1.java:311–369` | Primeiro quadro dura um passo; demais, três. Conferir posição inicial, deslocamentos, quadro 9, remoção no passo 28 e retomada da trilha. | JVM/JS; pixels no Chrome em 320 e 1200 px, incluindo pausa e redesenhos. |
| Encerramento e reinício — contratos atuais da especificação | Derrota durante o combate preserva score/vidas e encerra novos disparos da nave; projéteis existentes terminam. Nova partida limpa boss, ataques, efeitos e relógios. Resultado com vidas preserva tiro visual e duas confirmações. | Ampliar jornadas existentes e repetir partida completa com a mesma seed. |

Executar regras JVM/JS, os seis percursos atuais, o novo percurso do boss, infraestrutura Python e contrato CI. Todos devem terminar com exit 0. Inspecionar as capturas do novo combate em Chrome nas duas larguras e comparar os assets copiados byte a byte.

Antes da entrega, conferir **a correção das expectativas contra as fontes separadamente da qualidade das assertions**. Registrar, para cada critério, comando/procedimento, resultado observado, assertion ou captura, SHA testado, identidade do Kof, navegador e links de CI. Manter resumo versionado no aceite existente e evidências geradas em `.agent/tmp/`.

Registrar falhas e critérios não verificados explicitamente. A comparação visual com o vídeo histórico permanece pendente; o aceite deste ciclo não encerra a v1 completa.

Execução confirmada em `sifuture-boss-primary`, worker `primary`, `gpt-6.1-sol` / `medium`; papéis, validação e revisão compartilham contexto. Branch `sifuture-boss`; base imutável `8f8f0710c3d440888aec27226e1ee87d25c54d97`. Sonar, Habit e mutação excluídos por ausência de configuração. Inventário local inclui regras JVM/JS, sete jornadas Chrome, infraestrutura Python e contrato CI. O `yq` v4.54.1 foi preparado em `.agent/tmp/tools/`, após confirmação do usuário.

Releitura complementar antes da entrega: quinta tentativa desliga o gatilho especial histórico. Assertion vermelha em JVM e correção do ramo `else`; gates iniciais/finais repetidos no novo SHA antes do PR.

Conferência posterior do planejador no head `b1989d082952aad16eef9e336a649630d1dbd482`: nenhum desvio funcional do ciclo aprovado identificado. Reexecutados os onze comandos, todos com exit 0; 103/103 em JVM/JS e sete jornadas Chrome. Três provas complementares de capacidade inicial, gatilho desligado e absorção protegendo nave normal passaram nos dois alvos; recomenda-se incorporá-las à suíte permanente. [CI 37484705995](https://github.com/renanfranca/kof-sifuture/actions/runs/37484705995) confirmado no mesmo head do PR #14, Pages SKIPPED. O [aceite existente](.agent/validation/stage-hud-result.md#conferência-do-planejador-após-a-implementação--06102026) registra comparação por critério, comandos, SHA, fontes, capturas, qualidade da cobertura e limites. Esta conferência altera somente registros, sem novo código ou commit; vídeo histórico e Android permanecem pendentes.


## Alinhar as setas com o jogo e reposicionar o Especial — 06/10/2026

### Purpose and success

↑ e ↓ compartilham o centro horizontal do canvas; Especial fica 16 px à direita dele e centralizado somente nos seus 220 px de altura. Este ciclo substitui explicitamente Especial ao lado do direcional; registros anteriores permanecem históricos.

### Context and limits

Branch `controls-alignment`, base fixa `origin/main` `42d76fe443edf0dbbb3857cea47824fce7ad59e4`, em checkout separado. Worker `primary`, chat `01a11249-dd7e-7530-b57c-32308372ff83`, `gpt-6.1-sol`/`medium`, título `controls-alignment-primary`. Implementação, validação e revisão compartilham contexto. Sonar, mutação e Habit não configurados e excluídos; CI Resolve/JVM/JS selecionado. Pages depende de push em main, fora do gate do PR.

### Milestones

1. Compor `Column(surface, pad)` à esquerda e uma coluna de altura 220 para o Especial à direita, dentro de `Row`. Usar widgets e `Style` Kof, sem alterar eventos, IDs, ordem de foco, regras ou interfaces públicas.
2. Preservar canvas 176×220, setas 56×56, cruz 168×168, Especial 72×64, gap 16 e janela 296. Fixar conjunto 264 e impedir quebra. Centro/cantos da cruz vazios; nenhuma sobreposição, corte ou scroll horizontal.
3. Ampliar percursos existentes: touch no eixo do canvas, alvo real ↑, (60,100)→(60,95) em um passo, continuidade enquanto mantido e parada ao soltar. Medir centros com tolerância 1 px em 320/1200; verificar posição do Especial em todas as disponibilidades e ordem de Tab.
4. Reutilizar diagonais, solturas independentes, Especial simultâneo, teclado e pausa. Conferir expectativas e assertions separadamente; inspecionar capturas. Atualizar especificação, README e aceite de controles sem apagar evidências anteriores.

### Validation

`python3 tests/browser_controls.py`; `python3 tests/browser_weapons.py`; `python3 scripts/kof_project.py test --target jvm`; idem `js`; `python3 tests/browser.py`; `python3 tests/browser_meteor.py`; `python3 tests/browser_stage.py`; `python3 tests/browser_subchief.py`; `python3 tests/browser_boss.py`; `python3 -m unittest discover -s tests -p 'test_kof_project.py'`; `PATH="/home/renanfranca/projects/kof-sifuture/.agent/tmp/tools:$PATH" bash tests/ci-contract.sh` (yq preexistente).

Registrar SHA testado, comandos, resultado por critério, Chrome/versão e links persistentes de workflow no [aceite existente](.agent/validation/sifuture-controls.md). Logs, JSON de medidas e capturas ficam em `.agent/tmp/`. Touch simulado comprova as jornadas automatizadas; conforto no celular físico permanece pendente.

### Progress

- [x] Regressão de toque no eixo demonstrada antes da correção; composição Kof implementada.
- [x] Gate inicial em `fced14f80d3590736b7a586a2a14871f8a495e1d`: 11/11 checks exit 0; JVM/JS 103/103; revisão estrutural sem refactor. Critérios, medidas, auditorias e comandos no aceite existente.
Gate de entrega: repetir os onze checks sobre o complemento documental; resultados do head final e links de PR/CI serão associados ao ledger e ao PR.
- [ ] Conforto no Android físico.

Conferência posterior do planejamento no head `2d4e1e867aae2dd26963bc165eafcde78d3f6ab5`: nenhum desvio funcional identificado; os nove comandos do plano foram reexecutados com exit 0 (103/103 em JVM e JS, sete percursos Chrome). Geometria apresentou diferença 0 px nos centros e gap 16 em 320/1200; toque no eixo do canvas moveu e parou na soltura. Gate final do executor 11/11 conferido e [CI 37509126926](https://github.com/renanfranca/kof-sifuture/actions/runs/37509126926) confirmado no mesmo head do [PR #17](https://github.com/renanfranca/kof-sifuture/pull/17), Pages SKIPPED. O aceite existente registra critérios, comandos, capturas, qualidade da cobertura e limites. Apenas registros foram complementados, sem alteração de produção ou commit; conforto no Android físico permanece pendente.


## Ciclo aprovado: Especial vertical na altura inteira do canvas — 06/10/2026

Partir de `controls-alignment`, preservando os aceites anteriores como históricos. Substituir neste ciclo o Especial 72 × 64 pelo retângulo 56 × 220, coluna de 56 e conjunto de 248 pixels; manter canvas 176 × 220, cruz 168 × 168, setas 56, gap 16 e janela 296 sem quebra. Aplicar `writing-mode: vertical-rl` nos dois estilos declarativos de Kof, preservando nome “Especial”, IDs, foco, eventos e regras.

- [x] Expectativa de layout atualizada antes da produção; controles e armas falharam no tamanho anterior.
- [x] Alteração mínima nos estilos e largura da composição.
- [x] Percursos integrados: texto inteiro/centralizado, topo/meio/base com duas cargas → uma, estados e regressões.
- [x] Gate inicial em `38fa85903db8b0c648d778a6557ebb99b0c0ed2b`: onze checks exit 0; JVM/JS 103 cada, sete percursos Chrome e infraestrutura aprovados.
- [x] Auditorias separadas de expectativas/assertions; revisão estrutural No action e capturas 320/1200 revisadas.
- [x] SHA inicial, comandos, navegador, resultados por critério e links persistentes de CI no aceite existente.
- [ ] Conforto no Android físico (permanece fora do aceite simulado).

Execução por `primary`, neste chat, com papéis e leases serializados. Validação e revisão compartilham o contexto da implementação. Sonar, Habit e mutation testing permanecem excluídos por ausência de configuração. Plano literal, ledger e evidências locais: `.agent/tmp/special-vertical.*`.

Gate de entrega deste ciclo: repetir todos os onze checks no complemento documental; o ledger e a descrição do PR #17 registrarão o head final, resultado do gate e execução específica de CI antes da entrega.


# Próximo ciclo: créditos, Controles e navegação da pausa

## Purpose and success

**Sim: o núcleo das mecânicas já está implementado e aceito nos ciclos de gameplay, incluindo subchefe e boss final. A v1 completa continua aberta.** A própria [especificação](/home/renanfranca/projects/kof-sifuture/.agent/specifications/port-sifuture-to-kof.md:3) registra:

> subchief and final boss combat slices implemented. Full v1 remains open.

Nesta releitura, executei as suítes JVM/JS e o percurso principal do Chrome no commit `2322d90f6d98e1cdd4a9d209efeb216c1182b8e4`, todos com saída 0:

```text
0 failed of 103 tests
1 passed, 0 failed
PASS menu, Enter and Space, conservative confirmation, pause, result and menu in Chrome
```

As regras da partida têm evidência automatizada. Ainda faltam requisitos da aplicação completa e a comparação visual com o vídeo histórico.

O próximo ciclo escolhido entregará **abertura com créditos animados → menu navegável → Controles → partida → pausa com Continuar, Reiniciar e Menu principal**.

## Context and limits

- Preservar a animação histórica dos créditos. A frequência será a determinada pela [especificação](/home/renanfranca/projects/kof-sifuture/.agent/specifications/port-sifuture-to-kof.md:148):

  > Credits MUST appear once when the application opens. Enter or touch MUST skip them. They MUST NOT recur within the same running application instance.

- Opções e os controles de Música ficam para o ciclo de áudio, conforme a escolha feita nesta conversa. Continuam obrigatórios para concluir a v1.
- Pausa automática, escala adaptável, entrada fora da árvore de controles e execução Android ficam para ciclos posteriores. Neste ciclo, o teclado mantém a ativação por clique ou Tab.
- Consultar o histórico em `6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f`, sem executar seu JAR como oráculo. Kof consultado: `317d9f6b1c3e27032cc955a05f859f6c627d9338`; instalação executada: `0.5.0-beta`.

## Milestones

1. **Adicionar abertura e navegação ao modelo.** Acrescentar Credits e Controls às telas existentes. Os créditos aparecem na criação da aplicação; iniciar, reiniciar e voltar ao menu nunca os reativam. Manter `Game.start(seed)`, `step()` e `stagePosition()`. Acrescentar ações explícitas para abrir Controles, navegar entre opções, reiniciar com seed injetável e abandonar a partida.

2. **Integrar telas e controles Kof.** Reutilizar a composição atual, com botões acessíveis para toque direto. Menu: Novo Jogo e Controles. Pausa: Continuar, Reiniciar e Menu principal. Cima/Baixo selecionam sem ultrapassar as extremidades; confirmação executa a seleção. Controles explica teclado, foco, diagonais, opostos, arrasto, soltura e especial, com ação Voltar. Preservar os bloqueios de teclas mantidas e a deduplicação do clique nativo.

3. **Preservar apresentação e responsabilidades.** Copiar `copyright0.png`, `copyright1.png` e os sprites de menu utilizados sem transformação; preservar NOTICE. Animações avançam somente nos passos de 30 ms; desenho apenas consulta estado. O estado mutável dos créditos pertence a uma classe, seguindo o [idioma Kof](/home/renanfranca/projects/kof/training/idioms/classes.md:35):

   > for **mutable state** use explicit fields + `constructor(...)`.

   Isso mantém posição e relógios da animação juntos, permitindo redesenhar sem acelerar sua execução.

4. **Consolidar testes e documentação.** Ampliar as jornadas existentes e promover as três provas complementares do boss já [registradas](/home/renanfranca/projects/kof-sifuture/.agent/validation/stage-hud-result.md:837) à suíte permanente. Atualizar a especificação, o EXECPLAN e os registros de aceite existentes, preservando a história dos ciclos anteriores.

## Progress

- [x] Especificação, implementação, testes e aceites relidos.
- [x] Base atual verificada em JVM, JS e no percurso principal do Chrome.
- [x] Recorte e animação histórica escolhidos pelo usuário.
- [ ] Implementação e aceite do novo ciclo. Nenhum arquivo versionado foi alterado nesta preparação.

## Validation

As verificações abaixo são **planejadas**, ainda não resultados do novo ciclo.

| Critério e fonte | Contexto, ação e resultado esperado | Prova prevista |
|---|---|---|
| Créditos — [histórico](/home/renanfranca/projects/sifuture/src/MenuCanvas.java:192) | Abertura começa em x=-134; primeiro avanço mostra x=-129. Preservar chegada, 50 quadros de espera e saída vertical histórica. Redesenhar não avança a animação. | JVM/JS nas transições; Chrome com relógio controlado e comparação dos sprites. |
| Exibição única — [especificação](/home/renanfranca/projects/kof-sifuture/.agent/specifications/port-sifuture-to-kof.md:148) | Enter focado ou toque pula somente para Menu. Manter Enter pressionado não inicia a partida. Retornos de Controles, pausa e resultado não repetem créditos. | Ampliar `browser.py`, observando também o evento seguinte à transição. |
| Navegação — [especificação](/home/renanfranca/projects/kof-sifuture/.agent/specifications/port-sifuture-to-kof.md:144) | Seleção inicial Novo Jogo; Baixo seleciona Controles; repetição mantida não navega novamente. Toque executa diretamente a opção tocada. Voltar de Controles conserva essa seleção. | Modelo e Chrome em 320/1200; nomes acessíveis, foco e ausência de Carregar/Opções neste recorte. |
| Continuar — [especificação](/home/renanfranca/projects/kof-sifuture/.agent/specifications/port-sifuture-to-kof.md:150) | Pausar uma partida com movimento e projéteis ativos congela estado. Continuar conserva a partida; o primeiro passo avança uma vez, sem recuperar movimento mantido. | Reutilizar provas de pausa e acrescentar a navegação pela nova tela. |
| Reiniciar — mesma fonte | Reiniciar uma partida evoluída restaura nave em `(0,100)`, três vidas, score zero, posição 5, arma básica, zero cargas e chefes inativos. Uma seed fixa reproduz a nova partida. | JVM/JS pelo comando de reinício; Chrome pela ação real, verificando também o primeiro passo. |
| Menu principal — mesma fonte | Abandonar durante combate retorna ao menu com Novo Jogo selecionado; passos seguintes não retomam a tentativa. Novo Jogo começa uma partida limpa, sem créditos. | Modelo e Chrome, incluindo teclas e contatos mantidos durante a saída. |
| Regressões | Resultado mantém suas duas confirmações; combate, controles e geometria atuais continuam aceitos. As três provas complementares do boss tornam-se permanentes. | Suíte completa e sete jornadas existentes. |

Executar:

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

Antes da entrega, conferir separadamente **se cada expectativa corresponde às fontes** e **se suas assertions demonstram o comportamento**. Registrar por critério comando, resultado, assertion/captura, SHA, identidade Kof, navegador e links de CI. Guardar evidência gerada em `.agent/tmp/` e resumos versionados em `.agent/validation/`.

Falhas, cobertura ausente, comparação com vídeo e Android real devem permanecer explicitamente pendentes; uma suíte verde não encerra esses critérios.


### Execução confirmada — créditos e navegação

Branch `credits-pause-navigation`, checkout atual sem worktree, base `main` fixa `2322d90f6d98e1cdd4a9d209efeb216c1182b8e4`. Worker `primary`, chat `01a113e4-c500-76c1-850c-191a12bc6f41`, título `sifuture-navigation-primary`, `gpt-6.1-sol`/`medium`. Os sete papéis compartilham contexto e usam leases serializados; revisão e validação não são independentes. Onze checks locais e Resolve/JVM/JS no CI confirmados. Sonar, Habit e mutação excluídos por ausência de configuração, sem atribuir pass. Plano literal, ledger, inventário, coletores e logs em `.agent/tmp/credits-pause-navigation.*`.

Implementação e checkpoints comportamentais: Credits/Controls no modelo; créditos em classe mutável avançada por step; seleção limitada e deduplicada; reinício com seed e abandono; telas, botões e explicação Kof. Três provas do boss promovidas à suíte permanente. JVM/JS: 112 casos; Chrome: créditos, navegação e reinício nos percursos existentes em 320/1200. Gates completos e auditorias serão registrados no aceite antes da entrega.


- [x] Gate inicial 11/11 no SHA `50affe515aeeec0f6ee9776a4d774feb8c7cf469`, 236,96 s; JVM/JS 112/112, sete percursos Chrome e infraestrutura.
- [x] Expectativas históricas e qualidade das assertions auditadas separadamente; oito sprites idênticos, NOTICE preservado, capturas320/1200 inspecionadas.
- [x] Revisão estrutural com consolidação do protocolo dos callbacks direcionais; registros de fase/resultado e controles atualizados, história preservada.
- [ ] Gate final no commit revisado/documentado e entrega PR/CI (serão registrados no ledger e no PR).
- [ ] V1: vídeo, Android, áudio/Opções/Música, escala e lifecycle posteriores continuam abertos.

Revisão complementar: estilos de navegação agora são construídos uma vez, evitando registros KofJS a cada tick; sonda19→19 em1000 ticks e percurso público preservado. Correção adicional `6daccf42529c19e5f69d1cef1b84b04959b1e193` voltou pelo fluxo de implementação; gate completo11/11 passou em237,27s,112 testes por alvo e sete jornadas Chrome. Revisão estrutural reconferida no mesmo contexto, sem nova alteração comportamental. Consolidação final de documentação será validada novamente antes do PR; links posteriores no ledger/PR e registro de aceite.

- [x] Gate final local11/11 no head `b8ceb17123b16cd4ee3b29dc3a7c44677715a632`,237,94s,112 testes por alvo.
- [x] [PR18](https://github.com/renanfranca/kof-sifuture/pull/18) criado pronto para revisão, sem merge; [CI37558500360](https://github.com/renanfranca/kof-sifuture/actions/runs/37558500360) com Resolve/JVM/JS success,112 testes por alvo. Links e identidade do merge sintético registrados no aceite.
- [ ] Commit documental com estes links: repetir gates e acompanhar CI do novo head antes da entrega; registros posteriores no ledger e PR. Código do ciclo concluído; v1 permanece aberta.


## Complemento aprovado — menu, entrada e contato (07/10/2026)

$implement-approved-plan # Melhorar o menu, restaurar a entrada da nave e atualizar os créditos

## Resultado esperado

Este plano substitui o anterior e mantém as correções R1/R2. Entregar:

- Uma única ação **Confirmar (Enter)** abaixo do menu e da pausa, executando a seleção atual.
- Toque direto nas opções desenhadas, sem repetir a lista abaixo.
- Entrada da nave com propulsores somente na primeira abertura do Menu, inclusive após pular créditos.
- Contato **renan.andradefranca@gmail.com** como texto Kof no bloco animado dos créditos.
- Espera de50 quadros e término histórico dos créditos, com Menu no quadro260.

Incorporar este complemento ao `EXECPLAN.md` durante a execução, preservando os registros anteriores.

## Menu e confirmação

Atualmente, tocar na ação principal força a primeira opção, conforme [GameControls.kf:174](/home/renanfranca/projects/kof-sifuture/src/main/kof/sifuture/GameControls.kf:174):

```kof
if (game.screen == Screen.Menu) { game.menuSelection = 0 }
if (game.screen == Screen.Pause) { game.pauseSelection = 0 }
game.confirm()
```

O novo botão Confirmar removerá essas atribuições: focá-lo, tocá-lo ou pressionar Space executará a seleção existente, assim como Enter. Selecionar Controles e confirmar abrirá Controles imediatamente.

- Reaproveitar `Button` e `Style` Kof para criar áreas transparentes sobre as opções, com nomes acessíveis e indicação de foco. Toque executa diretamente a opção tocada.
- Menu conserva as posições atuais. Na pausa, mostrar Continuar, Reiniciar e Menu principal nas linhas y80/99/118; conservar o sprite de Continuar e desenhar os outros dois rótulos em Kof.
- Cima/Baixo continuam limitados às opções; foco numa opção atualiza a seleção. Focar Confirmar conserva a seleção.
- Construir widgets e estilos uma vez, reutilizando-os nas atualizações.
- Validar seleção e ativação pela tela atual. Opções anteriores retidas para receber solturas ficam fora da área visível, sem receber toque, e não podem confirmar outra tela.
- Preservar bloqueios de Enter/Space mantidos e descarte do clique nativo. Soltar a tecla continua funcionando após uma transição.
- Pular créditos, Voltar, Pausar e as duas confirmações de resultado mantêm suas ações específicas.

## Entrada da nave

O histórico usa o sprite com propulsores e avanço de dez unidades, em [MenuCanvas.java:123](/home/renanfranca/projects/sifuture/src/MenuCanvas.java:123):

```java
g.drawImage(this.arrow[1], this.iMenu, Midlet.height/2, 0);
this.iMenu += 10;
```

Depois troca para o sprite normal e recua três unidades. Preservar essas velocidades e adaptar o percurso à composição atual, cuja posição final é x18:

| Passo desde a abertura do Menu | x | Apresentação |
|---|---:|---|
| 0 / 1 | -30 / -20 | `3lives.png`, com propulsores |
| 11 | 80 | Último quadro com propulsores |
| 12 / 13 | 87 / 84 | `2lives.png`, desaceleração |
| 35 / 36 | 18 / 18 | Posição final, sem quadro vazio |

- Acrescentar uma classe mutável `MenuEntrance`, com posição e fases Entrada/Frenagem/Pronta. Somente `Game.step()` avança essa animação, a cada30ms.
- Desenhar a nave na linha da seleção atual. Navegação e confirmação permanecem disponíveis durante a entrada; nenhuma ação fica esperando a animação terminar.
- Sair para uma partida ou Controles encerra definitivamente a entrada. Retornos de Controles, abandono e resultado apresentam o seletor pronto, conservando as regras de seleção.
- A animação não avança os relógios da partida nem reaparece na pausa.

O estado permanece em uma classe, conforme o [idioma Kof](/home/renanfranca/projects/kof/training/idioms/classes.md:36):

> for **mutable state** use explicit fields + `constructor(...)`.

Isso mantém a atualização temporal separada do desenho, como explicado em [Learn Kof](/home/renanfranca/projects/kof/learn/07-classes-and-objects.md:65).

## Créditos e novo contato

Preservar o término histórico escolhido:

| Quadro | Resultado esperado |
|---|---|
| 0 / 1 | x=-134 / -129; y0=110, y1=141 |
| 36–85 | Exatamente50 quadros em46/110/141 |
| 86 / 87 |46/111/140 e46/112/139 |
| 258 | Última atualização:46/283/-32 |
| 259 | Credits, sem sprites ou texto |
| 260 | Menu, começando a entrada da nave |

- Contar a chegada como primeiro quadro de espera.
- Acrescentar `exitComplete` em `Credits`: marcado no259; `advance()` retorna true no260. Desenho não altera esses estados.
- Conservar `copyright0.png`, com autor e anos. Substituir somente a apresentação de `copyright1.png` por três linhas Kof: `contact:`, `renan.andradefranca@gmail.com` e `Inc. All rights reserved.`.
- O texto acompanha x/y1, usa azul RGB(0,128,255) e ocupa o bloco existente de30 unidades de altura. Desenhar com escala0,75, reduzida apenas se a largura medida ultrapassar130 unidades; baselines locais10/22/34.
- Usar `save`/`restore` para isolar a transformação e a cor, seguindo o [idioma Canvas](/home/renanfranca/projects/kof/training/idioms/ui.md:266). Isso impede que o ajuste dos créditos afete desenhos posteriores.
- Preservar os PNGs históricos e NOTICE. A mudança de apresentação do contato é uma exceção explicitamente escolhida; o e-mail antigo não aparece nos créditos.

## Testes e entrega

Ampliar as jornadas existentes, sem criar testes de helpers internos:

- **Confirmação:** selecionar cada opção e executar com Enter, Confirmar/Space e toque direto. Demonstrar que focar Confirmar não volta à primeira opção.
- **Transições:** confirmar Reiniciar, Menu principal e Controles com Enter mantido; tocar na antiga área e tentar Space no controle retido. Nenhuma ação indevida ocorre. Após solturas, uma nova confirmação funciona uma vez.
- **Entrada:** verificar os passos da tabela em JVM/JS e os sprites no Chrome320/1200; redesenhar não avança. Confirmar durante a entrada funciona imediatamente; retornos não repetem a animação.
- **Créditos:** verificar chegada, último quadro de espera, primeira saída, intervalo terminal e Menu260. Enter mantido ao pular não inicia uma partida.
- **Contato:** observar o texto literal e sua transformação no Canvas, conferir ausência do desenho antigo e inspecionar capturas320/1200 quanto a corte e legibilidade.
- **Regressões:** conservar reset com seed, pausa, movimento, resultado e combate.

As novas regressões devem demonstrar falha antes das correções. Executar os [onze comandos previstos](/home/renanfranca/projects/kof-sifuture/EXECPLAN.md:696), exigindo saída zero e nenhuma falha.

Atualizar especificação, README e aceites existentes com fontes, expectativas, assertions, resultados, SHA, identidade Kof, navegador e CI disponível. Evidências ficam em `.agent/tmp/`. Auditar separadamente a expectativa correta e a suficiência da prova.

Áudio, Android, escala, lifecycle e comparação integral com o vídeo permanecem fora deste complemento. Nenhuma alteração de implementação foi realizada neste planejamento.

Execução: worker primary neste chat 01a11641-92f1-7902-9c41-c3aaa6668c66, título menu-credits-primary, gpt-6.1-sol/medium. Branch menu-entrance-credits em worktree limpo, base fixa 7e35430837571ab11fa1d94e7f16abfd8097ed3f. Revisão e validação compartilham contexto. Onze checks locais e três CI confirmados; Sonar/Habit/mutação sem configuração, excluídos. Registros anteriores preservados.


### Progresso do complemento

- [x] Contrato incorporado sem apagar registros anteriores; worktree e ledger v6 separados.
- [x] TDD: créditos50/terminal260, entrada única, confirmação, retenção por tela e contato literal.
- [x] Provas JVM/JS 113 casos e jornadas Chrome320/1200; sonda de reutilização137 nodes/26 styles estáveis em1000 ticks.
- [x] Especificação, README e aceites existentes ampliados; auditorias de expectativa e suficiência separadas.
- [ ] Checkpoint e gates completos iniciais/finais; revisão estrutural; entrega PR/CI.
- [ ] Áudio/Android/escala/lifecycle/vídeo integral: fora do complemento, pendentes na v1.


Gate inicial no complemento: `b6a46355b0e4b31d0a0511452344733fc7abc6f2`,11/11 comandos com exit0,113 casos por alvo,253,37s. O primeiro checkpoint `4ab9cf78` teve duas expectativas de teste corrigidas em commit adicional; nenhum gate foi aceito para ele. Revisão estrutural no mesmo contexto sem delta de produção; auditorias separadas e imagens inspecionadas. PR18 recebe o complemento; CI do checkpoint [37622526346](https://github.com/renanfranca/kof-sifuture/actions/runs/37622526346). Aceites existentes preservam fonte, assertions, comandos, SHA, Kof e navegador. Gate final no commit documental e CI do head entregue permanecem pendentes e serão registrados no ledger/PR.


- [x] CI do checkpoint: [37622526346](https://github.com/renanfranca/kof-sifuture/actions/runs/37622526346), Resolve/JVM/JS success,113 testes por alvo; identidade do merge sintético/Kof e links dos jobs no aceite versionado.
- [x] Revisão estrutural concluída no contexto primary, sem refactor de produção; somente consolidação documental após checkpoint.
- [ ] Final-validating e CI do head final: resultados posteriores no ledger/PR, mantendo os SHAs deste registro explícitos.


## Ciclo aprovado: textos, seleção e guia de controles — 2026-10-07

Plano aprovado pelo usuário e confirmação de execução recebida neste chat. Distribuição: `primary`, `gpt-6.1-sol` / `medium`, com os sete papéis atribuídos e leases serializados. Mutation Analyst e Habit Curator inativos, sem configuração local. Validação e revisão compartilham o contexto da implementação. Checkout atual, branch `credits-pause-navigation`, base `main` no SHA `2322d90f6d98e1cdd4a9d209efeb216c1182b8e4`. O [PR #18](https://github.com/renanfranca/kof-sifuture/pull/18) permanece aberto.

O plano literal e o estado do fluxo ficam em `.agent/tmp/controls-guide.md` e `.agent/tmp/controls-guide.workflow.json`; este registro permanece legível sem esses arquivos locais.

$implement-approved-plan # Melhorar textos, seleção e guia de controles

## Resultado desejado

Conforme suas escolhas: texto Kof uniforme nos créditos e menus, nave como indicador de seleção, guia curto de controles e remoção da instrução fixa no rodapé.

Hoje existe uma mistura de imagem e texto. Em [GameView.kf](/home/renanfranca/projects/kof-sifuture/src/main/kof/sifuture/GameView.kf:88):

```kof
canvas.drawImage(copyright0, game.credits.x, game.credits.firstY)
drawContact(game.credits)
```

O copyright vem do PNG; o contato é desenhado separadamente. Usar a mesma renderização, cor e escala nos dois blocos corrigirá a diferença visual.

## Créditos e menus

- Desenhar copyright, nome completo e contato com `Canvas.fillText`, mantendo `renan.andradefranca@gmail.com` e a cor azul `RGB(0,128,255)`.
- Aplicar uma escala compartilhada aos dois blocos, calculada pela linha mais larga, com limite de 130 pixels. Preservar conteúdo, posições e duração da animação.
- Desenhar as opções em português, com fonte sans-serif uniforme de aproximadamente 12 pixels: **Novo Jogo**, **Controles**, **Continuar**, **Reiniciar** e **Menu principal**. Alinhar todas em `x=48`, dentro das áreas de toque existentes.
- Remover o retângulo azul da seleção. A nave continuará apontando a opção escolhida, inclusive durante sua entrada animada.
- Mostrar foco do teclado com contorno neutro de 1 pixel no perímetro da área do jogo; botões externos terão seu próprio contorno discreto. Nenhum retângulo acompanhará as linhas do menu.
- Manter confirmação direta por Enter e toque, nomes acessíveis e proteção contra ações duplicadas.

Para ajustar texto no Canvas, seguir a orientação do [training de UI](/home/renanfranca/projects/kof/training/idioms/ui.md:277):

> `measureText` returns a `Double` (width in px) for text layout.

A largura medida determinará o ajuste; `save()` e `restore()` isolarão as transformações para não alterar desenhos posteriores.

## Guia de controles

Substituir o parágrafo extenso por dois blocos em uma coluna, com fonte sans-serif de 14 pixels, entrelinha de 20 pixels e títulos de 16 pixels. Usar texto claro sobre fundo escuro, largura máxima de 248 pixels e espaçamento de 12 pixels.

**Teclado**

Introdução: “Na partida, clique na área do jogo ou use Tab até ‘Ativar teclado do jogo’.”

| Tecla | Ação |
|---|---|
| Setas | Mover a nave na partida |
| ↑ / ↓ | Escolher uma opção nos menus |
| Enter | Confirmar nos menus; pausar na partida |
| 1 | Usar o especial quando disponível |

**Toque**

- “Toque em uma opção do menu para abri-la.”
- “Segure as setas para mover. Combine duas para fazer diagonal.”
- “Solte todas as setas para parar.”
- “Especial: uma tentativa por pressão, quando disponível.”
- “Pausar: abrir o menu da pausa.”

Adicionar **Mais detalhes**, inicialmente fechado, com regras de direções opostas, arrasto, soltura independente, cancelamento, prioridade do direcional, disponibilidade do especial e foco dos botões. Explicar que Espaço ativa o botão focado e que Enter/Espaço sobre **Especial** tentam o especial.

Na tela Controles, recolher o direcional e o botão Especial e substituir o canvas vazio por um cabeçalho compacto de 44 pixels. Preservar o elemento que recebe teclado e a retenção temporária de foco durante teclas mantidas. Manter **Voltar** e fechar os detalhes ao entrar novamente no guia.

Remover completamente a instrução fixa do rodapé.

## Verificação e limites

- Ampliar os testes existentes em `tests/browser.py`: conferir textos dos créditos, cor e escala compartilhadas; nave indicando a seleção; foco independente; guia fechado/aberto; ausência do rodapé e de rolagem horizontal.
- Verificar abertura e retorno de Controles por Enter, Espaço, clique e toque. Abrir detalhes não poderá confirmar o jogo; manter uma tecla não poderá provocar uma segunda transição.
- Preservar os testes dos quadros dos créditos, entrada da nave, seleção limitada, pausa, reinício e opções antigas retidas durante uma pressão.
- Executar testes Kof em JVM/JS e os sete percursos existentes no navegador.
- Inspecionar capturas de créditos, menu, pausa e guia em larguras de 320 e 1200 pixels. Aprovação funcional e aprovação visual serão registradas separadamente.
- Atualizar documentação e registro em `.agent/validation/`, com SHA, comandos, navegador e resultados; capturas e logs ficarão em `.agent/tmp/`. Registrar qualquer critério ainda não comprovado.

O ciclo altera apresentação e orientação. Logo, sprites, HUD e mecânicas permanecem preservados. A implementação usará o checkout atual e as APIs existentes de Kof, sem alterações no compilador.

### Implementação e evidências deste ciclo

- Créditos e cinco opções desenhados com `Canvas.fillText`; uma escala determinada pela maior largura dos dois blocos; transformações isoladas por `save`/`restore`. Conteúdo dos créditos transcrito do PNG preservando os anos 2006-2007 e o nome sem alteração do asset.
- Nave indica seleção durante entrada e retornos; foco neutro de 1 px no perímetro da área ou no botão externo, sem retângulos nas opções.
- `ControlsGuide` compõe tabela, lista de toque e detalhes com widgets Kof existentes. Cabeçalho de 44 px, direcional/Especial recolhidos, receptor de teclado preservado. Detalhes usam a proteção de uma ação por pressão e fecham na saída.
- A janela acompanha o conteúdo: a inspeção revelou que a antiga altura fixa deixava o guia fora da moldura; a largura fixa também causava rolagem horizontal interna quando havia scrollbar vertical. O canvas mantém 176×220 e os controles mantêm 248 px.
- Testes mantêm quadros dos créditos, entrada da nave, seleção limitada, pausa, reinício e opções retidas. No guia compacto, após tocar a antiga coordenada sobre texto informativo, o teste devolve foco explicitamente ao receptor antes de soltar a tecla: a soltura deve ser observada na árvore de controles, conforme o contrato existente. A retenção efetiva de foco também é verificada antes desse toque.
- Registros RED/GREEN e capturas locais: `.agent/tmp/controls-guide-*.json` e `.agent/tmp/navigation-browser/`. Suíte principal e checkpoint do percurso de fase passaram durante implementação; gates completos e revisão estrutural serão registrados em [controls-guide.md](.agent/validation/controls-guide.md).


### Gate inicial e revisão do ciclo de apresentação

No SHA `e1025afc61397ea01a6bb8c40aa61520bd299743`, os onze comandos aprovados passaram em 263,43 s: JVM/JS 113 testes por alvo sem falhas; sete percursos Chrome; 8 testes Python; contrato CI. Capturas em 320/1200 px de créditos/menu/pausa/guia fechado e aberto, incluindo fim dos detalhes, inspecionadas separadamente. Revisão estrutural no mesmo contexto: nenhum refactor necessário. O registro completo, com comandos, trechos, limites e links persistentes, está em [controls-guide.md](.agent/validation/controls-guide.md). A versão documental será comprometida antes de repetir os onze comandos no gate final e atualizar o PR #18 com SHA/resultados/CI.

## Investigação de teclado sem clicar na área — 08/10/2026

Pedido do usuário: explicar por que o menu aceita teclado sem clicar no receptor transparente e testar a possibilidade de dispensar o clique também na partida. A habilidade `plan-behavioral-acceptance` orienta a separação entre expectativa, qualidade da prova e resultados observados. Esta seção não autoriza nem relata uma implementação do novo contrato.

### Observações concluídas

No SHA `02eb48e55102b5f0cafd85020b77f37da07060fa`, Chrome `139.0.7258.154`, JS, 320/1200 px, o build local e Pages apresentaram os mesmos resultados. O [registro existente de controles](.agent/validation/sifuture-controls.md#investigação-teclado-sem-clicar-na-área-do-jogo--08102026) contém procedimentos, trechos, fontes, limites e identidade do deployment/compilador. Cada percurso começa em contexto novo e usa Tab, nunca `.focus()`, para obter foco; conta zero pressões de ponteiro.

1. Com BODY como alvo, Enter não pula créditos; depois da abertura natural, Baixo/Enter não selecionam nem iniciam o jogo.
2. Tab até o receptor permite créditos → menu → Controles → menu → partida → pausa → retomada apenas com teclado. Direita por seis passos leva `(0,100)` a `(30,100)`; soltar mantém x=30; Cima leva y a 70.
3. Com foco em Confirmar, Baixo muda a seleção de y=120 para y=139. Cima/Enter inicia a partida conservando foco em Pausar; Direita por seis passos mantém x=0. Soltar e usar Tab até o receptor permite uma nova pressão levar x a 30.
4. Uma cópia temporária Kof, compilada e executada em JS, permite `game-action` também durante Play: a mesma pressão leva x=0 a x=30 sem clicar ou focar o receptor. Porém, manter Direita e sair de Pausar por Shift+Tab deixa movimento ativo até x=60. Esse protótipo demonstra viabilidade e uma lacuna, não é uma correção aceita.

A distinção vem do filtro de [GameControls.kf](src/main/kof/sifuture/GameControls.kf:319), que aceita `game-action` só em Menu/Pause. O observador está na coluna dos controles, não no documento inteiro. O [training de UI](../kof/training/idioms/ui.md:380) estabelece que `Event.target()` identifica a origem do evento, e o runtime JS consultado registra o observador no nó DOM. O [contrato atual](.agent/specifications/port-sifuture-to-kof.md:34) limita movimento ao receptor; estendê-lo muda esse contrato.

### Critérios para eventual execução, separados das observações

Os critérios P1–P5 abaixo são uma proposta de extensão para o foco já adquirido dentro do jogo. Não representam aprovação de captura global, foco automático ao abrir a página ou remoção do receptor. Se o escopo pretendido incluir funcionar imediatamente desde BODY, o plano de implementação permanece incompleto até definir o comportamento de foco e demonstrar a API correspondente no Kof; a prova atual não resolve esse escopo.

| Critério e fonte da expectativa | Contexto, ação e resultado proposto | Verificação planejada e evidência exigida | Situação da prova |
| --- | --- | --- | --- |
| P1 — possibilidade levantada pelo usuário; mecanismo em `GameControls.kf:319`; alteração explícita ao contrato atual | Tab até o botão principal, Enter pula créditos, novo Enter inicia; com foco em Pausar, nova Direita move x=0→30 em seis passos; soltura mantém x=30 nos seis seguintes. Nenhum clique na área nem transferência manual de foco para o receptor. | Ampliar o percurso real existente em `tests/browser.py`, com relógio e comparação de sprites; registrar alvo dos eventos, foco, coordenadas antes/depois e zero pointerdown em 320/1200. | Viabilidade demonstrada apenas na cópia temporária. Código atual permanece x=0. |
| P2 — menu, pausa e transições do contrato atual; entradas em `GameControls.kf:232` e `:296` | Entrar por Confirmar, pela opção Novo Jogo e por retorno de pausa; manter Enter durante cada transição causa somente uma ação. Depois da soltura, a primeira pressão de movimento deve funcionar no escopo aprovado. Repetir o início não repete créditos. | Reutilizar `tests/browser.py` e suas provas de Enter/Espaço/opções retidas; acrescentar somente a primeira seta depois da transição e observar se a origem ficou em BODY. Diferenciar Enter, Space e clique no botão externo. | Fluxo atual pelo receptor observado; protótipo cobre só Enter no principal. Demais caminhos não comprovados para a extensão. |
| P3 — perda de foco e memória de teclas do contrato atual; limpeza em `GameControls.kf:187`; casos existentes em `tests/browser_controls.py` | Com movimento ativo, sair do novo receptor permitido deve limpar movimento efetivo sem pausar. Voltar por Tab não deve retomar uma tecla antiga; uma soltura observada seguida de nova pressão permite mover. Incluir soltura fora da árvore, preservando as regras documentadas e qualquer exceção explicitamente aprovada. | Reutilizar o controle negativo e os percursos de retorno por Tab/clique em `tests/browser_controls.py`; comparar posição por seis passos após saída e após retorno, antes e depois de soltura/nova pressão. Registrar o destino do foco. | Falha demonstrada na alteração de uma linha: x=30→60 depois de Shift+Tab. Critério não satisfeito. |
| P4 — Especial e prioridades do contrato atual; filtro de tecla 1 em `GameControls.kf:288` | No caminho sem clique aprovado, tecla 1 com carga disponível deve criar três feixes e consumir uma carga, uma vez por pressão; manter/repetir não acumula tentativas. Direcional mantido conserva prioridade, e soltá-lo não retoma seta antiga automaticamente. | Reutilizar `tests/browser_weapons.py`/`tests/weapons.kf` e `tests/browser_controls.py`. Preparar carga realmente disponível, observar consumo e feixes pelos pontos públicos existentes; uma tentativa sem carga não prova a aceitação da tecla. | Não verificado no protótipo; seu filtro de tecla 1 não foi alterado. |
| P5 — composição e navegação acessível existentes | Tab/Shift+Tab ainda percorrem os controles; guia e Mais detalhes não iniciam partida nem acionam especial por engano. Setas originadas fora do escopo aprovado não deixam movimento pendente. O contorno representa o receptor efetivo. | Reutilizar provas existentes do guia/foco em `tests/browser.py`; observar telas, seleção, contorno e a primeira atualização após voltar à partida. | Comportamento atual consultado; extensão não comprovada. |

### Obrigações do executor antes da entrega

- Conferir separadamente se cada expectativa corresponde ao pedido e às exceções aprovadas e se cada cenário/assertion realmente distingue o resultado correto de um plausível resultado incorreto. Não converter o protótipo nem um teste verde em autoridade normativa.
- Confirmar o escopo de recepção e suas transições antes de modificar o contrato. Consultar novamente o training de UI, anti-patterns e fontes atuais do Kof; demonstrar em JS qualquer API ou mecanismo novo de foco. A inscrição atual em uma coluna não demonstra inscrição global nem foco programático.
- Reaproveitar as provas existentes, ampliando só as lacunas acima. Executar `python3 tests/browser.py`, `python3 tests/browser_controls.py`, `python3 tests/browser_weapons.py`, `python3 scripts/kof_project.py test --target jvm` e `python3 scripts/kof_project.py test --target js` após a implementação escolhida.
- Registrar por critério comando/procedimento, SHA, alvo, navegador, resultado observado, assertion relevante e artefato opcional no aceite de controles existente. Uma suíte aprovada não substitui a associação por critério. Registrar falhas, cobertura faltante e critérios não verificados antes da entrega.

Investigação concluída, sem alteração de fontes de produção. A extensão proposta e a ativação automática desde BODY não estão entregues. Evidência gerada permanece em `.agent/tmp/keyboard-no-click/`, excluída localmente do Git.

## Execução aprovada: foco do menu durante a partida — 08/10/2026

O usuário aprovou a extensão delimitada na mensagem “Jogar sem clicar na área após navegar pelo menu” e confirmou execução no chat atual, na mesma pasta. Branch `keyboard-menu-focus`, base `27dcc29f5b7e617249e6381824401e99fee85d5d`. Chat `controls-keyboard-primary`, `gpt-6.1-sol`/`medium`, todos os papéis no mesmo contexto; sem workers separados nem worktree. O ledger v6 e o plano literal ficam em `.agent/tmp/keyboard-menu-focus.*`.

A classificação derivada em GameControls, retenção até blur, nome acessível temporário, limpeza de movimento no blur e recepção de1 foram implementados. README, especificação e guia descrevem o novo contrato. As jornadas existentes recebem provas de entrada exclusivamente por teclado, clique/toque em opções, pausas, retorno por Tab/Shift+Tab, memória de teclas, pixels e três feixes disponíveis. O [aceite existente](.agent/validation/sifuture-controls.md#aceite-jogar-com-o-foco-adquirido-no-menu--08102026) mantém auditorias separadas de expectativa e assertions, RED/GREEN, critérios e limites.

Inventário confirmado: onze checks locais (Kof JVM/JS, sete jornadas Chrome, Python e contrato CI); CI resolve a distribuição oficial e testa JVM/JS. Sonar, Habit e mutation runner excluídos por ausência de configuração. Gates completos sobre os commits, revisão estrutural no mesmo contexto e entrega em PR seguem o fluxo da skill; não há autorização de merge ou publicação neste ciclo.
