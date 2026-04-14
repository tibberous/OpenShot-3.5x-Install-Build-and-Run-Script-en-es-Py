# Contributing

Thanks for taking the time to improve **OpenShot BnR**.

## What good contributions look like

Good contributions reduce friction, improve repeatability, or make the project easier to inspect and extend. That includes:

- build fixes
- launcher/runtime fixes
- documentation improvements
- packaging and distribution work
- better logging and diagnostics
- cleaner Windows/MSYS2 automation

## Ground rules

- Keep the script readable. If a change is clever but harder to audit, it is probably worse.
- Prefer truthful output over optimistic output.
- Do not hide failures behind vague success messaging.
- Keep docs in sync with code. If behavior changes, update the visible help.
- Preserve the project's practical tone: this repo exists to save time and reduce setup waste.

## Before you open a pull request

1. Run the script through a syntax check.
2. Test any new CLI switches you add.
3. Update `README.md`, `INSTALL.md`, or `help.html` if the user-facing behavior changed.
4. Add a changelog entry for notable visible changes.
5. Include logs or screenshots when reporting a runtime or packaging issue.

## Suggested issue report format

- Windows version
- Python version
- MSYS2 path / shell used
- exact command run
- stage that failed
- relevant log excerpt
- whether the failure happened in build mode, launch mode, portable mode, or frozen mode

## Pull request notes

Small, focused pull requests are easier to review than giant mixed passes.

If you are changing launch/bootstrap behavior, explain:
- what failed before
- what you changed
- how you tested it
- what still is not proven yet
