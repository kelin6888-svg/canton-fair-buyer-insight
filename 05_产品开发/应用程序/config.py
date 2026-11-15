# -*- coding: utf-8 -*-
"""
config.py — 全局配置与字段映射（配置与程序分离）
"""
import os

# 项目根目录（本文件位于 05_产品开发/应用程序/ 下，向上三级到项目根）
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "03_数据工程")
CLEAN_DIR = os.path.join(DATA_DIR, "清洗数据")
DESENS_DIR = os.path.join(DATA_DIR, "真实脱敏数据")
DB_DIR = os.path.join(PROJECT_ROOT, "05_产品开发", "数据库")
LOG_DIR = os.path.join(PROJECT_ROOT, "06_Agent_Harness", "执行日志")
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 7 份问卷注册表：code -> (中文名, 文件路径, 数据空间)
QUESTIONNAIRES = {
    "demand": ("重点市场采购需求变化", os.path.join(DESENS_DIR, "采购需求问卷_清洗后.csv")),
    "emerging": ("境外采购商综合(新兴产业)", os.path.join(DESENS_DIR, "新兴产业问卷_清洗后.csv")),
    "trade_service": ("贸易服务", os.path.join(CLEAN_DIR, "trade_service_清洗后.csv")),
    "exhibitor_product": ("展商展品评价", os.path.join(CLEAN_DIR, "exhibitor_product_清洗后.csv")),
    "participation_service": ("参会服务", os.path.join(CLEAN_DIR, "participation_service_清洗后.csv")),
    "accommodation": ("住宿情况", os.path.join(CLEAN_DIR, "accommodation_清洗后.csv")),
    "catering": ("餐饮服务", os.path.join(CLEAN_DIR, "catering_清洗后.csv")),
}

# 国家 -> 大洲 标准化（处理"大洲-国家"与纯国家名混用）
BARE_COUNTRY_CONTINENT = {
    "UK": "Europe", "USA": "North America", "US": "North America",
    "China": "Asia", "Brazil": "South America", "South Africa": "Africa",
    "UAE": "Middle East", "Russia": "Europe",
}

# 满意度编码说明（问卷星序号：1=最高档）
SATISFACTION_SCALE = "1=非常满意, 2=满意, 3=一般, 4=不满意, 5=非常不满意（问卷星选项序号）"

# 大模型 API（可选，放环境变量；未设置时走纯规则问答，不依赖外部服务）
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "")


def continent_of(country_str):
    """把国家值标准化为大洲。支持 '大洲-国家' 与纯国家名。"""
    if not isinstance(country_str, str) or not country_str.strip():
        return "未知"
    s = country_str.strip()
    # 形如 "Asia-India" / "North America-United States" / "Asia-China - Hong Kong SAR"
    if "-" in s:
        head = s.split("-")[0].strip()
        if head in ("Asia", "Europe", "Africa", "Oceania", "Middle East"):
            return head
        if head in ("North America", "South America", "Latin America"):
            return head
    # 纯国家名映射
    for k, v in BARE_COUNTRY_CONTINENT.items():
        if s.lower().startswith(k.lower()):
            return v
    return "其他"
