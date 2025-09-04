from pathlib import Path
from urllib.parse import urlparse
import os
import time

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from config.settings import DOWNLOAD_DIR
from downloader.page_parser import get_student_name, get_lab_number, find_download_links
from downloader.file_utils import (
    on_downloads_complete,
    sanitize_filename,
    split_extension,
)


def _is_firefox_neterror(driver):
    try:
        return bool(driver.execute_script(
            "return !!(document && document.body && "
            "document.body.classList && document.body.classList.contains('neterror'));"
        ))
    except Exception:
        return False

def _refind_download_element(driver, href, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul#currentAttempt_submissionList"))
        )
    except Exception:
        pass
    els = driver.find_elements(By.CSS_SELECTOR, "ul#currentAttempt_submissionList a.dwnldBtn")
    for e in els:
        if (e.get_attribute("href") or "") == href:
            return e
    els = driver.find_elements(By.CSS_SELECTOR, "div.downloadFile a.dwnldBtn")
    for e in els:
        if (e.get_attribute("href") or "") == href:
            return e
    return None


def _browser_download_with_retries(driver, el, href, dst_path, retries: int = 2):
    try:
        driver.execute_script("arguments[0].setAttribute('download', arguments[1]);", el, dst_path.name)
    except Exception:
        pass
    attempt = 0
    while attempt <= retries:
        attempt += 1
        before_handles = set(driver.window_handles)
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        except Exception:
            el = _refind_download_element(driver, href)
            if el is None:
                time.sleep(1.0)
                el = _refind_download_element(driver, href)
                if el is None:
                    continue

        try:
            driver.execute_script("arguments[0].target = '_blank'; arguments[0].click();", el)
        except WebDriverException:
            driver.execute_script("window.open(arguments[0], '_blank');", href)
        new_handles = set()
        for _ in range(30):
            current_handles = set(driver.window_handles)
            new_handles = current_handles - before_handles
            if new_handles:
                break
            time.sleep(0.1)
        if not new_handles:
            if _is_firefox_neterror(driver):
                try:
                    driver.back()
                except Exception:
                    pass
                for _ in range(50):
                    try:
                        if driver.execute_script("return document.readyState") == "complete":
                            break
                    except Exception:
                        pass
                    time.sleep(0.2)
                time.sleep(1.0)
                el = _refind_download_element(driver, href)
                continue
            on_downloads_complete(DOWNLOAD_DIR, idle_seconds=2)
            return True
        new_handle = list(new_handles)[0]
        driver.switch_to.window(new_handle)
        if _is_firefox_neterror(driver):
            try:
                driver.back()
            except Exception:
                pass
            try:
                driver.close()
            finally:
                remaining = list(before_handles)
                if remaining:
                    driver.switch_to.window(remaining[0])
            for _ in range(50):
                try:
                    if driver.execute_script("return document.readyState") == "complete":
                        break
                except Exception:
                    pass
                time.sleep(0.2)
            time.sleep(1.0)
            el = _refind_download_element(driver, href)
            continue
        on_downloads_complete(DOWNLOAD_DIR, idle_seconds=2)
        try:
            driver.close()
        finally:
            remaining = list(before_handles)
            if remaining:
                driver.switch_to.window(remaining[0])
        return True
    return False


def download_current_submission(driver, selected_lab=None):
    result = {
        "success": False,
        "skipped": False,
        "student": None,
        "lab": None,
        "filenames": [],
        "error": None,
    }
    student = get_student_name(driver)
    lab_num = get_lab_number(driver)
    result.update({"student": student, "lab": lab_num})
    if (selected_lab is not None) and (lab_num != selected_lab):
        result["skipped"] = True
        return result
    try:
        links = find_download_links(driver)
    except TimeoutException:
        result["error"] = "No downloadable files found on this page."
        return result
    safe_student = sanitize_filename(student)
    lab_suffix = f"_oving{lab_num}" if lab_num is not None else ""
    downloaded_any = False
    for (el, href, orig_file) in links:
        if not orig_file:
            path_part = urlparse(href).path
            orig_file = Path(path_part).name or "submission"
        stem, ext = split_extension(orig_file)
        if not ext:
            ext = ".txt"
        safe_stem = sanitize_filename(stem)
        new_name = f"{safe_student}{lab_suffix}_{safe_stem}{ext}"
        dst_path = Path(DOWNLOAD_DIR) / new_name
        if dst_path.exists():
            base, ext2 = dst_path.stem, dst_path.suffix
            n = 2
            while True:
                candidate = dst_path.with_name(f"{base}_{n}{ext2}")
                if not candidate.exists():
                    dst_path = candidate
                    break
                n += 1
        ok = _browser_download_with_retries(driver, el, href, dst_path, retries=2)
        if not ok:
            if result["error"] is None:
                result["error"] = "Browser download failed after retries (network protocol error)."
            continue
        files = list(Path(DOWNLOAD_DIR).glob("*"))
        if files:
            newest = max(files, key=lambda f: f.stat().st_mtime)
            if newest != dst_path:
                try:
                    os.replace(newest, dst_path)
                except Exception as e:
                    if result["error"] is None:
                        result["error"] = f"Could not rename downloaded file: {e}"
                    continue
        downloaded_any = True
        result["filenames"].append(dst_path.name)
        on_downloads_complete(DOWNLOAD_DIR, idle_seconds=1)
    result["success"] = downloaded_any
    if downloaded_any:
        result["error"] = None
    return result
