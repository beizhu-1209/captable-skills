"""场景2：纯老股转让"""

from typing import Dict, Any
from .base import round_to_decimal, adjust_tail_difference


def calculate(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    纯老股转让：只有老股转让，无增资，注册资本总额不变。

    参数:
        currentShareholders: 现有股东列表
        currentValuation: 当前估值（万元）
        transferDiscount: 转让折扣（0-1）
        transferAmount: 转让金额（万元）
        buyers: [{name, amount}]
        transferSettings: [{shareholderType, shouldTransfer, transferRatio}]
    """
    shareholders = params["currentShareholders"]
    valuation = params["currentValuation"]
    discount = params["transferDiscount"]
    transfer_amount = params["transferAmount"]
    buyers = params["buyers"]
    settings = params["transferSettings"]

    pre_total_capital = sum(sh["capital"] for sh in shareholders)
    transfer_valuation = valuation * discount
    price_per_share = transfer_valuation / pre_total_capital

    # 按股东类型设置转让比例
    ratio_map = {}
    for setting in settings:
        for sh in shareholders:
            if sh["type"] == setting["shareholderType"] and setting["shouldTransfer"]:
                ratio_map[sh["id"]] = setting["transferRatio"]

    # 计算总转让注册资本
    total_transfer_capital = 0.0
    for sh in shareholders:
        ratio = ratio_map.get(sh["id"], 0)
        total_transfer_capital += sh["capital"] * ratio

    # 调整转让比例以匹配转让金额
    target_capital = transfer_amount / price_per_share
    adj_factor = target_capital / total_transfer_capital if total_transfer_capital > 0 else 0

    updated = []
    for sh in shareholders:
        base_ratio = ratio_map.get(sh["id"], 0)
        actual_ratio = base_ratio * adj_factor
        transferred = sh["capital"] * actual_ratio
        updated.append({
            **sh,
            "capital": round_to_decimal(sh["capital"] - transferred, 2),
            "shares": round_to_decimal(sh["shares"] - transferred, 2),
            "percentage": (sh["capital"] - transferred) / pre_total_capital,
        })

    for i, buyer in enumerate(buyers):
        buyer_capital = buyer["amount"] / price_per_share
        updated.append({
            "id": f"buyer-{i}",
            "name": buyer["name"],
            "type": "新投资人",
            "round": "转股轮",
            "capital": round_to_decimal(buyer_capital, 2),
            "shares": round_to_decimal(buyer_capital, 2),
            "percentage": buyer_capital / pre_total_capital,
        })

    adjust_tail_difference(updated)

    return {
        "scenario": "scenario2",
        "scenarioName": "场景2：纯老股转让",
        "preTotalCapital": pre_total_capital,
        "preValuation": valuation,
        "transferAmount": transfer_amount,
        "transferValuation": transfer_valuation,
        "transferPricePerShare": price_per_share,
        "pricePerShare": price_per_share,
        "postTotalCapital": pre_total_capital,
        "postValuation": valuation,
        "newCapital": 0,
        "shareholders": updated,
    }
