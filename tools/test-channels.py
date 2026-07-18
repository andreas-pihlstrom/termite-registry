#!/usr/bin/env python3
"""Compile and run the offline test suite for every first-party Channel."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"


def fail(message: str) -> None:
    print(f"  x {message}", file=sys.stderr)
    raise SystemExit(1)


def check_example_secrets(value, package: str, path: str = "") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            field = f"{path}.{key}" if path else key
            if any(marker in key.lower() for marker in ("token", "password", "secret", "api_key")):
                if child not in ("", None, False, [], {}):
                    fail(f"{package}: {field} must be empty in config.example.json")
            check_example_secrets(child, package, field)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            check_example_secrets(child, package, f"{path}[{index}]")


def main() -> None:
    manifests = sorted(PLUGINS.glob("*/manifest.json"))
    if not manifests:
        fail("no first-party Channel manifests found")

    tested = 0
    for manifest_path in manifests:
        package = manifest_path.parent
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if "channels" not in manifest.get("capabilities", []):
            continue
        if package.name != "demo-inbox":
            readme = package / "README.md"
            example = package / "config.example.json"
            if not readme.is_file() or not example.is_file():
                fail(f"{package.name}: Channel needs README.md and config.example.json")
            try:
                example_value = json.loads(example.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                fail(f"{package.name}: invalid config.example.json: {exc}")
            check_example_secrets(example_value, package.name)
        entrypoint = package / manifest.get("entrypoint", "")
        if not entrypoint.is_file():
            fail(f"{package.name}: missing entrypoint")
        try:
            compile(entrypoint.read_text(encoding="utf-8"), str(entrypoint), "exec")
        except (OSError, SyntaxError) as exc:
            fail(f"{package.name}: entrypoint does not compile: {exc}")

        test_file = package / "test_channel.py"
        if test_file.is_file():
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "-v", test_file.name],
                cwd=package,
                env=env,
                timeout=60,
            )
            if result.returncode:
                fail(f"{package.name}: offline tests failed")
            tested += 1
        else:
            print(f"  - {package.name}: compiled (no offline test)")

    print(f"validated {len(manifests)} Channel sources; ran {tested} offline suites")


if __name__ == "__main__":
    main()
