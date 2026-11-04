# Medição do M1

Este módulo mede Kof com o lexer e parser oficiais e executa PMD CPD 7.17.0 sobre os mesmos tokens. Não instala hooks, não altera fontes e não aprova dívida de design.

Requisitos: Python 3, Maven 3.9 e Java 25; distribuição oficial Kof selecionada em PATH. As dependências Maven e os plugins têm versões fixadas no `pom.xml`. O jar do Kof é uma dependência `system`, fornecida pela instalação, sem cópia para o repositório. Kof e KofMut vêm do PATH: `test` e `run` resolvem `KOF` ou o `kof` do PATH e usam o `lib/kof.jar` ao lado do launcher real (`KOF_JAR` seleciona outro jar explicitamente); `verify-kofmut` usa o `kof-mut` do PATH. O `pom.xml` não tem jar padrão: `mvn -f scripts/kof-sensors/pom.xml test` sem `-Dkof.jar=/caminho/absoluto/lib/kof.jar` falha em vez de usar outra versão em silêncio. Mudança de distribuição exige repetir as provas, não reutilizar a identidade anterior.

Na raiz do SiFuture:

```bash
scripts/kof-sensors/test
scripts/kof-sensors/run . > .agent/tmp/sensors-m1/inventory.json
scripts/kof-sensors/verify-kofmut /home/renanfranca/projects/kof-mut .agent/tmp/sensors-m1
```

`run` resolve `KOF` ou PATH, encontra `lib/kof.jar` ao lado do launcher real e registra versão, caminho e SHA-256. `KOF_JAR` permite selecionar explicitamente outro jar; a versão informada vem do launcher, enquanto caminho/hash identificam os bytes efetivamente carregados. É responsabilidade do operador selecionar um par compatível. A medição registrada neste M1 usa o par oficial da mesma instalação. O JSON sai em stdout; mensagens Maven vão para stderr. `target/` é descartável e fica ignorado pelo Git.

Argumentos: raiz do projeto, seguida opcionalmente pelos caminhos relativos explícitos de arquivos ou diretórios. O escopo padrão é `src/main/kof` e `src/test/kof`, sem limitar quantidade. Exemplo de escopo controlado:

```bash
scripts/kof-sensors/run /tmp/projeto src/main/kof/Probe.kf
```

Falha de leitura, lexer ou parser aparece em `failures` e resulta em exit 1. `expected`, inventário e `cpd.result.expected/tokenized/failures` permitem reconciliar o escopo. Findings de tamanho e clones não mudam o exit desta ferramenta de medição: exit 0 significa medição disponível. A ativação e o protocolo dos sensores pertencem aos próximos marcos. Com falhas, os números parciais não constituem calibração aprovada.

As seis definições e referências estão no plano aprovado e em [sensor-calibration.md](../../.agent/validation/sensor-calibration.md). A visita usa os records do AST oficial, sem criar uma gramática. Localizações são reconstruídas nos tokens oficiais porque alguns nodes expõem a posição do corpo ou do token seguinte. Os testes cobrem cabeçalhos de métodos em várias linhas, construtores, corpos de expressão, lambdas e funções locais. Formas novas do frontend exigem provas adicionais; este módulo não promete cobrir toda sintaxe futura.

Linhas por função incluem declaração, delimitadores e corpos aninhados, removendo linhas vazias ou somente comentários pelos tokens. Complexidade, profundidade e statements dos corpos aninhados são medidos separadamente. Um corpo de expressão possui o `return` sintético do parser, contado como um statement. Um statement vazio explícito conta; blocos delimitadores e declarações de funções locais não contam no corpo externo. Inicializador de `for` é statement no AST e conta. Cases e catches acrescentam decisões, mas não um nível extra além do switch/try; `else if` conserva o nível da cadeia. Parâmetros são os declarados, sem receiver. As únicas exceções de suítes são linhas por função e statements, reconhecidas em `src/test/kof/`; o inventário conserva seus valores.

CPD usa `CpdAnalysis` e um `CpdCapableLanguage` local; `TokenFactory.recordToken` recebe tipo, grafia original e coordenadas do lexer oficial. Não normaliza nomes nem literais, não usa `AnyCpdLexer`, não descarta arquivos iguais. Ignora espaços/comentários porque o lexer oficial não os emite. Um grupo requer ao menos 50 tokens e duas ocorrências com ao menos 5 linhas cada, incluindo grupos dentro do mesmo arquivo. O JSON registra cada ocorrência. Os testes incluem um clone real, renomeação de identificadores, sequência longa em uma linha, sequência curta em cinco linhas e falhas de tokenização/leitura. API consultada no fonte publicado de [PMD 7.17.0](https://github.com/pmd/pmd/tree/pmd_releases/7.17.0/pmd-core/src/main/java/net/sourceforge/pmd/cpd).

`verify-kofmut` usa o `kof-mut` do PATH e as fixtures do checkout KofMut indicado no primeiro argumento. Recusa checkout sujo e recusa quando os `runtimeSources` do `image.json` instalado diferem dos arquivos desse checkout: o KofMut instalado não se atualiza sozinho, só com `./install.sh` a partir de um checkout atualizado. O sumário registra caminho do `kof-mut`, id da imagem e SHA do checkout. Em seguida, copia `detected` e `survived` para temporários externos e invoca a interface real. Confere anúncio único, project-id, UUID, schema, versão, baseline, contagens, estado, exit e hashes antes/depois. Cada execução conserva seus próprios stdout/stderr, relatório e sumário com UUID; não procura o relatório mais recente. Isso qualifica a dependência com essas fixtures e não mede cobertura nem desempenho do jogo.

A referência de design e limiares permanece Katacombs `44cb39c916e9a05de561123d7b13554ee6e0a516`. No M1, nenhum guia ou implementação do Katacombs foi copiado ou modificado.

## Modo de achados (M2)

```bash
scripts/kof-sensors/run --findings . src/main/kof/sifuture/game/Meteor.kf
```

`--findings <raiz> <arquivos…>` emite JSON (`schemaVersion` 1) com `findings` (`rule`, `file`, `name`, `line`, `column` e, quando há limite, `value` e `limit`), `frontend`, `expected`, `failures` e `duplication` (CPD 50/5 com `expected`, `tokenized` e `clones`, caminhos relativos à raiz). Exit 1 quando algum arquivo não pôde ser lido, tokenizado ou analisado. O inventário de calibração (sem `--findings`) não mudou. As regras estruturais reutilizam `Analyzer` e `Calibration.exceeds` com os limites 150/25/10/4/2/17; `TestRules` e `CommentRules` leem o AST e os tokens oficiais. Comentários são achados nos intervalos entre tokens, porque o lexer não os emite. Os comandos `npm run lint:sensor`, `dup:sensor` e `sensors:debt` formatam esse JSON; veja [SENSORS.md](../../SENSORS.md). Os testes do modo estão em `FindingsTest`, com probes que passam por `kof check` JVM e JS.
