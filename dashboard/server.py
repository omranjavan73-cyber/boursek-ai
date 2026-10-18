# -*- coding: utf-8 -*-
"""
شاگرد بورس | دستیار بورسی — سرور محلی ایمن (dashboard/server.py)
- محدود به 127.0.0.1 (Localhost) به صورت پیش‌فرض برای امنیت
- محافظت در برابر Directory Traversal و عدم افشای مسیرهای داخلی در پیام‌های خطا
- ارائهٔ API خواندنی لایهٔ دادهٔ مشترک (/api/bundle) و وضعیت سلامت منابع (/api/health)
"""
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")

FORBIDDEN_PREFIXES = (".env", ".git", ".publish.lock")


class ShagerdSafeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        super().end_headers()

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        clean_path = parsed.path.lstrip("/")

        # جلوگیری از دسترسی به فایل‌های حساس یا مخفی
        for part in clean_path.split("/"):
            if part.startswith(".") or part.startswith(FORBIDDEN_PREFIXES) or "secret" in part.lower():
                self.send_json({"error": "دسترسی مجاز نیست (Forbidden)"}, status=403)
                return

        if parsed.path == "/api/health":
            files_status = {}
            for name in ("market.json", "signals.json", "portfolios.json", "fundamentals.json", "industries.json", "news.json", "options.json"):
                fpath = os.path.join(DATA_DIR, name)
                files_status[name] = {
                    "exists": os.path.exists(fpath),
                    "sizeBytes": os.path.getsize(fpath) if os.path.exists(fpath) else 0
                }
            self.send_json({"status": "ok", "product": "شاگرد بورس | دستیار بورسی", "files": files_status})
            return

        if parsed.path == "/api/bundle":
            bundle = {}
            for key in ("market", "signals", "portfolios", "fundamentals", "industries", "news", "options"):
                fpath = os.path.join(DATA_DIR, f"{key}.json")
                if os.path.exists(fpath):
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            bundle[key] = json.load(f)
                    except Exception:
                        bundle[key] = {"error": "خطا در خواندن فایل داده"}
                else:
                    bundle[key] = {"error": "فایل داده موجود نیست"}
            self.send_json(bundle)
            return

        return super().do_GET()

    def send_error(self, code, message=None, explain=None):
        """عدم افشای جزئیات مسیرهای سیستم در خطاهای عمومی"""
        self.send_json({"error": f"HTTP Error {code}", "status": code}, status=code)


def run_server():
    host = os.environ.get("SHAGERD_HOST", "127.0.0.1")
    port = int(os.environ.get("SHAGERD_PORT", "8080"))
    server = ThreadingHTTPServer((host, port), ShagerdSafeHandler)
    print(f"[OK] Shagerd Bourse Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Server stopped cleanly.")
        server.server_close()


if __name__ == "__main__":
    run_server()
