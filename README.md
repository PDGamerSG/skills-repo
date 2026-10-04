# Personal Agent Skills Library

A researched collection of the skills available on this Mac, plus selected public
skills for coding, research, documents, design, data, and productivity.

Built on **5 October 2026 (Asia/Kolkata)**. The GitHub repository contains the
public imports, catalogs, research, and tooling. Private local snapshots remain
on this Mac. Existing skill installations are unchanged.

## What is included

| Collection | Coverage | Location |
|---|---|---|
| Local inventory | 225 occurrences, 138 distinct bundles across Claude, Codex, shared folders, and plugin caches | [Local catalog](catalog/LOCAL_SKILLS.md) |
| Private preservation | 133 distinct bundles, including supporting resources | `.local/archive/` (ignored by Git) |
| Restricted installed bundles | Five distinct bundles / nine occurrences, recorded as references to the original installations | `.local/inventory.json` |
| Public imports | 76 unchanged bundles from seven sources, with pinned commits and licenses | [Public catalog](catalog/README.md), `skills/` |
| Broader discovery | 926 folders inventoried across ten public repositories | [Screened catalog](catalog/screened-skills.json) |
| Research | Selection rationale, evidence, dependency limits, and overlap analysis | [Research report](research/REPORT.md) |

Local snapshots stay on this Mac. A Git clone carries the public imports and
catalogs, not `.local/`. Restricted copies were not duplicated. Local source
checkouts from uninstalled marketplace collections were not treated as skills you use.
Cloud-only skills that are absent from this Mac are outside this inventory.

## Browse and choose

The repository tools require Python 3.10+ and PyYAML. They do not execute imported
skill scripts. If PyYAML is unavailable, use an isolated environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Search public skills or your preserved local versions:

```sh
python3 scripts/skills_repo.py list debugging
python3 scripts/skills_repo.py list research
python3 scripts/skills_repo.py list --local research
```

Useful starting choices:

| Task | Recommended starting point |
|---|---|
| Debugging and implementation | `obra/systematic-debugging`, `obra/verification-before-completion` |
| Frontend work | `anthropics/frontend-design`; upstream Vercel React/composition references |
| Research and evidence appraisal | Your local `research` customization; `k-dense/literature-review`, `k-dense/scientific-critical-thinking` |
| Citation accuracy | Your local customization or `k-dense/citation-management`; choose one version |
| Data and scientific figures | `k-dense/exploratory-data-analysis`, `k-dense/scientific-visualization` |
| Documents and presentations | Existing document skills; `k-dense/markitdown`, `k-dense/scientific-slides`, `k-dense/scientific-writing` |
| Connected productivity | OpenAI's Notion skill variants, when the Notion connector is available |
| SQL and backend design | `supabase/supabase-postgres-best-practices` |
| Review and testing | `trailofbits/differential-review`, `trailofbits/property-based-testing` |

These are fit-based recommendations from source review, not a benchmark ranking.
Prerequisites and limitations are recorded per skill in `catalog/skills.json`.

## Install selected skills

Preview a copy into a staging directory:

```sh
python3 scripts/skills_repo.py install --profile balanced --dest .local/staging-skills --dry-run
python3 scripts/skills_repo.py install --profile balanced --dest .local/staging-skills
```

Profiles: `balanced`, `coding`, `research`, `documents`, `productivity`, `security`,
`data-ml`, and `superpowers-framework`. See [profiles.json](catalog/profiles.json).
Framework-wide activation and delegated workflows are confined to the opt-in
framework profile. Profiles are alternatives; combining them may duplicate names.

To install one public skill in a supported agent skill folder, for example:

```sh
python3 scripts/skills_repo.py install obra/systematic-debugging --dest ~/.claude/skills --dry-run
```

Remove `--dry-run` to copy. Existing skills are never overwritten; an existing
name stops the operation before copying starts. The inventory shows many such
collisions, so staging is the best place to compare versions first.

Preserved local bundles can also be copied by their exact ID:

```sh
python3 scripts/skills_repo.py list --local research
# Use an ID from that output:
python3 scripts/skills_repo.py install --local BUNDLE-ID --dest .local/local-staging --dry-run
```

Restricted references and malformed originals are excluded from installation.
Installed copies include provenance and attribution. Copying a skill does not
install its packages, connected MCP server, plugin hooks, account access, or
named helper agents. For ChatGPT, use its supported skill/plugin packaging and
installation flow; this repository does not claim a filesystem copy installs a
ChatGPT plugin. See [official OpenAI skill guidance](https://developers.openai.com/plugins/build/skills).

## Reproduce and maintain

```sh
python3 scripts/skills_repo.py snapshot
python3 scripts/skills_repo.py vendor
python3 scripts/build_catalog.py
python3 -m unittest discover -s tests -v
python3 scripts/skills_repo.py verify --local
```

`snapshot` inventories the configured local skill roots, follows skill-directory
symlinks, preserves full eligible bundles, and records duplicates by content hash.
It skips environment files and generated caches. It preserves malformed local
instructions verbatim and records metadata warnings rather than editing originals.

`vendor` imports exactly the reviewed paths and commits in
[sources.lock.json](catalog/sources.lock.json). It rejects changed upstream
checkouts and mismatched licenses. Updates require reviewing a new commit and
changing the lock file deliberately. No automatic pull of changing upstream code
is configured.

[Validation results](research/validation.json) cover structure, asset integrity,
license attribution, and profiles. Runtime testing of imported skills remains
separate. [Unresolved resource links](research/static-review.json) identify
upstream companion references that may require the original plugin.

## Licenses

Original repository tools and editorial documentation use the MIT license.
Imported skills retain MIT, Apache-2.0, or CC-BY-SA-4.0 terms, as applicable.
The entire collection is not relicensed as MIT. See
[third-party notices](THIRD_PARTY_NOTICES.md) and the copied upstream license files.
