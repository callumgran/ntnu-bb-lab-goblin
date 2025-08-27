import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from config.settings import WAIT
from downloader.selenium_utils import wait_for_page, url_contains_any

def ensure_logged_in(driver):
    wait_for_page(driver)

    try:
        login_btn = driver.find_element(By.CSS_SELECTOR, "a.loginPrimary")
        login_btn.click()
        time.sleep(0.5)
    except NoSuchElementException:
        pass

    try:
        if "login.microsoftonline.com" in driver.current_url or "microsoft.com" in driver.current_url:
            print("👉 Continue with Microsoft login if prompted… (waiting for redirect back)")
            url_contains_any(
                driver,
                ["ntnu.blackboard.com/ultra/courses", "ntnu.blackboard.com/learn"],
                timeout=180,
            )
    except TimeoutException:
        raise RuntimeError("Microsoft login did not complete in time.")

    try:
        WebDriverWait(driver, WAIT * 3).until(EC.url_contains("/cl/outline"))
    except TimeoutException:
        WebDriverWait(driver, WAIT).until(lambda d: "ntnu.blackboard.com" in d.current_url)
    wait_for_page(driver)


def go_next_submission(driver):
    wait_for_page(driver)

    try:
        before_txt = driver.find_element(
            By.CSS_SELECTOR, "div.students-pager h3"
        ).text.strip()
    except Exception:
        before_txt = None

    locators = [
        (By.CSS_SELECTOR, "div.pager.next a[onclick*='viewNext']"),
        (By.XPATH, "//div[contains(@class,'pager') and contains(@class,'next')]//a[contains(@onclick,'viewNext')]"),
    ]

    for loc in locators:
        try:
            a = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located(loc))
            try:
                container = a.find_element(By.XPATH, "./ancestor::div[contains(@class,'pager')][1]")
                if "disabled" in (container.get_attribute("class") or ""):
                    return False
            except Exception:
                pass

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", a)
            try:
                a.click()
            except Exception:
                driver.execute_script("arguments[0].click();", a)

            try:
                WebDriverWait(driver, WAIT * 3).until(
                    lambda d: (
                        (before_txt is not None and
                         d.find_element(By.CSS_SELECTOR, "div.students-pager h3").text.strip() != before_txt)
                        or "currentAttemptIndex=" in d.current_url
                        or "attempt_id=" in d.current_url
                    )
                )
            except TimeoutException:
                pass

            wait_for_page(driver)
            return True
        except TimeoutException:
            continue

    try:
        has_controller = driver.execute_script(
            "return (typeof theAttemptNavController !== 'undefined') && "
            "theAttemptNavController && typeof theAttemptNavController.viewNext === 'function';"
        )
        if has_controller:
            driver.execute_script("return theAttemptNavController.viewNext();")
            try:
                WebDriverWait(driver, WAIT * 3).until(
                    lambda d: (
                        (before_txt is not None and
                         d.find_element(By.CSS_SELECTOR, "div.students-pager h3").text.strip() != before_txt)
                        or "currentAttemptIndex=" in d.current_url
                        or "attempt_id=" in d.current_url
                    )
                )
            except TimeoutException:
                pass
            wait_for_page(driver)
            return True
    except Exception:
        pass

    legacy_locators = [
        (By.XPATH, "//button[@aria-label='Next' or @title='Next' or contains(.,'Next')]"),
        (By.XPATH, "//button[@aria-label='Neste' or @title='Neste' or contains(.,'Neste')]"),
        (By.XPATH, "//*[contains(@class,'chevron') and (contains(@aria-label,'Next') or contains(@aria-label,'Neste'))]"),
    ]
    for loc in legacy_locators:
        try:
            el = driver.find_element(*loc)
            disabled = (el.get_attribute("disabled") or el.get_attribute("aria-disabled"))
            if disabled and str(disabled).lower() in ("true", "disabled"):
                return False
            el.click()
            wait_for_page(driver)
            return True
        except Exception:
            continue

    return False


def open_vurdering(driver):
	wait_for_page(driver)

	needs_grading_url = "https://ntnu.blackboard.com/webapps/gradebook/do/instructor/viewNeedsGrading?course_id=_52568_1"
	current = driver.current_url
	if "viewNeedsGrading" not in current:
		driver.get(needs_grading_url)
		try:
			WebDriverWait(driver, WAIT * 2).until(
				lambda d: "viewNeedsGrading" in d.current_url or
						  d.find_elements(By.CSS_SELECTOR, "iframe.classic-learn-iframe, iframe[src*='/webapps/']")
			)
		except TimeoutException:
			pass

	if "viewNeedsGrading" in driver.current_url:
		wait_for_page(driver)
		return True


def open_first_submission(driver):
    wait_for_page(driver)
    locator = (By.CSS_SELECTOR, "tbody#listContainer_databody a.gradeAttempt[aria-label^='Vurder forsøk for']")
    try:
        el = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable(locator))
        aria = el.get_attribute("aria-label") or "Vurder forsøk"
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        el.click()
        print(f"✅ Opened first submission: {aria}")

        WebDriverWait(driver, WAIT * 3).until(
            lambda d: any(s in d.current_url for s in ("gradeAssignment", "attempt_id", "assignment/grade"))
        )
        wait_for_page(driver)
        return True
    except TimeoutException:
        raise RuntimeError("Could not find any submission link (a.gradeAttempt).")
