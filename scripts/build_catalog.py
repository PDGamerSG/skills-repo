#!/usr/bin/env python3
"""Generate human-readable catalogs and bounded static review evidence."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from skills_repo import ROOT, read_json, write_json


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def main():
    skills = read_json(ROOT / 'catalog/skills.json')['skills']
    local = read_json(ROOT / 'catalog/local-skills.json')
    screened = read_json(ROOT / 'catalog/screened-skills.json')
    selected = {(e['source'], e['upstream_path']) for e in skills}
    for e in screened['skills']:
        if (e['repo'], e['path']) in selected:
            e['status'] = 'vendored'
            e['decision'] = 'Selected for balanced task coverage; see catalog/skills.json for rationale.'
    write_json(ROOT / 'catalog/screened-skills.json', screened)
    lines = ['# Skill catalog', '',
             f'{len(skills)} public skill bundles. Exact provenance and all file hashes: [skills.json](skills.json).', '',
             'Browse with `python3 scripts/skills_repo.py list QUERY` from the repository root.', '',
             '| ID | Purpose | License | Upstream |', '|---|---|---|---|']
    for e in skills:
        lines.append(f'| [{cell(e["id"])}](../{e["path"]}/SKILL.md) | {cell(e["reason"])} | {e["license"]} | [pinned source]({e["url"]}) |')
    lines.extend(['', '## Recommended upstream references', '',
                  'These entries are discoverable but their contents are not redistributed here.', '',
                  '| Skill or collection | Why reference-only |', '|---|---|',
                  '| [Vercel React and composition skills](https://github.com/vercel-labs/agent-skills) | Strong frontend-specific fit. MIT is declared; the inspected tree lacks a full license/copyright notice. |',
                  '| [Remotion skills](https://github.com/remotion-dev/skills) | Useful for video work; no skill-level license file found in the inspected tree. |',
                  '| [Anthropic DOCX, PDF, PPTX, XLSX](https://github.com/anthropics/skills) | Explicit restricted terms; use authorized existing installations. |',
                  '| [OpenAI historical catalog](https://github.com/openai/skills) | Deprecated; consult current openai/plugins first. |', '',
                  'All 926 discovered upstream folders, including excluded fixtures and specialized skills: [screened-skills.json](screened-skills.json). Inventorying a folder is not an endorsement.'])
    (ROOT / 'catalog/README.md').write_text('\n'.join(lines) + '\n')
    groups = defaultdict(list)
    for e in local['skills']:
        groups[e['name']].append(e)
    lines = ['# Local skill inventory', '',
             'This catalog contains names, origin groups, bundle hashes, and preservation status. Source paths and private instructions live only under the ignored `.local/` directory.', '',
             f'{len(local["skills"])} occurrences; {len({e["id"] for e in local["skills"]})} distinct bundles; {len(groups)} distinct names.', '',
             'Cache presence means available locally, not proof of current activation or usage. Marketplace source checkouts were excluded; symlinked app-owned skills were included.', '',
             '| Skill name | Origin groups | Bundle variants | Preservation |', '|---|---|---|---|']
    for name, entries in sorted(groups.items()):
        states = ', '.join(sorted({e['status'] for e in entries}))
        if any(not e['metadata_valid'] for e in entries):
            states += '; malformed frontmatter preserved verbatim'
        lines.append(f'| {cell(name)} | {cell(", ".join(sorted({e["provider"] for e in entries})))} | {len({e["id"] for e in entries})} | {cell(states)} |')
    (ROOT / 'catalog/LOCAL_SKILLS.md').write_text('\n'.join(lines) + '\n')
    # This is structural evidence, not execution or an injection/security certification.
    evidence = []
    for e in skills:
        file = ROOT / e['path'] / 'SKILL.md'
        text = file.read_text(); rows = text.splitlines()
        headings = [{'line': i+1, 'heading': line} for i,line in enumerate(rows) if line.startswith('## ')]
        indicators = {}
        patterns = {
            'credentials': r'API[_ -]?KEY|AUTH[_ -]?TOKEN|HF_TOKEN|credentials|authentication',
            'network_or_service': r'https?://|MCP|OpenRouter|Parallel|cloud',
            'write_or_publish': r'\b(upload|publish|deploy|delete|push|send|overwrite)\b',
            'delegation': r'\b(subagent|sub-agent|agent helper|parallel agents)\b',
            'dependencies': r'\b(pip install|uv pip|npm install|npx |requires|prerequisites|dependencies)\b'
        }
        for key, pattern in patterns.items():
            indicators[key] = [i+1 for i,line in enumerate(rows) if re.search(pattern,line,re.I)]
        missing = []
        for match in re.finditer(r'\[[^\]]+\]\(([^\s)]+)\)', text):
            target = match.group(1).split('#')[0]
            if not target or re.match(r'^[a-z]+:', target) or target.startswith('/'):
                continue
            if any(x in target for x in ['<', '>', '{', '*', '$']):
                continue
            resolved = file.parent / target
            if not resolved.exists():
                missing.append({'target': target, 'line': text[:match.start()].count('\n')+1})
        evidence.append({'id':e['id'],'source':e['url'],'line_count':len(rows),'headings':headings,
                         'indicator_lines':indicators,'unresolved_relative_links':missing,
                         'prerequisites':e['prerequisites']})
    write_json(ROOT / 'research/static-review.json', {
        'scope':'All imported SKILL.md files parsed and scanned for structure, dependencies, action keywords, and relative Markdown links. Helper scripts were preserved, not executed or comprehensively security-audited.',
        'skills':evidence})
    variants = [{'name':name,'variants':len({e['id'] for e in entries}),
                 'providers':sorted({e['provider'] for e in entries})}
                for name,entries in sorted(groups.items()) if len({e['id'] for e in entries}) > 1]
    write_json(ROOT / 'research/overlaps.json', {
        'same_name_local_variants':variants,
        'public_names_already_local':sorted({e['name'] for e in skills} & set(groups)),
        'policy':'Do not overwrite local customizations. Choose one version per name for installation.'})
    print(json.dumps({'public_skills':len(skills),'public_by_source':dict(Counter(e['source'] for e in skills)),
                      'local_names':len(groups),'same_name_variants':len(variants),
                      'unresolved_link_occurrences':sum(len(e['unresolved_relative_links']) for e in evidence)},indent=2))


if __name__ == '__main__':
    main()
