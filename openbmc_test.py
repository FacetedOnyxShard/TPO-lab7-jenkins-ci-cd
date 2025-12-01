import subprocess
import time

class IPMITestSetup:
    def __init__(self):
        self.host = "10.168.44.66"
        self.port = "2623"
        self.user = "root"
        self.password = "0penBmc"
        self.base_cmd = f"ipmitool -I lanplus -H {self.host} -p {self.port} -U {self.user} -P {self.password}"

class IPMITestUtils:
    def __init__(self, setup):
        self.setup = setup
    
    def execute_command(self, command):
        return subprocess.run(command, shell=True, capture_output=True, text=True)
    
    def power_status(self):
        cmd = f"{self.setup.base_cmd} power status"
        return self.execute_command(cmd)
    
    def power_on(self):
        cmd = f"{self.setup.base_cmd} power on"
        return self.execute_command(cmd)
    
    def power_off(self):
        cmd = f"{self.setup.base_cmd} power off"
        return self.execute_command(cmd)
    
    def fru_print(self):
        cmd = f"{self.setup.base_cmd} fru print"
        return self.execute_command(cmd)

def test_power():
    setup = IPMITestSetup()
    utils = IPMITestUtils(setup)
    
    status_result = utils.power_status()
    current_status = status_result.stdout.lower()
    
    if 'on' in current_status:
        off_result = utils.power_off()
        
        if off_result.returncode == 0:
            print("Сервер выключен")
            time.sleep(5)
            
            print("Включаем сервер...")
            on_result = utils.power_on()
            if on_result.returncode == 0:
                print("Сервер включен")
        else:
            print(f"Ошибка выключения: {off_result.stderr}")

def test_inventory():
    setup = IPMITestSetup()
    utils = IPMITestUtils(setup)
    
    fru_result = utils.fru_print()
    
    assert fru_result.returncode == 0
    assert len(fru_result.stdout) > 0