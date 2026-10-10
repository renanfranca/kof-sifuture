# Reorganização da documentação — 09/10/2026

Base examinada: SiFuture em Kof
`e38f5e0ccb98bfd443a0d57833b6be0b6bed6aee`, branch `sifuture-documentation`.
Os comandos abaixo verificam essa base com as alterações documentais locais;
nenhum novo commit ou publicação é atribuído a esta execução.
Fontes Kof locais: `317d9f6b1c3e27032cc955a05f859f6c627d9338`.
História original consultada: SiFuture
`6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f`.

## Escopo e destinos

| Público | Entrada e documento responsável |
| --- | --- |
| Visitante | [README](../../README.md): motivação em primeira pessoa, jogo disponível, estado, documentação e recursos. |
| Jogador | [Como jogar](../../docs/jogar.md): percurso mínimo antes de detalhes de foco e recuperação. |
| Leitor das regras | [Regras do jogo](../../docs/regras-do-jogo.md): conceitos, progressão, armas, encontros, indicadores, resultado e diferenças aprovadas. |
| Colaborador | [Desenvolvimento](../../docs/desenvolvimento.md): requisitos, receitas locais, raízes de fontes, workaround e código. |
| Mantenedor | [CI e publicação](../../docs/ci-e-publicacao.md): distribuição, checks, atualização na URL oficial, reprodução e recuperação. |

[fonts/README.md](../../fonts/README.md) continua responsável pela tipografia.
Especificações, EXECPLAN e registros anteriores conservam requisitos e provas
das suas revisões. Os seis documentos previstos são o escopo de escrita neste
repositório. Código, testes, scripts, workflow, manifesto, assets, AGENTS.md e
demais documentos são protegidos.

O usuário corrigiu o período cursado para **quarto período** durante a execução
e pediu a mesma correção no projeto histórico. Essa autorização adicional
limita a escrita em `sifuture` ao README, na branch `fourth-semester-history`:
linha 13 em inglês e linha 115 em português. O segundo semestre **de 2006** é
a época do desenvolvimento e permanece intacto. A revisão histórica fixada
acima antecede essa correção biográfica; a instrução do autor é a fonte da
correção. Nenhum arquivo do repositório Kof é alterado.

## Expectativas conferidas

| Critério | Fonte e conclusão |
| --- | --- |
| Abertura em primeira pessoa | Relato original de 2006 a 01/08/2007, aprendizado pela Sun, slogan e emulador; quarto período conforme correção explícita do autor. |
| Link de jogo | README e guia apontam exatamente para `https://renanfranca.github.io/kof-sifuture/`. |
| Atualização automática | Gatilho push em main; `build-pages` depende de `resolve-kof` e `test`; `deploy-pages` depende do build e exige freshness. Merges iniciam o fluxo; sucesso e revisão atual condicionam a publicação na mesma URL. |
| Portabilidade honesta | Especificação exige navegador e Android para v1, reservando JVM/Native gráficos à pesquisa. Bloqueio Android de 06/10/2026 e revisão publicada de 09/10/2026 mantêm SHA, ambiente e lacunas. |
| Percurso do jogador | Créditos → Novo Jogo → movimento → pausa/Continuar → resultado/menu; especial e recuperação aparecem depois. Comparado com ControlsGuide, GameControls e especificação. |
| Receitas do colaborador e mantenedor | Argumentos e precedência `--kof`/`KOF`/`PATH` conferidos no wrapper e em sua ajuda; distribuição e reexecução conferidas no helper e workflow. |
| Navegação compatível | Os 13 fragmentos antigos recebem IDs explícitos perto dos resumos e encaminhamentos. Todos os guias voltam ao README e ligam assuntos complementares. |
| Conceitos antes dos detalhes | Mundo/passo precedem fase; contadores são explicados antes de faixas; classe, enum, semente, raiz de fontes, suíte e fixture têm definição; revisão/SHA/artefato/job precedem os procedimentos de publicação. |

