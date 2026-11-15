# -*- coding: utf-8 -*-
"""
harness.py — 单 Agent 调研分析工作流（执行与质量控制）
主流程：识别问题类型 → 确认可用数据 → 检查字段/样本 → 调用确定性统计
       → 获取结果 → 证据/结论检查 → 质量评估 → 记录执行日志（人工审核由界面触发）
"""
import json
import time
import os
from config import LOG_DIR, QUESTIONNAIRES

LOG_FILE = os.path.join(LOG_DIR, "execution_log.jsonl")


def _append_log(entry):
    """追加一行执行日志（JSONL，可追溯）。"""
    entry["时间"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_logs():
    """读取历史执行日志。"""
    if not os.path.exists(LOG_FILE):
        return []
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except Exception:
                continue
    return logs


class Harness:
    """单 Agent 工作流：把一次分析任务拆成可检查、可追溯的步骤。"""

    def __init__(self, data):
        # data: {code: {"df":..., "meta":..., "quality":...}}
        self.data = data

    def run(self, task, intent, analyzer):
        """
        task: 用户问题文本
        intent: 识别出的问题类型（str）
        analyzer: 可调用对象，返回 (result, evidence)
        """
        steps = []
        log = {"任务": task, "问题类型": intent}

        # 1. 识别问题类型
        steps.append({"步骤": "识别问题类型", "结果": intent, "状态": "ok"})
        if not intent:
            steps.append({"步骤": "识别问题类型", "结果": "无法识别", "状态": "fail"})
            log["状态"] = "无法识别问题类型"
            _append_log(log)
            return {"result": None, "steps": steps, "log": log}

        # 2. 确认可用问卷数据
        data_code = log.get("数据问卷", intent.split(":")[0] if ":" in intent else "")
        steps.append({"步骤": "确认可用数据", "结果": data_code or "由分析器决定", "状态": "ok"})

        # 3. 调用确定性统计（分析器内部已检查字段与样本）
        try:
            result, evidence = analyzer()
        except Exception as e:
            steps.append({"步骤": "调用统计工具", "结果": f"失败: {e}", "状态": "fail"})
            log["状态"] = "统计失败"
            _append_log(log)
            return {"result": None, "steps": steps, "log": log}

        # 4. 获取统计结果 + 证据检查
        steps.append({
            "步骤": "获取统计结果", "结果": "成功",
            "样本量": evidence.get("样本量"), "有效样本": evidence.get("有效样本"),
            "状态": "ok",
        })

        # 5. 证据/结论检查（无依据则判不合格）
        evidence_ok = evidence.get("有效样本", 0) > 0 and evidence.get("样本量", 0) > 0
        steps.append({
            "步骤": "证据与结论检查",
            "结果": "有依据" if evidence_ok else "无依据（样本为空）",
            "状态": "ok" if evidence_ok else "fail",
        })

        # 6. 质量评估
        quality_ok = evidence_ok
        steps.append({
            "步骤": "质量评估",
            "结果": "通过" if quality_ok else "不通过",
            "状态": "ok" if quality_ok else "fail",
        })

        log["状态"] = "通过" if quality_ok else "不通过"
        log["证据"] = evidence
        _append_log(log)

        return {
            "result": result,
            "evidence": evidence,
            "steps": steps,
            "log": log,
            "质量评估": "通过" if quality_ok else "不通过",
        }
