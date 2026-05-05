# Codex Skills

Shared Codex skills, organized by domain.

## Structure

```text
writing/
  write-with-zinsser/
    SKILL.md
    agents/
    references/
    scripts/
```

## Skills

### Writing

- `write-with-zinsser`: Drafts, edits, and critiques prose with a clear, warm, source-faithful nonfiction standard, plus a scanner for common AI-writing tells.

## Using a Skill

Copy a skill directory into your Codex skills folder:

```bash
cp -R writing/write-with-zinsser ~/.codex/skills/write-with-zinsser
```

Then refer to it as:

```text
$write-with-zinsser
```

## Sources and Attribution

The `write-with-zinsser` skill is an original practical editing workflow influenced by:

- William Zinsser, [On Writing Well](https://www.harpercollins.com/products/on-writing-well-william-zinsser), for the emphasis on clarity, simplicity, brevity, warmth, and nonfiction craft.
- Wikipedia contributors, [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), for public guidance on common AI-writing and formatting patterns.

The skill does not include copied passages from those sources. It summarizes and operationalizes the editing principles as Codex instructions, references, and helper scripts.

## License

This repository is licensed under the Apache License 2.0. See `LICENSE`.
