#!/usr/bin/env python3
"""Author: Trenton Tompkins <trenttompkins@gmail.com> © 2026
Coded with ❤️ by ChatGPT GPT-5.4 Thinking
(724) 431-5207
https://www.trentontompkins.com

OpenShot BnR 1.0
OpenShot Windows Install, Build, Run, and Distribution Prep Script
https://www.trentontompkins.com
https://github.com/tibberous/OpenShot-3.5x-Install-Build-and-Run-Script-en-es-Py
Released under the MIT License: https://opensource.org/license/mit
See README.md, README.txt, INSTALL.md, MANUAL_INSTALL.md, LOG_GUIDE.md, TROUBLESHOOTING.md, RELEASE_GUIDE.md, LICENSE.txt, help.html, CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, and CODE_OF_CONDUCT.md
OpenShot BnR is proud to be Open Source software. No warranty is expressed or implied.
By downloading or using this software you agree to:
https://trentontompkins.com/tos.html

For custom development, integration, automation, or support, call or email
Trenton Tompkins for a free consultation:
(724) 431-5207
trenttompkins@gmail.com
Portfolio: https://www.trentontompkins.com

What this script is:
OpenShot BnR is a practical Windows build, bootstrap, run, document, and distribution-prep
tool for OpenShot 3.5.x. It exists to turn setup friction into a readable,
repeatable workflow.

What it does:
- checks prerequisites before the expensive work starts
- restores or installs the Windows/MSYS2 tooling it needs
- resolves build dependencies from the live UCRT64 package index
- builds libopenshot-audio and libopenshot in order
- verifies Python bindings honestly in installed and source-build modes
- repairs the launch path and generates helper launchers
- exposes usage, help, man, about, version, readme, license, docs, and debug output
- leaves behind logs, state files, and distribution helpers you can inspect

Why that matters:
You can inspect it, extend it, automate it, and make it fit your workflow instead
of bending around closed software. The result is a tool that keeps getting more
valuable because it can be customized to the way you actually work, bill, and
deliver.

Finalized CLI groups:
  usage  : --usage -usage /usage usage -u /u /U
  help   : --help -help /help help -h /h /? ?
  man    : man --man -man /man manual --manual -manual /manual
  about  : --about -about /about about
  version: --version -version /version version --ver -ver /ver ver -v /v
  docs   : --docs -docs /docs docs
  readme : --readme -readme /readme readme
  install: --install -install /install install
  manual : --manual-install -manual-install /manual-install manual-install manualinstall
  logs   : --log-guide -log-guide /log-guide log-guide --logs -logs /logs logs
  trouble: --troubleshoot -troubleshoot /troubleshoot troubleshoot
           --troubleshooting -troubleshooting /troubleshooting troubleshooting
  release: --release-guide -release-guide /release-guide release-guide
  change : --changelog -changelog /changelog changelog
  contrib: --contributing -contributing /contributing contributing
  secure : --security -security /security security
  conduct: --code-of-conduct -code-of-conduct /code-of-conduct code-of-conduct
  license: --license -license /license license
  debug  : --debug -debug /debug debug
"""

import ctypes
import difflib
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import textwrap
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent

PRODUCT_NAME = "OpenShot BnR"
VERSION = "1.1-cpython"
APP_NAME = f"{PRODUCT_NAME} {VERSION}"
APP_FULL_NAME = f"{APP_NAME} - OpenShot Windows Install, Build, and Run Script"
BUILD_ROOT = Path(r"C:\OpenShotBuild")
MSYS_ROOT_DEFAULT = Path(r"C:\msys64")
LOG_PATH = SCRIPT_DIR / "openshot-installer.log"
STATE_PATH = SCRIPT_DIR / "openshot-installer-state.json"
RELAY_PATH = SCRIPT_DIR / "openshot-installer-relay.log"
BNR_PATH = SCRIPT_DIR / "bnr.txt"

WEBSITE_URL = "https://www.trentontompkins.com"
REPO_URL = "https://github.com/tibberous/OpenShot-3.5x-Install-Build-and-Run-Script-en-es-Py"
OPENSHOT_DOCS_URL = "https://www.openshot.org/static/files/user-guide/developers.html"
README_MD_PATH = SCRIPT_DIR / "README.md"
README_TXT_PATH = SCRIPT_DIR / "README.txt"
INSTALL_MD_PATH = SCRIPT_DIR / "INSTALL.md"
LICENSE_TXT_PATH = SCRIPT_DIR / "LICENSE.txt"
HELP_HTML_PATH = SCRIPT_DIR / "help.html"
MANUAL_INSTALL_MD_PATH = SCRIPT_DIR / "MANUAL_INSTALL.md"
LOG_GUIDE_MD_PATH = SCRIPT_DIR / "LOG_GUIDE.md"
TROUBLESHOOTING_MD_PATH = SCRIPT_DIR / "TROUBLESHOOTING.md"
RELEASE_GUIDE_MD_PATH = SCRIPT_DIR / "RELEASE_GUIDE.md"
CHANGELOG_MD_PATH = SCRIPT_DIR / "CHANGELOG.md"
CONTRIBUTING_MD_PATH = SCRIPT_DIR / "CONTRIBUTING.md"
SECURITY_MD_PATH = SCRIPT_DIR / "SECURITY.md"
CODE_OF_CONDUCT_MD_PATH = SCRIPT_DIR / "CODE_OF_CONDUCT.md"


CPYTHON_NUGET_ID = os.environ.get("OPENSHOT_CPYTHON_NUGET_ID", "python").strip() or "python"
CPYTHON_NUGET_VERSION = os.environ.get("OPENSHOT_CPYTHON_NUGET_VERSION", "").strip()
CPYTHON_NUGET_ROOT = BUILD_ROOT / "cpython"
CPYTHON_VENV_DIR = BUILD_ROOT / "cpython-venv"
NUGET_EXE = BUILD_ROOT / "tools" / "nuget.exe"


def windows_to_msys_path(path: Path | str) -> str:
    p = Path(path)
    s = str(p).replace("\\", "/")
    if len(s) >= 2 and s[1] == ':':
        drive = s[0].lower()
        rest = s[2:]
        if not rest.startswith('/'):
            rest = '/' + rest
        return f"/{drive}{rest}"
    return s


def run_msys_script(msys_root: Path, script_name: str, script_content: str, env_name: str = "ucrt64", cwd: Optional[Path] = None, check: bool = False) -> int:
    scripts_dir = BUILD_ROOT / "_installer_scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    script_path = scripts_dir / script_name
    script_path.write_text(script_content.strip() + "\n", encoding="utf-8")
    try:
        script_path.chmod(0o755)
    except Exception:
        pass
    script_msys = windows_to_msys_path(script_path)
    cmd = msys_shell(msys_root, env_name) + [f"bash '{script_msys}'"]
    return run_stream(cmd, cwd=cwd, check=check)

CHILD_ARG = "--elevated-child"
NO_PROMPT_ARG = "--no-prompt"

USAGE_ALIASES = {"--usage", "-usage", "/usage", "usage", "-u", "/u", "/U"}
HELP_ALIASES = {"--help", "-help", "/help", "help", "-h", "/h", "/?", "?"}
MAN_ALIASES = {"man", "--man", "-man", "/man", "manual", "--manual", "-manual", "/manual"}
ABOUT_ALIASES = {"--about", "-about", "/about", "about"}
VERSION_ALIASES = {"--version", "-version", "/version", "version", "--ver", "-ver", "/ver", "ver", "-v", "/v"}
DOCS_ALIASES = {"--docs", "-docs", "/docs", "docs"}
README_ALIASES = {"--readme", "-readme", "/readme", "readme"}
INSTALL_ALIASES = {"--install", "-install", "/install", "install"}
MANUAL_INSTALL_ALIASES = {"--manual-install", "-manual-install", "/manual-install", "manual-install", "manualinstall"}
LOG_GUIDE_ALIASES = {"--log-guide", "-log-guide", "/log-guide", "log-guide", "--logs", "-logs", "/logs", "logs", "logguide"}
TROUBLESHOOTING_ALIASES = {"--troubleshoot", "-troubleshoot", "/troubleshoot", "troubleshoot", "--troubleshooting", "-troubleshooting", "/troubleshooting", "troubleshooting"}
RELEASE_GUIDE_ALIASES = {"--release-guide", "-release-guide", "/release-guide", "release-guide", "releaseguide"}
CHANGELOG_ALIASES = {"--changelog", "-changelog", "/changelog", "changelog"}
CONTRIBUTING_ALIASES = {"--contributing", "-contributing", "/contributing", "contributing"}
SECURITY_ALIASES = {"--security", "-security", "/security", "security"}
CODE_OF_CONDUCT_ALIASES = {"--code-of-conduct", "-code-of-conduct", "/code-of-conduct", "code-of-conduct", "codeofconduct"}
LICENSE_ALIASES = {"--license", "-license", "/license", "license"}
DEBUG_ALIASES = {"--debug", "-debug", "/debug", "debug"}
INFO_ALIASES = (
    USAGE_ALIASES | HELP_ALIASES | MAN_ALIASES | ABOUT_ALIASES | VERSION_ALIASES |
    DOCS_ALIASES | README_ALIASES | INSTALL_ALIASES | MANUAL_INSTALL_ALIASES |
    LOG_GUIDE_ALIASES | TROUBLESHOOTING_ALIASES | RELEASE_GUIDE_ALIASES |
    CHANGELOG_ALIASES | CONTRIBUTING_ALIASES | SECURITY_ALIASES |
    CODE_OF_CONDUCT_ALIASES | LICENSE_ALIASES | DEBUG_ALIASES
)

MIN_WINDOWS_BUILD = 17763
SUPPORTED_HOST_PYTHON_MIN = (3, 9)

REPOS = {
    "libopenshot-audio": "https://github.com/OpenShot/libopenshot-audio.git",
    "libopenshot": "https://github.com/OpenShot/libopenshot.git",
    "openshot-qt": "https://github.com/OpenShot/openshot-qt.git",
}

CAPABILITIES: Dict[str, Dict[str, object]] = {
    "gcc": {
        "commands": ["gcc"],
        "aliases": ["gcc", "gnu compiler collection", "c compiler", "toolchain"],
        "prefer": ["gcc"],
        "required": True,
    },
    "g++": {
        "commands": ["g++"],
        "aliases": ["g++", "c++ compiler", "cpp compiler", "toolchain"],
        "prefer": ["gcc", "g++"],
        "required": True,
    },
    "make": {
        "commands": ["mingw32-make", "make"],
        "aliases": ["mingw32 make", "make", "build make", "toolchain"],
        "prefer": ["make"],
        "required": True,
    },
    "cmake": {
        "commands": ["cmake"],
        "aliases": ["cmake", "build system"],
        "prefer": ["cmake"],
        "required": True,
    },
    "ninja": {
        "commands": ["ninja"],
        "aliases": ["ninja", "build tool"],
        "prefer": ["ninja"],
        "required": False,
    },
    "ffmpeg": {
        "commands": ["ffmpeg"],
        "aliases": ["ffmpeg", "video codec", "avcodec", "avformat", "swscale"],
        "prefer": ["ffmpeg"],
        "required": True,
    },
    "swig": {
        "commands": ["swig"],
        "aliases": ["swig", "wrapper generator"],
        "prefer": ["swig"],
        "required": True,
    },
    "doxygen": {
        "commands": ["doxygen"],
        "aliases": ["doxygen", "documentation generator"],
        "prefer": ["doxygen"],
        "required": False,
    },
    "zeromq": {
        "commands": [],
        "aliases": ["zeromq", "zmq", "libzmq"],
        "prefer": ["zeromq", "zmq"],
        "required": True,
    },
    "python": {
        "commands": ["python3", "python"],
        "aliases": ["python", "python3"],
        "prefer": ["python"],
        "required": False,
    },
    "pip": {
        "commands": ["pip3", "pip"],
        "aliases": ["pip", "python pip"],
        "prefer": ["python pip", "pip"],
        "required": False,
    },
    "pyqt5": {
        "commands": [],
        "aliases": ["python pyqt5", "pyqt5", "qt5 bindings for python", "python qt5"],
        "prefer": ["python pyqt5", "pyqt5"],
        "required": False,
    },
    "pyzmq": {
        "commands": [],
        "aliases": ["python pyzmq", "pyzmq", "python zmq", "zeromq python"],
        "prefer": ["python pyzmq", "pyzmq"],
        "required": False,
    },
    "cx_freeze": {
        "commands": [],
        "aliases": ["python cx freeze", "cxfreeze", "cx freeze"],
        "prefer": ["cx freeze", "cxfreeze"],
        "required": False,
    },
    "rust": {
        "commands": ["rustc", "cargo"],
        "aliases": ["rust", "rustc", "cargo", "rust toolchain"],
        "prefer": ["rust", "rustc", "cargo"],
        "required": False,
    },
    "catch": {
        "commands": [],
        "aliases": ["catch", "catch2", "unittest", "unit test cpp"],
        "prefer": ["catch", "unittest"],
        "required": False,
    },
}

NOISY_TOKENS = {
    "docs", "doc", "debug", "dbg", "testdata", "examples", "demo", "static",
    "bootstrap", "gui", "gtk", "qt6", "clang", "arm", "aarch64", "i686",
    "mingw32", "mingw64", "headers", "python2", "python38", "python39"
}

_ansi_enabled = False
_log_lock = threading.Lock()


def enable_ansi_colors() -> None:
    global _ansi_enabled
    if os.name != "nt":
        _ansi_enabled = True
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            _ansi_enabled = True
    except Exception:
        _ansi_enabled = False


def color(text: str, code: str) -> str:
    if not _ansi_enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def green(text: str) -> str:
    return color(text, "92")


def red(text: str) -> str:
    return color(text, "91")


def yellow(text: str) -> str:
    return color(text, "93")


def cyan(text: str) -> str:
    return color(text, "96")


def timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")



def script_md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def script_lmd(path: Path) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(path.stat().st_mtime))

def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", errors="ignore") as f:
        f.write(text)


def log(level: str, msg: str) -> None:
    line = f"{timestamp()} {level} {msg}"
    with _log_lock:
        print(line, flush=True)
        append_text(LOG_PATH, line + "\n")
        append_text(RELAY_PATH, line + "\n")
        append_text(BNR_PATH, line + "\n")


def info(msg: str) -> None: log("[INFO]", msg)
def trace(msg: str) -> None: log("[TRACE]", msg)
def ok(msg: str) -> None: log("[OK]", msg)
def warn(msg: str) -> None: log("[WARN]", msg)
def fail(msg: str) -> None: log("[FAIL]", msg)


