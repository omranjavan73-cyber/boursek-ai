# -*- coding: utf-8 -*-
"""
شاگرد بورس | دستیار بورسی — ماژول ارزیابی استراتژی‌ها و رژیم بازار (tools/strategies.py)
"""

REGIME_ALLOCATIONS = {
    "bull": {
        "id": "bull",
        "label": "صعودی تهاجمی (Bullish Momentum)",
        "stocksAndLeveragedPct": 95,
        "safeAndCashPct": 5,
        "description": "کاهش وزن طلا/نقد به حداقل ممکن (0% تا 5%) و تمرکز بر صندوق‌های اهرمی و نمادهای پیش‌صف."
    },
    "neutral": {
        "id": "neutral",
        "label": "تعادلی و نوسانی (Sideways / Swing)",
        "stocksAndLeveragedPct": 80,
        "safeAndCashPct": 20,
        "description": "نوسان‌گیری با الگوی ساعت (تیک صعودی)، آربیتراژ حباب اهرمی‌ها و نگهداری 15% تا 20% نقد/طلا."
    },
    "bear": {
        "id": "bear",
        "label": "نزولی تدافعی (Bearish / High-Risk)",
        "stocksAndLeveragedPct": 55,
        "safeAndCashPct": 45,
        "description": "افزایش موقت سپر طلا/نقد و تمرکز صرف بر تک‌سهم‌های دارویی و صادراتی ضدریزش با تقاضای سرخط."
    }
}


def detect_regime_from_flow(real_money_flow_b: float, positive_symbols_pct: float) -> str:
    """تشخیص خودکار رژیم بازار بر اساس جریان پول حقیقی و درصد نمادهای مثبت"""
    if real_money_flow_b >= 250 and positive_symbols_pct >= 60:
        return "bull"
    if real_money_flow_b <= -300 or positive_symbols_pct <= 35:
        return "bear"
    return "neutral"
