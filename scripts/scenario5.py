"""场景5：部分股东转股+增资"""

from typing import Dict, Any
from .base import round_to_decimal, adjust_tail_difference


def calculate(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    部分股东转股+增资：仅指定股东参与转让。

    参数:
        currentShareholders: 现有股东列表
        currentValuation: 当前估值（万元）
        transferDiscount: 转让折扣（0-1）
        transferAmount: 转让金额（万元）
        investmentAmount: 增资金额（万元）
        investors: [{name, transferAmount, investmentAmount}]
        transferShareholders: [股东ID列表]
    """
    shareholders = params["currentShareholders"]
    valuation = params["currentValuation"]
    discount = params["transferDiscount"]
    transfer_amount = params["transferAmount"]
    investment = params["investmentAmount"]
    investors = params["investors"]
    transfer_ids = params["transferShareholders"]

    pre_total_capital = sum(sh["capital"] for sh in shareholders)

    # 第一步：部分股东转让
    transfer_valuation = valuation * discount
    transfer_price = transfer_valuation / pre_total_capital

    transferring_capital = sum(
        sh["capital"] for sh in shareholders if sh["id"] in transfer_ids
    )
    target_capital = transfer_amount / transfer_price
    transfer_ratio = target_capital / transferring_capital if transferring_capital > 0 else 0

    transfer_details = []
    after_transfer = []
    for sh in shareholders:
        if sh["id"] in transfer_ids:
            transferred = sh["capital"] * transfer_ratio
            transferred_amount = transferred * transfer_price
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
        else:
            after_transfer.append({**sh})

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

    for sh in after_transfer:
        sh["percentage"] = sh["capital"] / post_total_capital

    adjust_tail_difference(after_transfer)

    return {
        "scenario": "scenario5",
        "scenarioName": "场景5：部分股东转股+增资",
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
