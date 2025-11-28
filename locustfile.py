from locust import HttpUser, task, between
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

  