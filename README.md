# Cap Table 股权计算器 Skill

专为中国律师设计的融资股权计算工具，支持 8 种常见融资场景。可作为 Claude Code / OpenClaw 等 AI 编程工具的 Skill 使用。

## 项目结构

```
captable-skills/
├── main.py                        # 主入口（命令行调用）
├── skill.json                     # Skill 元数据
├── SKILL.md                       # Skill 指令文件（AI 自动读取）
├── scripts/                       # 核心计算模块
│   ├── base.py                    #   工具函数（四舍五入、尾差调整）
│   ├── scenario1.py               #   场景1：仅增资
│   ├── scenario2.py               #   场景2：纯老股转让
│   ├── scenario3.py               #   场景3：同比例转股+增资
│   ├── scenario4.py               #   场景4：差异化转股+增资
│   ├── scenario5.py               #   场景5：部分股东转股+增资
│   ├── scenario6.py               #   场景6：指定股东退出+增资
│   ├── scenario7.py               #   场景7：分层折扣转股
│   └── scenario8.py               #   场景8：ESOP调整+转股+增资
├── data/
│   └── sample_shareholders.csv    # 示例股东数据
├── tests/
│   └── test_scenarios.py          # 单元测试（25个用例）
└── output/
    └── results/                   # 计算结果输出目录
```

## 环境准备

### Conda 环境

```bash
# 激活环境
conda activate captable-skills

# 安装依赖（仅需 pytest 用于测试，计算引擎无第三方依赖）
pip install pytest
```

### 验证安装

```bash
conda run -n captable-skills python main.py --list
```

## 命令行用法

### 列出所有场景

```bash
conda run -n captable-skills python /home/ai/captable-skills/main.py --list
```

### 执行计算（直接传 JSON）

```bash
conda run -n captable-skills python /home/ai/captable-skills/main.py \
  --scenario scenario1 \
  --params '{
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

### 执行计算（从文件读取参数）

```bash
conda run -n captable-skills python /home/ai/captable-skills/main.py \
  --scenario scenario1 \
  --params-file /path/to/params.json
```

### 输出到文件

```bash
conda run -n captable-skills python /home/ai/captable-skills/main.py \
  --scenario scenario1 \
  --params-file params.json \
  --output output/results/result.json
```

## 8 种融资场景

### 场景1：仅增资

新一轮纯增资入股，无老股转让。

**参数**：
```json
{
  "currentShareholders": [...],
  "preMoneyValuation": 100000,
  "investmentAmount": 30000,
  "investors": [{"name": "投资人名称", "amount": 30000}]
}
```

**公式**：
```
每股单价 = 投前估值 / 投前注册资本
新增注册资本 = 增资金额 / 每股单价
投后注册资本 = 投前注册资本 + 新增注册资本
```

### 场景2：纯老股转让

只有老股转让，无增资，注册资本总额不变。

**参数**：
```json
{
  "currentShareholders": [...],
  "currentValuation": 100000,
  "transferDiscount": 0.7,
  "transferAmount": 7000,
  "buyers": [{"name": "买方名称", "amount": 7000}],
  "transferSettings": [
    {"shareholderType": "创始人", "shouldTransfer": true, "transferRatio": 0.1}
  ]
}
```

### 场景3：同比例转股+增资

所有老股东按持股比例同比例转让 + 增资。

**参数**：
```json
{
  "currentShareholders": [...],
  "currentValuation": 100000,
  "transferDiscount": 0.7,
  "transferAmount": 7000,
  "investmentAmount": 30000,
  "investors": [{"name": "投资人", "transferAmount": 7000, "investmentAmount": 30000}]
}
```

### 场景4：差异化转股+增资

不同股东按不同比例转让。

**额外参数**：
```json
{
  "shareholderTransferRatios": [
    {"shareholderId": "sh-1", "transferRatio": 0.1},
    {"shareholderId": "sh-2", "transferRatio": 0.3}
  ]
}
```

### 场景5：部分股东转股+增资

仅指定股东参与转让。

**额外参数**：
```json
{
  "transferShareholders": ["sh-2"]
}
```

### 场景6：指定股东退出+增资

指定股东100%退出。

**参数**：
```json
{
  "currentShareholders": [...],
  "currentValuation": 100000,
  "transferDiscount": 0.7,
  "investmentAmount": 30000,
  "exitShareholders": ["sh-2"],
  "investors": [{"name": "投资人", "transferAmount": 10000, "investmentAmount": 30000}]
}
```

### 场景7：分层折扣转股

不同轮次不同折扣定价。每个股东固定转让 20% 注册资本。

**额外参数**：
```json
{
  "discountByRound": [
    {"round": "初始", "discount": 0.6},
    {"round": "A轮", "discount": 0.7},
    {"round": "B轮", "discount": 0.8}
  ]
}
```

### 场景8：ESOP调整+转股+增资

先扩大 ESOP 比例，再转股 + 增资。

**额外参数**：
```json
{
  "esopAdjustment": {
    "currentRatio": 0.15,
    "targetRatio": 0.20
  }
}
```

## 作为 Skill 使用

### Claude Code

将本项目放在可访问的路径，AI 读取 `SKILL.md` 后自动获得以下能力：

1. 识别用户的股权计算需求
2. 判断应使用哪种场景
3. 引导用户提供必要参数
4. 调用 `main.py` 执行计算
5. 将 JSON 结果解读为用户友好的表格

**配置方式**：将项目路径添加到 Claude Code 的 skills 目录：

```bash
# 项目级（当前项目可用）
cp -r /home/ai/captable-skills/.  your-project/.claude/skills/captable-calculator/

# 用户级（所有项目可用）
cp -r /home/ai/captable-skills/.  ~/.claude/skills/captable-calculator/
```

或直接在项目的 `CLAUDE.md` 中引用：

```markdown
## Skills
- 股权计算：参考 /home/ai/captable-skills/SKILL.md
```

### OpenClaw / 其他 AI 工具

SKILL.md 遵循开放标准，兼容支持 Agent Skills 的 AI 工具。将项目目录作为 skill 加载即可。

## 运行测试

```bash
# 运行全部测试
conda run -n captable-skills python -m pytest tests/test_scenarios.py -v

# 运行指定场景测试
conda run -n captable-skills python -m pytest tests/test_scenarios.py::TestScenario7 -v
```

当前覆盖：25 个测试用例，覆盖全部 8 种场景的核心计算 + 持股比例总和 + 注册资本一致性校验。

## 输出格式

所有场景统一输出 JSON，包含：

| 字段 | 说明 |
|------|------|
| scenario | 场景ID |
| scenarioName | 场景名称 |
| preTotalCapital | 投前注册资本（万元） |
| preValuation | 投前估值（万元） |
| pricePerShare | 每股单价（元/股） |
| postTotalCapital | 投后注册资本（万元） |
| postValuation | 投后估值（万元） |
| newCapital | 新增注册资本（万元） |
| shareholders | 投后股东列表 |
| transferDetails | 转让明细（如适用） |
| esopAdjustment | ESOP调整信息（场景8） |

## 注意事项

- 所有金额单位为**万元**
- 注册资本保留 2 位小数
- 自动尾差调整确保持股比例总和 = 100%
- 场景7中每个股东固定转让 20%（如需调整修改 `scripts/scenario7.py` 中的 `transfer_ratio`）
- 本工具仅供模拟计算参考，实际交易以法律文件为准
