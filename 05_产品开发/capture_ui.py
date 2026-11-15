# -*- coding: utf-8 -*-
"""
capture_ui.py — 视觉验收脚本（开发辅助，不属于产品运行时）
用真实 Chrome 打开应用，等待 Streamlit 渲染完成，抓取脚本异常并多页截图。
运行前需先启动应用： bash 启动应用.sh
"""
import os
from playwright.sync_api import sync_playwright

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "08_求职作品集", "产品截图")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:8501"
ERROR_KEYS = ["Traceback", "StreamlitAPIException", "AttributeError", "KeyError",
              "ValueError", "ModuleNotFoundError"]


def snap(page, name, full=False):
    path = os.path.join(OUT, name)
    page.screenshot(path=path, full_page=full)
    print(f"  截图 -> {name} ({os.path.getsize(path):,} bytes)")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True,
                                    args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width": 1600, "height": 1050},
                                device_scale_factor=1, color_scheme="light")
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        print("打开应用，等待 Streamlit 渲染…")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector(".hero", timeout=90000)
        page.wait_for_timeout(3500)  # 等 Plotly 图表绘制

        body = page.inner_text("body")
        print("  ✓ 品牌区渲染:", "AI 国际采购商洞察与客户运营助手" in body)
        print("  ✓ KPI 渲染:", "采购额预期增长" in body)
        found = [k for k in ERROR_KEYS if k in body]
        print("  页面异常关键字:", found or "无")
        print("  JS 异常:", errors[:3] or "无")
        snap(page, "新版界面_01_数据概览.png")
        page.evaluate("""() => { const c=document.querySelector('[data-testid="stMain"]'); if(c) c.scrollTo(0, 700); }""")
        page.wait_for_timeout(1200)
        snap(page, "新版界面_01_数据质量表.png")
        page.evaluate("""() => { const c=document.querySelector('[data-testid="stMain"]'); if(c) c.scrollTo(0, 0); }""")
        page.wait_for_timeout(600)

        tabs = page.locator('[role="tab"]')
        print("  Tab 数量:", tabs.count())

        # 02 市场洞察（上半 + 滚动后下半）
        tabs.nth(1).click()
        page.wait_for_timeout(3500)
        snap(page, "新版界面_02_市场洞察.png")
        page.evaluate("""() => {
            const c = document.querySelector('[data-testid="stMain"]') || document.querySelector('main');
            if (c) c.scrollTo(0, 820);
        }""")
        page.wait_for_timeout(1500)
        snap(page, "新版界面_02_市场洞察_下半.png")

        # 03 AI 问答：填入真实问题并提交
        tabs.nth(2).click()
        page.wait_for_timeout(1200)
        try:
            page.get_by_placeholder("例如：哪些大洲采购商最多？ / 采购商最关注哪些品类？").fill(
                "哪些大洲的采购商最多？")
            page.get_by_role("button", name="开始分析").click()
            page.wait_for_timeout(2500)
            txt = page.inner_text("body")
            print("  ✓ AI 回答渲染:", "问题说明" in txt and "结论限制" in txt)
        except Exception as e:
            print("  (问答交互跳过:", e, ")")
        snap(page, "新版界面_03_AI问答.png")
        page.evaluate("""() => { const c=document.querySelector('[data-testid="stMain"]'); if(c) c.scrollTo(0, 760); }""")
        page.wait_for_timeout(1200)
        snap(page, "新版界面_03_AI问答_回答详情.png")

        # 04 执行与质控
        tabs.nth(3).click()
        page.wait_for_timeout(1500)
        snap(page, "新版界面_04_执行与质控.png")

        browser.close()
        print("\n视觉验收完成 ✅  截图目录:", OUT)


if __name__ == "__main__":
    main()
