# OpenShot BnR 1.0

**OpenShot BnR** is a Windows-first **install, build, run, and distro-prep** script for OpenShot 3.5.x.

It exists for one reason: to turn a fragile manual setup into a readable, repeatable workflow you can inspect, rerun, adapt, and eventually distribute.

## Project status

**Status:** release candidate / active polish  
**Audience:** Windows users, builders, tinkerers, consultants, and anyone tired of rebuilding the same environment from scratch  
**Goal:** get from a stock Windows machine to a real OpenShot launch with honest logs and useful artifacts

## What it does

- checks elevation, WinGet, Git, and MSYS2
- refreshes MSYS2 and resolves live package dependencies
- clones or updates:
  - `libopenshot-audio`
  - `libopenshot`
  - `openshot-qt`
- builds the native stack in order
- verifies Python bindings honestly in installed and source-build modes
- patches and bootstraps the runtime launch path
- generates launcher, portable, and frozen helper files
- exposes repo docs and diagnostic output from the command line


## Run examples

```bash
py -3 OpenShot_BnR_v1_0.py
py -3 OpenShot_BnR_v1_0.py --usage
py -3 OpenShot_BnR_v1_0.py --about
py -3 OpenShot_BnR_v1_0.py --version
py -3 OpenShot_BnR_v1_0.py --debug
cmd /c "C:\OpenShotBuild\Launch-OpenShot-Qt.cmd"
py -3 "C:\OpenShotBuild\Launch-OpenShot-Qt.py"
```

## Extra docs

- [INSTALL.md](INSTALL.md) — install and workflow notes
- [MANUAL_INSTALL.md](MANUAL_INSTALL.md) — manual package URLs, what each package does, and why it exists
- [LOG_GUIDE.md](LOG_GUIDE.md) — successful log walkthrough and stage-by-stage explanation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — permissions, manual install, runtime, and packaging fallback tips
- [RELEASE_GUIDE.md](RELEASE_GUIDE.md) — release-candidate checklist and ship criteria


## Official project links

- Project website: https://www.trentontompkins.com
- Project repository: https://github.com/tibberous/OpenShot-3.5x-Install-Build-and-Run-Script-en-es-Py-add
- OpenShot developer docs: https://www.openshot.org/static/files/user-guide/developers.html
- OpenShot downloads: https://www.openshot.org/download/

## Direct fetch examples

```bash
git clone https://github.com/tibberous/OpenShot-3.5x-Install-Build-and-Run-Script-en-es-Py-add
curl -L -o OpenShot_BnR.zip https://github.com/tibberous/OpenShot-3.5x-Install-Build-and-Run-Script-en-es-Py-add/archive/refs/heads/main.zip
```

## Why it matters

Manual setup looks cheap until you count retries, stale docs, wrong shells, missing paths, and vague launcher errors. OpenShot BnR compresses that waste.

Open source compounds. You can inspect it, extend it, automate it, and make it fit your own workflow instead of bending around somebody else’s defaults.

## Quick start

```bash
py -3 OpenShot_BnR_v1_0.py
```

Then let the script elevate, resolve dependencies, build the OpenShot stack, verify the bindings, and generate the launch helpers.


## Information commands

```bash
py -3 OpenShot_BnR_v1_0.py --usage
py -3 OpenShot_BnR_v1_0.py --help
py -3 OpenShot_BnR_v1_0.py man
py -3 OpenShot_BnR_v1_0.py --about
py -3 OpenShot_BnR_v1_0.py --version
py -3 OpenShot_BnR_v1_0.py --docs
py -3 OpenShot_BnR_v1_0.py --readme
py -3 OpenShot_BnR_v1_0.py --install
py -3 OpenShot_BnR_v1_0.py --manual-install
py -3 OpenShot_BnR_v1_0.py --log-guide
py -3 OpenShot_BnR_v1_0.py --troubleshoot
py -3 OpenShot_BnR_v1_0.py --release-guide
py -3 OpenShot_BnR_v1_0.py --changelog
py -3 OpenShot_BnR_v1_0.py --contributing
py -3 OpenShot_BnR_v1_0.py --security
py -3 OpenShot_BnR_v1_0.py --code-of-conduct
py -3 OpenShot_BnR_v1_0.py --license
py -3 OpenShot_BnR_v1_0.py --debug
```


