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
- [x] Entidade, progressão e TDD: 72 cenários executados em JVM e JS.
- [x] Geometria histórica, prioridade, marcadores do especial e prêmio único.
- [x] Desenho/transições; checkpoints Chrome de controles, armas, fase e subchefe aprovados. Os seis percursos serão executados pelos gates formais.
- [ ] Aceite por critério, revisão estrutural, gates finais e CI.
