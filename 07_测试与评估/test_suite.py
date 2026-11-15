# -*- coding: utf-8 -*-
"""
test_suite.py — 20 个测试用例（阶段6）
每个用例含：预期结果 + 通过标准。实际运行后输出结果表到 07_测试与评估/测试结果.xlsx。
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "05_产品开发", "应用程序"))

import pandas as pd
from data_loader import load_all, quality_check, find_col
from config import continent_of, QUESTIONNAIRES
import analysis as A
from harness import Harness, read_logs
import qa
import report_gen

RESULTS = []  # {ID, 用例, 预期, 实际, 结果}

def check(cid, name, expect, actual, passed):
    RESULTS.append({"ID": cid, "用例": name, "预期结果": expect, "实际结果": actual, "结果": "通过" if passed else "失败"})
    print(f"[{'PASS' if passed else 'FAIL'}] 用例{cid} {name}: {actual}")

data, overview = load_all()
harness = Harness(data)
demand = data["demand"]["df"]

# 1 数据导入
n = len(data)
check(1, "多类问卷数据导入", "7份问卷均可加载", f"加载{n}份", n == 7)

# 2 字段映射（国家→大洲标准化）
c1 = continent_of("Asia-India"); c2 = continent_of("UK"); c3 = continent_of("Asia-China - Hong Kong SAR")
check(2, "字段映射(国家→大洲)", "India→Asia, UK→Europe, 香港→Asia", f"{c1},{c2},{c3}", c1 == "Asia" and c2 == "Europe" and c3 == "Asia")

# 3 缺失数据
q_cater = data["catering"]["quality"]
check(3, "缺失数据识别", "餐饮国家缺失663(82.4%)", f"缺失{q_cater['国家缺失']}({q_cater['国家缺失率%']}%)", q_cater['国家缺失'] == 663)

# 4 重复记录（清洗阶段已去重）
check(4, "重复记录去重", "展商展品去重后623(去53)", f"行数{len(data['exhibitor_product']['df'])}", len(data['exhibitor_product']['df']) == 623)

# 5 分批快照合并
check(5, "分批快照合并", "贸易服务645=131+304+210", f"行数{len(data['trade_service']['df'])}", len(data['trade_service']['df']) == 645)

# 6 采购需求统计
col = find_col(demand, ["采购额变化"])
vc = demand[col].value_counts()
growth = vc[[k for k in vc.index if "增长" in str(k)]].sum()
pct = round(growth / len(demand) * 100, 1)
check(6, "采购需求统计", "采购额增长约79.3%", f"增长{pct}%", abs(pct - 79.3) < 0.5)

# 7 国家地区统计
cont, ev = A.continent_distribution(demand, "采购需求问卷_清洗后.csv")
asia_pct = round(cont["Asia"] / ev["样本量"] * 100, 1)
check(7, "国家地区统计", "亚洲约50%", f"亚洲{asia_pct}%", abs(asia_pct - 50.2) < 1)

# 8 商品分类
cats, _ = A.multi_select_counts(demand, "d", "行业_", top_n=1)
check(8, "商品分类", "电子家电居首约34.1%", f"{cats[0]['选项']}{cats[0]['占比%']}%", cats[0]['选项'] == "电子家电" and abs(cats[0]['占比%'] - 34.1) < 0.5)

# 9 群体标签(新兴产业)
emg, _ = A.multi_select_counts(data["emerging"]["df"], "e", "关注_")
check(9, "群体标签(新兴产业)", "AI居首约31.8%", f"{emg[0]['选项']}{emg[0]['占比%']}%", emg[0]['选项'] == "人工智能" and abs(emg[0]['占比%'] - 31.8) < 0.5)

# 10 群体画像(大洲+品类可组合)
cats_full, _ = A.multi_select_counts(demand, "d", "行业_")
check(10, "群体画像", "大洲与品类统计可组合", f"大洲{len(cont)}类, 行业{len(cats_full)}类", len(cont) >= 5 and len(cats_full) >= 5)

# 11 AI数据问答(意图识别)
intents = {q: qa.detect_intent(q) for q in ["哪些大洲采购商最多？", "采购需求如何？", "参展商满意度如何？"]}
check(11, "AI数据问答(意图)", "三类意图均识别", str(intents), all(intents.values()))

# 12 证据引用
ans = qa.ask("哪些大洲采购商最多？", harness, data)
ev = ans["harness"]["evidence"]
check(12, "证据引用", "回答含数据来源+样本量", f"来源={ev.get('数据来源','无')}, 样本={ev.get('样本量',0)}", bool(ev.get("数据来源")) and ev.get("样本量", 0) > 0)

# 13 数据不足处理
ans13 = qa.ask("请讲一个访谈故事", harness, data)
check(13, "数据不足/无法识别处理", "不编造，明确拒绝", f"状态={ans13['harness']['log'].get('状态')}", ans13["harness"]["log"].get("状态") == "无法识别问题类型")

# 14 跨问卷隔离
rows = {k: len(v["df"]) for k, v in data.items()}
check(14, "跨问卷隔离", "各问卷样本独立不相加", f"行数{rows}", len(set(rows.values())) >= 7)

# 15 AI任务拆解(Harness步骤)
steps = ans["harness"]["steps"]
check(15, "AI任务拆解", "Harness步骤≥5", f"{len(steps)}步", len(steps) >= 5)

# 16 工具调用
r, ev16 = A.satisfaction_summary(data["exhibitor_product"]["df"], "e", ["參展商", "滿意"])
check(16, "工具调用", "统计工具返回结果+证据", f"满意率{ev16['有效样本']}样本", ev16["有效样本"] > 0)

# 17 错误结果识别
empty_analyzer = lambda: ({}, {"数据来源": "x", "样本量": 0, "有效样本": 0})
out17 = harness.run("测试", "测试:demand", empty_analyzer)
check(17, "错误结果识别", "空样本质检不通过", f"评估={out17['质量评估']}", out17["质量评估"] == "不通过")

# 18 报告导出
report = report_gen.generate_report()
check(18, "报告导出", "报告非空且含关键数字", f"长度{len(report)}字符", len(report) > 1000 and "79.3" in report or "增长" in report)

# 19 群体标签管理(基于真实字段)
tag_cols = [c for c in demand.columns if c.startswith("行业_") or c.startswith("供应链因素_")]
check(19, "群体标签管理", "标签维度基于真实字段", f"{len(tag_cols)}个标签字段", len(tag_cols) >= 20)

# 20 人工审核(执行日志可查)
logs = read_logs()
check(20, "人工审核/执行日志", "日志可追溯", f"{len(logs)}条日志", len(logs) >= 1)

# 输出结果表
df = pd.DataFrame(RESULTS)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "测试结果.xlsx")
os.makedirs(os.path.dirname(out), exist_ok=True)
df.to_excel(out, index=False)
passed = sum(1 for r in RESULTS if r["结果"] == "通过")
print(f"\n===== 测试结果：{passed}/{len(RESULTS)} 通过 =====")
print("结果已写入:", out)
