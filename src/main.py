def main():
    import argparse
    from downloader.driver import DriverManager
    from downloader.navigation import ensure_logged_in, open_vurdering, go_next_submission, open_first_submission
    from downloader.submission import download_current_submission
    from downloader.page_parser import get_total_items_from_header
    from config.settings import COURSE_OUTLINE_URL, DOWNLOAD_DIR, FIREFOX_PROFILE

    parser = argparse.ArgumentParser(description="Blackboard Downloader CLI")
    parser.add_argument('--course-url', type=str, default=COURSE_OUTLINE_URL, help='URL of the course outline')
    parser.add_argument('--download-dir', type=str, default=DOWNLOAD_DIR, help='Directory to save downloaded files')
    parser.add_argument('--profile', type=str, default=FIREFOX_PROFILE, help='Firefox profile path')
    args = parser.parse_args()

    driver_manager = DriverManager(args.profile, args.download_dir)
    driver = driver_manager.build_driver()
    
    try:
        driver.get(args.course_url)
        ensure_logged_in(driver)
        open_vurdering(driver)

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
            if download_current_submission(driver):
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