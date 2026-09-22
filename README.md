# phenates-agents-plugins

**Personal Agent Plugin.** A reusable portable Agent Plugins 1.0.0 package containing skills, agents, commands, and MCP configurations for multi-platform deployment across Claude Code, Claude Desktop, Hermes Agent, and other compatible agent frameworks.

## Overview

This package consolidates:

- **Skills** — Agent Skills (agentskills.io), portable across all platforms
- **Agents** — Sub-agents for Claude Code (coming soon)
- **Commands** — Slash commands (coming soon)
- **MCP servers** — Model Context Protocol integrations at fixed URLs (coming soon)

## Directory Structure

```
phenates-agents-plugins/
├── skills/
│   ├── markdown-flavor/        # House Markdown conventions + OFM syntax
│   ├── obsidian-vault/         # Obsidian vault access via MCP
│   ├── json-canvas/            # JSON Canvas (.canvas) file editing
│   ├── obsidian-bases/         # Obsidian Bases (.base) file editing
│   └── obsidian-cli/           # Obsidian CLI integration
├── agents/                      # Sub-agents (coming soon)
├── commands/                    # Slash commands (coming soon)
├── mcp.json                     # MCP server configurations
├── plugin.json                  # Agent Plugins 1.0 manifest
├── .claude-plugin/
│   ├── plugin.json             # Claude Code plugin manifest
│   └── marketplace.json        # Claude Code marketplace metadata
├── LICENSE                      # MIT license
└── README.md                    # This file
```

**Note:** `agents/` and `commands/` are empty placeholders; they exist to clarify the package structure and support future expansion. `mcp.json` is a skeleton JSON file ready for MCP server definitions.

## Platform Compatibility

| Platform                      | Mechanism             | Install                                                                                                                | Update                          | Remove                       | Status                   |
| ----------------------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ---------------------------- | ------------------------ |
| **Claude Code**               | Marketplace           | `/plugin marketplace add phenates-agents-plugins`                                                                        | `/plugin marketplace update`    | `/plugin marketplace remove` | ✅ Tested                |
| **Claude Desktop (Cowork)**   | Marketplace UI        | Add via Settings → Plugins → Marketplace                                                                               | Auto-update                     | Auto-remove                  | ✅ Tested                |
| **Hermes Agent**              | Native tap + portable | `hermes skills tap add phenates/phenates-agents-plugins` (native) or `hermes plugins install ... --no-enable` (portable) | `tap update` or manual override | `tap remove` or manual       | 🔶 Portable format ready |
| **npx skills (Vercel)**       | CLI                   | `npx skills add phenates/phenates-agents-plugins`                                                                        | `npx skills update`             | `npx skills remove`          | ✅ Ready                 |
| **Generic Agent Plugins 1.0** | Direct reference      | Point client to this repository                                                                                        | Fetch latest on startup         | N/A                          | ✅ Compliant             |

## Installation by Platform

### Claude Code

Add from the marketplace:

```bash
/plugin marketplace add phenates-agents-plugins
```

List installed plugins:

```bash
/plugin marketplace list
```

Or discover in the plugin browser:

```bash
/plugin discover
```

### Claude Desktop (Cowork)

1. Go to **Settings → Plugins → Marketplace**
2. Search for `phenates-agents-plugins`
3. Click **Add**

Updates sync automatically.

### Hermes Agent

**Native tap (current):**

```bash
hermes skills tap add phenates/phenates-agents-plugins
hermes skills check
```

**Portable format (future):**

```bash
hermes plugins install https://github.com/phenates/phenates-agents-plugins --no-enable
```

### npx skills

```bash
npx skills add phenates/phenates-agents-plugins --list
```

### Generic Agent Plugins 1.0 Client

Point your client to this repository (branch: `main`):

```
https://github.com/phenates/phenates-agents-plugins
```

## Skills Included

