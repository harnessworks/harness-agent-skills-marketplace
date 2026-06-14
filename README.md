# Harness Agent Skills Marketplace

Codex plugin marketplace for Harness Starter Kit's Universal Agent Skills
package.

This marketplace publishes the `harness-agent-skills` plugin, which exposes the
prompt-first Harness Starter Kit workflows as portable Agent Skills for Codex:

- `$harness`
- `$harness-adopt`
- `$harness-doctor`
- `$harness-update`
- `$harness-refresh`
- `$harness-review`

The plugin is copied from
[`harnessworks/harness-starter-kit`](https://github.com/harnessworks/harness-starter-kit)
release `v0.1.12`.

## Install

Add this marketplace to Codex:

```bash
codex plugin marketplace add harnessworks/harness-agent-skills-marketplace --ref v0.1.12
```

Restart Codex, open `/plugins`, select the `Harnessworks` marketplace, and
install `harness-agent-skills`.

## Update

To update an installed marketplace snapshot after a new release:

```bash
codex plugin marketplace upgrade harnessworks
```

Then restart Codex so the updated plugin package is discovered.

## Package Structure

```text
marketplace.json
plugins/
  harness-agent-skills/
    .codex-plugin/plugin.json
    references/
    skills/
```

## Validation

Validate the marketplace package before tagging a release:

```bash
python3 scripts/check_marketplace.py
```

## Source Of Truth

Harness Starter Kit remains the source of truth for the package. Update
`agent-skills/` there first, run its package validation, tag a release, then
copy the released package into this marketplace repository.
