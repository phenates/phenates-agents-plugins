#!/usr/bin/env python3
"""
check_skills.py — Validate skill frontmatter and its declaration in the Claude Code marketplace.

Component manifests are covered by agent-plugins-doctor / -builder and claude plugin validate.
This script covers the two gaps those tools leave open:

  * a SKILL.md whose frontmatter is broken, whose name does not match its directory, or whose
    description breaks the Agent Skills limits is silently ignored by every harness;
  * a skill directory that is absent from the marketplace entry's `skills` list is not offered
    by the npx skills picker, because that list drives the grouping.

Usage:
    python scripts/check_skills.py <repo-root>

Exit code 0 when no error is found. Warnings alone never fail the run.
"""

import json
import re
import sys
from pathlib import Path

# Frontmatter keys accepted by the Agent Skills spec and by the skills CLI.
ALLOWED_KEYS = {
    "name",
    "description",
    "version",
    "author",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}

KEBAB_CASE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024

errors = []
warnings = []
checked_skills = 0


def report(level, location, message):
    """Record a finding, keeping errors and warnings in separate buckets."""
    (errors if level == "ERROR" else warnings).append(f"  {location}: {message}")


def parse_frontmatter(text):
    """
    Extract the YAML frontmatter of a SKILL.md as a flat mapping.

    Only the shape used by skill files is supported: top-level `key: value` pairs, quoted or bare,
    plus folded/literal block scalars. Nested mappings are recorded as present but not parsed,
    which is enough to validate the keys this script cares about.
    """
    if not text.startswith("---"):
        return None, "missing YAML frontmatter"

    lines = text.replace("\r\n", "\n").split("\n")
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, "frontmatter block is not closed by a second '---'"

    fields = {}
    index = 1
    while index < end:
        line = lines[index]
        index += 1

        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] in " \t":  # nested value, belongs to the previous key
            continue

        if ":" not in line:
            return None, f"line {index} has no 'key: value' separator"

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        # Folded (>) and literal (|) block scalars: join the indented lines that follow.
        if value.startswith((">", "|")):
            block = []
            while index < end and (lines[index].startswith((" ", "\t")) or not lines[index].strip()):
                block.append(lines[index].strip())
                index += 1
            value = " ".join(part for part in block if part)

        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]

        fields[key] = value

    return fields, None


def check_skill(skill_dir, repo_root):
    """Validate one skill directory and return its declared name."""
    global checked_skills

    location = skill_dir.relative_to(repo_root).as_posix()
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        report("ERROR", location, "no SKILL.md found in this skill directory")
        return None

    checked_skills += 1
    fields, problem = parse_frontmatter(skill_md.read_text(encoding="utf-8"))

    if problem:
        report("ERROR", location, problem)
        return None

    for key in fields:
        if key not in ALLOWED_KEYS:
            report("WARN", location, f"unexpected frontmatter key '{key}'")

    name = fields.get("name", "")
    if not name:
        report("ERROR", location, "frontmatter is missing 'name'")
    elif not KEBAB_CASE.match(name):
        report("ERROR", location, f"name '{name}' is not kebab-case")
    elif len(name) > MAX_NAME_LENGTH:
        report("ERROR", location, f"name is {len(name)} characters, maximum is {MAX_NAME_LENGTH}")
    elif name != skill_dir.name:
        report("ERROR", location, f"name '{name}' does not match its directory '{skill_dir.name}'")

    description = fields.get("description", "")
    if not description:
        report("ERROR", location, "frontmatter is missing 'description'")
    else:
        if len(description) > MAX_DESCRIPTION_LENGTH:
            report(
                "ERROR",
                location,
                f"description is {len(description)} characters, maximum is {MAX_DESCRIPTION_LENGTH}",
            )
        if "<" in description or ">" in description:
            report("ERROR", location, "description cannot contain angle brackets")

    version = fields.get("version")
    if version is not None and not SEMVER.match(version):
        report("WARN", location, f"version '{version}' is not X.Y.Z")

    return name


