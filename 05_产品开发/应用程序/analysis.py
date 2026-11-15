# -*- coding: utf-8 -*-
"""
analysis.py — 确定性统计分析引擎
原则：所有统计用 pandas 确定性计算，不引入任何模型推断。
每个函数返回 (result, evidence)，evidence 记录数据来源/字段/样本量/口径，供追溯。
"""
import pandas as pd
from data_loader import find_col
from config import continent_of, SATISFACTION_SCALE


def _ev(source, field, sample, valid, note=""):
    return {
        "数据来源": source,
        "字段": field,
        "样本量": sample,
        "有效样本": valid,
        "统计口径": note or "有效样本内占比",
    }


def continent_distribution(df, source):
    """大洲分布。返回 (sorted counts dict, evidence)。"""
    col = find_col(df, ["國家"]) or find_col(df, ["国家"]) or find_col(df, ["Country"])
    if not col:
        return {}, _ev(source, "无国家字段", len(df), 0, "字段缺失")
    s = df[col].dropna().astype(str).str.strip()
    s = s[s != ""]
    cont = s.map(continent_of)
    counts = cont.value_counts().to_dict()
    return counts, _ev(source, col, len(df), len(s))


def top_countries(df, source, n=10):
    """国家 Top N。"""
    col = find_col(df, ["國家"]) or find_col(df, ["国家"]) or find_col(df, ["Country"])
    if not col:
        return {}, _ev(source, "无国家字段", len(df), 0, "字段缺失")
    s = df[col].dropna().astype(str).str.strip()
    s = s[s != ""]
    counts = s.value_counts().head(n).to_dict()
    return counts, _ev(source, col, len(df), len(s), f"国家Top{n}")


def categorical_dist(df, source, keywords, exclude=None):
    """单变量（单选）分布。按关键字定位列。"""
    col = find_col(df, keywords, exclude=exclude)
    if not col:
        return {}, _ev(source, "未定位字段:" + "/".join(keywords), len(df), 0, "字段缺失")
    s = df[col].dropna()
    counts = s.value_counts().to_dict()
    return counts, _ev(source, col, len(df), len(s))


def multi_select_counts(df, source, prefix, top_n=None):
    """多选题计数。列名以 prefix 开头、值为 1 表示选中。返回 [(选项, 次数, 占比%)]"""
    cols = [c for c in df.columns if str(c).startswith(prefix)]
    if not cols:
        return [], _ev(source, f"前缀:{prefix}", len(df), 0, "无匹配列")
    total = len(df)
    out = []
    for c in cols:
        sel = int((df[c].astype(str).str.strip() == "1").sum())
        option = str(c).replace(prefix, "").strip()
        pct = round(sel / total * 100, 1) if total else 0
        out.append({"选项": option, "次数": sel, "占比%": pct})
    out.sort(key=lambda x: -x["次数"])
    if top_n:
        out = out[:top_n]
    return out, _ev(source, f"多选前缀:{prefix}", total, total, "多选题，占比可能合计>100%")


def satisfaction_summary(df, source, keywords, exclude=None):
    """满意度汇总。返回 {档位: 次数, 满意及以上占比%}。编码 1=非常满意。"""
    col = find_col(df, keywords, exclude=exclude)
    if not col:
        return {}, _ev(source, "未定位满意度字段", len(df), 0, "字段缺失")
    s = df[col].dropna().astype(int)
    valid = len(s)
    counts = s.value_counts().sort_index().to_dict()
    sat = int(((s == 1) | (s == 2)).sum())
    rate = round(sat / valid * 100, 1) if valid else 0
    return {
        "分布": {str(k): int(v) for k, v in counts.items()},
        "满意及以上占比%": rate,
        "满意及以上人数": sat,
        "编码说明": SATISFACTION_SCALE,
    }, _ev(source, col, len(df), valid, "满意度编码 1=非常满意...5=非常不满意")
