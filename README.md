# phenates-agents-plugins

**A plugin store for AI coding agents.** This repository hosts several independent plugins, each one
portable across Agent Plugins 1.0.0 clients (Claude Code, Claude Desktop, Hermes Agent, and other
compatible frameworks) and published through a single Claude Code marketplace.

The repository itself is **not** a plugin. Every folder that contains a `plugin.json` is a plugin in
its own right: it is validated, installed, versioned, and released independently of the others.

## Ref documentation

- https://code.claude.com/docs/fr/plugins-reference
- https://agent-plugins.org/
- https://agentskills.io/home

## Plugins in this repository

| Plugin                                                   | Purpose                                         | Skills | Version | Status    |
| -------------------------------------------------------- | ----------------------------------------------- | ------ | ------- | --------- |
| [`markdown-obsidian-toolkit`](markdown-obsidian-toolkit) | Markdown notes and Obsidian knowledge artifacts | 5      | `0.1.1` | ✅ Tested |
| [`dev-general`](dev-general)                             | General development tooling                     | 2      | `0.1.0` | ✅ Tested |

### Skills

| Skill                                                                 | Plugin                    | Version | Origin                         |
| --------------------------------------------------------------------- | ------------------------- | ------- | ------------------------------ |
| [`markdown-flavor`](markdown-obsidian-toolkit/skills/markdown-flavor) | markdown-obsidian-toolkit | `0.1.0` | This repository                |
| [`obsidian-vault`](markdown-obsidian-toolkit/skills/obsidian-vault)   | markdown-obsidian-toolkit | `0.1.0` | This repository                |
| [`json-canvas`](markdown-obsidian-toolkit/skills/json-canvas)         | markdown-obsidian-toolkit | —       | Vendored (kepano, unmodified)  |
| [`obsidian-bases`](markdown-obsidian-toolkit/skills/obsidian-bases)   | markdown-obsidian-toolkit | —       | Vendored (kepano, unmodified)  |
| [`obsidian-cli`](markdown-obsidian-toolkit/skills/obsidian-cli)       | markdown-obsidian-toolkit | —       | Vendored (kepano, not adopted) |
| [`code-explain`](dev-general/skills/code-explain)                     | dev-general               | —       | This repository                |
| [`doc-generate`](dev-general/skills/doc-generate)                     | dev-general               | —       | This repository                |

Skills that carry no `version` in their frontmatter are not versioned individually: vendored skills
stay untouched by design, and new plugins may adopt per-skill versions later.

## Repository layout

```
phenates-agents-plugins/
├── .claude-plugin/
│   └── marketplace.json          # Claude Code marketplace: one entry per plugin, plus its skill list
├── markdown-obsidian-toolkit/    # Plugin (Agent Plugins 1.0.0)
│   ├── plugin.json               # Plugin manifest: name, version, author, license, keywords
│   └── skills/
│       ├── markdown-flavor/      # House Markdown conventions + Obsidian Flavored Markdown
│       ├── obsidian-vault/       # Obsidian vault access via MCP
│       ├── obsidian-cli/         # Obsidian CLI integration
│       ├── obsidian-bases/       # Obsidian Bases (.base) editing
│       └── json-canvas/          # JSON Canvas (.canvas) editing
├── dev-general/                  # Plugin (Agent Plugins 1.0.0)
│   ├── plugin.json
│   └── skills/
│       ├── code-explain/         # Code explanation and analysis
│       └── doc-generate/         # Documentation generation from a codebase
├── scripts/
│   └── validate.sh               # Validates every plugin + the marketplace
├── plan-test-multiplateforme.md  # Multi-platform test plan (working document)
├── LICENSE                       # MIT
└── README.md                     # This file
```

There is no repository-level manifest: agents, commands, MCP servers, LSP servers, hooks, or other
components a plugin needs go inside that plugin's own folder.

## Platform compatibility

| Platform                      | Mechanism             | Status                   |
| ----------------------------- | --------------------- | ------------------------ |
| **Claude Code**               | Marketplace           | ✅ Tested                |
| **Claude Desktop (Cowork)**   | Marketplace UI        | ✅ Tested                |
| **npx skills (Vercel)**       | CLI, grouped picker   | ✅ Tested                |
| **Hermes Agent**              | Native tap + portable | 🔶 Portable format ready |
| **Generic Agent Plugins 1.0** | Point at a plugin     | ✅ Compliant             |

## Installation

### Claude Code

```bash
/plugin marketplace add phenates/phenates-agents-plugins
/plugin install markdown-obsidian-toolkit@phenates-plugins
/plugin install dev-general@phenates-plugins
```

The marketplace is `phenates-plugins`; each plugin is installed independently. Browse with
`/plugin discover`, then open the **Marketplaces** tab to update or remove.

### Claude Desktop (Cowork)

1. Go to **Settings → Plugins**
2. Search for `markdown-obsidian-toolkit` or `dev-general`
3. Click **Add**

Updates sync automatically.

### npx skills

```bash
# List the skills of every plugin
npx skills add phenates/phenates-agents-plugins --list

# Install one skill, globally, for a specific agent
npx skills add phenates/phenates-agents-plugins --skill markdown-flavor -g -a claude-code
```

