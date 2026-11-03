# Skill usage review — 4 November 2026

The user requested removing unused additions from this repository and explicitly chose to keep Windows-only skills until Windows usage can be verified. This cleanup affects repository imports; it does not uninstall skills from either computer.

## Evidence and limits

- Current Mac scan: 296 valid skill occurrences and 180 distinct names across user skill folders and installed plugin caches. Uninstalled marketplace source checkouts were excluded.
- Historical Mac inventory: the 5 October snapshot in [local-skills.json](local-skills.json).
- Saved Windows installation evidence: commit `895a89b`, including both published bundles and withheld records. Ignoring withheld records would incorrectly classify installed skills as absent.
- Available Mac usage history: Claude session tool calls, Codex session/command history, and T3 Code historical tool inputs. Skill catalogs injected into prompts and this maintenance conversation were excluded from usage evidence.
- Claude history contains 55 successful, deduplicated Skill invocations across 21 names, with actual invocations dated 1–31 October. The available transcript files extend through 3 November UTC. This measures agent workflow use, not necessarily explicit user naming.
- No live Windows filesystem or invocation history was accessible. The Windows snapshot proves installation, not actual use or nonuse. Windows-only bundles are therefore preserved.
- Absence from these bounded records does not prove lifetime nonuse. Raw conversations, account data, absolute source paths, and session identifiers remain outside the public repository.

## Confirmed historical workflow use

The successful Claude Skill calls include:

- Design and frontend: `impeccable`, `frontend-design`, `emil-design-eng`, `ui-ux-pro-max`.
- Development process: `brainstorming`, `systematic-debugging`, `using-git-worktrees`, `writing-plans`.
- Browser and connected work: `ego-browser`, `built-in-browser`, `google-workspace`, `neo4j-driver-python-skill`.
- Research, documents, and writing: `research`, `deep-research`, `pdf`, `prompt-master`, `unslop`.
- Other invoked helpers: `artifact-capabilities`, `cardboard`, `rescue`, `run`.

This is a confirmed-use sample, not a complete cross-platform allowlist. Some tools are environment-owned or license-restricted and cannot be bundled here. Additional direct SKILL.md reads were assessed separately; reading every file during an inventory was not treated as use.

## Removed additions

42 public imports had no observed installation in the current Mac scan or saved Mac/Windows inventories, no invocation in the available history checked, and no retained workflow handoff. They were removed as the unsupported extras from the earlier broad collection. Exact IDs, upstream links, original hashes, and decision reasons are in [curation.json](curation.json).

- Anthropic: `claude-api`, `webapp-testing`.
- Hugging Face: `hf-cli`, `huggingface-community-evals`, `huggingface-datasets`, `huggingface-gradio`, `huggingface-local-models`, `huggingface-papers`, `huggingface-trackio`.
- K-Dense: `exploratory-data-analysis`, `markitdown`, `matplotlib`, `polars`, `pptx-posters`, `research-grants`, `scientific-slides`, `scientific-visualization`, `scientific-writing`, `seaborn`, `sympy`, `uncertainty-and-units`.
- OpenAI: `agents-sdk`, `android-emulator-qa`, `build-chatgpt-app`, `chatgpt-app-submission`, `cloudflare`, `notion-knowledge-capture`, `notion-meeting-intelligence`, `notion-research-documentation`, `notion-spec-to-implementation`, `sentry`, `wrangler`.
- Supabase: `supabase`, `supabase-postgres-best-practices`.
- Trail of Bits: `audit-context-building`, `differential-review`, `modern-python`, `property-based-testing`, `semgrep`, `sharp-edges`, `supply-chain-risk-auditor`, `variant-analysis`.

The corresponding bundle directories, unreferenced per-bundle license copies, catalog entries, selected source-lock paths, and installation-profile memberships were removed together. Discovery references remain available without copying those skills. Future `vendor` runs use the reduced selections.

## Preserved

- All 88 published local bundles, including the Windows versions and the new `namecheap` skill.
- 34 remaining imported bundles, with their contents and original provenance unchanged.
- Five named research workflow handoffs: `experimental-design`, `hypothesis-generation`, `peer-review`, `statistical-analysis`, and `statsmodels`. Their preservation is dependency evidence, not a claim of direct user use.
- Private snapshots and all installed skills on disk.

The previous complete repository state is recoverable at commit `63a7fd093db45e33478cfa0c4a61074375ccb743`. The original [research report](../research/REPORT.md) remains dated historical evidence rather than a claim about current use.

## Validation

The repository unit tests, public bundle verification, and private snapshot verification passed. Retained bundles match their prior complete file manifests. Catalog, source-lock selections, profiles, screened statuses, and attribution were checked for agreement. This verifies repository integrity; it does not claim runtime compatibility for every imported skill.
