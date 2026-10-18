# -*- coding: utf-8 -*-
"""
شاگرد بورس | دستیار بورسی — اعتبارسنج و سازندهٔ خروجی ایستا (dashboard/make_static.py)
پیش از هرگونه انتشار، سلامت و کامل بودن فایل‌های دادهٔ مشترک را بررسی می‌کند.
"""
import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

import build_data_layer  # noqa: E402
import build_options_data  # noqa: E402


def verify_outputs():
    data_dir = os.path.join(ROOT_DIR, "data")
    required = ["market.json", "signals.json", "portfolios.json", "fundamentals.json", "industries.json", "news.json", "options.json"]
    report = {}
    for fname in required:
        fpath = os.path.join(data_dir, fname)
        if not os.path.exists(fpath) or os.path.getsize(fpath) < 50:
            raise RuntimeError(f"فایل خروجی معتبر نیست یا ناقص است: {fname}")
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            report[fname] = os.path.getsize(fpath)
    index_path = os.path.join(ROOT_DIR, "index.html")
    if not os.path.exists(index_path) or os.path.getsize(index_path) < 1000:
        raise RuntimeError("فایل index.html یافت نشد یا ناقص است.")
    report["index.html"] = os.path.getsize(index_path)
    return report


def main():
    build_data_layer.build_all()
    build_options_data.build_options_json()
    rep = verify_outputs()
    print("[OK] Static verification passed:", json.dumps(rep))


if __name__ == "__main__":
    main()
