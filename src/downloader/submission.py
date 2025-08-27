from pathlib import Path
from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException

from config.settings import DOWNLOAD_DIR
from downloader.page_parser import get_student_name, get_lab_number, find_download_link
from downloader.file_utils import (
    on_downloads_complete,
    sanitize_filename,
    split_extension,
)


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
    src_path = Path(DOWNLOAD_DIR) / orig_file
    dst_path = Path(DOWNLOAD_DIR) / new_name

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    el.click()
    on_downloads_complete(DOWNLOAD_DIR, idle_seconds=2)

    if not src_path.exists():
        files = list(Path(DOWNLOAD_DIR).glob("*"))
        if files:
            src_path = max(files, key=lambda f: f.stat().st_mtime)

    try:
        if src_path.exists():
            if dst_path.exists():
                base = dst_path.stem
                ext2 = dst_path.suffix
                n = 2
                while True:
                    candidate = dst_path.with_name(f"{base}_{n}{ext2}")
                    if not candidate.exists():
                        dst_path = candidate
                        break
                    n += 1
            src_path.rename(dst_path)
            result["success"] = True
            result["filename"] = dst_path.name
            return result
        else:
            result["error"] = "Download finished but file not found to rename."
            return result
    except Exception as e:
        result["error"] = f"Could not rename file: {e}"
        return result
