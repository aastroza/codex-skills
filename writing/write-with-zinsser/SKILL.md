---
name: write-with-zinsser
description: "Draft, edit, and critique prose with a Zinsser-style standard: clear, warm, concrete, source-faithful, and free of common AI-writing tells. Use when writing or revising chapters, essays, posts, newsletters, documentation for nontechnical readers, technical narratives, voice-transcript drafts, AI-generated drafts, or any text where the user asks for better writing, stronger voice, less AI-sounding prose, or a style pass."
---

# Write With Zinsser

## Overview

Use this skill to make prose sound like a person who knows what they mean. Cut clutter, keep facts tied to the source, preserve the writer's voice, and scan for mechanical AI patterns before calling the work done.

## Workflow

1. Read the user's draft, source material, and project instructions before editing.
2. Identify the job: draft from notes, revise an existing draft, critique only, or audit for AI tells.
3. State the main point in one plain sentence. If the draft cannot support that point, ask for source material or narrow the claim.
4. Shape the structure around interest, story, and reader need. Do not organize by taxonomy unless taxonomy helps the reader.
5. Edit sentences for clean verbs, active voice, short paragraphs, concrete detail, and one stable voice.
6. Run an AI-tell pass with `scripts/scan_ai_tells.py` when there is a file to scan.
7. Do a final human pass. Keep the writer's surprises, opinions, hesitations, and specific observations when they are true and useful.

## Editing Standard

Keep this standard in working memory:

- Start with the point.
- Cut throat-clearing, filler, hedging, and repeated ideas.
- Prefer verbs over noun clusters.
- Use short words unless a precise term earns its place.
- Use first person or second person when it fits the piece. Do not drift between voices.
- Replace abstractions with specifics only when the source gives those specifics.
- Explain technical details through choices, trade-offs, or consequences.
- Let examples carry the lesson. Do not retell the lesson after the example already did the work.
- Keep warmth. Tight writing should not become cold writing.

Read `references/zinsser-style.md` for the full style guide, editing patterns, and before/after examples.

## AI Tell Audit

Before delivering prose, check for:

- Stock AI phrases such as "let's dive in", "game-changer", and "in today's fast-paced world".
- AI vocabulary clusters such as "delve", "intricate", "pivotal", "showcase", "underscore", "tapestry", and "vibrant".
- Corrective constructions such as "not just X, but Y" or "it is not X, it is Y".
- Em dashes, curly quotes, decorative bolding, and title-case headings.
- Inline-header lists where every bullet starts with a bold label and a colon.
- The rule of three when it pads a weak point.
- Elegant variation that avoids the plain name of the thing.
- Tables, lists, and headings that appear because the agent wanted structure, not because the reader needed it.

Read `references/ai-writing-tells.md` for the full checklist adapted from Wikipedia's signs of AI writing.

Run the scanner on markdown or text files:

```bash
python scripts/scan_ai_tells.py path/to/draft.md
```

The scanner flags patterns. It does not decide. Keep a flagged word when the word is exact, sourced, and natural in context.

## Drafting From Notes

When turning notes or transcripts into prose:

1. Treat the notes as source, not as finished structure.
2. Find the live wire: the detail, problem, or claim that makes the piece worth reading.
3. Build the draft around that interest.
4. Keep the writer's natural language where it works.
5. Remove transcript residue: repeated starts, half-thoughts, scaffolding phrases, and loops.
6. Mark unsupported claims instead of inventing proof.

For long writing projects, read `references/wiki-loop.md` and capture new taste decisions after a productive session.

## CodexBook Fit

When editing `Codex for the Rest of Us`, follow the repository instructions first. Write in English unless the file or user request says otherwise. Keep the book practical for capable beginners. Prefer concrete work, visible outputs, check steps, and honest recovery patterns over abstract claims about AI.

## Output

When editing files, summarize:

- What changed in structure.
- What changed in voice.
- Any claims you cut or marked because the source did not support them.
- Any scanner findings you kept on purpose.
