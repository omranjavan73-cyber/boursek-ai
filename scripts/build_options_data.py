# -*- coding: utf-8 -*-
"""
شاگرد بورس | دستیار بورسی — سازندهٔ لایهٔ دادهٔ ماژول آپشن‌ها (scripts/build_options_data.py)
تولید اتمیک data/options.json با استفاده از موتور ریاضی tools/options_engine.py
"""
import json
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tools.options_engine import (
    DEFAULT_RISK_FREE_RATE,
    DEFAULT_OPTION_FEE_RATE,
    DEFAULT_EXERCISE_FEE_RATE,
    solve_implied_volatility,
    bs_greeks,
    classify_moneyness,
    calc_tse_initial_margin,
    score_option_contract,
    evaluate_strategy_payoff,
)

DATA_DIR = os.path.join(ROOT_DIR, "data")
DUBAI_TZ = timezone(timedelta(hours=4))
TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))


def atomic_write_json(target_path: str, payload: dict):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_opt_", suffix=".json", dir=os.path.dirname(target_path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, target_path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


RAW_OPTION_CONTRACTS = [
    # ۱. زنجیره اختیار صندوق اهرم (SYM_AHROM - قیمت پایه: 72,946 ریال)
    {
        "contractId": "OPT_AHROM_C_70000_0705",
        "contractSymbol": "ضاهرم705",
        "contractTitle": "اختیار خرید اهرم - اعمال 70,000 - سررسید آذر 1405",
        "underlyingSymbol": "اهرم",
        "underlyingId": "SYM_AHROM",
        "optionType": "Call",
        "underlyingPrice": 72946,
        "strikePrice": 70000,
        "premium": 9450,
        "bid": 9380,
        "ask": 9520,
        "contractSize": 1000,
        "maturityDate": "1405/09/10",
        "daysToMaturity": 44,
        "volume": 28450,
        "valueTomanB": 26.88,
        "openInterest": 64200,
        "source": "اسنپ‌شات زنجیره اختیار + سبد H3",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_H3", "PORT_H1", "PORT_M2"]
    },
    {
        "contractId": "OPT_AHROM_C_75000_0706",
        "contractSymbol": "ضاهرم706",
        "contractTitle": "اختیار خرید اهرم - اعمال 75,000 - سررسید آذر 1405",
        "underlyingSymbol": "اهرم",
        "underlyingId": "SYM_AHROM",
        "optionType": "Call",
        "underlyingPrice": 72946,
        "strikePrice": 75000,
        "premium": 6680,
        "bid": 6610,
        "ask": 6750,
        "contractSize": 1000,
        "maturityDate": "1405/09/10",
        "daysToMaturity": 44,
        "volume": 34120,
        "valueTomanB": 22.79,
        "openInterest": 78500,
        "source": "اسنپ‌شات زنجیره اختیار + سبد H3",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_H3", "PORT_H1"]
    },
    {
        "contractId": "OPT_AHROM_C_80000_0707",
        "contractSymbol": "ضاهرم707",
        "contractTitle": "اختیار خرید اهرم - اعمال 80,000 - سررسید آذر 1405",
        "underlyingSymbol": "اهرم",
        "underlyingId": "SYM_AHROM",
        "optionType": "Call",
        "underlyingPrice": 72946,
        "strikePrice": 80000,
        "premium": 4420,
        "bid": 4320,
        "ask": 4520,
        "contractSize": 1000,
        "maturityDate": "1405/09/10",
        "daysToMaturity": 44,
        "volume": 19800,
        "valueTomanB": 8.75,
        "openInterest": 49100,
        "source": "اسنپ‌شات زنجیره اختیار",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_H3"]
    },
    {
        "contractId": "OPT_AHROM_P_70000_0705",
        "contractSymbol": "طاهرم705",
        "contractTitle": "اختیار فروش اهرم - اعمال 70,000 - سررسید آذر 1405",
        "underlyingSymbol": "اهرم",
        "underlyingId": "SYM_AHROM",
        "optionType": "Put",
        "underlyingPrice": 72946,
        "strikePrice": 70000,
        "premium": 3890,
        "bid": 3810,
        "ask": 3970,
        "contractSize": 1000,
        "maturityDate": "1405/09/10",
        "daysToMaturity": 44,
        "volume": 11400,
        "valueTomanB": 4.43,
        "openInterest": 22300,
        "source": "اسنپ‌شات زنجیره اختیار (پوشش ریسک)",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_H1", "PORT_M2"]
    },
    {
        "contractId": "OPT_AHROM_C_75000_NEAR",
        "contractSymbol": "ضاهرم628",
        "contractTitle": "اختیار خرید اهرم - اعمال 75,000 - سررسید آبان 1405 (نزدیک سررسید)",
        "underlyingSymbol": "اهرم",
        "underlyingId": "SYM_AHROM",
        "optionType": "Call",
        "underlyingPrice": 72946,
        "strikePrice": 75000,
        "premium": 1950,
        "bid": 1840,
        "ask": 2060,
        "contractSize": 1000,
        "maturityDate": "1405/08/07",
        "daysToMaturity": 11,
        "volume": 9200,
        "valueTomanB": 1.79,
        "openInterest": 31000,
        "source": "اسنپ‌شات زنجیره اختیار",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": []
    },
    # ۲. زنجیره اختیار ملی صنایع مس ایران - فملی (SYM_FAMELI - قیمت پایه: 31,370 ریال)
    {
        "contractId": "OPT_FAMELI_C_30000_0812",
        "contractSymbol": "ضفلا812",
        "contractTitle": "اختیار خرید فملی - اعمال 30,000 - سررسید دی 1405",
        "underlyingSymbol": "فملی",
        "underlyingId": "SYM_FAMELI",
        "optionType": "Call",
        "underlyingPrice": 31370,
        "strikePrice": 30000,
        "premium": 4650,
        "bid": 4600,
        "ask": 4700,
        "contractSize": 1000,
        "maturityDate": "1405/10/02",
        "daysToMaturity": 66,
        "volume": 24600,
        "valueTomanB": 11.44,
        "openInterest": 54000,
        "source": "اسنپ‌شات زنجیره اختیار",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_L1", "PORT_L3", "FUND_PROD"]
    },
    {
        "contractId": "OPT_FAMELI_C_34000_0813",
        "contractSymbol": "ضفلا813",
        "contractTitle": "اختیار خرید فملی - اعمال 34,000 - سررسید دی 1405",
        "underlyingSymbol": "فملی",
        "underlyingId": "SYM_FAMELI",
        "optionType": "Call",
        "underlyingPrice": 31370,
        "strikePrice": 34000,
        "premium": 2690,
        "bid": 2630,
        "ask": 2750,
        "contractSize": 1000,
        "maturityDate": "1405/10/02",
        "daysToMaturity": 66,
        "volume": 18900,
        "valueTomanB": 5.08,
        "openInterest": 41200,
        "source": "اسنپ‌شات زنجیره اختیار",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_L1", "PORT_L3"]
    },
    {
        "contractId": "OPT_FAMELI_P_30000_0812",
        "contractSymbol": "طفلا812",
        "contractTitle": "اختیار فروش فملی - اعمال 30,000 - سررسید دی 1405",
        "underlyingSymbol": "فملی",
        "underlyingId": "SYM_FAMELI",
        "optionType": "Put",
        "underlyingPrice": 31370,
        "strikePrice": 30000,
        "premium": 1720,
        "bid": 1680,
        "ask": 1760,
        "contractSize": 1000,
        "maturityDate": "1405/10/02",
        "daysToMaturity": 66,
        "volume": 8400,
        "valueTomanB": 1.44,
        "openInterest": 19500,
        "source": "اسنپ‌شات زنجیره اختیار (بیمه سبد بنیادی)",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_L1", "PORT_L3", "FUND_PROD"]
    },
    # ۳. زنجیره اختیار صندوق طلای عیار (SYM_AYAR - قیمت پایه: 712,879 ریال)
    {
        "contractId": "OPT_AYAR_C_700000_0904",
        "contractSymbol": "ضعیار904",
        "contractTitle": "اختیار خرید صندوق طلای عیار - اعمال 700,000 - سررسید آذر 1405",
        "underlyingSymbol": "عیار",
        "underlyingId": "SYM_AYAR",
        "optionType": "Call",
        "underlyingPrice": 712879,
        "strikePrice": 700000,
        "premium": 74500,
        "bid": 73900,
        "ask": 75100,
        "contractSize": 100,
        "maturityDate": "1405/09/18",
        "daysToMaturity": 52,
        "volume": 21500,
        "valueTomanB": 16.01,
        "openInterest": 38900,
        "source": "اسنپ‌شات زنجیره اختیار کالایی",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_OMIX_WEEKLY", "PORT_L1", "PORT_L2", "PORT_L3"]
    },
    {
        "contractId": "OPT_AYAR_P_700000_0904",
        "contractSymbol": "طعیار904",
        "contractTitle": "اختیار فروش صندوق طلای عیار - اعمال 700,000 - سررسید آذر 1405",
        "underlyingSymbol": "عیار",
        "underlyingId": "SYM_AYAR",
        "optionType": "Put",
        "underlyingPrice": 712879,
        "strikePrice": 700000,
        "premium": 29800,
        "bid": 29100,
        "ask": 30500,
        "contractSize": 100,
        "maturityDate": "1405/09/18",
        "daysToMaturity": 52,
        "volume": 6200,
        "valueTomanB": 1.85,
        "openInterest": 12400,
        "source": "اسنپ‌شات زنجیره اختیار کالایی",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_OMIX_WEEKLY", "PORT_L1"]
    },
    # ۴. زنجیره اختیار بانک ملت - وبملت (SYM_VBMELAT - قیمت پایه: 4,120 ریال)
    {
        "contractId": "OPT_VBMELAT_C_4000_0718",
        "contractSymbol": "ضملت718",
        "contractTitle": "اختیار خرید وبملت - اعمال 4,000 - سررسید آذر 1405",
        "underlyingSymbol": "وبملت",
        "underlyingId": "SYM_VBMELAT",
        "optionType": "Call",
        "underlyingPrice": 4120,
        "strikePrice": 4000,
        "premium": 510,
        "bid": 502,
        "ask": 518,
        "contractSize": 10000,
        "maturityDate": "1405/09/15",
        "daysToMaturity": 49,
        "volume": 14200,
        "valueTomanB": 7.24,
        "openInterest": None,  # نمونه واقعی از فیلد Open Interest ناموجود در منبع رایگان
        "source": "اسنپ‌شات زنجیره اختیار",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_L1", "PORT_L2", "PORT_M2"]
    },
    # ۵. زنجیره اختیار شتاب (SYM_SHETAB - قیمت پایه در پرتفوی واقعی: 54,360 ریال)
    {
        "contractId": "OPT_SHETAB_C_55000_0802",
        "contractSymbol": "ضشتاب802",
        "contractTitle": "اختیار خرید صندوق شتاب - اعمال 55,000 - سررسید آذر 1405",
        "underlyingSymbol": "شتاب",
        "underlyingId": "SYM_SHETAB",
        "optionType": "Call",
        "underlyingPrice": 54360,
        "strikePrice": 55000,
        "premium": 4850,
        "bid": 4650,
        "ask": 5050,
        "contractSize": 1000,
        "maturityDate": "1405/09/12",
        "daysToMaturity": 46,
        "volume": 6400,
        "valueTomanB": 3.10,
        "openInterest": 14800,
        "source": "اسنپ‌شات زنجیره اختیار",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["PORT_M3", "PORT_H3", "REAL_EASYTRADER"]
    },
    {
        "contractId": "OPT_SHETAB_P_55000_0802",
        "contractSymbol": "طشتاب802",
        "contractTitle": "اختیار فروش صندوق شتاب - اعمال 55,000 - سررسید آذر 1405 (فاقد مظنه خرید)",
        "underlyingSymbol": "شتاب",
        "underlyingId": "SYM_SHETAB",
        "optionType": "Put",
        "underlyingPrice": 54360,
        "strikePrice": 55000,
        "premium": 4120,
        "bid": 0,      # نمونه واقعی قرارداد بدون مظنه خرید معتبر جهت تست محافظت امتیازدهی
        "ask": 4450,
        "contractSize": 1000,
        "maturityDate": "1405/09/12",
        "daysToMaturity": 46,
        "volume": 180,
        "valueTomanB": 0.07,
        "openInterest": None,
        "source": "اسنپ‌شات زنجیره اختیار",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": ["REAL_EASYTRADER"]
    },
    # ۶. زنجیره اختیار ایران خودرو - خودرو (SYM_KHODRO - قیمت پایه: 2,380 ریال)
    {
        "contractId": "OPT_KHODRO_P_2400_0805",
        "contractSymbol": "طخود805",
        "contractTitle": "اختیار فروش خودرو - اعمال 2,400 - سررسید آذر 1405",
        "underlyingSymbol": "خودرو",
        "underlyingId": "SYM_KHODRO",
        "optionType": "Put",
        "underlyingPrice": 2380,
        "strikePrice": 2400,
        "premium": 245,
        "bid": 238,
        "ask": 252,
        "contractSize": 10000,
        "maturityDate": "1405/09/05",
        "daysToMaturity": 39,
        "volume": 19500,
        "valueTomanB": 4.77,
        "openInterest": 62000,
        "source": "اسنپ‌شات زنجیره اختیار",
        "dataTime": "1405/07/26 12:30",
        "linkedPortfolios": []
    }
]


