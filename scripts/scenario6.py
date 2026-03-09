"""场景6：指定股东退出+增资"""

from typing import Dict, Any
from .base import round_to_decimal, adjust_tail_difference


def calculate(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    指定股东退出+增资：指定股东100%退出。

    参数:
        currentShareholders: 现有股东列表
        currentValuation: 当前估值（万元）
        transferDiscount: 转让折扣（0-1）
        investmentAmount: 增资金额（万元）
        exitShareholders: [退出股东ID列表]
        investors: [{name, transferAmount, investmentAmount}]
    """
    shareholders = params["currentShareholders"]
    valuation = params["currentValuation"]
    discount = params["transferDiscount"]
    investment = params["investmentAmount"]
    exit_ids = params["exitShareholders"]
    investors = params["investors"]

    pre_total_capital = sum(sh["capital"] for sh in shareholders)

    # 第一步：指定股东完全退出
    transfer_valuation = valuation * discount
    transfer_price = transfer_valuation / pre_total_capital

    exit_capital = sum(
        sh["capital"] for sh in shareholders if sh["id"] in exit_ids
    )
    transfer_amount = exit_capital * transfer_price

    transfer_details = []
    after_transfer = []

    for sh in shareholders:
        if sh["id"] in exit_ids:
            transfer_details.append({
                "shareholderId": sh["id"],
                "shareholderName": sh["name"],
                "transferredCapital": sh["capital"],
                "transferredAmount": sh["capital"] * transfer_price,
            })
        else:
            after_transfer.append({**sh})

    # 第二步：增资
    post_valuation = valuation + investment
    increase_price = post_valuation / pre_total_capital

    actual_new_capital = 0.0
    for i, inv in enumerate(investors):
        transferred_cap = inv["transferAmount"] / transfer_price
        invested_cap = inv["investmentAmount"] / increase_price
        actual_new_capital += invested_cap
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
    post_total_capital = sum(sh["capital"] for sh in after_transfer)

    for sh in after_transfer:
        sh["percentage"] = sh["capital"] / post_total_capital

    adjust_tail_difference(after_transfer)

    return {
        "scenario": "scenario6",
        "scenarioName": "场景6：指定股东退出+增资",
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
        "transferDetails": transfer_details,
    }
