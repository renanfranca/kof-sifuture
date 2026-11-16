# SiFuture em Kof 0.6.4 com Kof e KofMut vindos do PATH

> **Para a sessão executora:** plano aprovado em conversa em 01/11/2026 e preparado em outra sessão. Trabalhar no checkout atual `/home/renanfranca/projects/kof-sifuture` (branch `sensor-calibration-m1`), sem worktree, sem subagentes, **sem commit nem push**. Antes de começar, ler o `AGENTS.md` do SiFuture e o training index do Kof, e reconferir os “Fatos conferidos” abaixo: se algum mudou, parar e informar o usuário. Instalar o KofMut em `~/.local` está autorizado. Nenhuma outra alteração no repositório KofMut.

## Context

Antes do M2 dos sensores, o usuário quer garantir que tudo o que foi entregue no SiFuture funciona com Kof 0.6.4 e que o KofMut usado é o atual da `main`. A investigação mostrou duas fixações que contrariam isso. Decisão do usuário: **Kof e KofMut devem vir do PATH**, instalando a versão atual do KofMut. **Sem commit.**

Fatos conferidos (01/11, somente leitura):
- `kof` → `~/.local/share/kof/kof-0.6.4-linux-x86_64/bin/kof`, `kof 0.6.4`.
- KofMut checkout: `main` = `origin/main` = `9f9bb06` (merge do PR #2), limpo.
- `kof-mut` no PATH → `~/.local/bin/kof-mut` → `~/.local/share/kof-mut/current/launch.sh`, imagem `b8b2faa7…` instalada em **25/10**, construída com Kof 0.6.6. **Está defasada**: `Run.kf`, `Evidence.kf`, `RunResources.kf`, `InstalledPreflight.kf` e `CompatibilityProbe.kf` diferem da `main` (inclui o leitor de várias suítes).
- ❗️ O KofMut **não se atualiza sozinho**. Pelo `docs/cli.md` (linhas 60–62), ele adota automaticamente outro **Kof** compatível no PATH sem reinstalar, mas o próprio código só muda com `./install.sh` rodado a partir de um checkout atualizado.
- `scripts/kof-sensors/run` já usa o jar ao lado do `kof` do PATH. Só `mvn test` direto usa o padrão 0.6.6 do `pom.xml`, e com isso mistura parser 0.6.6 com `kof check` 0.6.4 (`AnalyzerTest.java:22`).
- `verify-kofmut` exige o checkout em `a40b20ac`, mas a receita real chama `/home/renanfranca/projects/kof-mut/bin/kof-mut`, em qualquer revisão.
- O CI do SiFuture usa o release mais recente do Kof (0.6.9), não o PATH local. Só registro.

## Mudanças

1. **Instalar o KofMut atual** (fora dos repositórios): `cd /home/renanfranca/projects/kof-mut && ./install.sh`, com 0.6.4 no PATH. Prefixo padrão `~/.local`; a imagem anterior fica preservada. Conferir `kof-mut --version`, o novo `current` e o `image.json` (`buildDependency.version` 0.6.4; `runtimeSources` iguais aos arquivos de `main`).
2. **`scripts/kof-sensors/pom.xml`**: remover o caminho padrão 0.6.6 e trocar a versão rótulo da dependência `system` por um valor neutro (`installed`). Sem `-Dkof.jar`, o Maven falha explicitamente em vez de usar outra versão em silêncio.
3. **Novo `scripts/kof-sensors/test`** (Python, mesmo padrão do `run`): resolve `KOF`/PATH, o jar ao lado (`KOF_JAR` opcional) e executa `mvn -f pom.xml test -Dkof.jar=<jar>`. Para não duplicar código, extrair a resolução de `kof`/jar do `run` só se ficar natural. Do contrário, manter as poucas linhas paralelas.
4. **`scripts/kof-sensors/verify-kofmut`**: remover a constante `revision` e a recusa por SHA. Executar o `kof-mut` resolvido no PATH (`shutil.which`). As fixtures `detected`/`survived` continuam vindo do checkout (argumento 1, padrão atual). Recusar se o checkout estiver sujo ou se os `runtimeSources` do `image.json` instalado não baterem com os arquivos do checkout, porque nesse caso a instalação está defasada em relação às fixtures. O sumário registra o caminho do `kof-mut`, o id da imagem e o SHA do checkout. O restante das asserções fica como está.
5. **Receita manual** em `docs/desenvolvimento.md` e `docs/desenvolvimento.pt_BR.md`: trocar `/home/renanfranca/projects/kof-mut/bin/kof-mut` por `kof-mut`. Ajustar o texto que cita o checkout, se houver.
6. **`scripts/kof-sensors/README.md`**: comandos (`scripts/kof-sensors/test` no lugar de `mvn … test`), regra “Kof e KofMut do PATH”, fim da exigência de `a40b20ac`.

Não mexer em fontes ou testes do jogo, `kof-mut.json`, `kof-mut-scope.json`, wrapper `kof_project.py` nem no repositório KofMut.

## Revalidação com 0.6.4 (sequencial; logs em `.agent/tmp/kof064-revalidation-20261101/`)

Antes de tudo, salvar hashes de `src/`, `tests/`, `kof-mut*.json` e `scripts/kof_project.py` no scratchpad.

1. `python3 -m unittest discover -s tests -p 'test_*.py'` (anterior: 16).
2. `python3 scripts/kof_project.py check --target jvm|js --json` (success true, 0 erros).
3. `python3 scripts/kof_project.py test --target jvm|js` (114 casos, 0 falhas em cada).
4. `scripts/kof-sensors/test` (anterior: 21 testes) e também `mvn -f scripts/kof-sensors/pom.xml test` sem `-Dkof.jar`, que agora deve falhar explicitamente.
5. `scripts/kof-sensors/run .` e comparação por arquivo e unidade com `.agent/tmp/sensors-m1-repair-20261025-continuation/inventory.json` (25 arquivos, 321 unidades, 45.443 tokens, 17 grupos CPD). Diferenças serão listadas.
6. As sete jornadas `python3 tests/browser*.py` (a parte que quebra no 0.6.9).
7. `scripts/kof-sensors/verify-kofmut`: `detected` complete/0 Killed, `survived` complete/1 Survived, hashes preservados, `kofVersion` 0.6.4. Controle negativo: com a imagem anterior ativa, a recusa por defasagem deve aparecer. Por isso a ordem de execução é: Mudanças 2–6, verify novo contra a imagem de 25/10 (recusa registrada), Mudança 1 (instalar) e depois os passos 1–8 desta seção.
8. Receita manual atualizada sobre Background + Meteor. Referência de 26/10 (0.6.6, checkout `338c7b3`): complete/1, 42 candidatos, 38 Killed, 4 Survived, sem pendências. Conferir UUID, `reportPath`, contagens, exit e preservação.
9. Opcional, a confirmar se o tempo permitir: `./scripts/check` do KofMut na `main` com 0.6.4 (cerca de 12 min, sozinho na máquina; o registro de 01/11 em `check-parallel.md` já cobre essa árvore com 0.6.4).

## Registro (sem commit)

Acrescentar uma continuidade datada em `.agent/validation/sensors-adoption.md` e no `EXECPLAN.md` do SiFuture: decisão “Kof e KofMut do PATH”, imagem instalada, comandos, resultados, controle negativo e pendências (CI em 0.6.9). Resumo também no plano externo dos sensores. Atualizar a memória `sensors-kof-version` (Kof e KofMut do PATH; o KofMut só se atualiza reinstalando). Históricos preservados como prefixo.

## Verification

- Cada passo com comando, exit e números reais. Falha fica registrada como falha, sem repetir até passar.
- Hashes do jogo e das configurações iguais antes e depois. `git status` mostra apenas os arquivos listados em Mudanças e os registros. Repositório KofMut sem alterações.
- `git diff --check`; `bash -n` nos blocos de shell alterados da receita.
