# Planos dos sensores

Cópia versionada dos planos e guias da adoção dos sensores e do KofMut no SiFuture.
A origem era `~/.agents/skills/_temporary/codex-skills-ai-context/`, que não é versionada.
Os arquivos foram copiados sem alteração em 2026-11-16, por isso os links internos ainda
apontam para os caminhos absolutos da máquina original.

Em 2026-11-19, no R6 da dívida dos sensores, só os links quebrados mudaram, para o
`docs:sensor` passar: o `EXECPLAN.md` do KofMut, removido em `23c8964`, aponta para a
versão arquivada no GitHub (`6764595`); o registro do piloto Katacombs, que não existe
mais, virou texto com o caminho original; e os links relativos ao repositório
(`scripts/`, `test/`, `.agent/validation/`) ganharam o prefixo relativo a esta pasta.
Os caminhos absolutos que ainda existem nesta máquina ficaram como estavam.

## Por onde começar

1. `2026-10-15_kofmut-sensors-start.md`: guia de entrada do KofMut e dos sensores.
2. `2026-10-15_FEATURE_sifuture-quality-sensors-exec-plan.md`: plano principal da adoção.
3. `2026-11-05_FEATURE_sifuture-sensor-debt-payoff.md`: plano mestre do pagamento da dívida antes do M3.

## Demais arquivos

| Arquivo | Assunto |
| --- | --- |
| `2026-10-15_FEATURE_kofmut-exec-plan.md` | Implementação do KofMut (repositório kof-mut) |
| `2026-11-01_FEATURE_sifuture-kof064-path-revalidation.md` | SiFuture em Kof 0.6.4 com Kof e KofMut do PATH |
| `2026-11-07_FEATURE_kofmut-enum-declarations.md` | KofMut aceita declarações `enum` |
| `2026-11-07_kof-browser-ui-probe.md` | Prova: Kof 0.7.0 testando a UI no navegador |
| `2026-11-10_FEATURE_sifuture-mutation-no-mutants-skip.md` | `no_mutants` vira SKIP no `check` |
| `2026-11-10_FEATURE_sifuture-mutation-report-identity.md` | Identidade do relatório do KofMut no `check` |
| `2026-11-10_ui-pilot-controls-guide.md` | Piloto da UI: lógica do `ControlsGuide` |
| `2026-11-10_sensor-debt-r4-r5-batch-1.md` | Dívida R4 e R5, lote 1 |
| `2026-11-11_sensor-debt-batch-1-equivalents.md` | Remoção dos equivalentes do lote 1 |