def read_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_state(state: dict) -> None:
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(STATE_PATH)


def update_state(**kwargs) -> None:
    state = read_state()
    state.update(kwargs)
    write_state(state)


def record_stage(stage: str, status: str, detail: str = "") -> None:
    state = read_state()
    stages = state.setdefault("stages", {})
    stages[stage] = {
        "status": status,
        "detail": detail,
        "time": timestamp(),
    }
    write_state(state)
    marker = {"PASS": green("PASS"), "FAIL": red("FAIL"), "WARN": yellow("WARN"), "RUNNING": cyan("RUN")}.get(status, status)
    log("[STAGE]", f"{stage}: {marker} {detail}".rstrip())


def record_artifact(name: str, path: Optional[str], exists: bool, detail: str = "", status: Optional[str] = None) -> None:
    state = read_state()
    artifacts = state.setdefault("artifacts", {})
    normalized_status = (status or ("OK" if exists else "MISS")).upper()
    artifacts[name] = {
        "path": path,
        "exists": exists,
        "detail": detail,
        "status": normalized_status,
        "time": timestamp(),
    }
    write_state(state)


def reset_state_files() -> None:
    LOG_PATH.write_text("", encoding="utf-8")
    RELAY_PATH.write_text("", encoding="utf-8")
    BNR_PATH.write_text("", encoding="utf-8")
    write_state({
        "app_name": APP_NAME,
        "started": timestamp(),
        "completed": False,
        "success": False,
        "stages": {},
        "artifacts": {},
    })


def finalize_bnr_output(reason: str) -> None:
    try:
        snapshot = read_text_best_effort(LOG_PATH)
    except Exception:
        snapshot = ""
    header = f"\n\n{'=' * 72}\nBNR FINAL SNAPSHOT ({reason}) @ {timestamp()}\n{'=' * 72}\n"
    append_text(BNR_PATH, header)
    if snapshot:
        if not snapshot.endswith("\n"):
            snapshot += "\n"
        append_text(BNR_PATH, snapshot)
    else:
        append_text(BNR_PATH, "[WARN] installer.log was empty at finalize time.\n")


def run_capture(
    cmd: Sequence[str] | str,
    *,
    cwd: Optional[Path] = None,
    shell: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess:
    trace(f"RUN_CAPTURE cwd={cwd or Path.cwd()} shell={shell} cmd={cmd!r}")
    cp = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        shell=shell,
        text=True,
        capture_output=True,
        env=env,
    )
    if cp.stdout:
        for line in cp.stdout.splitlines():
            trace(f"STDOUT {line}")
    if cp.stderr:
        for line in cp.stderr.splitlines():
            trace(f"STDERR {line}")
    trace(f"EXIT code={cp.returncode}")
    return cp


def run_stream(
    cmd: Sequence[str] | str,
    *,
    cwd: Optional[Path] = None,
    shell: bool = False,
    env: Optional[Dict[str, str]] = None,
    check: bool = False,
) -> int:
    trace(f"RUN cwd={cwd or Path.cwd()} shell={shell} cmd={cmd!r}")
    process = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        shell=shell,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\r\n")
        if line:
            trace(f"OUT {line}")
    process.wait()
    trace(f"EXIT code={process.returncode}")
    if check and process.returncode != 0:
        raise RuntimeError(f"Command failed ({process.returncode}): {cmd!r}")
    return process.returncode


def which_any(names: Sequence[str]) -> Optional[str]:
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def host_python_ok() -> bool:
    ver = sys.version_info[:3]
    info(f"Host Python version={ver[0]}.{ver[1]}.{ver[2]}")
    return ver >= SUPPORTED_HOST_PYTHON_MIN


def is_windows() -> bool:
    return os.name == "nt"


def windows_build_number() -> Optional[int]:
    if not is_windows():
        return None
    ver = platform.version()
    m = re.search(r"\.(\d+)$", ver)
    return int(m.group(1)) if m else None


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def powershell_path() -> str:
    sysroot = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    return str(sysroot / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe")


def common_paths() -> Dict[str, List[Path]]:
    return {
        "git": [
            Path(r"C:\Program Files\Git\cmd\git.exe"),
            Path(r"C:\Program Files (x86)\Git\cmd\git.exe"),
        ],
        "msys2_shell": [
            MSYS_ROOT_DEFAULT / "msys2_shell.cmd",
        ],
        "pacman": [
            MSYS_ROOT_DEFAULT / "usr" / "bin" / "pacman.exe",
        ],
        "winget": [
            Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps" / "winget.exe",
            Path(r"C:\Users\Default\AppData\Local\Microsoft\WindowsApps\winget.exe"),
        ],
    }


def find_existing_tool(key: str, path_names: Sequence[str]) -> Optional[Path]:
    p = which_any(path_names)
    if p:
        ok(f"{key} found in PATH: {p}")
        return Path(p)
    for candidate in common_paths().get(key, []):
        if candidate.exists():
            ok(f"{key} found in common location: {candidate}")
            return candidate
    return None


def wait_for_elevated_child() -> int:
    last_pos = 0
    start = time.time()
    last_growth = time.time()
    printed_banner = False

    while True:
        if RELAY_PATH.exists():
            size = RELAY_PATH.stat().st_size
            if size > last_pos:
                with RELAY_PATH.open("r", encoding="utf-8", errors="ignore") as f:
                    f.seek(last_pos)
                    chunk = f.read()
                if chunk:
                    print(chunk, end="", flush=True)
                    last_pos = size
                    last_growth = time.time()
                    printed_banner = True

        state = read_state()
        if state.get("completed"):
            if RELAY_PATH.exists():
                size = RELAY_PATH.stat().st_size
                if size > last_pos:
                    with RELAY_PATH.open("r", encoding="utf-8", errors="ignore") as f:
                        f.seek(last_pos)
                        chunk = f.read()
                    if chunk:
                        print(chunk, end="", flush=True)
            return int(state.get("exit_code", 1))

        if time.time() - start > 20 and not printed_banner and not RELAY_PATH.exists():
            print(red("[FAIL]"), "Elevation likely failed or was cancelled before the child started logging.", flush=True)
            return 1

        if printed_banner and time.time() - last_growth > 600:
            print(yellow("[WARN]"), "No new installer output for 10 minutes. Still waiting...", flush=True)
            last_growth = time.time()

        time.sleep(0.20)


def elevate_and_wait() -> int:
    if is_admin():
        ok("Running elevated")
        return 0

    warn("Not elevated. Relaunching with admin rights...")
    args = [str(SCRIPT_PATH), CHILD_ARG, NO_PROMPT_ARG]
    quoted_args = subprocess.list2cmdline(args)
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, quoted_args, str(SCRIPT_DIR), 1)
    if rc <= 32:
        print(red("[FAIL]"), f"Elevation request failed or was cancelled (ShellExecuteW={rc})", flush=True)
        update_state(completed=True, success=False, exit_code=1, failed=True, error=f"Elevation failed ({rc})")
        return 1

    print(cyan("[INFO]"), "Admin child launched. Streaming installer output...\n", flush=True)
    return wait_for_elevated_child()


def check_windows_support() -> None:
    if not is_windows():
        raise RuntimeError("This installer only supports Windows.")
    build = windows_build_number()
    if build is None:
        warn("Could not determine Windows build number")
        return
    info(f"Windows build={build}")
    if build < MIN_WINDOWS_BUILD:
        raise RuntimeError(f"Windows build {build} is too old. Need 17763 or later for WinGet support.")


