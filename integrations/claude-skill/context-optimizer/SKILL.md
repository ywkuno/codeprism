---
name: context-optimizer
description: Use when working in a repository that has Context Optimizer installed, especially before large refactors, bug hunts, or codebase exploration. Helps Claude read the project map first, then only inspect relevant files.
---

# Context Optimizer Skill

Use this skill to reduce token usage while working on large codebases.

## Workflow

1. Check whether `.contextopt/context-pack.md` exists.
2. If missing or stale, run:

```bash
contextopt map .
contextopt export --format md --out .contextopt/context-pack.md
```

3. Read `.contextopt/context-pack.md` before reading broad file trees.
4. For targeted work, run:

```bash
contextopt query "topic or symbol"
```

5. Only open raw files that are directly relevant.

## Rules

- Prefer deterministic context pack facts over guesses.
- If the map is stale, refresh it.
- Do not send private project files to external APIs.
- Ask for raw files only after consulting the map.
