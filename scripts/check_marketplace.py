#!/usr/bin/env python3
"""Validate the Harness Agent Skills marketplace package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "harness-agent-skills"
RELEASE_VERSION = "0.1.13"
REQUIRED_SKILLS = (
    "harness",
    "harness-adopt",
    "harness-doctor",
    "harness-refresh",
    "harness-review",
    "harness-update",
)
REFERENCE_RE = re.compile(r"\.\./\.\./references/[A-Za-z0-9._/-]+")
README_REQUIRED_PHRASES = (
    "Codex Pinned Release",
    "Claude Code Pinned Release",
    "Moving Channel",
    "re-running the marketplace add",
)


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


def validate_codex_marketplace() -> Path:
    path = ROOT / "marketplace.json"
    require(path.exists(), "Codex marketplace.json is missing")
    marketplace = load_json(path)

    require(marketplace.get("name") == "harnessworks", "Codex marketplace name must be harnessworks")
    require(
        marketplace.get("interface", {}).get("displayName") == "Harnessworks",
        "Codex marketplace interface.displayName must be Harnessworks",
    )

    plugins = marketplace.get("plugins")
    require(isinstance(plugins, list), "Codex marketplace plugins must be a list")
    matches = [plugin for plugin in plugins if plugin.get("name") == PLUGIN_NAME]
    require(len(matches) == 1, f"Codex marketplace must contain exactly one {PLUGIN_NAME} entry")

    entry = matches[0]
    require(entry.get("category") == "Productivity", "Codex plugin category must be Productivity")
    require(
        entry.get("policy") == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "Codex plugin policy must install on request and authenticate on install",
    )
    source = entry.get("source", {})
    require(source.get("source") == "local", "Codex plugin source must be local")
    require(source.get("path") == f"./plugins/{PLUGIN_NAME}", "Codex plugin source path is unexpected")

    plugin_root = (ROOT / source["path"]).resolve()
    require(plugin_root.is_dir(), f"Codex plugin path does not exist: {source['path']}")
    require(ROOT.resolve() in plugin_root.parents, "Codex plugin path must stay inside marketplace root")
    return plugin_root


def validate_claude_marketplace() -> Path:
    path = ROOT / ".claude-plugin" / "marketplace.json"
    require(path.exists(), "Claude marketplace catalog is missing")
    marketplace = load_json(path)

    require(marketplace.get("name") == "harnessworks", "Claude marketplace name must be harnessworks")
    require(
        marketplace.get("owner", {}).get("name") == "Harnessworks",
        "Claude marketplace owner.name must be Harnessworks",
    )
    require(marketplace.get("version") == RELEASE_VERSION, f"Claude marketplace version must be {RELEASE_VERSION}")
    require(marketplace.get("description"), "Claude marketplace description is required")

    plugins = marketplace.get("plugins")
    require(isinstance(plugins, list), "Claude marketplace plugins must be a list")
    matches = [plugin for plugin in plugins if plugin.get("name") == PLUGIN_NAME]
    require(len(matches) == 1, f"Claude marketplace must contain exactly one {PLUGIN_NAME} entry")

    entry = matches[0]
    require(entry.get("source") == f"./plugins/{PLUGIN_NAME}", "Claude plugin source path is unexpected")
    require(entry.get("displayName") == "Harness Agent Skills", "Claude plugin displayName mismatch")
    require(entry.get("category") == "Productivity", "Claude plugin category must be Productivity")
    require("version" not in entry, "Claude marketplace entry should not duplicate plugin.json version")

    plugin_root = (ROOT / entry["source"]).resolve()
    require(plugin_root.is_dir(), f"Claude plugin path does not exist: {entry['source']}")
    require(ROOT.resolve() in plugin_root.parents, "Claude plugin path must stay inside marketplace root")
    return plugin_root


def validate_codex_plugin_manifest(plugin_root: Path) -> Path:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    require(manifest_path.exists(), "Codex plugin manifest is missing")
    manifest = load_json(manifest_path)

    require(manifest.get("name") == PLUGIN_NAME, "Codex plugin manifest name mismatch")
    require(manifest.get("version") == RELEASE_VERSION, f"Codex plugin version must be {RELEASE_VERSION}")
    require(manifest.get("skills") == "./skills/", "Codex plugin skills path must be ./skills/")
    require(manifest.get("license") == "MIT", "Codex plugin license must be MIT")
    require("harness-starter-kit" in manifest.get("repository", ""), "Codex plugin repository must point to starter kit")
    require(
        manifest.get("interface", {}).get("displayName") == "Harness Agent Skills",
        "Codex plugin interface.displayName mismatch",
    )

    skills_root = plugin_root / "skills"
    require(skills_root.is_dir(), "plugin skills directory is missing")
    return skills_root


def validate_claude_plugin_manifest(plugin_root: Path) -> Path:
    manifest_path = plugin_root / ".claude-plugin" / "plugin.json"
    require(manifest_path.exists(), "Claude plugin manifest is missing")
    manifest = load_json(manifest_path)

    require(manifest.get("name") == PLUGIN_NAME, "Claude plugin manifest name mismatch")
    require(manifest.get("displayName") == "Harness Agent Skills", "Claude plugin displayName mismatch")
    require(manifest.get("version") == RELEASE_VERSION, f"Claude plugin version must be {RELEASE_VERSION}")
    require(manifest.get("license") == "MIT", "Claude plugin license must be MIT")
    require("harness-starter-kit" in manifest.get("repository", ""), "Claude plugin repository must point to starter kit")
    require("claude-code" in manifest.get("keywords", []), "Claude plugin keywords must include claude-code")

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


def validate_readme() -> None:
    readme = ROOT / "README.md"
    require(readme.exists(), "README.md is missing")
    text = readme.read_text(encoding="utf-8")
    for phrase in README_REQUIRED_PHRASES:
        require(phrase in text, f"README.md must explain marketplace update semantics: {phrase}")


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_files(path: Path) -> dict[str, Path]:
    return {
        str(child.relative_to(path)): child
        for child in path.rglob("*")
        if child.is_file()
    }


def compare_trees(expected: Path, actual: Path) -> None:
    expected_files = tree_files(expected)
    actual_files = tree_files(actual)

    missing = sorted(set(expected_files) - set(actual_files))
    extra = sorted(set(actual_files) - set(expected_files))
    changed = sorted(
        relative
        for relative in set(expected_files) & set(actual_files)
        if file_hash(expected_files[relative]) != file_hash(actual_files[relative])
    )

    if missing or extra or changed:
        details: list[str] = []
        if missing:
            details.append(f"missing from marketplace: {missing}")
        if extra:
            details.append(f"extra in marketplace: {extra}")
        if changed:
            details.append(f"different files: {changed}")
        fail(
            "marketplace plugin does not match source package at "
            f"{expected}: {'; '.join(details)}"
        )


def validate_source_parity(source_agent_skills: Path | None, plugin_root: Path) -> None:
    if source_agent_skills is None:
        return
    source = source_agent_skills.resolve()
    require(source.is_dir(), f"source agent-skills path does not exist: {source}")
    compare_trees(source, plugin_root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-agent-skills",
        type=Path,
        help="Optional path to the source starter-kit agent-skills directory to compare against the packaged plugin.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    codex_plugin_root = validate_codex_marketplace()
    claude_plugin_root = validate_claude_marketplace()
    require(codex_plugin_root == claude_plugin_root, "Codex and Claude marketplaces must point to the same plugin")
    skills_root = validate_codex_plugin_manifest(codex_plugin_root)
    claude_skills_root = validate_claude_plugin_manifest(claude_plugin_root)
    require(skills_root == claude_skills_root, "Codex and Claude plugin manifests must share the same skills directory")
    validate_skills(skills_root)
    validate_readme()
    validate_source_parity(args.source_agent_skills, codex_plugin_root)
    print("Marketplace package check passed.")


if __name__ == "__main__":
    main()
