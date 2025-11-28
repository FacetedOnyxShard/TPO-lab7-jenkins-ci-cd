import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

class TestWebUI:
  OPENBMC_URL = "https://localhost:2443"
  F_USERNAME = os.getenv('F_USERNAME')
  F_PASSWORD = os.getenv('F_PASSWORD')
  S_USERNAME = os.getenv('S_USERNAME')
  S_PASSWORD = os.getenv('S_PASSWORD')

  def setup_method(self):
    self.service = Service('/usr/bin/chromedriver')
    self.driver = webdriver.Chrome(service=self.service)
    self.wait = WebDriverWait(self.driver, 30)
    self.driver.get(self.OPENBMC_URL)
    try:
      self.driver.find_element(By.ID, "details-button").click()
      self.driver.find_element(By.ID, "proceed-link").click()
    except:
      pass

  def teardown_method(self):
    self.driver.delete_all_cookies()
    self.driver.quit()

  def login_root(self):
    self.login(self.F_USERNAME, self.F_PASSWORD)

  def login(self, username, password):
    username_field = self.wait.until(
      EC.presence_of_element_located((By.ID, "username"))
    )
    password_field = self.driver.find_element(By.ID, "password")
    login_button = self.driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary")

    username_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

  def incorrect_login(self):
    self.login(self.S_USERNAME, self.F_PASSWORD)

  def login_unsuccess_assert(self, username_field):
    assert username_field.get_attribute("value") == ""

  def reload_condition_auth_page(self):
    WebDriverWait(self.driver, 10).until(
      lambda d: d.find_element(By.ID, "username").get_attribute("value") == ""
    )

  def success_auth_assert(self, expected, username_label):
    self.driver.find_element(By.ID, "app-header-user__BV_toggle_").click()
    self.driver.find_element(By.CSS_SELECTOR, '[data-test-id="appHeader-link-logout"]').click()
    assert expected in username_label.text
    self.reload_condition_auth_page()

  def test_success_auth_root(self):
    """ Тест успешной авторизации """
    self.login(self.F_USERNAME, self.F_PASSWORD)

    parent_for_username = self.wait.until(
      EC.presence_of_element_located((By.ID, "app-header-user"))
    )
    username_after_login = parent_for_username.find_element(By.CLASS_NAME, "responsive-text")

    self.success_auth_assert(self.F_USERNAME, username_after_login)

  def test_success_auth_neroot(self):
    self.login(self.S_USERNAME, self.S_PASSWORD)

    parent_for_username = self.wait.until(
      EC.presence_of_element_located((By.ID, "app-header-user"))
    )
    username_after_login = parent_for_username.find_element(By.CLASS_NAME, "responsive-text")

    self.success_auth_assert(self.S_USERNAME, username_after_login)
  
  def test_unsuccess_auth_root(self):
    """ Тест неуспешной авторизации """
    self.incorrect_login()

    self.reload_condition_auth_page()
    username_field = self.driver.find_element(By.ID, "username")

    self.login_unsuccess_assert(username_field)

  def test_blocking(self):
    for _ in range(3):
      self.incorrect_login()

      self.reload_condition_auth_page()

    self.reload_condition_auth_page()
    username_field = self.driver.find_element(By.ID, "username")

    self.login_unsuccess_assert(username_field)
    
    self.login(self.S_USERNAME, self.S_PASSWORD)
    
    self.reload_condition_auth_page()
    username_field = self.driver.find_element(By.ID, "username")
    
    self.login_unsuccess_assert(username_field)

  def test_poweron_server(self):
    self.login_root()

    power_btn = self.wait.until(
      EC.presence_of_element_located((By.XPATH, "//a[@href='#/operations/server-power-operations']"))
    )

    power_btn.click()

    power_on_btn = self.wait.until(
      EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test-id="serverPowerOperations-button-powerOn"]'))
    )

    power_on_btn.click()

    alert_msg = self.driver.find_element(By.CLASS_NAME, "alert-msg")

    assert "There are no options to display while a power operation is in progress. When complete, power operations will be displayed here." in alert_msg.text

  def test_openlogs(self):
    result = subprocess.run(
        f'sshpass -p "{self.F_PASSWORD}" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
        root@localhost -p 2222 "journalctl -u bmcweb --no-pager -n 3"', 
        shell=True, 
        capture_output=True, 
        text=True
    )
    assert result.stdout != "" and result.stdout is not None