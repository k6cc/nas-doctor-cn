#!/usr/bin/env python3
"""Add i18n keys to en.json and zh.json in bulk.

Usage:
    python tools/i18n/add_keys.py

Edit the KEYS_EN and KEYS_ZH dictionaries below before running.
Keys are merged into existing JSON files (existing keys are skipped).
Both files are sorted alphabetically after update.

This is the standard tool for adding new translation keys during i18n development.
"""
import json
import os

LOCALE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'internal', 'api', 'i18n', 'locales')

# ===== Edit these dictionaries with your new keys =====
KEYS_EN = {
    # "namespace.key": "English text",
}

KEYS_ZH = {
    # "namespace.key": "中文文本",
}
# ======================================================

def main():
    for filename, new_keys in [("en.json", KEYS_EN), ("zh.json", KEYS_ZH)]:
        if not new_keys:
            print(f"[{filename}] No keys to add (empty dictionary)")
            continue

        filepath = os.path.join(LOCALE_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        added, skipped = 0, 0
        for k, v in new_keys.items():
            if k not in data:
                data[k] = v
                added += 1
            else:
                skipped += 1

        data = dict(sorted(data.items()))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')

        print(f"[{filename}] Added {added}, Skipped {skipped}, Total: {len(data)}")

if __name__ == '__main__':
    main()
