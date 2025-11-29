from locust import HttpUser, task, between
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RedfishUser(HttpUser):
    host = "https://localhost:2443"
    wait_time = between(1, 3)
    
    def on_start(self):
        self.auth = ("root", "0penBmc")
    
    @task
    def get_system_info(self):
        self.client.get(
            "/redfish/v1/Systems/system",
            auth=self.auth,
            verify=False,
            name="01_System_Info"
        )
    
    @task
    def check_power_state(self):
        with self.client.get(
            "/redfish/v1/Systems/system",
            auth=self.auth, 
            verify=False,
            name="02_Power_State",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    power_state = response.json().get("PowerState")
                    if power_state in ["On", "Off", "PoweringOn", "PoweringOff"]:
                        response.success()
                    else:
                        response.failure(f"Unexpected PowerState: {power_state}")
                except ValueError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")