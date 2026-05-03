# GitHub Copilot Instructions

This project uses Cortext.

Before broad exploration, check `.contextopt/context-pack.md`. If it is absent or stale, suggest running:

```bash
contextopt map .
contextopt export --format md --out .contextopt/context-pack.md
```

Use the context pack as the first source for project structure, important files, and symbol locations. Verify in raw files before changing code.
