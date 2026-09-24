# Construir o primeiro ciclo jogável de SiFuture em Kof

## Purpose and success

Entregar o percurso de navegador menu → Novo Jogo → partida com nave, tiros e meteoros → resultado após três vidas → menu, em Kof. Cada etapa deve ter código Kof executável, um comando de execução e um experimento pequeno para o leitor. Se a API de entrada impedir o percurso, deixar reproducer e evidência precisa, mantendo as regras e a cena executáveis onde possível.

## Context and limits

O projeto inicia apenas com `AGENTS.md` e a especificação `.agent/specifications/port-sifuture-to-kof.md`. A fonte histórica é `/home/renanfranca/projects/sifuture`; a implementação Kof está em `/home/renanfranca/projects/kof`, versão `0.4.10-beta`, SHA `ebd11a1af42b525c583c28ab444e060fae8a9c6a`. A branch de trabalho limpa `port-sifuture-to-kof` já corresponde ao pedido. Consulte os documentos Kof listados em `AGENTS.md` antes de atribuir capacidades. Este recorte omite os recursos reservados a ciclos posteriores no pedido; não declara a especificação integral concluída. Nenhum JavaScript, CSS ou DOM escrito à mão, nem alterações em `.mjs` gerado.

## Milestones

1. **Provar ferramentas, desenho e entrada.** Criar `probes/ui-input.kf`, incluir sprites históricos mínimos em `assets/`, e documentar em `README.md` a sintaxe de `Window`, `Canvas`, `Image`, `time.interval` e eventos. Validar com o compilador Kof do SHA acima (`bin/kof build probes/ui-input.kf --target=js`) e abrir o `index.html` gerado em navegador real; verificar atualização e pressionar/soltar teclas. Se falhar, registrar `docs/kof-input-gap.md` com programa, comando, ambiente e resultado. Aceite: imagem/intervalo visíveis e evento comprovado, ou dossier do bloqueio.
2. **Construir regras isoladas.** Criar `src/Game.kf` com testes Kof no próprio arquivo (blocos `test`, ignorados pelo build normal), mundo 176 × 220, passo 30 ms, nave 5 unidades, tiro normal automático a cada 13 passos, seis meteoros horizontais, colisões, pontos, três vidas, reinício e resultado. Preservar regras relevantes do histórico e aceitar semente injetada com `rng.seed`. Validar com `bin/kof test src/Game.kf --target jvm` e `--target js`. Aceite: testes de semente, limites, tiro, colisão, vidas, pontuação, reinício e seis fronteiras de resultado verdes.
3. **Conectar o percurso.** Criar `src/Main.kf`, copiar sprites históricos usados e incluir instruções de execução e lições por etapa no `README.md`. Validar `bin/kof build src --target=js`, servir a saída gerada por HTTP local e exercitar menu, setas com soltura, derrota, resultado persistente e Enter para voltar no Chrome. Aceite: percurso completo observado, ou bloqueio documentado sem esconder as partes executáveis.

## Progress

- [x] Fontes locais, branch, especificação e SHA identificados.
- [x] Ferramentas e prova de UI concluídas: build JS; Chrome real mostrou sprite, 30 quadros, `keydown`/`keyup` no `Input` focado.
- [x] Regras e testes concluídos: 5 testes verdes em JVM e JS; `test` fica no arquivo da regra para compilar o código real sem duplicação.
- [x] Percurso no navegador e documentação concluídos: menu, movimento/soltura, três vidas, resultado persistente e retorno testados no Chrome; instruções e limite de foco registrados.

## Validation

Revisão visual no Kof `0.4.10-beta` (`ebd11a1af42b525c583c28ab444e060fae8a9c6a`): 16 testes Kof passaram tanto em JVM quanto em JS; o build JS passou. O percurso Chrome passou duas vezes, inclusive a troca `Middle.png`/`Middle2.png` com teclas opostas. O fixture Kof `tests/meteor-motion.kf` também passou duas vezes no Chrome: um clique por passo confirmou o movimento horizontal durante os três quadros de impacto e o reaparecimento. O estado avança em `step()` e `render()` apenas lê os quadros.

Ampliação do ciclo em Kof `0.4.10-beta` (`ebd11a1af42b525c583c28ab444e060fae8a9c6a`): 15 testes de comportamento em JVM e JS, build JS e percurso Chrome passaram. As regras agora incluem laser básico único, precedência histórica da colisão da nave, explosão e reinício temporizados no `step()`, meteoros animados e pontuação nas duas colisões, suas fórmulas históricas e o quadro `laser03.png` de impacto. O teste de navegador espera a mudança observável da posição da nave e estabilização após `keyup`.

Comandos observados no SHA acima: `mvn -q package -DskipTests` (exit 0, Maven 3.9.11 local em `/tmp`); `bin/kof check probes/ui-input.kf --target js` (exit 0); `bin/kof build probes/ui-input.kf --target js --output /tmp/sifuture-probe` (exit 0); Chrome real servido por HTTP mostrou canvas 176 × 220, sprite não vazio, contador de quadros e `keydown`/`keyup` após clique no Input. `bin/kof test src/Game.kf --target jvm` e `--target js`: ambos exit 0, 5 testes aprovados. `bin/kof build src --target js --output /tmp/sifuture-game` (exit 0); `python3 tests/browser.py` (exit 0, percurso integral observado no Chrome real). Auditoria: a aplicação e a prova contêm apenas `.kf`; Python é somente automação de teste, e não há JS/CSS nem `.mjs` escrito ou editado. `LICENSE` e `NOTICE` distinguem código e sprites históricos.

## Risks

- `Canvas` não oferece `.on(...)` na implementação inspecionada; uma composição de eventos em widget vizinho ainda precisa de prova de foco e keyup.
- O checkout Kof não tem distribuição empacotada e não há `mvn` no PATH atual. Isso pode atrasar a validação, mas o compilador deve ser preparado antes de assumir um bloqueio da linguagem.
- Recursos históricos têm direitos incertos segundo `/home/renanfranca/projects/sifuture/NOTICE`; copiar apenas os necessários e preservar aviso explícito.
- O teclado requer foco explícito no `Input`; a composição funciona depois do clique, mas não recebe Enter logo na abertura. O dossier `docs/kof-input-gap.md` conserva o reproducer e a classificação cautelosa.
