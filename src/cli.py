import argparse

from downloader.driver import DriverManager
from downloader.navigation import ensure_logged_in, open_vurdering, open_first_submission, go_next_submission
from downloader.submission import download_current_submission
from config.settings import FIREFOX_PROFILE, DOWNLOAD_DIR, COURSE_ID
from downloader.page_parser import get_total_items_from_header

def main():
    parser = argparse.ArgumentParser(description="NTNU Blackboard Downloader CLI")
    parser.add_argument('--course-id', type=str, default=COURSE_ID, help='NTNU Blackboard course ID (e.g., _52568_1), required!')
    parser.add_argument('--download-dir', type=str, default=DOWNLOAD_DIR, help='Directory to save downloaded files, default is ./bb_downloads')
    parser.add_argument('--profile', type=str, default=FIREFOX_PROFILE, help='Firefox profile path, default is ~/.mozilla/firefox/selenium-profile. See README for setup instructions.')
    parser.add_argument('--lab-num', type=int, help='Optional to only download submissions for a specific lab number (e.g., 1, 2, 3, ...)')
    parser.add_argument('--headless', type=bool, default=True, help='Run browser in headless mode (no GUI), default is True')
    args = parser.parse_args()

    course_url = f"https://ntnu.blackboard.com/ultra/courses/{args.course_id}/cl/outline"

    driver_manager = DriverManager(args.profile, args.download_dir, args.headless)
    driver = driver_manager.build_driver()

    try:
        driver.get(course_url)
        ensure_logged_in(driver)
        open_vurdering(driver, args.course_id)

        total = get_total_items_from_header(driver)
        if total is not None:
            print(f"📝 Needs grading: {total} element(er).")
        else:
            print("📝 Couldn’t read the total count from the header.")

        open_first_submission(driver)

        count = 0
        while count < (total if total is not None else 9999):
            count += 1
            print(f"\n=== Submission {count} ===")
            if download_current_submission(driver, selected_lab=args.lab_num):
                pass

            if not go_next_submission(driver):
                print("Reached last submission ✅")
                break

        print(f"\nDone! Files are in: {args.download_dir}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver_manager.quit_driver()

if __name__ == "__main__":
    main()