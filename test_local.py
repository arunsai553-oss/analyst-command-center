from playwright.sync_api import sync_playwright
import time
import os

urls = {
    "0_Home": "http://localhost:8505",
    "1_Market_Scanner": "http://localhost:8505/Market_and_Company_Scanner",
    "2_Deep_Dive": "http://localhost:8505/Deep_Dive_Lab",
    "3_Forecast": "http://localhost:8505/Forecast_and_Scenarios",
    "4_Experiments": "http://localhost:8505/Experiments_and_KPIs",
    "5_Executive": "http://localhost:8505/Executive_Summary",
    "6_Tableau": "http://localhost:8505/Tableau_Data_Studio"
}

output_dir = "test_results"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1600, 'height': 900})
    
    for name, url in urls.items():
        print(f"Testing {name} at {url}...")
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            # Wait for Streamlit "RUNNING" overlay to disappear or for content to appear
            time.sleep(10) 
            path = os.path.join(output_dir, f"{name}.png")
            page.screenshot(path=path, full_page=True)
            print(f"SUCCESS: Saved {path}")
        except Exception as e:
            print(f"ERROR: Failed {name}: {str(e)}")
            
    browser.close()
