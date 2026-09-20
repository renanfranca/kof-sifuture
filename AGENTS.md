# AGENTS.md — Consulta à documentação do Kof

## Regra principal

Antes de orientar, planejar ou implementar qualquer tarefa que dependa da
linguagem ou da plataforma Kof, consulte a documentação local relevante. Não
responda por memória quando a sintaxe, o comportamento, a arquitetura, o estado
de implementação ou as decisões do projeto puderem ser confirmados nas fontes.

Consulte apenas as áreas relacionadas à tarefa; não é necessário reler toda a
documentação em cada trabalho.

## Documentação local

A fonte local esperada é o repositório
[Kof4j](/home/renanfranca/projects/kof), disponível também como
`~/projects/kof/`.

- [Training](/home/renanfranca/projects/kof/training/README.pt_BR.md): sintaxe,
  semântica, exemplos, formas idiomáticas e antipadrões. Use-o para entender
  como escrever e explicar Kof no estado atual.
- [Development](/home/renanfranca/projects/kof/docs/development/README.pt_BR.md):
  trabalho técnico em andamento. Leia o índice, o plano relacionado à tarefa e,
  quando houver decisão arquitetural, `DECISIONS.pt_BR.md`.
- [Future](/home/renanfranca/projects/kof/docs/development/future/README.pt_BR.md):
  planos futuros ou frentes pausadas. Respeite a classificação e o estado
  descritos no índice; não apresente uma proposta como funcionalidade já
  implementada.

Prefira a versão `.pt_BR.md` quando existir. Se precisar confirmar o estado real
de uma capacidade, siga esta precedência registrada pelo próprio corpus:

1. implementação;
2. testes;
3. documentação;
4. `training/`.

Quando houver divergência, informe-a em vez de escolher silenciosamente uma
fonte conveniente. Ao responder, mencione os documentos consultados e separe
claramente fato atual, plano futuro e hipótese.

## Se o repositório local não existir

Se `~/projects/kof/` não estiver disponível, pause a tarefa antes de fazer
afirmações sobre Kof. Mostre ao usuário o repositório oficial
[KofLang/Kof4j](https://github.com/KofLang/Kof4j) e pergunte se deseja cloná-lo
em `~/projects/kof` para manter as consultas locais.

Só execute o clone após autorização explícita. O destino e a origem esperados
são:

```bash
git clone https://github.com/KofLang/Kof4j.git ~/projects/kof
```

Se o usuário preferir não clonar, use como fallback a documentação da branch
`main` no GitHub:

- [training](https://github.com/KofLang/Kof4j/tree/main/training)
- [docs/development](https://github.com/KofLang/Kof4j/tree/main/docs/development)
- [docs/development/future](https://github.com/KofLang/Kof4j/tree/main/docs/development/future)

## Modelo mental documentado

Use esta visão apenas como guia de navegação; os documentos e o código atuais
continuam sendo a autoridade:

```text
intenção em Kof
    ↓
contrato da linguagem ou da plataforma
    ↓
compilador e IR
    ↓
backend/runtime específico do target
```

- O programa expressa a intenção; o mecanismo pode variar entre JVM, Native,
  JS e outros targets.
- O fato de o compilador reconhecer ou baixar uma operação não significa que a
  capacidade pertença conceitualmente ao compilador. A realização pode viver no
  runtime, no host ou em uma integração própria do target.
- Classifique novas capacidades pela camada mais adequada: core da linguagem,
  stdlib/plataforma, pacote oficial, ecossistema ou interop/FFI. Ser reutilizável
  não basta, por si só, para entrar no core ou na stdlib.
- Portabilidade deve ser honesta. Quando um target não realizar uma capacidade,
  procure o diagnóstico e o gap documentados; não invente paridade nem fallback
  silencioso.
- Não transforme interpretações de conversas anteriores em decisões do Kof.
  Verifique `DECISIONS.pt_BR.md` e os planos atuais; trate o que não estiver
  decidido como hipótese ou pergunta para o usuário/mantenedora.