Correção factual adicional: a issue Kof #708 está fechada. O checkout local
não contém o objeto mais novo, por isso a decisão, implementação e teste foram
lidos na [revisão upstream fixada](https://github.com/KofLang/Kof4j/commit/0e6a02f23d295d89e2ce4975b6d8b177240f5222).
`D-CLI-SOURCE-ROOTS` registra raízes explícitas em `[sources]`; CmdBuild as
resolve, e TwoRootsCliE2ETest cobre build e import da aplicação pelos testes.
Esse teste upstream foi consultado, não executado. O manifesto SiFuture segue
sem `[sources]`; documentar a evolução não migra a instalação nem o wrapper.

## Provas executadas e suficiência

Ambiente local: Linux x86_64, `kof 0.5.0-beta`, compiler/runtime/stdlib 0.5.0,
Eclipse Adoptium 25.0.4.1 e `embeddedJdk: true`, conforme `kof info --json`.
O SHA de origem da instalação no PATH não é presumido a partir do checkout.
Nenhum navegador foi executado neste trabalho documental.

Comandos de conferência:

```bash
kof version
kof info --json
python3 scripts/kof_project.py build --help
python3 scripts/kof_project.py test --help
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
python3 scripts/kof_project.py build --output .agent/tmp/documentacao/site
python3 /home/renanfranca/.agents/skills/restructure-documentation/scripts/check_markdown_links.py README.md docs fonts/README.md .agent/validation/documentacao.md
git diff --check
git -C /home/renanfranca/projects/sifuture diff --check
```

As execuções de build/test usaram `PYTHONDONTWRITEBYTECODE=1`; os logs foram
guardados em `.agent/tmp/documentacao/`. Ambas as suítes retornaram 0:

```text
0 failed of 114 tests
1 passed, 0 failed
```

O build retornou 0 e produziu `index.html`, `Default.mjs`, módulos/runtime e
assets em saída local. Isso verifica as receitas e o modelo em JVM/JS; não
constitui um novo aceite gráfico. O servidor HTTP e as sete jornadas Chrome
não foram reexecutados; os resultados citados nos guias pertencem aos registros
anteriores e são identificados por revisão e ambiente.

O validador local antes da reorganização retornou 1 por destinos dependentes
de caminhos locais. Após a reorganização, retornou **0** para README, docs,
fonts/README e este registro. `git diff --check` retornou **0** nos dois
projetos. A navegação por registros históricos usa os documentos completos;
seus títulos com pontuação não exigem novos IDs nesses arquivos protegidos.

Auditorias adicionais executadas, sem adicionar testes ao produto:

```bash
python3 .agent/tmp/documentacao/check_structure.py
python3 .agent/tmp/documentacao/check_external.py
```

Resultado da auditoria de interfaces e escopo:

```text
old_fragments: 13
protected_files: 176
original_commands_preserved: 23
guide_return_links: 4
documentation_files: 6
historical_readme_edits: 2
build_files: 113
result: PASS
```

Os 13 IDs são comparados ao inventário anterior, com unicidade e destinos
válidos. Os 23 comandos não incluem os antigos `cd` para o caminho pessoal:
os guias exigem execução na raiz do checkout, conservando comandos e argumentos
de build/test/servidor/reprodução. Os hashes SHA-256 dos 176 arquivos protegidos
continuam idênticos. No projeto histórico, o README corresponde exatamente à
base com as duas substituições autorizadas, em inglês e português.
Os excertos Kof dos guias correspondem a trechos contíguos das fontes reais.
O build tem 113 arquivos; os assets foram comparados aos originais do checkout.

A conferência externa retornou HTTP 200 para **39 URLs distintas**, sem
pendência. Links de fonte `github.com/.../blob/...` foram resolvidos pelo
conteúdo equivalente em `raw.githubusercontent.com`, com conferência das
linhas citadas e dos bytes das revisões históricas disponíveis localmente.
A URL do jogo, issues, workflow, vídeo e documentação do GitHub também
responderam. Isso comprova acesso aos destinos, não o conteúdo visual do vídeo
nem o funcionamento do jogo. Os quatro percursos foram revisados do README
até seus guias e até as receitas ou explicações correspondentes, sem ciclos
que impeçam a conclusão.

A referência antiga a `Window.size(296, 510)` não foi transferida como chamada
atual da aplicação: Main.kf e a saída compilada não a usam. A largura observada
no viewport de 320 pixels é descrita como medida desse ambiente. Isso evita
atribuir às outras larguras uma configuração fixa que o código não aplica.

## Evidência de publicação consultada e lacunas

O [workflow 37949665153](https://github.com/renanfranca/kof-sifuture/actions/runs/37949665153)
e o [registro existente](sifuture-controls.md)
documentam o SHA publicado `5609febbc76cc2dd5d0f52c90349dae3ef1f5057`, comparação
de 113 arquivos e percurso específico do menu no Chrome 155.0.8059.39.
Não representam execução do CI sobre esta reorganização.

As lacunas preservadas são Android físico, comparação com o vídeo histórico,
áudio/Opções/Música, pausa automática, escala adaptável, captura fora dos
controles e aprovações visuais ainda pendentes nos registros respectivos.
HTTP e validação de links não encerram nenhuma dessas aceitações.

Evidências locais opcionais: inventário anterior, cópia do README, hashes dos
176 arquivos protegidos, logs de links, ajuda/ambiente, testes JVM/JS, build e
fontes upstream consultadas em `.agent/tmp/documentacao/`. O resumo acima
contém resultados essenciais; os arquivos locais não são links necessários
para compreender a validação. A exclusão local `/.agent/tmp/` é conferida
exatamente uma vez, sem alterar arquivos de exclusão versionados.
