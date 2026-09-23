# phenates-agents-plugins

**A single source of truth for personal agent skills, portable across coding-agent harnesses.**

This repository hosts one or more independent plugins. Each plugin is a folder containing an
[Agent Plugins 1.0.0](https://agent-plugins.org/) manifest (`plugin.json`) and a `skills/`
directory. The repository itself is **not** a plugin — every folder with its own `plugin.json` is
validated, installed, and versioned independently.

The distribution model is deliberately narrow: **[npx skills](https://skills.sh/) (Vercel) is the
only installation path**, targeting every Agent Skills-compatible harness in one command. Nothing
here is installed through a Claude Code marketplace — see [Why this
architecture](#why-this-architecture) for the reasoning.

## Ref documentation

- https://code.claude.com/docs/fr/plugins-reference
- https://agent-plugins.org/
- https://agentskills.io/home
- https://skills.sh/

## Repository layout

```
phenates-agents-plugins/
├── .claude-plugin/
│   └── marketplace.json              # Grouping metadata for the npx skills picker — see below
├── <plugin-name>/                    # One folder per plugin (Agent Plugins 1.0.0)
│   ├── plugin.json                   # Plugin manifest: name, version, author, license, keywords
│   └── skills/
│       └── <skill-name>/             # A distributable skill (Agent Skills spec)
│           ├── SKILL.md              # Required: name + description frontmatter, instructions
│           ├── scripts/, references/, assets/     # Optional skill payload
│           ├── .claude-plugin/
│           │   └── plugin.json       # Optional — see "Claude Code-only richness" below
│           ├── agents/                # Optional, Claude Code-only
│           ├── commands/              # Optional, Claude Code-only
│           ├── hooks/                 # Optional, Claude Code-only
│           └── .mcp.json              # Optional, Claude Code-only
├── scripts/
│   └── validate.sh                   # Validates every plugin + the marketplace manifest
├── LICENSE
└── README.md
```

There is no repository-level manifest: everything a plugin needs lives inside that plugin's own
folder, and everything a skill needs — including an optional Claude Code-only extension — lives
inside that skill's own folder.

## Why this architecture

Three deliberate choices, each solving a specific problem observed in practice while building this
repository.

### Why installation goes only through npx skills

Claude Code's `/plugin install` copies a plugin into
`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` — a path that changes on every update
(the previous version is kept for a grace period, then cleaned up). That's workable for Claude Code
in isolation, but it makes the installed files a moving target for anything reading them from
outside Claude Code. `npx skills` instead installs to a **stable, flat path**
(`~/.claude/skills/<name>/`, `~/.agents/skills/<name>/`, …) that never changes on update, and
targets every supported harness from a single command. That stability is why it is the only
supported install path here.

### Why `marketplace.json` still exists

Even without a Claude Code marketplace install, `.claude-plugin/marketplace.json` is not dead
weight: `npx skills` reads it to **group skills by plugin** in its interactive picker (each
`name` in the manifest becomes a group label in that picker). Its only remaining job is that
grouping — it is metadata for the installer's UX, not an installation channel.

### Claude Code-only richness, without breaking other harnesses

A skill can optionally carry more than a `SKILL.md`: a `.claude-plugin/plugin.json` dropped
_inside_ a skill's own folder turns that installed skill into a full [Claude Code skills-dir
plugin](https://code.claude.com/docs/fr/plugins-reference#skills-directory-plugins) — Claude Code
then also loads whatever `agents/`, `commands/`, `hooks/`, or `.mcp.json` sit next to it, no
marketplace or separate install step required beyond the normal `npx skills` install.

Every other harness that installs the same skill through `npx skills` (Kilo Code, Goose, …) simply
never looks inside `.claude-plugin/`, `agents/`, `commands/`, or `hooks/` — those paths aren't part
of the Agent Skills spec, so they are silently ignored rather than causing an error or a broken
install. The same physical files therefore serve as a full plugin for Claude Code and as a plain,
portable skill for everyone else, with zero duplication and zero cross-harness interference. This
was verified empirically, not assumed: a test skill carrying a nested `plugin.json`, a sub-agent,
and a `SKILL.md` installed cleanly everywhere, loaded fully (skill + sub-agent, namespaced) in
Claude Code, and loaded as a plain skill — extras silently ignored — in Kilo Code.

## Platform compatibility

| Platform                             | What it gets                                                                                                              | Status                   |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| **npx skills** (any supported agent) | Skills, flat and native — the install path for everything                                                                 | ✅ Tested                |
| **Claude Code** (CLI & Desktop)      | Skills, plus any Claude Code-only `agents/`/`commands/`/`hooks/`/MCP a skill carries, via the skills-dir plugin mechanism | ✅ Tested                |
| **Kilo Code**                        | Skills only — Claude Code-only extras are ignored, not broken (native support for the user's `skills/` directory)         | ✅ Tested                |
| **Goose**                            | Skills only — Claude Code-only extras are ignored, not broken (native support for the user's `skills/` directory)         | ✅ Tested                |
| **Hermes Agent**                     | Native tap or portable Agent Plugins install                                                                              | 🔶 Portable format ready |
| **Generic Agent Plugins 1.0 client** | Point it at a plugin folder                                                                                               | ✅ Compliant             |

## Installation

Everything goes through `npx skills`. No other install path is supported.

```bash
# Discover what's here without installing
npx skills add phenates/phenates-agents-plugins --list

# Install everything, globally, letting the CLI auto-detect installed agents
npx skills add phenates/phenates-agents-plugins -g

# Install specific skills, for specific agents
npx skills add phenates/phenates-agents-plugins --skill <skill-name> -g -a claude-code -a kilo-code -a goose

# List what's currently installed
npx skills list

# Update everything, or a specific skill
npx skills update
npx skills update <skill-name>

# Remove a skill
npx skills remove <skill-name>
```

Run `npx skills --help` for the full, current flag set — the CLI evolves faster than this README.

## Publishing a plugin or skill

### `<plugin>/plugin.json` — the plugin manifest

The Agent Plugins 1.0.0 manifest for that plugin. Validated by `agent-plugins-doctor` and
`agent-plugins-builder`. Keep `name`, `version`, `description`, `author`, `license`, and `keywords`
current.

### `.claude-plugin/marketplace.json` — grouping metadata

One entry per plugin:

```json
{
  "name": "<plugin-name>",
  "source": "./<plugin-name>",
  "skills": ["./skills/<skill-name>", "./skills/<other-skill-name>"],
  "description": "…",
  "category": "productivity",
  "author": { "name": "phenates" }
}
```

- `name` becomes the group label the npx skills picker shows for this plugin.
- `source` is the plugin directory, relative to the repository root.
- `skills` must list each skill directory **individually** — listing just `"./skills"` finds the
  skills but produces no group in the picker, and a skill that's neither listed here nor stored in
  a standard container (`skills/`, `.claude/skills/`, …) isn't offered at all.

### Checklist — new skill

1. `<plugin>/skills/<skill-name>/SKILL.md` with `name` and `description` frontmatter.
2. Add `"./skills/<skill-name>"` to that plugin's `skills` array in `marketplace.json`.
3. Optional Claude Code-only richness: add `.claude-plugin/plugin.json` (and `agents/`,
   `commands/`, `hooks/`, `.mcp.json` as needed) inside the skill's own folder.
4. Bump the plugin `version` when the change warrants a release.
5. Run `./scripts/validate.sh`.

### Checklist — new plugin

1. Create the plugin folder with `plugin.json` and `skills/`, and add it to `marketplace.json`.
2. Nothing else to change — `scripts/validate.sh` discovers plugins by looking for `plugin.json`
   outside `.claude-plugin/`.

## Development

### Validation

```bash
./scripts/validate.sh
```

Runs, for every plugin:

- **Agent Plugins 1.0.0** schema and structure compliance (`agent-plugins-doctor check`)
- **Agent Plugins 1.0.0** component detection (`agent-plugins-builder inspect`)
- **Skill frontmatter** checks (`scripts/check_skills.py`) — parsable frontmatter, `name` matching
  the directory, description within Agent Skills limits, no unexpected keys, SemVer `version` when
  present
- **Marketplace consistency** — every declared skill exists on disk, and every skill on disk is
  declared (an undeclared skill is invisible to the npx skills picker)
- `claude plugin validate --strict` on the whole marketplace

```bash
python scripts/check_skills.py .   # skill check on its own
```

Exit code `0` = everything passes; details print only on failure, except skill-check warnings,
which always show since they point at skills the picker won't offer.

### Pre-commit hook (optional)

```bash
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
exec "$(git rev-parse --show-toplevel)/scripts/validate.sh"
EOF
chmod +x .git/hooks/pre-commit
```

`.git/hooks/` isn't version-controlled — each clone installs it independently.
`git commit --no-verify` bypasses it.

### Continuous integration

Not set up yet. Intended: a GitHub Actions workflow on push/PR to `main` running
`./scripts/validate.sh`, so local and CI checks stay identical.

### Versioning

Two independent levels.

**Skill versions** — `version: X.Y.Z` in the skill's frontmatter, when the skill carries one.
MAJOR: breaking frontmatter/behavior change. MINOR: new capability. PATCH: fix or rewording.

**Plugin versions** — `version` in `<plugin>/plugin.json`, bumped deliberately, not automatically
on every skill change. MAJOR: breaking structural change (renamed/removed skill, reorganized
folders). MINOR: skill added, or an existing skill takes a MINOR/MAJOR bump. PATCH: internal fix,
metadata, documentation.

Git tags (`vX.Y.Z`) mark plugin releases.

## License

MIT — see [LICENSE](LICENSE). Some skills may vendor third-party content under their own license;
check that skill's own files when in doubt.

---

**Maintainer:** [phenates](https://github.com/phenates)
