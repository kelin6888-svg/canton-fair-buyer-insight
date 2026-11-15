# -*- coding: utf-8 -*-
"""
qa.py — AI 数据分析问答（规则式意图识别 + 确定性统计，绝不编造数据）
可选接入大模型仅用于"理解问题"，但数值一律来自确定性统计引擎。
回答遵循八段式：问题说明 → 统计范围 → 样本量 → 数据来源 → 发现 → 解释 → 建议 → 限制。
"""
import analysis as A


# 意图 -> 关键词
INTENTS = [
    ("大洲分布", ["大洲", "地区分布", "哪个洲", "洲", "区域分布"]),
    ("国家分布", ["国家", "排名", "哪个国家", "top"]),
    ("采购需求", ["采购需求", "采购额", "需求变化", "增长", "下降", "需求"]),
    ("品类行业", ["品类", "行业", "商品类别", "什么行业", "哪些行业"]),
    ("新兴产业", ["新兴产业", "人工智能", "电动车", "锂电", "光伏", "绿电", "空天", "ai"]),
    ("贸易服务", ["贸易服务", "配对", "贸易"]),
    ("展商满意度", ["展商", "参展商"]),
    ("参会满意度", ["参会", "整体服务", "服务评价", "全旅程", "满意度"]),
    ("供应链因素", ["供应链", "因素", "考量"]),
]


def detect_intent(question):
    q = (question or "").lower()
    for name, kws in INTENTS:
        if any(k in q for k in kws):
            return name
    return None


def _analyzer_for(intent, data):
    """返回 (analyzer_callable, 问卷code)。analyzer 返回 (result, evidence)。"""
    def get(code):
        return data[code]["df"] if code in data else None

    if intent == "大洲分布":
        def f():
            df = get("demand")
            return A.continent_distribution(df, "采购需求问卷_清洗后.csv")
        return f, "demand"
    if intent == "国家分布":
        def f():
            df = get("demand")
            return A.top_countries(df, "采购需求问卷_清洗后.csv", n=10)
        return f, "demand"
    if intent == "采购需求":
        def f():
            df = get("demand")
            return A.categorical_dist(df, "采购需求问卷_清洗后.csv", ["采购额变化"])
        return f, "demand"
    if intent == "品类行业":
        def f():
            df = get("demand")
            return A.multi_select_counts(df, "采购需求问卷_清洗后.csv", "行业_", top_n=10)
        return f, "demand"
    if intent == "新兴产业":
        def f():
            df = get("emerging")
            return A.multi_select_counts(df, "新兴产业问卷_清洗后.csv", "关注_")
        return f, "emerging"
    if intent == "贸易服务":
        def f():
            df = get("trade_service")
            return A.categorical_dist(df, "trade_service_清洗后.csv", ["是否需要", "配對"])
        return f, "trade_service"
    if intent == "展商满意度":
        def f():
            df = get("exhibitor_product")
            return A.satisfaction_summary(df, "exhibitor_product_清洗后.csv", ["參展商", "滿意"])
        return f, "exhibitor_product"
    if intent == "参会满意度":
        def f():
            df = get("participation_service")
            return A.satisfaction_summary(df, "participation_service_清洗后.csv", ["整體服務", "滿意"])
        return f, "participation_service"
    if intent == "供应链因素":
        def f():
            df = get("demand")
            return A.multi_select_counts(df, "采购需求问卷_清洗后.csv", "供应链因素_", top_n=10)
        return f, "demand"
    return None, None


def format_answer(question, intent, result, evidence):
    """把 (result, evidence) 渲染成八段式 Markdown。"""
    if not intent:
        return ("抱歉，我暂时无法识别这个问题类型。\n\n"
                "本系统支持的问题类型：大洲/国家分布、采购需求、品类行业、新兴产业、"
                "贸易服务、展商满意度、参会满意度、供应链因素。\n\n"
                "我不会在无数据支撑时编造结论。")
    lines = [
        f"### 问题说明\n> {question}",
        f"### 统计范围\n{evidence.get('字段', '-')}（问卷：{evidence.get('数据来源', '-')}）",
        f"### 样本数量\n样本量 {evidence.get('样本量', 0)}，有效样本 {evidence.get('有效样本', 0)}",
        f"### 数据来源\n{evidence.get('数据来源', '-')} · 口径：{evidence.get('统计口径', '-')}",
        "### 数据发现",
    ]
    if isinstance(result, dict) and "分布" in result and "满意及以上占比%" in result:
        lines.append(f"- 满意度分布：{result['分布']}")
        lines.append(f"- **满意及以上占比 {result['满意及以上占比%']}%**（{result['满意及以上人数']}人）")
        lines.append(f"- 编码：{result['编码说明']}")
        lines.append("### 业务解释\n采购商对该维度评价整体积极，满意及以上占比高。")
        lines.append("### 建议\n可结合该维度短板（不满意/一般档）做针对性改进，具体需下钻到细分选项。")
    elif isinstance(result, dict) and result:
        top = list(result.items())[:8]
        lines += [f"- {k}：{v}" for k, v in top]
        lines.append("### 业务解释\n见分布，具体解读需结合业务语境。")
        lines.append("### 建议\n关注占比最高的类别/选项，作为重点方向。")
    elif isinstance(result, list) and result:
        for r in result[:10]:
            lines.append(f"- {r['选项']}：{r['次数']} 次（{r['占比%']}%）")
        lines.append("### 业务解释\n以上为多选题选项热度，占比合计可能超过 100%（可多选）。")
        lines.append("### 建议\n热度最高的选项为采购商核心关注点。")
    else:
        lines.append("- （无有效数据）")
        lines.append("### 业务解释\n该问题在当前数据中无可支撑的结果。")
        lines.append("### 建议\n请检查数据字段或样本范围。")
    lines += [
        "### 结论限制",
        "1. 采购意向 ≠ 实际订单；问卷为到会采购商截面样本。",
        "2. 无访谈记录，结论均为结构化问卷统计。",
    ]
    return "\n".join(lines)


def ask(question, harness, data):
    """入口：识别意图 → 走 Harness 工作流 → 生成八段式回答。"""
    intent = detect_intent(question)
    analyzer, code = _analyzer_for(intent, data)
    if analyzer is None:
        out = harness.run(question, None, lambda: ({}, {}))
        return {"markdown": format_answer(question, None, {}, {}), "harness": out}
    out = harness.run(question, f"{intent}:{code or ''}", analyzer)
    md = format_answer(question, intent, out["result"], out["evidence"])
    return {"markdown": md, "harness": out}
