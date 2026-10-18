# -*- coding: utf-8 -*-
"""
شاگرد بورس | دستیار بورسی — موتور محاسباتی و تحلیلی اختیار معامله (tools/options_engine.py)
شامل:
1. قیمت‌گذاری بلک-شولز (Black-Scholes) و محاسبهٔ تحلیلی یونانی‌ها (Delta, Gamma, Theta, Vega)
2. استخراج نوسان‌پذیری ضمنی (Implied Volatility - IV) به روش ترکیبی نیوتن-رافسون و دوبخشی (Bisection)
3. محاسبهٔ نقطهٔ سربه‌سر، اهرم مؤثر، کارمزد بورس تهران و وجه تضمین اولیه (Initial Margin)
4. آزمایشگاه استراتژی‌ها (تک‌قراردادی، پوشش‌دار، اسپردهای ترکیبی) و مقایسه با سهم پایه
5. سیستم امتیازدهی شفاف و وزن‌دار با تشخیص خودکار نقص داده یا مظنه نامعتبر
"""
import math
from typing import Dict, Any, List, Optional

# مفروضات پایه بازار آپشن بورس تهران (قابل تنظیم توسط کاربر در رابط کاربری)
DEFAULT_RISK_FREE_RATE = 0.30       # نرخ بازده بدون ریسک سالانه (معادل اخزا ~ 30%)
DEFAULT_OPTION_FEE_RATE = 0.00103   # کارمزد معاملات اختیار در بورس تهران (0.103% در هر سمت خرید/فروش)
DEFAULT_EXERCISE_FEE_RATE = 0.0005  # کارمزد اعمال قرارداد (0.05%)
DEFAULT_SPOT_BUY_FEE = 0.003712     # کارمزد خرید سهام عادی (0.3712%)
DEFAULT_SPOT_SELL_FEE = 0.0088      # کارمزد فروش سهام عادی (0.88%)


def norm_cdf(x: float) -> float:
    """تابع توزیع تجمعی نرمال استاندارد N(x)"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_pdf(x: float) -> float:
    """تابع چگالی احتمال نرمال استاندارد N'(x)"""
    return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * x * x)


def bs_price(s: float, k: float, t_years: float, r: float, sigma: float, option_type: str = "call") -> float:
    """محاسبهٔ قیمت نظری اختیار معامله اروپایی بر اساس مدل بلک-شولز"""
    if s <= 0 or k <= 0:
        return 0.0
    if t_years <= 0 or sigma <= 0:
        return max(0.0, s - k) if option_type.lower() == "call" else max(0.0, k - s)

    sqrt_t = math.sqrt(t_years)
    d1 = (math.log(s / k) + (r + 0.5 * sigma * sigma) * t_years) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t

    if option_type.lower() == "call":
        return s * norm_cdf(d1) - k * math.exp(-r * t_years) * norm_cdf(d2)
    else:
        return k * math.exp(-r * t_years) * norm_cdf(-d2) - s * norm_cdf(-d1)


def solve_implied_volatility(
    market_price: float,
    s: float,
    k: float,
    days_to_maturity: int,
    r: float = DEFAULT_RISK_FREE_RATE,
    option_type: str = "call"
) -> Optional[float]:
    """
    محاسبهٔ نوسان‌پذیری ضمنی (IV) به صورت درصد سالانه از روی قیمت بازار.
    اگر قیمت بازار کمتر از ارزش ذاتی تنزیل‌شده باشد یا داده نامعتبر باشد، None برمی‌گرداند.
    """
    if market_price <= 0 or s <= 0 or k <= 0 or days_to_maturity <= 0:
        return None

    t_years = days_to_maturity / 365.0
    # بررسی حد پایین آربیتراژی
    if option_type.lower() == "call":
        intrinsic_disc = max(0.0, s - k * math.exp(-r * t_years))
    else:
        intrinsic_disc = max(0.0, k * math.exp(-r * t_years) - s)

    if market_price < intrinsic_disc * 0.98:
        return None

    low_vol = 0.01
    high_vol = 4.00
    for _ in range(60):
        mid_vol = 0.5 * (low_vol + high_vol)
        est = bs_price(s, k, t_years, r, mid_vol, option_type)
        diff = est - market_price
        if abs(diff) < 1e-2:
            return round(mid_vol * 100.0, 2)
        if diff > 0:
            high_vol = mid_vol
        else:
            low_vol = mid_vol

    final_vol = 0.5 * (low_vol + high_vol)
    if 0.015 < final_vol < 3.95:
        return round(final_vol * 100.0, 2)
    return None


