# Aceite do ciclo de fundo, coleta e armamento

Data: 03/10/2026. Revisão testada: `ab72af72471236fb336270a3b6ec8d7812dab6c4` (checkpoint de implementação). Base: `ac9bc1a65dced6d72f49fab06ad749c3fd21bb40`; branch: `background-items-weapons`. O commit posterior do registro altera apenas documentação; não altera a aplicação aceita neste SHA.

## Ambiente e método

Linux x86_64; Kof instalado `0.5.0-beta` no PATH, launcher `/home/renanfranca/.local/bin/kof`; JVM embarcada Eclipse Adoptium `25.0.4.1`; Chrome `139.0.7258.154`, Playwright e Pillow. `yq` v4.54.1 já existente em `/tmp/kof-ci-tools` foi acrescentado ao PATH do executor para o contrato de CI.

`kof info --json` identifica versão e instalação, mas não o SHA de origem do pacote local. O JAR executado tem SHA-256 `78e5ab9b65994889b8e593378aeabfbb6d5d71862e28a96f186085cabe404334`. O checkout Kof consultado está em `317d9f6b1c3e27032cc955a05f859f6c627d9338`; esse SHA identifica a consulta de código e documentação, não prova sozinho a origem do binário local. O workflow do PR registra separadamente o commit da distribuição oficial resolvida e verificada.

Execução com worker `primary`, `gpt-6.1-sol` / `medium`, no chat invocador. Implementação, avaliação das evidências, inspeção visual e revisão estrutural compartilham contexto; não são verificação independente. O executor determinístico executa e coleta; a aprovação semântica cabe ao papel Validator.

## Comandos e resultados do checkpoint

Todos os oito comandos selecionados concluíram com exit 0 e coleta completa; nenhum bloqueado. Duração total do executor: 66,43 s.

| Comando | Resultado |
| --- | --- |
| `python3 scripts/kof_project.py test --target jvm` | 47 testes, zero falhas |
| `python3 scripts/kof_project.py test --target js` | 47 testes, zero falhas |
| `python3 tests/browser.py` | Menu, Enter/Espaço, confirmação conservadora, pausa, derrota determinística, resultado e menu aprovados |
| `python3 tests/browser_controls.py` | Teclado, foco, pointer e touch existentes aprovados |
| `python3 tests/browser_meteor.py` | Movimento, três quadros de impacto e respawn aprovados |
| `python3 tests/browser_weapons.py` | Fundo, itens, armas, especial, dois contatos, pausa e layout aprovados |
| `python3 -m unittest discover -s tests -p 'test_kof_project.py'` | Oito testes, OK |
| `bash tests/ci-contract.sh` | Contrato de resolução, instalação, matriz e Pages aprovado com fixtures |

Excertos dos comandos Kof, em ambos os alvos:

```text
0 failed of 47 tests
1 passed, 0 failed
```

O primeiro número mede os casos de regras; o segundo mede o programa de suíte executado. Os alvos JVM e JS executaram as regras, não a interface gráfica. A prova gráfica abaixo ocorreu no Chrome.

Excertos de `python3 tests/browser_weapons.py`:

```text
PASS background tiling, item animation, three collection frames, lives 3 to 4 and paused redraw
PASS animated laser, blaster launch/impact and all special colors with hit/death frames
PASS key 1 and button keyboard repeat suppression, no queued attempts and native click deduplication
PASS two simultaneous contacts, each release order, touch cancellation and subsequent new press
PASS 320px/desktop layout, 72x64 button, 16px separation and retained icon during special/paused state
PASS deterministic background, collection, weapon evolution and special journey in Chrome
```

As fixtures são Kof e importam o modelo, o desenho e os controles da aplicação. Posições e eventos são controlados somente no teste. Não há API de teste acrescentada à aplicação. `browser.py` conserva o menu, entrada e pausa na aplicação normal; a derrota usa três colisões determinísticas, pois itens de vida/evolução invalidam a expectativa antiga de derrota espontânea em prazo fixo. Retorno ao menu e uma segunda partida são exercitados com os controles reais.

## Aceite visual e interações

Capturas da aplicação normal e da fixture foram inspecionadas em 320 × 800/1000 e 1200 × 800/1000 no Chrome indicado. Canvas de 176 × 220, fundo repetido sem lacunas abaixo do cabeçalho, sprites originais, pontos/vidas legíveis, ícone original e controles abaixo da cena. Especial mediu 72 × 64, alinhado ao centro vertical do direcional, com 16 pixels de separação; o centro do pad permaneceu vazio. Na aplicação normal, sem carga, o botão permanece visível e desabilitado. Na fixture evoluída, a carga habilita o botão e mantém o ícone durante disparo e pausa.

