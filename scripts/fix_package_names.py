#!/usr/bin/env python3
"""Fix package names to use real Android package identifiers."""

import json
import sys
from pathlib import Path

# Mapping from simplified names to actual Android package names
PACKAGE_NAME_MAP = {
    # Work apps
    "slack": "com.slack",
    "teams": "com.microsoft.teams",
    "gmail": "com.google.android.gm",
    "outlook": "com.microsoft.office.outlook",
    "jira": "com.atlassian.jira.core",
    "github": "com.github.android",
    "linear": "com.linear.app",
    "notion": "notion.id",
    "asana": "com.asana.app",
    "monday": "com.monday.monday",
    "feishu": "com.ss.android.lark",
    "lark": "com.ss.android.lark",
    "dingtalk": "com.alibaba.android.rimet",

    # Personal apps
    "whatsapp": "com.whatsapp",
    "wechat": "com.tencent.mm",
    "douyin": "com.ss.android.ugc.aweme",
    "rednote": "com.xingin.xhs",
    "xiaohongshu": "com.xingin.xhs",
    "telegram": "org.telegram.messenger",
    "imessage": "com.apple.mobilesms",  # Theoretical for cross-platform
    "messenger": "com.facebook.orca",
    "viber": "com.viber.voip",
    "snapchat": "com.snapchat.android",
    "twitter": "com.twitter.android",
    "instagram": "com.instagram.android",
    "line": "jp.naver.line.android",

    # Promotions apps
    "amazon": "com.amazon.mShop.android.shopping",
    "shopee": "com.shopee.ph",
    "lazada": "com.lazada.android",
    "target": "com.target.ui",
    "walmart": "com.walmart.android",
    "ebay": "com.ebay.mobile",
    "aliexpress": "com.alibaba.aliexpresshd",
    "hm": "com.hm.goe",
    "h&m": "com.hm.goe",
    "clothing_store": "com.hm.goe",
    "newsletter": "com.newsletter.app",
    "coupon_app": "com.rmn.mobile.coupons",
    "coupon": "com.rmn.mobile.coupons",

    # Alerts apps
    "chase": "com.chase.sig.android",
    "bofa": "com.infonow.bofa",
    "wellsfargo": "com.wf.wellsfargomobile",
    "ups": "com.ups.mobile.android",
    "fedex": "com.fedex.ida.android",
    "usps": "com.usps.mobile.usps",
    "uber": "com.ubercab",
    "doordash": "com.dd.doordash",
    "system": "android",
    "calendar": "com.google.android.calendar",
}

def fix_file(filepath: Path) -> tuple[int, int]:
    """Fix package names in a file. Returns (total, changed)."""
    lines = []
    changed = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
                old_app = entry["notification"]["app"]

                if old_app in PACKAGE_NAME_MAP:
                    new_app = PACKAGE_NAME_MAP[old_app]
                    entry["notification"]["app"] = new_app
                    changed += 1

                lines.append(json.dumps(entry, ensure_ascii=False))
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error in {filepath}: {e}")
                lines.append(line)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')

    return len(lines), changed

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_package_names.py <file.jsonl> [file2.jsonl ...]")
        sys.exit(1)

    total_files = 0
    total_entries = 0
    total_changed = 0

    for filepath in sys.argv[1:]:
        path = Path(filepath)
        if not path.exists():
            print(f"File not found: {filepath}")
            continue

        count, changed = fix_file(path)
        total_files += 1
        total_entries += count
        total_changed += changed

        print(f"{filepath}: {changed}/{count} entries updated")

    print(f"\nSummary:")
    print(f"Files processed: {total_files}")
    print(f"Total entries: {total_entries}")
    print(f"Package names updated: {total_changed}")

if __name__ == "__main__":
    main()