def ensure_winget() -> Path:
    p = find_existing_tool("winget", ["winget"])
    if p:
        ok(f"winget available: {p}")
        record_artifact("winget", str(p), True, "available")
        return p

    warn("winget not found. Attempting registration with App Installer family name...")
    ps = (
        'try { '
        'Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe -ErrorAction Stop; '
        'exit 0 '
        '} catch { '
        'Write-Host $_.Exception.Message; exit 1 '
        '}'
    )
    run_stream([powershell_path(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps])

    p = find_existing_tool("winget", ["winget"])
    if p:
        ok(f"winget became available after registration: {p}")
        record_artifact("winget", str(p), True, "restored by RegisterByFamilyName")
        return p

    warn("RegisterByFamilyName did not restore winget. Trying official aka.ms/getwinget bootstrap...")
    ps2 = (
        'try { '
        'Add-AppxPackage https://aka.ms/getwinget -ErrorAction Stop; '
        'exit 0 '
        '} catch { '
        'Write-Host $_.Exception.Message; exit 1 '
        '}'
    )
    run_stream([powershell_path(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps2])

    p = find_existing_tool("winget", ["winget"])
    if p:
        ok(f"winget installed from aka.ms/getwinget: {p}")
        record_artifact("winget", str(p), True, "installed from aka.ms/getwinget")
        return p

    record_artifact("winget", None, False, "winget unavailable after recovery attempts")
    raise RuntimeError("winget is still unavailable after registration and aka.ms/getwinget bootstrap.")


def winget_has_package(package_id: str) -> bool:
    cp = run_capture(["winget", "list", "--id", package_id, "-e", "--accept-source-agreements"])
    text = (cp.stdout + cp.stderr).lower()
    return cp.returncode == 0 and package_id.lower() in text


def winget_install(package_id: str, *, name: Optional[str] = None) -> None:
    label = name or package_id
    if winget_has_package(package_id):
        ok(f"{label} already present according to winget")
        return
    info(f"Installing {label} via winget ({package_id})...")
    rc = run_stream([
        "winget", "install", "-e", "--id", package_id,
        "--accept-package-agreements", "--accept-source-agreements",
        "--disable-interactivity",
    ])
    if rc != 0:
        raise RuntimeError(f"winget failed to install {package_id}")


def ensure_git() -> Path:
    p = find_existing_tool("git", ["git"])
    if p:
        record_artifact("git", str(p), True, "available")
        return p
    ensure_winget()
    winget_install("Git.Git", name="Git")
    p = find_existing_tool("git", ["git"])
    if not p:
        record_artifact("git", None, False, "git.exe not found after install")
        raise RuntimeError("Git installation completed but git.exe was not found.")
    record_artifact("git", str(p), True, "installed")
    return p


def ensure_msys2() -> Path:
    root = Path(os.environ.get("MSYS2_ROOT", str(MSYS_ROOT_DEFAULT)))
    shell_cmd = root / "msys2_shell.cmd"
    pacman = root / "usr" / "bin" / "pacman.exe"
    if shell_cmd.exists() and pacman.exists():
        ok(f"MSYS2 present at {root}")
        record_artifact("msys2_shell", str(shell_cmd), True, "available")
        record_artifact("pacman", str(pacman), True, "available")
        return root

    ensure_winget()
    winget_install("MSYS2.MSYS2", name="MSYS2")

    if shell_cmd.exists() and pacman.exists():
        ok(f"MSYS2 installed at {root}")
        record_artifact("msys2_shell", str(shell_cmd), True, "installed")
        record_artifact("pacman", str(pacman), True, "installed")
        return root

    record_artifact("msys2_shell", str(shell_cmd), False, "missing after MSYS2 install")
    record_artifact("pacman", str(pacman), False, "missing after MSYS2 install")
    raise RuntimeError("MSYS2 install completed but msys2_shell.cmd / pacman.exe were not found.")


def msys_shell(msys_root: Path, env_name: str = "ucrt64") -> List[str]:
    return [str(msys_root / "msys2_shell.cmd"), "-defterm", "-no-start", f"-{env_name}", "-here", "-c"]


def msys_capture(msys_root: Path, command: str, env_name: str = "ucrt64", cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    cmd = msys_shell(msys_root, env_name) + [command]
    return run_capture(cmd, cwd=cwd)


def msys_stream(msys_root: Path, command: str, env_name: str = "ucrt64", cwd: Optional[Path] = None, check: bool = False) -> int:
    cmd = msys_shell(msys_root, env_name) + [command]
    return run_stream(cmd, cwd=cwd, check=check)

def shell_quote(value: str) -> str:
    return "\'" + value.replace("\'", "\'\"\'\"\'") + "\'"


def msys_resolve_python(msys_root: Path, preferred_python: Optional[Path] = None, env_name: str = "ucrt64", allow_fallback: bool = False) -> str:
    candidates: List[str] = []
    if preferred_python and preferred_python.exists():
        candidates.append(windows_to_msys_path(preferred_python))
    if allow_fallback:
        candidates.extend(["python3", "python"])

    checked: List[str] = []
    for candidate in candidates:
        checked.append(candidate)
        quoted = shell_quote(candidate)
        if "/" in candidate or "\\" in candidate:
            cp = msys_capture(msys_root, f"[ -x {quoted} ] && printf '%s\n' {quoted}", env_name=env_name)
            resolved = (cp.stdout or "").strip().splitlines()
            if cp.returncode == 0 and resolved:
                return quoted
        else:
            cp = msys_capture(msys_root, f"command -v {candidate}", env_name=env_name)
            resolved = (cp.stdout or "").strip().splitlines()
            if cp.returncode == 0 and resolved:
                return shell_quote(resolved[0])

    joined = ", ".join(checked) if checked else "no candidates"
    raise RuntimeError(f"Could not resolve the required official CPython interpreter. Checked: {joined}")


def msys_env_exports(bindings_dir: Path, build_src_dir: Path) -> str:
    exports: List[str] = []
    if bindings_dir.exists():
        exports.append(f"export PYTHONPATH={shell_quote(windows_to_msys_path(bindings_dir))}:$PYTHONPATH")
    if build_src_dir.exists():
        exports.append(f"export PATH={shell_quote(windows_to_msys_path(build_src_dir))}:$PATH")
    return " && ".join(exports)


def windows_cmd_quote(value: Path | str) -> str:
    return '"' + str(value).replace('"', '""') + '"'


def resolve_windows_python(preferred_python: Optional[Path], msys_root: Path, allow_fallback: bool = False) -> Optional[Path]:
    candidates: List[Path] = []
    if preferred_python:
        candidates.append(preferred_python)
    if allow_fallback:
        candidates.extend([
            msys_root / "ucrt64" / "bin" / "python.exe",
            msys_root / "usr" / "bin" / "python.exe",
        ])
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def create_runtime_bootstrap_script(root: Path, msys_root: Path, qt_repo: Path) -> Path:
    bootstrap = root / "Launch-OpenShot-Qt.py"
    qt_src_dir = qt_repo / "src"
    lib_repo = root / "libopenshot"
    bindings_dir = lib_repo / "build" / "bindings" / "python"
    build_src_dir = lib_repo / "build" / "src"
    ucrt_bin_dir = msys_root / "ucrt64" / "bin"
    freeze_script = qt_repo / "freeze.py"

    bootstrap_text = f'''#!/usr/bin/env python3
import importlib.util
import os
import runpy
import sys
import traceback
from pathlib import Path

QT_REPO = Path(r"{qt_repo}")
QT_SRC_DIR = Path(r"{qt_src_dir}")
BINDINGS_DIR = Path(r"{bindings_dir}")
BUILD_SRC_DIR = Path(r"{build_src_dir}")
UCRT_BIN_DIR = Path(r"{ucrt_bin_dir}")
LAUNCH_PY = QT_SRC_DIR / "launch.py"
FREEZE_PY = Path(r"{freeze_script}")
SMOKE_FLAG = "--installer-smoke-import"
FROZEN_FLAG = "--installer-build-frozen"

def prepend_env(name, values):
    existing = [item for item in os.environ.get(name, "").split(os.pathsep) if item]
    merged = []
    for value in values:
        text = str(value)
        if text and text not in merged:
            merged.append(text)
    for item in existing:
        if item and item not in merged:
            merged.append(item)
    os.environ[name] = os.pathsep.join(merged)

def configure_runtime():
    os.chdir(str(QT_REPO))
    bootstrap_paths = [QT_SRC_DIR, BINDINGS_DIR]
    dll_paths = [BUILD_SRC_DIR, UCRT_BIN_DIR]
    for entry in bootstrap_paths:
        text = str(entry)
        if entry.exists() and text not in sys.path:
            sys.path.insert(0, text)
    prepend_env("PYTHONPATH", bootstrap_paths)
    prepend_env("OPENSHOT_BOOTSTRAP_PATHS", bootstrap_paths)
    prepend_env("PATH", dll_paths)
    os.environ.setdefault("OPENSHOT_INSTALLER_RUNTIME_MODE", "source-build")
    add_dir = getattr(os, "add_dll_directory", None)
    if add_dir:
        for entry in dll_paths:
            if entry.exists():
                try:
                    add_dir(str(entry))
                except OSError:
                    pass

def inject_bootstrap_args(extra_args):
    args = []
    existing = list(extra_args)
    for entry in (BINDINGS_DIR, QT_SRC_DIR):
        args.extend(["--path", str(entry)])
    args.extend(existing)
    return args

def smoke_import() -> int:
    configure_runtime()
    import openshot
    from classes import settings, project_data, updates, sentry  # noqa: F401
    from classes.app import OpenShotApp  # noqa: F401
    print("SMOKE_IMPORT_OK")
    print(f"openshot={{getattr(openshot, '__file__', '')}}")
    print(f"settings={{getattr(settings, '__file__', '')}}")
    print(f"project_data={{getattr(project_data, '__file__', '')}}")
    print(f"updates={{getattr(updates, '__file__', '')}}")
    return 0

def run_frozen_build(extra_args):
    configure_runtime()
    if not FREEZE_PY.exists():
        print(f"freeze.py not found at {{FREEZE_PY}}", file=sys.stderr)
        return 1
    sys.argv = [str(FREEZE_PY)] + list(extra_args or ["build"])
    runpy.run_path(str(FREEZE_PY), run_name="__main__")
    return 0

def run_launch(extra_args):
    configure_runtime()
    spec = importlib.util.spec_from_file_location("openshot_runtime_launch", str(LAUNCH_PY))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load launch.py from {{LAUNCH_PY}}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["openshot_runtime_launch"] = module
    sys.argv = [str(LAUNCH_PY)] + inject_bootstrap_args(extra_args)
    spec.loader.exec_module(module)
    try:
        result = module.main()
        if isinstance(result, int):
            return result
        return 0
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        print(code)
        return 1

def main():
    args = list(sys.argv[1:])
    try:
        if args and args[0] == SMOKE_FLAG:
            return smoke_import()
        if args and args[0] == FROZEN_FLAG:
            return run_frozen_build(args[1:])
        return run_launch(args)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        print(code)
        return 1
    except Exception:
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
'''
    bootstrap.write_text(bootstrap_text, encoding="utf-8", newline="\n")
    record_artifact("launcher_bootstrap_py", str(bootstrap), bootstrap.exists(), "Python runtime bootstrap launcher")
    return bootstrap


def patch_openshot_qt_launch(qt_repo: Path) -> bool:
    launch_py = qt_repo / "src" / "launch.py"
    if not launch_py.exists():
        record_artifact("openshot_qt_launch_patch", str(launch_py), False, "launch.py missing; patch not applied", status="WARN")
        return False

    original = launch_py.read_text(encoding="utf-8", errors="ignore")
    patched = original
    changed = False

    if "import traceback" not in patched:
        if "import logging" in patched:
            patched = patched.replace("import logging", "import logging\nimport traceback", 1)
            changed = True

    if "OPENSHOT_BOOTSTRAP_PATHS" not in patched:
        needle = "    if args.py_path:\n        for p in args.py_path:\n            newpath = os.path.realpath(p)\n            try:\n                if os.path.exists(newpath):\n                    sys.path.insert(0, newpath)\n                    print(f\"Added {newpath} to PYTHONPATH\")\n                else:\n                    print(f\"{newpath} does not exist\")\n            except TypeError as ex:\n                print(f\"Bad path {newpath}: {ex}\")\n                continue\n"
        replacement = needle + "\n    bootstrap_env_paths = os.environ.get('OPENSHOT_BOOTSTRAP_PATHS', '')\n    if bootstrap_env_paths:\n        for p in bootstrap_env_paths.split(os.pathsep):\n            newpath = os.path.realpath(p)\n            if newpath and os.path.exists(newpath) and newpath not in sys.path:\n                sys.path.insert(0, newpath)\n                print(f\"Added {newpath} from OPENSHOT_BOOTSTRAP_PATHS\")\n"
        if needle in patched:
            patched = patched.replace(needle, replacement, 1)
            changed = True

    if "app.show_errors()" in patched and "if app is not None:" not in patched:
        needle = "    try:\n        app = OpenShotApp(argv)\n    except Exception:\n        app.show_errors()\n"
        replacement = "    try:\n        app = OpenShotApp(argv)\n    except Exception:\n        traceback.print_exc()\n        if app is not None:\n            try:\n                app.show_errors()\n            except Exception:\n                traceback.print_exc()\n        raise SystemExit(1)\n"
        if needle in patched:
            patched = patched.replace(needle, replacement, 1)
            changed = True

    if changed:
        backup = launch_py.with_suffix(launch_py.suffix + ".installer.bak")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8", newline="\n")
        launch_py.write_text(patched, encoding="utf-8", newline="\n")
        record_artifact("openshot_qt_launch_patch", str(launch_py), True, "launch.py runtime bootstrap and error handling patch applied")
        return True

    already_patched = ("OPENSHOT_BOOTSTRAP_PATHS" in original) and ("if app is not None:" in original) and ("import traceback" in original)
    record_artifact("openshot_qt_launch_patch", str(launch_py), already_patched, "launch.py patch already present" if already_patched else "launch.py patch pattern not found", status="OK" if already_patched else "WARN")
    return already_patched


def create_distribution_helper(root: Path, msys_root: Path, qt_repo: Path, preferred_python: Optional[Path], bootstrap_path: Path) -> Optional[Path]:
    helper = root / "Build-OpenShot-Frozen.cmd"
    freeze_py = qt_repo / "freeze.py"
    python_exe = resolve_windows_python(preferred_python, msys_root)
    if not freeze_py.exists():
        record_artifact("frozen_build_helper", str(helper), False, "freeze.py not found; frozen build helper not created", status="WARN")
        return None
    python_cmd = windows_cmd_quote(python_exe) if python_exe else "python"
    helper_lines = [
        "@echo off",
        "setlocal",
        f"set OPENSHOT_BUILD_ROOT={root}",
        f"set OPENSHOT_QT_REPO={qt_repo}",
        f"set OPENSHOT_BOOTSTRAP_PATHS={qt_repo / 'src'};{root / 'libopenshot' / 'build' / 'bindings' / 'python'}",
        f"set PATH={root / 'libopenshot' / 'build' / 'src'};{msys_root / 'ucrt64' / 'bin'};%PATH%",
        f'cd /d "{qt_repo}"',
        f"{python_cmd} {windows_cmd_quote(bootstrap_path)} --installer-build-frozen %*",
        "endlocal",
        "",
    ]
    helper.write_text("\r\n".join(str(line) for line in helper_lines), encoding="utf-8", newline="\r\n")
    record_artifact("frozen_build_helper", str(helper), helper.exists(), "Windows frozen-build helper")
    return helper


def create_portable_distribution_helper(root: Path, msys_root: Path, qt_repo: Path, preferred_python: Optional[Path]) -> Optional[Path]:
    helper_py = root / "Build-OpenShot-Portable.py"
    helper_cmd = root / "Build-OpenShot-Portable.cmd"
    python_exe = resolve_windows_python(preferred_python, msys_root)
    if python_exe is None or not python_exe.exists():
        record_artifact("portable_build_helper", str(helper_cmd), False, "Unable to resolve Windows Python for portable helper", status="WARN")
        return None

    lib_repo = root / "libopenshot"
    bindings_dir = lib_repo / "build" / "bindings" / "python"
    build_src_dir = lib_repo / "build" / "src"
    ucrt_bin_dir = msys_root / "ucrt64" / "bin"

    helper_py_text = f'''#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

ROOT = Path(r"{root}")
QT_REPO = Path(r"{qt_repo}")
BINDINGS_DIR = Path(r"{bindings_dir}")
BUILD_SRC_DIR = Path(r"{build_src_dir}")
UCRT_BIN_DIR = Path(r"{ucrt_bin_dir}")
PYTHON_EXE = Path(r"{python_exe}")
DIST_ROOT = ROOT / "dist-portable"
APP_ROOT = DIST_ROOT / "OpenShot-Portable"
RUNTIME_ROOT = APP_ROOT / "runtime"
PYTHON_ROOT = RUNTIME_ROOT / "python"
APP_DATA = APP_ROOT / "app"
QT_TARGET = APP_DATA / "openshot-qt"
BINDINGS_TARGET = APP_DATA / "libopenshot-bindings"
LIB_TARGET = APP_DATA / "libopenshot-bin"
MSYS_TARGET = APP_DATA / "msys-ucrt64-bin"

def copytree_filtered(src: Path, dst: Path, ignore_names=None):
    ignore_names = set(ignore_names or [])
    if dst.exists():
        shutil.rmtree(dst)
    def _ignore(_path, names):
        ignored = set()
        for name in names:
            if name in ignore_names:
                ignored.add(name)
            if name == "__pycache__":
                ignored.add(name)
            if name.endswith(".pyc") or name.endswith(".pyo"):
                ignored.add(name)
        return ignored
    shutil.copytree(src, dst, ignore=_ignore)

def copy_matching(src: Path, dst: Path, patterns):
    dst.mkdir(parents=True, exist_ok=True)
    for pattern in patterns:
        for path in src.glob(pattern):
            if path.is_file():
                shutil.copy2(path, dst / path.name)

def write_portable_launcher():
    launcher_py = APP_ROOT / "OpenShot-Portable.py"
    launcher_cmd = APP_ROOT / "OpenShot-Portable.cmd"
    text = f"""#!/usr/bin/env python3
import importlib.util
import os
import sys
import traceback
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent
QT_REPO = APP_ROOT / "app" / "openshot-qt"
QT_SRC_DIR = QT_REPO / "src"
BINDINGS_DIR = APP_ROOT / "app" / "libopenshot-bindings"
BUILD_SRC_DIR = APP_ROOT / "app" / "libopenshot-bin"
UCRT_BIN_DIR = APP_ROOT / "app" / "msys-ucrt64-bin"
LAUNCH_PY = QT_SRC_DIR / "launch.py"

def prepend_env(name, values):
    existing = [item for item in os.environ.get(name, "").split(os.pathsep) if item]
    merged = []
    for value in values:
        text = str(value)
        if text and text not in merged:
            merged.append(text)
    for item in existing:
        if item and item not in merged:
            merged.append(item)
    os.environ[name] = os.pathsep.join(merged)

def configure():
    os.chdir(str(QT_REPO))
    bootstrap_paths = [QT_SRC_DIR, BINDINGS_DIR]
    dll_paths = [BUILD_SRC_DIR, UCRT_BIN_DIR]
    for entry in bootstrap_paths:
        text = str(entry)
        if entry.exists() and text not in sys.path:
            sys.path.insert(0, text)
    prepend_env("PYTHONPATH", bootstrap_paths)
    prepend_env("OPENSHOT_BOOTSTRAP_PATHS", bootstrap_paths)
    prepend_env("PATH", dll_paths)
    add_dir = getattr(os, "add_dll_directory", None)
    if add_dir:
        for entry in dll_paths:
            if entry.exists():
                try:
                    add_dir(str(entry))
                except OSError:
                    pass

def main():
    configure()
    spec = importlib.util.spec_from_file_location("openshot_portable_launch", str(LAUNCH_PY))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load launch.py from {{LAUNCH_PY}}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["openshot_portable_launch"] = module
    sys.argv = [str(LAUNCH_PY), "--path", str(BINDINGS_DIR), "--path", str(QT_SRC_DIR)] + list(sys.argv[1:])
    spec.loader.exec_module(module)
    return module.main()

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
"""
    launcher_py.write_text(text, encoding="utf-8", newline="\n")
    python_candidates = [
        PYTHON_ROOT / "python.exe",
        PYTHON_ROOT / "bin" / "python.exe",
        PYTHON_ROOT / "Scripts" / "python.exe",
    ]
    python_cmd = next((candidate for candidate in python_candidates if candidate.exists()), PYTHON_ROOT / "python.exe")
    launcher_cmd.write_text("\r\n".join([
        "@echo off",
        "setlocal",
        f'cd /d "{{APP_ROOT}}"',
        f'"{{python_cmd}}" "{{launcher_py.name}}" %*',
        "endlocal",
        "",
    ]), encoding="utf-8", newline="\r\n")

def main():
    DIST_ROOT.mkdir(parents=True, exist_ok=True)
    if APP_ROOT.exists():
        shutil.rmtree(APP_ROOT)
    APP_ROOT.mkdir(parents=True, exist_ok=True)
    copytree_filtered(QT_REPO, QT_TARGET, ignore_names={{".git", "build", "dist", "dist-portable", ".pytest_cache"}})
    copytree_filtered(PYTHON_EXE.parent.parent if (PYTHON_EXE.parent.name.lower() in ("bin", "scripts")) else PYTHON_EXE.parent, PYTHON_ROOT, ignore_names={{"__pycache__"}})
    copytree_filtered(BINDINGS_DIR, BINDINGS_TARGET, ignore_names={{"__pycache__"}})
    copytree_filtered(BUILD_SRC_DIR, LIB_TARGET, ignore_names={{"__pycache__"}})
    copy_matching(UCRT_BIN_DIR, MSYS_TARGET, ["*.dll", "*.exe"])
    write_portable_launcher()
    print(APP_ROOT)

if __name__ == "__main__":
    main()
'''
    helper_py.write_text(helper_py_text, encoding="utf-8", newline="\n")
    helper_cmd_lines = [
        "@echo off",
        "setlocal",
        f"{windows_cmd_quote(python_exe)} {windows_cmd_quote(helper_py)} %*",
        "endlocal",
        "",
    ]
    helper_cmd.write_text("\r\n".join(helper_cmd_lines), encoding="utf-8", newline="\r\n")
    record_artifact("portable_build_helper_py", str(helper_py), helper_py.exists(), "Portable distribution builder script")
    record_artifact("portable_build_helper", str(helper_cmd), helper_cmd.exists(), "Portable distribution builder launcher")
    return helper_cmd


def query_python_runtime_info(msys_root: Path, preferred_python: Optional[Path] = None) -> Dict[str, object]:
    probe = BUILD_ROOT / "query_python_runtime_info.py"
    probe.write_text(
        """import json
import site
import sys
import sysconfig

data = {
    'executable': sys.executable,
    'version': sys.version,
    'sys_path': sys.path,
    'site_packages': site.getsitepackages() if hasattr(site, 'getsitepackages') else [],
    'user_site': site.getusersitepackages() if hasattr(site, 'getusersitepackages') else '',
    'sysconfig_paths': sysconfig.get_paths(),
}
print(json.dumps(data))
""",
        encoding="utf-8",
    )
    python_cmd = msys_resolve_python(msys_root, preferred_python)
    cp = msys_capture(msys_root, f"{python_cmd} {shell_quote(windows_to_msys_path(probe))}", env_name="ucrt64")
    if cp.returncode != 0:
        return {
            "ok": False,
            "detail": (cp.stdout + cp.stderr).strip(),
            "site_packages": [],
            "sys_path": [],
            "user_site": "",
            "sysconfig_paths": {},
        }
    lines = [line.strip() for line in cp.stdout.splitlines() if line.strip()]
    for line in reversed(lines):
        try:
            data = json.loads(line)
            data["ok"] = True
            data["detail"] = "runtime info loaded"
            return data
        except Exception:
            continue
    return {
        "ok": False,
        "detail": cp.stdout.strip() or cp.stderr.strip() or "Unable to parse python runtime info",
        "site_packages": [],
        "sys_path": [],
        "user_site": "",
        "sysconfig_paths": {},
    }


def msys_update(msys_root: Path) -> None:
    info("Refreshing MSYS2 package database...")
    msys_stream(msys_root, "pacman -Sy --noconfirm", env_name="ucrt64", check=True)
    info("Upgrading MSYS2 packages (pass 1)...")
    msys_stream(msys_root, "pacman -Syu --noconfirm --needed", env_name="ucrt64", check=True)
    info("Upgrading MSYS2 packages (pass 2)...")
    msys_stream(msys_root, "pacman -Su --noconfirm --needed", env_name="ucrt64", check=True)


def get_ucrt_repo_packages(msys_root: Path) -> List[str]:
    cp = msys_capture(msys_root, "pacman -Sl ucrt64", env_name="ucrt64")
    if cp.returncode != 0:
        raise RuntimeError("Unable to query pacman package list for ucrt64")
    packages = []
    for line in cp.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[0] == "ucrt64":
            packages.append(parts[1])
    if not packages:
        raise RuntimeError("No package names were returned from pacman -Sl ucrt64")
    ok(f"Loaded {len(packages)} live UCRT64 package names")
    return packages


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"^mingw-w64-(ucrt|clang|mingw32|mingw64|clangarm64)-x86_64-", "", text)
    text = re.sub(r"^ucrt64/", "", text)
    text = text.replace("python3", "python")
    text = text.replace("cx_freeze", "cx freeze")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def token_set(text: str) -> List[str]:
    return [t for t in normalize(text).split() if t]


def score_package(alias: str, package_name: str) -> float:
    q = normalize(alias)
    p = normalize(package_name)
    if not q or not p:
        return 0.0

    q_tokens = set(token_set(q))
    p_tokens = set(token_set(p))

    ratio = difflib.SequenceMatcher(None, q, p).ratio()
    overlap = len(q_tokens & p_tokens) / max(1, len(q_tokens))
    containment = 1.0 if q in p else 0.0
    exact = 1.0 if q == p else 0.0

    prefix_bonus = 0.0
    if p.startswith(q):
        prefix_bonus += 0.15
    if q_tokens:
        first = sorted(q_tokens)[0]
        if first in p_tokens:
            prefix_bonus += 0.05

    penalty = 0.0
    penalty += 0.09 * len(NOISY_TOKENS & p_tokens)

    if "python" in q_tokens and "python" not in p_tokens:
        penalty += 0.40
    if "qt5" in q_tokens and "qt5" not in p_tokens and "pyqt5" not in p_tokens:
        penalty += 0.40
    if "zmq" in q_tokens and not ({"zmq", "zeromq"} & p_tokens):
        penalty += 0.40
    if "cargo" in q_tokens and "cargo" not in p_tokens:
        penalty += 0.40
    if "rust" in q_tokens and not ({"rust", "rustc", "cargo", "rustup"} & p_tokens):
        penalty += 0.35

    score = ratio * 0.45 + overlap * 0.35 + containment * 0.10 + exact * 0.20 + prefix_bonus - penalty
    if package_name.startswith("mingw-w64-ucrt-x86_64-"):
        score += 0.08
    if package_name.startswith("mingw-w64-clang") or package_name.startswith("mingw-w64-i686-"):
        score -= 0.40
    return score


def rank_candidates(aliases: Sequence[str], package_names: Sequence[str], limit: int = 20) -> List[Tuple[str, float, str]]:
    best: Dict[str, Tuple[float, str]] = {}
    for alias in aliases:
        for pkg in package_names:
            s = score_package(alias, pkg)
            prev = best.get(pkg)
            if prev is None or s > prev[0]:
                best[pkg] = (s, alias)
    ranked = sorted(((pkg, score, alias) for pkg, (score, alias) in best.items()), key=lambda x: x[1], reverse=True)
    return ranked[:limit]


def msys_command_exists(msys_root: Path, commands: Sequence[str]) -> bool:
    for cmd in commands:
        cp = msys_capture(msys_root, f"command -v {cmd}")
        if cp.returncode == 0 and cp.stdout.strip():
            ok(f"MSYS capability present: {cmd} -> {cp.stdout.strip()}")
            return True
    return False


def pacman_installed(msys_root: Path, package_name: str) -> bool:
    cp = msys_capture(msys_root, f"pacman -Q {package_name}")
    return cp.returncode == 0


def install_package(msys_root: Path, package_name: str) -> bool:
    info(f"Installing package candidate: {package_name}")
    rc = msys_stream(msys_root, f"pacman -S --needed --noconfirm --disable-download-timeout {package_name}")
    return rc == 0


def resolve_and_install_capability(msys_root: Path, capability: str, repo_packages: Sequence[str]) -> Optional[str]:
    spec = CAPABILITIES[capability]
    commands = list(spec.get("commands", []))
    aliases = list(spec.get("aliases", []))
    prefer = list(spec.get("prefer", []))
    required = bool(spec.get("required", False))

    info(f"Resolving capability: {capability}")
    if commands and msys_command_exists(msys_root, commands):
        ok(f"Capability already satisfied: {capability}")
        return None

    ranked = rank_candidates(aliases, repo_packages, limit=30)
    if not ranked:
        if required:
            raise RuntimeError(f"No live UCRT64 package candidates found for capability '{capability}'")
        warn(f"No package candidates found for optional capability '{capability}'")
        return None

    reranked = []
    for pkg, score, alias in ranked:
        bonus = 0.0
        norm_pkg = normalize(pkg)
        for token in prefer:
            if normalize(token) in norm_pkg:
                bonus += 0.08
        reranked.append((pkg, score + bonus, alias))
    reranked.sort(key=lambda x: x[1], reverse=True)

    top_preview = ", ".join([f"{pkg}={score:.3f}" for pkg, score, _ in reranked[:10]])
    info(f"Top package guesses for {capability}: {top_preview}")
    state = read_state()
    state[f"candidates_{capability}"] = [{"package": pkg, "score": score, "alias": alias} for pkg, score, alias in reranked[:10]]
    write_state(state)

    attempted = []
    for pkg, score, alias in reranked:
        attempted.append((pkg, score))
        if pacman_installed(msys_root, pkg):
            ok(f"{pkg} already installed for capability {capability}")
            if not commands or msys_command_exists(msys_root, commands):
                return pkg

        if install_package(msys_root, pkg):
            if not commands or msys_command_exists(msys_root, commands):
                ok(f"Capability {capability} satisfied by {pkg} (alias={alias}, score={score:.3f})")
                return pkg
            warn(f"{pkg} installed but capability {capability} still not verified; trying next guess...")
        else:
            warn(f"Install failed for candidate {pkg} (score={score:.3f}); trying next guess...")

    if required:
        raise RuntimeError(f"Failed to satisfy required capability '{capability}'. Tried: {attempted[:8]}")
    warn(f"Optional capability '{capability}' was not satisfied.")
    return None


def ensure_capabilities(msys_root: Path, repo_packages: Sequence[str]) -> Dict[str, Optional[str]]:
    installed = {}
    for capability in CAPABILITIES:
        installed[capability] = resolve_and_install_capability(msys_root, capability, repo_packages)
    return installed



def ensure_nuget_exe() -> Path:
    NUGET_EXE.parent.mkdir(parents=True, exist_ok=True)
    if NUGET_EXE.exists():
        return NUGET_EXE
    url = "https://aka.ms/nugetclidl"
    info(f"Downloading nuget.exe from {url}")
    powershell = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        f"$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri '{url}' -OutFile '{NUGET_EXE}'",
    ]
    run_stream(powershell, check=True)
    record_artifact("nuget_exe", str(NUGET_EXE), NUGET_EXE.exists(), "official NuGet CLI")
    return NUGET_EXE


def discover_cpython_layout(root: Path) -> Dict[str, Optional[Path]]:
    python_exe = None
    base_dir = None
    package_dir = None
    if not root.exists():
        return {"package_dir": None, "base_dir": None, "python_exe": None, "include_dir": None, "libs_dir": None, "python_lib": None, "site_packages": None}
    packages = []
    for child in root.iterdir():
        if child.is_dir() and child.name.lower().startswith("python"):
            packages.append(child)
    packages.sort(key=lambda p: p.name.lower())
    for pkg in packages:
        candidates = [pkg / "tools" / "python.exe", pkg / "python.exe", pkg / "bin" / "python.exe"]
        exe = next((c for c in candidates if c.exists()), None)
        if exe:
            package_dir = pkg
            python_exe = exe
            base_dir = exe.parent
            break
    if python_exe is None:
        for exe in root.rglob("python.exe"):
            python_exe = exe
            base_dir = exe.parent
            package_dir = exe.parent.parent if exe.parent.name.lower() == 'tools' else exe.parent
            break
    include_dir = None
    libs_dir = None
    site_packages = None
    python_lib = None
    if base_dir:
        for cand in [base_dir / "include", base_dir.parent / "include"]:
            if cand.exists():
                include_dir = cand
                break
        for cand in [base_dir / "libs", base_dir.parent / "libs"]:
            if cand.exists():
                libs_dir = cand
                break
        for cand in [base_dir / "Lib" / "site-packages", base_dir.parent / "Lib" / "site-packages"]:
            if cand.exists():
                site_packages = cand
                break
    if libs_dir:
        py_libs = sorted(libs_dir.glob("python*.lib"))
        python_lib = py_libs[0] if py_libs else None
    return {
        "package_dir": package_dir,
        "base_dir": base_dir,
        "python_exe": python_exe,
        "include_dir": include_dir,
        "libs_dir": libs_dir,
        "python_lib": python_lib,
        "site_packages": site_packages,
    }


def ensure_cpython_build_runtime() -> Dict[str, Optional[Path]]:
    info("Preparing official CPython build runtime (NuGet package)...")
    nuget_exe = ensure_nuget_exe()
    CPYTHON_NUGET_ROOT.mkdir(parents=True, exist_ok=True)
    layout = discover_cpython_layout(CPYTHON_NUGET_ROOT)
    if layout.get("python_exe") and layout.get("include_dir") and layout.get("python_lib"):
        ok(f"CPython build runtime already present: {layout['python_exe']}")
        record_artifact("cpython_python", str(layout["python_exe"]), True, "official CPython executable")
        record_artifact("cpython_include", str(layout["include_dir"]), True, "official CPython headers")
        record_artifact("cpython_lib", str(layout["python_lib"]), True, "official CPython import library")
        return layout
    install_cmd = [str(nuget_exe), "install", CPYTHON_NUGET_ID, "-ExcludeVersion", "-OutputDirectory", str(CPYTHON_NUGET_ROOT)]
    if CPYTHON_NUGET_VERSION:
        install_cmd.extend(["-Version", CPYTHON_NUGET_VERSION])
    info("Installing official CPython NuGet package for build scenarios...")
    run_stream(install_cmd, check=True)
    layout = discover_cpython_layout(CPYTHON_NUGET_ROOT)
    ok_runtime = bool(layout.get("python_exe") and layout.get("include_dir") and layout.get("python_lib"))
    record_artifact("cpython_python", str(layout.get("python_exe") or (CPYTHON_NUGET_ROOT / "python.exe")), ok_runtime, "official CPython executable")
    record_artifact("cpython_include", str(layout.get("include_dir") or (CPYTHON_NUGET_ROOT / "include")), ok_runtime, "official CPython headers")
    record_artifact("cpython_lib", str(layout.get("python_lib") or (CPYTHON_NUGET_ROOT / "libs")), ok_runtime, "official CPython import library")
    if not ok_runtime:
        raise RuntimeError("CPython NuGet install completed but python.exe / include / libs were not discovered")
    return layout


def ensure_windows_venv(base_python: Path) -> Path:
    info("Preparing Windows CPython venv for openshot-qt...")
    if CPYTHON_VENV_DIR.exists():
        shutil.rmtree(CPYTHON_VENV_DIR, ignore_errors=True)
    run_stream([str(base_python), "-m", "venv", str(CPYTHON_VENV_DIR)], check=True)
    venv_python = CPYTHON_VENV_DIR / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = CPYTHON_VENV_DIR / "python.exe"
    if not venv_python.exists():
        raise RuntimeError("CPython venv was not created as expected.")
    pip_cmd = [str(venv_python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"]
    run_stream(pip_cmd, check=True)
    package_cmd = [
        str(venv_python), "-m", "pip", "install",
        "httplib2", "tinys3", "github3.py==0.9.6", "requests", "sentry-sdk", "cx_Freeze",
        "PyQt5", "PyQtWebEngine", "pyzmq", "PyOpenGL",
    ]
    run_stream(package_cmd, check=True)
    record_artifact("cpython_venv", str(venv_python), True, "Windows CPython venv with openshot-qt deps")
    return venv_python


def cpython_cmake_args(preferred_python: Optional[Path]) -> List[str]:
    if not preferred_python:
        return []
    python_exe = Path(preferred_python)
    base_dir = python_exe.parent
    include_dir = None
    libs_dir = None
    python_lib = None
    site_packages = None
    for cand in [base_dir / "include", base_dir.parent / "include"]:
        if cand.exists():
            include_dir = cand
            break
    for cand in [base_dir / "libs", base_dir.parent / "libs"]:
        if cand.exists():
            libs_dir = cand
            break
    if libs_dir:
        py_libs = sorted(libs_dir.glob("python*.lib"))
        if py_libs:
            python_lib = py_libs[0]
    for cand in [base_dir / "Lib" / "site-packages", base_dir.parent / "Lib" / "site-packages"]:
        if cand.exists():
            site_packages = cand
            break
    args = [f"-DPYTHON_EXECUTABLE={windows_to_msys_path(python_exe)}"]
    if include_dir:
        args.append(f"-DPYTHON_INCLUDE_DIR={windows_to_msys_path(include_dir)}")
    if python_lib:
        args.append(f"-DPYTHON_LIBRARY={windows_to_msys_path(python_lib)}")
    if site_packages:
        args.append(f"-DPYTHON_MODULE_PATH={windows_to_msys_path(site_packages)}")
    args.append(f"-DPython3_EXECUTABLE={windows_to_msys_path(python_exe)}")
    args.append(f"-DPython3_ROOT_DIR={windows_to_msys_path(base_dir.parent if base_dir.name.lower() == 'scripts' else base_dir)}")
    return args


def run_python_capture(preferred_python: Optional[Path], args: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    if preferred_python and Path(preferred_python).exists():
        return run_capture([str(preferred_python), *args], cwd=cwd)
    raise RuntimeError("A Windows CPython interpreter was required but not resolved")

def ensure_python_support_env(msys_root: Path) -> Optional[Path]:
    info("Preparing Python support environment for openshot-qt...")
    venv_dir = BUILD_ROOT / "pyenv"
    msys_venv = windows_to_msys_path(venv_dir)
    base_python = msys_resolve_python(msys_root)

    script = f"""
rm -rf {shell_quote(msys_venv)}
{base_python} -m venv --system-site-packages {shell_quote(msys_venv)}
if [ -x {shell_quote(msys_venv + "/bin/python")} ]; then
    VENV_PY={shell_quote(msys_venv + "/bin/python")}
    VENV_PIP={shell_quote(msys_venv + "/bin/pip")}
else
    VENV_PY={shell_quote(msys_venv + "/Scripts/python.exe")}
    VENV_PIP={shell_quote(msys_venv + "/Scripts/pip.exe")}
fi
"$VENV_PY" -m pip install --upgrade pip setuptools wheel
"$VENV_PIP" install httplib2 tinys3 github3.py==0.9.6 requests sentry-sdk cx_Freeze
"""
    rc = run_msys_script(msys_root, "prepare_python_env.sh", script, env_name="ucrt64")
    venv_python_candidates = [
        venv_dir / "bin" / "python.exe",
        venv_dir / "bin" / "python",
        venv_dir / "Scripts" / "python.exe",
        venv_dir / "Scripts" / "python",
    ]
    venv_python = next((p for p in venv_python_candidates if p.exists()), None)
    ok_env = rc == 0 and venv_python is not None
    record_artifact("python_venv", str(venv_python or (venv_dir / "bin" / "python")), ok_env, "venv extras ready" if ok_env else "venv extras unavailable")
    if ok_env:
        ok(f"Python support environment ready: {venv_python}")
        return venv_python
    warn("Python venv extras were not fully prepared. Falling back to system MSYS2 Python.")
    return None


def git_clone_or_update(name: str, url: str, root: Path) -> Path:
    dest = root / name
    if (dest / ".git").exists():
        info(f"Updating existing repo: {name}")
        run_stream(["git", "-C", str(dest), "fetch", "--all", "--tags"], check=True)
        run_stream(["git", "-C", str(dest), "pull", "--ff-only"], check=True)
    elif dest.exists():
        warn(f"{dest} exists but is not a git repo; leaving it untouched.")
    else:
        info(f"Cloning {name} from {url}")
        run_stream(["git", "clone", url, str(dest)], check=True)
    return dest


def clone_or_update_repos(root: Path) -> Dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    repos: Dict[str, Path] = {}
    for name, url in REPOS.items():
        repos[name] = git_clone_or_update(name, url, root)
        record_artifact(f"repo_{name}", str(repos[name]), repos[name].exists(), "repo ready")
    return repos


def write_python_probe(
    script_path: Path,
    module_name: str,
    extra_lines: Optional[List[str]] = None,
    bootstrap_lines: Optional[List[str]] = None,
) -> Path:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "import importlib",
        "import os",
        "import sys",
    ]
    if bootstrap_lines:
        lines.extend(bootstrap_lines)
    lines.extend([
        f"name = {module_name!r}",
        "mod = importlib.import_module(name)",
        "print(f\"module={name}\")",
        "print(f\"file={getattr(mod, '__file__', '')}\")",
        "print(f\"sys_path_0={sys.path[0] if sys.path else ''}\")",
        "print(f\"path={os.environ.get('PYTHONPATH', '')}\")",
    ])
    if extra_lines:
        lines.extend(extra_lines)
    script_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return script_path




def read_text_best_effort(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def discover_imagemagick_libraries(msys_root: Path) -> Dict[str, object]:
    lib_dir = msys_root / "ucrt64" / "lib"
    patterns = {
        "magickpp": ["libMagick++-*.dll.a", "libMagick++*.dll.a", "libMagick++-*.a", "libMagick++*.a"],
        "magickwand": ["libMagickWand-*.dll.a", "libMagickWand*.dll.a", "libMagickWand-*.a", "libMagickWand*.a"],
        "magickcore": ["libMagickCore-*.dll.a", "libMagickCore*.dll.a", "libMagickCore-*.a", "libMagickCore*.a"],
    }
    resolved: Dict[str, Optional[Path]] = {}
    link_items: List[Path] = []
    quoted_items: List[str] = []
    linker_names: List[str] = []
    for key, globs in patterns.items():
        match: Optional[Path] = None
        for pattern in globs:
            candidates = sorted(lib_dir.glob(pattern))
            if candidates:
                match = candidates[0]
                break
        resolved[key] = match
        if match:
            link_items.append(match)
            quoted_items.append(shell_quote(windows_to_msys_path(match)))
            linker_name = match.name
            for suffix in (".dll.a", ".a", ".lib"):
                if linker_name.endswith(suffix):
                    linker_name = linker_name[:-len(suffix)]
                    break
            if linker_name.startswith("lib") and len(linker_name) > 3:
                linker_name = linker_name[3:]
            linker_names.append(linker_name)
    linker_flags = [f"-L{windows_to_msys_path(lib_dir)}"] + [f"-l{name}" for name in linker_names]
    return {
        "lib_dir": lib_dir,
        "magickpp": resolved.get("magickpp"),
        "magickwand": resolved.get("magickwand"),
        "magickcore": resolved.get("magickcore"),
        "items": link_items,
        "quoted_items": quoted_items,
        "linker_names": linker_names,
        "linker_flags": linker_flags,
        "complete": bool(resolved.get("magickcore")) and bool(resolved.get("magickwand")),
    }


def find_link_patch_targets(build_dir: Path) -> List[Path]:
    if not build_dir.exists():
        return []
    patterns = [
        "**/CMakeFiles/openshot.dir/link.txt",
        "**/CMakeFiles/openshot.dir/linkLibs.rsp",
        "**/CMakeFiles/openshot.dir/*.rsp",
    ]
    found: List[Path] = []
    seen = set()
    for pattern in patterns:
        for candidate in build_dir.glob(pattern):
            if candidate.is_file():
                key = str(candidate.resolve())
                if key not in seen:
                    seen.add(key)
                    found.append(candidate)
    return found


def patch_link_command_file_with_libraries(link_file: Path, libraries: Sequence[Path]) -> Dict[str, object]:
    try:
        text = link_file.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"ok": False, "changed": False, "detail": f"{link_file.name} missing or unreadable"}

    missing: List[str] = []
    for lib in libraries:
        lib_text = windows_to_msys_path(lib)
        if lib.name not in text and lib_text not in text:
            missing.append(shell_quote(lib_text))

    if not missing:
        return {"ok": True, "changed": False, "detail": f"ImageMagick import libraries already present in {link_file.name}"}

    patched = text.rstrip() + " " + " ".join(missing) + "\n"
    link_file.write_text(patched, encoding="utf-8", newline="\n")
    return {"ok": True, "changed": True, "detail": f"Appended {len(missing)} ImageMagick import libraries to {link_file.name}"}


def patch_link_targets_with_libraries(link_targets: Sequence[Path], libraries: Sequence[Path]) -> Dict[str, object]:
    if not link_targets:
        return {"ok": False, "changed": False, "detail": "No openshot link command files were discovered after configure", "targets": []}
    details: List[str] = []
    any_ok = False
    any_changed = False
    target_names: List[str] = []
    for target in link_targets:
        target_names.append(str(target))
        result = patch_link_command_file_with_libraries(target, libraries)
        details.append(f"{target.name}: {result.get('detail', '')}")
        if result.get("ok"):
            any_ok = True
        if result.get("changed"):
            any_changed = True
    return {
        "ok": any_ok,
        "changed": any_changed,
        "detail": "; ".join(details),
        "targets": target_names,
    }


def detect_imagemagick_link_failure(text: str) -> bool:
    if not text:
        return False
    markers = (
        "__imp_WriteImages",
        "__imp_AcquireExceptionInfo",
        "__imp_DestroyExceptionInfo",
        "__imp_ExportImagePixels",
        "MagickUtilities.cpp.obj",
        "ImageWriter.cpp.obj",
    )
    return any(marker in text for marker in markers)
def verify_openshot_import(msys_root: Path, repo_dir: Path, preferred_python: Optional[Path] = None) -> Dict[str, object]:
    probe = BUILD_ROOT / "verify_openshot_import.py"
    bindings_dir = repo_dir / "build" / "bindings" / "python"
    build_src_dir = repo_dir / "build" / "src"
    ucrt_bin_dir = msys_root / "ucrt64" / "bin"

    runtime_info = query_python_runtime_info(msys_root, preferred_python)
    site_packages: List[Path] = []
    for item in runtime_info.get("site_packages", []) or []:
        try:
            site_packages.append(Path(str(item)))
        except Exception:
            pass
    user_site = runtime_info.get("user_site")
    if user_site:
        try:
            site_packages.append(Path(str(user_site)))
        except Exception:
            pass

    bootstrap_common = [
        f"build_src_dir = {str(build_src_dir)!r}",
        f"ucrt_bin_dir = {str(ucrt_bin_dir)!r}",
        "path_parts = []",
        "for part in (build_src_dir, ucrt_bin_dir):",
        "    if os.path.isdir(part):",
        "        path_parts.append(part)",
        "        add_dir = getattr(os, 'add_dll_directory', None)",
        "        if add_dir:",
        "            try:",
        "                add_dir(part)",
        "            except OSError:",
        "                pass",
        "if path_parts:",
        "    os.environ['PATH'] = os.pathsep.join(path_parts + [os.environ.get('PATH', '')])",
        "print(f'bootstrap_build_src={build_src_dir}')",
        "print(f'bootstrap_ucrt_bin={ucrt_bin_dir}')",
    ]

    installed_bootstrap = list(bootstrap_common)
    installed_bootstrap.extend([
        "print('probe_mode=installed')",
        "print(f'sys_path_0={sys.path[0] if sys.path else ''}')",
    ])
    write_python_probe(probe, "openshot", [
        "version = getattr(mod, 'Version', None)",
        "print(f'version={version}')",
    ], bootstrap_lines=installed_bootstrap)

    python_cmd = msys_resolve_python(msys_root, preferred_python)
    probe_cmd = f"{python_cmd} {shell_quote(windows_to_msys_path(probe))}"
    installed_cp = msys_capture(msys_root, probe_cmd, env_name="ucrt64")
    installed_ok = installed_cp.returncode == 0 and 'module=openshot' in installed_cp.stdout

    source_cp = installed_cp
    source_ok = False
    if not installed_ok:
        source_bootstrap = list(bootstrap_common)
        source_bootstrap.extend([
            f"bindings_dir = {str(bindings_dir)!r}",
            "if os.path.isdir(bindings_dir) and bindings_dir not in sys.path:",
            "    sys.path.insert(0, bindings_dir)",
            "print('probe_mode=source-build')",
            "print(f'bootstrap_bindings={bindings_dir}')",
        ])
        write_python_probe(probe, "openshot", [
            "version = getattr(mod, 'Version', None)",
            "print(f'version={version}')",
        ], bootstrap_lines=source_bootstrap)
        source_cp = msys_capture(msys_root, probe_cmd, env_name="ucrt64")
        source_ok = source_cp.returncode == 0 and 'module=openshot' in source_cp.stdout

    installed_detail = (installed_cp.stdout + installed_cp.stderr).strip()
    source_detail = (source_cp.stdout + source_cp.stderr).strip() if source_cp is not installed_cp else ""
    if installed_ok:
        mode = "installed"
        detail = installed_detail
    elif source_ok:
        mode = "source-build"
        detail = source_detail
    else:
        mode = "failed"
        detail = (installed_detail + "\n\n--- source fallback ---\n" + source_detail).strip() if source_detail else installed_detail

    return {
        "ok": installed_ok or source_ok,
        "detail": detail,
        "mode": mode,
        "installed_import_ok": installed_ok,
        "source_import_ok": source_ok,
        "runtime_info": runtime_info,
        "site_packages": [str(p) for p in site_packages],
    }


def build_libopenshot_audio(msys_root: Path, repo_dir: Path) -> bool:
    info("Building libopenshot-audio...")
    repo_msys = windows_to_msys_path(repo_dir)
    rc = run_msys_script(
        msys_root,
        "build_libopenshot_audio.sh",
        f"""
cd '{repo_msys}'
rm -rf build
cmake -S . -B build -G 'MSYS Makefiles' -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/ucrt64 -DCMAKE_PREFIX_PATH=/ucrt64
cmake --build build --parallel
cmake --install build
""",
        env_name="ucrt64",
    )
    install_manifest = repo_dir / "build" / "install_manifest.txt"
    cache_file = repo_dir / "build" / "CMakeCache.txt"
    build_outputs = list((repo_dir / "build").rglob("*openshot*audio*")) + list((repo_dir / "build").rglob("*OpenShotAudio*"))
    installed_outputs = list((MSYS_ROOT_DEFAULT / "ucrt64").rglob("*openshot*audio*")) + list((MSYS_ROOT_DEFAULT / "ucrt64").rglob("*OpenShotAudio*"))

    record_artifact("audio_build_cache", str(cache_file), cache_file.exists(), "libopenshot-audio CMake cache")
    record_artifact("audio_install_manifest", str(install_manifest), install_manifest.exists(), "libopenshot-audio install manifest")
    record_artifact("audio_build_outputs", str(repo_dir / "build"), bool(build_outputs), f"{len(build_outputs)} libopenshot-audio build outputs found")
    record_artifact("audio_installed_outputs", str(MSYS_ROOT_DEFAULT / "ucrt64"), bool(installed_outputs), f"{len(installed_outputs)} installed audio outputs found")

    ok_build = rc == 0 and cache_file.exists() and (install_manifest.exists() or bool(build_outputs) or bool(installed_outputs))
    return ok_build



def build_libopenshot(msys_root: Path, repo_dir: Path, preferred_python: Optional[Path] = None) -> Dict[str, object]:
    info("Building libopenshot...")
    repo_msys = windows_to_msys_path(repo_dir)
    imagemagick = discover_imagemagick_libraries(msys_root)

    record_artifact(
        "imagemagick_link_libraries",
        str(imagemagick.get("lib_dir") or ""),
        bool(imagemagick.get("items")),
        ", ".join(path.name for path in imagemagick.get("items", [])) or "No ImageMagick import libraries discovered under /ucrt64/lib",
        status="OK" if imagemagick.get("complete") else "WARN",
    )
    record_artifact(
        "imagemagick_linker_flags",
        None,
        bool(imagemagick.get("linker_flags")),
        " ".join(imagemagick.get("linker_flags", [])) or "No ImageMagick linker flags generated",
        status="OK" if imagemagick.get("linker_flags") else "WARN",
    )

    cmake_args = [
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_PREFIX=/ucrt64",
        "-DCMAKE_PREFIX_PATH=/ucrt64",
    ]
    if imagemagick.get("linker_flags"):
        linker_flag_text = " ".join(imagemagick.get("linker_flags", []))
        cmake_args.append(f"-DCMAKE_SHARED_LINKER_FLAGS={shell_quote(linker_flag_text)}")
    cmake_args.extend(cpython_cmake_args(preferred_python))
    cmake_arg_text = " ".join(cmake_args)

    configure_rc = run_msys_script(
        msys_root,
        "configure_libopenshot.sh",
        f"""
cd '{repo_msys}'
rm -rf build
export LIBOPENSHOT_AUDIO_DIR=/ucrt64
cmake -S . -B build -G 'MSYS Makefiles' {cmake_arg_text}
""",
        env_name="ucrt64",
    )

    link_patch_result = {"ok": False, "changed": False, "detail": "libopenshot configure did not complete", "targets": []}
    link_targets: List[Path] = []
    if configure_rc == 0:
        link_targets = find_link_patch_targets(repo_dir / "build")
        link_patch_result = patch_link_targets_with_libraries(link_targets, imagemagick.get("items", []))
    record_artifact(
        "libopenshot_link_targets",
        None,
        bool(link_targets),
        "; ".join(str(path) for path in link_targets) if link_targets else "No openshot link command files discovered after configure",
        status="OK" if link_targets else "WARN",
    )
    record_artifact(
        "libopenshot_link_patch",
        "; ".join(link_patch_result.get("targets", [])) if link_patch_result.get("targets") else None,
        bool(link_patch_result.get("ok")),
        str(link_patch_result.get("detail", "")),
        status="OK" if link_patch_result.get("ok") else "WARN",
    )

    build_rc = configure_rc
    if configure_rc == 0:
        build_rc = run_msys_script(
            msys_root,
            "compile_install_libopenshot.sh",
            f"""
cd '{repo_msys}'
cmake --build build --parallel --verbose
cmake --install build || true
""",
            env_name="ucrt64",
        )
    rc = build_rc

    cache_file = repo_dir / "build" / "CMakeCache.txt"
    install_manifest = repo_dir / "build" / "install_manifest.txt"
    bindings_dir = repo_dir / "build" / "bindings" / "python"
    openshot_py = bindings_dir / "openshot.py"
    openshot_pyd = next(iter(bindings_dir.glob("*_openshot*.pyd")), None)
    if openshot_pyd is None:
        openshot_pyd = next(iter(bindings_dir.glob("_openshot*.pyd")), None)
    build_src = repo_dir / "build" / "src"
    build_dll = next(iter(build_src.glob("libopenshot*.dll")), None)
    build_import_lib = next(iter(build_src.glob("libopenshot*.a")), None)
    installed_dll = next(iter((MSYS_ROOT_DEFAULT / "ucrt64" / "bin").glob("libopenshot.dll")), None)

    verify = verify_openshot_import(msys_root, repo_dir, preferred_python)
    runtime_info = verify.get("runtime_info", {}) if isinstance(verify.get("runtime_info"), dict) else {}
    site_package_dirs: List[Path] = []
    for item in verify.get("site_packages", []) or []:
        try:
            site_package_dirs.append(Path(str(item)))
        except Exception:
            pass
    if not site_package_dirs:
        for site_packages_dir in (MSYS_ROOT_DEFAULT / "ucrt64" / "lib").glob("python*/site-packages"):
            site_package_dirs.append(site_packages_dir)

    installed_pyd = None
    installed_py = None
    for site_packages_dir in site_package_dirs:
        candidate_py = site_packages_dir / "openshot.py"
        candidate_pyd = next(iter(site_packages_dir.glob("_openshot*.pyd")), None)
        if candidate_py.exists() and installed_py is None:
            installed_py = candidate_py
        if candidate_pyd and installed_pyd is None:
            installed_pyd = candidate_pyd
        if installed_py and installed_pyd:
            break

    built_enough = cache_file.exists() and openshot_py.exists() and bool(openshot_pyd) and bool(build_dll)
    source_ready = openshot_py.exists() and bool(openshot_pyd) and bindings_dir.exists() and bool(build_dll)

    record_artifact("python_runtime_info", None, bool(runtime_info.get("ok")), runtime_info.get("detail", ""), status="OK" if runtime_info.get("ok") else "WARN")
    record_artifact("python_runtime_site_packages", "; ".join(str(p) for p in site_package_dirs) if site_package_dirs else None, bool(site_package_dirs), f"{len(site_package_dirs)} python site-packages path(s) discovered", status="OK" if site_package_dirs else "WARN")
    record_artifact("libopenshot_build_cache", str(cache_file), cache_file.exists(), "libopenshot CMake cache")
    record_artifact("libopenshot_install_manifest", str(install_manifest), install_manifest.exists(), "libopenshot install manifest", status="OK" if install_manifest.exists() else ("WARN" if source_ready else "MISS"))
    record_artifact("libopenshot_bindings_dir", str(bindings_dir), bindings_dir.exists(), "libopenshot Python bindings dir")
    record_artifact("libopenshot_py", str(openshot_py), openshot_py.exists(), "generated openshot.py binding")
    record_artifact("libopenshot_pyd", str(openshot_pyd) if openshot_pyd else str(bindings_dir / "_openshot*.pyd"), bool(openshot_pyd), "compiled _openshot extension")
    record_artifact("libopenshot_build_dll", str(build_dll) if build_dll else str(build_src / "libopenshot*.dll"), bool(build_dll), "built libopenshot DLL")
    record_artifact("libopenshot_build_lib", str(build_import_lib) if build_import_lib else str(build_src / "libopenshot*.a"), bool(build_import_lib), "built libopenshot import/static library", status="OK" if build_import_lib else ("WARN" if bool(build_dll) else "MISS"))
    record_artifact("libopenshot_installed_dll", str(installed_dll) if installed_dll else str(MSYS_ROOT_DEFAULT / "ucrt64" / "bin" / "libopenshot*.dll"), bool(installed_dll), "installed libopenshot DLL", status="OK" if installed_dll else ("WARN" if source_ready else "MISS"))
    record_artifact("libopenshot_installed_py", str(installed_py) if installed_py else None, bool(installed_py), "installed openshot.py binding", status="OK" if installed_py else ("WARN" if verify.get("mode") == "source-build" else "MISS"))
    record_artifact("libopenshot_installed_pyd", str(installed_pyd) if installed_pyd else None, bool(installed_pyd), "installed libopenshot Python extension", status="OK" if installed_pyd else ("WARN" if verify.get("mode") == "source-build" else "MISS"))
    record_artifact("python_openshot_import", None, bool(verify.get("ok")), verify.get("detail", ""), status="OK" if verify.get("ok") else ("WARN" if source_ready else "MISS"))
    record_artifact("python_openshot_import_mode", None, bool(verify.get("ok")), str(verify.get("mode", "failed")), status="OK" if verify.get("ok") else ("WARN" if source_ready else "MISS"))
    record_artifact("python_openshot_import_installed", None, bool(verify.get("installed_import_ok")), "installed site-packages import probe", status="OK" if verify.get("installed_import_ok") else ("WARN" if verify.get("source_import_ok") else "MISS"))
    record_artifact("python_openshot_import_source", None, bool(verify.get("source_import_ok")), "source-build import probe", status="OK" if verify.get("source_import_ok") else ("WARN" if verify.get("installed_import_ok") else "MISS"))

    compile_ok = rc == 0 and built_enough
    recent_log = read_text_best_effort(LOG_PATH)
    imagemagick_link_failed = detect_imagemagick_link_failure(recent_log)

    if compile_ok and verify.get("ok"):
        stage_status = "PASS"
        if verify.get("mode") == "installed":
            stage_detail = "Video library built and installed Python bindings import successfully"
        else:
            stage_detail = "Video library built; source-build Python bindings import successfully"
    elif compile_ok:
        stage_status = "WARN"
        stage_detail = "Video library built, but Python import verification still needs runtime bootstrap"
    else:
        stage_status = "FAIL"
        if configure_rc != 0:
            stage_detail = f"Video configure failed with exit code {configure_rc}"
        elif imagemagick_link_failed:
            stage_detail = "Video build still failed at the ImageMagick/Magick++ link stage"
        elif rc != 0:
            stage_detail = f"Video build command failed with exit code {rc}"
        else:
            stage_detail = "Video build did not leave the expected binary and binding artifacts"

    return {
        "ok": compile_ok,
        "runtime_ok": bool(verify.get("ok")),
        "stage_status": stage_status,
        "stage_detail": stage_detail,
        "compile_ok": compile_ok,
        "source_ready": source_ready,
        "verify": verify,
    }


def create_launcher(root: Path, msys_root: Path, qt_repo: Path, preferred_python: Optional[Path]) -> Path:
    bootstrap_path = create_runtime_bootstrap_script(root, msys_root, qt_repo)
    create_distribution_helper(root, msys_root, qt_repo, preferred_python, bootstrap_path)
    create_portable_distribution_helper(root, msys_root, qt_repo, preferred_python)

    launcher = root / "Launch-OpenShot-Qt.cmd"
    lib_repo = root / "libopenshot"
    bindings_dir = lib_repo / "build" / "bindings" / "python"
    build_src_dir = lib_repo / "build" / "src"
    qt_src_dir = qt_repo / "src"
    python_exe = resolve_windows_python(preferred_python, msys_root)
    if python_exe is None:
        raise RuntimeError("Unable to resolve the required official CPython launcher runtime.")
    python_cmd = windows_cmd_quote(python_exe)

    lines = [
        "@echo off",
        "setlocal",
        f"set OPENSHOT_BUILD_ROOT={root}",
        f"set OPENSHOT_QT_REPO={qt_repo}",
        f"set OPENSHOT_BOOTSTRAP_PATHS={qt_src_dir};{bindings_dir}",
        f"set PYTHONPATH={bindings_dir};{qt_src_dir};%PYTHONPATH%",
        f"set PATH={build_src_dir};{msys_root / 'ucrt64' / 'bin'};%PATH%",
        f'cd /d "{qt_repo}"',
        f"{python_cmd} {windows_cmd_quote(bootstrap_path)} %*",
        "endlocal",
        "",
    ]
    launcher.write_text("\r\n".join(str(line) for line in lines), encoding="utf-8", newline="\r\n")
    record_artifact("launcher_cmd", str(launcher), launcher.exists(), "Launch OpenShot .cmd")
    ok(f"Created launcher: {launcher}")
    return launcher


def verify_qt_launcher(msys_root: Path, qt_repo: Path, preferred_python: Optional[Path]) -> bool:
    launch_py = qt_repo / "src" / "launch.py"
    record_artifact("openshot_qt_launch_py", str(launch_py), launch_py.exists(), "openshot-qt launch script")
    bootstrap = BUILD_ROOT / "Launch-OpenShot-Qt.py"
    record_artifact("launcher_bootstrap_py", str(bootstrap), bootstrap.exists(), "Python runtime bootstrap launcher")
    if not launch_py.exists() or not bootstrap.exists():
        return False

    python_exe = resolve_windows_python(preferred_python, msys_root)
    if python_exe is None:
        record_artifact("openshot_qt_runtime_smoke", None, False, "Unable to resolve Windows Python for runtime smoke test", status="WARN")
        return False

    cp = run_capture([str(python_exe), str(bootstrap), "--installer-smoke-import"], cwd=qt_repo)
    smoke_ok = cp.returncode == 0 and "SMOKE_IMPORT_OK" in cp.stdout
    detail = (cp.stdout.strip() or cp.stderr.strip())
    record_artifact("openshot_qt_smoke_import", None, smoke_ok, detail, status="OK" if smoke_ok else "WARN")
    record_artifact("openshot_qt_runtime_smoke", None, smoke_ok, detail, status="OK" if smoke_ok else "WARN")
    return smoke_ok


def print_summary_from_state(state: dict) -> None:
    print("\n" + "=" * 72)
    print(cyan(APP_NAME))
    print("=" * 72)
    stages = state.get("stages", {})
    for stage_name in [
        "Prerequisites",
        "Dependencies",
        "Repositories",
        "Build libopenshot-audio",
        "Build libopenshot",
        "Prepare openshot-qt",
        "Verification",
        "Launch OpenShot",
    ]:
        st = stages.get(stage_name, {})
        status = st.get("status", "SKIP")
        detail = st.get("detail", "")
        if status == "PASS":
            marker = green("🟢 PASS")
        elif status == "FAIL":
            marker = red("🔴 FAIL")
        elif status == "WARN":
            marker = yellow("🟡 WARN")
        else:
            marker = cyan("🔵 " + status)
        print(f"{marker:<12} {stage_name}: {detail}")

    print("\nArtifacts:")
    for name, art in state.get("artifacts", {}).items():
        status = str(art.get("status") or ("OK" if art.get("exists") else "MISS")).upper()
        if status == "OK":
            marker = green("OK")
        elif status == "WARN":
            marker = yellow("WARN")
        else:
            marker = red("MISS")
        path = art.get("path") or ""
        detail = art.get("detail") or ""
        print(f"  {marker:>4}  {name}: {path} {detail}".rstrip())

    launcher = state.get("launcher_path")
    run_command = state.get("run_command")
    print("\nHow to run OpenShot:")
    if launcher:
        print(f"  1) Double-click: {launcher}")
        print(f'  2) Or run: cmd /c "{launcher}"')
    if run_command:
        print(f"  3) Raw command: {run_command}")
    print(f"\nLog files: {LOG_PATH} | {BNR_PATH}")
    print("=" * 72 + "\n")


def launch_openshot_once(launcher: Path, qt_repo: Path, preferred_python: Optional[Path], msys_root: Path, warmup_seconds: int = 12) -> Dict[str, object]:
    if not launcher.exists():
        return {"ok": False, "detail": f"Launcher does not exist: {launcher}", "pid": None, "command": ""}

    bootstrap = BUILD_ROOT / "Launch-OpenShot-Qt.py"
    python_exe = resolve_windows_python(preferred_python, msys_root)
    if python_exe and bootstrap.exists():
        cmd = [str(python_exe), str(bootstrap)]
        cwd = qt_repo
        label = "direct CPython bootstrap"
    else:
        cmd = ["cmd", "/c", str(launcher)]
        cwd = launcher.parent
        label = "launcher cmd"

    info(f"Launching OpenShot automatically via {label}: {cmd!r}")
    process = subprocess.Popen(cmd, cwd=str(cwd))
    deadline = time.time() + warmup_seconds
    while time.time() < deadline:
        rc = process.poll()
        if rc is not None:
            elapsed = warmup_seconds - max(0.0, deadline - time.time())
            return {
                "ok": False,
                "detail": f"OpenShot exited too quickly with code {rc} after about {elapsed:.1f}s via {label}",
                "pid": process.pid,
                "command": " ".join(cmd),
            }
        time.sleep(0.5)

    return {
        "ok": True,
        "detail": f"OpenShot stayed running for at least {warmup_seconds}s via {label}",
        "pid": process.pid,
        "command": " ".join(cmd),
    }


def maybe_prompt_run(state: dict) -> None:
    launcher = state.get("launcher_path")
    success = bool(state.get("success"))
    if not success or not launcher or not Path(launcher).exists():
        return
    try:
        answer = input("OpenShot looks ready. Run it now? [Y/n]: ").strip().lower()
    except EOFError:
        return
    if answer in ("", "y", "yes"):
        info(f"Launching OpenShot via {launcher}")
        subprocess.Popen(["cmd", "/c", launcher], cwd=str(Path(launcher).parent))
    else:
        info("Run skipped by user.")


def do_install_work(prompt_at_end: bool) -> int:
    reset_state_files()
    enable_ansi_colors()
    info(APP_FULL_NAME)
    try:
        info(f"Installer file md5={script_md5(SCRIPT_PATH)}")
        info(f"Installer file lmd={script_lmd(SCRIPT_PATH)}")
    except Exception as exc:
        warn(f"Unable to fingerprint installer file: {exc}")
    trace(f"argv={sys.argv!r}")
    trace(f"cwd={Path.cwd()}")
    trace(f"script={SCRIPT_PATH}")

    if not host_python_ok():
        raise RuntimeError(f"Host Python must be >= {SUPPORTED_HOST_PYTHON_MIN[0]}.{SUPPORTED_HOST_PYTHON_MIN[1]}")

    check_windows_support()

    record_stage("Prerequisites", "RUNNING", "Checking admin, winget, git, and MSYS2")
    ensure_winget()
    ensure_git()
    msys_root = ensure_msys2()
    ok("Prerequisites are ready")
    update_state(msys_root=str(msys_root))
    record_stage("Prerequisites", "PASS", "Admin, winget, git, and MSYS2 verified")

    record_stage("Dependencies", "RUNNING", "Refreshing MSYS2, resolving live packages, and provisioning official CPython")
    msys_update(msys_root)
    repo_packages = get_ucrt_repo_packages(msys_root)
    update_state(repo_package_count=len(repo_packages))
    ensured = ensure_capabilities(msys_root, repo_packages)
    update_state(capabilities=ensured)
    cpython_layout = ensure_cpython_build_runtime()
    base_cpython = cpython_layout.get("python_exe")
    if not base_cpython:
        raise RuntimeError("Official CPython build runtime was not resolved.")
    preferred_python = ensure_windows_venv(Path(base_cpython))
    update_state(
        cpython_python=str(base_cpython),
        cpython_site_packages=str(cpython_layout.get("site_packages") or ""),
        preferred_python=str(preferred_python),
    )
    record_stage("Dependencies", "PASS", f"Resolved {len(ensured)} capability entries against {len(repo_packages)} live packages and locked the build to official CPython")

    record_stage("Repositories", "RUNNING", "Cloning or updating OpenShot repositories")
    repos = clone_or_update_repos(BUILD_ROOT)
    update_state(repos={k: str(v) for k, v in repos.items()})
    record_stage("Repositories", "PASS", "OpenShot repositories are present")

    record_stage("Build libopenshot-audio", "RUNNING", "Building and installing audio library")
    audio_ok = build_libopenshot_audio(msys_root, repos["libopenshot-audio"])
    if audio_ok:
        record_stage("Build libopenshot-audio", "PASS", "Audio library built and install manifest found")
    else:
        record_stage("Build libopenshot-audio", "FAIL", "Audio build did not leave expected artifacts")
        raise RuntimeError("libopenshot-audio build failed verification")

    record_stage("Build libopenshot", "RUNNING", "Building and installing video library and Python bindings")
    lib_result = build_libopenshot(msys_root, repos["libopenshot"], preferred_python)
    record_stage("Build libopenshot", lib_result["stage_status"], lib_result["stage_detail"])
    if not lib_result["ok"]:
        raise RuntimeError("libopenshot build failed to produce the expected binary outputs")

    record_stage("Prepare openshot-qt", "RUNNING", "Patching launch.py, creating runtime bootstrap, and validating startup")
    patched_launch = patch_openshot_qt_launch(repos["openshot-qt"])
    launcher = create_launcher(BUILD_ROOT, msys_root, repos["openshot-qt"], preferred_python)
    qt_ok = verify_qt_launcher(msys_root, repos["openshot-qt"], preferred_python)
    update_state(
        launcher_path=str(launcher),
        run_command=f'cmd /c "{launcher}"',
        preferred_python=str(preferred_python) if preferred_python else "",
        launch_patch_applied=patched_launch,
    )
    if qt_ok:
        record_stage("Prepare openshot-qt", "PASS", "launch.py patched, bootstrap launcher created, and runtime smoke import verified")
    else:
        record_stage("Prepare openshot-qt", "WARN", "Runtime launcher was created, but the final startup smoke test still needs adjustment")

    record_stage("Verification", "RUNNING", "Checking final expected files and launch entry points")
    artifacts = read_state().get("artifacts", {})
    success = (
        artifacts.get("audio_install_manifest", {}).get("exists") and
        artifacts.get("libopenshot_bindings_dir", {}).get("exists") and
        artifacts.get("libopenshot_py", {}).get("exists") and
        artifacts.get("libopenshot_pyd", {}).get("exists") and
        artifacts.get("libopenshot_build_dll", {}).get("exists") and
        artifacts.get("openshot_qt_launch_py", {}).get("exists") and
        artifacts.get("openshot_qt_launch_patch", {}).get("exists") and
        artifacts.get("launcher_bootstrap_py", {}).get("exists") and
        artifacts.get("launcher_cmd", {}).get("exists") and
        artifacts.get("openshot_qt_runtime_smoke", {}).get("exists")
    )
    if success:
        record_stage("Verification", "PASS", "Build artifacts exist and the real runtime bootstrap smoke test passed")
        ok("OpenShot source build finished successfully")
    else:
        record_stage("Verification", "FAIL", "Build artifacts exist, but the real runtime bootstrap smoke test did not pass yet")
        raise RuntimeError("Build artifacts were created, but the final runtime bootstrap smoke test failed")

    record_stage("Launch OpenShot", "RUNNING", "Launching the freshly built OpenShot with the locked CPython runtime")
    launch_result = launch_openshot_once(launcher, repos["openshot-qt"], preferred_python, msys_root)
    record_artifact(
        "openshot_auto_launch",
        launch_result.get("command"),
        bool(launch_result.get("ok")),
        str(launch_result.get("detail", "")),
        status="OK" if launch_result.get("ok") else "WARN",
    )
    update_state(
        auto_launch_ok=bool(launch_result.get("ok")),
        auto_launch_pid=launch_result.get("pid"),
        auto_launch_command=launch_result.get("command"),
    )
    if launch_result.get("ok"):
        record_stage("Launch OpenShot", "PASS", str(launch_result.get("detail", "")))
    else:
        record_stage("Launch OpenShot", "FAIL", str(launch_result.get("detail", "")))
        raise RuntimeError("OpenShot built, but the automatic launch exited too quickly.")

    state = read_state()
    state["completed"] = True
    state["success"] = True
    state["exit_code"] = 0
    state["finished"] = timestamp()
    write_state(state)

    finalize_bnr_output("child-success")
    print_summary_from_state(state)
    return 0


def normalize_cli_token(token: str) -> str:
    return token.strip().lower()


def read_local_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def build_identity_text() -> str:
    return textwrap.dedent(f"""\
    Script file: {SCRIPT_PATH.name}
    Script md5:  {script_md5(SCRIPT_PATH)}
    Script lmd:  {script_lmd(SCRIPT_PATH)}
    Version:     {VERSION}
    """).strip()


def build_docs_index_text() -> str:
    return textwrap.dedent(f"""\
    {APP_FULL_NAME}
    {'=' * 72}
    Documentation suite:
      README.md           Project overview and first-run summary
      INSTALL.md          Fast path, workflow, and result reading
      MANUAL_INSTALL.md   Manual package URLs, package roles, and direct install commands
      LOG_GUIDE.md        Successful log walkthrough and stage meanings
      TROUBLESHOOTING.md  Permission, install, runtime, and packaging fixes
      RELEASE_GUIDE.md    Release-candidate and ship checklist
      CHANGELOG.md        Release history
      CONTRIBUTING.md     Contribution rules and workflow expectations
      SECURITY.md         Vulnerability reporting guidance
      CODE_OF_CONDUCT.md  Project behavior expectations
      LICENSE.txt         MIT license text
      help.html           Styled local wiki with navigation and developer quick start

    Project links:
      Website:       {WEBSITE_URL}
      Repository:    {REPO_URL}
      OpenShot docs: {OPENSHOT_DOCS_URL}
    """).strip()


def build_usage_text() -> str:
    return textwrap.dedent(f"""\
    {APP_FULL_NAME}
    {'=' * 72}
    {build_identity_text()}

    Usage:
      py -3 {SCRIPT_PATH.name}                Run the full install/build/launch-prep workflow
      py -3 {SCRIPT_PATH.name} [info-switch]  Print docs or diagnostics and exit

    Quick commands:
      usage : --usage  -usage  /usage  usage  -u  /u  /U
      help  : --help   -help   /help   help   -h  /h  /?  ?
      man   : man  --man  -man  /man  manual  --manual  -manual  /manual
      about : --about  -about  /about  about
      ver   : --version  -version  /version  version  --ver  -ver  /ver  ver  -v  /v
      docs  : --docs  -docs  /docs  docs
      debug : --debug  -debug  /debug  debug

    Read next:
      help.html, README.md, INSTALL.md
    """).strip()


def build_help_text() -> str:
    return textwrap.dedent(f"""\
    {APP_FULL_NAME}
    {'=' * 72}
    {build_identity_text()}

    Help summary:
      This script installs, builds, verifies, launches, and prepares distribution helpers
      for OpenShot 3.5.x on Windows. Use no switches to run the real workflow. Use the
      switches below when you want docs, diagnostics, or project metadata without touching
      the build.

    Information commands:
      --usage  -usage  /usage  usage  -u  /u  /U
          Quick command reminder.

      --help  -help  /help  help  -h  /h  /?  ?
          Detailed command guide.

      man  --man  -man  /man  manual  --manual  -manual  /manual
          Full manual-style reference.

      --about  -about  /about  about
          Project purpose, value, identity, and contact info.

      --version  -version  /version  version  --ver  -ver  /ver  ver  -v  /v
          Version banner, md5, and project links.

      --docs  -docs  /docs  docs
          Print the local docs index.

      --readme  -readme  /readme  readme
          Print README.md.

      --install  -install  /install  install
          Print INSTALL.md.

      --manual-install  -manual-install  /manual-install  manual-install  manualinstall
          Print MANUAL_INSTALL.md.

      --log-guide  -log-guide  /log-guide  log-guide  --logs  -logs  /logs  logs
          Print LOG_GUIDE.md.

      --troubleshoot  -troubleshoot  /troubleshoot  troubleshoot
      --troubleshooting  -troubleshooting  /troubleshooting  troubleshooting
          Print TROUBLESHOOTING.md.

      --release-guide  -release-guide  /release-guide  release-guide
          Print RELEASE_GUIDE.md.

      --changelog  -changelog  /changelog  changelog
          Print CHANGELOG.md.

      --contributing  -contributing  /contributing  contributing
          Print CONTRIBUTING.md.

      --security  -security  /security  security
          Print SECURITY.md.

      --code-of-conduct  -code-of-conduct  /code-of-conduct  code-of-conduct
          Print CODE_OF_CONDUCT.md.

      --license  -license  /license  license
          Print LICENSE.txt.

      --debug  -debug  /debug  debug
          Print local machine, tool, file, and md5 info.

    Common examples:
      py -3 {SCRIPT_PATH.name}
      py -3 {SCRIPT_PATH.name} --help
      py -3 {SCRIPT_PATH.name} man
      py -3 {SCRIPT_PATH.name} --about
      py -3 {SCRIPT_PATH.name} --version
      py -3 {SCRIPT_PATH.name} --debug
      py -3 {SCRIPT_PATH.name} --docs
      py -3 {SCRIPT_PATH.name} --install
      py -3 {SCRIPT_PATH.name} --troubleshoot
    """).strip()


def build_man_text() -> str:
    return textwrap.dedent(f"""\
    NAME
        {PRODUCT_NAME} - Windows install, build, run, and distribution-prep helper for OpenShot 3.5.x

    SYNOPSIS
        py -3 {SCRIPT_PATH.name}
        py -3 {SCRIPT_PATH.name} [information-switches]

    IDENTITY
        {build_identity_text().replace(chr(10), chr(10) + '        ')}

    DESCRIPTION
        {PRODUCT_NAME} turns a fragile Windows source-build process into a readable workflow.
        It checks the machine, restores or installs toolchain pieces, resolves MSYS2 UCRT64
        packages against the live repo index, builds libopenshot-audio and libopenshot, verifies
        Python bindings honestly, patches the launch path, and generates helper launchers and
        distribution prep scripts.

        Run it with no switches when you want the real build. Run it with an information switch
        when you want documentation, diagnostics, version info, or local file help.

    INFORMATION SWITCHES
        usage
            --usage  -usage  /usage  usage  -u  /u  /U
        help
            --help  -help  /help  help  -h  /h  /?  ?
        man
            man  --man  -man  /man  manual  --manual  -manual  /manual
        about
            --about  -about  /about  about
        version
            --version  -version  /version  version  --ver  -ver  /ver  ver  -v  /v
        docs
            --docs  -docs  /docs  docs
        readme
            --readme  -readme  /readme  readme
        install
            --install  -install  /install  install
        manual install
            --manual-install  -manual-install  /manual-install  manual-install  manualinstall
        log guide
            --log-guide  -log-guide  /log-guide  log-guide  --logs  -logs  /logs  logs
        troubleshooting
            --troubleshoot  -troubleshoot  /troubleshoot  troubleshoot
            --troubleshooting  -troubleshooting  /troubleshooting  troubleshooting
        release guide
            --release-guide  -release-guide  /release-guide  release-guide
        changelog
            --changelog  -changelog  /changelog  changelog
        contributing
            --contributing  -contributing  /contributing  contributing
        security
            --security  -security  /security  security
        code of conduct
            --code-of-conduct  -code-of-conduct  /code-of-conduct  code-of-conduct
        license
            --license  -license  /license  license
        debug
            --debug  -debug  /debug  debug

    GENERATED OUTPUTS
        C:\\OpenShotBuild\\Launch-OpenShot-Qt.cmd
        C:\\OpenShotBuild\\Launch-OpenShot-Qt.py
        C:\\OpenShotBuild\\Build-OpenShot-Frozen.cmd
        C:\\OpenShotBuild\\Build-OpenShot-Portable.cmd
        openshot-installer.log
        openshot-installer-state.json
        openshot-installer-relay.log

    SUCCESS LOOKS LIKE
        1. Prerequisites, Dependencies, Repositories, and build stages all pass.
        2. libopenshot bindings import in installed or source-build mode.
        3. Launch helpers are generated.
        4. OpenShot starts, initializes the UI, and ends the session cleanly.

    FILES
        README.md, INSTALL.md, MANUAL_INSTALL.md, LOG_GUIDE.md, TROUBLESHOOTING.md,
        RELEASE_GUIDE.md, CHANGELOG.md, CONTRIBUTING.md, SECURITY.md,
        CODE_OF_CONDUCT.md, LICENSE.txt, help.html

    LINKS
        Website: {WEBSITE_URL}
        Repository: {REPO_URL}
        OpenShot docs: {OPENSHOT_DOCS_URL}
    """).strip()


def build_about_text() -> str:
    return textwrap.dedent(f"""\
    {APP_FULL_NAME}
    {'=' * 72}
    {build_identity_text()}

    OpenShot BnR is the script you use when you are tired of spending a whole night
    arguing with prerequisites, shell paths, Python bindings, and launchers that
    almost work.

    It takes the expensive part of a source build — the uncertainty — and replaces it
    with a readable workflow.

    What it does well:
      - checks the machine before the costly steps begin
      - restores or installs the Windows/MSYS2 tooling it needs
      - builds the OpenShot native stack in order
      - verifies Python bindings honestly instead of faking success
      - repairs the runtime launch path so source-build mode actually launches
      - leaves behind logs, state files, helper launchers, and docs you can inspect

    Why that matters:
      Closed tools make you bend around their defaults.
      Open tools can bend toward your workflow.

      That means the value of the tool can keep rising, because you can script it,
      audit it, package it differently, and adapt it to the way you actually build
      and deliver software.

    Benefit:
      You spend less time guessing and more time shipping.

    Outcome:
      OpenShot BnR becomes a reusable asset instead of a one-night rescue script.

    For custom development:
      Trenton Tompkins
      (724) 431-5207
      trenttompkins@gmail.com
      {WEBSITE_URL}
    """).strip()


def build_version_text() -> str:
    return textwrap.dedent(f"""\
    {APP_FULL_NAME}
    {build_identity_text()}
    Repository: {REPO_URL}
    Website: {WEBSITE_URL}
    OpenShot docs: {OPENSHOT_DOCS_URL}
    """).strip()


def print_document(title: str, path: Path, fallback: str = "") -> None:
    print(title)
    print("=" * max(len(title), 24))
    content = read_local_text(path).strip()
    if content:
        print(content)
    elif fallback:
        print(fallback.strip())
    else:
        print(f"Document not found: {path}")


def build_debug_report() -> str:
    tools = {
        "python": sys.executable,
        "git": shutil.which("git") or "not found",
        "winget": shutil.which("winget") or "not found",
        "cmake": shutil.which("cmake") or "not found",
        "msys2_shell": str(MSYS_ROOT_DEFAULT / "msys2_shell.cmd") if (MSYS_ROOT_DEFAULT / "msys2_shell.cmd").exists() else "not found",
        "pacman": str(MSYS_ROOT_DEFAULT / "usr" / "bin" / "pacman.exe") if (MSYS_ROOT_DEFAULT / "usr" / "bin" / "pacman.exe").exists() else "not found",
    }
    lines = [
        APP_FULL_NAME,
        "=" * 72,
        f"Script path: {SCRIPT_PATH}",
        f"Script dir:  {SCRIPT_DIR}",
        f"Build root:   {BUILD_ROOT}",
        f"Windows:      {platform.platform()}",
        f"Python:       {platform.python_version()} ({sys.executable})",
        f"Admin:        {'yes' if is_windows() and is_admin() else 'no'}",
        f"README.md:    {'found' if README_MD_PATH.exists() else 'missing'} -> {README_MD_PATH}",
        f"INSTALL.md:   {'found' if INSTALL_MD_PATH.exists() else 'missing'} -> {INSTALL_MD_PATH}",
        f"MANUAL_INSTALL.md: {'found' if MANUAL_INSTALL_MD_PATH.exists() else 'missing'} -> {MANUAL_INSTALL_MD_PATH}",
        f"LOG_GUIDE.md: {'found' if LOG_GUIDE_MD_PATH.exists() else 'missing'} -> {LOG_GUIDE_MD_PATH}",
        f"TROUBLESHOOTING.md: {'found' if TROUBLESHOOTING_MD_PATH.exists() else 'missing'} -> {TROUBLESHOOTING_MD_PATH}",
        f"RELEASE_GUIDE.md: {'found' if RELEASE_GUIDE_MD_PATH.exists() else 'missing'} -> {RELEASE_GUIDE_MD_PATH}",
        f"CHANGELOG.md: {'found' if CHANGELOG_MD_PATH.exists() else 'missing'} -> {CHANGELOG_MD_PATH}",
        f"CONTRIBUTING.md: {'found' if CONTRIBUTING_MD_PATH.exists() else 'missing'} -> {CONTRIBUTING_MD_PATH}",
        f"SECURITY.md: {'found' if SECURITY_MD_PATH.exists() else 'missing'} -> {SECURITY_MD_PATH}",
        f"CODE_OF_CONDUCT.md: {'found' if CODE_OF_CONDUCT_MD_PATH.exists() else 'missing'} -> {CODE_OF_CONDUCT_MD_PATH}",
        f"LICENSE.txt:  {'found' if LICENSE_TXT_PATH.exists() else 'missing'} -> {LICENSE_TXT_PATH}",
        f"help.html:    {'found' if HELP_HTML_PATH.exists() else 'missing'} -> {HELP_HTML_PATH}",
        "",
        "Tool discovery:",
    ]
    for name, value in tools.items():
        lines.append(f"  - {name}: {value}")
    lines.extend([
        "",
        "Information command groups:",
        "  usage, help, man, about, version, docs, readme, install, manual-install, log-guide, troubleshooting, release-guide, changelog, contributing, security, code-of-conduct, license, debug",
    ])
    return "\n".join(lines)


def try_handle_information_flags(argv: Sequence[str]) -> Optional[int]:
    filtered = [arg for arg in argv[1:] if arg not in (CHILD_ARG, NO_PROMPT_ARG)]
    if not filtered:
        return None

    normalized = [normalize_cli_token(arg) for arg in filtered]

    alias_to_action = {}
    for aliases, action in [
        (USAGE_ALIASES, "usage"),
        (HELP_ALIASES, "help"),
        (MAN_ALIASES, "man"),
        (ABOUT_ALIASES, "about"),
        (VERSION_ALIASES, "version"),
        (DOCS_ALIASES, "docs"),
        (README_ALIASES, "readme"),
        (INSTALL_ALIASES, "install"),
        (MANUAL_INSTALL_ALIASES, "manual-install"),
        (LOG_GUIDE_ALIASES, "log-guide"),
        (TROUBLESHOOTING_ALIASES, "troubleshooting"),
        (RELEASE_GUIDE_ALIASES, "release-guide"),
        (CHANGELOG_ALIASES, "changelog"),
        (CONTRIBUTING_ALIASES, "contributing"),
        (SECURITY_ALIASES, "security"),
        (CODE_OF_CONDUCT_ALIASES, "code-of-conduct"),
        (LICENSE_ALIASES, "license"),
        (DEBUG_ALIASES, "debug"),
    ]:
        for alias in aliases:
            alias_to_action[alias.lower()] = action

    if not all(token in alias_to_action for token in normalized):
        return None

    def show(action: str) -> None:
        if action == "usage":
            print(build_usage_text())
        elif action == "help":
            print(build_help_text())
        elif action == "man":
            print(build_man_text())
        elif action == "about":
            print(build_about_text())
        elif action == "version":
            print(build_version_text())
        elif action == "docs":
            print(build_docs_index_text())
        elif action == "readme":
            print_document("README.md", README_MD_PATH, build_about_text())
        elif action == "install":
            print_document("INSTALL.md", INSTALL_MD_PATH, "INSTALL.md is missing from this folder.")
        elif action == "manual-install":
            print_document("MANUAL_INSTALL.md", MANUAL_INSTALL_MD_PATH, "MANUAL_INSTALL.md is missing from this folder.")
        elif action == "log-guide":
            print_document("LOG_GUIDE.md", LOG_GUIDE_MD_PATH, "LOG_GUIDE.md is missing from this folder.")
        elif action == "troubleshooting":
            print_document("TROUBLESHOOTING.md", TROUBLESHOOTING_MD_PATH, "TROUBLESHOOTING.md is missing from this folder.")
        elif action == "release-guide":
            print_document("RELEASE_GUIDE.md", RELEASE_GUIDE_MD_PATH, "RELEASE_GUIDE.md is missing from this folder.")
        elif action == "changelog":
            print_document("CHANGELOG.md", CHANGELOG_MD_PATH, "CHANGELOG.md is missing from this folder.")
        elif action == "contributing":
            print_document("CONTRIBUTING.md", CONTRIBUTING_MD_PATH, "CONTRIBUTING.md is missing from this folder.")
        elif action == "security":
            print_document("SECURITY.md", SECURITY_MD_PATH, "SECURITY.md is missing from this folder.")
        elif action == "code-of-conduct":
            print_document("CODE_OF_CONDUCT.md", CODE_OF_CONDUCT_MD_PATH, "CODE_OF_CONDUCT.md is missing from this folder.")
        elif action == "license":
            print_document("LICENSE.txt", LICENSE_TXT_PATH, "MIT License file is missing from this folder.")
        elif action == "debug":
            print(build_debug_report())

    shown = []
    seen = set()
    for token in normalized:
        action = alias_to_action[token]
        if action in seen:
            continue
        seen.add(action)
        shown.append(action)

    for index, action in enumerate(shown):
        show(action)
        if index < len(shown) - 1:
            print("\n" + "-" * 72 + "\n")

    return 0 if shown else None


def main() -> int:
    enable_ansi_colors()
    info_result = try_handle_information_flags(sys.argv)
    if info_result is not None:
        return info_result

    child_mode = CHILD_ARG in sys.argv
    no_prompt = NO_PROMPT_ARG in sys.argv

    if not is_windows():
        print(red("[FAIL]"), "This installer only supports Windows.", flush=True)
        return 1

    if child_mode:
        try:
            if not is_admin():
                raise RuntimeError("Elevated child started without admin rights.")
            ok("Running elevated")
            return do_install_work(prompt_at_end=not no_prompt)
        except Exception as exc:
            fail(str(exc))
            tb = traceback.format_exc()
            for line in tb.splitlines():
                trace(line)
            state = read_state()
            state["completed"] = True
            state["success"] = False
            state["exit_code"] = 1
            state["failed"] = True
            state["error"] = str(exc)
            state["traceback"] = tb
            state["finished"] = timestamp()
            write_state(state)
            finalize_bnr_output("child-exception")
            print_summary_from_state(state)
            return 1

    reset_state_files()
    rc = elevate_and_wait()
    state = read_state()
    print_summary_from_state(state)
    return rc


if __name__ == "__main__":
    sys.exit(main())
