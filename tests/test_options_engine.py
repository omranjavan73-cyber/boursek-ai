# -*- coding: utf-8 -*-
"""
آزمون‌های کنترل‌شده برای اعتبارسنجی ریاضی موتور اختیار معامله (tests/test_options_engine.py)
"""
import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tools.options_engine import (
    bs_price,
    solve_implied_volatility,
    bs_greeks,
    classify_moneyness,
    calc_tse_initial_margin,
    score_option_contract,
    evaluate_strategy_payoff,
)


class TestOptionsEngine(unittest.TestCase):
    def test_black_scholes_and_iv_roundtrip(self):
        """بررسی صحت فرمول بلک-شولز و بازیافت دقیق نوسان‌پذیری ضمنی (IV Round-Trip)"""
        spot = 72946.0
        strike = 70000.0
        days = 45
        r = 0.30
        true_sigma = 0.48  # 48%

        theo_call = bs_price(spot, strike, days / 365.0, r, true_sigma, "call")
        solved_iv = solve_implied_volatility(theo_call, spot, strike, days, r, "call")
        self.assertIsNotNone(solved_iv)
        self.assertAlmostEqual(solved_iv, 48.0, delta=0.15)

        theo_put = bs_price(spot, strike, days / 365.0, r, true_sigma, "put")
        solved_put_iv = solve_implied_volatility(theo_put, spot, strike, days, r, "put")
        self.assertIsNotNone(solved_put_iv)
        self.assertAlmostEqual(solved_put_iv, 48.0, delta=0.15)

    def test_greeks_bounds(self):
        """بررسی محدودهٔ منطقی یونانی‌ها (Delta, Gamma, Theta, Vega)"""
        g_call = bs_greeks(72946.0, 70000.0, 45, 48.5, 0.30, "call")
        self.assertIsNotNone(g_call)
        self.assertTrue(0.5 < g_call["delta"] < 1.0)
        self.assertTrue(g_call["gamma"] > 0)
        self.assertTrue(g_call["thetaDaily"] < 0)
        self.assertTrue(g_call["vega"] > 0)

        g_put = bs_greeks(72946.0, 75000.0, 45, 51.0, 0.30, "put")
        self.assertIsNotNone(g_put)
        self.assertTrue(-1.0 < g_put["delta"] < -0.3)

    def test_moneyness_classification(self):
        """بررسی تشخیص صحیح ITM / ATM / OTM"""
        m_itm = classify_moneyness(72946, 65000, "call")
        self.assertEqual(m_itm["status"], "ITM")
        self.assertEqual(m_itm["intrinsicValue"], 7946)

        m_atm = classify_moneyness(72946, 72000, "call")
        self.assertEqual(m_atm["status"], "ATM")

        m_otm = classify_moneyness(72946, 85000, "call")
        self.assertEqual(m_otm["status"], "OTM")
        self.assertEqual(m_otm["intrinsicValue"], 0)

    def test_incomplete_data_scoring_protection(self):
        """بررسی عدم تولید امتیاز کاذب برای قراردادهای فاقد مظنه Bid/Ask معتبر"""
        broken_contract = {
            "contractSymbol": "ضاهرم999",
            "bid": 0,
            "ask": 4200,
            "volume": 120,
            "valueTomanB": 0.2,
            "daysToMaturity": 30,
            "breakevenMovePct": 8.0,
            "ivPct": None
        }
        res = score_option_contract(broken_contract)
        self.assertTrue(res["isIncomplete"])
        self.assertIsNone(res["score"])
        self.assertEqual(res["grade"], "ناقص")

    def test_strategy_payoff_and_margin(self):
        """بررسی محاسبات استراتژی Bull Call Spread و وجه تضمین اولیه بورس تهران"""
        margin = calc_tse_initial_margin(72946, 75000, 6800, 1000, "call")
        self.assertTrue(margin >= 1000 * (0.10 * 75000 + 6800))

        spread = evaluate_strategy_payoff(
            "bull_call_spread",
            spot=72946,
            strike_1=70000,
            premium_1=9200,
            strike_2=80000,
            premium_2=4100,
            contract_size=1000
        )
        self.assertEqual(len(spread["scenarios"]), 7)
        # در سناریوی +20% (قیمت 87,535 بالای هر دو اعمال)، سود ناخالص هر سهم برابر (80000-70000) منهای خالص پریمیوم پرداختی است
        top_scen = spread["scenarios"][-1]
        self.assertTrue(top_scen["pnlPerShareRial"] > 4800)


if __name__ == "__main__":
    unittest.main()
