import re
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from ..config.settings import WAIT
from .selenium_utils import wait_for_page


def get_student_name(driver):
    wait_for_page(driver)
    try:
        print("Trying primary selector for student name...")
        span = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'students-pager')]//h3/span[last()]"))
        )
        text = (span.text or "").strip()
        name = re.sub(r"\s*\(Forsøk\s+\d+\s+av\s+\d+\)\s*$", "", text).strip()
        if name:
            return name
    except Exception:
        pass

    try:
        print("Trying alternative selectors for student name...")
        h1 = driver.find_element(By.CSS_SELECTOR, "div.students-pager h3 .name-information-profile-card, h1.name-information-profile-card")
        if h1 and h1.text.strip():
            return h1.text.strip()
    except Exception:
        pass

    try:
        print("Trying fallback selector for student name...")
        h3 = driver.find_element(By.CSS_SELECTOR, "div.students-pager h3")
        txt = h3.text or ""
        m = re.search(r"^\s*(.*?)\s*\(Forsøk", txt)
        if m:
            return m.group(1).strip()
    except Exception:
        pass

    return "UkjentStudent"


def get_lab_number(driver):
    wait_for_page(driver)
    try:
        title = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pageTitleHeader #pageTitleText"))
        ).text.strip()
    except Exception:
        title = ""

    m = re.search(r"(\d+)", title)
    lab_num = int(m.group(1)) if m else None
    return title, lab_num


def get_total_items_from_header(driver):
    wait_for_page(driver)
    try:
        h3 = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.criteriaSummary > h3"))
        )
        text = h3.text or ""
        m = re.search(r"(\d+)", text)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def find_download_link(driver):
    wait_for_page(driver)
    locator = (By.CSS_SELECTOR, "div.downloadFile a.dwnldBtn[href*='/webapps/assignment/download']")
    el = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable(locator))
    href = el.get_attribute("href") or ""
    file_basename = None
    if href:
        try:
            qs = parse_qs(urlparse(href).query)
            if "fileName" in qs and qs["fileName"]:
                file_basename = qs["fileName"][0]
        except Exception:
            pass
    return el, href, file_basename
