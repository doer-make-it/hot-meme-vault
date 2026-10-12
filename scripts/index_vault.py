#!/usr/bin/env python3
"""扫描素材目录，解析文件名元数据，合并 sidecar 标签，生成 index.json。

用法:
    python index_vault.py vault/
    python index_vault.py vault/ --output vault/index.json

纯本地操作，不联网，不修改素材原件，只生成索引文件。
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


NAME_PATTERN = re.compile(
    r"^(?P<date>\d{8})_(?P<source>[^_]+)_(?P<name>[^_]+(?:_[^_]+)*?)_(?P<seq>\d{2})\.(?P<ext>[^.]+)$"
)

EXT_TO_TYPE = {
    ".jpg": "表情包", ".jpeg": "表情包", ".png": "表情包",
    ".webp": "表情包", ".gif": "动图",
    ".mp4": "视频片段", ".mov": "视频片段", ".webm": "视频片段",
    ".txt": "文字金句", ".md": "文字金句",
}


def parse_filename(path: Path):
    m = NAME_PATTERN.match(path.name)
    if not m:
        return None
    date = m.group("date")
    source = m.group("source")
    name = m.group("name")
    seq = m.group("seq")
    try:
        dt = datetime.strptime(date, "%Y%m%d")
    except ValueError:
        dt = None
    return {
        "file": path.name,
        "collected_date": date,
        "collected_iso": dt.isoformat() if dt else None,
        "source": [source],
        "meme_name": name,
        "sequence": int(seq),
        "type": [EXT_TO_TYPE.get(path.suffix.lower(), "未分类")],
    }


def load_sidecar(path: Path):
    sidecar = path.with_suffix(path.suffix + ".json")
    if not sidecar.exists():
        sidecar = path.parent / (path.stem + ".json")
    if not sidecar.exists():
        return None
    try:
        with open(sidecar, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def merge_tags(meta, sidecar):
    if not sidecar:
        meta["tags"] = {
            "mood": [], "scene": [], "type": meta.get("type", []),
            "source": meta.get("source", []),
            "time": {"collected": meta.get("collected_date"), "trend": "未知"},
            "heat": [],
        }
        meta["verified"] = meta.get("source", ["未知"]) != ["未知"]
        return meta
    tags = sidecar.get("tags", {})
    if not tags.get("type"):
        tags["type"] = meta.get("type", [])
    if not tags.get("source"):
        tags["source"] = meta.get("source", [])
    if "time" not in tags:
        tags["time"] = {"collected": meta.get("collected_date"), "trend": "未知"}
    elif not tags["time"].get("collected"):
        tags["time"]["collected"] = meta.get("collected_date")
    meta["tags"] = tags
    meta["verified"] = sidecar.get("verified", meta.get("source", ["未知"]) != ["未知"])
    if sidecar.get("source_url"):
        meta["source_url"] = sidecar["source_url"]
    if sidecar.get("timestamp"):
        meta["timestamp"] = sidecar["timestamp"]
    if sidecar.get("note"):
        meta["note"] = sidecar["note"]
    return meta


def index_vault(vault_dir: Path, output: Path):
    entries = []
    skipped = []
    for sub in ("images", "videos", "texts"):
        subdir = vault_dir / sub
        if not subdir.exists():
            continue
        for path in sorted(subdir.iterdir()):
            if path.is_dir():
                continue
            if path.suffix.lower() == ".json":
                continue
            meta = parse_filename(path)
            if not meta:
                skipped.append(str(path.relative_to(vault_dir)))
                continue
            sidecar = load_sidecar(path)
            meta = merge_tags(meta, sidecar)
            meta["relative_path"] = str(path.relative_to(vault_dir)).replace("\\", "/")
            meta["absolute_path"] = str(path)
            entries.append(meta)
    index = {
        "vault": str(vault_dir),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total": len(entries),
        "skipped": skipped,
        "entries": entries,
    }
    with open(output, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"索引完成: {len(entries)} 条素材, {len(skipped)} 条跳过(命名不规范)")
    print(f"输出: {output}")
    return index


def main():
    ap = argparse.ArgumentParser(description="扫描素材目录生成 index.json")
    ap.add_argument("vault", help="素材库根目录 (含 images/videos/texts)")
    ap.add_argument("--output", "-o", default=None, help="索引输出路径, 默认 vault/index.json")
    args = ap.parse_args()
    vault = Path(args.vault)
    if not vault.exists():
        sys.exit(f"目录不存在: {vault}")
    out = Path(args.output) if args.output else vault / "index.json"
    index_vault(vault, out)


if __name__ == "__main__":
    main()