def bs_greeks(
    s: float,
    k: float,
    days_to_maturity: int,
    sigma_pct: Optional[float],
    r: float = DEFAULT_RISK_FREE_RATE,
    option_type: str = "call"
) -> Optional[Dict[str, float]]:
    """
    محاسبهٔ یونانی‌ها (Delta, Gamma, Theta روزانه، Vega به ازای 1% تغییر نوسان).
    فقط در صورت وجود نوسان‌پذیری معتبر (sigma_pct) خروجی تولید می‌کند.
    """
    if sigma_pct is None or sigma_pct <= 0 or s <= 0 or k <= 0 or days_to_maturity <= 0:
        return None

    sigma = sigma_pct / 100.0
    t_years = days_to_maturity / 365.0
    sqrt_t = math.sqrt(t_years)
    d1 = (math.log(s / k) + (r + 0.5 * sigma * sigma) * t_years) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t
    pdf_d1 = norm_pdf(d1)

    if option_type.lower() == "call":
        delta = norm_cdf(d1)
        theta_annual = -(s * pdf_d1 * sigma) / (2.0 * sqrt_t) - r * k * math.exp(-r * t_years) * norm_cdf(d2)
    else:
        delta = norm_cdf(d1) - 1.0
        theta_annual = -(s * pdf_d1 * sigma) / (2.0 * sqrt_t) + r * k * math.exp(-r * t_years) * norm_cdf(-d2)

    gamma = pdf_d1 / (s * sigma * sqrt_t)
    theta_daily = theta_annual / 365.0
    vega_pct = (s * pdf_d1 * sqrt_t) / 100.0

    return {
        "delta": round(delta, 3),
        "gamma": round(gamma, 6),
        "thetaDaily": round(theta_daily, 2),
        "vega": round(vega_pct, 2)
    }


def classify_moneyness(s: float, k: float, option_type: str = "call") -> Dict[str, Any]:
    """تعیین وضعیت ITM / ATM / OTM و درصد فاصلهٔ قیمت اعمال از قیمت سهم پایه"""
    if s <= 0 or k <= 0:
        return {"status": "نامشخص", "distancePct": 0.0, "intrinsicValue": 0.0}

    dist_pct = ((k - s) / s) * 100.0
    if option_type.lower() == "call":
        intrinsic = max(0.0, s - k)
        ratio = (s - k) / s
    else:
        intrinsic = max(0.0, k - s)
        ratio = (k - s) / s

    if abs(ratio) <= 0.03:
        status = "ATM"
        label = "نزدیک به قیمت اعمال (ATM)"
    elif ratio > 0.03:
        status = "ITM"
        label = "در سود (ITM)"
    else:
        status = "OTM"
        label = "خارج از سود (OTM)"

    return {
        "status": status,
        "label": label,
        "strikeVsSpotPct": round(dist_pct, 2),
        "intrinsicValue": round(intrinsic, 0)
    }


def calc_tse_initial_margin(s: float, k: float, premium: float, contract_size: int, option_type: str = "call") -> float:
    """
    فرمول استاندارد وجه تضمین اولیه فروش اختیار معامله در بورس تهران (به ریال):
    Margin = ContractSize * (Premium + max(A * S - OTM_Amount, B * Strike))
    که در بورس تهران ضریب A معمولاً 20% و ضریب B برابر 10% است (گردشده به بالا در مضارب 10,000 ریال).
    """
    a_factor = 0.20
    b_factor = 0.10
    if option_type.lower() == "call":
        otm_amount = max(0.0, k - s)
        base_req = max(a_factor * s - otm_amount, b_factor * k)
    else:
        otm_amount = max(0.0, s - k)
        base_req = max(a_factor * s - otm_amount, b_factor * k)

    raw_margin = contract_size * (base_req + premium)
    return float(math.ceil(raw_margin / 10000.0) * 10000.0)


