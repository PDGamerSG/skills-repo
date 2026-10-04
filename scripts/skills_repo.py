#!/usr/bin/env python3
"""Inventory, preserve, browse, install, and verify skill bundles. Never runs them."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
SKIP_FILES = {'.DS_Store', '.env', '.env.local', '.env.production'}
SAFE_NAME = re.compile(r'^[a-z0-9][a-z0-9-]{0,63}$')
PUBLISHABLE = {'MIT', 'Apache-2.0', 'CC-BY-SA-4.0'}
# Windows has no POSIX exec bit, and Git checks out files there without one.
EXEC_BITS = os.name != 'nt'
# Roots whose skills the user may have written; plugin caches belong to their vendors.
OWNER_ROOTS = {'claude-user', 'codex-user', 'shared-agent'}
ACCOUNT_ID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_text(path, text):
    """Write UTF-8 with LF endings on every OS."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def write_json(path, value):
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def metadata(path):
    text = path.read_text(encoding='utf-8-sig')
    match = re.match(r'^---\s*\n(.*?)\n---(?:\s*\n|$)', text, re.S)
    if not match:
        raise ValueError(f'Missing frontmatter: {path}')
    result = yaml.safe_load(match.group(1))
    if not isinstance(result, dict):
        raise ValueError(f'Frontmatter is not a mapping: {path}')
    if not isinstance(result.get('name'), str) or not isinstance(result.get('description'), str):
        raise ValueError(f'Missing name/description: {path}')
    return result


def files_in(root):
    """Follow internal resource symlinks only; reject links outside a bundle."""
    base = root.resolve()
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for d in dirs:
            if (Path(directory) / d).is_symlink():
                raise ValueError(f'Directory symlink requires review: {Path(directory) / d}')
        for name in sorted(files):
            if name in SKIP_FILES or name.endswith('.pyc'):
                continue
            path = Path(directory) / name
            if not path.resolve().is_relative_to(base):
                raise ValueError(f'External resource symlink requires review: {path}')
            if path.is_file():
                yield path


def fingerprint(root):
    manifest = []
    for path in files_in(root):
        manifest.append({'path': path.relative_to(root).as_posix(),
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'executable': EXEC_BITS and bool(path.stat().st_mode & 0o111)})
    manifest.sort(key=lambda x: x['path'])
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    return digest, manifest


def content_key(manifest):
    """Hash of paths and contents only, comparable across operating systems."""
    return hashlib.sha256(json.dumps([(f['path'], f['sha256']) for f in manifest]).encode()).hexdigest()


def matches(entry, root):
    """Compare a bundle with its catalog entry; exec bits count only where the OS records them."""
    digest, manifest = fingerprint(root)
    if EXEC_BITS:
        return digest == entry['sha256'] and manifest == entry['files']
    return content_key(manifest) == content_key(entry['files'])


def copy_bundle(source, dest):
    dest.mkdir(parents=True, exist_ok=False)
    for path in files_in(source):
        target = dest / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def license_files(skill, boundary):
    result = []
    for parent in [skill, *skill.parents]:
        if not parent.is_relative_to(boundary):
            break
        result.extend(p for p in sorted(parent.glob('LICENSE*')) if p.is_file())
        if result:
            break
    return result


def license_kind(paths):
    text = '\n'.join(p.read_text(errors='replace') for p in paths)
    low = text.lower()
    if 'retain copies' in low or 'internal use only' in low or 'proprietary' in low or 'governed by your agreement' in low:
        return 'restricted'
    if 'apache license' in low and 'version 2.0' in low:
        return 'Apache-2.0'
    if ('mit license' in low or 'permission is hereby granted, free of charge' in low) and 'without restriction' in low:
        return 'MIT'
    if 'attribution-sharealike 4.0' in low:
        return 'CC-BY-SA-4.0'
    return 'unresolved'


def find_skills(root):
    """Walk skill roots, including known symlinked skill directories, without loops."""
    seen = set()
    def walk(path):
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        if (path / 'SKILL.md').is_file():
            yield path / 'SKILL.md'
        for child in sorted(path.iterdir()):
            if child.is_dir() and child.name not in SKIP_DIRS:
                yield from walk(child)
    if root.is_dir():
        yield from walk(root)


