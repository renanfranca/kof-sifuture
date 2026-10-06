# Bloqueios da geração do APK Android — 06/10/2026

Entrega: [issue #15 — Geração do APK Android bloqueada por RNG001 e ausência de SDK configurado](https://github.com/renanfranca/kof-sifuture/issues/15), publicada e relida após a criação.

## Snapshot e comandos

SHA do SiFuture testado: `8edf5ebbb28391b5e7de5a905513c5e9a55e5ccd`. Checkout Kof consultado: `317d9f6b1c3e27032cc955a05f859f6c627d9338`. Instalação examinada por `kof info --json`: Kof `0.5.0-beta`, compiler/runtime/stdlib `0.5.0`, Linux x86_64, Eclipse Adoptium `25.0.4.1`, JDK embutido. O SHA do checkout consultado não é presumido como metadado da distribuição instalada.

Comandos executados:

```bash
kof info --json
PYTHONDONTWRITEBYTECODE=1 python3 .agent/tmp/android-apk-blockers/probe.py
gh issue view 15 --repo renanfranca/kof-sifuture --json number,title,body,url,state,labels,assignees
```

A prova usou `prepared_sources()` do [automatizador canônico](https://github.com/renanfranca/kof-sifuture/blob/8edf5ebbb28391b5e7de5a905513c5e9a55e5ccd/scripts/kof_project.py#L49-L79). O comando de compilação foi `kof build <fontes temporárias preparadas> --target android --apk --output <saída temporária nova>`. A issue contém o reproducer completo, independente dos arquivos de evidência locais.

## Resultados

Trecho fiel da compilação no alvo Android:

```text
:0:0: warning: driver.target android without android.jar in ExternalClasspath: the host Activity was not included in the jar [AND004]
Game.kf:92:9: error: rng.seed: not available on the ANDROID target yet (RNG001) [RNG001]
Meteor.kf:22:13: error: rng.int: not available on the ANDROID target yet (RNG001) [RNG001]
EXIT: 1
APK_EXISTS: False
```

O trecho omite os demais diagnósticos. A inspeção da saída completa contabilizou `RNG001_COUNT: 17`, envolvendo Game, Meteor, Item, Subchief e Boss. O código 1 representa a falha da compilação. A busca por `*.apk` na saída temporária nova encontrou zero artefatos.

Inspeção por `os.environ.get` e `shutil.which`:

```text
ANDROID_HOME=<unset>
ANDROID_SDK_ROOT=<unset>
sdkmanager=None
adb=None
```

Não foram encontrados `~/Android/Sdk`, `/opt/android-sdk`, `/usr/lib/android-sdk` ou `/mnt/c/Users/renan/AppData/Local/Android/Sdk`. A conclusão se limita à configuração e aos locais examinados.

A issue preserva trechos e links permanentes de Game, Meteor, KofRng, ApkToolchain, teste do Kof, referência da linguagem, training, Learn Kof e README. A rejeição de rng é demonstrada pela compilação e pela condição de suporte do compilador. A exigência de SDK na etapa posterior é sustentada pela implementação do empacotador. A tentativa não alcançou essa etapa; não foi observado DEP001 nem executada a recusa por ANDROID_HOME.

Verificação após publicação:

```text
PASS published issue #15: exact title/body, OPEN, no labels or assignees
https://github.com/renanfranca/kof-sifuture/issues/15
```

O corpo retornado pelo GitHub foi comparado integralmente ao texto preparado. O reproducer foi extraído desse corpo e executado: confirmou novamente 17 erros RNG001, aviso AND004, código 1 da compilação e ausência de APK. O script de inspeção retorna zero após capturar esse código e imprimir o resultado; isso não representa sucesso do build. As cercas Markdown e a ausência de placeholders também foram verificadas. Os links fixados de Game.kf e KofRng.java foram recuperados do GitHub e correspondem aos trechos consultados localmente. O arquivo de exclusões local contém `/.agent/tmp/` exatamente uma vez.

## Lacunas e evidências

Não houve execução da aplicação em Android, instalação do SDK, aceite de licenças ou workflow de CI para APK. O teste existente do Kof foi consultado, não executado. As decisões sobre rng determinístico versus random e configuração do SDK permanecem pendentes; novas falhas podem surgir nas etapas ainda não alcançadas. Os critérios de encerramento estão na issue.

Evidências locais opcionais em `.agent/tmp/android-apk-blockers/`: `build-android.log`, `published-reproducer.log`, `summary.json`, `environment.json`, `kof-info.json`, `issue.md`, `published-issue.json` e `probe.py`. Este registro e a issue contêm os resultados essenciais sem depender desses arquivos.
