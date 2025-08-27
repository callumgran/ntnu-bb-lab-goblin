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

    locator = By.CSS_SELECTOR, "div.pager.next a[onclick*='viewNext']"

    try:
        a = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located(locator))
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
        return False


def open_vurdering(driver, course_id):
	wait_for_page(driver)

	needs_grading_url = f"https://ntnu.blackboard.com/webapps/gradebook/do/instructor/viewNeedsGrading?course_id={course_id}"
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
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        el.click()

        WebDriverWait(driver, WAIT * 3).until(
            lambda d: any(s in d.current_url for s in ("gradeAssignment", "attempt_id", "assignment/grade"))
        )
        wait_for_page(driver)
        return True
    except TimeoutException:
        raise RuntimeError("Could not find any submission link (a.gradeAttempt).")
