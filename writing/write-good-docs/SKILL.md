---
name: write-good-docs
description: "Write and revise documentation that supports code creation and technical projects: READMEs, project guides, engineering blog posts, setup docs, agent instructions, release notes, and technical narratives. Use when the user asks for clearer docs, better README prose, less AI-sounding writing, stronger documentation structure, or a writing pass grounded in real project work."
---

# Write good docs

## Overview

Use this skill to write documentation that helps a reader understand the project, run it, change it, or learn from it.

Good docs do not perform intelligence. They reduce the reader's work.

## Workflow

1. Read the draft, repo context, source notes, and user feedback before editing.
2. State the point of the document in one plain sentence.
3. Identify the reader's job: understand the project, install it, use it, modify it, reproduce a result, or learn from a build story.
4. Cut anything that does not help that job.
5. Keep technical detail only when it explains a decision or a step the reader must repeat.
6. Use examples and links as context instead of adding explanatory filler.
7. Run `scripts/scan_ai_tells.py` on Markdown or text drafts when a file exists.
8. Do a final deletion pass: ask what can be removed without losing the point.

## Structure rules

Start with the useful thing.

For READMEs, prefer this order unless the project asks for something else:

1. What the project is.
2. Why it exists or what problem it solves.
3. What is in the repo now.
4. How to try it.
5. How to contribute or extend it, if that matters.

For technical blog posts, prefer this order:

1. The concrete situation or problem.
2. The attempt.
3. The thing that worked or failed.
4. The useful lesson.
5. The next question, only if it is real.

Do not organize by internal taxonomy unless the taxonomy helps the reader act.

## Editing standard

Keep the Zinsser standard:

- Start with the point.
- Cut filler and repeated ideas.
- Prefer verbs over noun clusters.
- Use short words unless a precise term earns its place.
- Use first person or second person when it fits the document.
- Explain technical details through choices and consequences.
- Let examples carry the lesson.
- Keep warmth. Tight writing should not become cold writing.

## Lessons from README editing

Use these lessons when improving project docs:

- Cut before polishing. A better sentence cannot save a paragraph the reader does not need.
- Delete frame sentences when the next sentence can do the work.
- Use links as context instead of explaining every background fact.
- Do not repeat material that a linked post or issue already covers.
- Trust the reader. If the point is clear, do not restate it.
- Distinguish voice from taglines. A sharp line can help, but it should not decorate every section.
- Prefer a direct sentence to a sentence with posture.
- Ask "what happens if I delete this paragraph?" before rewriting it.

## Common cuts

Cut or rewrite these patterns:

- fake-contrast sentences that create drama instead of meaning.
- corrective constructions that say the same idea twice.
- "This repo is a guide for anyone who wants to..." when the repo itself can show that.
- "The goal is simple" unless the next line truly earns it.
- long lists of future plans that do not help the reader now.
- repository layout sections when the visible tree or file names already explain the repo.
- repeated explanations of the same linked article or workflow.
- hype words listed by the scanner.

## Documentation for code work

Tie docs to the work in front of you.

Use:

- real paths
- real commands
- current limitations
- decisions the project already made
- mistakes from actual runs
- links to source material

Avoid:

- invented benefits
- roadmap padding
- generic audience claims
- setup steps that were not tested or sourced
- explaining implementation details that do not affect the reader's next action

## AI tell audit

Before delivering prose, check for:

- stock AI phrases listed by the scanner
- corrective constructions that create fake contrast
- rule-of-three padding
- title-case headings where sentence case fits better
- lists that exist because the writer wanted structure, not because the reader needed them
- sections that can be reordered without changing the document

Run the scanner:

```bash
python scripts/scan_ai_tells.py path/to/draft.md
```

The scanner flags patterns. It does not decide. Keep a finding when it is the project name, exact source language, or genuinely natural in context.

## Output

When editing docs, summarize:

- what changed in structure
- what changed in voice
- what you cut because it repeated or drifted into AI prose
- scanner findings you kept on purpose
