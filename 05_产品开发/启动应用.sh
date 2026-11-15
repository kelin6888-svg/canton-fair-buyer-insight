#!/usr/bin/env bash
# AI 国际采购商洞察与客户运营助手 —— 本地启动脚本
# 用法：在本文件所在目录执行  bash 启动应用.sh
# 启动后浏览器打开： http://127.0.0.1:8501
set -e
cd "$(dirname "$0")/应用程序"
PORT=8501
echo "正在启动 AI 国际采购需求分析系统 (http://127.0.0.1:$PORT) ..."
exec python -m streamlit run app.py --server.headless true --server.port "$PORT" --server.address 127.0.0.1
