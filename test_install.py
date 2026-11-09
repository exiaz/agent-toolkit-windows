import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest
import zipfile
from unittest.mock import patch

import install


class InstallerTests(unittest.TestCase):
    def test_zip_payload_rejects_extra_entries_and_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            manifest = {'files': [{'path': 'user/file.txt', 'sha256': install.sha(b'expected')}]}
            with zipfile.ZipFile(package / 'payload.zip', 'w') as archive:
                archive.writestr('user/file.txt', b'expected')
            self.assertEqual(install.payload_bytes(package, manifest)['user/file.txt'], b'expected')
            with zipfile.ZipFile(package / 'payload.zip', 'w') as archive:
                archive.writestr('user/file.txt', b'changed')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                install.payload_bytes(package, manifest)
            with zipfile.ZipFile(package / 'payload.zip', 'w') as archive:
                archive.writestr('user/file.txt', b'expected')
                archive.writestr('../outside', b'bad')
            with self.assertRaisesRegex(ValueError, 'entries differ'):
                install.payload_bytes(package, manifest)

    def test_preserves_auth_and_rejects_scalar_conflicts(self):
        existing = {'auth': {'token': 'fictional'}, 'mcpServers': {}}
        merged = install.merge(existing, {'mcpServers': {'example': {'command': 'node'}}})
        self.assertEqual(merged['auth'], existing['auth'])
        self.assertEqual(existing['mcpServers'], {})
        with self.assertRaises(ValueError):
            install.merge({'sandbox': 'read-only'}, {'sandbox': 'danger-full-access'})

    def test_toml_preserves_existing_tables_and_is_idempotent(self):
        original = '# User setting\nmodel = "example"\n[features]\nother = true\n[mcp_servers.mine]\ncommand = "mine"\n'
        incoming = {'features': {'hooks': True}, 'hooks': {'PreToolUse': [{'matcher': '.*', 'hooks': [{'type': 'command', 'command': 'node "C:/Users/Other User/guard.mjs"'}]}]}, 'mcp_servers': {'new': {'command': 'node', 'env': {'X': 'y'}}}}
        result = install.merge_toml(original, incoming)
        parsed = tomllib.loads(result)
        self.assertEqual(parsed['model'], 'example')
        self.assertTrue(parsed['features']['other'])
        self.assertTrue(parsed['features']['hooks'])
        self.assertEqual(result, install.merge_toml(result, incoming))
        self.assertIn('# User setting', result)

    def test_no_duplicate_hook_with_changed_metadata(self):
        group = {'matcher': '.*', 'hooks': [{'type': 'command', 'command': 'node guard.mjs'}]}
        changed = copy.deepcopy(group)
        changed['hooks'][0]['timeout'] = 10
        with self.assertRaises(ValueError):
            install.merge([group], [changed])

    def test_rejects_paths_outside_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                install.safe_target(root, '../outside')
            with self.assertRaises(ValueError):
                install.safe_target(root, root.parent / 'outside')

    def test_package_hashes_and_no_private_state(self):
        manifest = json.loads((install.ROOT / 'manifest.json').read_text('utf-8'))
        self.assertGreater(len(manifest['files']), 100)
        payload = install.payload_bytes(install.ROOT, manifest)
        self.assertIn('user/.agent-collab/CREDITS.md', payload)
        self.assertIn('user/.agent-collab/third-party-licenses/pbakaus--impeccable--NOTICE.md', payload)
        for item in manifest['files']:
            self.assertEqual(install.sha(payload[item['path']]), item['sha256'], item['path'])
            parts = Path(item['path']).parts
            self.assertFalse(set(parts) & {'state', 'backups', '.git', 'node_modules', 'synced'})
            self.assertNotIn(Path(item['path']).name, ['auth.json', '.credentials.json'])
        self.assertNotIn('state', manifest['configs']['user/.codex/config.toml'].get('hooks', {}))
        self.assertNotIn('node_repl', manifest['configs']['user/.codex/config.toml'].get('mcp_servers', {}))
        for config in manifest['configs'].values():
            for server in config.get('mcpServers', config.get('mcp_servers', {})).values():
                self.assertNotIn('FIGMA_ACCESS_TOKEN', server.get('env', {}))

    def test_relocation_backup_and_second_install(self):
        with tempfile.TemporaryDirectory(prefix='toolkit-other-user-') as tmp:
            home = Path(tmp) / 'Other User'
            home.mkdir()
            config = home / '.claude/settings.json'
            config.parent.mkdir()
            config.write_text('{"theme":"existing"}', encoding='utf-8')
            with patch.object(install, 'short_runtime', return_value=None):
                plan, pending = install.build_plan(home)
                self.assertTrue(any('Antigravity hooks' in x for x in pending))
                self.assertTrue(all(str(p).startswith(str(home)) for p in plan))
                backup = install.apply_plan(plan, home)
                self.assertEqual(json.loads(config.read_text())['theme'], 'existing')
                self.assertIn(str(home).replace('\\', '/'), (home / '.claude/CLAUDE.md').read_text())
                receipt = json.loads((backup / 'receipt.json').read_text())
                entry = next(x for x in receipt if x['target'] == str(config))
                self.assertEqual((backup / entry['backup']).read_text(), '{"theme":"existing"}')
                again, _ = install.build_plan(home)
                self.assertEqual(again, {})
                # An unrelated destination change is detected before any writes.
                target = home / '.agent-collab/runtime/guard.mjs'
                target.write_text('user customization', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'File conflict'):
                    install.build_plan(home)
                self.assertEqual(target.read_text(), 'user customization')

    def test_public_payload_contains_only_general_components(self):
        manifest = json.loads((install.ROOT / 'manifest.json').read_text('utf-8'))
        self.assertTrue(all(x['path'].startswith('user/') for x in manifest['files']))
        self.assertTrue(all(x.startswith('user/') for x in manifest['configs']))
        self.assertNotIn('project_snapshot', manifest['inventory'])

    def test_real_snapshot_global_runtime(self):
        manifest = json.loads((install.ROOT / 'manifest.json').read_text('utf-8'))
        with tempfile.TemporaryDirectory(prefix='toolkit-global-snapshot-') as tmp:
            root = Path(tmp)
            for name, data in install.payload_bytes(install.ROOT, manifest).items():
                if name.startswith('user/.agent-collab/runtime/'):
                    target = install.safe_target(root, name.removeprefix('user/.agent-collab/'))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
            result = subprocess.run(['node', '--test', str(root / 'runtime/coord.test.mjs')], capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)



if __name__ == '__main__':
    unittest.main(verbosity=2)
