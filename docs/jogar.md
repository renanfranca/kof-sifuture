# Como jogar

[Voltar à apresentação do projeto](../README.md) ·
[Regras do jogo](regras-do-jogo.md) ·
[Compilar uma versão local](desenvolvimento.md#compilar-e-abrir-a-aplicação) ·
[Atualização do site](ci-e-publicacao.md#atualização-do-site)

## Começar uma partida

**[Jogar SiFuture](https://renanfranca.github.io/kof-sifuture/)**

1. Na abertura, clique ou toque em **Pular créditos**. Também é possível tocar
   na área dos créditos ou usar Tab até um controle e pressionar Enter.
2. No menu, clique ou toque em **Novo Jogo**. Pelo teclado, solte Enter e
   pressione novamente em **Confirmar (Enter)**, com Novo Jogo selecionado.
   Cima/Baixo mudam a seleção; a nave indica a opção atual.
3. Mova a nave com as setas do teclado ou segure as setas do direcional abaixo
   do jogo. O controle usado no menu já recebe seu teclado para jogar.
4. Para pausar, pressione Enter ou ative **Pausar**. Escolha **Continuar** e
   faça uma nova pressão de direção para voltar a mover.
5. Ao terminar, **Concluir contagem** mostra a pontuação total imediatamente.
   Uma nova confirmação em **Voltar ao menu** retorna ao menu.

Os tiros normais são automáticos. Para conhecer todos os comandos antes de
jogar, abra **Controles** no menu. **Voltar** retorna com Controles selecionado;
selecione Novo Jogo para iniciar. **Mais detalhes** começa fechado, passa a
**Menos detalhes** quando aberto e fecha novamente na próxima entrada.
Abrir detalhes não inicia a partida.

Esse percurso corresponde aos rótulos do [guia dentro do jogo](../src/main/kof/sifuture/ControlsGuide.kf#L26):

```kof
listOf("Setas", "Mover a nave na partida"),
listOf("↑ / ↓", "Escolher uma opção nos menus"),
listOf("Enter", "Confirmar nos menus; pausar na partida"),
listOf("1", "Usar o especial quando disponível")))
```

Enter confirma a ação da tela atual. Soltar e pressionar novamente distingue
a intenção de abrir o menu da intenção seguinte de iniciar a partida.

## Créditos e menus

Os créditos aparecem uma vez por instância da aplicação. É possível esperar
a animação ou pulá-la. Segurar Enter pula apenas para o menu, sem iniciar uma
partida. Voltar de Controles, da pausa ou do resultado não repete os créditos.

Cima/Baixo selecionam uma opção por pressão, sem ultrapassar as extremidades.
Enter ou **Confirmar (Enter)** executam a seleção atual. Usar Tab até Confirmar
conserva a seleção; clique e Espaço também confirmam. Clique ou toque
diretamente no nome de uma opção para executá-la. As opções têm nomes
acessíveis; a nave indica a seleção e nenhum retângulo acompanha as linhas.
Já é possível selecionar ou confirmar durante a entrada animada da nave.

## Teclado e foco

**Foco** é o controle que recebe o teclado. Na abertura, adquira foco com Tab
ou clique em um controle. Ao iniciar ou retomar pelo menu, o foco permite
usar setas e **1** no botão principal ou na opção que o conserva. A área do
jogo também pode receber o teclado por clique ou Tab.

| Entrada | Ação |
| --- | --- |
| Setas na partida | Movem a nave. Duas direções de eixos diferentes formam uma diagonal. |
| Cima/Baixo nos menus | Selecionam uma opção por pressão. |
| Enter na área, no botão principal ou na opção que conserva foco | Executa a ação principal da tela uma vez por pressão. Na partida, pausa. |
| Espaço | Ativa o botão funcional focado. Em uma opção conservada fora da tela original, não confirma. |
| **1** na área, no botão principal ou na opção que conserva foco | Tenta usar o especial. |
| **1**, Enter ou Espaço no botão Especial | Tenta usar o especial. |
| Tab / Shift+Tab | Percorrem os controles em ordem / ordem inversa. |

Um contorno neutro de 1 pixel no perímetro do jogo indica foco na área ou numa
opção conservada; botões externos têm contorno próprio. A opção conservada
fora da sua tela original recebe o nome acessível **Teclado do jogo**; seu
nome volta ao retornar à tela original. Perder foco encerra essa retenção e
limpa o movimento do teclado, preservando um direcional que ainda esteja
pressionado. A perda de foco não pausa automaticamente neste recorte.

Enter precisa ter sua soltura observada em algum controle do jogo antes de
confirmar novamente. Clique e Espaço no botão principal continuam funcionando
mesmo com Enter pressionado. Os controles observam o teclado dentro da sua
árvore: isso significa o conjunto de controles do jogo e seus elementos
internos, sem captura de teclas no restante da página. WASD não é um comando.

## Toque, mouse e direções combinadas

As quatro setas ficam abaixo do jogo, em cruz, com centro e cantos vazios.
Cada botão tem 56 × 56 pixels. Mantenha direita e cima para fazer uma diagonal.
Entre direções opostas, vence a última pressionada; soltá-la retoma a outra
que ainda estiver mantida. Soltar uma seta conserva a outra; soltar a última
para o movimento.

Com o mouse, sair de uma seta encerra aquela pressão; retornar sem pressionar
não recomeça. Com toque, arrastar conserva a seta inicial até soltura ou
cancelamento: deslizar para outra seta não muda a direção neste ciclo.
O direcional fica desabilitado fora da partida.

Enquanto alguma seta do direcional está pressionada, ele tem prioridade
sobre o teclado. Depois de soltá-lo, uma seta do teclado que já estava
mantida não assume o movimento sozinha: solte e pressione novamente.
O multitouch demonstrado usa dedos em botões distintos; não cobre vários
dedos no mesmo botão.

## Pausa, reinício e retorno

| Opção na pausa | Resultado |
| --- | --- |
| **Continuar** | Mantém a partida e todos os seus contadores; requer novas pressões para mover. |
| **Reiniciar** | Recomeça com nave na posição inicial, três vidas, pontuação zero, início da fase, arma básica, zero cargas e chefes inativos. |
| **Menu principal** | Encerra a tentativa e seleciona Novo Jogo no menu. |

A pausa congela a simulação, incluindo tiros, meteoros, itens e animações.
Novo Jogo, depois de abandonar ou terminar, começa uma tentativa limpa.
Opções e Música seguem previstas para o ciclo de áudio.

## Especial

O especial lança três feixes e consome uma carga. Depois de atingir a terceira
evolução do armamento, novas coletas do item de evolução guardam cargas;
as [regras de coleta](regras-do-jogo.md#coleta-e-evolução) explicam essa progressão.

O botão **Especial** fica à direita da área de jogo, mede 56 × 220 pixels e
tem a palavra centralizada na vertical, lida de cima para baixo. Seu topo e
base acompanham o jogo, com separação de 16 pixels. Pressione-o por mouse ou
toque, ou use **1** com foco no jogo. Enter e Espaço no botão também tentam o
disparo. Dois dedos podem manter uma diagonal enquanto um terceiro tenta o
especial.

Segurar uma tecla ou o botão não repete o disparo. Uma tentativa recusada não
fica pendente: solte e pressione novamente. O especial fica indisponível sem
carga, durante outro especial, na pausa ou quando a nave não está normal.
O ícone no cabeçalho aparece enquanto houver alguma carga, inclusive durante
indisponibilidade temporária, sem mostrar a quantidade.

Existe uma retenção de foco para observar a soltura: se o botão Especial está
focado e **1**, Enter ou Espaço continuam mantidos, ele pode permanecer
habilitado para receber eventos, com opacidade `0.5` quando indisponível.
Isso não autoriza outro disparo. A última soltura ou a saída do botão reaplica
a disponibilidade imediatamente. Se os feixes terminarem antes da soltura e
ainda houver carga, o botão volta à opacidade `1`, mas outra tentativa ainda
exige soltar e pressionar.

Soltar **1**, Enter ou Espaço em qualquer controle do jogo libera o bloqueio
do especial. Soltar fora conserva-o. O [registro dessa regressão](../.agent/validation/special-key-release.md)
conserva as verificações de foco, teclas simultâneas e solturas.

## Recuperar comandos depois de sair dos controles

O jogo lembra as teclas que observou pressionadas. Se a soltura acontecer
fora dos controles, essa memória pode continuar bloqueando uma nova pressão.

| Situação | Como recuperar |
| --- | --- |
| Direita foi solta fora; retorno por clique na área | O clique rearma apenas as setas e não move por si só. A primeira nova pressão de Direita pode mover imediatamente. |
| Direita foi solta fora; retorno por Tab | Tab conserva a memória. Solte Direita dentro dos controles e pressione novamente. |
| Enter foi solto fora; retorno por clique na área | O clique conserva o bloqueio de Enter. Solte Enter dentro dos controles e pressione novamente. |
| Uma seta foi pressionada em outro controle; retorno por Tab | Solte a seta dentro dos controles antes da próxima pressão para mover. |
| O direcional foi solto enquanto uma seta do teclado estava mantida | Solte e pressione novamente a seta do teclado. |

Esses casos preservam o contrato da [especificação do recorte entregue](../.agent/specifications/port-sifuture-to-kof.md#implemented-browser-slice-issue-3):

> A pointer press on the canvas overlay clears remembered arrow presses and effective keyboard movement without ending any held pad direction.

Tradução explicativa: pressionar a área do jogo com o ponteiro limpa a memória
das setas do teclado, sem encerrar o direcional mantido. A limpeza vale para
as setas; a trava compartilhada de Enter depende da sua própria soltura.
O modelo implementa a limpeza em [Game.rearmKeyboard](../src/main/kof/sifuture/game/Game.kf#L50):

```kof
rearmKeyboard() {
    heldLeft = false
    heldRight = false
    heldUp = false
    heldDown = false
    if (!padPressed()) { ship.clearInput() }
}
```

Os quatro campos representam somente as setas. `padPressed()` impede que
limpar o teclado interrompa um direcional ainda mantido.

## Android e limites do aceite

No viewport de 320 pixels examinado, a janela ocupa 296 pixels de largura.
O jogo continua com área de 176 × 220; o conjunto com Especial mede
248 pixels, e a cruz mede 168 × 168, sem espaçamento entre as setas.

Os percursos automatizados verificaram diagonais, direções opostas, arrasto,
soltura, cancelamento, pausa e dois dedos no direcional com um terceiro no
especial. O [registro de controles](../.agent/validation/sifuture-controls.md)
distingue as revisões: o gate de `cedf4875abe101d8fd85012dbfb30ef20bf5406c`
registra sete percursos completos em Chrome 155.0.8059.39; o toque é simulado
por CDP, a interface de automação do navegador.

Conforto, alcance dos dedos e combate com subchefe em um Android físico ainda
exigem aceite manual. A [tentativa de APK](../.agent/validation/android-apk-blockers.md)
de 06/10/2026 falhou sem gerar artefato. Abrir uma largura pequena no Chrome
do computador não prova que o jogo foi instalado ou executado em Android.

Para reproduzir as verificações automatizadas, use o [guia de desenvolvimento](desenvolvimento.md#verificar-o-navegador).
O [guia de publicação](ci-e-publicacao.md#evidência-da-revisão-publicada) explica
como associar a experiência pública à revisão entregue.