def local_roots():
    return {'claude-user': Path.home() / '.claude/skills',
            'codex-user': Path.home() / '.codex/skills',
            'shared-agent': Path.home() / '.agents/skills',
            'claude-plugin-cache': Path.home() / '.claude/plugins/cache',
            'openai-plugin-cache': Path.home() / '.codex/plugins/cache'}


def snapshot(args):
    roots = local_roots()
    if args.root:
        roots = {f'custom-{i+1}': Path(p).expanduser().resolve() for i, p in enumerate(args.root)}
    local = ROOT / '.local'
    archive = local / 'archive'
    records, public, errors, warnings = [], [], [], []
    counts = Counter()
    for label, root in roots.items():
        for path in find_skills(root):
            counts[label] += 1
            try:
                valid_metadata = True
                try:
                    meta = metadata(path)
                except (ValueError, yaml.YAMLError) as exc:
                    # Preserve a malformed installed skill verbatim; do not silently lose it.
                    raw = path.read_text(encoding='utf-8-sig')
                    name = re.search(r'^name:\s*[\"\']?([a-z0-9-]+)', raw, re.M)
                    meta = {'name': name.group(1) if name else path.parent.name}
                    valid_metadata = False
                    warnings.append({'provider': label, 'path': str(path), 'warning': str(exc)})
                licfiles = license_files(path.parent, root.resolve())
                # A symlinked app-owned skill may have a license at its real location.
                if path.parent.is_symlink():
                    licfiles = license_files(path.parent.resolve(), path.parent.resolve().parent)
                kind = license_kind(licfiles)
                digest, manifest = fingerprint(path.parent)
                slug = re.sub(r'[^a-z0-9-]', '-', meta['name'].lower()).strip('-') or 'unnamed'
                key = f'{slug}--{digest[:16]}'
                dest = archive / key
                status = 'reference-only-restricted' if kind == 'restricted' else 'private-snapshot'
                if status == 'private-snapshot' and not dest.exists():
                    copy_bundle(path.parent, dest)
                if status == 'private-snapshot':
                    copied_digest, _ = fingerprint(dest)
                    if copied_digest != digest:
                        raise ValueError(f'Snapshot differs from source: {key}')
                    for i, lic in enumerate(licfiles):
                        target = local / 'licenses' / key / f'{i}-{lic.name}'
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(lic, target)
                records.append({'id': key, 'name': meta['name'], 'provider': label,
                                'source_path': str(path.parent), 'relative_path': str(path.parent.relative_to(root)),
                                'license': kind, 'license_paths': [str(p) for p in licfiles],
                                'sha256': digest, 'files': manifest, 'status': status, 'metadata_valid': valid_metadata,
                                'archive_path': str(dest.relative_to(ROOT)) if status == 'private-snapshot' else None})
                public.append({'id': key, 'name': meta['name'], 'provider': label,
                               'license': kind, 'sha256': digest, 'status': status, 'metadata_valid': valid_metadata})
            except (ValueError, OSError, yaml.YAMLError) as exc:
                errors.append({'provider': label, 'path': str(path), 'error': str(exc)})
    now = datetime.now(timezone.utc).isoformat()
    write_json(local / 'inventory.json', {'captured_at': now, 'roots': {k: str(v) for k,v in roots.items()},
                                        'counts': dict(counts), 'skills': records, 'errors': errors, 'warnings': warnings})
    write_json(ROOT / 'catalog/local-skills.json', {'captured_at': now, 'counts': dict(counts), 'skills': public,
                                                'error_count': len(errors), 'metadata_warning_count': len(warnings)})
    print(json.dumps({'occurrences': len(records), 'unique_bundles': len({r['id'] for r in records}),
                      'private_snapshots': len({r['id'] for r in records if r['archive_path']}),
                      'restricted_references': sum(r['status'].startswith('reference') for r in records),
                      'counts': dict(counts), 'errors': errors, 'metadata_warnings': len(warnings)}, indent=2))
    return 1 if errors else 0