Interações automatizadas e verificadas por estado/pixels: evolução até nível três, cargas seguintes, vida 3 → 4, animações dos cinco `iten`, onze `life` indo e voltando, três efeitos de coleta, laser animado, lançamento/impacto do blaster e nove frames `e0`–`e8`. O último impacto do blaster contém alfa parcial; a comparação verifica sua composição sobre o fundo, com tolerância de um valor por canal.

Tecla 1 repetida enquanto mantida não dispara novamente depois de os feixes terminarem. Pressão recusada por falta de carga ou durante reinício não dispara depois da mudança de estado; exige soltar e pressionar. Enter/Espaço no Especial também não duplicam a tentativa por clique nativo. Com dois contatos, soltar primeiro o especial mantém o movimento; soltar primeiro o direcional interrompe o movimento sem outro consumo. Cancelar os contatos interrompe o movimento, não agenda disparo e permite uma nova pressão posteriormente. Pausa congela os pixels da cena; redesenhos repetidos não avançam quadros. Feixe superior próximo à borda não cobre o cabeçalho.

A inspeção visual foi feita sobre capturas; as interações foram executadas por Playwright/CDP, não apresentadas como uma sessão manual de toque em dispositivo físico. Os screenshots e logs são apoio local opcional em `.agent/tmp/background-items-weapons/` e `.agent/tmp/validation/20261003T202929-0osbzzpv/`. Este registro contém os resultados necessários sem depender desses arquivos.

## Revisão e fidelidade

Revisão estrutural após as suítes verdes: nenhuma correção de produção selecionada. Progressão/cargas/cadência pertencem a `Weapons`; UI consulta o modelo; entidades mutáveis atualizam no passo; frames de lançamento derivam dos contadores; prioridade de colisão é explícita e meteoro colidido não recompensa outra arma. O índice de cor é fechado pela composição de três feixes e os nove mappings têm prova por pixels. Nenhuma camada de JavaScript/CSS/DOM foi escrita para a aplicação.

Os 41 sprites adicionados são byte a byte iguais aos arquivos históricos de `sifuture/res`. O carregamento do especial corrige nomes inexistentes `especial*.png` e índices além do vetor de três posições do original para os grupos `e0`–`e2`, `e3`–`e5`, `e6`–`e8`. `NOTICE` permaneceu intacto; a cópia não altera as condições de direitos nele registradas.

## Entrega e limites

Checks de CI selecionados: Resolve verified Kof, Kof tests (jvm), Kof tests (js), em `.github/workflows/kof-ci-and-pages.yml`. Entrega: [PR #9](https://github.com/renanfranca/kof-sifuture/pull/9), pronto para revisão. A [execução 37152371521](https://github.com/renanfranca/kof-sifuture/actions/runs/37152371521) aprovou os três checks selecionados em 03/10/2026, sobre o head `69301d86d915ecc2ce15f1e30a02566fa71ba7d9` e merge de teste `1b549883c2fc388823eea63dab9c2c5e06cffa85`. Resolveu Kof `0.5.0-beta` do commit `317d9f6b1c3e27032cc955a05f859f6c627d9338`; cada alvo executou 47 testes sem falhas. Build/Publish Pages foram pulados por ser PR. Sonar, Habit e runner de mutação não são configurados neste repositório e foram excluídos; sua ausência não é aprovação. Os testes Python, de Chrome e do contrato CI foram executados localmente; o workflow executa a matriz Kof.

Este aceite fecha somente o ciclo aprovado. Chefes, música, Android, reformulação completa dos controles, eventos gerais da página, pausa automática/redimensionamento e requisitos restantes da v1 continuam abertos. Nenhum dispositivo físico/Android foi validado. Publicação Pages exige merge em main e o workflow de publicação; este ciclo não executa merge nem declara a página pública atualizada.

## Validação final e registro da entrega

A rodada final em `69301d86d915ecc2ce15f1e30a02566fa71ba7d9` repetiu os oito comandos acima: oito executados, nenhum bloqueado, exit 0 e coleta completa, em 65,94 s. JVM/JS 47/47, quatro percursos Chrome PASS, oito testes Python OK e contrato CI PASS. Os diagnósticos de parse na suíte Python pertencem ao teste intencional de fonte inválida, seguido de `Ran 8 tests` / `OK`.

Este complemento registra resultados já observados; muda somente documentação. Seu commit posterior repete as verificações locais e CI exigidas antes da entrega. O PR concentra o estado corrente desses checks e conserva os links das execuções anteriores.
