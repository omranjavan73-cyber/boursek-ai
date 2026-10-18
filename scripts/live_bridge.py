# -*- coding: utf-8 -*-
"""
Boursek PRO v6.0 AI — Python Live TSE Orderbook Bridge
پل ارتباطی پایتون برای دریافت زنده اطلاعات تابلو و ارسال به دیتابیس ابری فایربیس
"""
import json
import time
from urllib.request import Request, urlopen

FIREBASE_URL = "https://stock-21aa7-default-rtdb.europe-west1.firebasedatabase.app/live_market.json"
TABLOKHANI_API = "https://api.tablokhani.com/public/source-arena?endpoint=all&type=0"


def calculate_buyer_power(buy_vol, real_buyers, sell_vol, real_sellers):
    """فرمول استاندارد قدرت خریدار حقیقی در بورسک"""
    if not real_buyers or not real_sellers or not sell_vol:
        return 1.0
    per_capita_buy = buy_vol / max(real_buyers, 1)
    per_capita_sell = sell_vol / max(real_sellers, 1)
    return round(per_capita_buy / max(per_capita_sell, 1), 2)


def push_to_firebase(payload):
    req = Request(FIREBASE_URL, data=json.dumps(payload).encode("utf-8"), method="PUT")
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[!] Error pushing to Firebase: {e}")
        return False


def main():
    print("🚀 Boursek PRO v6.0 AI Live Bridge Started...")
    req = Request(TABLOKHANI_API, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
            count = len(data) if isinstance(data, list) else 0
            print(f"[+] Fetched {count} symbols from TSE.")
            payload = {
                "system": "Boursek PRO v6.0 AI",
                "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "totalCount": count,
                "status": "online",
                "source": "python-live-bridge-v6"
            }
            if push_to_firebase(payload):
                print("✅ Successfully synced with Firebase Realtime Database!")
    except Exception as e:
        print(f"[!] Fetch failed: {e}")


if __name__ == "__main__":
    main()
