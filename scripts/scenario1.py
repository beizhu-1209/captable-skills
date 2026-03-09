"""场景1：仅增资"""

from typing import List, Dict, Any
from .base import round_to_decimal, adjust_tail_difference


def calculate(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    仅增资：新一轮纯增资入股，无老股转让。

    参数:
        currentShareholders: 现有股东列表
        preMoneyValuation: 投前估值（万元）
        investmentAmount: 增资金额（万元）
        investors: [{name, amount}]
    """
    shareholders = params["currentShareholders"]
    pre_valuation = params["preMoneyValuation"]
    investment = params["investmentAmount"]
    investors = params["investors"]

    pre_total_capital = sum(sh["capital"] for sh in shareholders)
    post_valuation = pre_valuation + investment
    price_per_share = pre_valuation / pre_total_capital
    new_capital = investment / price_per_share
    post_total_capital = pre_total_capital + new_capital

    dilution_factor = pre_total_capital / post_total_capital

    updated = []
    for sh in shareholders:
        updated.append({
            **sh,
            "capital": round_to_decimal(sh["capital"], 2),
            "shares": round_to_decimal(sh["shares"], 2),
            "percentage": sh["percentage"] * dilution_factor,
        })

    for i, inv in enumerate(investors):
        inv_capital = inv["amount"] / price_per_share
        updated.append({
            "id": f"investor-{i}",
            "name": inv["name"],
            "type": "新投资人",
            "round": "E轮",
            "capital": round_to_decimal(inv_capital, 2),
            "shares": round_to_decimal(inv_capital, 2),
            "percentage": inv_capital / post_total_capital,
        })

    adjust_tail_difference(updated)

    return {
        "scenario": "scenario1",
        "scenarioName": "场景1：仅增资",
        "preTotalCapital": pre_total_capital,
        "preValuation": pre_valuation,
        "investmentAmount": investment,
        "pricePerShare": price_per_share,
        "postTotalCapital": round_to_decimal(post_total_capital, 2),
        "postValuation": post_valuation,
        "newCapital": round_to_decimal(new_capital, 2),
        "shareholders": updated,
    }
