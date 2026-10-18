# -*- coding: utf-8 -*-
"""
شاگرد بورس | دستیار بورسی — ماژول متمرکز فرمول‌های فیلتر و تابلوخوانی (tools/filters.py)
جلوگیری از تکرار کد محاسباتی در بخش‌های مختلف پروژه.
"""


def calc_buyer_power(buy_vol: float, real_buyers: int, sell_vol: float, real_sellers: int) -> float:
    """محاسبهٔ قدرت خریدار حقیقی: سرانه خرید تقسیم بر سرانه فروش"""
    if real_buyers <= 0 or real_sellers <= 0 or sell_vol <= 0:
        return 1.0
    per_capita_buy = buy_vol / real_buyers
    per_capita_sell = sell_vol / real_sellers
    return round(per_capita_buy / per_capita_sell, 2)


def calc_etf_bubble_pct(market_price: float, nav: float) -> float:
    """محاسبهٔ درصد حباب صندوق‌های اهرمی و کالایی"""
    if nav <= 0:
        return 0.0
    return round(((market_price - nav) / nav) * 100.0, 2)


def check_asiatech_filter(price_change_pct: float, bid_ask_ratio: float, buyer_power: float) -> bool:
    """منطق فیلتر آسیاتک (شکار پیش از قفل صف خرید)"""
    return (2.0 <= price_change_pct <= 3.85) and (bid_ask_ratio >= 3.0) and (buyer_power >= 2.2)


def check_exit_warning(buyer_power: float, real_flow_b: float) -> bool:
    """منطق فیلتر هشدار خروج / نخر"""
    return (buyer_power < 0.70) and (real_flow_b < -1.5)
