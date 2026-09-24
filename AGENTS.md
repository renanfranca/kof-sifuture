# AGENTS.md — Consulting the Kof documentation

## Primary rule

Before advising, planning, or implementing any task that depends on the Kof
language or platform, consult the relevant local documentation. Do not answer
from memory when syntax, behavior, architecture, implementation status, or
project decisions can be confirmed from the sources.

Consult only the areas related to the task; there is no need to reread the
entire documentation set for every task.

## Local documentation

The expected local source is the
[Kof4j repository](/home/renanfranca/projects/kof), also available at
`~/projects/kof/`.

- [Training](/home/renanfranca/projects/kof/training/README.md): syntax,
  semantics, examples, idiomatic practices, and anti-patterns. Use it to
  understand how to write and explain Kof in its current state.
- [Development](/home/renanfranca/projects/kof/docs/development/README.md):
  active technical work. Read the index, the plan related to the task, and
  `DECISIONS.md` when an architectural decision applies.
- [Future](/home/renanfranca/projects/kof/docs/development/future/README.md):
  future plans or paused work. Respect the classification and status described
  in the index; do not present a proposal as an implemented feature.

Also consult the [Complete Kof Course](/home/renanfranca/projects/curso-completo-de-kof/README.md)
for guided study, practical examples, exercises, and idiomatic usage related to
the task. Use its relevant modules alongside the Kof4j sources above; confirm
claims about current language behavior and implementation status against the
implementation, tests, and official documentation.

Prefer the English `.md` version whenever it is available. Use a localized
version such as `.pt_BR.md` only when the English document is missing or when
the task explicitly requires that translation. When confirming the real state
of a capability, follow the precedence recorded by the corpus itself:

1. implementation;
2. tests;
3. documentation;
4. `training/`.

When sources disagree, report the discrepancy instead of silently choosing the
most convenient source. In responses, mention the documents consulted and
clearly separate current facts, future plans, and hypotheses.

## If the local repository is unavailable

If `~/projects/kof/` is unavailable, pause the task before making claims about
Kof. Show the user the official
[KofLang/Kof4j repository](https://github.com/KofLang/Kof4j) and ask whether
they want it cloned into `~/projects/kof` so documentation can be consulted
locally.

Only run the clone after explicit authorization. The expected source and
destination are:

```bash
git clone https://github.com/KofLang/Kof4j.git ~/projects/kof
```

If the user prefers not to clone it, use the documentation from the `main`
branch on GitHub as a fallback:

- [training](https://github.com/KofLang/Kof4j/tree/main/training)
- [docs/development](https://github.com/KofLang/Kof4j/tree/main/docs/development)
- [docs/development/future](https://github.com/KofLang/Kof4j/tree/main/docs/development/future)

## Documented mental model

Use this model only as a navigation guide; the current documentation and code
remain authoritative:

```text
intent expressed in Kof
    ↓
language or platform contract
    ↓
compiler and IR
    ↓
target-specific backend/runtime
```

- The program expresses intent; the mechanism may differ across JVM, Native,
  JS, and other targets.
- A compiler recognizing or lowering an operation does not mean the capability
  conceptually belongs to the compiler. Its realization may live in the
  runtime, host, or a target-specific integration.
- Classify new capabilities in the most appropriate layer: language core,
  stdlib/platform, official package, ecosystem, or interop/FFI. Reusability
  alone is not sufficient reason to place a capability in the core or stdlib.
- Portability must be honest. When a target cannot realize a capability, find
  the documented diagnostic and gap; do not invent parity or a silent fallback.
- Do not turn interpretations of earlier conversations into Kof decisions.
  Check `DECISIONS.md` and the current plans; treat anything undecided as a
  hypothesis or a question for the user/maintainer.
