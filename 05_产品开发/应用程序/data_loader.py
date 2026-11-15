# -*- coding: utf-8 -*-
"""
data_loader.py — 数据导入与质量审查
职责：加载 7 份清洗后问卷，返回 DataFrame 与质量统计（行数/列数/缺失）。
"""
import os
import pandas as pd
from config import QUESTIONNAIRES


def load_questionnaire(code):
    """加载单份问卷，返回 (df, meta)。文件不存在时返回 (None, 错误信息)。"""
    name, path = QUESTIONNAIRES[code]
    if not os.path.exists(path):
        return None, {"问卷": name, "错误": f"文件不存在: {path}"}
    df = pd.read_csv(path)
    return df, {"问卷": name, "文件": os.path.basename(path)}


def quality_check(df):
    """对单份 DataFrame 做质量检查，返回统计字典。"""
    if df is None or df.empty:
        return {}
    total = len(df)
    # 国家列
    country_col = find_col(df, ["國家"]) or find_col(df, ["国家"]) or find_col(df, ["Country"])
    country_missing = int(df[country_col].isna().sum()) if country_col else total
    missing_ratio = round(country_missing / total * 100, 1) if total else 0
    return {
        "行数": total,
        "列数": len(df.columns),
        "国家列": country_col or "无",
        "国家缺失": country_missing,
        "国家缺失率%": missing_ratio,
    }


def find_col(df, keywords, exclude=None):
    """按关键字（须全部命中）查找列名，返回第一个匹配列名或 None。"""
    for c in df.columns:
        s = str(c)
        if all(k in s for k in keywords):
            if exclude and any(e in s for e in exclude):
                continue
            return c
    return None


def load_all():
    """加载全部 7 份问卷，返回 {code: {df, meta, quality}} 与总体概览。"""
    data = {}
    overview = []
    for code, (name, path) in QUESTIONNAIRES.items():
        df, meta = load_questionnaire(code)
        q = quality_check(df)
        data[code] = {"df": df, "meta": meta, "quality": q}
        overview.append({
            "问卷": name, "文件": meta.get("文件", "缺失"),
            "行数": q.get("行数", 0), "列数": q.get("列数", 0),
            "国家缺失": q.get("国家缺失", "-"),
            "国家缺失率%": q.get("国家缺失率%", "-"),
        })
    return data, pd.DataFrame(overview)
