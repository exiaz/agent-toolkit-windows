# Agent Toolkit for Windows

A toolkit for AI-assisted application development and design. It brings together agent skills, hooks, configuration, and tool references for writing code, designing interfaces, creating animations, reviewing work, and preparing documents and visual assets.

The goal is to make a reusable development environment easier to set up on another Windows PC, with configuration installed at the **user level**.

Curated for use with **Codex, Claude Code, Google Antigravity, and TasteCode**. Third-party work, product names, and licenses belong to their respective creators. See [Credits](CREDITS.md) for attribution and [Tools](TOOLS.md) for official sources and installation links.

> **Language:** This toolkit was originally assembled in Indonesian. Some bundled rules, workflow notes, and supporting documentation are in Indonesian. This README provides the English setup guide. Upstream skills and license texts retain their original language.

## What you can use it for

| Area | Examples |
|---|---|
| Application development | Understand a codebase, plan features, write code, debug, and review changes |
| UI/UX design | Work on layouts, typography, color, components, and responsive interfaces |
| Animation and interaction | Design motion and microinteractions, and review animation performance |
| Agent collaboration | Delegate tasks explicitly and coordinate file changes |
| Documents and visual content | Connect tools for documents, spreadsheets, presentations, images, and design assets |

Choose the skills and integrations that fit your work. Install provider applications, plugins, and account connectors through their original providers.

## Getting started

### 1. Install the prerequisites

- Windows with [Python 3.11+](https://www.python.org/downloads/windows/) and [Node.js 24+](https://nodejs.org/en/download).
- [Git](https://gitforwindows.org/) and [GitHub CLI](https://cli.github.com/).
- The agent applications you want to use. Links are listed in [TOOLS.md](TOOLS.md).

Close agent applications and desktop harnesses normally before installing configuration. Follow GitHub CLI authentication prompts if your setup requires them.

### 2. Run one command

In PowerShell, use a new destination folder:

```powershell
gh repo clone exiaz/agent-toolkit-windows "$env:USERPROFILE\agent-toolkit-windows"; if ($LASTEXITCODE -eq 0) { python "$env:USERPROFILE\agent-toolkit-windows\install.py" }
```

The installer adapts paths to your user profile, verifies file integrity, and creates backups before changing configuration. Install provider applications and system dependencies separately using their official installation guides.

### 3. Connect the services you use

Open your agent application, review hooks using its native permission controls, and sign in or connect the services you need. The installer lists MCP configurations that require additional executables so you can install those dependencies first.

Credentials, API keys, OAuth tokens, conversation history, and session databases are not included in the package.

## Repository contents

| File | Purpose |
|---|---|
| [Install.ps1](Install.ps1) / [install.py](install.py) | User-level configuration installer |
| [payload.zip](payload.zip) | Skills, hooks, agent definitions, collaboration runtime, and supporting files |
| [manifest.json](manifest.json) | File inventory, SHA-256 hashes, and plugin and connector inventory |
| [TOOLS.md](TOOLS.md) | Tool catalog and official links |
| [CREDITS.md](CREDITS.md) | Original creators, sources, attribution, and third-party licenses |
| [third-party-licenses/](third-party-licenses/) | Copies of upstream license texts and notices |
| [VERIFICATION.md](VERIFICATION.md) | Package checks and verification commands |

Collaboration supports explicit delegation between Codex and Claude. Startup hooks do not launch workers. Antigravity uses its own hook schema; this package does not enable inbound delegation to Antigravity. TasteCode runs native agent providers with its own session management and permission controls.

## Installation options

**Preview the plan without changing files:**

```powershell
python "$env:USERPROFILE\agent-toolkit-windows\install.py" --dry-run
```

**Copy skills manually:**

```powershell
Expand-Archive .\payload.zip .\payload
Get-ChildItem .\payload\user\.agents\skills -Directory
```

Copy the complete skill folder, including its references, scripts, assets, and licenses. Include [Credits](CREDITS.md) and the relevant licenses when redistributing components. Use the installer for files containing `@@HOME@@` or `@@SHORT_RUNTIME@@` so paths are adapted correctly.

## Configuration and backups

The installer preserves existing destination rules and rejects conflicting files or configuration so you can review the differences. Reinstalling the same configuration does not duplicate hooks. Native permissions, sandbox settings, hook trust, authentication, and Git branches remain under your control.

Backups and receipts are stored in `%USERPROFILE%\.agent-toolkit\backups\TIMESTAMP`. Each receipt records paths, before/after hashes, and the location of original copies. Before restoring a file, close the agents normally and compare its current hash with `after_sha256`. Restore a copy only after checking for newer changes you want to keep. If installation is interrupted, use the receipt to review which files were changed.

Coordination depends on active hooks. Manual edits and tools that bypass hooks remain outside that coordination.

## Verification and updates

Run the checks from the repository folder:

```powershell
python -m unittest -v test_install.py
```

When updating the package, include only general-purpose configuration and skills intended for sharing. Preserve upstream licenses and verify payload hashes before distributing a new version.

## Credits

Thanks to the creators and contributors behind this environment, including OpenAI, Anthropic, Google, Leon Lin, Emil Kowalski, Paul Bakaus, Dominik Martin, Hallmark contributors, Vercel, DeusData, morluto, DietrichGebert, and the contributors to the referenced projects.

This is a community-curated toolkit, not an official distribution or an affiliation with those providers. Sources and component terms are listed in [CREDITS.md](CREDITS.md).