def build_enriched_contracts():
    enriched = []
    for raw in RAW_OPTION_CONTRACTS:
        s = raw["underlyingPrice"]
        k = raw["strikePrice"]
        prem = raw["premium"]
        days = raw["daysToMaturity"]
        otype = raw["optionType"]
        csize = raw["contractSize"]
        bid = raw["bid"]
        ask = raw["ask"]

        m_info = classify_moneyness(s, k, otype)
        intrinsic = m_info["intrinsicValue"]
        time_val = max(0.0, prem - intrinsic)

        # نقطهٔ سربه‌سر با احتساب کارمزد خرید اختیار (0.103%) و اعمال (0.05%)
        entry_with_fee = prem * (1.0 + DEFAULT_OPTION_FEE_RATE)
        if otype.lower() == "call":
            breakeven = round((k + entry_with_fee) * (1.0 + DEFAULT_EXERCISE_FEE_RATE), 0)
            be_move_pct = round(((breakeven - s) / s) * 100.0, 2)
        else:
            breakeven = round((k - entry_with_fee) * (1.0 - DEFAULT_EXERCISE_FEE_RATE), 0)
            be_move_pct = round(((breakeven - s) / s) * 100.0, 2)

        # بررسی اعتبار مظنه Bid/Ask
        has_valid_quote = (bid > 0 and ask > 0 and ask >= bid)
        spread_rial = (ask - bid) if has_valid_quote else None
        spread_pct = round(((ask - bid) / ((ask + bid) / 2.0)) * 100.0, 2) if has_valid_quote else None

        # محاسبهٔ IV و یونانی‌ها فقط برای قراردادهای دارای مظنهٔ معتبر
        mid_price = ((bid + ask) / 2.0) if has_valid_quote else None
        iv_pct = solve_implied_volatility(mid_price, s, k, days, DEFAULT_RISK_FREE_RATE, otype) if has_valid_quote else None
        greeks = bs_greeks(s, k, days, iv_pct, DEFAULT_RISK_FREE_RATE, otype) if iv_pct is not None else None

        # اهرم مؤثر (Elasticity / Omega = Delta * (S / Premium))
        effective_leverage = round(abs(greeks["delta"]) * (s / prem), 2) if (greeks and prem > 0) else round(s / max(prem, 1), 2)

        # وجه تضمین اولیه فروشنده به ریال و تومان
        margin_rial = calc_tse_initial_margin(s, k, prem, csize, otype)
        margin_toman = round(margin_rial / 10.0, 0)

        item = {
            **raw,
            "moneynessStatus": m_info["status"],
            "moneynessLabel": m_info["label"],
            "strikeVsSpotPct": m_info["strikeVsSpotPct"],
            "intrinsicValue": intrinsic,
            "timeValue": time_val,
            "breakevenPrice": breakeven,
            "breakevenMovePct": be_move_pct,
            "hasValidQuote": has_valid_quote,
            "spreadRial": spread_rial,
            "spreadPct": spread_pct,
            "ivPct": iv_pct,
            "greeks": greeks,
            "effectiveLeverage": effective_leverage,
            "initialMarginRial": margin_rial,
            "initialMarginToman": margin_toman,
            "dataCompleteness": (
                "کامل و معتبر"
                if (has_valid_quote and raw["openInterest"] is not None)
                else ("مظنه معتبر (بدون داده Open Interest در منبع)" if has_valid_quote else "ناقص (فاقد مظنه خرید فعال)")
            )
        }
        score_info = score_option_contract(item)
        item["scoring"] = score_info
        enriched.append(item)

    return enriched


