# Research and selection report

Research date: **5 October 2026, Asia/Kolkata**. Retrieval began on 4 October UTC.
Scope: the skills available on this Mac and a balanced public-source collection
for coding, research, documents, design, data, and productivity.

## Recommendation

Use this repository as a versioned library, then choose a small profile for each
workflow. The strongest starting families in this review are Superpowers for
development process, K-Dense for research/data workflows, Anthropic for design
and skill authoring, Supabase for Postgres, and the current OpenAI plugins
collection for connected productivity. Trail of Bits adds focused review and
testing workflows; Hugging Face adds ML-specific capabilities.

These are judgments about source content and task fit. They are **not measured
performance rankings**. There is no controlled experiment here showing that one
collection improves your model more than another.

The repository contains 76 selected public bundles, seven pinned upstreams, a
926-folder discovery catalog, and your local inventory. Your existing custom
research and citation skills should be compared with upstream versions before
replacement. The installer refuses to overwrite them.

## Method and coverage

1. Inventory `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`, Claude's
   installed plugin cache, and the local OpenAI plugin cache. Follow symlinked
   skill directories and compare complete resource bundles by SHA-256.
2. Use internet discovery queries to identify collections, then inspect primary
   repositories, documentation, pinned trees, README files, and license files.
   Social posts and popularity lists were discovery leads, not evidence of quality.
3. Inventory ten public repositories. Inspect representative task workflows,
   then parse all selected `SKILL.md` files and review structural/dependency
   indicators. Preserve full selected directories, not just prompts.
4. Select useful, reasonably distinct workflows with explicit redistribution
   license evidence. Keep narrower, overlapping, restricted, deprecated, or
   insufficiently documented candidates as references.
5. Verify metadata, every imported resource hash, copied license hashes, profile
   membership, local snapshot hashes, and installer behavior.

This is a **bounded curation review**, not an exhaustive or systematic review of
the entire skill ecosystem. The 926 figure counts discovered `SKILL.md` folders,
including nested workflows, examples, and fixtures. It does not mean 926 skills
were manually assessed, benchmarked, or endorsed. See the
[source inventory](source-inventory.json), [search log](SEARCH_LOG.md), and
[static evidence](static-review.json).

## Selection criteria

| Criterion | Evidence sought | Effect on the decision |
|---|---|---|
| Source accountability | Original maintainer repository; first-party documentation where relevant | Prefer an accountable source over unattributed copies |
| Recognizable task | Clear trigger and intended output | Prefer focused skills over generic role prompts |
| Workflow substance | Decision points, failure handling, references, examples, useful scripts | Prefer actionable guidance |
| Distinct contribution | Coverage missing from another selected workflow | Keep alternatives cataloged without recommending all at once |
| Maintenance | Pinned commit and inspected current upstream notices | Recognize changed/deprecated sources; commit recency alone is not quality |
| Operational fit | Stated tools, keys, accounts, packages, GPU, and sibling-skill needs | Record prerequisites and avoid pretending a prompt installs a capability |
| Redistribution evidence | Skill-level or inherited license and relevant attribution | Restricted or incomplete evidence becomes reference-only |

No star-count threshold or numerical quality score was used. Public popularity
does not establish scientific validity, secure execution, or compatibility.

## Source comparison