The picker groups skills by plugin, using the plugin names from the marketplace manifest (see
[Publishing a plugin](#publishing-a-plugin)).

### Hermes Agent

```bash
hermes skills tap add phenates/phenates-agents-plugins        # native tap
hermes plugins install https://github.com/phenates/phenates-agents-plugins --no-enable   # portable
```

### Generic Agent Plugins 1.0 client

Point your client at the **plugin directory**, not at the repository root:

```
https://github.com/phenates/phenates-agents-plugins/tree/main/markdown-obsidian-toolkit
```

## Publishing a plugin

Two manifests are involved, and only one of them lives at the repository root.

### `<plugin>/plugin.json` — the plugin manifest

The Agent Plugins 1.0.0 manifest of that plugin. This is what a portable client reads, and what the
`agent-plugins-doctor` and `agent-plugins-builder` tools validate. Keep `name`, `version`,
`description`, `author`, `license`, and `keywords` up to date.

### `.claude-plugin/marketplace.json` — the marketplace

A single marketplace named `phenates-plugins`, with one entry per plugin:

```json
{
  "name": "markdown-obsidian-toolkit",
  "source": "./markdown-obsidian-toolkit",
  "skills": ["./skills/json-canvas", "./skills/markdown-flavor"],
  "description": "…",
  "category": "productivity",
  "author": { "name": "phenates" }
}
```

- `name` is both the plugin identifier for Claude Code and the **group label** shown in the npx
  skills picker (`markdown-obsidian-toolkit` renders as _Markdown Obsidian Toolkit_).
- `source` is the plugin directory, relative to the repository root.
- `skills` lists each skill directory of the plugin, relative to the plugin root.

The `skills` list drives the grouping in the npx skills picker. Two constraints, both verified
against the CLI:

- Listing the container (`"./skills"`) finds the skills but produces **no group**: every skill
  directory must be listed individually.
- A skill that is neither listed here nor stored in a standard container (`skills/`,
  `.claude/skills/`, …) is not offered at all.

### Checklist for a new skill

1. Create `<plugin>/skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter.
2. Add `"./skills/<skill-name>"` to that plugin's `skills` array in `.claude-plugin/marketplace.json`.
3. Bump the plugin `version` when the change warrants a release.
4. Run `./scripts/validate.sh`.

### Checklist for a new plugin

1. Create the plugin folder with `plugin.json` and `skills/`, and add the plugin to
   `.claude-plugin/marketplace.json`.
2. Nothing else to change: `scripts/validate.sh` discovers plugins by looking for `plugin.json`
   outside `.claude-plugin/`, so no validator entry has to be added.

## Development

### Validation

```bash
./scripts/validate.sh
```

For every plugin in the repository, the script runs:

- **Agent Plugins 1.0.0** — schema and structure compliance via `@hiai-gg/agent-plugins-doctor check`
- **Agent Plugins 1.0.0** — component detection via `@hiai-gg/agent-plugins-builder inspect`

It then checks the skills and the marketplace manifest:

- **Skill frontmatter** — `scripts/check_skills.py` verifies each `SKILL.md` has parsable
  frontmatter with a `name` matching its directory, a `description` within the Agent Skills limits,
  no unexpected keys, and a SemVer `version` when one is set.
- **Marketplace consistency** — the same script compares each entry's `skills` list with the skill
  directories on disk, and reports both directions: a declared skill that no longer exists, and a
  skill that exists but is not declared (which the picker would not offer).

Finally, the whole marketplace goes through `claude plugin validate --strict`.

The skill check is also usable on its own:

```bash
python scripts/check_skills.py .
```

Details are printed only when a check fails, except for the skill check, whose warnings are always
shown because they point at skills the picker will not offer. Exit code `0` = everything passes.

### Pre-commit hook (optional)

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
exec "$(git rev-parse --show-toplevel)/scripts/validate.sh"
EOF
chmod +x .git/hooks/pre-commit
```

`.git/hooks/` is not version-controlled, so every clone installs it independently. Commits are
blocked while validation fails; `git commit --no-verify` bypasses it.

### Continuous integration

Not set up yet. The intended setup is a GitHub Actions workflow on push and pull request to `main`
that runs `./scripts/validate.sh`, so the local and CI checks stay identical.

### Versioning

Two independent levels.

**Skill versions** — `version: X.Y.Z` in the skill's frontmatter, when the skill carries one.

- MAJOR: breaking change in the skill's frontmatter or behavior
- MINOR: new capability
- PATCH: fix or rewording, no behavior change

**Plugin versions** — `version` in `<plugin>/plugin.json`. Bumping is a deliberate decision, not a
side effect of a skill bump.

- MAJOR: breaking change to the plugin structure (renamed or removed skill, reorganized folders)
- MINOR: skill added, or an existing skill takes a MINOR/MAJOR bump
- PATCH: internal fix, metadata, documentation

Git tags (`vX.Y.Z`) mark plugin releases only. A `CHANGELOG.md` at the repository root is planned
(following [Keep a Changelog](https://keepachangelog.com/)), with one entry per plugin release; it does
not exist yet.

### Distribution behaviour

| Platform           | Version behaviour                                             |
| ------------------ | ------------------------------------------------------------- |
| Claude Code        | Follows the repository, one plugin per marketplace entry      |
| Claude Desktop     | Follows GitHub updates automatically through the plugin entry |
| Hermes (`tap add`) | Reads each skill's version individually                       |
| npx skills         | Follows the repository HEAD continuously, no pinned version   |

## License

MIT — see [LICENSE](LICENSE).

`json-canvas`, `obsidian-bases`, and `obsidian-cli` are vendored unmodified from
[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills), MIT licensed by kepano.

---

**Maintainer:** [phenates](https://github.com/phenates)
