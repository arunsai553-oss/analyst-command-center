from playwright.sync_api import sync_playwright
import time
import os

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1600, 'height': 1000})
    print("Testing Tableau Data Studio...")
    try:
        page.goto("http://localhost:8505/Tableau_Data_Studio", wait_until="networkidle", timeout=60000)
        time.sleep(15)  # PyGWalker needs more time to render
        page.screenshot(path="test_results/6_Tableau_new.png", full_page=True)
        print("SUCCESS: Saved test_results/6_Tableau_new.png")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    browser.close()
