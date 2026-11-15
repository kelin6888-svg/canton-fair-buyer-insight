# -*- coding: utf-8 -*-
"""
theme.py — 视觉设计系统（仅负责呈现，不参与任何数据计算）

设计语言：与《项目演示.pptx》保持一致的「科技蓝」体系
  主色 #2563EB / 辅色 #06B6D4 / 强调色 #F59E0B / 底色 #FFFFFF / 正文 #1E293B
本模块只提供：全局 CSS、HTML 组件、Plotly 图表统一主题。
业务数据仍全部来自 analysis.py 的确定性统计，不在此处加工。
"""
import streamlit as st
import plotly.graph_objects as go

# ---------- 设计令牌（与 PPT DESIGN.md 一致） ----------
PRIMARY = "#2563EB"
CYAN = "#06B6D4"
AMBER = "#F59E0B"
INK = "#1E293B"
MUTED = "#64748B"
BG = "#F4F7FC"
CARD = "#FFFFFF"
BORDER = "#E2E8F0"
LIGHT = "#EFF6FF"
GREEN = "#10B981"
RED = "#EF4444"

# 图表序列色：蓝 → 青 → 靛 → 金，冷色为主、暖色点睛
PALETTE = ["#2563EB", "#3B82F6", "#06B6D4", "#0EA5E9", "#6366F1",
           "#8B5CF6", "#14B8A6", "#F59E0B", "#F97316", "#94A3B8"]
BLUE_SCALE = [[0, "#BFDBFE"], [0.5, "#60A5FA"], [1, "#1D4ED8"]]
CYAN_SCALE = [[0, "#CFFAFE"], [0.5, "#67E8F9"], [1, "#0891B2"]]
AMBER_SCALE = [[0, "#FEF3C7"], [0.5, "#FBBF24"], [1, "#D97706"]]

_FONT = ('-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", '
         '"Microsoft YaHei", "Hiragino Sans GB", sans-serif')

