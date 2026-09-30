## Objetivo

Separar as fontes da aplicação e os testes de SiFuture, adotando `src/main/kof` e `src/test/kof` com `sifuture` como pacote principal, sem alterar a jogabilidade. Automatizar uma preparação temporária das fontes para que o CLI atual do Kof consiga compilar a aplicação e executar testes sobre a implementação real.

Esta issue registra a investigação que fundamenta a migração, um reproducer independente do jogo, o workaround comprovado e os critérios de aceite. A migração ainda não foi aplicada ao projeto. Modificações no próprio Kof constituem trabalho separado.

## Contexto atual e organização desejada

SiFuture é um jogo portado para Kof. O primeiro ciclo jogável já possui menu, movimento da nave, tiros, meteoros, colisões, três vidas e resultado no navegador. Para entender esta issue, basta conhecer os conceitos de pacote, import e teste de Kof.

A estrutura atual é:

~~~text
src/
├── kof.toml
├── Main.kf
├── GameView.kf
├── game/
│   ├── Game.kf
│   ├── Ship.kf
│   └── outros arquivos do modelo
└── tests/
    └── GameJourney.kf
~~~

As classes do modelo declaram `package game`. O teste importa `game.*`, utilizando os arquivos reais da aplicação. O manifesto em `src/` contém apenas:

~~~toml
[project]
name = "sifuture"
~~~

Na execução atual dos testes, esse manifesto permite descobrir `src/` como raiz dos imports. A estrutura funciona e possui 19 cenários de comportamento em JVM e JS; o problema investigado apareceu ao tentar separar as raízes da aplicação e dos testes.

A organização desejada é:

~~~text
kof.toml
src/
├── main/kof/
│   └── sifuture/
│       ├── Main.kf
│       ├── GameView.kf
│       └── game/
│           ├── Game.kf
│           ├── Ship.kf
│           └── outros arquivos do modelo
└── test/kof/
    └── sifuture/game/
        └── GameJourney.kf
~~~

`Main.kf` e `GameView.kf` declararão `package sifuture`; o modelo e a suíte de regras usarão `package sifuture.game`. As raízes `src/main/kof` e `src/test/kof` não fazem parte do nome do pacote.

**Decisão confirmada:** mover o manifesto para a raiz do projeto e preservar `name = "sifuture"`. A preparação temporária não usará esse manifesto para resolver os imports.

