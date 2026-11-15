# -*- coding: utf-8 -*-
"""
app.py — Streamlit 主界面（v2 视觉重构版）

模块：数据概览 / 洞察 Dashboard / AI 问答 / 任务记录 / 自动报告
说明：本文件只负责「呈现」。所有统计仍由 analysis.py 确定性计算，
      Harness、QA、报告生成逻辑均未改动，原版见 ../应用程序_原版备份_20261115/
视觉：theme.py 设计系统（与项目演示 PPT 的科技蓝体系一致）
运行：streamlit run app.py
"""
import re
import html as _html
from contextlib import contextmanager

import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_all
from config import QUESTIONNAIRES
import analysis as A
from harness import Harness, read_logs
import qa
import report_gen
import theme as T

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="AI 国际采购商洞察与客户运营助手 · 第140届广交会",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
T.inject()


@st.cache_data(show_spinner="正在加载 7 份脱敏问卷…")
def get_data():
    return load_all()


data, overview = get_data()
harness = Harness(data)


# ---------- KPI（全部现场确定性计算，不硬编码） ----------
def compute_kpis():
    d = data["demand"]["df"]
    dist, ev = A.categorical_dist(d, "采购需求问卷_清洗后.csv", ["采购额变化"])
    growth = sum(v for k, v in dist.items() if "增长" in str(k))
    valid = ev.get("有效样本", 0)
    growth_rate = round(growth / valid * 100, 1) if valid else 0.0

    cont, _ = A.continent_distribution(d, "采购需求问卷_清洗后.csv")
    total_cont = sum(cont.values())
    asia_rate = round(cont.get("Asia", 0) / total_cont * 100, 1) if total_cont else 0.0

    es, _ = A.satisfaction_summary(data["exhibitor_product"]["df"],
                                   "exhibitor_product_清洗后.csv", ["參展商", "滿意"])
    ps, _ = A.satisfaction_summary(data["participation_service"]["df"],
                                   "participation_service_清洗后.csv", ["整體服務", "滿意"])
    return {
        "问卷数": len(data),
        "记录数": int(overview["行数"].sum()),
        "growth": growth_rate,
        "asia": asia_rate,
        "exhibitor": es.get("满意及以上占比%", "N/A"),
        "participation": ps.get("满意及以上占比%", "N/A"),
    }


K = compute_kpis()


# ---------- 呈现层工具 ----------
@contextmanager
def card(title, pill="", hint="", foot=""):
    """原生边框容器做卡片，保证 head / 图表 / 脚注被完整包裹。"""
    with st.container(border=True):
        st.markdown(T.chart_head(title, pill, hint), unsafe_allow_html=True)
        yield
        if foot:
            st.markdown(T.chart_foot(foot), unsafe_allow_html=True)


def plot(fig):
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False, "responsive": True})


def _inline(t):
    """Markdown 行内语法 → HTML（先转义，避免注入）。"""
    t = _html.escape(t)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)


def md_to_html(md):
    """把 qa.py 的八段式 Markdown 转成 HTML，便于在单个渲染单元里完整包裹卡片。
    仅做展示转换，不改动任何数值与文字。"""
    out = []
    for ln in (md or "").split("\n"):
        s = ln.strip()
        if not s:
            continue
        if s.startswith("### "):
            out.append(f"<h3>{_inline(s[4:])}</h3>")
        elif s.startswith("> "):
            out.append(f"<blockquote>{_inline(s[2:])}</blockquote>")
        elif s.startswith("- "):
            out.append(f"<p class='li'>{_inline(s[2:])}</p>")
        elif re.match(r"^\d+\. ", s):
            out.append(f"<p class='li'>{_inline(re.sub(r'^\d+\. ', '', s))}</p>")
        else:
            out.append(f"<p>{_inline(s)}</p>")
    return "".join(out)


# ---------- 顶部品牌区 ----------
st.markdown(T.hero(), unsafe_allow_html=True)

st.markdown(T.kpi_grid([
    {"label": "接入问卷", "value": K["问卷数"], "unit": "类", "foot": "第 140 届 · 独立样本", "accent": T.PRIMARY},
    {"label": "清洗后作答记录", "value": f'{K["记录数"]:,}', "unit": "条", "foot": "已去重 · 已脱敏", "accent": T.CYAN},
    {"label": "采购额预期增长", "value": K["growth"], "unit": "%", "foot": "采购需求问卷 · 有效样本内", "accent": T.AMBER},
    {"label": "亚洲采购商占比", "value": K["asia"], "unit": "%", "foot": "按国家字段标准化", "accent": T.PRIMARY},
    {"label": "参展商满意度", "value": K["exhibitor"], "unit": "%", "foot": "满意及以上占比", "accent": T.CYAN},
    {"label": "参会服务满意度", "value": K["participation"], "unit": "%", "foot": "满意及以上占比", "accent": T.GREEN},
]), unsafe_allow_html=True)