# ---------- 全局样式 ----------
GLOBAL_CSS = """
<style>
/* ---------- 基础 ---------- */
.stApp { background: BGCOLOR; }
.main .block-container { padding-top: 1.6rem; padding-bottom: 3.5rem; max-width: 1440px; }
h1, h2, h3, h4, h5 { color: #0F172A; letter-spacing: -0.015em; font-weight: 700; }
p, li, span, div { font-family: FONTSTACK; }
.stCaption, .stCaption p, [data-testid="stCaptionContainer"] p { color: #7B8AA3 !important; font-size: 12px !important; }
hr { border-color: #E2E8F0 !important; margin: 1.4rem 0 !important; }

/* ---------- 顶部 Hero ---------- */
.hero {
  position: relative; overflow: hidden; border-radius: 20px;
  padding: 34px 40px 30px 40px; margin-bottom: 20px; color: #FFFFFF;
  background: linear-gradient(118deg, #0A1B33 0%, #123C77 52%, #2563EB 100%);
  box-shadow: 0 16px 38px rgba(16, 45, 95, .20);
}
.hero::before {
  content: ""; position: absolute; inset: 0; opacity: .16;
  background-image: linear-gradient(rgba(255,255,255,.13) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,.13) 1px, transparent 1px);
  background-size: 34px 34px;
}
.hero::after {
  content: ""; position: absolute; right: -90px; top: -150px; width: 430px; height: 430px;
  border-radius: 50%; background: radial-gradient(circle, rgba(6,182,212,.38), transparent 66%);
}
.hero > * { position: relative; z-index: 2; }
.hero .eyebrow {
  font-size: 11px; letter-spacing: .22em; text-transform: uppercase;
  color: #7DD3FC; font-weight: 700; margin-bottom: 12px;
}
.hero h1 { font-size: 32px; line-height: 1.25; margin: 0 0 8px 0; color: #FFFFFF; font-weight: 750; }
.hero .en { font-size: 12px; letter-spacing: .16em; color: #BFDBFE; font-weight: 600; text-transform: uppercase; }
.hero .desc { font-size: 13px; color: #D6E6FF; margin-top: 16px; line-height: 1.7; }
.hero .rule { height: 3px; width: 64px; background: #F59E0B; border-radius: 3px; margin: 16px 0 0 0; }
.hero-badges { display: flex; gap: 9px; flex-wrap: wrap; margin-top: 18px; }
.hero-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 13px; border-radius: 100px; font-size: 11.5px; font-weight: 600;
  background: rgba(255,255,255,.11); border: 1px solid rgba(255,255,255,.24);
  color: #EAF3FF; backdrop-filter: blur(6px);
}
.hero-badge i { width: 6px; height: 6px; border-radius: 50%; background: #34D399; display: inline-block; }

/* ---------- KPI 卡片 ---------- */
.kpi-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin: 4px 0 22px 0; }
@media (max-width: 1200px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); } }
.kpi {
  position: relative; overflow: hidden; background: #FFFFFF;
  border: 1px solid #E2E8F0; border-radius: 14px; padding: 17px 18px 15px 18px;
  box-shadow: 0 2px 10px rgba(15,23,42,.045); transition: transform .18s ease, box-shadow .18s ease;
}
.kpi:hover { transform: translateY(-3px); box-shadow: 0 12px 26px rgba(37,99,235,.13); }
.kpi::before { content: ""; position: absolute; left: 0; top: 0; width: 100%; height: 3px; background: var(--accent, #2563EB); }
.kpi .label { font-size: 11.5px; color: #64748B; font-weight: 600; letter-spacing: .01em; }
.kpi .value { font-size: 27px; font-weight: 750; color: #0F172A; line-height: 1.2; margin: 7px 0 3px 0; font-variant-numeric: tabular-nums; }
.kpi .value em { font-style: normal; font-size: 15px; font-weight: 650; color: #475569; margin-left: 2px; }
.kpi .foot { font-size: 10.5px; color: #94A3B8; line-height: 1.45; }

/* ---------- 区块标题 ---------- */
.section { margin: 6px 0 14px 0; }
.section .kicker { font-size: 10.5px; letter-spacing: .18em; color: #2563EB; font-weight: 750; text-transform: uppercase; }
.section .title { font-size: 19px; font-weight: 720; color: #0F172A; margin-top: 3px; }
.section .sub { font-size: 12.5px; color: #7B8AA3; margin-top: 4px; line-height: 1.6; }
.section .line { height: 1px; background: linear-gradient(90deg, #2563EB 0%, #DBEAFE 22%, transparent 70%); margin-top: 12px; }

/* ---------- 图表卡片内部（外框由 st.container(border=True) 提供） ---------- */
.cc-head {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 2px 0 6px 0; flex-wrap: nowrap;
}
.cc-title { font-size: 14.5px; font-weight: 700; color: #0F172A; white-space: nowrap; }
.cc-right { display: flex; align-items: center; gap: 8px; flex: none; }
.cc-hint { font-size: 11px; color: #94A3B8; white-space: nowrap; }
.cc-pill {
  font-size: 10.5px; font-weight: 650; color: #1D4ED8; background: #EFF6FF;
  border: 1px solid #DBEAFE; padding: 3px 10px; border-radius: 100px; white-space: nowrap;
}
.cc-foot {
  border-top: 1px dashed #E2E8F0; margin-top: 6px; padding-top: 9px;
  font-size: 10.5px; color: #94A3B8; line-height: 1.5;
}

/* ---------- 提示 / 口径框 ---------- */
.note {
  border-radius: 12px; padding: 13px 16px; font-size: 12.5px; line-height: 1.65;
  border: 1px solid #DBEAFE; background: #F0F7FF; color: #1E3A5F; margin: 10px 0 4px 0;
}
.note.warn { border-color: #FDE68A; background: #FFFBEB; color: #92400E; }
.note.ok { border-color: #A7F3D0; background: #ECFDF5; color: #065F46; }
.note b { font-weight: 700; }

/* ---------- 徽章 ---------- */
.tag {
  display: inline-block; font-size: 10.5px; font-weight: 650; padding: 3px 9px;
  border-radius: 6px; margin-right: 6px;
}
.tag.blue { background: #EFF6FF; color: #1D4ED8; border: 1px solid #DBEAFE; }
.tag.amber { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
.tag.green { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
.tag.gray { background: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }

/* ---------- Tabs（兼容 Streamlit 1.6x 新版 role=tab DOM） ---------- */
.stTabs [role="tablist"], .stTabs [data-baseweb="tab-list"] {
  gap: 5px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 13px;
  padding: 6px; box-shadow: 0 2px 10px rgba(15,23,42,.04); margin-bottom: 18px;
}
.stTabs [role="tab"], .stTabs [data-baseweb="tab"] {
  border-radius: 9px; padding: 9px 17px; color: #64748B; font-weight: 650; font-size: 13px;
  transition: all .15s ease; border: none !important; background: transparent !important;
}
.stTabs [role="tab"] p, .stTabs [data-baseweb="tab"] p { color: inherit !important; font-weight: inherit !important; font-size: inherit !important; }
.stTabs [role="tab"]:hover, .stTabs [data-baseweb="tab"]:hover { background: #F1F5F9 !important; color: #2563EB !important; }
.stTabs [role="tab"][aria-selected="true"], .stTabs [data-baseweb="tab"][aria-selected="true"] {
  background: #2563EB !important; color: #FFFFFF !important;
  box-shadow: 0 4px 12px rgba(37,99,235,.28);
}
.stTabs [role="tab"][aria-selected="true"] p { color: #FFFFFF !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"],
.stTabs [data-rac-indicator] { display: none !important; }

/* ---------- 隐藏 Streamlit 自带工具栏（Deploy / 菜单），保持作品纯净 ---------- */
[data-testid="stToolbar"], [data-testid="stAppDeployButton"],
[data-testid="stStatusWidget"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; }

/* ---------- 按钮 / 输入 ---------- */
.stButton > button {
  border-radius: 9px; font-weight: 650; font-size: 13px; padding: 8px 18px;
  border: 1px solid #E2E8F0; transition: all .16s ease;
}
.stButton > button:hover { border-color: #2563EB; color: #2563EB; transform: translateY(-1px); }
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
  background: linear-gradient(118deg, #2563EB, #1D4ED8) !important;
  color: #FFFFFF !important; border: none !important;
  box-shadow: 0 5px 14px rgba(37,99,235,.26) !important;
}
.stTextInput > div > div > input, .stSelectbox > div > div {
  border-radius: 9px !important; border-color: #E2E8F0 !important; font-size: 13px;
}
.stTextInput > div > div > input:focus { border-color: #2563EB !important; box-shadow: 0 0 0 3px rgba(37,99,235,.10) !important; }

/* ---------- 表格 ---------- */
.stDataFrame, [data-testid="stDataFrame"] {
  border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden;
  box-shadow: 0 2px 10px rgba(15,23,42,.035);
}
.stDataFrame table { font-size: 12.5px; }

/* ---------- AI 回答区 ---------- */
.answer-card {
  background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 15px;
  padding: 20px 24px 8px 24px; box-shadow: 0 4px 18px rgba(15,23,42,.05); margin-top: 14px;
  border-top: 3px solid #2563EB;
}
.answer-card h3 {
  font-size: 13px !important; color: #1D4ED8 !important; font-weight: 700 !important;
  letter-spacing: .02em; margin: 16px 0 5px 0 !important; padding-left: 10px;
  border-left: 3px solid #93C5FD;
}
.answer-card blockquote {
  background: #F8FAFC; border-left: 3px solid #06B6D4; border-radius: 6px;
  padding: 8px 14px; margin: 6px 0; color: #334155; font-size: 13px;
}
.answer-card p { font-size: 13px; color: #334155; line-height: 1.7; margin: 4px 0; }
.answer-card .li { position: relative; padding-left: 15px; }
.answer-card .li::before {
  content: ""; position: absolute; left: 2px; top: 9px;
  width: 5px; height: 5px; border-radius: 50%; background: #06B6D4;
}
.answer-card strong { color: #0F172A; font-weight: 700; }
.answer-card .ai-sep { height: 1px; background: #EEF2F7; margin: 12px 0; }
.ai-head { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.ai-avatar {
  width: 30px; height: 30px; border-radius: 9px; flex: none;
  background: linear-gradient(135deg, #2563EB, #06B6D4);
  display: flex; align-items: center; justify-content: center;
  color: #FFF; font-size: 13px; font-weight: 800;
}
.ai-name { font-size: 13px; font-weight: 700; color: #0F172A; }
.ai-meta { font-size: 10.5px; color: #94A3B8; }

/* ---------- 侧边栏 ---------- */
[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E2E8F0; }
[data-testid="stSidebar"] .block-container { padding-top: 1.8rem; }
.sb-brand { padding: 0 2px 14px 2px; border-bottom: 1px solid #E2E8F0; margin-bottom: 16px; }
.sb-brand .lg {
  width: 34px; height: 34px; border-radius: 10px; display: inline-flex; vertical-align: middle;
  align-items: center; justify-content: center; color: #FFF; font-weight: 800; font-size: 15px;
  background: linear-gradient(135deg, #2563EB, #06B6D4); margin-right: 9px;
}
.sb-brand .nm { font-size: 13.5px; font-weight: 750; color: #0F172A; vertical-align: middle; }
.sb-brand .sb-sub { font-size: 10.5px; color: #94A3B8; margin-top: 9px; line-height: 1.5; }
.sb-title { font-size: 10.5px; letter-spacing: .16em; color: #94A3B8; font-weight: 750; margin: 4px 0 10px 0; text-transform: uppercase; }
.sb-row {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  padding: 7px 9px; border-radius: 8px; font-size: 11.5px; color: #334155;
}
.sb-row:hover { background: #F8FAFC; }
.sb-row .dot { width: 6px; height: 6px; border-radius: 50%; background: #2563EB; flex: none; }
.sb-row .n { font-variant-numeric: tabular-nums; color: #64748B; font-weight: 650; }
.sb-note {
  margin-top: 14px; padding: 11px 12px; border-radius: 10px; font-size: 11px; line-height: 1.6;
  background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E;
}
.sb-foot { margin-top: 18px; font-size: 10px; color: #B4C0D0; line-height: 1.6; }
</style>
""".replace("BGCOLOR", BG).replace("FONTSTACK", _FONT)


