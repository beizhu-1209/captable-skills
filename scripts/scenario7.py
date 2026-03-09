"""场景7：分层折扣转股"""

from typing import Dict, Any
from .base import round_to_decimal, adjust_tail_difference


def calculate(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    分层折扣转股：不同轮次不同折扣定价。

    参数:
        currentShareholders: 现有股东列表
        currentValuation: 当前估值（万元）
        investmentAmount: 增资金额（万元）
        investors: [{name, transferAmount, investmentAmount}]
        discountByRound: [{round, discount}]
    """
    shareholders = params["currentShareholders"]
    valuation = params["currentValuation"]
    investment = params["investmentAmount"]
    investors = params["investors"]
    discount_by_round = params["discountByRound"]

    pre_total_capital = sum(sh["capital"] for sh in shareholders)
    discount_map = {item["round"]: item["discount"] for item in discount_by_round}

    transfer_details = []
    total_transfer_amount = 0.0
    total_transfer_capital = 0.0

    # 第一步：按不同折扣转让（每个股东转让20%）
    after_transfer = []
    for sh in shareholders:
        disc = discount_map.get(sh["round"], 1.0)
        t_valuation = valuation * disc
        price = t_valuation / pre_total_capital

        transfer_ratio = 0.2  # 固定转让20%
        transferred = sh["capital"] * transfer_ratio
        transferred_amount = transferred * price

        total_transfer_capital += transferred
        total_transfer_amount += transferred_amount

        transfer_details.append({
            "shareholderId": sh["id"],
            "shareholderName": sh["name"],
            "transferredCapital": transferred,
            "transferredAmount": transferred_amount,
        })

        after_transfer.append({
            **sh,
            "capital": round_to_decimal(sh["capital"] - transferred, 2),
            "shares": round_to_decimal(sh["shares"] - transferred, 2),
            "percentage": (sh["capital"] - transferred) / pre_total_capital,
        })

    # 第二步：增资
    post_valuation = valuation + investment
    increase_price = post_valuation / pre_total_capital

    actual_new_capital = 0.0
    total_inv_transfer = sum(inv["transferAmount"] for inv in investors)

    for i, inv in enumerate(investors):
        invested_cap = inv["investmentAmount"] / increase_price
        actual_new_capital += invested_cap
        transferred_cap = (
            total_transfer_capital * (inv["transferAmount"] / total_inv_transfer)
            if total_inv_transfer > 0 else 0
        )
        total_cap = transferred_cap + invested_cap

        after_transfer.append({
            "id": f"investor-{i}",
            "name": inv["name"],
            "type": "新投资人",
            "round": "转股轮",
            "capital": round_to_decimal(total_cap, 2),
            "shares": round_to_decimal(total_cap, 2),
            "percentage": 0,
        })

    new_capital = actual_new_capital
    post_total_capital = pre_total_capital + new_capital

    for sh in after_transfer:
        sh["percentage"] = sh["capital"] / post_total_capital

    adjust_tail_difference(after_transfer)

    return {
        "scenario": "scenario7",
        "scenarioName": "场景7：分层折扣转股",
        "preTotalCapital": pre_total_capital,
        "preValuation": valuation,
        "transferAmount": total_transfer_amount,
        "investmentAmount": investment,
        "pricePerShare": increase_price,
        "postTotalCapital": round_to_decimal(post_total_capital, 2),
        "postValuation": post_valuation,
        "newCapital": round_to_decimal(new_capital, 2),
        "shareholders": after_transfer,
        "transferDetails": transfer_details,
    }