st.markdown(T.note(
    "<b>统计口径提醒：</b>7 份问卷为相互独立的样本，作答记录数<b>不可相加视为唯一采购商人数</b>；"
    "不同问卷的有效样本量分别统计。本项目无访谈记录，全部结论来自结构化问卷。", "warn"),
    unsafe_allow_html=True)

# ---------- 侧边栏 ----------
with st.sidebar:
    st.markdown(
        '<div class="sb-brand"><span class="lg">◈</span><span class="nm">采购商洞察工作台</span>'
        '<div class="sb-sub">第 140 届广交会 · 真实调研数据<br>AI 调研分析工作流 v2.0</div></div>',
        unsafe_allow_html=True)
    st.markdown('<div class="sb-title">数据源 · 7 份问卷</div>', unsafe_allow_html=True)
    rows = []
    for _, r in overview.iterrows():
        name = str(r["问卷"])
        rows.append(
            f'<div class="sb-row"><span style="display:flex;align-items:center;gap:8px;min-width:0">'
            f'<span class="dot"></span><span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name}</span>'
            f'</span><span class="n">{int(r["行数"]):,}</span></div>'
        )
    st.markdown("".join(rows), unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-note"><b>⚠ 口径约束</b><br>各问卷独立抽样，样本量不可相加；'
        '餐饮问卷国家字段缺失约 82.4%，涉国家分析已单独标注。</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div class="sb-foot">敏感字段（证件号 / IP / 来源详情 / 调研员编号）'
        '已在清洗阶段剔除。<br>本系统为独立个人项目原型，非广交会官方系统。</div>',
        unsafe_allow_html=True)

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "01 · 数据概览", "02 · 市场洞察", "03 · AI 分析问答", "04 · 执行与质控", "05 · 自动报告",
])

# ============ 01 数据概览 ============
with tab1:
    st.markdown(T.section("01 / DATA ASSETS", "数据质量审查",
                          "7 份问卷逐份检查行数、列数与国家字段缺失率；清洗与脱敏在导入前完成。"),
                unsafe_allow_html=True)

    with card("问卷数据质量总表", "7 份问卷", "行数 / 列数 / 国家缺失率",
              foot="来源：03_数据工程/清洗数据/ 与 真实脱敏数据/ · 口径：清洗去重后的独立样本"):
        st.dataframe(overview, use_container_width=True, hide_index=True)

    st.markdown(T.note(
        "<b>脱敏说明：</b>证件号、来自 IP、来源详情、调研员编号已在清洗阶段剔除，"
        "公开演示数据<b>零敏感字段残留</b>；证件号仅作为跨批次去重的临时键，用完即删。", "ok"),
        unsafe_allow_html=True)

    miss = pd.to_numeric(overview.get("国家缺失率%"), errors="coerce") if "国家缺失率%" in overview else None
    worst = overview.loc[miss.idxmax()] if miss is not None and miss.notna().any() else None
    if worst is not None and float(miss.max()) > 0:
        st.markdown(T.note(
            f"<b>已知质量限制：</b>「{worst['问卷']}」国家字段缺失率 "
            f"<b>{worst['国家缺失率%']}%</b>（问卷字段跨批次演进所致）。"
            "涉该问卷的国家/大洲分析已单独标注，未用其他问卷填补。", "warn"),
            unsafe_allow_html=True)

