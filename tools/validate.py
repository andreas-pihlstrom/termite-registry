#!/usr/bin/env python3
"""Validate the registry: schema, files present, every shader compiles,
every theme parses. CI runs this on every PR; merged = published.

Usage: tools/validate.py   (from anywhere; paths resolve from the repo root)
Exit 0 = publishable.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KINDS = {"shader", "theme", "rig", "patch", "plugin"}
REQUIRED = ["kind", "id", "name", "description", "author", "license", "version"]

errors = []


def err(msg):
    errors.append(msg)
    print(f"  ✗ {msg}")


def check_shader(entry, path: Path):
    if "termite_main" not in path.read_text():
        err(f"{entry['id']}: no termite_main")
        return
    preamble = (ROOT / "tools" / "preamble.metal").read_text()
    with tempfile.NamedTemporaryFile(suffix=".metal", mode="w", delete=False) as f:
        f.write(preamble + "\n" + path.read_text())
        tmp = f.name
    r = subprocess.run(
        ["xcrun", "-sdk", "macosx", "metal", "-c", tmp, "-o", "/dev/null"],
        capture_output=True, text=True)
    if r.returncode != 0:
        err(f"{entry['id']}: shader does not compile:\n{r.stderr[:400]}")


def check_theme(entry, path: Path):
    try:
        t = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        err(f"{entry['id']}: theme is not valid JSON ({e})")
        return
    for key in ("name", "background", "foreground", "ansi"):
        if key not in t:
            err(f"{entry['id']}: theme missing '{key}'")
    if len(t.get("ansi", [])) != 16:
        err(f"{entry['id']}: theme needs exactly 16 ansi colors")


def check_rig(entry, path: Path):
    known = {"theme", "shader", "font-family", "font-size", "line-height",
             "cursor-style", "cursor-blink", "hide-border", "margin",
             "opacity", "blur", "ghost-text", "smooth-cursor"}
    for n, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            err(f"{entry['id']}: rig line {n} is not key = value")
            continue
        key = line.split("=", 1)[0].strip()
        if key not in known:
            err(f"{entry['id']}: rig uses unknown key '{key}'")


def main():
    reg = json.loads((ROOT / "registry.json").read_text())
    entries = reg.get("entries", [])
    ids = set()
    print(f"validating {len(entries)} entries…")
    for e in entries:
        for key in REQUIRED:
            if key not in e:
                err(f"{e.get('id', '?')}: missing '{key}'")
        if e.get("kind") not in KINDS:
            err(f"{e.get('id', '?')}: unknown kind '{e.get('kind')}'")
        if e.get("id") in ids:
            err(f"{e.get('id')}: duplicate id")
        ids.add(e.get("id"))

        kind = e.get("kind")
        if kind == "plugin":
            if not (e.get("url") or e.get("file")):
                err(f"{e['id']}: plugin needs 'url' or 'file'")
            if e.get("url") and not e.get("sha256"):
                err(f"{e['id']}: remote plugin needs 'sha256'")
            continue

        rel = e.get("file")
        if not rel:
            err(f"{e.get('id', '?')}: content entry needs 'file'")
            continue
        path = ROOT / rel
        if not path.exists():
            err(f"{e['id']}: file missing: {rel}")
            continue
        if kind == "shader":
            check_shader(e, path)
        elif kind == "theme":
            check_theme(e, path)
        elif kind == "rig":
            check_rig(e, path)

    for f in reg.get("featured", []):
        if f.split(":", 1)[-1] not in ids:
            err(f"featured entry not in registry: {f}")

    if errors:
        print(f"\n{len(errors)} problem(s).")
        sys.exit(1)
    print("registry is publishable ✓")


if __name__ == "__main__":
    main()
