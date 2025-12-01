from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class AuthTestSetup:
    def __init__(self):
        self.driver_path = "./chromedriver-linux64/chromedriver"
        self.chrome_options = Options()
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--start-maximized")
        self.service = Service(executable_path=self.driver_path)

    def create_driver(self):
        return webdriver.Chrome(service=self.service, options=self.chrome_options)

class AuthTestUtils:
    @staticmethod
    def login(driver, username, password):
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)

    @staticmethod
    def navigate_to_user_management(driver):
        driver.find_element(By.CSS_SELECTOR, '[data-test-id="nav-button-security-and-access"]').click()
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, '[data-test-id="nav-item-user-management"]').click()
        time.sleep(3)

def test_successful_auth():
    setup = AuthTestSetup()
    driver = setup.create_driver()
    
    try:
        driver.get("https://localhost:2443")
        AuthTestUtils.login(driver, "root", "0penBmc")
        assert "login" not in driver.current_url.lower()
    finally:
        driver.quit()

def test_failed_auth():
    setup = AuthTestSetup()
    driver = setup.create_driver()
    
    try:
        driver.get("https://localhost:2443")
        AuthTestUtils.login(driver, "wrong_user", "wrong_password")
        assert "login" in driver.current_url.lower()
    finally:
        driver.quit()

def test_block_user():
    setup = AuthTestSetup()
    driver = setup.create_driver()
    
    try:
        driver.get("https://localhost:2443")
        time.sleep(3)

        for _ in range(3):
            AuthTestUtils.login(driver, "igor", "abcdefg")
        
        AuthTestUtils.login(driver, "root", "0penBmc")
        AuthTestUtils.navigate_to_user_management(driver)
        
        page_html = driver.page_source
        assert "igor" in page_html and "locked" in page_html.lower()
    
    finally:
        driver.quit()