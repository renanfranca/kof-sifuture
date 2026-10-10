<a id="sifuture-em-kof-créditos-navegação-e-combate"></a>

# SiFuture em Kof

## Por que trazer o SiFuture para Kof

Comecei a desenvolver o SiFuture no segundo semestre de 2006, quando estava
no quarto período do bacharelado em Ciência da Computação. No curso, havia
aprendido Portugol e estava começando a estudar Turbo Pascal. Para criar meu
jogo de nave em Java ME (J2ME), aprendi Java diretamente pela documentação
oficial da Sun. Ela foi minha única fonte para aprender a linguagem e
construir o jogo.

Foi nessa documentação que conheci a promessa **“write once, run anywhere”**:
escreva uma vez e rode em qualquer lugar. Como iniciante, imaginei que o jogo
também funcionaria em outros ambientes. Quando o terminei, em **1º de agosto
de 2007**, veio a decepção: ele rodava no celular, mas eu precisava de um
emulador no computador. Meu jogo não rodava diretamente no desktop nem na web.

A motivação está preservada no [README do projeto original, na revisão
`6f59817`](https://github.com/renanfranca/sifuture/blob/6f59817aef0f8aaf56bf7d8854d20c26e84bfc4f/README.md#L17):

> That documentation was where I discovered Java's slogan: "Write once, run anywhere".

Agora quero retomar aquela expectativa usando Kof: ampliar os ambientes em
que o SiFuture pode ser jogado, preservando suas regras e sua apresentação
reconhecível. A versão de navegador já permite jogar. Portabilidade continua
sendo um objetivo que precisa ser demonstrado em cada ambiente.

<a id="percurso-no-navegador"></a>

## Jogue no navegador

**[Jogar SiFuture](https://renanfranca.github.io/kof-sifuture/)**

Toque ou clique em **Pular créditos**, depois em **Novo Jogo**. Pelo teclado,
use Tab para obter foco, Enter para pular os créditos e uma nova pressão de
Enter para confirmar Novo Jogo. Mova a nave com as setas ou com o direcional
abaixo do jogo. A opção **Controles** no menu explica teclado, toque e especial;
o [guia de jogo](docs/jogar.md) acompanha o percurso completo.

Após cada merge em `main`, o workflow publica automaticamente a nova versão
neste mesmo endereço quando os testes, o build e a publicação terminam com
sucesso. **A URL permanece a mesma; seu conteúdo é atualizado.** Uma revisão
superada por outro avanço de `main` pula a publicação. Os detalhes estão no
[guia de CI e publicação](docs/ci-e-publicacao.md#atualização-do-site).

<a id="escopo-e-fontes"></a>

## Estado do projeto

O recorte entregue inclui créditos, menu com Novo Jogo e Controles, partida,
pausa com Continuar/Reiniciar/Menu principal, fundo, itens, evolução das armas,
meteoros, subchefe, boss final, indicadores e resultado. A v1 completa ainda
está aberta. A [especificação do port](.agent/specifications/port-sifuture-to-kof.md)
distingue essas entregas da meta:

> Full v1 remains open.

| Ambiente | Resultado demonstrado e limite |
| --- | --- |
| Navegador | Jogo publicado na URL acima. Em 09/10/2026, a revisão `5609febbc76cc2dd5d0f52c90349dae3ef1f5057` teve publicação, comparação dos 113 arquivos e percurso do menu no Chrome 155.0.8059.39 em 320/1200 px, conforme o [registro de publicação](.agent/validation/sifuture-controls.md). |
| Modelo em JVM e JS | O checkpoint `cedf4875abe101d8fd85012dbfb30ef20bf5406c` registra 114 testes por alvo e sete percursos completos no Chrome. São provas diferentes: testes do modelo não demonstram desenho ou interação gráfica em JVM. Consulte os [resultados e limites](docs/desenvolvimento.md#o-que-as-verificações-demonstram). |
| Android | Meta da v1, com execução em emulador ou aparelho. A tentativa de 06/10/2026 na revisão `8edf5ebbb28391b5e7de5a905513c5e9a55e5ccd`, usando Kof 0.5.0-beta, falhou com `RNG001`, sem gerar APK. SDK não configurado naquele ambiente; veja o [registro dos bloqueios](.agent/validation/android-apk-blockers.md). |
| JVM e Native gráficos | Alvos de pesquisa de portabilidade. A especificação não exige o port gráfico nesses alvos para aceitar a v1. Não há aceite gráfico do jogo nesses ambientes nos registros citados. |

O [registro de 09/10/2026](.agent/validation/sifuture-controls.md)
contém a prova de entrega da revisão publicada:

```text
PASS published Pages matches CI artifact: 113 files
```

Esse resultado compara arquivos. O mesmo registro descreve o percurso do menu
no Chrome; não atribui uma partida completa nessa publicação aos 113 arquivos.

<a id="aceite-dos-controles-no-chrome-do-android"></a>

Continuam pendentes Opções/Música, áudio com os MIDIs originais, pausa
automática, escala adaptável, entrada fora da árvore de controles, execução e
conforto em Android físico e comparação visual com o vídeo histórico. Toque
simulado no navegador não encerra o aceite em aparelho. O [guia de jogo](docs/jogar.md#android-e-limites-do-aceite)
explica esse limite; a [issue #4](https://github.com/renanfranca/kof-sifuture/issues/4)
acompanha necessidades restantes. Os registros de cada revisão conservam suas
próprias lacunas, inclusive aprovação visual humana quando ainda pendente.

## Documentação

Os guias públicos estão em português. Escolha o percurso que precisa:

| Quero… | Começar por… |
| --- | --- |
| Jogar e entender os comandos | [Como jogar](docs/jogar.md): abertura, menus, teclado, toque, pausa, especial e recuperação de comandos. |
| Entender o comportamento do jogo | [Regras do jogo](docs/regras-do-jogo.md): tempo, fase, pontuação, vidas, evolução, meteoros, chefes e resultado. |
| Compilar, testar ou colaborar | [Desenvolvimento](docs/desenvolvimento.md): requisitos, receitas locais, código e workaround das fontes. |
| Acompanhar checks ou recuperar uma publicação | [CI e publicação](docs/ci-e-publicacao.md): distribuição, integridade, atualização do site e diagnósticos. |

<a id="fase-e-resultado"></a>
<a id="coleta-e-evolução"></a>

As explicações de [fase e resultado](docs/regras-do-jogo.md#fase) e de
[coleta e evolução](docs/regras-do-jogo.md#coleta-e-evolução) incluem as regras,
exemplos e evidências antes concentrados aqui.

<a id="kof-instalado"></a>
<a id="compilar-a-aplicação-com-o-workaround"></a>
<a id="regras-módulos-e-testes"></a>

Para colaborar, confira [Kof instalado](docs/desenvolvimento.md#requisitos),
[compilação local](docs/desenvolvimento.md#compilar-e-abrir-a-aplicação) e
[organização e testes](docs/desenvolvimento.md#organização-do-código).
O workaround e seus diagnósticos têm uma única explicação no guia.

<a id="ci-kof-e-github-pages"></a>
<a id="uma-distribuição-por-resolução"></a>
<a id="publicação-e-atualização-de-main"></a>
<a id="diagnóstico-reprodução-e-reexecução"></a>

Para manter a entrega, consulte [checks](docs/ci-e-publicacao.md#checks),
[distribuição por resolução](docs/ci-e-publicacao.md#uma-distribuição-por-resolução),
[atualização de main](docs/ci-e-publicacao.md#atualização-do-site) e
[diagnóstico, reprodução e reexecução](docs/ci-e-publicacao.md#diagnóstico-reprodução-e-reexecução).

A [tipografia](fonts/README.md) tem documentação própria. Especificações,
[EXECPLAN.md](EXECPLAN.md) e [registros de validação](.agent/validation/)
preservam requisitos, decisões e evidências das respectivas revisões.

## Projeto original e recursos

O [SiFuture original](https://github.com/renanfranca/sifuture) preserva o jogo
em J2ME. O [vídeo histórico](https://youtu.be/1xMKYEy7Jqw?si=oF48Zq7EeNTLTb3J)
mostra sua apresentação e serve à comparação ainda pendente neste port.

O código de autoria de Renan Franca está sob a **Apache License 2.0**;
consulte [LICENSE](LICENSE) e [NOTICE](NOTICE). O NOTICE distingue esse código
das imagens e dos MIDIs de terceiros:

> Essas imagens estão excluídas da Apache License 2.0, inclusive quando
> incorporadas aos arquivos de distribuição .jar.

> Seus títulos originais, autores e licenças não foram identificados. Eles
> estão excluídos da Apache License 2.0.

O segundo trecho trata dos MIDIs. Este repositório não atribui uma licença
nova a esses recursos nem concede direitos de reutilização ou redistribuição.
