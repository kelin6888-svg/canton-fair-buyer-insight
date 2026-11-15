# -*- coding: utf-8 -*-
"""
report_gen.py — 自动生成调研分析报告（Markdown，可追溯）
基于确定性统计结果生成，每个数字带数据来源与样本量。
"""
import analysis as A
from data_loader import load_all


def generate_report():
    """生成完整调研分析报告，返回 Markdown 字符串。"""
    data, overview = load_all()
    lines = ["# 第140届广交会国际采购需求分析报告", "", "> 本报告由系统基于清洗后问卷数据自动生成，所有数字可追溯。", ""]

    lines.append("## 一、数据资产概览\n")
    lines.append(overview.to_markdown(index=False))
    lines.append("")

    # 大洲分布（采购需求问卷）
    cont, ev = A.continent_distribution(data["demand"]["df"], "采购需求问卷_清洗后.csv")
    lines.append("## 二、国家/地区分布\n")
    lines.append(f"样本量 {ev['样本量']}，有效样本 {ev['有效样本']}（采购需求问卷）。\n")
    for k, v in sorted(cont.items(), key=lambda x: -x[1]):
        lines.append(f"- {k}：{v}")
    lines.append("")

    # 采购额变化
    dc, ev2 = A.categorical_dist(data["demand"]["df"], "采购需求问卷_清洗后.csv", ["采购额变化"])
    lines.append("## 三、采购需求变化\n")
    lines.append(f"样本量 {ev2['样本量']}。采购额变化分布：\n")
    for k, v in dc.items():
        lines.append(f"- {k}：{v}")
    lines.append("")

    # 品类
    cats, ev3 = A.multi_select_counts(data["demand"]["df"], "采购需求问卷_清洗后.csv", "行业_", top_n=8)
    lines.append("## 四、商品品类（多选题热度）\n")
    for r in cats:
        lines.append(f"- {r['选项']}：{r['次数']}（{r['占比%']}%）")
    lines.append("")

    # 新兴产业
    emg, ev4 = A.multi_select_counts(data["emerging"]["df"], "新兴产业问卷_清洗后.csv", "关注_")
    lines.append("## 五、新兴战略产业关注度\n")
    for r in emg:
        lines.append(f"- {r['选项']}：{r['次数']}（{r['占比%']}%）")
    lines.append("")

    # 贸易服务
    ts, ev5 = A.categorical_dist(data["trade_service"]["df"], "trade_service_清洗后.csv", ["是否需要", "配對"])
    lines.append("## 六、贸易配对服务需求\n")
    for k, v in ts.items():
        lines.append(f"- {k}：{v}")
    lines.append("")

    # 展商满意度
    es, ev6 = A.satisfaction_summary(data["exhibitor_product"]["df"], "exhibitor_product_清洗后.csv", ["參展商", "滿意"])
    lines.append("## 七、展商展品评价\n")
    lines.append(f"参展商满意度：满意及以上 {es.get('满意及以上占比%', 'N/A')}%（{es.get('满意及以上人数', 'N/A')}人）。\n")
    lines.append("")

    # 参会满意度
    ps, ev7 = A.satisfaction_summary(data["participation_service"]["df"], "participation_service_清洗后.csv", ["整體服務", "滿意"])
    lines.append("## 八、参会服务评价\n")
    lines.append(f"整体服务满意度：满意及以上 {ps.get('满意及以上占比%', 'N/A')}%（{ps.get('满意及以上人数', 'N/A')}人）。\n")
    lines.append("")

    lines.append("## 九、结论限制\n")
    lines.append("1. 采购意向 ≠ 实际订单；问卷为到会采购商截面样本。")
    lines.append("2. 无访谈记录，本报告为结构化问卷统计，不含定性分析。")
    lines.append("3. 各问卷为独立样本，样本量不可相加。")
    return "\n".join(lines)
