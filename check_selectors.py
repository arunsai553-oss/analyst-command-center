from playwright.sync_api import sync_playwright
import time

PAGES = {
    'home': 'http://localhost:8505',
    'forecast': 'http://localhost:8505/Forecast_and_Scenarios',
    'experiments': 'http://localhost:8505/Experiments_and_KPIs',
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1600,'height':900})
    
    for name, url in PAGES.items():
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(18)
        metrics = page.locator('[data-testid=stMetric]').count()
        charts  = page.locator('[data-testid=stPlotlyChart]').count()
        upload  = page.locator('[data-testid=stFileUploader]').count()
        mselect = page.locator('[data-testid=stMultiSelect]').count()
        errors  = page.locator('[data-testid=stException]').count()
        print(f'{name}: metrics={metrics}, charts={charts}, upload={upload}, mselect={mselect}, errors={errors}')
    
    browser.close()
