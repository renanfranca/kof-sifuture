# KofMut aceita declarações `enum`

> **Para a sessão executora:** autorizado pelo usuário em 07/11/2026. Trabalhar em `/home/renanfranca/projects/kof-mut`, sem worktree, sem subagentes e **sem commit nem push** (o usuário faz com Luna).
>
> Antes de começar:
> - copiar este plano para `/home/renanfranca/.agents/skills/_temporary/codex-skills-ai-context/2026-11-07_FEATURE_kofmut-enum-declarations.md` e trabalhar a partir dessa cópia;
> - ler o `AGENTS.md` do KofMut, o `.agent/README.md` e o training index do Kof;
> - conferir: `main` = `origin/main` = `77dfa58`, checkout limpo, `kof version` = `kof 0.7.0` e 0.6.4 em `~/.local/share/kof/kof-0.6.4-linux-x86_64`. Se algo divergir, parar e avisar;
> - criar a branch `enum-declarations` com o skill `create-git-branch`;
> - invocar o skill `tdd-behavior-autonomous-quiet` pelo Skill tool, sem comentários `[TEST]`.

## Context

Uma execução real do KofMut sobre toda a produção do SiFuture gerou 8 limitações `Unsupported AST node: dev.kof.compiler.EnumDeclarationNode`. É o R0 do pagamento da dívida dos sensores: `/home/renanfranca/projects/kof-sifuture/.agent/validation/sensor-debt-payoff.md`, seção "KofMut sobre toda a produção" (linhas 60 a 104, commit `e6703db` do SiFuture). As limitações vieram de `Boss.kf`, `Item.kf`, `MenuEntrance.kf`, `Subchief.kf` e quatro vezes de `State.kf`.

A mensagem é gerada em `src/main/kof/kofmut/Frontend.kf:502`, no fim da visita, para qualquer nó sem tratamento. Qualquer limitação torna a execução `incomplete`, com exit 3 (`src/main/kof/kofmut/Run.kf:116`; `docs/report-format.md:205`). O resultado é que um arquivo com `enum` nunca chega a `complete`, mesmo com todos os mutantes mortos, e o `npm run check` do SiFuture sempre reprova esse escopo (`kof-sifuture/scripts/mutation-step.mjs`, tabela `VERDICTS`: exit 3 vira `FAIL`).

## Fatos conferidos em leitura (07/11, durante o planejamento)

Observações feitas só com leitura; não provam o resultado da implementação.

- Referência do Kof (`/home/renanfranca/projects/kof/docs/language-reference/classes.md:133-145`): um `enum` é só uma lista de identificadores, `enum-declaration = modifiers , "enum" , identifier , "{" , [ identifier , { "," , identifier } ] , "}"`. Métodos, campos e corpo dão `PARSE032`.
- O checkout do Kof em `/home/renanfranca/projects/kof` está em `22a111f56`, que **não** é a tag 0.7.0. Por isso a forma do nó foi conferida nos jars instalados, que são a autoridade pelo `AGENTS.md`:
  - comando: `<kof>/jdk/bin/javap -cp <kof>/lib/kof.jar dev.kof.compiler.EnumDeclarationNode dev.kof.compiler.AnnotationPair` para `kof-0.7.0-linux-x86_64` e `kof-0.6.4-linux-x86_64`;
  - resultado: nas duas versões, `EnumDeclarationNode(SourcePosition, String name, List<String> modifiers, List<String> constants, List<AnnotationNode> annotations)` e `AnnotationPair(String key, Object value)`, com os mesmos acessores. Nenhum campo contém expressão ou corpo, então o nó não tem ponto de mutação.
- Valores de anotação vêm de `AnnotationParser.parseAnnotationValue` (`kof-compiler/.../parser/AnnotationParser.java:47`): literais e referências a enum (`AnnotationEnumRef`, `grammar.md:418`), não expressões mutáveis.
- O `Frontend.kf` trata `ClassDeclarationNode` (linha 134) e `MethodDeclarationNode` (linha 158) por tipo, explicitamente. Nenhum arquivo em `src/main/kof/kofmut/` chama `annotations()`: anotações de classe são ignoradas, sem limitação e sem sítio. Não há teste que cubra uma classe anotada.
- Testes existentes que já cobrem "nó não suportado continua limitação":
  - `src/test/kof/kofmut/FrontendContracts.kf:132-140` (`unsupportedForms`): `record Point(Int x)` produz exatamente 1 limitação contendo `RecordDeclarationNode` e 0 sítios;
  - `src/test/kof/kofmut/Run.kf:425-444` ("unsupported production forms and absent applicable operators stay inconclusive", fila `check-run-b`): o mesmo `record` pelo comando público dá exit 3, `incomplete`, 1 limitação.
