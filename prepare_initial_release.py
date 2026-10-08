#!/usr/bin/env python3
"""Prepare the complete first Plektra asset release from verified upstream assets."""

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TAG = "v1"
REPOSITORY = "pkb-rocks/plektra-dict"


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(output):
    if output.exists():
        raise ValueError(f"Output already exists: {output}")
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifests = {}
    assets = []
    provenance = []
    for kind in ("dicts", "layouts"):
        upstream = json.loads((ROOT / "docs/upstream-manifests" / f"{kind}-manifest.json").read_text())
        manifest = {**upstream, "generatedAt": now, "releaseTag": TAG, "items": []}
        for original in upstream["items"]:
            filename = original["filename"]
            if Path(filename).name != filename:
                raise ValueError(f"Invalid asset filename: {filename}")
            asset = ROOT / kind / filename
            digest = hashlib.sha256(asset.read_bytes()).hexdigest()
            if digest != original["sha256"] or asset.stat().st_size != original["bytes"]:
                raise ValueError(f"Upstream size/hash mismatch: {filename}")
            if kind == "layouts":
                layout = json.loads(asset.read_text())
                if not layout.get("name") or not layout.get("mappings"):
                    raise ValueError(f"Invalid keyboard layout: {filename}")
            manifest["items"].append({
                **original,
                "url": f"https://github.com/{REPOSITORY}/releases/download/{TAG}/{filename}",
            })
            assets.append(asset)
            provenance.append(f"| {filename} | {original['sha256']} | {original['url']} |")
        manifests[kind] = manifest

    output.mkdir(parents=True)
    for asset in assets:
        shutil.copyfile(asset, output / asset.name)
    shutil.copyfile(ROOT / "LICENSE", output / "LICENSE")
    (output / "PROVENANCE.md").write_text(
        "# Plektra dictionary and layout provenance\n\n"
        "Imported unchanged from palsoftware/pastiera-dict, commit "
        "243432ab0006d3f16c0792f8e78b17d983f48034.\n\n"
        "Corpus sources and license notices: "
        "https://github.com/pkb-rocks/plektra-dict/blob/main/docs/UPSTREAM_README.md\n\n"
        "The repository code is GPLv3. Corpus and database licenses remain as "
        "documented upstream; the Greek produced database is CC BY-SA 3.0.\n\n"
        "| Asset | SHA-256 | Original published asset |\n| --- | --- | --- |\n"
        + "\n".join(provenance) + "\n", encoding="utf-8"
    )
    (output / "RELEASE_NOTES.md").write_text(
        "# Plektra dictionaries and layouts v1\n\n"
        f"Complete initial collection: {len(manifests['dicts']['items'])} dictionaries "
        f"and {len(manifests['layouts']['items'])} keyboard layouts.\n\n"
        "All assets retain their upstream bytes, hashes and identifiers. "
        "See PROVENANCE.md for original release URLs and source/license notices.\n\n"
        "Dictionary manifest: https://pkb.rocks/plektra-dict/dicts-manifest.json\n\n"
        "Layout manifest: https://pkb.rocks/plektra-dict/layouts-manifest.json\n",
        encoding="utf-8"
    )
    checksums = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}"
        for path in sorted(output.iterdir()) if path.is_file()
    ]
    (output / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    for kind, manifest in manifests.items():
        write_json(ROOT / "docs" / f"{kind}-manifest.json", manifest)
    print(f"Prepared {len(assets)} verified assets and release metadata at {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.output.resolve())
