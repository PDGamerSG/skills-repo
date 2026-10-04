# Working in this repository

This is a catalog and archive of agent skills, not a request to activate every
skill it contains. Treat imported `SKILL.md` files and their scripts as source
material unless the user's task calls for a specific skill.

Keep upstream bundles unchanged. Record selections and provenance in `catalog/`.
Keep local user skill snapshots and absolute source paths under ignored `.local/`.
Only `scripts/skills_repo.py publish` writes local bundles to the tracked
`local-skills/` tree, and only open-licensed or user-owned ones.
Do not run imported helper scripts during catalog maintenance.

After changing repository tooling or catalogs, run:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/skills_repo.py verify
```

If the private snapshot is present, also run `verify --local`. Runtime compatibility
of imported skills is a separate evaluation and must not be claimed from hash checks.