- Padrão de fluxo com mutante morto: `fixtures/detected` (`src/math/Calc.kf` com `class Calc { Int sum(Int a, Int b) { return a + b } }` e teste `sum(2, 3) == 5`), copiado por `runProjectCopy()` (`Run.kf:115`), com asserções de `Killed`, `complete` e `limitations.size == 0` em `Run.kf:55-74`.
- O id do mutante é `file + ":" + offset + ":" + replacement` (`Run.kf:108`). Portanto inserir um `enum` **antes** da função desloca os offsets e muda os IDs.
- `KOF_MUT_COMPATIBILITY_OTHER` só é lido em `src/test/kof/kofmut/Install.kf:1174` (aprovação de compatibilidade). As suítes de frontend e de execução rodam só com o Kof primeiro no PATH. Logo, o `./scripts/check` do K4 **não** exercita o enum no 0.6.4.
- Documentação que cita a sintaxe não percorrida: `docs/operators.md:59` e `docs/operators.pt_BR.md:59` usam `record` como exemplo. `README.md:82` e `docs/llm-guide.md:75,88` falam de sintaxe não suportada de forma genérica.
- No R0, por arquivo do SiFuture: `MenuEntrance.kf` 7 candidatos, 7 mortos; `Item.kf` 39, 27 mortos, 12 sobreviventes; `Background.kf` 1, 1 morto, sem `enum`; `State.kf` 0 candidatos, só com os quatro `enum`.

## Mudança

Tratar `EnumDeclarationNode` no `Frontend.kf` como uma declaração **sem pontos de mutação e sem limitação**, no mesmo padrão explícito, por tipo, usado nos demais nós. Não criar um ramo genérico que aceite nós desconhecidos.

**Decisão sobre anotações em `enum`** (resolve o condicional anterior): o KofMut já ignora anotações de classe sem limitação, e valores de anotação não são expressões mutáveis. Então `enum` anotado recebe o mesmo tratamento: sem limitação e sem sítio. Se o executor encontrar uma fonte que contradiga isso, parar e avisar em vez de escolher outro comportamento.

## Critérios de aceitação

Cada critério traz fonte, exemplo, verificação planejada, evidência esperada e lacuna. Isto é o **planejado**; o observado vai para o registro em `.agent/validation/`.

- **K1. Um enum puro não gera limitação.**
  - **Fonte:** gramática em `classes.md:133-145`; forma do nó conferida nos jars; contrato de status em `docs/report-format.md:197-207`.
  - **Exemplo:** a cópia de `fixtures/detected` com `Calc.kf` = `package src.math` + a classe `Calc` original + `enum Phase { A, B }` **depois** da classe. Ação: `./bin/kof-mut run --project <cópia> --files <cópia>/scope.json --report-dir <cópia>/report.json`.
  - **Esperado:** exit 0, `status: complete`, `limitations: []`, 1 candidato, 1 mutante `+ -> -` com `status: Killed`.
  - **RED esperado antes da mudança:** exit 3, `incomplete`, 1 limitação contendo `Unsupported AST node: dev.kof.compiler.EnumDeclarationNode`, o mutante ainda `Killed`. Isso mostra que o mesmo cenário distingue as duas implementações.
  - **Verificação:** novo `test` em `src/test/kof/kofmut/Run.kf`, com uma tag `check-run-a` ou `check-run-b` (o check exige exatamente uma), no padrão de `Run.kf:425-444`, asserindo exit, `status`, `limitations.size == 0`, `counts.killed == 1` e o conteúdo exato da limitação no RED. Mais um caso em `FrontendContracts.kf` pela função `scanSource`: `enum Phase { A, B }` sozinho dá `errors == 0`, `limitations == 0`, `sites == 0`.
  - **Caso adicional:** `@Name("x") enum Phase { A }` em `scanSource` também dá 0 limitação e 0 sítio (decisão de anotações). O executor deve confirmar antes, com `kof check` num arquivo descartável em `.agent/tmp/`, que essa anotação é aceita pelo 0.7.0; se não for, usar uma anotação que o Kof aceite e registrar qual.
  - **Lacuna:** nenhuma prevista.
- **K2. O enum não cria mutantes nem altera os existentes.**
  - **Fonte:** o nó não tem expressões (jars); id definido em `Run.kf:108`.
  - **Exemplo:** pela `scanSource`, a fonte `Bool less(Int a, Int b) { return a < b }` com e sem ` enum Phase { A, B }` **anexado ao final** produz a mesma lista de sítios: 1 sítio, `<` para `<=`, offset 35, linha 1, coluna 36 (os mesmos valores de `binaryTokenLocation`, `FrontendContracts.kf:5-21`). No teste de fluxo do K1, o id do mutante é igual ao do fixture sem enum.
  - **Por que distingue:** uma implementação que visitasse as constantes poderia inventar sítios e ainda passar no K1 se as asserções olhassem só o status. O enum vai no final para que um deslocamento de offset não seja confundido com sítio novo.
  - **Verificação:** comparar a lista inteira (tamanho e campos), não só a contagem.
