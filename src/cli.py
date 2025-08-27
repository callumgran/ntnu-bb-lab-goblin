from tqdm import tqdm

from downloader.driver import DriverManager
from downloader.navigation import (
    ensure_logged_in,
    open_vurdering,
    open_first_submission,
    go_next_submission,
)
from downloader.submission import download_current_submission
from downloader.page_parser import get_total_items_from_header
from parser.parser import build_parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    course_url = (
        f"https://ntnu.blackboard.com/ultra/courses/{args.course_id}/cl/outline"
    )

    driver_manager = DriverManager(args.profile, args.download_dir, args.headless)
    driver = driver_manager.build_driver()

    try:
        driver.get(course_url)
        ensure_logged_in(driver)
        open_vurdering(driver, args.course_id)

        total = get_total_items_from_header(driver)
        if total is not None:
            print(f"📝 Needs grading: {total} element(s).")
        else:
            print(
                "📝 Couldn’t read the total count from the header (progress will be unbounded)."
            )

        open_first_submission(driver)

        if total and total > 0:
            pbar = tqdm(total=total, unit="sub", desc="Downloading", ncols=100)
            remaining_limit = total
        else:
            pbar = tqdm(unit="sub", desc="Downloading", ncols=100)
            remaining_limit = 10_000

        processed = 0
        while processed < remaining_limit:
            pbar.set_description(f"Submission {processed + 1}")
            info = download_current_submission(driver, selected_lab=args.lab_num)

            if info["skipped"]:
                pbar.write(
                    f"⏭️  Skipped {info['student']} (lab {info['lab']}, looking for {args.lab_num})"
                )
            elif info["success"]:
                pbar.set_postfix({"student": info["student"], "lab": info["lab"]})
                pbar.write(
                    f"👤 {info['student']} | 📘 Lab {info['lab']} | ⬇️ {info['filename']}"
                )
            else:
                msg = info["error"] or "unknown error"
                pbar.write(f"⚠️  {info['student']} | Lab {info['lab']}: {msg}")

            processed += 1
            pbar.update(1)

            if not go_next_submission(driver):
                break

        pbar.close()
        print(f"\nDone! Files are in: {args.download_dir}")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        driver_manager.quit_driver()


if __name__ == "__main__":
    main()
