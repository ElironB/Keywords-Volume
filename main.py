from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

main = FastAPI()


@main.get("/get-keyword-results/")
async def get_keyword_results(keyword: str):
    options = webdriver.ChromeOptions()
    # options.binary_location = os.environ.get("CHROMIUM_PATH")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-images')
    options.page_load_strategy = 'eager'

    # service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    # driver = webdriver.Chrome(service=service, options=options)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(f"https://tools.wordstream.com/fkt?website={keyword}")
        def click_with_retry(selector, retries=3, delay=1):
            for attempt in range(retries):
                try:
                    driver.execute_script(f'document.querySelector("{selector}").click();')
                    print("Clicked the button via JavaScript.")
                    return
                except Exception as e:
                    print(f"Attempt {attempt+1}: Failed to click the button via JavaScript. Retrying...")
                    time.sleep(delay)
                    print("Failed to click the button after retries.")

        # Use JavaScript to click the "Continue" button without waiting for full page load
        time.sleep(1)  # Give it a little extra time to render
        try:
            click_with_retry("#refine-continue", retries=3, delay=1)
        except Exception as e:
            return {"error": "Failed to find or click the 'Continue' button."}

        # Wait for the specific elements to ensure the page has loaded the necessary content
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.sc-bTmccw.cFltLW.MuiTable-root"))
        )
        print("Table has loaded.")

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "download-keywords"))
        )
        # Proceed to extract data from the table
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
        print(f"An error occurred: {e}")
        return {"error": "An unexpected error occurred."}
    finally:
        driver.quit()
