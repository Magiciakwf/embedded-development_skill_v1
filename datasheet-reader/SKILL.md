---
name: datasheet-reader
description: "Resolve device-specific register, timing, electrical, initialization and errata questions from exact-device datasheets, reference manuals and programming manuals. Use for hardware fact lookup, not broad firmware diagnosis."
---

# Datasheet Reader

Answer the concrete hardware question from applicable documentation. Reply in the user's language; preserve register names and document identifiers.

## Start from available evidence

- Inspect supplied documents and project device definitions before requesting information. Establish the exact part, peripheral instance, package and silicon revision only where they change the answer.
- Use datasheets for electrical limits/pins, reference manuals for peripherals, programming manuals for the core, and errata for affected silicon. Application examples do not establish mandatory behavior.
- For PDFs, locate the chapter via contents/bookmarks and search extracted text with layout preserved. Read the relevant section, cross-references and footnotes; inspect the page visually when extraction loses bit positions, columns, units or timing diagrams. Distinguish PDF page index from printed page number.
- Use the user's document as the starting source. If evidence is missing, locate the exact vendor document with available search tools when permitted, or identify the specific missing section. Never silently substitute a related chip. Do not invent sources or claim an errata check that was not performed.

## Resolve the question

1. State the required fact and material operating conditions. Skip a lengthy intake for a narrow question.
2. Map code/macros to the actual register and field when code is provided. A header proves a definition, not its hardware semantics.
3. Check access type, legal encodings, side effects, dependencies, order, flag-clear mechanism and affected errata. For register writes and timing calculations read [references/hardware-semantics.md](references/hardware-semantics.md).
4. Reconcile sources by applicability and revision. An applicable erratum changes normal behavior for its affected silicon; report unresolved conflicts rather than choosing silently.
5. For calculated results show source values, equation, units, actual encoded divider, rounding/error and limits. Label assumptions, documented requirements, derivations and engineering suggestions distinctly.

## Deliver

Lead with the answer or the exact unresolved fact, then the required value/sequence and constraints. Cite document ID, revision, section/table/register and page if useful, plus a local path or official URL. Omit irrelevant template fields.

Do not propose generic read-modify-write for W1C/W0C, read-to-clear, write-only or mixed-access registers. Do not infer minimum/maximum guarantees from typical or absolute-maximum ratings. When a missing fact blocks device-specific code, finish the independent analysis and ask only for the evidence that would settle it.
