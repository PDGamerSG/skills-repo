# Reproducible search and retrieval log

Local research date: 2026-10-05, Asia/Kolkata. Tool clock at early inventory:
2026-10-04T19:18:15Z. Source files are pinned independently of changing URLs.

## Discovery searches

| Exact query | Database/tool | Decision |
|---|---|---|
| `best agent skills github anthropics skills openai skills vercel superpowers` | Web search | Discovery leads; followed original repositories |
| `github scientific skills claude K-Dense license` | Web search | Followed original K-Dense repository and inspected its root license |
| `Codex skills build plugins` with `developers.openai.com` domain restriction | Official-domain web search | Opened official skill-building documentation |

Search-result popularity claims and secondary articles were not used as quality
evidence. No exhaustive recall or search saturation is claimed.

## Opened primary sources

- https://github.com/anthropics/skills
- https://github.com/openai/skills
- https://github.com/openai/plugins
- https://github.com/obra/superpowers
- https://github.com/K-Dense-AI/claude-scientific-skills
- https://github.com/vercel-labs/agent-skills
- https://github.com/trailofbits/skills
- https://github.com/supabase/agent-skills
- https://github.com/huggingface/skills
- https://github.com/remotion-dev/skills
- https://github.com/microsoft/skills (additional lead; not tree-inventoried)
- https://agentskills.io/specification
- https://developers.openai.com/plugins/build/skills
- https://developers.openai.com/codex/skills/

Observed redirects:

- K-Dense's former `claude-scientific-skills` repository resolved to
  `K-Dense-AI/scientific-agent-skills`.
- The Codex skills documentation URL resolved to
  `https://learn.chatgpt.com/docs/build-skills`.

## Repository inspection

Fetched ten primary repositories with Git, recorded their exact HEAD commits and
commit dates, inventoried `SKILL.md` paths, and inspected README/license files.
Exact commits, folder counts, and paths: [source-inventory.json](source-inventory.json).
Selections and rationales: [selections.json](../catalog/selections.json).
Reproducible import paths: [sources.lock.json](../catalog/sources.lock.json).

Representative close reads covered Anthropic frontend-design, webapp-testing,
MCP/skill creation; Superpowers debugging and verification; K-Dense literature,
citations, critical thinking, statistics, experimental design, and visualization;
Supabase Postgres; Trail of Bits differential review, properties, and sharp edges;
Hugging Face datasets, CLI, evaluation, local models, papers, and Gradio; OpenAI
app building, Notion research, Sentry, and Cloudflare.

All 76 imports received metadata/structure parsing and dependency/action keyword
inspection. [static-review.json](static-review.json) records source URLs, section
locations, indicator line numbers, and link-check results. This automated scan
complements representative reading; it is not a comprehensive script audit.

## Retrieval failures and unresolved items

All ten Git fetches completed. No failed fetch was treated as evidence of absence.
Unresolved license evidence is explicit in the screened catalog, particularly for
Remotion, parts of OpenAI plugins, and some other skill folders. Vercel's README
declares MIT, but a complete license/copyright notice was not located in its
inspected tree. Those observations are bounded to the recorded commits.

Local inventory initially found three malformed `cardboard` frontmatters. The
snapshot was corrected to preserve malformed originals and log metadata warnings;
the original installed files were not changed. Root symlinks were also included
after the initial non-following inventory, raising local occurrences from 223 to 225.