def inject():
    """注入全局样式（每个页面渲染一次即可）。"""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ---------- HTML 组件 ----------
def hero():
    """顶部品牌横幅：产品定位 + 数据合规徽章。"""
    return """
<div class="hero">
  <div class="eyebrow">Canton Fair · Buyer Intelligence Platform</div>
  <h1>AI 国际采购商洞察与客户运营助手</h1>
  <div class="en">International Buyer Intelligence &amp; CRM Copilot</div>
  <div class="desc">基于第 140 届广交会真实调研数据的 AI 国际采购需求分析与市场洞察系统<br>
  多类问卷 → 结构化数据资产 → 市场洞察 → 可追溯的调研报告</div>
  <div class="rule"></div>
  <div class="hero-badges">
    <span class="hero-badge"><i></i>第 140 届 · 真实问卷数据</span>
    <span class="hero-badge"><i></i>全量脱敏 · 零敏感字段</span>
    <span class="hero-badge"><i></i>确定性统计 · 口径可追溯</span>
    <span class="hero-badge"><i></i>无访谈记录 · 不虚构</span>
  </div>
</div>
"""


def kpi_grid(items, cols=None):
    """KPI 卡片行。items: [{label, value, unit, foot, accent}]；cols 可覆盖默认 6 列。"""
    cards = []
    for it in items:
        unit = f"<em>{it['unit']}</em>" if it.get("unit") else ""
        cards.append(
            f'<div class="kpi" style="--accent:{it.get("accent", PRIMARY)}">'
            f'<div class="label">{it["label"]}</div>'
            f'<div class="value">{it["value"]}{unit}</div>'
            f'<div class="foot">{it.get("foot", "")}</div></div>'
        )
    style = f' style="grid-template-columns:repeat({cols},1fr)"' if cols else ""
    return f'<div class="kpi-grid"{style}>{"".join(cards)}</div>'


