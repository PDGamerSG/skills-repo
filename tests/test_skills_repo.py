import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import skills_repo as repo


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(repo, 'ROOT', self.root)
        self.root_patch.start()
        self.skill = self.root / 'skills/test/sample'
        self.skill.mkdir(parents=True)
        (self.skill / 'SKILL.md').write_text('---\nname: sample\ndescription: Sample task.\n---\nBody\n')
        (self.skill / 'asset.txt').write_text('important resource')
        license_path = self.root / 'licenses/test/sample/LICENSE'
        license_path.parent.mkdir(parents=True)
        license_path.write_text('license evidence')
        digest, files = repo.fingerprint(self.skill)
        entry = {'id':'test/sample','name':'sample','path':'skills/test/sample',
                 'sha256':digest,'files':files,'prerequisites':'none',
                 'license_files':['licenses/test/sample/LICENSE'],
                 'license_hashes':{'licenses/test/sample/LICENSE':hashlib.sha256(license_path.read_bytes()).hexdigest()}}
        repo.write_json(self.root / 'catalog/skills.json', {'skills':[entry]})
        repo.write_json(self.root / 'catalog/profiles.json', {'sample':['test/sample']})
    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()
    def install(self, **kwargs):
        args = dict(ids=['test/sample'], profile=None, dest=str(self.root / 'installed'), dry_run=False, local=False, published=False)
        args.update(kwargs)
        with contextlib.redirect_stdout(io.StringIO()):
            repo.install(SimpleNamespace(**args))
    def test_resource_changes_change_bundle_hash(self):
        before = repo.fingerprint(self.skill)[0]
        (self.skill / 'asset.txt').write_text('changed')
        self.assertNotEqual(before, repo.fingerprint(self.skill)[0])
    def test_copy_preserves_complete_bundle(self):
        target = self.root / 'copy'
        repo.copy_bundle(self.skill, target)
        self.assertEqual(repo.fingerprint(self.skill), repo.fingerprint(target))
    def test_external_resource_symlink_rejected(self):
        outside = self.root / 'outside.txt'; outside.write_text('private')
        (self.skill / 'link.txt').symlink_to(outside)
        with self.assertRaises(ValueError): repo.fingerprint(self.skill)
    def test_env_and_cache_files_excluded(self):
        (self.skill / '.env').write_text('SECRET=private')
        cache = self.skill / '__pycache__'; cache.mkdir(); (cache / 'secret.pyc').write_text('private')
        self.assertEqual(len(repo.fingerprint(self.skill)[1]), 2)
    def test_symlinked_skill_discovered(self):
        root = self.root / 'local'; root.mkdir(); (root / 'linked').symlink_to(self.skill, target_is_directory=True)
        self.assertEqual(len(list(repo.find_skills(root))), 1)
    def test_dry_run_has_no_installation_side_effect(self):
        self.install(dry_run=True)
        self.assertFalse((self.root / 'installed').exists())
    def test_install_copies_resources_and_attribution(self):
        self.install()
        target = self.root / 'installed/sample'
        self.assertEqual((target / 'asset.txt').read_text(), 'important resource')
        self.assertTrue((target / '_collection_attribution/LICENSE').exists())
        self.assertTrue((target / '_collection_attribution/provenance.json').exists())
    def test_existing_skill_never_overwritten(self):
        target = self.root / 'installed/sample'; target.mkdir(parents=True)
        (target / 'keep.txt').write_text('original')
        with self.assertRaises(ValueError): self.install()
        self.assertEqual((target / 'keep.txt').read_text(), 'original')
    def test_tampered_skill_not_installed(self):
        (self.skill / 'asset.txt').write_text('changed')
        with self.assertRaises(ValueError): self.install()
        self.assertFalse((self.root / 'installed').exists())
    def test_collision_is_rejected_before_any_copy(self):
        with self.assertRaises(ValueError): self.install(ids=['test/sample','test/sample'])
        self.assertFalse((self.root / 'installed').exists())
    def test_restricted_license_recognized(self):
        license_path = self.root / 'restricted'
        license_path.write_text('You may not retain copies outside the Services.')
        self.assertEqual(repo.license_kind([license_path]), 'restricted')
    def test_tampered_license_not_installed(self):
        (self.root / 'licenses/test/sample/LICENSE').write_text('changed')
        with self.assertRaises(ValueError): self.install()
        self.assertFalse((self.root / 'installed').exists())


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve() / 'repo'
        self.home = Path(self.temp.name).resolve() / 'home'
        self.patches = [patch.object(repo, 'ROOT', self.root),
                        patch.object(repo, 'local_roots', lambda: {'claude-user': self.home / 'skills',
                                                                   'claude-plugin-cache': self.home / 'cache'})]
        for p in self.patches: p.start()
        repo.write_json(self.root / 'catalog/skills.json', {'skills': []})
        repo.write_json(self.root / 'catalog/profiles.json', {})
        repo.write_json(self.root / 'catalog/owned-skills.json', {'names': ['mine']})
    def tearDown(self):
        for p in self.patches: p.stop()
        self.temp.cleanup()
    def skill(self, where, name, license_text=None):
        folder = self.home / where / name
        folder.mkdir(parents=True)
        (folder / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Test.\n---\nBody\n')
        if license_text:
            (folder / 'LICENSE').write_text(license_text)
        return folder
    def publish(self):
        with contextlib.redirect_stdout(io.StringIO()):
            repo.publish(SimpleNamespace())
        return repo.read_json(self.root / 'catalog/published-local.json')
    def test_publishes_open_and_owned_only(self):
        self.skill('cache', 'open', 'MIT License\nPermission is hereby granted, free of charge, without restriction')
        self.skill('skills', 'mine')
        self.skill('cache', 'mine')
        self.skill('cache', 'vendor')
        self.skill('skills', 'closed', 'You may not retain copies outside the Services.')
        self.skill('skills/.trash/x', 'deleted', 'MIT License\nPermission is hereby granted, free of charge, without restriction')
        data = self.publish()
        self.assertEqual(sorted(e['name'] for e in data['skills']), ['mine', 'open'])
        reasons = {w['name']: w['reason'] for w in data['withheld']}
        self.assertEqual(reasons, {'mine': 'No license file; vendor-owned', 'vendor': 'No license file; vendor-owned',
                                   'closed': 'Restricted license'})
        for e in data['skills']:
            self.assertTrue((self.root / e['path'] / 'SKILL.md').exists())
    def test_duplicate_content_published_once(self):
        self.skill('skills', 'mine')
        self.skill('skills/synced/0d13df11-0139-4163-9927-e73ea9adbc26', 'mine')
        data = self.publish()
        self.assertEqual(len(data['skills']), 1)
        self.assertEqual([o['path'] for o in data['skills'][0]['origins']], ['mine', 'synced/<id>/mine'])
    def test_verify_flags_uncataloged_and_tampered_bundles(self):
        self.skill('skills', 'mine')
        entry = self.publish()['skills'][0]
        (self.root / entry['path'] / 'SKILL.md').write_text('---\nname: mine\ndescription: Changed.\n---\n')
        (self.root / 'local-skills/stray').mkdir()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(repo.verify(SimpleNamespace(local=False)), 1)
        errors = repo.read_json(self.root / 'research/validation.json')['errors']
        self.assertEqual(errors, [f'{entry["id"]}: Bundle integrity mismatch',
                                  'Uncataloged published bundle: local-skills/stray'])


if __name__ == '__main__': unittest.main()
