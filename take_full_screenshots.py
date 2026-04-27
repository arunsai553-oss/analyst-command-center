from playwright.sync_api import sync_playwright
import time

urls = {
    "1_Home_Page_Overview": "https://analyst-co-dsrfyitsyyj2zib2esg6hf.streamlit.app/",
    "2_Market_Scanner": "https://analyst-co-dsrfyitsyyj2zib2esg6hf.streamlit.app/Market_and_Company_Scanner",
    "3_Monte_Carlo_Forecast": "https://analyst-co-dsrfyitsyyj2zib2esg6hf.streamlit.app/Forecast_and_Scenarios",
    "4_Tableau_Data_Studio": "https://analyst-co-dsrfyitsyyj2zib2esg6hf.streamlit.app/Tableau_Data_Studio"
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    # Set viewport large enough to trigger desktop view
    page = browser.new_page(viewport={'width': 1600, 'height': 900})
    
    for name, url in urls.items():
        print(f"Capturing full page for {name}...")
        page.goto(url)
        # Wait for Streamlit to render charts
        time.sleep(6) 
        
        # Take full page screenshot
        page.screenshot(path=f"{name}.png", full_page=True)
        print(f"Saved {name}.png")
        
    browser.close()
