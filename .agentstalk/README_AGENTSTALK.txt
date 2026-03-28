# .agentstalk SOP

- Shared coordination surface for multi-agent tasks in this repo.
- Each progress item or issue uses its own file with a timestamp in the filename.
- Close resolved items by appending `_CLOSED` to the filename.
- Avoid duplicate writes: update your own item file when possible; only touch shared baselines intentionally.
- Keep `.agentstalk/Features` current as the canonical functional baseline.
- Use `.agentstalk/issues/` for open findings and `.agentstalk/progress/` for scan/progress snapshots.
- Historical snapshots can stay in `archive/` or `Features.md`, but `Features` is the active source of truth.