def score_option_contract(
    contract: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    سیستم امتیازدهی شفاف و قابل تنظیم قراردادهای اختیار.
    اگر مظنه Bid/Ask نامعتبر باشد یا نقدشوندگی صفر باشد، امتیاز نهایی تولید نمی‌کند (امتیاز ناقص).
    """
    w = weights or {
        "liquidity": 25.0,
        "spread": 20.0,
        "maturity": 15.0,
        "breakeven": 20.0,
        "ivQuality": 20.0
    }
    total_w = sum(w.values()) or 100.0

    bid = contract.get("bid") or 0
    ask = contract.get("ask") or 0
    vol = contract.get("volume") or 0
    val_b = contract.get("valueTomanB") or 0.0
    days = contract.get("daysToMaturity") or 0
    be_pct = abs(contract.get("breakevenMovePct") or 99.0)
    iv = contract.get("ivPct")

    reasons = []
    # بررسی صحت و کفایت داده برای امتیازدهی معتبر
    if bid <= 0 or ask <= 0 or ask < bid or vol <= 0:
        return {
            "score": None,
            "isIncomplete": True,
            "grade": "ناقص",
            "statusLabel": "امتیاز ناقص (نبود مظنهٔ دوطرفه معتبر)",
            "reasons": ["به دلیل نبود مظنهٔ خرید/فروش هم‌زمان یا حجم معاملات بسیار پایین، امتیاز نهایی تولید نشد تا از رتبه‌بندی گمراه‌کننده جلوگیری شود."]
        }

    spread_pct = ((ask - bid) / ((ask + bid) / 2.0)) * 100.0

    # 1. امتیاز نقدشوندگی (0 تا 100)
    if val_b >= 15.0:
        liq_score = 95.0
        reasons.append(f"نقدشوندگی بالا ({val_b} میلیارد تومان)")
    elif val_b >= 5.0:
        liq_score = 80.0
        reasons.append(f"نقدشوندگی مناسب ({val_b} میلیارد تومان)")
    elif val_b >= 1.0:
        liq_score = 60.0
        reasons.append(f"نقدشوندگی متوسط ({val_b} میلیارد تومان)")
    else:
        liq_score = 35.0
        reasons.append("ارزش معاملات پایین (ریسک نقدشوندگی)")

    # 2. امتیاز فشردگی Bid/Ask (0 تا 100)
    if spread_pct <= 1.8:
        sp_score = 95.0
        reasons.append(f"فاصله Bid/Ask بسیار کم ({spread_pct:.1f}%)")
    elif spread_pct <= 3.5:
        sp_score = 80.0
        reasons.append(f"فاصله Bid/Ask متعادل ({spread_pct:.1f}%)")
    elif spread_pct <= 6.5:
        sp_score = 55.0
        reasons.append(f"فاصله Bid/Ask نسبتاً باز ({spread_pct:.1f}%)")
    else:
        sp_score = 25.0
        reasons.append(f"فاصله Bid/Ask زیاد ({spread_pct:.1f}% - هزینه اسلیپیج بالا)")

    # 3. امتیاز زمان تا سررسید (بهترین بازه 20 تا 65 روز برای تعادل تتا و نقدشوندگی)
    if 21 <= days <= 65:
        mat_score = 90.0
        reasons.append(f"زمان استاندارد تا سررسید ({days} روز)")
    elif 10 <= days < 21:
        mat_score = 62.0
        reasons.append(f"نزدیک به سررسید ({days} روز - شتاب افت زمانی Theta)")
    elif days > 65:
        mat_score = 78.0
        reasons.append(f"سررسید میان‌مدت ({days} روز - افت زمانی ملایم)")
    else:
        mat_score = 30.0
        reasons.append(f"ریسک بسیار بالای انقضا ({days} روز باقی‌مانده)")

    # 4. امتیاز فاصله تا نقطهٔ سربه‌سر
    if be_pct <= 6.0:
        be_score = 92.0
        reasons.append(f"فاصلهٔ کم تا نقطهٔ سربه‌سر ({be_pct:.1f}%)")
    elif be_pct <= 12.0:
        be_score = 76.0
        reasons.append(f"فاصلهٔ متعادل تا سربه‌سر ({be_pct:.1f}%)")
    elif be_pct <= 20.0:
        be_score = 54.0
        reasons.append(f"نیازمند حرکت {be_pct:.1f}% سهم پایه برای سربه‌سر")
    else:
        be_score = 30.0
        reasons.append(f"نقطهٔ سربه‌سر دور ({be_pct:.1f}%)")

    # 5. امتیاز IV و کیفیت داده
    if iv is not None:
        if iv <= 48.0:
            iv_score = 90.0
            reasons.append(f"نوسان‌پذیری ضمنی متعادل/ارزان (IV: {iv}%)")
        elif iv <= 68.0:
            iv_score = 74.0
            reasons.append(f"نوسان‌پذیری ضمنی میانه (IV: {iv}%)")
        else:
            iv_score = 48.0
            reasons.append(f"نوسان‌پذیری ضمنی بالا/گران (IV: {iv}%)")
    else:
        iv_score = 40.0
        reasons.append("عدم امکان استخراج دقیق IV")

    weighted = (
        liq_score * w.get("liquidity", 25.0)
        + sp_score * w.get("spread", 20.0)
        + mat_score * w.get("maturity", 15.0)
        + be_score * w.get("breakeven", 20.0)
        + iv_score * w.get("ivQuality", 20.0)
    ) / total_w

    final_score = round(weighted, 1)
    if final_score >= 82:
        grade = "A"
    elif final_score >= 68:
        grade = "B"
    elif final_score >= 52:
        grade = "C"
    else:
        grade = "D"

    return {
        "score": final_score,
        "isIncomplete": False,
        "grade": grade,
        "statusLabel": f"امتیاز مقایسه‌ای: {final_score} ({grade})",
        "components": {
            "liquidity": liq_score,
            "spread": sp_score,
            "maturity": mat_score,
            "breakeven": be_score,
            "ivQuality": iv_score
        },
        "reasons": reasons
    }


def evaluate_strategy_payoff(
    strategy_id: str,
    spot: float,
    strike_1: float,
    premium_1: float,
    strike_2: float = 0.0,
    premium_2: float = 0.0,
    contract_size: int = 1000,
    fee_rate: float = DEFAULT_OPTION_FEE_RATE
) -> Dict[str, Any]:
    """
    محاسبهٔ دقیق هزینه/اعتبار اولیه، نقاط سربه‌سر، حداکثر سود/زیان و جدول سناریوهای سررسید
    برای استراتژی‌های تک‌قراردادی، پوشش‌دار و اسپردهای ترکیبی با لحاظ کارمزد و اندازه قرارداد.
    """
    scenarios_pct = [-20, -10, -5, 0, 5, 10, 20]
    scenario_rows = []

    fee_1 = premium_1 * fee_rate
    fee_2 = premium_2 * fee_rate if premium_2 > 0 else 0.0

    for pct in scenarios_pct:
        s_t = round(spot * (1.0 + pct / 100.0))
        if strategy_id == "long_call":
            net_cost_per_share = premium_1 + fee_1
            intrinsic = max(0.0, s_t - strike_1)
            pnl_per_share = intrinsic - net_cost_per_share
        elif strategy_id == "long_put":
            net_cost_per_share = premium_1 + fee_1
            intrinsic = max(0.0, strike_1 - s_t)
            pnl_per_share = intrinsic - net_cost_per_share
        elif strategy_id == "naked_short_call":
            net_credit_per_share = premium_1 - fee_1
            intrinsic = max(0.0, s_t - strike_1)
            pnl_per_share = net_credit_per_share - intrinsic
        elif strategy_id == "short_put":
            net_credit_per_share = premium_1 - fee_1
            intrinsic = max(0.0, strike_1 - s_t)
            pnl_per_share = net_credit_per_share - intrinsic
        elif strategy_id == "covered_call":
            spot_cost = spot * (1.0 + DEFAULT_SPOT_BUY_FEE)
            call_credit = premium_1 - fee_1
            net_entry = spot_cost - call_credit
            effective_exit = min(s_t, strike_1)
            pnl_per_share = effective_exit - net_entry
        elif strategy_id == "protective_put":
            spot_cost = spot * (1.0 + DEFAULT_SPOT_BUY_FEE)
            put_cost = premium_1 + fee_1
            net_entry = spot_cost + put_cost
            effective_exit = max(s_t, strike_1)
            pnl_per_share = effective_exit - net_entry
        elif strategy_id == "bull_call_spread":
            # خرید Call با اعمال پایین (strike_1) و فروش Call با اعمال بالا (strike_2)
            net_debit = (premium_1 + fee_1) - (premium_2 - fee_2)
            payoff = max(0.0, s_t - strike_1) - max(0.0, s_t - strike_2)
            pnl_per_share = payoff - net_debit
        elif strategy_id == "bear_put_spread":
            # خرید Put با اعمال بالا (strike_1) و فروش Put با اعمال پایین (strike_2)
            net_debit = (premium_1 + fee_1) - (premium_2 - fee_2)
            payoff = max(0.0, strike_1 - s_t) - max(0.0, strike_2 - s_t)
            pnl_per_share = payoff - net_debit
        else:
            pnl_per_share = 0.0

        scenario_rows.append({
            "movePct": pct,
            "spotAtExpiry": s_t,
            "pnlPerShareRial": round(pnl_per_share, 0),
            "totalPnlRial": round(pnl_per_share * contract_size, 0),
            "totalPnlToman": round((pnl_per_share * contract_size) / 10.0, 0)
        })

    return {
        "strategyId": strategy_id,
        "contractSize": contract_size,
        "scenarios": scenario_rows
    }
