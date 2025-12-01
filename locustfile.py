from locust import HttpUser, task, between
<<<<<<< HEAD
import json

class OpenBmcTestUser(HttpUser):
  wait_time = between(1, 3)
  host = "https://localhost:2443"

  def __init__(self, enviroment):
    super().__init__(enviroment)
    self.auth = ("root", "0penBmc")

  @task(3)
  def get_system_info(self):
    with self.client.get("/redfish/v1/Systems/system", 
    auth=self.auth, verify=False, catch_response=True, 
    name="Get system info") as response:
      if response.status_code == 200:
        try:
          data = response.json()
          response.success()
        except ValueError:
          response.failure("Invalid json response")
      else:
        response.failure(f"Status code: {response.status_code}")

  @task(2)
  def get_power_state(self):
    with self.client.get("/redfish/v1/Systems/system", 
    auth=self.auth, verify=False, catch_response=True, 
    name="Get power state") as response:
      if response.status_code == 200:
        try:
          data = response.json()
          power_state = data.get("PowerState", "Unknown")
          response.success()
        except ValueError:
          response.failure("Invalid json response")
      else:
        response.failure(f"Status code: {response.status_code}")

class PublicAPITestUser(HttpUser):
  wait_time = between(1, 5)
  host = ""

  @task(4)
  def get_posts(self):
    with self.client.get("https://jsonplaceholder.typicode.com/posts",
    catch_response=True, name="Get posts lists") as response:
      if response.status_code == 200:
        try:
          data = response.json()
          if len(data) > 0:
            response.success()
          else:
            response.failure("Empty data")
        except ValueError:
          response.failure("Invalid json response")
      else:
        response.failure(f"Status code: {response.status_code}")

  @task(3)
  def get_weather(self):
    with self.client.get("https://wttr.in/Novosibirsk?format=j1",
    catch_response=True, name="Get weather data") as response:
      if response.status_code == 200:
        try:
          if response.text > 0:
            response.success()
          else:
            response.failure("Empty response")
        except ValueError:
          response.failure("Invalid json response")
      else:
        response.failure(f"Status code: {response.status_code}")

  
=======
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RedfishUser(HttpUser):
    """Пользователь для нагрузочного тестирования Redfish API"""
    
    host = "https://localhost:2443"
    wait_time = between(1, 3)
    
    def on_start(self):
        """Инициализация пользователя при начале теста"""
        self.credentials = ("root", "0penBmc")
    
    @task
    def fetch_system_information(self):
        """Получение общей информации о системе"""
        self.client.get(
            "/redfish/v1/Systems/system",
            auth=self.credentials,
            verify=False,
            name="01_System_Information"
        )
    
    @task
    def verify_power_state(self):
        """Проверка текущего состояния питания системы"""
        with self.client.get(
            "/redfish/v1/Systems/system",
            auth=self.credentials,
            verify=False,
            name="02_Power_State_Verification",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    power_state = response.json().get("PowerState")
                    valid_power_states = {"On", "Off", "PoweringOn", "PoweringOff"}
                    
                    if power_state in valid_power_states:
                        response.success()
                    else:
                        response.failure(f"Недопустимое состояние питания: {power_state}")
                except ValueError:
                    response.failure("Некорректный JSON-ответ")
            else:
                response.failure(f"Ошибка HTTP: {response.status_code}")
>>>>>>> 634deb7 (need to check)
