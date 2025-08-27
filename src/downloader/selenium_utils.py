import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.settings import WAIT


def wait_for_page(driver, timeout=WAIT):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(0.5)


def click_when_clickable(driver, locator, timeout=WAIT):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    el.click()
    return el


def url_contains_any(driver, substrings, timeout=180):
    WebDriverWait(driver, timeout).until(
        lambda d: any(s in d.current_url for s in substrings)
    )
