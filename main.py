#!/usr/bin/env python3
"""
Cap Table 股权计算器 - Skill 主入口

用法:
    python main.py --scenario scenario1 --params '{"currentShareholders":[...], ...}'
    python main.py --list                # 列出所有支持的场景
    python main.py --help                # 帮助信息
"""

import argparse
import json
import sys

from scripts.scenario1 import calculate as calc1
from scripts.scenario2 import calculate as calc2
from scripts.scenario3 import calculate as calc3
from scripts.scenario4 import calculate as calc4
from scripts.scenario5 import calculate as calc5
from scripts.scenario6 import calculate as calc6
from scripts.scenario7 import calculate as calc7
from scripts.scenario8 import calculate as calc8

SCENARIOS = {
    "scenario1": {"name": "场景1：仅增资", "desc": "新一轮纯增资入股，无老股转让", "fn": calc1},
    "scenario2": {"name": "场景2：纯老股转让", "desc": "只有老股转让，无增资", "fn": calc2},
    "scenario3": {"name": "场景3：同比例转股+增资", "desc": "所有老股东按持股比例同比例转让+增资", "fn": calc3},
    "scenario4": {"name": "场景4：差异化转股+增资", "desc": "不同股东按不同比例转让+增资", "fn": calc4},
    "scenario5": {"name": "场景5：部分股东转股+增资", "desc": "仅指定股东参与转让+增资", "fn": calc5},
    "scenario6": {"name": "场景6：指定股东退出+增资", "desc": "指定股东100%退出+增资", "fn": calc6},
    "scenario7": {"name": "场景7：分层折扣转股", "desc": "不同轮次不同折扣定价", "fn": calc7},
    "scenario8": {"name": "场景8：ESOP调整+转股+增资", "desc": "ESOP扩大后转股+增资", "fn": calc8},
}


def list_scenarios():
    """列出所有支持的场景"""
    result = []
    for key, info in SCENARIOS.items():
        result.append({"id": key, "name": info["name"], "description": info["desc"]})
    return result


def run_scenario(scenario_id: str, params: dict) -> dict:
    """执行指定场景的计算"""
    if scenario_id not in SCENARIOS:
        return {"error": f"未知场景: {scenario_id}", "availableScenarios": list(SCENARIOS.keys())}

    try:
        return SCENARIOS[scenario_id]["fn"](params)
    except KeyError as e:
        return {"error": f"缺少必要参数: {e}"}
    except Exception as e:
        return {"error": f"计算错误: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="Cap Table 股权计算器")
    parser.add_argument("--scenario", type=str, help="场景ID (scenario1-scenario8)")
    parser.add_argument("--params", type=str, help="计算参数 (JSON字符串)")
    parser.add_argument("--params-file", type=str, help="计算参数文件路径 (JSON文件)")
    parser.add_argument("--list", action="store_true", help="列出所有支持的场景")
    parser.add_argument("--output", type=str, help="输出文件路径 (默认输出到stdout)")

    args = parser.parse_args()

    if args.list:
        result = list_scenarios()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if not args.scenario:
        parser.print_help()
        sys.exit(1)

    # 读取参数
    params = None
    if args.params:
        params = json.loads(args.params)
    elif args.params_file:
        with open(args.params_file, "r", encoding="utf-8") as f:
            params = json.load(f)
    else:
        # 从 stdin 读取
        stdin_data = sys.stdin.read().strip()
        if stdin_data:
            params = json.loads(stdin_data)

    if params is None:
        print(json.dumps({"error": "未提供计算参数，请使用 --params 或 --params-file"}, ensure_ascii=False))
        sys.exit(1)

    result = run_scenario(args.scenario, params)

    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"结果已保存到: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