def build_options_json():
    dubai_now = datetime.now(DUBAI_TZ).isoformat(timespec="seconds")
    tehran_now = datetime.now(TEHRAN_TZ).isoformat(timespec="seconds")
    contracts = build_enriched_contracts()

    payload = {
        "schemaVersion": "1.0.0",
        "moduleName": "آپشن‌ها (Options Intelligence)",
        "updatedAtDubai": dubai_now,
        "updatedAtTehran": tehran_now,
        "dataFreshness": "snapshot_verified",
        "modelAssumptions": {
            "pricingModel": "Black-Scholes-Merton (European Exercise)",
            "riskFreeRateAnnualPct": 30.0,
            "optionTradeFeePct": 0.103,
            "optionExerciseFeePct": 0.05,
            "spotBuyFeePct": 0.3712,
            "spotSellFeePct": 0.88,
            "marginFormula": "TSE Standard (20% Spot - OTM, min 10% Strike + Premium)",
            "shortSellingSpotRule": "فروش استقراضی یک‌طرفه سهم پایه در بورس تهران برای عموم فعال نیست و صرفاً به عنوان سناریوی نظری (Theoretical Benchmark) در کنار خرید Put نمایش داده می‌شود."
        },
        "capabilityAndLimitationsMap": {
            "implementedNow": [
                "رادار اختیار خرید (Call) و فروش (Put) با فیلترهای چندگانه روی داده‌های واقعی",
                "محاسبهٔ تحلیلی نوسان‌پذیری ضمنی (IV) و یونانی‌ها (Delta, Gamma, Theta, Vega) بر پایه مدل بلک-شولز",
                "سیستم امتیازدهی وزن‌دار قابل تنظیم توسط کاربر با مسدودسازی خودکار امتیاز برای مظنه‌های نامعتبر",
                "آزمایشگاه استراتژی‌ها (تک‌قراردادی، پوشش‌دار، اسپردهای صعودی و نزولی) با نمودار سررسید و جدول 7 سناریو",
                "مقایسهٔ مستقیم خرید/فروش سهم پایه با استراتژی‌های اختیار در افق زمانی و سرمایهٔ یکسان",
                "اسکنر استراتژی‌های بازار و تحلیل پوشش ریسک سبدهای موجود بدون تغییر خودکار سبدها"
            ],
            "currentDataLimitations": [
                "به دلیل محدودیت شبکه (IP خارج از ایران / Asia/Dubai)، اتصال مستقیم بدون پراکسی به cdn.tsetmc.com مسدود (Timeout) است و داده از آخرین اسنپ‌شات معتبر پروژه تغذیه می‌شود.",
                "تاریخچهٔ کندلی دقیقه‌ای قراردادهای آپشن و تغییرات تاریخی Open Interest در منابع رایگان فعلی وجود ندارد و از شبیه‌سازی فرضی به عنوان بک‌تست تاریخی استفاده نشده است."
            ],
            "allowedUpgradePaths": [
                "استفاده از پل ابری Google Apps Script یا Cloudflare Worker برای دریافت زنجیره کامل GetInstrumentOptionMarketWatch از TSETMC",
                "بارگذاری فایل CSV/JSON خروجی دیده‌بان اختیار معامله ره‌آورد365 یا TSETMC در پنل تنظیمات"
            ]
        },
        "totalContracts": len(contracts),
        "validQuotedContracts": sum(1 for c in contracts if c["hasValidQuote"]),
        "incompleteContracts": sum(1 for c in contracts if not c["hasValidQuote"]),
        "contracts": contracts
    }

    target = os.path.join(DATA_DIR, "options.json")
    atomic_write_json(target, payload)
    return payload


if __name__ == "__main__":
    res = build_options_json()
    print(f"[OK] data/options.json built with {res['totalContracts']} contracts ({res['validQuotedContracts']} valid quotes, {res['incompleteContracts']} incomplete).")
