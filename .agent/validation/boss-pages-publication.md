# Publicação do boss final no GitHub Pages — 06/10/2026

[PR #14](https://github.com/renanfranca/kof-sifuture/pull/14) mesclado em `2026-10-06T15:47:31Z`. SHA publicado/testado: `81d420afe8020cdae4e4468882da7002310298e2`; head aprovado antes do merge: `b1989d082952aad16eef9e336a649630d1dbd482`.

[Workflow 37490473629](https://github.com/renanfranca/kof-sifuture/actions/runs/37490473629) terminou SUCCESS. A verificação dentro do lock confirmou o SHA atual antes da publicação:

```text
Current main: 81d420afe8020cdae4e4468882da7002310298e2; publication eligible
```

| Job | Resultado |
|---|---|
| Resolve verified Kof | [SUCCESS](https://github.com/renanfranca/kof-sifuture/actions/runs/37490473629/job/112361561878) |
| Kof tests (js) | [SUCCESS](https://github.com/renanfranca/kof-sifuture/actions/runs/37490473629/job/112362850239) |
| Kof tests (jvm) | [SUCCESS](https://github.com/renanfranca/kof-sifuture/actions/runs/37490473629/job/112362850319) |
| Build complete Pages site | [SUCCESS](https://github.com/renanfranca/kof-sifuture/actions/runs/37490473629/job/112363069801) |
| Publish current main | [SUCCESS](https://github.com/renanfranca/kof-sifuture/actions/runs/37490473629/job/112363299995) |

Ambos os jobs `Run complete Kof suite`, JVM e JS:

```text
0 failed of 103 tests
1 passed, 0 failed
```

Conferência do [site publicado](https://renanfranca.github.io/kof-sifuture/) por `python3 .agent/tmp/boss-pages/check_published.py`, exit 0. O script compara SHA-256 de todos os arquivos do artefato Pages com os bytes recebidos por HTTP, com query de revisão e cache desabilitado. Resultado:

```text
PASS all live site files match the exact deployed Pages artifact: 109 files
PASS Chrome 139.0.7258.154 live Pages at 320/1200: start, keyboard, four-arrow layout, multitouch diagonal/opposites, pause/resume, no JS or HTTP errors
```

As 109 comparações incluem HTML, todos os módulos JS e os assets do boss. Chrome `139.0.7258.154` abriu a URL real em 320/1200 px: Novo Jogo, movimento com sprites observados, quatro setas em cruz, diagonais/opostos por touch simulado, pausa com pixels congelados e retomada. Nenhum pageerror ou resposta HTTP >=400. Capturas das duas larguras foram inspecionadas.

O combate completo continua coberto pelos testes do modelo e pelo percurso com fixture registrado no [aceite do boss](stage-hud-result.md#boss-final--06102026); a conferência desta publicação não jogou a fase completa no site remoto. Android físico e comparação com vídeo histórico permanecem pendentes.

Evidências locais opcionais: `.agent/tmp/boss-pages/workflow.json`, `workflow.log`, `artifact.tar`, `published-checksums.json`, `live-check.log`, `acceptance.json` e `live-320/1200.png`. Os resultados essenciais estão acima.

Somente este registro é incluído no commit de publicação. As alterações locais anteriores em EXECPLAN.md e stage-hud-result.md foram preservadas sem inclusão. O complemento documental será acompanhado no CI/Pages; não modifica código ou assets do jogo.