def publish(args):
    """Copy redistributable local bundles into local-skills/ and record what stays private."""
    owned = set(read_json(ROOT / 'catalog/owned-skills.json')['names'])
    vendored = {content_key(e['files']): e['id'] for e in read_json(ROOT / 'catalog/skills.json')['skills']}
    published, withheld, errors = {}, [], []
    for label, root in local_roots().items():
        for path in find_skills(root):
            rel = path.parent.relative_to(root)
            if '.trash' in rel.parts:
                continue
            # Account UUIDs in synced paths identify the user, not the skill.
            origin = {'provider': label, 'path': ACCOUNT_ID.sub('<id>', rel.as_posix())}
            try:
                try:
                    name, valid = metadata(path)['name'], True
                except (ValueError, yaml.YAMLError):
                    name, valid = path.parent.name, False
                licfiles = license_files(path.parent, root.resolve())
                kind = license_kind(licfiles)
                digest, manifest = fingerprint(path.parent)
                slug = re.sub(r'[^a-z0-9-]', '-', name.lower()).strip('-') or 'unnamed'
                key = f'{slug}--{digest[:16]}'
                owner = name in owned and label in OWNER_ROOTS
                same = vendored.get(content_key(manifest))
                if same:
                    reason = f'Same content as public import {same}'
                elif kind == 'restricted':
                    reason = 'Restricted license'
                elif not valid:
                    reason = 'Malformed frontmatter'
                elif kind not in PUBLISHABLE and not owner:
                    reason = 'No license file; vendor-owned'
                else:
                    reason = None
                if reason:
                    withheld.append({'name': name, **origin, 'license': kind, 'sha256': digest, 'reason': reason})
                    continue
                if key in published:
                    published[key]['origins'].append(origin)
                    continue
                dest = ROOT / 'local-skills' / key
                if not dest.exists():
                    copy_bundle(path.parent, dest)
                if fingerprint(dest)[0] != digest:
                    raise ValueError(f'Published copy differs from source: {key}')
                notice_root = ROOT / 'licenses/local' / key
                for i, lic in enumerate(licfiles):
                    notice_root.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(lic, notice_root / f'{i}-{lic.name}')
                lics = sorted(notice_root.iterdir()) if notice_root.exists() else []
                published[key] = {
                    'id': key, 'name': name, 'license': kind if kind in PUBLISHABLE else 'owned-by-user',
                    'origins': [origin], 'path': dest.relative_to(ROOT).as_posix(),
                    'prerequisites': 'Original plugin tools, packages, and connectors; see SKILL.md.',
                    'sha256': digest, 'files': manifest,
                    'license_files': [p.relative_to(ROOT).as_posix() for p in lics],
                    'license_hashes': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                       for p in lics}}
            except (ValueError, OSError) as exc:
                errors.append({**origin, 'error': str(exc)})
    entries = sorted(published.values(), key=lambda e: e['id'])
    write_json(ROOT / 'catalog/published-local.json', {'captured_at': datetime.now(timezone.utc).isoformat(),
                                                      'skills': entries, 'withheld': withheld, 'errors': errors})
    lines = ['# Published local skills', '',
             f'{len(entries)} distinct bundles copied unchanged from local skill folders into `local-skills/`. '
             'Exact files and hashes: [published-local.json](published-local.json).', '',
             'A bundle is published when it carries an MIT, Apache-2.0, or CC-BY-SA-4.0 license file, '
             'or when a user skill folder holds it under a name listed in [owned-skills.json](owned-skills.json). '
             'Restricted, unlicensed vendor, and malformed bundles stay local and appear below by name only.', '',
             '| Skill | License | Found in |', '|---|---|---|']
    for e in entries:
        where = ', '.join(sorted({o['provider'] for o in e['origins']}))
        lines.append(f'| [{e["name"]}](../{e["path"]}/SKILL.md) | {e["license"]} | {where} |')
    lines.extend(['', '## Withheld', '', '| Skill | Reason | Found in |', '|---|---|---|'])
    groups = {}
    for w in withheld:
        groups.setdefault((w['name'], w['reason']), set()).add(w['provider'])
    for (name, reason), providers in sorted(groups.items()):
        lines.append(f'| {name} | {reason} | {", ".join(sorted(providers))} |')
    write_text(ROOT / 'catalog/PUBLISHED_LOCAL.md', '\n'.join(lines) + '\n')
    print(json.dumps({'published': len(entries), 'withheld_occurrences': len(withheld), 'errors': errors}, indent=2))
    return 1 if errors else 0


