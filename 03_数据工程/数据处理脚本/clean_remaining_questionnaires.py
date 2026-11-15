# -*- coding: utf-8 -*-
"""
clean_remaining_questionnaires.py — 清洗其余5份问卷（贸易服务/展商展品/参会服务/住宿/餐饮）
步骤：
1. 合并3个数据批次（10.18-10.20 / 10.23-10.25 / 10.26-10.28）
2. 按"证件号"去重（同一采购商多次填写，保留最新提交）——证件号仅作临时去重键，用后删除
3. 剔除敏感字段（证件号/IP/来源详情/调研员编号/来源/所用时间/序号）
4. 字段对齐（住宿/餐饮跨批次列数不同，取并集并标注）
5. 输出清洗后CSV + 数据质量统计
只读原始文件，写入本项目 03_数据工程/清洗数据/。
"""
import os
import glob
import json
import pandas as pd

GONGPAN = r"<原始资料目录>"
BASE = r"<项目根目录>"
OUT_DIR = os.path.join(BASE, "03_数据工程", "清洗数据")
os.makedirs(OUT_DIR, exist_ok=True)

BATCHES = ["10.18-10.20", "10.23-10.25", "10.26-10.28"]

TYPES = [
    ("贸易服务", "貿易服務", "trade_service"),
    ("展商展品", "展商展品評價", "exhibitor_product"),
    ("参会服务", "參會服務", "participation_service"),
    ("住宿", "住宿情況", "accommodation"),
    ("餐饮", "餐飲服務", "catering"),
]

SENSITIVE_HINTS = ["證件號", "证件号", "Badge", "来自IP", "IP", "來源詳情", "来源详情",
                   "调研员编号", "調研員編號", "Survey Staff", "來源", "来源", "所用时间", "所用時間", "序号", "序號"]

def find_batches(kw):
    files = {}
    for f in glob.glob(os.path.join(GONGPAN, "**", "*.xlsx"), recursive=True):
        b = os.path.basename(f)
        if "~$" in b or "修改后" in f or "副本" in b or "_已处理" in b or "修改版" in f:
            continue
        if kw not in b:
            continue
        d = os.path.normpath(f).split(os.sep)[-2]
        if d in BATCHES:
            files[d] = f
    return files

def find_col(df, hints):
    for c in df.columns:
        if all(h in str(c) for h in hints):
            return c
    return None

def is_sensitive(col):
    return any(h in str(col) for h in SENSITIVE_HINTS)

report = {}

for label, kw, code in TYPES:
    files = find_batches(kw)
    print("=" * 72)
    print(f"【{label}】批次文件 {len(files)} 个")
    frames = []
    per_batch = {}
    for d in BATCHES:
        if d not in files:
            per_batch[d] = 0
            continue
        df = pd.read_excel(files[d], sheet_name=0)
        per_batch[d] = len(df)
        frames.append(df)

    if not frames:
        print("  无数据，跳过")
        continue

    raw = pd.concat(frames, ignore_index=True)

    # 证件号列（临时去重键）
    badge_col = find_col(raw, ["證件號"]) or find_col(raw, ["Badge"])
    time_col = find_col(raw, ["提交答卷时间", "提交答卷時間"]) or find_col(raw, ["提交"])

    before = len(raw)
    if badge_col:
        # 保留最新提交：按提交时间排序后 drop_duplicates keep last
        if time_col:
            raw[time_col] = pd.to_datetime(raw[time_col], errors="coerce")
            raw = raw.sort_values(time_col, na_position="first")
        raw = raw.drop_duplicates(subset=[badge_col], keep="last")
        dup_removed = before - len(raw)
    else:
        dup_removed = 0

    # 剔除敏感字段
    drop_cols = [c for c in raw.columns if is_sensitive(c)]
    clean = raw.drop(columns=drop_cols)

    # 保留提交答卷时间（重命名为提交时间），其余敏感/无用已剔除
    out_path = os.path.join(OUT_DIR, f"{code}_清洗后.csv")
    clean.to_csv(out_path, index=False, encoding="utf-8-sig")

    report[code] = {
        "问卷": label,
        "原始行数": before,
        "去重后行数": len(clean),
        "去除重复": dup_removed,
        "各批次": per_batch,
        "剔除敏感字段数": len(drop_cols),
        "最终列数": len(clean.columns),
        "文件": os.path.basename(out_path),
    }
    print(f"  原始 {before} 行 → 去重后 {len(clean)} 行（去除重复 {dup_removed}）")
    print(f"  剔除敏感字段 {len(drop_cols)} 个；最终 {len(clean.columns)} 列")
    print(f"  已输出: {out_path}")

# 输出质量统计JSON
with open(os.path.join(OUT_DIR, "_数据质量统计.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("\n质量统计已写入 _数据质量统计.json")
print("清洗完成。")
