# termite-registry

The index behind the termite marketplace: shaders, themes, rigs, Channel
connectors, and Extensions, browsable and installable from inside the terminal
(`Browse the Marketplace…` in the palette, or `termite marketplace install <id>`).

## How it works

- `registry.json` is the whole truth. termite fetches it, shows the entries,
  and installs from it. Merged to main = published; `git revert` = unpublished.
- **Content kinds live in this repo** — a shader is one `.metal` file, a
  theme one `.json`, a rig one `.conf`. Contributing is one PR with one file
  plus one entry in `registry.json`.
- **Extensions and Channels are reviewed archives** (`file` or `url` plus a
  pinned `sha256`), because
  they're native code. Big payloads (chromium's CEF) ship as a separate
  `payload` asset.
- CI compiles every shader (`tools/preamble.metal` + your file must build),
  parses every theme, checks every rig key, and verifies the schema.
  Run `tools/validate.py` locally before opening a PR.

## Contributing a shader

1. Fork. Copy any file in `shaders/` as a starting point — or start in
   termite itself (palette → New User Shader…, edit live, then
   `termite share`).
2. Your file implements `termite_main` (see any seed file for the contract;
   helpers `termite_hash/palette/textMask` come for free).
3. Add your entry to `registry.json` under `shaders/<you>/<name>.metal`,
   with a one-line description that earns its place.
4. `tools/validate.py`, then PR.

Themes (`{"name", "background", "foreground", "cursor?", "border?",
"ansi"[16]}`) and rigs (a `key = value` subset of termite's config:
theme/shader/font/cursor/border/spacing) work the same way.

## Extensions

An Extension is termite's standard folder — `manifest.json` + an executable,
speaking the HTTP SDK (see PLUGINS.md in the main repo) — zipped with
`tools/pack-plugin.sh`. Publish the zip as a GitHub Release on your own
repo and PR an entry with its URL, sha256, `sdk` version, and arch.
Native code is reviewed more carefully than content; keep the diff small
and the repo public.

## Channels

A Channel connector is a v1 Extension whose manifest requests `channels` and
whose registry entry uses `"kind": "channel"`. Add `events.read` when the
connector needs approved outbound replies. The validator checks local Channel
archives all the way through: pinned hash, safe paths, manifest id/version,
capability grant, and executable entrypoint. Start from:

```sh
termite channel new ./my-channel
termite extension validate ./my-channel
```

## License

Entries declare their own license (MIT for everything seeded here).
