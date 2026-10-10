# CI e publicação

[English](ci-e-publicacao.md) | [Português (Brasil) — pt-BR](ci-e-publicacao.pt_BR.md)

**CI** é a integração contínua: verificações automáticas aplicadas a cada
alteração recebida. A publicação entrega o site aprovado pelo fluxo.

[Voltar à apresentação do projeto](../README.pt_BR.md) ·
[Desenvolvimento local](desenvolvimento.pt_BR.md) ·
[Como jogar](jogar.pt_BR.md)

Este guia concentra distribuição, verificações, construção do site e recuperação
quando uma etapa falha. O [fluxo configurado](https://github.com/renanfranca/kof-sifuture/actions/workflows/kof-ci-and-pages.yml)
permite acompanhar as execuções no GitHub.

## Revisão e artefatos

Uma **revisão** é um estado do repositório identificado por seu commit.
**SHA** é o identificador completo desse commit usado nos registros abaixo.
Um **artefato** é um conjunto de arquivos guardado por uma execução para
outra etapa consumir ou para reproduzir a entrega. Um **job** é uma etapa do
fluxo executada pelo GitHub Actions. Um **workflow** descreve esse fluxo;
as dependências entre jobs determinam
quais resultados precisam estar aprovados antes da próxima etapa.

## Checks

Um **check** é o resultado visível de uma verificação da revisão. Neste fluxo,
os testes de regras têm um check para JVM e outro para JS.

O workflow [Kof CI and GitHub Pages](../.github/workflows/kof-ci-and-pages.yml) executa em todo **PR destinado a `main`** e todo **push em `main`**, inclusive alterações apenas em documentação ou assets. Os checks **Kof tests (jvm)** e **Kof tests (js)** executam separadamente o comando completo `python3 scripts/kof_project.py test --target ALVO`. A matriz usa `fail-fast: false`: a falha de um alvo não cancela o outro e impede build e publicação. A descoberta recursiva inclui novas suítes aninhadas. Esse CI executa somente as suítes Kof; Python é o wrapper existente. Não instala nem executa testes Python, Playwright, navegadores ou Pillow.

Os testes JS usam o engine embarcado, conforme o [treinamento de alvos Kof](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/reference/targets.md#L135):

> ES Modules 2022+ via embedded GraalJS (KofJsRunner) — no Node.js

O [capítulo de testes do Learn Kof](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/23-testing.md#L42) registra:

> Each test runs **in isolation** (one failing does not interrupt the others).

Essa regra trata dos casos dentro de uma invocação Kof. A matriz do workflow preserva adicionalmente a independência entre JVM e JS. Ela não demonstra o funcionamento da interface publicada no navegador.

## Uma distribuição por resolução

[`scripts/kof_ci.sh`](../scripts/kof_ci.sh) é um helper Bash com três operações. Requer Bash, `gh` autenticado, `jq`, `curl`, `sha256sum` e `tar`.

- `resolve BUNDLE SHA`: percorre todas as páginas de releases e assets de `KofLang/Kof4j`, exclui `draft: true` e `prerelease: true` e escolhe o arquivo oficial Linux x86_64 de maior `published_at`. Um sufixo `beta` não exclui uma release elegível. Exige seu `SHA256SUMS`, exatamente uma entrada válida para o nome do arquivo, digest correto e tag resolvida até um commit, inclusive tags anotadas. Falhas e ambiguidades encerram a execução sem recorrer a outro compilador.
- `install BUNDLE DIRETORIO SHA`: valida a revisão SiFuture do manifesto, confere novamente checksum e digest, extrai em diretório novo e valida `VERSION`, `kof version` e JVM embarcada. Em Actions, grava `KOF` em `GITHUB_ENV`; localmente, retorna JSON com o caminho do launcher.
- `check-main OWNER/REPOSITORY SHA`: consulta o commit atual de `main` e retorna `fresh: true` ou `false`. Um SHA superado produz diagnóstico explícito e pula a publicação. Falha de API ou resposta inválida retorna erro; nunca autoriza deploy.

A distribuição é completa, conforme o [treinamento de instalação](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/training/distribution/install.md#L13):

> The official package contains: compiler, CLI, runtime, stdlib, tooling, editor
> support, embedded OpenJDK and documentation.

Por isso o CI instala o pacote oficial e exige a JVM embarcada, usando seu launcher por `KOF`. Não usa JAR avulso, compilação do checkout Kof ou cache de compilador. O job produtor transfere o arquivo original, `SHA256SUMS` e `manifest.json` em `kof-RUN_ID-TENTATIVA`. Testes e build baixam o nome recebido pelo output desse produtor e não consultam releases novamente.

O manifesto, logs e resumos registram versão, release e tag, commit completo Kof, ID/nome/URL do arquivo, SHA-256 verificado e SHA completo SiFuture. Todos os checkouts usam explicitamente `github.sha`; em PR, essa é a revisão de merge testada pelo evento. Os logs de cada alvo e do build ficam nos respectivos jobs e em artefatos separados, retidos por 30 dias.

## Atualização do site

O site oficial é **[Jogar SiFuture](https://renanfranca.github.io/kof-sifuture/)**.
Após cada merge em `main`, o workflow publica automaticamente a nova versão
neste mesmo endereço quando os testes, o build e a publicação terminam com
sucesso. A URL permanece a mesma; seu conteúdo é atualizado.

O merge produz um push em `main`, observado pelo workflow. O
[build](../.github/workflows/kof-ci-and-pages.yml#L94) exige testes aprovados:

```yaml
  build-pages:
    name: Build complete Pages site
    if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    needs: [resolve-kof, test]
```

`needs` faz o build esperar a distribuição e ambos os alvos de teste.
A [publicação](../.github/workflows/kof-ci-and-pages.yml#L148) depende do build:

```yaml
  deploy-pages:
    name: Publish current main
    if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    needs: build-pages
```

Antes de publicar, [check-main](../scripts/kof_ci.sh#L185) compara a revisão:

```bash
if [[ "$current" == "$tested_sha" ]]; then
    fresh=true
    printf 'Current main: %s; publication eligible\n' "$tested_sha" >&2
else
    printf 'Superseded: tested %s; current main %s; publication skipped\n' "$tested_sha" "$current" >&2
fi
```

Somente `fresh=true` autoriza o passo de deploy. Se outro commit já avançou
`main`, a execução superada pula a publicação. Portanto, um merge inicia o
fluxo, mas não promete que toda revisão intermediária substituirá o site.

Antes da primeira publicação, habilite **Settings → Pages → Source: GitHub Actions**. O workflow usa `actions/configure-pages` com `enablement: false`: Pages desabilitado faz o deploy falhar e deve ser corrigido nas configurações do repositório. O endereço oficial é [https://renanfranca.github.io/kof-sifuture/](https://renanfranca.github.io/kof-sifuture/).

Somente push em `main`, após ambos os checks aprovados, executa o build existente em diretório novo e vazio. `actions/upload-pages-artifact` recebe a raiz da saída inteira: HTML, módulos, runtimes e assets conservam os caminhos relativos. Não há uma pasta extra `kof-sifuture` dentro do pacote; o prefixo `/kof-sifuture/` pertence à URL de Pages. O [Learn Kof JS](https://github.com/KofLang/Kof4j/blob/317d9f6b1c3e27032cc955a05f859f6c627d9338/learn/37-kofjs.md#L54) descreve esse modelo:

> `kof build --target=js` generates `index.html` + modules: serve the
> folder as a static web application (any HTTP server).

Os jobs comuns têm somente `contents: read`. Apenas o deploy recebe `pages: write` e `id-token: write`, entra no ambiente `github-pages` e expõe a URL publicada. PRs não entram nesse ambiente nem produzem artefato Pages.

O deploy inteiro mantém o grupo fixo `kof-sifuture-pages`, com `cancel-in-progress: false` e `queue: max`. Dentro dele, `check-main` compara o SHA construído com o `main` atual imediatamente antes de `actions/deploy-pages`. A [documentação de concorrência](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency) explica que a fila segue a chegada à exclusividade, que pode diferir da ordem dos commits. Assim, um build antigo concluído depois ou reexecutado pula publicação. Se `main` avançar durante um deploy já iniciado, a exclusividade continua até ele terminar; a publicação nova precisa aguardar e não pode ser substituída ao final pela antiga.

## Diagnóstico, reprodução e reexecução

Consulte primeiro **Resolve verified Kof** para erros de API, seleção, tag e integridade; depois o check do alvo para instalação/testes, **Build complete Pages site** para build e artefato, e **Publish current main** para Pages/freshness/deploy. Falhas anteriores ao deploy preservam o site existente. Falhas de deploy permanecem visíveis; não são registradas como publicação bem-sucedida.

### Reproduzir uma distribuição

Para reproduzir exatamente uma distribuição selecionada, baixe o artefato `kof-...` indicado pelo job produtor, extraia seu conteúdo para um diretório e use o SHA do manifesto:

```bash
bundle=/caminho/para/bundle
sha=$(jq -r .sifuture_sha "$bundle/manifest.json")
scratch=$(mktemp -d)
installation=$(bash scripts/kof_ci.sh install "$bundle" "$scratch/installation" "$sha")
export KOF=$(jq -r .kof <<< "$installation")
python3 scripts/kof_project.py test --target jvm
python3 scripts/kof_project.py test --target js
python3 scripts/kof_project.py build --output "$scratch/site"
```

Execute esses comandos num checkout desse mesmo SHA. Alternativamente, passe `--kof "$KOF"` aos comandos existentes. Para fazer uma nova resolução local, use `bash scripts/kof_ci.sh resolve "$scratch/bundle" "$(git rev-parse HEAD)"`; o destino ainda não pode existir. A resolução local também exige acesso autenticado de leitura ao GitHub.

### Reexecutar jobs

**Re-run failed jobs** reutiliza os outputs dos produtores bem-sucedidos, inclusive o nome do bundle ou pacote Pages original; o consumidor não calcula o nome usando sua nova tentativa. **Re-run all jobs** executa uma nova resolução e repete os testes e build com ela. Se os artefatos expiraram, reexecute todos os jobs; não substitua manualmente o compilador. Reexecutar um deploy antigo não restaura um site antigo: a atualização de `main` continua sendo obrigatória.

### Verificações locais de infraestrutura

As verificações locais de infraestrutura ficam em [`tests/ci-contract.sh`](../tests/ci-contract.sh), com fixtures JSON e executáveis Bash para as APIs e downloads. Execute `bash tests/ci-contract.sh` com `yq` v4 disponível. Elas não fazem parte do workflow. O [registro de validação](../.agent/validation/kof-ci-and-pages.md) distingue simulações locais, execução real do compilador e pendências de produção.

O aceite de uma revisão publicada precisa identificar a execução, o SHA e o navegador, e verificar carregamento, módulos/runtimes, sprites, início, movimento, pausa/continuação e retorno. Automação e aceite manual devem ser registrados separadamente. Os resultados públicos já documentados estão abaixo; eles pertencem às revisões indicadas e não validam automaticamente uma publicação posterior.

## Evidência da revisão publicada

O [registro inicial do CI](../.agent/validation/kof-ci-and-pages.md) associa
os testes e a primeira publicação de 03/10/2026 ao SHA
`f812999ebbbabb1677f5b114401ab311cf04fda2`, com comparação de 34 arquivos.
Naquele registro, o aceite interativo permaneceu pendente. Essa lacuna não
apaga as provas de navegador obtidas depois em outras revisões.

O [registro do boss](../.agent/validation/boss-pages-publication.md) documenta
`81d420afe8020cdae4e4468882da7002310298e2` em 06/10/2026: 109 arquivos
comparados e Chrome 139.0.7258.154 na URL real em 320/1200 px. O combate
completo foi verificado pela fixture local, sem atribuí-lo à conferência
remota dessa publicação.

O [registro de créditos](../.agent/validation/controls-guide.md)
documenta `e649066885e3b3fd6513bebf8629c29d46f835b3` em 08/10/2026 e o
comando `python3 tests/browser.py https://renanfranca.github.io/kof-sifuture/`,
saída zero. Chrome 139.0.7258.154 verificou abertura, textos, guia e navegação
em 320/1200 px e densidades 1/2. O cenário determinístico de resultado usou
uma fixture servida localmente pelo mesmo script.

Em 09/10/2026, o [workflow 37949665153](https://github.com/renanfranca/kof-sifuture/actions/runs/37949665153)
publicou `5609febbc76cc2dd5d0f52c90349dae3ef1f5057`. O
[registro de controles](../.agent/validation/sifuture-controls.md)
conserva o resultado:

```text
PASS published Pages matches CI artifact: 113 files
```

Essa comparação verifica os bytes de HTML, módulos/runtime e assets contra o
artefato dessa execução. O registro também descreve percurso do menu público
em Chrome 155.0.8059.39, 320/1200 px: composição, fonte, posição, hover/foco,
seleção, início e pausa, inclusive sob uma cor nativa imposta no teste.
O relato manual “Resolvido” do usuário encerra a confirmação específica do
problema dos receptores do menu, sem representar um teste automatizado do Windows.

Cada evidência tem seu alcance. Testes JS do CI usam o engine embarcado;
eles não abrem um navegador. Um HTTP 200 ou uma comparação de arquivos não
prova interação. Um percurso automatizado público não substitui aprovação
visual humana ainda pendente para outra revisão ou apresentação, nem aceite
em Android físico. Os resumos versionados devem permitir entender a prova
sem os logs e capturas opcionais em `.agent/tmp/`.