def vendor(args):
    lock = read_json(ROOT / 'catalog/sources.lock.json')
    entries = []
    for source in lock['sources']:
        repo = ROOT / '.local/upstreams' / source['repo'].replace('/', '--')
        if not repo.exists():
            repo.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['git', 'clone', '--filter=blob:none', '--no-checkout', 'https://github.com/' + source['repo'] + '.git', str(repo)], check=True)
            patterns = {'/LICENSE*', '/THIRD_PARTY_NOTICES.md'}
            for item in source['selected']:
                path = Path(item['path'])
                patterns.add('/' + path.as_posix() + '/')
                for parent in path.parents:
                    if str(parent) != '.':
                        patterns.add('/' + parent.as_posix() + '/LICENSE*')
            subprocess.run(['git', '-C', str(repo), 'sparse-checkout', 'set', '--no-cone', *sorted(patterns)], check=True)
            subprocess.run(['git', '-C', str(repo), 'checkout', '--detach', source['commit']], check=True)
        actual = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != source['commit']:
            raise ValueError(f'Wrong upstream commit for {source["id"]}: {actual}')
        if subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'], text=True).strip():
            raise ValueError(f'Upstream checkout has local changes: {source["id"]}')
        for selection in source['selected']:
            skill = (repo / selection['path']).resolve()
            if not skill.is_relative_to(repo.resolve()):
                raise ValueError('Skill path escapes checkout')
            meta = metadata(skill / 'SKILL.md')
            if not SAFE_NAME.fullmatch(meta['name']):
                raise ValueError(f'Invalid skill name: {meta["name"]}')
            licenses = license_files(skill, repo.resolve())
            kind = license_kind(licenses)
            if kind != selection['license'] or kind not in {'MIT', 'Apache-2.0', 'CC-BY-SA-4.0'}:
                raise ValueError(f'Unapproved license for {source["id"]}/{meta["name"]}: {kind}')
            dest = ROOT / 'skills' / source['id'] / meta['name']
            upstream_digest, _ = fingerprint(skill)
            if not dest.exists():
                copy_bundle(skill, dest)
            # Save inherited licenses outside the unchanged skill bundle.
            notice_root = ROOT / 'licenses' / source['id'] / meta['name']
            for i, lic in enumerate(licenses):
                notice_root.mkdir(parents=True, exist_ok=True)
                shutil.copy2(lic, notice_root / f'{i}-{lic.name}')
            notice = repo / 'THIRD_PARTY_NOTICES.md'
            if notice.exists():
                target = ROOT / 'licenses' / source['id'] / notice.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(notice, target)
            digest, manifest = fingerprint(dest)
            if digest != upstream_digest:
                raise ValueError(f'Vendored skill differs from pinned source: {dest}')
            entries.append({'id': source['id'] + '/' + meta['name'], 'name': meta['name'],
                            'description': meta['description'], 'category': selection['category'],
                            'reason': selection['reason'], 'prerequisites': selection['prerequisites'],
                            'license': kind, 'source': source['repo'], 'commit': source['commit'],
                            'upstream_path': selection['path'], 'url': f'https://github.com/{source["repo"]}/tree/{source["commit"]}/{selection["path"]}',
                            'path': str(dest.relative_to(ROOT)), 'sha256': digest, 'files': manifest,
                            'license_files': [str(p.relative_to(ROOT)) for p in sorted(notice_root.iterdir())],
                            'license_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                               for p in sorted(notice_root.iterdir())}})
    write_json(ROOT / 'catalog/skills.json', {'schema_version': 1, 'skills': entries})
    print(f'Vendored {len(entries)} unchanged skill bundles with pinned provenance.')


def verify(args):
    errors = []
    data = read_json(ROOT / 'catalog/skills.json')['skills']
    ids = set()
    for entry in data:
        try:
            if entry['id'] in ids:
                raise ValueError('Duplicate catalog ID')
            ids.add(entry['id'])
            skill = ROOT / entry['path']
            if metadata(skill / 'SKILL.md')['name'] != entry['name']:
                raise ValueError('Name mismatch')
            if not matches(entry, skill):
                raise ValueError('Bundle integrity mismatch')
            if not entry['license_files'] or any(not (ROOT / p).is_file() for p in entry['license_files']):
                raise ValueError('Missing license attribution')
            for p, expected_hash in entry['license_hashes'].items():
                if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != expected_hash:
                    raise ValueError('License attribution integrity mismatch')
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f'{entry["id"]}: {exc}')
    expected = {str((ROOT / e['path'] / 'SKILL.md').resolve()) for e in data}
    found = {str(p.resolve()) for p in (ROOT / 'skills').rglob('SKILL.md')}
    for p in found - expected:
        errors.append(f'Uncataloged nested skill: {p}')
    published_path = ROOT / 'catalog/published-local.json'
    published = read_json(published_path)['skills'] if published_path.exists() else []
    for entry in published:
        try:
            if metadata(ROOT / entry['path'] / 'SKILL.md')['name'] != entry['name']:
                raise ValueError('Name mismatch')
            if not matches(entry, ROOT / entry['path']):
                raise ValueError('Bundle integrity mismatch')
            if entry['license'] in PUBLISHABLE and not entry['license_files']:
                raise ValueError('Missing license attribution')
            for p, expected_hash in entry['license_hashes'].items():
                if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != expected_hash:
                    raise ValueError('License attribution integrity mismatch')
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f'{entry["id"]}: {exc}')
    if (ROOT / 'local-skills').is_dir():
        cataloged = {Path(e['path']).name for e in published}
        for extra in sorted({p.name for p in (ROOT / 'local-skills').iterdir()} - cataloged):
            errors.append(f'Uncataloged published bundle: local-skills/{extra}')
    profiles = read_json(ROOT / 'catalog/profiles.json')
    for name, members in profiles.items():
        unknown = set(members) - ids
        if unknown:
            errors.append(f'{name}: unknown IDs {sorted(unknown)}')
        names = [e['name'] for e in data if e['id'] in members]
        if len(names) != len(set(names)):
            errors.append(f'{name}: install name collision')
    if args.local:
        local = read_json(ROOT / '.local/inventory.json')
        errors.extend(str(e) for e in local['errors'])
        for e in {e['id']: e for e in local['skills'] if e['archive_path']}.values():
            try:
                if not matches(e, ROOT / e['archive_path']):
                    raise ValueError('Private snapshot integrity mismatch')
            except (ValueError, OSError) as exc:
                errors.append(f'{e["id"]}: {exc}')
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'public_skills': len(data),
              'public_files': sum(len(e['files']) for e in data), 'published_local': len(published), 'profiles': len(profiles),
              'local_checked': args.local, 'passed': not errors, 'errors': errors,
              'scope': 'Metadata, complete bundle hashes, attribution presence, profile IDs; no skill runtime execution.'}
    write_json(ROOT / 'research/validation.json', report)
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


