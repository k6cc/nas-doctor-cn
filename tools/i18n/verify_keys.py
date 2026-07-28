#!/usr/bin/env python3
"""Verify en.json / zh.json key alignment and report statistics.

Usage:
    python tools/i18n/verify_keys.py

Checks:
1. Both files have the same number of keys
2. No key exists in one file but not the other
3. No empty values
4. Reports key count by namespace prefix
"""
import json
import os
import sys
from collections import Counter

LOCALE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'internal', 'api', 'i18n', 'locales')

def load_json(filename):
    path = os.path.join(LOCALE_DIR, filename)
    if not os.path.exists(path):
        print(f"ERROR: {filename} not found at {path}")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    en = load_json('en.json')
    zh = load_json('zh.json')

    ek, zk = set(en.keys()), set(zh.keys())
    only_en = ek - zk
    only_zh = zk - ek

    print(f"en.json: {len(en)} keys")
    print(f"zh.json: {len(zh)} keys")
    print(f"Alignment: {'OK' if not only_en and not only_zh else 'MISMATCH'}")

    if only_en:
        print(f"\n  Only in en.json ({len(only_en)}):")
        for k in sorted(only_en)[:20]:
            print(f"    {k}")
    if only_zh:
        print(f"\n  Only in zh.json ({len(only_zh)}):")
        for k in sorted(only_zh)[:20]:
            print(f"    {k}")

    # Check for empty values
    empty_en = [k for k, v in en.items() if not v]
    empty_zh = [k for k, v in zh.items() if not v]
    if empty_en:
        print(f"\n  Empty values in en.json ({len(empty_en)}): {empty_en[:10]}")
    if empty_zh:
        print(f"\n  Empty values in zh.json ({len(empty_zh)}): {empty_zh[:10]}")

    # Key namespace stats
    ns = Counter()
    for k in en:
        prefix = k.split('.')[0]
        ns[prefix] += 1
    print(f"\nKey count by namespace:")
    for prefix, count in ns.most_common():
        print(f"  {prefix:30s} {count:4d}")

    return 0 if not only_en and not only_zh else 1

if __name__ == '__main__':
    sys.exit(main())
