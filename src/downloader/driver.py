import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager


class DriverManager:
    def __init__(self, profile_path: str, download_dir: str, headless: bool = True):
        self.profile_path = profile_path
        self.download_dir = download_dir
        self.driver = None
        self._setup_download_directory()
        self.headless = headless

    def _setup_download_directory(self):
        os.makedirs(self.download_dir, exist_ok=True)

    def build_driver(self):
        opts = webdriver.FirefoxOptions()
        opts.add_argument("-profile")
        opts.add_argument(self.profile_path)
        if self.headless:
            opts.add_argument("-headless")
            opts.set_preference("gfx.webrender.all", True)
            opts.set_preference("webgl.disabled", False)

        mime_list = ",".join(
            [
                "application/octet-stream",
                "application/zip",
                "application/x-zip-compressed",
                "application/pdf",
                "text/plain",
                "text/csv",
                "text/x-csrc",
                "text/x-c",
                "text/x-c++src",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/x-tar",
                "application/gzip",
                "application/x-7z-compressed",
                "application/x-rar-compressed",
            ]
        )

        opts.set_preference("browser.download.folderList", 2)
        opts.set_preference("browser.download.dir", self.download_dir)
        opts.set_preference("browser.download.useDownloadDir", True)
        opts.set_preference("browser.helperApps.neverAsk.saveToDisk", mime_list)
        opts.set_preference("pdfjs.disabled", True)
        opts.set_preference("browser.download.manager.showWhenStarting", False)
        opts.set_preference("browser.download.alwaysOpenPanel", False)
        opts.set_capability("unhandledPromptBehavior", "accept")

        self.driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=opts,
        )
        return self.driver

    def quit_driver(self):
        if self.driver:
            self.driver.quit()