| Primary collection | Discovered folders | Imported | Assessment and limitation |
|---|---:|---:|---|
| [Anthropic](https://github.com/anthropics/skills) | 20 | 12 | Useful first-party design, MCP, testing, and authoring workflows; licenses vary by skill |
| [OpenAI plugins](https://github.com/openai/plugins) | 536 | 11 | Current broad collection; many workflows depend on companion MCP/plugin wiring and some lack license evidence |
| [OpenAI historical skills](https://github.com/openai/skills) | 44 | 0 | Upstream explicitly deprecated; keep as a historical discovery reference |
| [Superpowers](https://github.com/obra/superpowers) | 15 | 15 | Composable planning, debugging, review, and verification; framework activation and delegation are opt-in |
| [K-Dense](https://github.com/K-Dense-AI/scientific-agent-skills) | 177 | 21 | Broad research, data, and scientific document coverage; varying package, API, and export requirements |
| [Vercel](https://github.com/vercel-labs/agent-skills) | 9 | 0 | Strong React/component guidance; MIT is declared but full copyright/license notice was absent in this inspected tree |
| [Trail of Bits](https://github.com/trailofbits/skills) | 85 | 8 | Focused security review/testing; CC-BY-SA-4.0 and optional analyzer/agent dependencies |
| [Supabase](https://github.com/supabase/agent-skills) | 2 | 2 | Postgres schema, security, migration, query, and platform workflows; live database actions need access |
| [Hugging Face](https://github.com/huggingface/skills) | 26 | 7 | Dataset, local-model, evaluation, UI, and tracking workflows; GPU/account requirements vary |
| [Remotion](https://github.com/remotion-dev/skills) | 12 | 0 | Useful specialized video candidate; no skill-level redistribution license file found in the inspected tree |

[Microsoft's collection](https://github.com/microsoft/skills) was also opened as
an additional SDK-oriented lead. Its tree was not included in the ten-repository
inventory or the 926 count. Vendor-specific SDK breadth was outside the first
balanced selection.

### Material findings and evidence

| Claim | Supporting primary location | Interpretation / limit |
|---|---|---|
| The old OpenAI catalog points to a successor | [Pinned README opening notice](https://github.com/openai/skills/blob/49f948faa9258a0c61caceaf225e179651397431/README.md) | Observed deprecation; a historical skill can still be useful, but is not evidence of current support |
| A skill and its MCP server serve different roles | [Official OpenAI skill guidance](https://developers.openai.com/plugins/build/skills), opening section | Packaging workflow instructions does not provision authentication or live tools |
| Portability includes environment constraints | [Agent Skills specification](https://agentskills.io/specification), frontmatter and compatibility sections | Shared structure does not guarantee equivalent browser, connector, or execution tools |
| Document skills have explicit restricted terms | [Pinned Anthropic DOCX license](https://github.com/anthropics/skills/blob/8a1541c4a3ffa5a20a5a91de0dcf3f0bab1d1ef4/skills/docx/LICENSE.txt), additional restrictions | Treat these as references; other document formats must be checked separately |
| Vercel declares MIT | [Pinned Vercel README, License section](https://github.com/vercel-labs/agent-skills/blob/063bee94c3f4df8453406c830b0a7df0f2860278/README.md) | MIT declaration is observed; full copyright notice was not found, so no content was vendored in this edition |
| Trail of Bits uses share-alike terms | [Pinned root license](https://github.com/trailofbits/skills/blob/82fe8226252622fa807643bdca1710901198553a/LICENSE) | Preserve attribution and the license; do not relabel these bundles MIT |
| Research workflows have optional and task-specific dependencies | [Pinned literature-review](https://github.com/K-Dense-AI/scientific-agent-skills/blob/154988403bb5a18e9d3c0ce4e6d5e2e4b184a298/skills/literature-review/SKILL.md), compatibility/dependencies sections | Bibliographic review, API-assisted search, figures, and PDF export have different prerequisites |
| ML evaluation can need substantial local compute | [Pinned community-evals](https://github.com/huggingface/skills/blob/ca0325bb20b2d0a1b2efa893670c4c72f79e707b/skills/huggingface-community-evals/SKILL.md), prerequisites | GPU/backend checks are part of actual evaluation; imports were not benchmarked here |

## Local collection findings

| Origin | Skill occurrences |
|---|---:|
| Claude user/synced skill folder, including app symlink | 26 |
| Codex user/system skill folder | 94 |
| Shared agent skill folder, including app symlink | 2 |
| Claude installed plugin cache | 68 |
| Local OpenAI plugin cache | 35 |
| Total | 225 |

The collection has 127 distinct names and 138 distinct resource bundles.
Identical copies were deduplicated by the hash of file paths, file contents, and
executable bits. Skills with the same name but different resources remain separate
variants. Eleven names have multiple local variants; see [overlaps](overlaps.json).

133 distinct bundles were preserved under ignored `.local/archive/`, totaling
approximately 46 MB. Five restricted bundles—DOCX, PDF, PPTX, XLSX, and one
OpenAI document bundle—remain references to their existing installations.
Their nine occurrences were inventoried without making additional archive copies.
No original skills were edited or removed.

The `cardboard` skill has malformed YAML in three installed copies. Its single
deduplicated bundle was preserved verbatim and marked with a metadata warning;
it is not silently repaired or offered for installation. Zero local inventory
errors remain after preserving that malformed content.

Cache presence does not prove recent use, enabled state, or account connectivity.
Cloud-only Claude uploads, ChatGPT-only account skills, instructions stored as
ordinary chats, and custom GPT configurations were not exported. Uninstalled
Claude marketplace source collections were excluded. Environment files and
generated caches were omitted from bundle snapshots.

## Choosing between overlaps

- **Local research customizations:** retain these as the starting choice when
  their workflow reflects your existing preferences. Compare pinned upstreams
  in staging; the repository makes no claim that a newer version is better.
- **Document production:** use your authorized installed document/plugin skills
  for their original runtime. Public imports cover conversion, scientific writing,
  slides, posters, themes, and communication; they do not recreate a complete
  office suite or account integration.
- **Development process:** select the individual debugging, planning, testing,
  and review skills you need. Install the framework activation/delegation profile
  only when that overall workflow matches your agent environment.
- **Research lookup:** Hub paper discovery and workspace synthesis are useful
  complements, but do not provide exhaustive bibliographic searches.

## Verification and outstanding evidence

The repository checks validate complete bundle preservation, frontmatter names,
attribution presence and hashes, installation profile IDs, and non-overwriting
installer behavior. All imported `SKILL.md` files were scanned for dependencies,
network/service references, account-write terminology, delegation, and relative
Markdown links. That scan found no unresolved relative Markdown links in those
top-level files; it does not cover every prose path or nested resource reference.

Imported helper scripts were **not executed** and have not received a comprehensive
security audit. No connector credentials were used, no accounts were connected,
and no paid API workflows or model evaluation jobs were run. These structural
checks do not establish factual correctness, scientific validity, or end-to-end
runtime compatibility. Exact check outcomes are in [validation.json](validation.json).

The next useful quality evaluation is task-specific: choose representative prompts,
compare the local and pinned versions on the same inputs, inspect the outputs, and
record activation accuracy, factual errors, completion rate, and cost. Until then,
the recommendation remains content-based and conditional on your environment.
