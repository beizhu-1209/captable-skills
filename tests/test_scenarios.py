"""Cap Table 计算器单元测试 - 覆盖全部8种场景"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from scripts.scenario1 import calculate as calc1
from scripts.scenario2 import calculate as calc2
from scripts.scenario3 import calculate as calc3
from scripts.scenario4 import calculate as calc4
from scripts.scenario5 import calculate as calc5
from scripts.scenario6 import calculate as calc6
from scripts.scenario7 import calculate as calc7
from scripts.scenario8 import calculate as calc8


# ===== 公用测试数据 =====

def base_shareholders():
    return [
        {"id": "sh-1", "name": "创始人张三", "type": "创始人", "round": "初始",
         "capital": 600, "shares": 600, "percentage": 0.6},
        {"id": "sh-2", "name": "投资人A", "type": "财务投资人", "round": "A轮",
         "capital": 250, "shares": 250, "percentage": 0.25},
        {"id": "sh-3", "name": "ESOP", "type": "员工激励", "round": "初始",
         "capital": 150, "shares": 150, "percentage": 0.15},
    ]


def assert_percentage_sum(shareholders, tol=1e-4):
    total = sum(sh["percentage"] for sh in shareholders)
    assert abs(total - 1.0) < tol, f"持股比例总和={total}, 期望=1.0"


def assert_capital_consistency(result, tol=1.0):
    actual = sum(sh["capital"] for sh in result["shareholders"])
    assert abs(actual - result["postTotalCapital"]) < tol, \
        f"注册资本总和={actual}, postTotalCapital={result['postTotalCapital']}"


# ===== 场景1：仅增资 =====

class TestScenario1:
    def params(self):
        return {
            "currentShareholders": base_shareholders(),
            "preMoneyValuation": 100000,
            "investmentAmount": 30000,
            "investors": [{"name": "新投资人B", "amount": 30000}],
        }

    def test_basic(self):
        r = calc1(self.params())
        assert r["scenario"] == "scenario1"
        assert r["preTotalCapital"] == 1000
        assert r["postValuation"] == 130000
        assert r["pricePerShare"] == pytest.approx(100, abs=0.01)
        assert r["newCapital"] == pytest.approx(300, abs=0.01)
        assert r["postTotalCapital"] == pytest.approx(1300, abs=0.01)

    def test_percentage_sum(self):
        r = calc1(self.params())
        assert_percentage_sum(r["shareholders"])

    def test_capital_consistency(self):
        r = calc1(self.params())
        assert_capital_consistency(r)

    def test_investor_percentage(self):
        r = calc1(self.params())
        inv = next(sh for sh in r["shareholders"] if sh["name"] == "新投资人B")
        assert inv["percentage"] == pytest.approx(300 / 1300, abs=0.001)


# ===== 场景2：纯老股转让 =====

class TestScenario2:
    def params(self):
        return {
            "currentShareholders": base_shareholders(),
            "currentValuation": 100000,
            "transferDiscount": 0.7,
            "transferAmount": 7000,
            "buyers": [{"name": "买方X", "amount": 7000}],
            "transferSettings": [
                {"shareholderType": "创始人", "shouldTransfer": True, "transferRatio": 0.1},
                {"shareholderType": "财务投资人", "shouldTransfer": True, "transferRatio": 0.1},
                {"shareholderType": "员工激励", "shouldTransfer": False, "transferRatio": 0},
            ],
        }

    def test_no_new_capital(self):
        r = calc2(self.params())
        assert r["newCapital"] == 0
        assert r["postTotalCapital"] == 1000  # 纯转让不改变总注册资本

    def test_percentage_sum(self):
        r = calc2(self.params())
        assert_percentage_sum(r["shareholders"])


# ===== 场景3：同比例转股+增资 =====

class TestScenario3:
    def params(self):
        return {
            "currentShareholders": base_shareholders(),
            "currentValuation": 100000,
            "transferDiscount": 0.7,
            "transferAmount": 7000,
            "investmentAmount": 30000,
            "investors": [{"name": "投资人C", "transferAmount": 7000, "investmentAmount": 30000}],
        }

    def test_basic(self):
        r = calc3(self.params())
        assert r["postValuation"] == 130000
        assert r["transferValuation"] == pytest.approx(70000, abs=0.01)

    def test_percentage_sum(self):
        r = calc3(self.params())
        assert_percentage_sum(r["shareholders"])

    def test_capital_consistency(self):
        r = calc3(self.params())
        assert_capital_consistency(r)


# ===== 场景4：差异化转股+增资 =====

class TestScenario4:
    def params(self):
        return {
            "currentShareholders": base_shareholders(),
            "currentValuation": 100000,
            "transferDiscount": 0.7,
            "transferAmount": 7000,
            "investmentAmount": 30000,
            "investors": [{"name": "投资人D", "transferAmount": 7000, "investmentAmount": 30000}],
            "shareholderTransferRatios": [
                {"shareholderId": "sh-1", "transferRatio": 0.1},
                {"shareholderId": "sh-2", "transferRatio": 0.3},
                {"shareholderId": "sh-3", "transferRatio": 0.0},
            ],
        }

    def test_differential_transfer(self):
        r = calc4(self.params())
        details = r["transferDetails"]
        assert len(details) == 2  # sh-3 不转让

    def test_percentage_sum(self):
        r = calc4(self.params())
        assert_percentage_sum(r["shareholders"])

    def test_capital_consistency(self):
        r = calc4(self.params())
        assert_capital_consistency(r)


# ===== 场景5：部分股东转股+增资 =====

class TestScenario5:
    def params(self):
        return {
            "currentShareholders": base_shareholders(),
            "currentValuation": 100000,
            "transferDiscount": 0.7,
            "transferAmount": 7000,
            "investmentAmount": 30000,
            "investors": [{"name": "投资人E", "transferAmount": 7000, "investmentAmount": 30000}],
            "transferShareholders": ["sh-2"],  # 仅A轮投资人参与转让
        }

    def test_partial_transfer(self):
        r = calc5(self.params())
        details = r["transferDetails"]
        assert len(details) == 1
        assert details[0]["shareholderName"] == "投资人A"

    def test_percentage_sum(self):
        r = calc5(self.params())
        assert_percentage_sum(r["shareholders"])

    def test_capital_consistency(self):
        r = calc5(self.params())
        assert_capital_consistency(r)


# ===== 场景6：指定股东退出+增资 =====

class TestScenario6:
    def params(self):
        return {
            "currentShareholders": base_shareholders(),
            "currentValuation": 100000,
            "transferDiscount": 0.7,
            "investmentAmount": 30000,
            "exitShareholders": ["sh-2"],  # A轮投资人退出
            "investors": [{"name": "投资人F", "transferAmount": 10000, "investmentAmount": 30000}],
        }

    def test_exit_removed(self):
        r = calc6(self.params())
        names = [sh["name"] for sh in r["shareholders"]]
        assert "投资人A" not in names

    def test_percentage_sum(self):
        r = calc6(self.params())
        assert_percentage_sum(r["shareholders"])

    def test_capital_consistency(self):
        r = calc6(self.params())
        assert_capital_consistency(r)


# ===== 场景7：分层折扣转股 =====

class TestScenario7:
    def shareholders(self):
        return [
            {"id": "sh-1", "name": "创始人张三", "type": "创始人", "round": "初始",
             "capital": 500, "shares": 500, "percentage": 0.5},
            {"id": "sh-2", "name": "A轮投资人", "type": "财务投资人", "round": "A轮",
             "capital": 300, "shares": 300, "percentage": 0.3},
            {"id": "sh-3", "name": "B轮投资人", "type": "财务投资人", "round": "B轮",
             "capital": 200, "shares": 200, "percentage": 0.2},
        ]

    def params(self):
        return {
            "currentShareholders": self.shareholders(),
            "currentValuation": 100000,
            "investmentAmount": 30000,
            "investors": [{"name": "新投资人A", "transferAmount": 5000, "investmentAmount": 20000}],
            "discountByRound": [
                {"round": "初始", "discount": 0.6},
                {"round": "A轮", "discount": 0.7},
                {"round": "B轮", "discount": 0.8},
            ],
        }

    def test_layered_discount(self):
        r = calc7(self.params())
        details = r["transferDetails"]
        founder = next(d for d in details if d["shareholderName"] == "创始人张三")
        assert founder["transferredCapital"] == pytest.approx(100, abs=0.01)  # 500*0.2
        assert founder["transferredAmount"] == pytest.approx(6000, abs=0.01)  # 100 * 60

    def test_total_transfer(self):
        r = calc7(self.params())
        # 6000 + 4200 + 3200 = 13400
        assert r["transferAmount"] == pytest.approx(13400, abs=1)

    def test_percentage_sum(self):
        r = calc7(self.params())
        assert_percentage_sum(r["shareholders"])

    def test_capital_consistency(self):
        r = calc7(self.params())
        assert_capital_consistency(r)


# ===== 场景8：ESOP调整+转股+增资 =====

class TestScenario8:
    def params(self):
        return {
            "currentShareholders": base_shareholders(),
            "currentValuation": 100000,
            "transferDiscount": 0.7,
            "transferAmount": 7000,
            "investmentAmount": 30000,
            "esopAdjustment": {"currentRatio": 0.15, "targetRatio": 0.20},
            "investors": [{"name": "投资人G", "transferAmount": 7000, "investmentAmount": 30000}],
        }

    def test_esop_expanded(self):
        r = calc8(self.params())
        assert r["esopAdjustment"]["before"] == 0.15
        assert r["esopAdjustment"]["after"] == 0.20
        assert r["esopAdjustment"]["dilutionAmount"] > 0

    def test_percentage_sum(self):
        r = calc8(self.params())
        assert_percentage_sum(r["shareholders"])

    def test_capital_consistency(self):
        r = calc8(self.params())
        assert_capital_consistency(r)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
