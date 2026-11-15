# DESIGN.md — AI 国际采购商洞察与客户运营助手 · 项目演示

## 全局视觉约定

### ① 画布与安全区
- 画布 1280×720；padding 上下 60px / 左右 60px；内容区 1160×600。

### ② 配色（科技蓝）
| 槽位 | Hex | 用途 |
|---|---|---|
| 主色 | #2563EB | 标题强调、编号、主图形 |
| 辅色 | #06B6D4 | 卡片底、图表第二序列、分隔 |
| 强调色 | #F59E0B | 关键数字、核心标注 |
| 底色 | #FFFFFF | 主背景 |
| 正文 | #1E293B | 主文字 |
| 浅底 | #EFF6FF | 卡片浅底 |

### ③ 字体
- 中文：微软雅黑（Microsoft YaHei）；西文：Helvetica / Arial
- 字号阶梯：封面主标 72 / 页面主标 32 / 巨型数字 96 / 卡片小标 22 / 正文 18 / 脚注 14

### ④ 视觉母题
标题下 1px 贯通细线（#2563EB），全篇复用。

### ⑤ 配图
全部用 SVG 结构化图形（流程链、架构图、巨型数字），不生成照片——本项目是数据/技术分享，结构化图形更贴合。

## 逐页设计（9 页）

| # | 标题 | type | role/rhythm | 版式 | 视觉 |
|---|---|---|---|---|---|
| 1 | 封面 | cover | hero/peak | 大字报式 | 主色块 + 大标题 |
| 2 | 为什么做：数据分散的痛点 | content | supporting/valley | 卡片组+结论条 | 4 痛点卡 |
| 3 | 数据资产：7 份真实问卷 | content | supporting/valley | 数据展示 | Table |
| 4 | 核心洞察 | content | hero/peak | 巨型数字+洞察 | 大数字 79.3% |
| 5 | 产品能力：5 大功能 | content | supporting/valley | 流程链 | SVG 流程 |
| 6 | Harness 工作流 | content | supporting/valley | 流程链 | SVG 7 步 |
| 7 | 可靠性：AI 不编数据 | content | supporting/valley | 对比式 | 普通Prompt vs Harness |
| 8 | 测试与个人贡献 | content | supporting/valley | 数据展示 | 20/20 大数 + 贡献 |
| 9 | 结束页 | ending | hero/peak | 收束金句+落款 | 主色底 |

节奏：Hero 2 页（封面、结束），中段 1 页核心洞察峰值；相邻版式不同。
