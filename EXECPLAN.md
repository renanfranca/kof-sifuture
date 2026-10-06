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
- **Interface:** quatro botões de **56 × 56 px**, cruz de **168 × 168 px**, sem espaçamento interno, com centro e cantos vazios. Conservar Especial à direita, **72 × 64 px**, centralizado verticalmente e separado por **16 px**. Usar janela de **296 px** de largura na aplicação e nas fixtures com esses controles para caber em viewport de 320 px.
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