- **K3. Um nó realmente não suportado continua gerando limitação.**
  - **Verificação:** reutilizar `unsupportedForms` (`FrontendContracts.kf:132-140`) e o teste de `Run.kf:425-444`, **sem alterá-los**. Os dois precisam continuar passando no check. Não criar duplicata.
  - **Por que distingue:** um "ignorar qualquer nó" passaria no K1 e no K2 e falharia aqui, porque `RecordDeclarationNode` deixaria de gerar limitação.
  - **Evidência esperada:** as linhas `PASS frontend: unsupported AST forms produce explicit limitations` e o teste da fila `run-b` no `.out` da execução do check.
- **K4. `./scripts/check` passa.**
  - **Comando:** `PATH=$HOME/.local/share/kof/kof-0.7.0-linux-x86_64/bin:$PATH LC_ALL=C.UTF-8 KOF_MUT_COMPATIBILITY_OTHER=$HOME/.local/share/kof/kof-0.6.4-linux-x86_64/bin ./scripts/check`.
  - **Esperado:** exit 0, todas as filas com exit 0 (o 0.7.0 levou 803 s em `kof-070-revalidation.md`).
  - **Prova no 0.6.4:** como o check não roda o frontend no 0.6.4, rodar à parte o novo caso do K1 em `FrontendContracts` e o teste de fluxo do K1 com o 0.6.4 primeiro no PATH (o mesmo comando que o check usa para essas suítes, só com o PATH trocado). A forma do nó é igual nas duas versões, então o esperado é idêntico.
  - **Lacuna possível:** se rodar a suíte isolada no 0.6.4 não for viável, registrar como lacuna, não como satisfeito.
- **K5. Prova real no SiFuture, depois de `./install.sh`.**
  - **Comando:** em `/home/renanfranca/projects/kof-sifuture`, a receita do `check` (`scripts/mutation-step.mjs`): `kof-mut run --project . --files <scope.json fora do repositório> --config kof-mut.json --report-dir <tmp fora do repositório> --run-id <uuid novo>`, uma execução por escopo:
    1. `["src/main/kof/sifuture/game/MenuEntrance.kf"]`: tem enum e teve 7 de 7 mortos no R0. **Esperado: exit 0, `complete`, `limitations: []`.** É a prova decisiva de que um arquivo com enum chega a `complete`.
    2. `["src/main/kof/sifuture/game/Item.kf", "src/main/kof/sifuture/game/Background.kf"]`: esperado `limitations: []`; com os 12 sobreviventes do R0, `complete` e exit 1, não `incomplete` e exit 3.
    3. `["src/main/kof/sifuture/game/State.kf"]`: só enums. **Esperado: exit 3, `no_mutants`, `limitations: []`.** Exit 3 aqui é correto (`report-format.md:207`) e não é regressão; o que prova a mudança é a lista vazia.
  - **Registrar:** exit, `status`, contagens, `limitations`, `kofVersion`, o novo id da imagem instalada e o commit do SiFuture. Se o SiFuture mudou desde `e6703db`, as contagens podem diferir; o critério é `limitations: []` e a coerência entre status e exit.
- **K6. Documentação e registro.**
  - Atualizar `docs/operators.md:59` e `docs/operators.pt_BR.md:59`: declarações `enum` são percorridas sem pontos de mutação; `record` continua como exemplo de sintaxe não percorrida. Conferir se `README.md`/`README.pt_BR.md` e `docs/llm-guide*.md` precisam de ajuste; se não precisarem, dizer isso no registro.
  - Criar um registro em `.agent/validation/` com RED esperado e observado, comandos, resultados de K1 a K5 e lacunas.
  - Acrescentar a entrada em "Current entry points" do `.agent/README.md`.

## Obrigações do executor

- Reconferir cada expectativa contra as fontes citadas acima, inclusive a decisão sobre anotações, **separado** de conferir se o teste a demonstra. Se uma fonte divergir, parar e avisar.
- Para cada teste novo, observar o RED antes da mudança e confirmar que ele falha pelo motivo esperado (a limitação de `EnumDeclarationNode`), não por erro de fixture.
- Registrar a evidência observada de K1 a K6, por critério: comando, resultado observado e local da asserção ou do artefato. O check verde sozinho não estabelece todos os critérios.
- Uma lacuna aberta, uma verificação que falhou ou um critério não verificado vai para o registro antes da entrega e não pode ser apresentado como satisfeito.
- Manter separados, no registro, o que foi planejado e o que foi observado.
