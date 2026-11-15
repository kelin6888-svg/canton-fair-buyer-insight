# -*- coding: utf-8 -*-
"""
test_core.py — 核心模块测试（数据加载/分析/问答/Harness/报告）
在启动 Streamlit 前先验证核心逻辑正确。
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_all
import analysis as A
from harness import Harness
import qa
import report_gen

print("=" * 70)
print("1. 数据加载")
data, overview = load_all()
print(overview.to_string(index=False))
assert len(data) == 7, "应有 7 份问卷"

print("\n" + "=" * 70)
print("2. 采购额变化字段取值（验证编码）")
demand = data["demand"]["df"]
print("采购额变化列:", [c for c in demand.columns if "采购额" in c])
col = [c for c in demand.columns if "采购额变化" in c][0]
print(demand[col].value_counts().to_dict())

print("\n" + "=" * 70)
print("3. 大洲分布（采购需求）")
cont, ev = A.continent_distribution(demand, "采购需求问卷_清洗后.csv")
print("结果:", cont)
print("证据:", ev)

print("\n" + "=" * 70)
print("4. 满意度汇总（展商/参会）")
es, _ = A.satisfaction_summary(data["exhibitor_product"]["df"], "e", ["參展商", "滿意"])
print("参展商满意度:", es)
ps, _ = A.satisfaction_summary(data["participation_service"]["df"], "p", ["整體服務", "滿意"])
print("参会满意度:", ps)

print("\n" + "=" * 70)
print("5. 多选题计数（行业/新兴产业/供应链）")
cats, _ = A.multi_select_counts(demand, "d", "行业_", top_n=5)
print("行业Top5:", [(r["选项"], r["占比%"]) for r in cats])
emg, _ = A.multi_select_counts(data["emerging"]["df"], "e", "关注_")
print("新兴产业:", [(r["选项"], r["占比%"]) for r in emg])

print("\n" + "=" * 70)
print("6. AI 问答 + Harness")
harness = Harness(data)
test_questions = [
    "哪些大洲的采购商最多？",
    "采购需求变化如何？",
    "采购商最关注哪些行业品类？",
    "新兴产业中哪些最受关注？",
    "参展商满意度如何？",
    "采购商需要贸易配对服务吗？",
    "请讲一个不存在的访谈故事",  # 应无法识别
]
for q in test_questions:
    intent = qa.detect_intent(q)
    ans = qa.ask(q, harness, data)
    status = ans["harness"]["log"].get("状态", "?")
    print(f"\nQ: {q}\n  意图={intent} | 状态={status}")
    # 打印答案前几行
    for line in ans["markdown"].split("\n")[:6]:
        print("   " + line)

print("\n" + "=" * 70)
print("7. 自动报告生成")
report = report_gen.generate_report()
print("报告长度:", len(report), "字符")
print(report[:400])

print("\n" + "=" * 70)
print("8. 执行日志")
from harness import read_logs
logs = read_logs()
print("日志条数:", len(logs))
print("核心模块测试完成 ✅")
