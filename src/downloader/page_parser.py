import re
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from config.settings import WAIT
from .selenium_utils import wait_for_page


def get_student_name(driver):
    wait_for_page(driver)
    try:
        span = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'students-pager')]//h3/span[last()]")
            )
        )
        text = (span.text or "").strip()
        name = re.sub(r"\s*\(Forsøk\s+\d+\s+av\s+\d+\)\s*$", "", text).strip()
        if name:
            return name
    except Exception:
        pass

    return "UkjentStudent"


def get_lab_number(driver):
    wait_for_page(driver)
    try:
        title = (
            WebDriverWait(driver, WAIT)
            .until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#pageTitleHeader #pageTitleText")
                )
            )
            .text.strip()
        )
    except Exception:
        title = ""

    m = re.search(r"(\d+)", title)
    lab_num = int(m.group(1)) if m else None
    return lab_num


def get_total_items_from_header(driver):
    wait_for_page(driver)
    try:
        h3 = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.criteriaSummary > h3")
            )
        )
        text = h3.text or ""
        m = re.search(r"(\d+)", text)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def find_download_links(driver):
    wait_for_page(driver)

    anchors = []
    try:
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul#currentAttempt_submissionList.filesList"))
        )
        anchors = driver.find_elements(
            By.CSS_SELECTOR,
            "ul#currentAttempt_submissionList.filesList li div.downloadFile a.dwnldBtn[href*='/webapps/assignment/download']"
        )
    except TimeoutException:
        anchors = []

    if not anchors:
        anchors = driver.find_elements(
            By.CSS_SELECTOR,
            "div.downloadFile a.dwnldBtn[href*='/webapps/assignment/download']"
        )

    links = []
    for el in anchors:
        href = el.get_attribute("href") or ""
        file_basename = None
        if href:
            try:
                qs = parse_qs(urlparse(href).query)
                vals = qs.get("fileName")
                if vals and vals[0]:
                    file_basename = vals[0]
            except Exception:
                pass
        links.append((el, href, file_basename))

    if not links:
        raise TimeoutException("No downloadable files found for this attempt.")

    return links
