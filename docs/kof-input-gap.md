# Prova da entrada de teclado e limite de foco

## Contrato e reproducer

Kof **0.4.10-beta**, SHA **`ebd11a1af42b525c583c28ab444e060fae8a9c6a`**. [`../probes/ui-input.kf`](../probes/ui-input.kf) é um programa Kof válido e completo: monta `Canvas` com sprite e um `Input` no mesmo `Window`; registra `keydown` e `keyup` no `Input` e atualiza `Label` e `Canvas` por `time.interval(30, ...)`.

```bash
cd /home/renanfranca/projects/kof-sifuture
/home/renanfranca/projects/kof/bin/kof check probes/ui-input.kf --target js
/home/renanfranca/projects/kof/bin/kof build probes/ui-input.kf --target js --output /tmp/sifuture-probe
cp -r assets /tmp/sifuture-probe/
python3 -m http.server 8765 --directory /tmp/sifuture-probe
```

No Chrome real em Linux/WSL2, `http://127.0.0.1:8765/` mostrou sprite e contador. **Depois de clicar no campo**, `ArrowRight` produziu `pressionada: ArrowRight`; a soltura produziu `solta: ArrowRight`. O canvas continha pixels não vazios na região do sprite. A compilação e a execução observadas não apresentaram erro.

## Limite observado

Esperado para a experiência do jogo: Enter responder imediatamente após abrir a página, sem o jogador selecionar um controle. Observado: a página não atribui foco inicial ao `Input`; é necessário clicar nele (ou selecioná-lo pelo teclado) antes de receber as teclas. A UI do jogo deixa esse campo e a instrução de clique visíveis.

Composição tentada: evento no `Input`, que é um widget DOM aceito por `kof.ui`, e `Canvas` no mesmo `Column`. Essa composição funciona para pressionar e soltar teclas após foco. Na implementação inspecionada, `Canvas` não está entre os widgets que aceitam `.on(...)`, e os métodos públicos de `Input` não incluem `focus()`. A ausência de foco inicial limita a experiência, mas não impede o ciclo jogável.

O contrato documentado de `kof.ui` admite eventos nos widgets DOM e desenho no `Canvas` em KofJS. Não há neste SHA um contrato público de foco inicial automático. Portanto o achado é um **candidato a lacuna de composição/foco** para avaliação do mantenedor, não um bug afirmado de uma promessa existente nem uma proposta de API já decidida. Nenhuma alteração em Kof é solicitada por este recorte.

## Alvos e critério futuro

| Alvo | Evidência neste recorte |
| --- | --- |
| KofJS/Chrome Linux | Compilação, sprite, intervalo e `keydown`/`keyup` após foco observados; Enter sem foco inicial não respondeu. |
| Android WebView | Não testado neste ciclo; reservado à versão completa. |
| JVM/Native | `kof.ui` é documentado como sem desenho real nesses alvos; não são alvos de aceitação gráfica deste ciclo. |

Critério para resolver a limitação em um ciclo futuro: um programa Kof válido abre a cena e recebe Enter, keydown e keyup sem clique prévio, em navegador real, usando uma composição pública documentada. Qualquer decisão sobre API, camada e política por alvo pertence à manutenção de Kof conforme `D-KOF-FIRST` e `D-UI-SCOPE`.
