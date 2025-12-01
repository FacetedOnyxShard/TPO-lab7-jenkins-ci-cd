from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def test_successful_auth():
    driver_path = "./chromedriver-linux64/chromedriver"

    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--start-maximized")

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("https://localhost:2443")
        
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password") 
        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        
        username.send_keys("root")
        password.send_keys("0penBmc")
        login_btn.click()
        
        time.sleep(5)
        
        assert "login" not in driver.current_url.lower()
        
    finally:
        driver.quit()

def test_failed_auth():
    driver_path = "./chromedriver-linux64/chromedriver"

    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--start-maximized")

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get("https://localhost:2443")
        
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password") 
        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        
        username.send_keys("wrong_user")
        password.send_keys("wrong_password")
        login_btn.click()
        
        time.sleep(5)
        
        assert "login" in driver.current_url.lower()
        
    finally:
        driver.quit()

def test_block_user():
    driver_path = "./chromedriver-linux64/chromedriver"

    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--start-maximized")

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://localhost:2443")
        time.sleep(3)

        for i in range(3):
            username = driver.find_element(By.ID, "username")
            password = driver.find_element(By.ID, "password") 
            login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")

            username.send_keys("igor")
            password.send_keys("abcdefg")
            login_btn.click()

            time.sleep(3)
        
        username = driver.find_element(By.ID, "username")
        password = driver.find_element(By.ID, "password") 
        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")

        username.send_keys("root")
        password.send_keys("0penBmc")
        login_btn.click()

        time.sleep(5)

        secur_and_acs = driver.find_element(By.CSS_SELECTOR, '[data-test-id="nav-button-security-and-access"]')
        secur_and_acs.click()

        time.sleep(5)

        user_mgmt = driver.find_element(By.CSS_SELECTOR, '[data-test-id="nav-item-user-management"]')
        user_mgmt.click()

        time.sleep(5)

        page_html = driver.page_source
        assert "igor" in page_html and "locked" in page_html.lower()
    
    finally:
        driver.quit()