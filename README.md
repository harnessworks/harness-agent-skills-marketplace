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
release `v0.1.14`.

## Install

### Codex Pinned Release

Add this marketplace to Codex pinned to this release:

```bash
codex plugin marketplace add harnessworks/harness-agent-skills-marketplace --ref v0.1.14
```

Restart Codex, open `/plugins`, select the `Harnessworks` marketplace, and
install `harness-agent-skills`. This is a reproducible release install. To move
to a later pinned release, run the same add command with the new release tag.

### Claude Code Pinned Release

Add this marketplace to Claude Code pinned to this release:

```bash
claude plugin marketplace add harnessworks/harness-agent-skills-marketplace@v0.1.14
claude plugin install harness-agent-skills@harnessworks
```

Use the router skill with the plugin namespace:

```text
/harness-agent-skills:harness doctor
```

### Moving Channel

If you want marketplace update commands to track the repository default branch
instead of a pinned release tag, add the marketplace without a ref:

```bash
codex plugin marketplace add harnessworks/harness-agent-skills-marketplace
claude plugin marketplace add harnessworks/harness-agent-skills-marketplace
```

## Update

For pinned installs, move to a newer release by re-running the marketplace add
command with the new tag, for example `v0.1.15`.

For moving-channel Codex installs, refresh the marketplace snapshot:

```bash
codex plugin marketplace upgrade harnessworks
```

For moving-channel Claude Code installs, refresh the marketplace and then update
the installed plugin:

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
python3 scripts/check_marketplace.py --source-agent-skills ../harness-starter-kit/agent-skills
claude plugin validate .
claude plugin validate plugins/harness-agent-skills
```

## Source Of Truth

Harness Starter Kit remains the source of truth for the package. Update
`agent-skills/` there first, run its package validation, tag a release, then
copy the released package into this marketplace repository.