O layout é uma escolha de organização, não uma exigência universal da linguagem. O [capítulo de build](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/24-build-tools.md) apresenta esse layout no contexto Maven/Gradle. O [guia do CLI](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/tooling/cli.md) descreve comandos que recebem caminhos explícitos, e [D-APP.1](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/docs/development/DECISIONS.md#d-app--application-model) estabelece que o manifesto é opcional.

## Investigação: o que impediu a migração direta

### 1. Descoberta das fontes pelo build

O build coleta apenas os arquivos diretamente na pasta informada. Quando `src/main/kof` contém somente a subpasta `sifuture/`, o comando:

~~~bash
kof build src/main/kof --target js --output out
~~~

informa `no .kf/.kof files found`, retorna código zero e não gera a aplicação. Portanto, o código de saída sozinho não comprova que o build produziu um artefato.

Isso decorre da [coleta não recursiva](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-cli/src/main/java/dev/kof/cli/KofCliSupport.java#L254-L261) e do [retorno quando não há fontes](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-cli/src/main/java/dev/kof/cli/CmdBuild.java#L280-L282). É o comportamento atual da descoberta, não uma regra segundo a qual pacotes devam ficar na raiz física do projeto.

### 2. Raiz dos testes, pacotes e imports

O CLI percorre os arquivos de testes e [compila cada um individualmente usando `compileForTests`](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-cli/src/main/java/dev/kof/cli/CmdTest.java#L103-L109).

O compilador [procura um manifesto a partir da fonte; sem manifesto, deriva a raiz a partir das fontes recebidas](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/CompilerPipeline.java#L42-L51). Em seguida, [valida o pacote declarado contra o caminho relativo à raiz descoberta](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/CompilerPipeline.java#L425-L435).

Isso produz duas situações distintas:

- Com o teste em outra árvore e declarando seu pacote, a raiz descoberta pode não representar a raiz pretendida das fontes: `PKG004`.
- Ao retirar apenas a declaração de pacote de uma cópia diagnóstica do teste, o import da implementação continua sem encontrar a outra árvore: `PKG006`.

Mover o manifesto para a raiz não configura automaticamente duas raízes de fontes. Tampouco renomear o pacote para `src.main.kof.sifuture.game` atende à organização desejada.

### 3. CLI e API Java do compilador são interfaces diferentes

**CLI** significa os comandos de terminal, como `kof build` e `kof test`.

**API Java do compilador** significa métodos que ferramentas escritas em Java podem chamar. Nesta investigação, o método [`CompilerDriver.compileForTestsSources(..., moduleRoot)`](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/CompilerDriver.java#L79-L82) é declarado como `public`.

Foi encontrado um defeito separado nessa API: [a implementação recebe `moduleRoot`, mas encaminha `driver.moduleRoot`](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/kof-compiler/src/main/java/dev/kof/compiler/CompilerPipeline.java#L130-L137), conservando a raiz de uma compilação anterior.

| Chamada da API | Resultado observado em JVM e JS |
| --- | --- |
| Compilador novo, recebendo a raiz correta | Falha com `PKG006` |
| Compilador reutilizado após uma compilação com a raiz correta, recebendo uma raiz inexistente | Compila e descobre o teste |

O anexo abaixo reproduz esse defeito sem depender de SiFuture.

**Esse defeito não é apresentado como causa direta de todas as falhas do CLI:** `kof test` chama `compileForTests`, outro método. Corrigir somente `compileForTestsSources` não adicionaria ao CLI o reconhecimento de duas raízes nem resolveria toda a validação dos pacotes.

O workaround desta issue usa o CLI existente. Uma solução com suporte direto à organização desejada exigiria trabalho adicional no Kof para tratar descoberta de fontes, raízes de imports e validação dos pacotes. Uma flag como `--source-root` foi apenas uma hipótese da investigação e não é uma opção disponível no comando examinado.

### 4. Alternativas examinadas

- No [snake-ai-kof, o arquivo de testes contém cópias das funções do jogo](https://github.com/ThiagoLange/snake-ai-kof/blob/main/tests/snake_test.kof). Esse arquivo pode ser compilado sozinho, mas copiar manualmente a implementação para os testes não atende ao objetivo de testar uma única fonte da lógica.
- No [Kof-Editor, um script concatena fontes em um arquivo antes de compilar](https://github.com/KofLang/Kof-Editor/blob/main/scripts/web-combine.sh). Isso demonstrou que uma preparação das fontes pode ser uma alternativa à alteração imediata do compilador.
- Para SiFuture, a solução comprovada preserva os arquivos separados e utiliza os imports do próprio Kof. Não concatena declarações nem transforma nomes de pacotes durante a preparação.

Esses exemplos não demonstram que o layout ou o manifesto sejam obrigatórios, nem que os comandos diretos de duas árvores separadas funcionem automaticamente.

## Ambiente e evidências

Investigação realizada em 29–30/09/2026, com:

| Item | Ambiente examinado |
| --- | --- |
| Kof | `0.5.0-beta` |
| SHA do checkout Kof | `317d9f6b1c3e27032cc955a05f859f6c627d9338` |
| SHA de SiFuture | `92d085b0a61c91b5dd0062920d4b0c09b5a5837d` |
| Sistema | Linux x86_64 |
| JVM das ferramentas | Eclipse Adoptium 25.0.2 |

A distribuição executada foi preparada a partir desse checkout. Estes resultados descrevem esse snapshot; não pressupõem que outras versões mantenham todos os comportamentos.

Em cópias experimentais do jogo, com os pacotes da organização desejada:

| Verificação | Evidência observada |
| --- | --- |
| Build direto de uma raiz contendo apenas subpastas | Código zero, mensagem de ausência de fontes e nenhum artefato da aplicação |
| Testes diretamente na árvore separada | Falha na resolução do pacote/import |
| Build JS usando preparação temporária | Aplicação gerada |
| Suíte de regras usando preparação temporária | 19/19 cenários aprovados em JVM e JS |
| Navegador | Os dois testes existentes passaram no Chrome |
| Alteração de `SHIP_SPEED` de `5` para `4` na implementação da cópia experimental, seguida de nova preparação | Três cenários falharam em cada alvo |
| Restauração da velocidade e nova preparação | 19/19 aprovados novamente em JVM e JS |
| Outra suíte contendo uma falha deliberada | A suíte de 19 cenários continuou passando isoladamente; a outra suíte executou e falhou somente no próprio cenário |

Os três cenários que detectaram a alteração de velocidade foram movimento de cinco unidades e limites, precedência das teclas opostas e precedência na ordem inversa com soltura. Isso comprova que os testes executavam a implementação utilizada na preparação.

Os testes de navegador verificaram o percurso menu → partida → resultado → menu, movimento, soltura, setas opostas e sprites; o fixture de meteoros verificou posição, três quadros de impacto e reaparecimento. A preparação das fontes preservou o conteúdo dos arquivos da cópia experimental, comprovado por comparação de bytes.

## Reproducer mínimo: apenas uma soma e um teste

O exemplo não usa o jogo, sprites, `kof.ui` ou navegador. Os pré-requisitos desta parte são Bash, ferramentas usuais de arquivos e o CLI `kof` disponível no PATH.

Use um diretório vazio fora do projeto, sem `kof.toml` nos ancestrais. No ambiente examinado, `/tmp` não continha esse manifesto.

Execute:

~~~bash
kof_repro_dir=$(mktemp -d /tmp/kof-raizes-XXXXXXXX)
cd "$kof_repro_dir"
mkdir -p src/main/kof/exemplo src/test/kof/exemplo

cat > src/main/kof/exemplo/Calculo.kf <<'KF'
package exemplo

Int somar(Int a, Int b) {
    return a + b
}
KF

cat > src/main/kof/exemplo/Main.kf <<'KF'
package exemplo

import exemplo.Calculo

main() {
    println(somar(2, 3))
}
KF

cat > src/test/kof/exemplo/CalculoTest.kf <<'KF'
package exemplo

import exemplo.Calculo

test "soma usa a implementação real" {
    assert(somar(2, 3) == 5)
}
KF
~~~

`exemplo` é o pacote. `src/main/kof` e `src/test/kof` são as raízes pretendidas das fontes. O import aponta para `exemplo/Calculo.kf` relativo à raiz usada pelo compilador, não relativo à pasta do arquivo que escreve o import. Consulte [sintaxe e imports](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/language/syntax.md), [funções de Kof](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/idioms/functions.md) e [Learn Kof: pacotes e módulos](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/19-packages-and-modules.md).

### Reproduzir as falhas do CLI

Execute os comandos individualmente. Nesta parte, falhas são esperadas:

~~~bash
kof build src/main/kof --target js --output out-direto
printf 'Código do build: %s\n' "$?"

kof test src/test/kof --target jvm
printf 'Código dos testes JVM: %s\n' "$?"

kof test src/test/kof --target js
printf 'Código dos testes JS: %s\n' "$?"
~~~

Resultados:

- Build: `no .kf/.kof files found`, código `0` e ausência de `out-direto/Default.mjs`.
- Testes em ambos os alvos: código `1`, com o diagnóstico:

~~~text
package 'exemplo' does not match the directory ('') — a directory is a package [PKG004]
~~~

O resultado pretendido é compilar a aplicação e executar um teste que importe a implementação real e confirme `somar(2, 3) == 5`.

### Isolar a resolução do import

Crie uma cópia diagnóstica sem a declaração de pacote, mantendo o import e o teste:

~~~bash
mkdir -p variante
sed '/^package exemplo$/d' src/test/kof/exemplo/CalculoTest.kf > variante/CalculoTest.kf

kof test variante/CalculoTest.kf --target jvm
printf 'Código da variante JVM: %s\n' "$?"

kof test variante/CalculoTest.kf --target js
printf 'Código da variante JS: %s\n' "$?"
~~~

Ambos retornam `1` e informam que `exemplo.Calculo` não foi encontrado, com `PKG006`. Retirar o pacote não é a solução proposta; essa cópia serve somente para observar a falha do import sem a validação anterior do pacote.

### Preservar o manifesto e demonstrar o workaround

Adicione um manifesto ao exemplo, representando a decisão de mantê-lo na raiz:

~~~bash
cat > kof.toml <<'TOML'
[project]
name = "exemplo"
TOML
~~~

Esse manifesto não configura duas raízes. Na execução direta, o pacote do teste passa a ser comparado ao caminho relativo à raiz do projeto, continuando a falhar com `PKG004`.

Prepare a suíte em um diretório temporário externo:

~~~bash
(
    set -e
    preparo_teste=$(mktemp -d /tmp/kof-teste-XXXXXXXX)
    trap 'rm -rf "$preparo_teste"' EXIT

    cp -R src/main/kof/. "$preparo_teste/"
    cp src/test/kof/exemplo/CalculoTest.kf "$preparo_teste/exemplo/"
    printf '%s\n' 'import exemplo.CalculoTest' > "$preparo_teste/Entrada.kf"

    cmp src/main/kof/exemplo/Calculo.kf "$preparo_teste/exemplo/Calculo.kf"
    cmp src/test/kof/exemplo/CalculoTest.kf "$preparo_teste/exemplo/CalculoTest.kf"

    kof test "$preparo_teste/Entrada.kf" --target jvm
    kof test "$preparo_teste/Entrada.kf" --target js
)
~~~

Cada alvo apresenta:

~~~text
PASS soma usa a implementação real
0 failed of 1 tests
1 passed, 0 failed
~~~

A entrada está na raiz temporária e importa somente a suíte selecionada. Essa suíte importa `exemplo.Calculo`, alcançando a cópia idêntica da implementação. Os testes continuam sendo descobertos e executados pelo compilador e pelo runner oficiais de Kof, descritos em [Learn Kof: testes](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/23-testing.md).

A preparação do build é separada e contém somente fontes da aplicação:

~~~bash
(
    set -e
    preparo_app=$(mktemp -d /tmp/kof-app-XXXXXXXX)
    trap 'rm -rf "$preparo_app"' EXIT

    cp -R src/main/kof/. "$preparo_app/"
    printf '%s\n' 'import exemplo.*' > "$preparo_app/Entrada.kf"

    kof build "$preparo_app" --target js --output out-com-workaround
    test -f out-com-workaround/Default.mjs

    kof run "$preparo_app/Entrada.kf" --target jvm
    kof run "$preparo_app/Entrada.kf" --target js
)
~~~

O artefato JS é produzido e cada execução da aplicação imprime `5`. O manifesto permanece na raiz do exemplo e não é copiado para a preparação.

**Por que fora do projeto?** A descoberta de manifesto sobe a partir da fonte. Preparar `Entrada.kf` dentro de uma subpasta do projeto permite encontrar o `kof.toml` ancestral e escolher a raiz do projeto em vez da raiz temporária. Na prova, uma preparação interna falhou com `PKG006`, enquanto a externa passou em JVM e JS. O automatizador deverá garantir que a preparação dos testes não herde um manifesto ancestral inadequado.

## Workaround a implementar no SiFuture

**WORKAROUND de organização/build.** É uma adaptação local ao caminho atual das ferramentas, não uma regra da linguagem nem o suporte nativo a múltiplas raízes. A classificação segue [runtime-workarounds.md](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/anti-patterns/runtime-workarounds.md).

A implementação desta issue deverá:

1. Mover as fontes da aplicação para `src/main/kof/sifuture` e a suíte de regras para `src/test/kof/sifuture/game`, atualizando pacotes e imports sem mudar a lógica.
2. Mover `src/kof.toml` para a raiz, preservando `name = "sifuture"`.
3. Automatizar a cópia das fontes para diretórios temporários externos, sem alterar seu conteúdo ou nomes de pacotes durante a preparação.
4. Gerar uma entrada de build na raiz temporária com `import sifuture.*` e chamar `kof build` sobre essa preparação.
5. Para cada suíte, preparar uma árvore nova com as fontes da aplicação e somente o arquivo de teste selecionado. Gerar uma entrada como `import sifuture.game.GameJourney` e executar `kof test` sobre ela.
6. Regenerar as preparações em cada execução. Não manter cópias manuais ou fontes preparadas persistentes como outra implementação.
7. Preservar códigos de falha da preparação, compilação e testes; remover temporários também em falhas. Confirmar a existência dos artefatos esperados, pois um retorno zero sem fontes não basta.
8. Adaptar a preparação do fixture de navegador para os novos caminhos e pacotes, continuando a utilizar o modelo real. A automação Python de navegador permanece distinta das suítes Kof de regras.
9. Atualizar os comandos, caminhos, links e a explicação do manifesto no README e nos registros pertinentes do projeto.

A aplicação continuará escrita em Kof. A automação não deverá editar JavaScript/CSS gerado, concatenar declarações, remover os pacotes para fazer o teste passar ou trocar a resolução dos imports por uma implementação própria.

## Critérios de aceite

- [ ] Aplicação e suíte de regras estão nas árvores desejadas, com pacotes `sifuture` e `sifuture.game`.
- [ ] O manifesto está na raiz e conserva `name = "sifuture"`.
- [ ] Os comandos documentados de build e testes regeneram a preparação externa e chamam as ferramentas oficiais de Kof.
- [ ] Fontes preparadas são cópias idênticas das fontes canônicas; somente as pequenas entradas de compilação são geradas.
- [ ] Cada suíte executa seus próprios testes, sem incluir outras suítes por imports de pacote.
- [ ] Os 19 cenários de comportamento passam em JVM e JS após a migração.
- [ ] Uma alteração controlada da velocidade de `5` para `4` na cópia de validação provoca os três cenários esperados; restaurar e preparar novamente recupera o resultado verde.
- [ ] O build JS produz artefatos efetivos e os dois testes existentes de navegador passam com os novos caminhos.
- [ ] Menu, movimento, soltura, teclas opostas, colisões, animações, três vidas e resultado preservam o comportamento anterior.
- [ ] Falhas retornam código diferente de zero, e os temporários são removidos em sucesso e falha.
- [ ] A documentação explica o contorno e permite reproduzir o exemplo sem conhecer SiFuture.

Este recorte não implementa novos sistemas do jogo ou novos alvos gráficos. Também não altera o CLI ou a API Java de Kof. A investigação fundamenta o contorno; o suporte direto a duas raízes e a correção da API permanecem trabalhos separados no Kof.

## Anexo: reproducer da API Java do compilador

Este anexo exige conhecer Java ou querer investigar a integração com o compilador. Ele não é necessário para executar o reproducer principal em Kof.

Pré-requisitos: o mesmo `kof.jar` utilizado pela distribuição examinada, JDK 25 para executar o programa Java e Python 3 para obter o caminho da instalação informado por `kof info --json`.

Continue no diretório do exemplo:

~~~bash
mkdir -p api-root/exemplo
cp src/main/kof/exemplo/Calculo.kf api-root/exemplo/Calculo.kf

cat > api-root/Teste.kf <<'KF'
import exemplo.Calculo

test "soma" {
    assert(somar(2, 3) == 5)
}

main() {
    println(somar(2, 3))
}
KF

cat > ApiRootProbe.java <<'JAVA'
import dev.kof.compiler.*;
import java.nio.file.*;
import java.util.*;

class ApiRootProbe {
    public static void main(String[] args) throws Exception {
        Path root = Path.of(args[0]).toAbsolutePath();
        var sources = List.of(root.resolve("Teste.kf"));

        for (Target target : List.of(Target.JVM, Target.JS)) {
            CompilerDriver fresh = new CompilerDriver();
            var first = fresh.compileForTestsSources(
                sources, Files.createTempDirectory("kof-api-fresh-"), target, root);

            System.out.println(target + " novo, raiz correta: " + first.success());
            for (var d : first.diagnostics().getDiagnostics()) {
                System.out.println(d.format());
            }
            if (first.success()) {
                throw new AssertionError("O defeito não foi reproduzido no compilador novo");
            }

            CompilerDriver reused = new CompilerDriver();
            var warmup = reused.compileSources(
                sources, Files.createTempDirectory("kof-api-warmup-"), target, root);
            if (!warmup.success()) {
                throw new AssertionError(warmup.diagnostics().getDiagnostics());
            }

            var second = reused.compileForTestsSources(
                sources, Files.createTempDirectory("kof-api-reused-"),
                target, root.resolve("inexistente"));

            System.out.println(target + " reutilizado, raiz incorreta: "
                + second.success() + "; testes: " + reused.discoveredTests().size());

            if (!second.success() || reused.discoveredTests().size() != 1) {
                throw new AssertionError("O uso da raiz anterior não foi reproduzido");
            }
        }
    }
}
JAVA

kof_api_jar=$(kof info --json | python3 -c 'import json,sys; from pathlib import Path; print(Path(json.load(sys.stdin)["install"]) / "lib/kof.jar")')
java -cp "$kof_api_jar" ApiRootProbe.java "$PWD/api-root"
~~~

Resultado no snapshot investigado, com `PKG006` na primeira compilação de cada alvo:

~~~text
JVM novo, raiz correta: false
JVM reutilizado, raiz incorreta: true; testes: 1
JS novo, raiz correta: false
JS reutilizado, raiz incorreta: true; testes: 1
~~~

A primeira chamada deveria usar `api-root` para localizar `exemplo/Calculo.kf`. A segunda deveria utilizar a raiz inexistente fornecida, em vez de reaproveitar silenciosamente a raiz anterior. O programa acima verifica a compilação e a descoberta do teste; a execução do teste e o valor da soma são comprovados pelo reproducer principal com o CLI.

Uma versão que corrija esse defeito deve fazer este programa de investigação deixar de confirmar o comportamento defeituoso. Esse anexo é um reproducer da falha, não um teste que exige preservar o defeito.

Os diretórios gerados pelo anexo contêm apenas artefatos de compilação temporários; não há alterações no código de SiFuture ou no checkout Kof.

