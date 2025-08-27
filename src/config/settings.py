from pathlib import Path

COURSE_OUTLINE_URL = "https://ntnu.blackboard.com/ultra/courses/_52568_1/cl/outline"
DOWNLOAD_DIR = str(Path.cwd() / "bb_downloads")
FIREFOX_PROFILE = str(Path.home() / ".mozilla/firefox/selenium-profile") # See the README for how to set up a Firefox profile for Selenium
WAIT = 10  # seconds