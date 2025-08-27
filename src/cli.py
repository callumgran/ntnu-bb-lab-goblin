import argparse

from src.downloader.driver import build_driver
from src.downloader.navigation import ensure_logged_in, open_vurdering, open_first_submission, go_next_submission
from src.downloader.submission import download_current_submission
from src.config.settings import COURSE_OUTLINE_URL, DOWNLOAD_DIR
from src.downloader.page_parser import get_total_items_from_header

def main():
    parser = argparse.ArgumentParser(description="Blackboard Downloader CLI")
    parser.add_argument(
        '--download', 
        action='store_true', 
        help='Download submissions from the specified course outline.'
    )
    
    args = parser.parse_args()

    if args.download:
        driver = build_driver()
        try:
            driver.get(COURSE_OUTLINE_URL)
            ensure_logged_in(driver)
            open_vurdering(driver)

            total = get_total_items_from_header(driver)
            if total is not None:
                print(f"📝 Needs grading: {total} element(er).")
            else:
                print("📝 Couldn’t read the total count from the header.")

            open_first_submission(driver)

            count = 0
            while True:
                count += 1
                print(f"\n=== Submission {count} ===")
                if download_current_submission(driver):
                    pass

                if not go_next_submission(driver):
                    print("Reached last submission ✅")
                    break

            print(f"\nDone! Files are in: {DOWNLOAD_DIR}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.quit()

if __name__ == "__main__":
    main()