def listing(args):
    if args.published:
        for e in read_json(ROOT / 'catalog/published-local.json')['skills']:
            if not args.query or args.query.lower() in e['id'].lower():
                print(f'{e["id"]:75} {e["license"]}')
        return
    if args.local:
        entries = read_json(ROOT / 'catalog/local-skills.json')['skills']
        unique = {e['id']:e for e in entries}
        for e in sorted(unique.values(), key=lambda e:e['id']):
            if not args.query or args.query.lower() in e['id'].lower():
                print(f'{e["id"]:75} {e["status"]} | {e["license"]}')
        return
    skills = read_json(ROOT / 'catalog/skills.json')['skills']
    for e in skills:
        if not args.query or args.query.lower() in (e['id'] + ' ' + e['description'] + ' ' + e['category']).lower():
            print(f'{e["id"]:65} {e["category"]} | {e["license"]}')


def install(args):
    if args.local:
        if args.profile:
            raise ValueError('Profiles contain public skills; choose local bundle IDs instead')
        local = read_json(ROOT / '.local/inventory.json')['skills']
        catalog = {}
        for e in local:
            entry = dict(e)
            entry['path'] = e['archive_path']
            entry['prerequisites'] = 'Original skill dependencies and app/plugin tools; private local use only.'
            entry['license_files'] = [str(p.relative_to(ROOT)) for p in sorted((ROOT / '.local/licenses' / e['id']).glob('*'))]
            catalog[e['id']] = entry
    elif args.published:
        if args.profile:
            raise ValueError('Profiles contain public skills; choose published bundle IDs instead')
        catalog = {e['id']: e for e in read_json(ROOT / 'catalog/published-local.json')['skills']}
    else:
        catalog = {e['id']: e for e in read_json(ROOT / 'catalog/skills.json')['skills']}
    selected = read_json(ROOT / 'catalog/profiles.json')[args.profile] if args.profile else args.ids
    if not selected:
        raise ValueError('Choose skill IDs or --profile')
    dest = Path(args.dest).expanduser().resolve()
    plan, names = [], set()
    for key in selected:
        e = catalog[key]
        if not e['path']:
            raise ValueError(f'Restricted reference cannot be installed from this repository: {key}')
        if not SAFE_NAME.fullmatch(e['name']):
            raise ValueError(f'Unsafe installation directory name: {e["name"]}')
        if args.local and not e['metadata_valid']:
            raise ValueError(f'Malformed original metadata requires review before installation: {key}')
        if e['name'] in names:
            raise ValueError(f'Selected skills collide: {e["name"]}')
        names.add(e['name'])
        source = ROOT / e['path']
        if not matches(e, source):
            raise ValueError(f'Integrity check failed: {key}')
        if not args.local:
            for lic, expected_hash in e['license_hashes'].items():
                if hashlib.sha256((ROOT / lic).read_bytes()).hexdigest() != expected_hash:
                    raise ValueError(f'License integrity check failed: {key}')
        target = dest / e['name']
        if target.exists() or target.is_symlink():
            raise ValueError(f'Refusing to overwrite existing skill: {target}')
        plan.append((e, source, target))
    for e, source, target in plan:
        print(f'{e["id"]} -> {target} | needs: {e["prerequisites"]}')
    if args.dry_run:
        return
    for e, source, target in plan:
        copy_bundle(source, target)
        notice_dir = target / '_collection_attribution'
        notice_dir.mkdir()
        write_json(notice_dir / 'provenance.json', {k:v for k,v in e.items() if k != 'files'})
        for lic in e['license_files']:
            shutil.copy2(ROOT / lic, notice_dir / Path(lic).name)
        notice = ROOT / 'licenses' / e['id'].split('/')[0] / 'THIRD_PARTY_NOTICES.md'
        if notice.exists():
            shutil.copy2(notice, notice_dir / notice.name)
    print('Copied skills only; dependencies, MCP servers, hooks, and account connections are not installed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('snapshot'); p.add_argument('--root', action='append'); p.set_defaults(fn=snapshot)
    p = sub.add_parser('publish'); p.set_defaults(fn=publish)
    p = sub.add_parser('vendor'); p.set_defaults(fn=vendor)
    p = sub.add_parser('verify'); p.add_argument('--local', action='store_true'); p.set_defaults(fn=verify)
    p = sub.add_parser('list'); p.add_argument('query', nargs='?', default=''); p.add_argument('--local', action='store_true')
    p.add_argument('--published', action='store_true'); p.set_defaults(fn=listing)
    p = sub.add_parser('install'); p.add_argument('ids', nargs='*'); p.add_argument('--profile');
    p.add_argument('--dest', required=True); p.add_argument('--dry-run', action='store_true'); p.add_argument('--local', action='store_true')
    p.add_argument('--published', action='store_true'); p.set_defaults(fn=install)
    args = parser.parse_args()
    try:
        return args.fn(args) or 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, yaml.YAMLError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
