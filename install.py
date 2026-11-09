"""Windows user-scope customization installer. Python 3.11+, Node.js 24+."""
import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def merge(existing, incoming):
    """Add missing values without replacing user customizations or duplicating hooks."""
    if isinstance(existing, dict) and isinstance(incoming, dict):
        result = dict(existing)
        for key, value in incoming.items():
            result[key] = merge(result[key], value) if key in result else value
        return result
    if isinstance(existing, list) and isinstance(incoming, list):
        result = list(existing)
        for value in incoming:
            if value not in result:
                if isinstance(value, dict):
                    for prior in result:
                        if not isinstance(prior, dict):
                            continue
                        if value.get('id') and value.get('id') == prior.get('id'):
                            raise ValueError('Configuration conflict: existing harness ID differs')
                        commands = lambda group: {json.dumps([h.get('command'), h.get('args', [])]) for h in group.get('hooks', [])}
                        if value.get('matcher') == prior.get('matcher') and commands(value) & commands(prior):
                            raise ValueError('Configuration conflict: overlapping hook command; merge manually')
                result.append(value)
        return result
    if existing != incoming:
        raise ValueError('Configuration conflict: differing scalar value; merge manually before installing')
    return existing


def toml_value(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return '[' + ', '.join(toml_value(x) for x in value) + ']'
    if isinstance(value, dict):
        return '{' + ', '.join(f'{toml_value(k)} = {toml_value(v)}' for k, v in value.items()) + '}'
    raise ValueError('Unsupported TOML value')


def merge_toml(text, incoming):
    current = tomllib.loads(text)
    # Appending individual dotted keys inside existing tables can silently relocate them.
    # Only append new tables/array entries; refuse other changes instead of rewriting TOML.
    additions = []
    for table, data in incoming.items():
        if table == 'hooks':
            for event, groups in data.items():
                prior = current.get('hooks', {}).get(event, [])
                merged = merge(prior, groups)
                for group in merged:
                    if group not in prior:
                        additions.append(f'[[hooks.{json.dumps(event)}]]\n' + '\n'.join(f'{json.dumps(k)} = {toml_value(v)}' for k, v in group.items()))
        elif table == 'mcp_servers':
            for name, config in data.items():
                if name in current.get(table, {}):
                    if merge(current[table][name], config) != current[table][name]:
                        raise ValueError(f'Existing MCP {name} needs manual merge of missing fields')
                    continue
                additions.append(f'[mcp_servers.{json.dumps(name)}]\n' + '\n'.join(f'{json.dumps(k)} = {toml_value(v)}' for k, v in config.items()))
        elif table not in current:
            additions.append(f'[{json.dumps(table)}]\n' + '\n'.join(f'{json.dumps(k)} = {toml_value(v)}' for k, v in data.items()))
        else:
            # features is deliberately limited to hooks; don't change sandbox/permissions.
            for key, value in data.items():
                if key in current[table]:
                    merge(current[table][key], value)
                else:
                    pattern = rf'(?m)^\[{re.escape(table)}\][ \t]*(?:#.*)?$'
                    text, count = re.subn(pattern, lambda m: m.group() + f'\n{json.dumps(key)} = {toml_value(value)}', text, count=1)
                    if count != 1:
                        raise ValueError(f'Cannot safely extend TOML table {table}')
    result = text.rstrip() + ('\n\n' + '\n\n'.join(additions) if additions else '') + '\n'
    tomllib.loads(result)
    return result


def safe_target(base, relative):
    target = base / relative
    if not target.resolve().is_relative_to(base.resolve()) or target.is_symlink():
        raise ValueError(f'Unsafe target path: {relative}')
    return target


def short_runtime(home):
    path = home / '.agent-collab'
    if os.name != 'nt':
        return None
    # Its existing parent must have an actual 8.3 alias; never reuse the source PC alias.
    buf = ctypes.create_unicode_buffer(32768)
    n = ctypes.windll.kernel32.GetShortPathNameW(str(home), buf, len(buf))
    if not n or n >= len(buf) or ' ' in buf.value:
        return None
    return (buf.value.replace('\\', '/') + '/.agent-collab')


def render(value, home, project, short):
    if isinstance(value, str):
        for token, replacement in [('@@HOME@@', home.as_posix()), ('@@PROJECT@@', project.as_posix() if project else '@@PROJECT@@'), ('@@SHORT_RUNTIME@@', short or '@@SHORT_RUNTIME@@')]:
            value = value.replace(token, replacement)
        return value
    if isinstance(value, dict):
        return {k: render(v, home, project, short) for k, v in value.items()}
    if isinstance(value, list):
        return [render(v, home, project, short) for v in value]
    return value


def payload_bytes(package, manifest):
    expected = {item['path']: item for item in manifest['files']}
    if len(expected) != len(manifest['files']):
        raise ValueError('Duplicate payload path')
    if (package / 'payload').is_dir():
        result = {name: safe_target(package / 'payload', name).read_bytes() for name in expected}
    else:
        with zipfile.ZipFile(package / 'payload.zip') as archive:
            entries = archive.infolist()
            if len(entries) != len(expected) or {x.filename for x in entries} != set(expected):
                raise ValueError('Archive entries differ from manifest')
            if sum(x.file_size for x in entries) > 512 * 1024 * 1024:
                raise ValueError('Archive exceeds package size limit')
            result = {name: archive.read(name) for name in expected}
    for name, data in result.items():
        # Validate names even when reading the archive without extracting it.
        safe_target(package / 'payload', name)
        if sha(data) != expected[name]['sha256']:
            raise ValueError(f'Payload hash mismatch: {name}')
    return result


def build_plan(home, package=ROOT):
    project = None
    manifest = json.loads((package / 'manifest.json').read_text('utf-8'))
    if manifest.get('format') != 1:
        raise ValueError('Unsupported package format')
    plan, pending = {}, []
    payload = payload_bytes(package, manifest)
    short = short_runtime(home)
    bases = {'user': home}
    for item in manifest['files']:
        scope, relative = item['path'].split('/', 1)
        if scope not in bases:
            raise ValueError('Unknown file scope')
        if not bases[scope]:
            continue
        raw = payload[item['path']]
        data = render(raw.decode('utf-8'), home, project, short).encode('utf-8') if item['text'] else raw
        target = safe_target(bases[scope], relative)
        if target.exists() and target.read_bytes() != data:
            # Project/global rule files belong to the destination user. Never replace them.
            if target.name in {'AGENTS.md', 'CLAUDE.md'}:
                pending.append(f'Preserved existing rules; review package copy: {target}')
                continue
            raise ValueError(f'File conflict (no files written): {target}')
        if not target.exists():
            plan[target] = data

    def available(config):
        command = config.get('command', '')
        if not command:
            return True
        if ((':' in command or '/' in command or '\\' in command) and not Path(command).is_file()) or (not any(x in command for x in '/\\:') and not shutil.which(command)):
            return False
        return all(Path(arg).is_file() or Path(arg) in plan for arg in config.get('args', []) if re.match(r'^[A-Za-z]:[/\\]', arg) and not Path(arg).is_dir())

    for location, incoming in manifest['configs'].items():
        scope, relative = location.split('/', 1)
        if scope not in bases or not bases[scope]:
            continue
        data = render(incoming, home, project, short)
        if relative == '.gemini/config/hooks.json' and not short:
            pending.append('Antigravity hooks: no verified space-free home path; native setup required')
            continue
        for key in ['mcpServers', 'mcp_servers']:
            if key in data:
                for name, config in list(data[key].items()):
                    if name == 'shared-conversation-history':
                        config['command'] = shutil.which('node') or config.get('command', 'node')
                    if not available(config):
                        pending.append(f'{location}: install prerequisite for MCP {name}, then rerun')
                        del data[key][name]
        if 'hooks' in data:
            for event, groups in data['hooks'].items():
                kept = []
                for group in groups:
                    # Codebase Memory hooks must not be registered before its executable exists.
                    if 'codebase-memory-mcp.exe' in json.dumps(group) and not (home / 'AppData/Local/Programs/codebase-memory-mcp/codebase-memory-mcp.exe').is_file():
                        pending.append(f'{location}: {event} Codebase Memory hook pending executable')
                    else:
                        kept.append(group)
                data['hooks'][event] = kept
        if relative == '.tastecode/custom-harnesses.json' and not (home / 'AppData/Roaming/npm/node_modules/@openai/codex/bin/codex.js').is_file():
            pending.append('TasteCode custom harness: install npm Codex CLI first, then rerun')
            continue
        if relative == '.tastecode/custom-harnesses.json':
            for harness in data.get('harnesses', []):
                if harness.get('id') == 'codex-global-cli':
                    harness['command'] = shutil.which('node') or harness['command']
        target = safe_target(bases[scope], relative)
        old = target.read_bytes() if target.exists() else b''
        if relative.endswith('.toml'):
            new = merge_toml(old.decode('utf-8-sig'), data).encode('utf-8')
        else:
            current = json.loads(old.decode('utf-8-sig')) if old else {}
            new = json_bytes(merge(current, data))
        if old != new:
            plan[target] = new
    pending += ['Native hook trust/permissions must be reviewed on this PC.',
                'Reinstall app-managed plugins and reconnect accounts using manifest inventory and README.',
                'No compatibility claim until native sessions are tested on this PC.']
    return plan, pending


def apply_plan(plan, home):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = home / '.agent-toolkit/backups' / stamp
    backup.mkdir(parents=True, exist_ok=False)
    receipt = []
    for index, (target, data) in enumerate(plan.items()):
        before = target.read_bytes() if target.exists() else None
        item = {'target': str(target), 'before_sha256': sha(before) if before is not None else None, 'after_sha256': sha(data), 'backup': str(index) if before is not None else None}
        if before is not None:
            (backup / str(index)).write_bytes(before)
        receipt.append(item)
    (backup / 'receipt.json').write_bytes(json_bytes(receipt))
    try:
        for item, (target, data) in zip(receipt, plan.items()):
            current = target.read_bytes() if target.exists() else None
            if (sha(current) if current is not None else None) != item['before_sha256']:
                raise ValueError(f'File changed during installation: {target}')
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as temp:
                temp.write(data)
                name = temp.name
            try:
                os.replace(name, target)
            finally:
                if os.path.exists(name):
                    os.unlink(name)
    except Exception:
        print(f'Installation interrupted; inspect recovery receipt: {backup / "receipt.json"}', file=sys.stderr)
        raise
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if os.name != 'nt':
        parser.error('Windows only; cross-platform runtime compatibility is not verified')
    home = Path.home().resolve()
    node = shutil.which('node')
    if not node or int(subprocess.check_output([node, '--version'], text=True).strip().lstrip('v').split('.')[0]) < 24:
        parser.error('Install Node.js 24+ before running this installer')
    # Hooks must not be replaced while an agent or harness is running.
    check = subprocess.check_output(['powershell.exe', '-NoProfile', '-Command', "Get-Process -Name 'codex','claude','antigravity','Taste Code' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProcessName; exit 0"], text=True)
    if check.strip() and not args.dry_run:
        parser.error('Quit Codex, Claude Code, Antigravity and TasteCode normally before installation')
    plan, pending = build_plan(home)
    if args.dry_run:
        print(json.dumps({'status': 'DRY RUN', 'files': [str(p) for p in plan], 'pending': pending}, ensure_ascii=False, indent=2))
    else:
        backup = apply_plan(plan, home) if plan else None
        print(json.dumps({'status': 'FILES INSTALLED; NATIVE TESTS PENDING', 'changed': len(plan), 'backup': str(backup) if backup else None, 'pending': pending}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