| Skill                                       | Description                                                                                                                                                         | Status                                                                                  | Version |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------- |
| [`markdown-flavor`](skills/markdown-flavor) | House Markdown conventions plus Obsidian Flavored Markdown syntax (wikilinks, embeds, callouts, properties). Applies to any Markdown file, not just Obsidian notes. | Actively maintained                                                                     | v0.1.0  |
| [`obsidian-vault`](skills/obsidian-vault)   | Access and write to an Obsidian vault via MCP: tool mechanics, default save folder, vault organization, plugin-specific behavior.                                   | Actively maintained                                                                     | v0.1.0  |
| [`json-canvas`](skills/json-canvas)         | Create and edit JSON Canvas (`.canvas`) files.                                                                                                                      | Vendored from Kepano, unmodified                                                        | —       |
| [`obsidian-bases`](skills/obsidian-bases)   | Create and edit Obsidian Bases (`.base`) files.                                                                                                                     | Vendored from Kepano, unmodified                                                        | —       |
| [`obsidian-cli`](skills/obsidian-cli)       | Obsidian CLI interaction.                                                                                                                                           | Vendored from Kepano, not adopted (redundant with the Local REST API MCP server in use) | —       |

## Development

### Validation Workflow

A multi-level validation pipeline ensures both **Agent Plugins 1.0.0** (portable) and **Claude Code native** manifests remain compliant at all stages.

#### Level 1 — Local validation (on-demand)

Run all validators in one command:

```bash
./scripts/validate.sh
```

Validates:

- **Agent Plugins 1.0.0** — Schema compliance via `@hiai-gg/agent-plugins-doctor check`
- **Agent Plugins structure** — Plugin integrity and skills detection via `@hiai-gg/agent-plugins-builder inspect`
- **Claude Code native** — Marketplace manifest and plugin structure via `claude plugin validate --strict`

Exit code `0` = all pass; non-zero = at least one failed.

#### Level 2 — Pre-commit hook (automatic)

**Setup** (one-time, after clone):

```bash
bash -c '
cat > .git/hooks/pre-commit << '"'"'EOF'"'"'
#!/usr/bin/env bash
"$(cd "$(dirname "$0")/../.." && pwd)"/scripts/validate.sh
EOF
chmod +x .git/hooks/pre-commit
'
```

Or create `.git/hooks/pre-commit` manually pointing to `./scripts/validate.sh`.

Then `./scripts/validate.sh` runs automatically before each `git commit`. Commit is blocked if validation fails (bypass with `git commit --no-verify`, but not recommended).

**Note:** `.git/hooks/` is not version-controlled by Git, so each clone must install the hook independently. Contributors see setup instructions in this README.

#### Level 4 — GitHub Actions (on push/PR)

Runs the same validators on GitHub after each push and pull request to `main`, providing a final safety net. (Setup required separately in `.github/workflows/`.)

### Versioning

This repository follows a two-level versioning policy, each level independent of the other.

#### Skill versions

Each skill has its own SemVer version number (`version: X.Y.Z`) in its frontmatter.

- **MAJOR** — breaking change in the skill's frontmatter or behavior
- **MINOR** — new feature added to the skill
- **PATCH** — bug fix, rewording, no behavior change

#### Plugin version

The plugin as a whole has a single version in `.claude-plugin/plugin.json`, read identically by every platform that consumes this manifest.

Bumping this version is **not automatic**: it's decided case by case, when a set of changes deserves to be seen as a new release of the package — not on every individual skill bump.

- **MAJOR** — breaking change to the bundle structure (modified `mcp.json` schema, renamed/removed skill, folder reorganization)
- **MINOR** — new skill/agent/command added to the bundle, or an existing skill receives a MINOR/MAJOR bump
- **PATCH** — internal fix within a skill that only warrants a patch, metadata, documentation

#### Git tags

A `vX.Y.Z` tag is created only for plugin releases (a `plugin.json` bump) — not on every individual skill bump.

#### Changelog

All changes are tracked in a single [`CHANGELOG.md`](./CHANGELOG.md) at the repo root (following [Keep a Changelog](https://keepachangelog.com/)), with one entry per plugin version detailing which skills were touched and their new version.

#### Platform distribution

| Platform           | Behavior                                                     |
| ------------------ | ------------------------------------------------------------ |
| Claude Desktop     | Follows GitHub updates automatically via the plugin manifest |
| Hermes (`tap add`) | Reads each skill's version individually                      |
| npx skills         | Follows the repo's HEAD continuously, no pinned version      |

## License

This repository's own content (`markdown-flavor`, `obsidian-vault`) is MIT licensed -- see [LICENSE](LICENSE).

`json-canvas`, `obsidian-bases`, and `obsidian-cli` are vendored unmodified from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills), MIT licensed by kepano.

---

**Maintainer:** [phenates](https://github.com/phenates)
