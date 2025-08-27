from pathlib import Path
from urllib.parse import urlparse
import os
import time

from selenium.common.exceptions import TimeoutException, WebDriverException

from config.settings import DOWNLOAD_DIR
from downloader.page_parser import get_student_name, get_lab_number, find_download_link
from downloader.file_utils import (
    on_downloads_complete,
    sanitize_filename,
    split_extension,
)


def _browser_download_with_retries(driver, el, href, dst_path: Path, retries: int = 2) -> bool:
    try:
        driver.execute_script("arguments[0].setAttribute('download', arguments[1]);", el, dst_path.name)
    except Exception:
        pass

    attempt = 0
    while attempt <= retries:
        attempt += 1

        before_handles = set(driver.window_handles)

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        try:
            driver.execute_script("arguments[0].target = '_blank'; arguments[0].click();", el)
        except WebDriverException:
            driver.execute_script("window.open(arguments[0], '_blank');", href)

        new_handles = set()
        for _ in range(20):
            current_handles = set(driver.window_handles)
            new_handles = current_handles - before_handles
            if new_handles:
                break
            time.sleep(0.1)

        if new_handles:
            new_handle = list(new_handles)[0]
            driver.switch_to.window(new_handle)

            new_url = driver.current_url or ""
            if new_url.startswith("about:neterror"):
                try:
                    driver.close()
                finally:
                    rest = list(before_handles)
                    if rest:
                        driver.switch_to.window(rest[0])
                time.sleep(2.0)
                continue

            on_downloads_complete(DOWNLOAD_DIR, idle_seconds=2)
            try:
                driver.close()
            finally:
                rest = list(before_handles)
                if rest:
                    driver.switch_to.window(rest[0])
            return True

        else:
            new_url = driver.current_url or ""
            if new_url.startswith("about:neterror"):
                try:
                    driver.back()
                except Exception:
                    pass
                time.sleep(2.0)
                continue

            on_downloads_complete(DOWNLOAD_DIR, idle_seconds=2)
            return True

    return False


def download_current_submission(driver, selected_lab=None):
    result = {
        "success": False,
        "skipped": False,
        "student": None,
        "lab": None,
        "filename": None,
        "error": None,
    }

    student = get_student_name(driver)
    lab_num = get_lab_number(driver)
    result.update({"student": student, "lab": lab_num})

    if (selected_lab is not None) and (lab_num != selected_lab):
        result["skipped"] = True
        return result

    try:
        el, href, orig_file = find_download_link(driver)
    except TimeoutException:
        result["error"] = "No download button found on this page."
        return result

    if not orig_file:
        path_part = urlparse(href).path
        orig_file = Path(path_part).name or "submission"

    _, ext = split_extension(orig_file)
    if not ext:
        ext = ".txt"

    safe_student = sanitize_filename(student)
    lab_suffix = f"_oving{lab_num}" if lab_num is not None else ""
    new_name = f"{safe_student}{lab_suffix}{ext}"
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

    try:
        ok = _browser_download_with_retries(driver, el, href, dst_path, retries=2)
        if not ok:
            result["error"] = "Browser download failed after retries (network error)."
            return result

        files = list(Path(DOWNLOAD_DIR).glob("*"))
        if files:
            newest = max(files, key=lambda f: f.stat().st_mtime)
            if newest != dst_path:
                try:
                    os.replace(newest, dst_path)
                except Exception as e:
                    result["error"] = f"Could not rename file after browser download: {e}"
                    return result

        result["success"] = True
        result["filename"] = dst_path.name
        result["error"] = None
        return result

    except Exception as e:
        result["error"] = f"Browser click/open failed: {e}"
        return result
