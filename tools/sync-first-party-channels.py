#!/usr/bin/env python3
"""Sync packaged first-party Channel metadata into registry.json."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry.json"

# Marketplace-facing facts that are not executable manifest fields.
CHANNEL_METADATA = {
    "apple-reminders": ("read-only", "macOS Reminders list allowlist"),
    "clipboard-inbox": ("two-way", "Explicit macOS clipboard opt-in"),
    "command-queue": ("two-way", "Producer and consumer argv arrays"),
    "demo-inbox": ("two-way", "No account or credentials"),
    "discord": ("two-way", "Bot token and channel allowlist"),
    "folder-drop": ("two-way", "Explicit inbox and outbox folders"),
    "git-watch": ("read-only", "One local Git repository"),
    "github-issues": ("two-way", "Fine-grained token and repository allowlist"),
    "imessage": ("two-way", "Full Disk Access and chat allowlist"),
    "imap-mail": ("two-way", "IMAP account; SMTP optional"),
    "jira": ("two-way", "Jira URL, API token, and project allowlist"),
    "linear": ("two-way", "API token and team allowlist"),
    "mastodon": ("two-way", "Instance URL and access token"),
    "matrix": ("two-way", "Homeserver token and room allowlist"),
    "ntfy": ("two-way", "Server, topic allowlist, and optional token"),
    "rss-feed": ("read-only", "One or more HTTPS feed URLs"),
    "slack": ("two-way", "Bot token and channel ID"),
    "telegram": ("two-way", "Bot token and chat allowlist"),
    "webhook-inbox": ("two-way", "Shared secret; callback optional"),
}


def entry_for(slug: str) -> dict:
    directory = ROOT / "plugins" / slug
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    archive = ROOT / "dist" / f"{slug}-{version}.zip"
    if not archive.is_file():
        raise SystemExit(f"missing archive: {archive.relative_to(ROOT)}")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    mode, setup = CHANNEL_METADATA[slug]
    return {
        "kind": "channel",
        "id": manifest["id"],
        "name": manifest["name"].removesuffix(" Channel"),
        "description": manifest["description"],
        "mode": mode,
        "setup": setup,
        "author": "termite",
        "license": "MIT",
        "version": version,
        "homepage": manifest["homepage"],
        "file": f"dist/{slug}-{version}.zip",
        "sha256": digest,
        "sdk": "v1",
        "capabilities": manifest["capabilities"],
    }


def main() -> None:
    present = {
        path.parent.name for path in (ROOT / "plugins").glob("*/manifest.json")
        if "channels" in json.loads(path.read_text(encoding="utf-8")).get("capabilities", [])
    }
    expected = set(CHANNEL_METADATA)
    if present != expected:
        missing = sorted(expected - present)
        unknown = sorted(present - expected)
        raise SystemExit(f"Channel catalog mismatch; missing={missing}, unknown={unknown}")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    retained = [
        entry for entry in registry["entries"]
        if not (entry.get("kind") == "channel" and str(entry.get("id", "")).startswith("dev.termite."))
    ]
    insertion = next((index for index, entry in enumerate(retained) if entry.get("kind") == "plugin"), len(retained))
    channels = [entry_for(slug) for slug in sorted(CHANNEL_METADATA)]
    registry["entries"] = retained[:insertion] + channels + retained[insertion:]
    ids = {entry["id"] for entry in registry["entries"]}
    registry["featured"] = [item for item in registry["featured"] if item in ids]
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(f"synced {len(channels)} first-party Channels")


if __name__ == "__main__":
    main()