def check_marketplace(repo_root, plugins_on_disk):
    """Compare the marketplace entries with what actually exists on disk."""
    manifest = repo_root / ".claude-plugin" / "marketplace.json"
    if not manifest.is_file():
        report("ERROR", ".claude-plugin", "marketplace.json not found")
        return

    try:
        entries = json.loads(manifest.read_text(encoding="utf-8")).get("plugins", [])
    except json.JSONDecodeError as exc:
        report("ERROR", ".claude-plugin/marketplace.json", f"invalid JSON: {exc}")
        return

    declared_sources = set()

    for entry in entries:
        entry_name = entry.get("name", "<unnamed>")
        source = entry.get("source")
        location = f"marketplace[{entry_name}]"

        if not isinstance(source, str) or not source.startswith("./"):
            report("ERROR", location, "source must be a relative path starting with './'")
            continue

        plugin_dir = (repo_root / source).resolve()
        declared_sources.add(plugin_dir)

        if not plugin_dir.is_dir():
            report("ERROR", location, f"source '{source}' does not exist")
            continue

        plugin_manifest = plugin_dir / "plugin.json"
        if not plugin_manifest.is_file():
            report("ERROR", location, f"source '{source}' has no plugin.json")
        else:
            try:
                plugin_name = json.loads(plugin_manifest.read_text(encoding="utf-8")).get("name")
            except json.JSONDecodeError as exc:
                report("ERROR", location, f"plugin.json is invalid JSON: {exc}")
                plugin_name = None
            if plugin_name and plugin_name != entry_name:
                report(
                    "WARN",
                    location,
                    f"name differs from plugin.json ('{plugin_name}'): the entry name wins as label",
                )

        declared = entry.get("skills")
        if declared is None:
            report("WARN", location, "no 'skills' list: its skills are not grouped in the picker")
            continue
        if not isinstance(declared, list) or not declared:
            report("ERROR", location, "'skills' must be a non-empty list of './skills/<name>' paths")
            continue

        # Resolve declared paths relative to the plugin root, as Claude Code does.
        declared_dirs = set()
        for declared_path in declared:
            if not isinstance(declared_path, str) or not declared_path.startswith("./"):
                report("ERROR", location, f"skill path '{declared_path}' must start with './'")
                continue
            resolved = (plugin_dir / declared_path).resolve()
            declared_dirs.add(resolved)
            if not (resolved / "SKILL.md").is_file():
                report(
                    "ERROR",
                    location,
                    f"declared skill '{declared_path}' has no SKILL.md (stale declaration)",
                )

        on_disk = {path.resolve() for path in (plugin_dir / "skills").glob("*") if path.is_dir()}
        for missing in sorted(on_disk - declared_dirs):
            report(
                "ERROR",
                location,
                f"skill '{missing.relative_to(plugin_dir).as_posix()}' exists but is not declared, "
                "so the picker does not offer it",
            )

    for plugin_dir in sorted(set(plugins_on_disk) - declared_sources):
        report(
            "WARN",
            plugin_dir.relative_to(repo_root).as_posix(),
            "plugin is not listed in the marketplace",
        )


def main():
    """Entry point: run every check and print a summary."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_skills.py <repo-root>")
        return 2

    # Findings may contain paths outside the console code page; replace instead of crashing.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    repo_root = Path(sys.argv[1]).resolve()

    plugins_on_disk = sorted(
        path.parent
        for path in repo_root.rglob("plugin.json")
        if ".claude-plugin" not in path.parts and ".git" not in path.parts
    )

    if not plugins_on_disk:
        report("ERROR", ".", "no plugin found: no plugin.json outside .claude-plugin/")

    for plugin_dir in plugins_on_disk:
        skills_dir = plugin_dir / "skills"
        if not skills_dir.is_dir():
            continue
        for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
            check_skill(skill_dir, repo_root)

    check_marketplace(repo_root, plugins_on_disk)

    for finding in warnings:
        print(f"[warn] {finding.strip()}")
    for finding in errors:
        print(f"[error] {finding.strip()}")

    print(f"\n{checked_skills} skills checked - {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
