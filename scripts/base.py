"""基础工具函数：四舍五入、尾差调整"""

import math
from typing import List, Dict, Any


def round_to_decimal(value: float, decimals: int = 2) -> float:
    """四舍五入到指定小数位"""
    factor = 10 ** decimals
    return math.floor(value * factor + 0.5) / factor


def adjust_tail_difference(shareholders: List[Dict[str, Any]]) -> None:
    """尾差调整：确保所有股东持股比例加总为 100%"""
    total = sum(sh["percentage"] for sh in shareholders)
    diff = 1.0 - total
    if abs(diff) > 1e-6:
        max_sh = max(shareholders, key=lambda sh: sh["percentage"])
        max_sh["percentage"] += diff


def make_shareholder(
    id: str,
    name: str,
    sh_type: str,
    round_name: str,
    capital: float,
    shares: float,
    percentage: float,
) -> Dict[str, Any]:
    """创建股东字典"""
    return {
        "id": id,
        "name": name,
        "type": sh_type,
        "round": round_name,
        "capital": capital,
        "shares": shares,
        "percentage": percentage,
    }
