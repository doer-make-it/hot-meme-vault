#!/usr/bin/env python3
"""按标签/关键词检索素材库。依赖 index_vault.py 生成的 index.json。

用法:
    python search.py vault/ --tags "情绪:无语,场景:职场"
    python search.py vault/ --keyword "我真无语"
    python search.py vault/ --tags "热度:爆款" --keyword 打工人
    python search.py vault/ --list-tags

纯本地读取, 不联网, 不修改任何文件。
"""

import argparse
import json
import sys
from pathlib import Path


TAG_KEY_MAP = {
    "情绪": "mood", "mood": "mood",
    "场景": "scene", "scene": "scene",
    "类型": "type", "type": "type",
    "来源": "source", "source": "source",
    "热度": "heat", "heat": "heat",
}


def load_index(vault: Path):
    idx_file = vault / "index.json"
    if not idx_file.exists():
        sys.exit(f"未找到索引 {idx_file}, 请先运行 index_vault.py")
    with open(idx_file, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_tags(tag_str):
    """解析 '情绪:无语,场景:职场' -> [('mood','无语'),('scene','职场')]"""
    if not tag_str:
        return []
    out = []
    for pair in tag_str.split(","):
        pair = pair.strip()
        if not pair or ":" not in pair:
            continue
        k, v = pair.split(":", 1)
        k = k.strip()
        v = v.strip()
        key = TAG_KEY_MAP.get(k)
        if not key:
            print(f"警告: 未知标签维度 '{k}', 跳过", file=sys.stderr)
            continue
        out.append((key, v))
    return out


def match(entry, tags, keyword):
    if not tags and not keyword:
        return True
    ok = True
    if tags:
        etags = entry.get("tags", {})
        for key, val in tags:
            vals = etags.get(key, [])
            if isinstance(vals, list):
                if val not in vals:
                    ok = False
                    break
            elif vals != val:
                ok = False
                break
    if ok and keyword:
        haystack = " ".join([
            entry.get("meme_name", ""),
            entry.get("file", ""),
            " ".join(entry.get("tags", {}).get("mood", [])),
            " ".join(entry.get("tags", {}).get("scene", [])),
            entry.get("note", "") or "",
        ])
        if keyword.lower() not in haystack.lower():
            ok = False
    return ok


def list_tags(index):
    from collections import Counter
    counts = {}
    for dim in ("mood", "scene", "type", "source", "heat"):
        c = Counter()
        for e in index["entries"]:
            for v in e.get("tags", {}).get(dim, []):
                c[v] += 1
        counts[dim] = c
    print(f"共 {index['total']} 条素材, 标签分布:")
    for dim, c in counts.items():
        print(f"\n[{dim}]")
        for v, n in c.most_common():
            print(f"  {v}: {n}")


def main():
    ap = argparse.ArgumentParser(description="检索素材库")
    ap.add_argument("vault", help="素材库根目录")
    ap.add_argument("--tags", "-t", default=None, help="标签过滤, 格式 '情绪:无语,场景:职场'")
    ap.add_argument("--keyword", "-k", default=None, help="关键词模糊匹配梗名/文件名")
    ap.add_argument("--list-tags", action="store_true", help="列出所有标签及计数")
    ap.add_argument("--paths-only", action="store_true", help="只输出路径(便于喂给剪辑工具)")
    args = ap.parse_args()

    vault = Path(args.vault)
    index = load_index(vault)

    if args.list_tags:
        list_tags(index)
        return

    tags = parse_tags(args.tags)
    results = [e for e in index["entries"] if match(e, tags, args.keyword)]

    if not results:
        print("没有匹配的素材")
        return

    print(f"匹配 {len(results)} 条:")
    if args.paths_only:
        for e in results:
            print(e["absolute_path"])
    else:
        for e in results:
            mood = ",".join(e["tags"].get("mood", []))
            scene = ",".join(e["tags"].get("scene", []))
            heat = ",".join(e["tags"].get("heat", []))
            print(f"  {e['relative_path']}  [{mood}|{scene}|{heat}]")


if __name__ == "__main__":
    main()
