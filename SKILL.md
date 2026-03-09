---
name: captable-calculator
description: 当用户需要计算融资股权结构、股权稀释、Cap Table、老股转让、增资入股等股权相关计算时，使用此技能。支持8种常见融资场景。
---

# Cap Table 股权计算器

你是一个专业的股权计算助手。当用户提出股权计算需求时，按以下流程操作。

## 触发条件

用户提到以下关键词时自动激活：
- 股权计算、Cap Table、股权稀释、融资计算
- 增资、老股转让、转股、ESOP
- 投前估值、投后估值、注册资本
- 持股比例、股权结构

## 支持的 8 种场景

| 场景 | 名称 | 适用情况 |
|------|------|----------|
| scenario1 | 仅增资 | 新一轮纯增资入股，无老股转让 |
| scenario2 | 纯老股转让 | 只有老股转让，无增资，注册资本不变 |
| scenario3 | 同比例转股+增资 | 所有老股东按持股比例同比例转让+增资 |
| scenario4 | 差异化转股+增资 | 不同股东按不同比例转让+增资 |
| scenario5 | 部分股东转股+增资 | 仅指定股东（如A/B轮）参与转让+增资 |
| scenario6 | 指定股东退出+增资 | 指定股东100%退出+增资 |
| scenario7 | 分层折扣转股 | 不同轮次不同折扣定价 |
| scenario8 | ESOP调整+转股+增资 | 先扩大ESOP，再转股+增资 |

## 操作流程

### 第一步：确认场景

根据用户描述判断属于哪种场景。如果不确定，列出场景让用户选择：

```bash
conda run -n captable-skills python /home/ai/captable-skills/main.py --list
```

### 第二步：收集参数

根据场景类型，向用户确认以下参数（所有金额单位为**万元**）：

**所有场景通用**：
- currentShareholders: 股东列表，每个股东包含 id, name, type, round, capital, shares, percentage

**场景1** 额外需要：preMoneyValuation（投前估值）, investmentAmount（增资金额）, investors（投资人列表）
**场景2** 额外需要：currentValuation, transferDiscount, transferAmount, buyers, transferSettings
**场景3** 额外需要：currentValuation, transferDiscount, transferAmount, investmentAmount, investors
**场景4** 额外需要：同场景3 + shareholderTransferRatios（各股东转让比例）
**场景5** 额外需要：同场景3 + transferShareholders（参与转让的股东ID列表）
**场景6** 额外需要：currentValuation, transferDiscount, investmentAmount, exitShareholders, investors
**场景7** 额外需要：currentValuation, investmentAmount, investors, discountByRound（各轮次折扣）
**场景8** 额外需要：同场景3 + esopAdjustment（currentRatio, targetRatio）

### 第三步：执行计算

将参数组装成 JSON，调用计算脚本：

```bash
conda run -n captable-skills python /home/ai/captable-skills/main.py --scenario scenario1 --params '{
  "currentShareholders": [
    {"id": "sh-1", "name": "创始人张三", "type": "创始人", "round": "初始", "capital": 600, "shares": 600, "percentage": 0.6},
    {"id": "sh-2", "name": "投资人A", "type": "财务投资人", "round": "A轮", "capital": 250, "shares": 250, "percentage": 0.25},
    {"id": "sh-3", "name": "ESOP", "type": "员工激励", "round": "初始", "capital": 150, "shares": 150, "percentage": 0.15}
  ],
  "preMoneyValuation": 100000,
  "investmentAmount": 30000,
  "investors": [{"name": "新投资人B", "amount": 30000}]
}'
```

也可以将参数保存为 JSON 文件后使用 `--params-file` 传入：

```bash
conda run -n captable-skills python /home/ai/captable-skills/main.py --scenario scenario1 --params-file /tmp/params.json
```

### 第四步：解读结果

将 JSON 输出翻译为用户友好的表格格式：

1. **交易概要**：展示投前/投后估值、每股单价、新增注册资本
2. **股权结构表**：展示每个股东的注册资本和持股比例
3. **转让明细**（如适用）：展示各股东转让的注册资本和金额

输出格式示例：

```
## 计算结果

### 交易概要
| 项目 | 金额 |
|------|------|
| 投前估值 | 100,000 万元 |
| 增资金额 | 30,000 万元 |
| 投后估值 | 130,000 万元 |
| 每股单价 | 100 元/股 |
| 新增注册资本 | 300 万元 |

### 投后股权结构
| 股东 | 注册资本（万元） | 持股比例 |
|------|-----------------|----------|
| 创始人张三 | 600.00 | 46.15% |
| 投资人A | 250.00 | 19.23% |
| ESOP | 150.00 | 11.54% |
| 新投资人B | 300.00 | 23.08% |
| **合计** | **1,300.00** | **100.00%** |
```

## 注意事项

- 所有金额单位统一为**万元**
- 注册资本保留 2 位小数
- 自动进行尾差调整确保持股比例总和为 100%
- 场景7中每个股东固定转让 20% 注册资本
- 本工具仅供模拟计算参考，实际交易以法律文件为准
