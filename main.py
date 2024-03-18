from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

main = FastAPI()


@main.get("/get-keyword-results/")
async def get_keyword_results(keyword: str):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-images')
    options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(service=Service('/app/chromedriver'), options=options)

    try:
        driver.get(f"https://tools.wordstream.com/fkt?website={keyword}")

        def click_with_retry(selector, retries=3, delay=1):
            for attempt in range(retries):
                try:
                    driver.execute_script(f'document.querySelector("{selector}").click();')
                    return
                except Exception:
                    time.sleep(delay)

        time.sleep(1)
        click_with_retry("#refine-continue", retries=3, delay=1)

        WebDriverWait(driver).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.sc-bTmccw.cFltLW.MuiTable-root"))
        )
        WebDriverWait(driver).until(
            EC.element_to_be_clickable((By.ID, "download-keywords"))
        )

        tbody = driver.find_element(By.CSS_SELECTOR, "tbody.MuiTableBody-root")
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        extracted_data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
            row_data = {
                "keyword": cells[0].text,
                "search_volume": cells[1].text,
                "cpc_low": cells[2].text,
                "cpc_high": cells[3].text,
                "competition": cells[4].text
            }
            extracted_data.append(row_data)

        return {"data": extracted_data}

    except Exception as e:
        return {"error": "An unexpected error occurred."}

    finally:
        driver.quit()
