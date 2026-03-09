"""场景8：ESOP调整+转股+增资"""

from typing import Dict, Any
from .base import round_to_decimal, adjust_tail_difference


def calculate(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    ESOP调整+转股+增资：先扩大ESOP，再转股+增资。

    参数:
        currentShareholders: 现有股东列表
        currentValuation: 当前估值（万元）
        transferDiscount: 转让折扣（0-1）
        transferAmount: 转让金额（万元）
        investmentAmount: 增资金额（万元）
        esopAdjustment: {currentRatio, targetRatio}
        investors: [{name, transferAmount, investmentAmount}]
    """
    shareholders = params["currentShareholders"]
    valuation = params["currentValuation"]
    discount = params["transferDiscount"]
    transfer_amount = params["transferAmount"]
    investment = params["investmentAmount"]
    esop = params["esopAdjustment"]
    investors = params["investors"]

    pre_total_capital = sum(sh["capital"] for sh in shareholders)

    # 第一步：ESOP调整
    esop_dilution = esop["targetRatio"] - esop["currentRatio"]
    esop_dilution_capital = (pre_total_capital * esop_dilution) / (1 - esop["targetRatio"])

    after_esop = []
    for sh in shareholders:
        if sh["type"] == "员工激励":
            after_esop.append({
                **sh,
                "capital": round_to_decimal(sh["capital"] + esop_dilution_capital, 2),
                "shares": round_to_decimal(sh["shares"] + esop_dilution_capital, 2),
                "percentage": esop["targetRatio"],
            })
        else:
            dilution_factor = (1 - esop["targetRatio"]) / (1 - esop["currentRatio"])
            after_esop.append({
                **sh,
                "percentage": sh["percentage"] * dilution_factor,
            })

    after_esop_total = pre_total_capital + esop_dilution_capital

    # 第二步：老股转让（同比例）
    transfer_valuation = valuation * discount
    transfer_price = transfer_valuation / after_esop_total
    transfer_capital = transfer_amount / transfer_price
    transfer_ratio = transfer_capital / after_esop_total

    after_transfer = []
    for sh in after_esop:
        transferred = sh["capital"] * transfer_ratio
        after_transfer.append({
            **sh,
            "capital": round_to_decimal(sh["capital"] - transferred, 2),
            "shares": round_to_decimal(sh["shares"] - transferred, 2),
            "percentage": (sh["capital"] - transferred) / after_esop_total,
        })

    # 第三步：增资
    post_valuation = valuation + investment
    increase_price = post_valuation / after_esop_total
    new_capital = investment / increase_price
    post_total_capital = after_esop_total + new_capital

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
        "scenario": "scenario8",
        "scenarioName": "场景8：ESOP调整+转股+增资",
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
        "esopAdjustment": {
            "before": esop["currentRatio"],
            "after": esop["targetRatio"],
            "dilutionAmount": esop_dilution_capital,
        },
    }
