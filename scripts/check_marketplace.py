#!/usr/bin/env python3
"""Validate the Harness Agent Skills marketplace package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "harness-agent-skills"
RELEASE_VERSION = "0.1.12"
REQUIRED_SKILLS = (
    "harness",
    "harness-adopt",
    "harness-doctor",
    "harness-refresh",
    "harness-review",
    "harness-update",
)
REFERENCE_RE = re.compile(r"\.\./\.\./references/[A-Za-z0-9._/-]+")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is invalid JSON: {exc}")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def validate_marketplace() -> Path:
    path = ROOT / "marketplace.json"
    require(path.exists(), "marketplace.json is missing")
    marketplace = load_json(path)

    require(marketplace.get("name") == "harnessworks", "marketplace name must be harnessworks")
    require(
        marketplace.get("interface", {}).get("displayName") == "Harnessworks",
        "marketplace interface.displayName must be Harnessworks",
    )

    plugins = marketplace.get("plugins")
    require(isinstance(plugins, list), "marketplace plugins must be a list")
    matches = [plugin for plugin in plugins if plugin.get("name") == PLUGIN_NAME]
    require(len(matches) == 1, f"marketplace must contain exactly one {PLUGIN_NAME} entry")

    entry = matches[0]
    require(entry.get("category") == "Productivity", "plugin category must be Productivity")
    require(
        entry.get("policy") == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "plugin policy must install on request and authenticate on install",
    )
    source = entry.get("source", {})
    require(source.get("source") == "local", "plugin source must be local")
    require(source.get("path") == f"./plugins/{PLUGIN_NAME}", "plugin source path is unexpected")

    plugin_root = (ROOT / source["path"]).resolve()
    require(plugin_root.is_dir(), f"plugin path does not exist: {source['path']}")
    require(ROOT.resolve() in plugin_root.parents, "plugin path must stay inside marketplace root")
    return plugin_root


def validate_plugin_manifest(plugin_root: Path) -> Path:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    require(manifest_path.exists(), "plugin manifest is missing")
    manifest = load_json(manifest_path)

    require(manifest.get("name") == PLUGIN_NAME, "plugin manifest name mismatch")
    require(manifest.get("version") == RELEASE_VERSION, f"plugin version must be {RELEASE_VERSION}")
    require(manifest.get("skills") == "./skills/", "plugin skills path must be ./skills/")
    require(manifest.get("license") == "MIT", "plugin license must be MIT")
    require("harness-starter-kit" in manifest.get("repository", ""), "plugin repository must point to starter kit")
    require(
        manifest.get("interface", {}).get("displayName") == "Harness Agent Skills",
        "plugin interface.displayName mismatch",
    )

    skills_root = plugin_root / "skills"
    require(skills_root.is_dir(), "plugin skills directory is missing")
    return skills_root


def validate_skill(skill_name: str, skills_root: Path) -> None:
    skill_path = skills_root / skill_name / "SKILL.md"
    require(skill_path.exists(), f"{skill_name}/SKILL.md is missing")
    text = skill_path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), f"{skill_name}/SKILL.md must start with frontmatter")
    require(f"name: {skill_name}\n" in text, f"{skill_name}/SKILL.md frontmatter name mismatch")
    require("description:" in text.split("---", 2)[1], f"{skill_name}/SKILL.md needs a description")

    refs = sorted(set(REFERENCE_RE.findall(text)))
    require(refs, f"{skill_name}/SKILL.md must reference bundled workflow docs")
    for ref in refs:
        ref_path = (skill_path.parent / ref).resolve()
        require(ref_path.exists(), f"{skill_name}/SKILL.md has missing reference: {ref}")


def validate_skills(skills_root: Path) -> None:
    actual = sorted(path.name for path in skills_root.iterdir() if path.is_dir())
    expected = sorted(REQUIRED_SKILLS)
    require(actual == expected, f"skill directories mismatch: expected {expected}, got {actual}")
    for skill_name in REQUIRED_SKILLS:
        validate_skill(skill_name, skills_root)


def main() -> None:
    plugin_root = validate_marketplace()
    skills_root = validate_plugin_manifest(plugin_root)
    validate_skills(skills_root)
    print("Marketplace package check passed.")


if __name__ == "__main__":
    main()
