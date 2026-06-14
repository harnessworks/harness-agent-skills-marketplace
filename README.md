# Harness Agent Skills Marketplace

Plugin marketplace for Harness Starter Kit's Universal Agent Skills package.

This marketplace publishes the `harness-agent-skills` plugin, which exposes the
prompt-first Harness Starter Kit workflows as portable Agent Skills for Codex
and Claude Code.

Codex skills:

- `$harness`
- `$harness-adopt`
- `$harness-doctor`
- `$harness-update`
- `$harness-refresh`
- `$harness-review`

Claude Code plugin skills are namespaced:

- `/harness-agent-skills:harness`
- `/harness-agent-skills:harness-adopt`
- `/harness-agent-skills:harness-doctor`
- `/harness-agent-skills:harness-update`
- `/harness-agent-skills:harness-refresh`
- `/harness-agent-skills:harness-review`

The plugin is copied from
[`harnessworks/harness-starter-kit`](https://github.com/harnessworks/harness-starter-kit)
release `v0.1.13`.

## Install

### Codex

Add this marketplace to Codex:

```bash
codex plugin marketplace add harnessworks/harness-agent-skills-marketplace --ref v0.1.13
```

Restart Codex, open `/plugins`, select the `Harnessworks` marketplace, and
install `harness-agent-skills`.

### Claude Code

Add this marketplace to Claude Code:

```bash
claude plugin marketplace add harnessworks/harness-agent-skills-marketplace@v0.1.13
claude plugin install harness-agent-skills@harnessworks
```

Use the router skill with the plugin namespace:

```text
/harness-agent-skills:harness doctor
```

## Update

To update an installed Codex marketplace snapshot after a new release:

```bash
codex plugin marketplace upgrade harnessworks
```

To update an installed Claude Code marketplace snapshot after a new release:

```bash
claude plugin marketplace update harnessworks
claude plugin update harness-agent-skills@harnessworks
```

Then restart the agent runtime, or reload plugins where the runtime supports it.

## Package Structure

```text
.claude-plugin/
  marketplace.json
marketplace.json
plugins/
  harness-agent-skills/
    .claude-plugin/plugin.json
    .codex-plugin/plugin.json
    references/
    skills/
```

## Validation

Validate the marketplace package before tagging a release:

```bash
python3 scripts/check_marketplace.py
claude plugin validate .
claude plugin validate plugins/harness-agent-skills
```

## Source Of Truth

Harness Starter Kit remains the source of truth for the package. Update
`agent-skills/` there first, run its package validation, tag a release, then
copy the released package into this marketplace repository.
