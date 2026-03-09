"""场景3：同比例转股+增资"""

from typing import Dict, Any
from .base import round_to_decimal, adjust_tail_difference


def calculate(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    同比例转股+增资：所有老股东按持股比例同比例转让+增资。

    参数:
        currentShareholders: 现有股东列表
        currentValuation: 当前估值（万元）
        transferDiscount: 转让折扣（0-1）
        transferAmount: 转让金额（万元）
        investmentAmount: 增资金额（万元）
        investors: [{name, transferAmount, investmentAmount}]
    """
    shareholders = params["currentShareholders"]
    valuation = params["currentValuation"]
    discount = params["transferDiscount"]
    transfer_amount = params["transferAmount"]
    investment = params["investmentAmount"]
    investors = params["investors"]

    pre_total_capital = sum(sh["capital"] for sh in shareholders)

    # 第一步：老股转让（同比例）
    transfer_valuation = valuation * discount
    transfer_price = transfer_valuation / pre_total_capital
    transfer_capital = transfer_amount / transfer_price
    transfer_ratio = transfer_capital / pre_total_capital

    after_transfer = []
    for sh in shareholders:
        transferred = sh["capital"] * transfer_ratio
        after_transfer.append({
            **sh,
            "capital": round_to_decimal(sh["capital"] - transferred, 2),
            "shares": round_to_decimal(sh["shares"] - transferred, 2),
            "percentage": (sh["capital"] - transferred) / pre_total_capital,
        })

    # 第二步：增资
    post_valuation = valuation + investment
    increase_price = post_valuation / pre_total_capital
    new_capital = investment / increase_price
    post_total_capital = pre_total_capital + new_capital

    for i, inv in enumerate(investors):
        transferred_cap = inv["transferAmount"] / transfer_price
        invested_cap = inv["investmentAmount"] / increase_price
        total_cap = transferred_cap + invested_cap
        after_transfer.append({
            "id": f"investor-{i}",
            "name": inv["name"],
            "type": "新投资人",
            "round": "转股轮",
            "capital": round_to_decimal(total_cap, 2),
            "shares": round_to_decimal(total_cap, 2),
            "percentage": total_cap / post_total_capital,
        })

    # 更新所有持股比例
    for sh in after_transfer:
        sh["percentage"] = sh["capital"] / post_total_capital

    adjust_tail_difference(after_transfer)

    return {
        "scenario": "scenario3",
        "scenarioName": "场景3：同比例转股+增资",
        "preTotalCapital": pre_total_capital,
        "preValuation": valuation,
        "transferAmount": transfer_amount,
        "transferValuation": transfer_valuation,
        "transferPricePerShare": transfer_price,
        "investmentAmount": investment,
        "pricePerShare": increase_price,
        "postTotalCapital": round_to_decimal(post_total_capital, 2),
        "postValuation": post_valuation,
        "newCapital": round_to_decimal(new_capital, 2),
        "shareholders": after_transfer,
    }
