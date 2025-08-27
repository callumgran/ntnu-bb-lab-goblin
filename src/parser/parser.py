import argparse
from config.settings import COURSE_ID, DOWNLOAD_DIR, FIREFOX_PROFILE


def build_parser():
    parser = argparse.ArgumentParser(
        prog="bb-downloader",
        description="🧌 NTNU BB LAB Goblin — fetch & rename submissions automatically 📥",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    general = parser.add_argument_group("General options")
    general.add_argument(
        "--course-id",
        type=str,
        default=COURSE_ID,
        metavar="_52568_1",
        help="Blackboard course ID (e.g., _52568_1). Overrides config.settings.COURSE_ID",
    )
    general.add_argument(
        "--download-dir",
        type=str,
        default=DOWNLOAD_DIR,
        metavar="/path/to/dir",
        help="Directory where files are saved",
    )
    general.add_argument(
        "--profile",
        type=str,
        default=FIREFOX_PROFILE,
        metavar="/path/to/profile",
        help="Firefox profile to reuse (keep NTNU cookies)",
    )
    general.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no GUI)",
    )

    filters = parser.add_argument_group("Filters")
    filters.add_argument(
        "--lab-num",
        type=int,
        metavar="1",
        help="Only download submissions for a specific lab number (e.g., 1, 2, 3). Default: all",
    )

    return parser
