# Repository Rename Plan

Last updated: 2026-05-28

This document tracks the Atom01 -> RPO / Roboparty repository naming migration.
The top-level aggregation repository remains `roboto_origin`.

## Current Decision

- `roboto_origin` stays as the public aggregation repository.
- Product-specific repositories use `rpo_*`.
- Shared framework repositories use `roboparty_*`.
- Forked or vendored upstream projects keep upstream names and license notices.
- Top-level `modules/...` snapshot paths use target public repository names.
- `.scripts/` remains a local operations directory and is not tracked by git.
- All future top-level changes must go through `dev -> PR -> main`.

## Stop Rules

- Do not delete repositories.
- Do not recreate old repository names as placeholder repositories, because that breaks GitHub rename redirects.
- Do not force-push `main`.
- Do not directly push naming migration changes to `main`.
- Do not globally replace `atom01` inside code without checking runtime interfaces, file paths, ROS package names, model names, and training/deployment compatibility.

## Repository Status

This public plan intentionally does not list individual staff names. Internal
ownership should be tracked in private project management channels.

| Old repository | New repository | Status | Notes |
| --- | --- | --- | --- |
| `Atom01_hardware` | `rpo_hardware` | Done | GitHub repo renamed. Snapshot path migrated to `modules/rpo_hardware`. |
| `atom01_appearance` | `rpo_appearance` | Done | GitHub repo renamed. Snapshot path migrated to `modules/rpo_appearance`; STL filenames kept for compatibility. |
| `atom01_description` | `rpo_description` | Done, needs confirmation | GitHub repo rename observed. Snapshot path migrated to `modules/rpo_description`; internal model/path migration status needs confirmation. |
| `atom01_deploy` | `roboparty_deploy` | Done, needs confirmation | GitHub repo rename observed. Snapshot path migrated to `modules/roboparty_deploy`; RPO-specific configs should remain documented as the current default. |
| `atom01_firmware` | `roboparty_firmware` | Done, needs confirmation | GitHub repo rename observed. Snapshot path migrated to `modules/roboparty_firmware`; forked/vendor code must preserve upstream names and licenses. |
| `atom01_train` | `roboparty_train` | Done, needs confirmation | GitHub repo rename observed. Snapshot path migrated to `modules/roboparty_train`; RPO-specific training assets should move under explicit product paths over time. |
| `atom01_navigation` | `roboparty_navigation` | Done, needs confirmation | GitHub repo rename observed. Snapshot path added at `modules/roboparty_navigation`; default branch is `master`. |
| `Atom_xr_teleop` | `roboparty_xr_teleop` | Done, needs confirmation | GitHub repo renamed. Snapshot path migrated to `modules/roboparty_xr_teleop`; internal package/path migration status needs confirmation. |

## Migration Phases

### Phase 0: Freeze

- Pause additional repository renames until this plan is reviewed.
- Record current repository names, owners, and redirect behavior.
- Create `dev` branch for `roboto_origin`.

### Phase 1: Repository Rename

- Repository owners rename their repositories through GitHub Settings.
- Owners update README clone/install URLs.
- Owners keep old runtime interfaces compatible unless a migration note and fallback are provided.
- Owners report the new URL and any internal breaking changes.

### Phase 2: Top-Level Aggregation Update

Tracked repository changes below happen on `roboto_origin/dev` first:

- Update `README.md` and `README_cn.md`.
- Update this public migration plan if repository status changes.
- Open a PR from `dev` to `main`.

Local operations changes are kept outside git:

- Update `.scripts/sync_subtrees.sh` locally if subtree source URLs change.
- Keep any local sync notes under `.scripts/logs/` if needed.
- Do not reference untracked `.scripts/` changes as reviewed PR content.

### Phase 3: Internal Package And Runtime Migration

This phase is optional and must be handled with separate PRs:

- Keep top-level `modules/...` snapshot paths aligned with target public repository names.
- Migrate internal package names, scripts, model files, ROS package names, and runtime paths only after each sub-repository owner confirms the compatibility plan.
- Provide compatibility aliases or clear migration notes when paths, scripts, model files, or ROS package names change.
- Validate at least the minimal documented build or usage path for each affected repository.

## Main Branch Policy

Target policy for `roboto_origin` and critical sub-repositories:

- `main` is stable and public-facing.
- `dev` is the integration branch.
- Changes merge through pull requests.
- At least one review is required before merging to `main`.
- Force pushes to `main` are disabled.
- Repository synchronization runs from reviewed branches, not ad-hoc local main changes.

## Communication Template

```text
This is a naming migration from the historical Atom01 naming to the RPO / Roboparty naming system.
The top-level roboto_origin repository remains unchanged.
Old GitHub URLs continue to redirect after repository rename.

Process issue acknowledged: some repository renames landed before a shared dev/PR workflow was established.
We are pausing further renames, creating a dev branch, recording the migration plan, and moving future top-level updates through dev -> PR -> main.
```
