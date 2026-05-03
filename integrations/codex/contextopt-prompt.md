# Codex Prompt: Build CodePrism

You are working on CodePrism, a local-first repo mapping tool for AI assistants.

Start by running tests and CLI smoke commands. Then implement the next roadmap item from `docs/roadmap.md`.

Core principles: local-first, deterministic first, inspectable outputs, token savings through maps and slices, good Windows support, no exaggerated benchmark claims.

Use `codeprism prime "<task>" --changed` before broad exploration, then read the generated slice first. CodePrism appends local command events to `.codeprism/live-trace.jsonl`; `codeprism visualize --outdir .codeprism/visual` can replay that trace as a lightweight inspection layer.

Suggested first improvement: implement incremental hashing so unchanged files are not rescanned.