## Command switches

| Group | Canonical switch | Useful aliases | Purpose |
|---|---|---|---|
| Usage | `--usage` | `-usage`, `/usage`, `usage`, `-u`, `/u`, `/U` | Quick command reminder |
| Help | `--help` | `-help`, `/help`, `help`, `-h`, `/h`, `/?`, `?` | Detailed command guide |
| Man | `--man` | `man`, `-man`, `/man`, `manual`, `--manual`, `-manual`, `/manual` | Manual-style reference |
| About | `--about` | `-about`, `/about`, `about` | Project overview and value |
| Version | `--version` | `-version`, `/version`, `version`, `--ver`, `-ver`, `/ver`, `ver`, `-v`, `/v` | Version and project links |
| Docs index | `--docs` | `-docs`, `/docs`, `docs` | Print the local docs suite map |
| README | `--readme` | `-readme`, `/readme`, `readme` | Print `README.md` |
| Install | `--install` | `-install`, `/install`, `install` | Print `INSTALL.md` |
| Manual install | `--manual-install` | `-manual-install`, `/manual-install`, `manual-install`, `manualinstall` | Print `MANUAL_INSTALL.md` |
| Log guide | `--log-guide` | `-log-guide`, `/log-guide`, `log-guide`, `--logs`, `-logs`, `/logs`, `logs` | Print `LOG_GUIDE.md` |
| Troubleshooting | `--troubleshoot` | `-troubleshoot`, `/troubleshoot`, `troubleshoot`, `--troubleshooting`, `-troubleshooting`, `/troubleshooting`, `troubleshooting` | Print `TROUBLESHOOTING.md` |
| Release guide | `--release-guide` | `-release-guide`, `/release-guide`, `release-guide` | Print `RELEASE_GUIDE.md` |
| Changelog | `--changelog` | `-changelog`, `/changelog`, `changelog` | Print `CHANGELOG.md` |
| Contributing | `--contributing` | `-contributing`, `/contributing`, `contributing` | Print `CONTRIBUTING.md` |
| Security | `--security` | `-security`, `/security`, `security` | Print `SECURITY.md` |
| Code of conduct | `--code-of-conduct` | `-code-of-conduct`, `/code-of-conduct`, `code-of-conduct` | Print `CODE_OF_CONDUCT.md` |
| License | `--license` | `-license`, `/license`, `license` | Print `LICENSE.txt` |
| Debug | `--debug` | `-debug`, `/debug`, `debug` | Print local machine/tool diagnostics |

## What success looks like

A real win looks like this:

- all build stages pass
- `libopenshot` bindings import successfully
- launcher files are generated
- OpenShot opens and logs a clean session
- the output is good enough to move toward portable/frozen distribution

At that point the machine is helping instead of fighting.

## Repository layout

```text
OpenShot_BnR_v1_0.py   Main script
README.md              Primary project overview
README.txt             Plain-text project overview
INSTALL.md             Step-by-step installation and usage guide
LICENSE.txt            MIT license text
CHANGELOG.md           Release history
CONTRIBUTING.md        Contribution rules and workflow guidance
SECURITY.md            Security contact and reporting guidance
CODE_OF_CONDUCT.md     Project behavior expectations
help.html              Wiki-style local help center
assets/                Help CSS / JS / Prism assets
vendor/                Vendored third-party assets and source trees
```

## Documentation map

- Start here: `README.md`
- Installation and workflow: `INSTALL.md`
- Local browser help: `help.html`
- Release history: `CHANGELOG.md`
- Contribution rules: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`

## Included in this pack

- the main Python script
- markdown/plain-text/local HTML documentation
- shortcuts to website, repo, and OpenShot docs
- local help assets
- vendored jQuery source tree

## Links

- Website: https://www.trentontompkins.com
- Repository: https://github.com/tibberous/OpenShot-3.5x-Install-Build-and-Run-Script-en-es-Py-add
- OpenShot developer docs: https://www.openshot.org/static/files/user-guide/developers.html

## Support and custom work

For custom development, automation, integration, or build support:

- **Trenton Tompkins**
- **Phone:** (724) 431-5207
- **Email:** trenttompkins@gmail.com
- **Portfolio:** https://www.trentontompkins.com

## License

Released under the MIT License. See `LICENSE.txt`.
