# Personal Agent Skills Library

A researched collection of the skills available on this Mac, plus selected public
skills for coding, research, documents, design, data, and productivity.

Initially built on **5 October 2026 (Asia/Kolkata)**; curated on **4 November 2026**.
The GitHub repository contains the
public imports, catalogs, research, and tooling. Private local snapshots remain
on this Mac. Existing skill installations are unchanged.

## What is included

| Collection | Coverage | Location |
|---|---|---|
| Mac inventory snapshot (5 October) | 225 occurrences, 138 distinct bundles across Claude, Codex, shared folders, and plugin caches | [Local catalog](catalog/LOCAL_SKILLS.md) |
| Private preservation | 133 distinct bundles, including supporting resources | `.local/archive/` (ignored by Git) |
| Restricted installed bundles | Five distinct bundles / nine occurrences, recorded as references to the original installations | `.local/inventory.json` |
| Public imports | 34 unchanged bundles from three sources, with pinned commits and licenses | [Public catalog](catalog/README.md), `skills/` |
| Published local skills | 88 distinct bundles: 79 with MIT or Apache-2.0 license files and 9 written by the user | [Published catalog](catalog/PUBLISHED_LOCAL.md), `local-skills/` |
| Broader discovery | 926 folders inventoried across ten public repositories | [Screened catalog](catalog/screened-skills.json) |
| Research | Selection rationale, evidence, dependency limits, and overlap analysis | [Research report](research/REPORT.md) |
| Usage-based cleanup | 42 imported extras removed after checking available Mac history and Mac/Windows installation evidence | [Usage review](catalog/USAGE_REVIEW.md), [decisions](catalog/curation.json) |

Local snapshots stay on this Mac. A Git clone carries the public imports, the
published local skills, and catalogs, not `.local/`. Restricted copies were not duplicated. Local source
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
| Documents and presentations | Existing authorized document skills; `anthropics/theme-factory` for themes |
| Review and testing | `obra/requesting-code-review`, `obra/test-driven-development` |
| Custom domain deployment | Published local `namecheap` skill |

These are fit-based recommendations from source review, not a benchmark ranking.
Prerequisites and limitations are recorded per skill in `catalog/skills.json`.

## Install selected skills

Preview a copy into a staging directory:

```sh
python3 scripts/skills_repo.py install --profile balanced --dest .local/staging-skills --dry-run
python3 scripts/skills_repo.py install --profile balanced --dest .local/staging-skills
```

Profiles: `balanced`, `coding`, `research`, `documents`, `productivity`,
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

Published local skills install the same way with `--published`:

```sh
python3 scripts/skills_repo.py list --published caveman
python3 scripts/skills_repo.py install --published BUNDLE-ID --dest .local/staging-skills --dry-run
```

Restricted references and malformed originals are excluded from installation.
Installed copies include provenance and attribution. Copying a skill does not
install its packages, connected MCP server, plugin hooks, account access, or
named helper agents. For ChatGPT, use its supported skill/plugin packaging and
installation flow; this repository does not claim a filesystem copy installs a
ChatGPT plugin. See [official OpenAI skill guidance](https://developers.openai.com/plugins/build/skills).

## Namecheap deployment skill

The personal `namecheap` skill publishes a project to Vercel, connects its
Namecheap subdomain, and checks the live release and relevant features. Invoke
`$namecheap` to be asked for a project name, or `$namecheap Agent Verse` to start
with a name. The default URL for that example is `https://agentverse.pallabdas.me`.
The actual source folder or Vercel project must be identified before deployment.

Find its current bundle and install it into your agent's skill directory:

```sh
python3 scripts/skills_repo.py list --published namecheap
python3 scripts/skills_repo.py install --published BUNDLE-ID --dest ~/.codex/skills
```

Use the ID from the list output. The published bundle includes workflow
instructions, a hostname/release verification helper, and its tests. Saved
Namecheap credentials remain in `~/.config/namecheap/credentials.env` on the
owner's machine, with owner-only access; account access is not included in GitHub.
The domain and credentials-file path can be overridden as documented in the skill.
An HTTP 200 response alone is not treated as proof that the latest changes work.

## Reproduce and maintain

```sh
python3 scripts/skills_repo.py snapshot
python3 scripts/skills_repo.py publish
python3 scripts/skills_repo.py vendor
python3 scripts/build_catalog.py
python3 -m unittest discover -s tests -v
python3 scripts/skills_repo.py verify --local
```

`snapshot` inventories the configured local skill roots, follows skill-directory
symlinks, preserves full eligible bundles, and records duplicates by content hash.
It skips environment files and generated caches. It preserves malformed local
instructions verbatim and records metadata warnings rather than editing originals.

`publish` scans the same local roots and copies a bundle into `local-skills/`
when it has an MIT, Apache-2.0, or CC-BY-SA-4.0 license file, or when a user
skill folder holds it under a name in [owned-skills.json](catalog/owned-skills.json).
It skips `.trash`, restricted licenses, unlicensed vendor bundles, malformed
frontmatter, and copies of public imports, and lists each skipped one by name in
[PUBLISHED_LOCAL.md](catalog/PUBLISHED_LOCAL.md). It replaces account UUIDs in
recorded paths with `<id>`.

Publish only one exact skill name without replacing the existing catalog:

```sh
python3 scripts/skills_repo.py publish --name namecheap
```

This preserves earlier bundles and catalog records and adds the selected skill.

`.gitattributes` turns off line-ending conversion, so a Windows checkout has the
same bytes and hashes as a Mac one. Windows does not record executable bits, so
`verify` and `install` compare only paths and file hashes there.

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