# ============ 02 市场洞察 ============
with tab2:
    st.markdown(T.section("02 / MARKET INSIGHT", "国际市场洞察 Dashboard",
                          "图表全部由确定性统计引擎生成，每张图下方标注数据来源、样本量与统计口径。"),
                unsafe_allow_html=True)

    q_choice = st.selectbox("选择问卷（用于大洲 / 国家分布）", list(QUESTIONNAIRES.keys()),
                            format_func=lambda c: QUESTIONNAIRES[c][0])
    df = data[q_choice]["df"]
    src = QUESTIONNAIRES[q_choice][1].replace("\\", "/").split("/")[-1]
    q_rows = int(data[q_choice]["quality"].get("行数", 0))
    st.markdown(
        f'<div style="margin:2px 0 12px 0"><span class="tag blue">当前问卷</span>'
        f'<span class="tag gray">{QUESTIONNAIRES[q_choice][0]}</span>'
        f'<span class="tag amber">样本量 {q_rows:,}</span>'
        f'<span class="tag green">已脱敏</span></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        cont, ev = A.continent_distribution(df, src)
        with card("大洲分布", f"有效 {ev['有效样本']:,}", "按国家字段标准化",
                  foot=f"来源 {src} · 字段 {ev['字段']} · 样本 {ev['样本量']:,} · 口径：{ev['统计口径']}"):
            if cont:
                cdf = pd.DataFrame({"大洲": list(cont.keys()), "采购商数": list(cont.values())})
                fig = px.bar(cdf, x="大洲", y="采购商数", color="采购商数",
                             color_continuous_scale=T.BLUE_SCALE)
                plot(T.style_fig(fig, height=290))
            else:
                st.warning("该问卷无国家字段或字段缺失。")
    with col2:
        top, ev2 = A.top_countries(df, src, n=10)
        with card("国家 / 地区 Top 10", "Top 10", "按作答次数降序",
                  foot=f"来源 {src} · 字段 {ev2['字段']} · 样本 {ev2['样本量']:,} · 口径：{ev2['统计口径']}"):
            if top:
                tdf = pd.DataFrame({"国家": list(top.keys()), "采购商数": list(top.values())})
                fig = px.bar(tdf, x="采购商数", y="国家", orientation="h", color="采购商数",
                             color_continuous_scale=T.CYAN_SCALE)
                fig.update_layout(yaxis=dict(autorange="reversed"))
                plot(T.style_fig(fig, height=290))
            else:
                st.warning("该问卷无国家字段或字段缺失。")

    col3, col4 = st.columns(2)
    with col3:
        cats, _ = A.multi_select_counts(data["demand"]["df"], "采购需求问卷_清洗后.csv", "行业_", top_n=10)
        with card("采购商品品类关注度", "多选题", "占比 = 选中次数 / 样本量",
                  foot="来源 采购需求问卷_清洗后.csv · 多选题，占比合计可能超过 100%"):
            if cats:
                cdf = pd.DataFrame(cats)
                fig = px.bar(cdf, x="占比%", y="选项", orientation="h", color="占比%",
                             color_continuous_scale=T.BLUE_SCALE)
                fig.update_layout(yaxis=dict(autorange="reversed"))
                plot(T.style_fig(fig, height=290))
    with col4:
        emg, _ = A.multi_select_counts(data["emerging"]["df"], "新兴产业问卷_清洗后.csv", "关注_")
        with card("新兴战略产业关注度", "多选题", "占比 = 选中次数 / 样本量",
                  foot="来源 新兴产业问卷_清洗后.csv · 多选题，占比合计可能超过 100%"):
            if emg:
                edf = pd.DataFrame(emg)
                fig = px.bar(edf, x="占比%", y="选项", orientation="h", color="占比%",
                             color_continuous_scale=T.AMBER_SCALE)
                fig.update_layout(yaxis=dict(autorange="reversed"))
                plot(T.style_fig(fig, height=290))

    st.markdown(T.section("02 / SERVICE QUALITY", "服务评价",
                          "满意度编码：1=非常满意 … 5=非常不满意；下图展示「满意及以上（1+2）」占比。"),
                unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    for col, (title, code, src_name, kw) in zip(
        (s1, s2),
        [("参展商满意度", "exhibitor_product", "exhibitor_product_清洗后.csv", ["參展商", "滿意"]),
         ("参会整体服务满意度", "participation_service", "participation_service_清洗后.csv", ["整體服務", "滿意"])],
    ):
        with col:
            res, ev = A.satisfaction_summary(data[code]["df"], src_name, kw)
            rate = res.get("满意及以上占比%", 0)
            sat = res.get("满意及以上人数", 0)
            valid = ev.get("有效样本", 0)
            with card(title, f"有效 {valid:,}", "满意及以上占比",
                      foot=f"来源 {src_name} · {res.get('编码说明', '')} · 满意及以上 {sat:,} 人 / 有效 {valid:,}"):
                fig = T.donut(["满意及以上", "其他档位"], [sat, max(valid - sat, 0)],
                              title=f"{rate}%", height=250,
                              colors=[T.PRIMARY, "#E8EEF7"] if code == "exhibitor_product"
                              else [T.CYAN, "#E8EEF7"])
                plot(fig)

# ============ 03 AI 分析问答 ============
with tab3:
    st.markdown(T.section("03 / AI ANALYST", "AI 数据分析问答",
                          "AI 只调用确定性统计工具，数值不经过语言模型；每个回答强制附数据来源、样本量与口径。"),
                unsafe_allow_html=True)

    EXAMPLES = [
        ("🌍 大洲分布", "哪些大洲的采购商最多？"),
        ("📈 采购需求", "采购需求变化如何？"),
        ("📦 商品品类", "采购商最关注哪些品类？"),
        ("⭐ 满意度", "参展商满意度如何？"),
    ]

    def _set_q(text):
        st.session_state["q"] = text

    ecols = st.columns(4)
    for c, (label, text) in zip(ecols, EXAMPLES):
        c.button(label, on_click=_set_q, args=(text,), use_container_width=True)

    question = st.text_input(
        "请输入分析问题", key="q", placeholder="例如：哪些大洲采购商最多？ / 采购商最关注哪些品类？",
        label_visibility="collapsed")
    ask_clicked = st.button("开始分析", type="primary")

    if ask_clicked and question:
        ans = qa.ask(question, harness, data)
        head = (
            '<div class="ai-head"><div class="ai-avatar">◈</div><div>'
            '<div class="ai-name">AI 调研分析助手</div>'
            '<div class="ai-meta">确定性统计 · 证据可追溯 · 已通过质量检查</div>'
            '</div></div><div class="ai-sep"></div>'
        )
        # 单个渲染单元内完整闭合，确保卡片样式覆盖整篇八段式回答
        st.markdown(f'<div class="answer-card">{head}{md_to_html(ans["markdown"])}</div>',
                    unsafe_allow_html=True)

        h = ans.get("harness", {})
        with st.expander("查看工作流执行步骤与证据（Harness Trace）"):
            for s in h.get("steps", []):
                status = s.get("状态", "")
                tag = "green" if status == "ok" else "amber"
                st.markdown(
                    f'<span class="tag {tag}">{status}</span> '
                    f'<b>{s.get("步骤", "")}</b> · {s.get("结果", "")}',
                    unsafe_allow_html=True)
            st.json(h.get("evidence", {"说明": "该问题未产生统计结果（无依据，已拒绝生成数值结论）"}))
    elif ask_clicked:
        st.markdown(T.note("请先输入问题，或点击上方示例问题。", "warn"), unsafe_allow_html=True)

    st.markdown(T.note(
        "<b>支持的问题类型：</b>大洲 / 国家分布 · 采购需求变化 · 品类行业 · 新兴产业 · "
        "贸易服务 · 展商满意度 · 参会满意度 · 供应链因素。<br>"
        "<b>可靠性设计：</b>无对应字段或样本为空时明确拒答，不编造数据；本项目无访谈记录，"
        "涉及访谈内容的提问会被拒绝。", "info"), unsafe_allow_html=True)

# ============ 04 执行与质控 ============
with tab4:
    st.markdown(T.section("04 / HARNESS TRACE", "AI 任务执行与质量控制记录",
                          "每次问答均记录问题类型、样本量、证据与质量评估结果，可逐条追溯、供人工审核。"),
                unsafe_allow_html=True)
    logs = read_logs()
    if logs:
        ldf = pd.DataFrame(logs)
        passed = int((ldf["状态"] == "通过").sum()) if "状态" in ldf else 0
        st.markdown(T.kpi_grid([
            {"label": "累计任务", "value": len(logs), "unit": "次", "foot": "全部写入 JSONL 日志", "accent": T.PRIMARY},
            {"label": "质量评估通过", "value": passed, "unit": "次", "foot": "有依据 · 样本非空", "accent": T.GREEN},
            {"label": "通过率", "value": round(passed / len(logs) * 100, 1), "unit": "%", "foot": "基于当前日志累计", "accent": T.CYAN},
        ], cols=3), unsafe_allow_html=True)
        with card("执行日志明细", f"{len(logs)} 条", "最新记录在后",
                  foot="来源 06_Agent_Harness/执行日志/execution_log.jsonl · 人工审核状态可由界面确认"):
            st.dataframe(ldf.tail(50), use_container_width=True, hide_index=True)
    else:
        st.markdown(T.note("暂无执行记录。请先到「03 · AI 分析问答」提问。"), unsafe_allow_html=True)

# ============ 05 自动报告 ============
with tab5:
    st.markdown(T.section("05 / REPORT", "自动生成调研分析报告",
                          "一键汇总关键指标、数据口径、质量限制与结论边界，输出可下载的 Markdown 报告。"),
                unsafe_allow_html=True)
    st.markdown(T.note(
        "<b>报告包含：</b>数据资产概览 · 采购需求分析 · 国家/地区分布 · 品类与新兴产业 · "
        "服务评价 · 数据质量限制 · 结论边界。<br>所有数字取自确定性统计结果，非模型生成。", "info"),
        unsafe_allow_html=True)

    if st.button("生成调研分析报告", type="primary"):
        report_md = report_gen.generate_report()
        st.markdown(T.note("<b>✅ 报告已生成</b>，可下载或直接预览下方内容。", "ok"),
                    unsafe_allow_html=True)
        st.download_button("⬇ 下载报告（Markdown）", report_md,
                           file_name="国际采购需求分析报告.md", mime="text/markdown")
        with card("报告预览", "自动生成", "Markdown 格式",
                  foot="来源：report_gen.generate_report() · 数值来自 analysis.py 确定性统计"):
            st.markdown(report_md)
