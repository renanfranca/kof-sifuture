# AGENTS.md — Learning and explaining Kof

## Mandatory retrieval in every session

At the start of every agent session in this repository, read the local
[training index](/home/renanfranca/projects/kof/training/README.md). A mention
of a directory in this file does not load its contents into the agent's context.
Before **each Kof-specific decision** in advice, planning, review, explanation,
or implementation, open the relevant `training/` files. This applies even when
the answer seems familiar. Do not infer Kof syntax or idioms from Java, Kotlin,
JavaScript, or memory of an earlier session.

Use the index to find the topic; read the corresponding `training/language/`
or `training/reference/` file for a language or target question, and the
corresponding `training/idioms/` and `training/anti-patterns/` files before
choosing how to write Kof. Check `training/anti-patterns/fake-idioms.md` when
a construction may have been borrowed from another language. Read only the
files relevant to the decision, not the entire corpus. If no training file
covers the question, state that gap and continue to the other sources below;
do not invent a rule.

## Route each question to its source

The expected local source is the
[Kof4j repository](/home/renanfranca/projects/kof), also available at
`~/projects/kof/`.

1. **What is valid Kof and what does it mean?** Read the relevant page in the
   [language reference](/home/renanfranca/projects/kof/docs/language-reference/README.md),
   including its status or gaps when relevant. Use it for the language contract.
2. **How should this be expressed in Kof?** Read the topic's `training/idioms/`
   and `training/anti-patterns/` files. Use their examples and reasoning to
   choose an idiom, then check the language contract as needed.
3. **How can the user understand the concept?** Read the relevant chapter of
   [Learn Kof](/home/renanfranca/projects/kof/learn/README.md) for a gradual
   explanation and a small example. For Kof-related user-facing answers, use
   that chapter when one covers the concept; check its examples against current
   sources before treating them as supported behavior.
4. **What exists in this checkout and on this target?** Check the relevant
   implementation and tests. For a consequential or uncertain construction,
   compile or run a focused proof on the target in question. A successful
   compile alone does not prove runtime behavior or idiomatic use.
5. **What is being developed or decided?** Read the
   [development index](/home/renanfranca/projects/kof/docs/development/README.md),
   the relevant plan, and
   [DECISIONS.md](/home/renanfranca/projects/kof/docs/development/DECISIONS.md)
   when an architectural decision applies. The
   [future index](/home/renanfranca/projects/kof/docs/development/future/README.md)
   describes proposals or paused work; do not present them as implemented.

For example, a mutable class calls for the classes idiom and language reference;
`kof test` calls for `training/tooling/cli.md`, `training/examples/testing.kf`,
the testing chapter in `learn/`, and current CLI evidence;
`kof.ui` in this project calls for UI idioms, UI documentation, and proof on JS.
A proposal in `future/` requires checking whether code and tests have since
landed before claiming it works.

Prefer the English `.md` version whenever it is available. Use a localized
version such as `.pt_BR.md` only when the English document is missing or when
the task explicitly requires that translation. `training/` is mandatory for
retrieval and idiomatic guidance, but is not the final authority on whether a
capability works in the current compiler. For implementation status, follow
the precedence recorded by the corpus itself:

1. implementation;
2. tests;
3. documentation;
4. `training/`.

The language reference describes the contract; implementation and tests show
the behavior of this checkout. When they disagree, report the discrepancy
instead of turning a compiler defect into a language rule. Separate current
facts, future plans, and hypotheses.

## Explain the choice to the user

In a user-facing answer that makes a Kof decision, explain the Kof rule, why
it applies here, and the relevant source or proof. Teach the concept with a
short example when that helps the user learn it. Cite the pertinent `training/`
file and, when used, the `learn/` chapter; include implementation, test, or
target evidence for claims about current behavior. Keep this explanation
proportionate to the decision rather than listing every file read.

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
- [language reference](https://github.com/KofLang/Kof4j/tree/main/docs/language-reference)
- [learn](https://github.com/KofLang/Kof4j/tree/main/learn)
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
