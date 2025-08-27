from pathlib import Path
from urllib.parse import urlparse
import os
import tempfile

import requests
from selenium.common.exceptions import TimeoutException, WebDriverException

from config.settings import DOWNLOAD_DIR
from downloader.page_parser import get_student_name, get_lab_number, find_download_link
from downloader.file_utils import (
    on_downloads_complete,
    sanitize_filename,
    split_extension,
)


def _requests_download(url: str, dst_path: Path, driver=None, timeout=180) -> bool:
    def _do(session: requests.Session) -> requests.Response:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
        }
        return session.get(
            url,
            headers=headers,
            stream=True,
            timeout=timeout,
            allow_redirects=True,
        )

    s = requests.Session()
    r = _do(s)

    if r.status_code in (401, 403) and driver is not None:
        s = requests.Session()
        try:
            for c in driver.get_cookies():
                s.cookies.set(
                    c.get("name"),
                    c.get("value"),
                    domain=c.get("domain"),
                    path=c.get("path") or "/",
                )
        except Exception:
            pass
        r = _do(s)

    r.raise_for_status()

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=str(dst_path.parent), delete=False) as tmp:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                tmp.write(chunk)
        tmp_path = Path(tmp.name)

    os.replace(tmp_path, dst_path)
    return True


def download_current_submission(driver, selected_lab=None):
    """
    Returns dict:
      {
        "success": bool,
        "skipped": bool,
        "student": str | None,
        "lab": int | None,
        "filename": str | None,
        "error": str | None,
      }
    """
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
        _requests_download(href, dst_path, driver=driver, timeout=180)
        result["success"] = True
        result["filename"] = dst_path.name
        return result
    except requests.HTTPError as e:
        result["error"] = f"HTTP error while downloading: {e}"
    except Exception as e:
        result["error"] = f"Requests download failed: {e}"

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        try:
            el.click()
        except WebDriverException:
            driver.execute_script("window.open(arguments[0], '_blank');", href)

        on_downloads_complete(DOWNLOAD_DIR, idle_seconds=2)

        files = list(Path(DOWNLOAD_DIR).glob("*"))
        if files:
            newest = max(files, key=lambda f: f.stat().st_mtime)
            try:
                os.replace(newest, dst_path)
                result["success"] = True
                result["filename"] = dst_path.name
                result["error"] = None
                return result
            except Exception as e:
                result["error"] = f"Could not rename file after browser download: {e}"
        else:
            result["error"] = "Browser download seems to have failed (no new file)."

    except Exception as e:
        result["error"] = f"Browser click/open failed: {e}"

    return result