def section(kicker, title, sub=""):
    """区块标题（序号 + 说明 + 贯通细线，呼应 PPT 版式）。"""
    return (f'<div class="section"><div class="kicker">{kicker}</div>'
            f'<div class="title">{title}</div><div class="sub">{sub}</div>'
            f'<div class="line"></div></div>')


def note(text, kind="info"):
    cls = "note" + ("" if kind == "info" else " " + kind)
    return f'<div class="{cls}">{text}</div>'


def chart_head(title, pill="", hint=""):
    right = ""
    if hint:
        right += f'<span class="cc-hint">{hint}</span>'
    if pill:
        right += f'<span class="cc-pill">{pill}</span>'
    return (f'<div class="cc-head"><div class="cc-title">{title}</div>'
            f'<div class="cc-right">{right}</div></div>')


def chart_foot(text):
    return f'<div class="cc-foot">{text}</div>'


# ---------- Plotly 统一主题 ----------
def style_fig(fig, height=300, gradient=True, scale=None, show_legend=False):
    """
    统一图表视觉：透明底、去网格、细基线、渐变色阶、统一悬停。
    仅修改外观，不修改任何数据序列。
    """
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=_FONT, size=11.5, color=INK),
        margin=dict(t=14, b=8, l=8, r=8),
        showlegend=show_legend,
        hoverlabel=dict(bgcolor="#0F172A", font_size=12, font_color="#FFFFFF",
                        bordercolor="#0F172A", font_family=_FONT),
        bargap=0.32,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#E2E8F0",
                     tickfont=dict(color=MUTED, size=10.5), title_font=dict(size=11, color=MUTED))
    fig.update_yaxes(showgrid=True, gridcolor="#EEF2F7", gridwidth=1, zeroline=False,
                     showline=False, tickfont=dict(color=MUTED, size=10.5),
                     title_font=dict(size=11, color=MUTED))
    # 连续色映射仅用于视觉渐变，隐藏色条保持画面干净（数值仍可在 hover 中查看）
    try:
        fig.update_coloraxes(showscale=False)
    except Exception:
        pass  # 无 coloraxis 的图表跳过，不影响数据
    if gradient and scale:
        fig.update_traces(marker=dict(
            color=fig.data[0].y if len(fig.data) else None,
            colorscale=scale,
            line=dict(width=0),
        ))
    return fig


def donut(labels, values, title="", height=260, colors=None):
    """高级感环形图（用于满意度/占比）。"""
    colors = colors or [PRIMARY, "#DBEAFE"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.72, sort=False,
        marker=dict(colors=colors, line=dict(color="#FFFFFF", width=3)),
        textfont=dict(size=11, color=INK, family=_FONT),
        hoverinfo="label+value+percent",
    ))
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.08,
                                     xanchor="center", x=0.5, font=dict(size=10.5, color=MUTED)),
        margin=dict(t=8, b=8, l=8, r=8),
        annotations=[dict(text=title, x=0.5, y=0.5, font=dict(size=22, color="#0F172A",
                         family=_FONT, weight="bold"), showarrow=False)],
        hoverlabel=dict(bgcolor="#0F172A", font_size=12, font_color="#FFFFFF"),
    )
    return fig
