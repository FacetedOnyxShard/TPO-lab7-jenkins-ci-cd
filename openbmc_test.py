import subprocess
import time

def test_power():
    base_cmd = "ipmitool -I lanplus -H 10.168.44.66 -p 2623 -U root -P 0penBmc"
    
    power_commands = {
        'status': f"{base_cmd} power status",
        'on': f"{base_cmd} power on", 
        'off': f"{base_cmd} power off"
    }
    
    result = subprocess.run(power_commands['status'], shell=True, capture_output=True, text=True)
    
    current_status = result.stdout.lower()
    
    if 'on' in current_status:
        result = subprocess.run(power_commands['off'], shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Сервер выключен")
            time.sleep(5)
            
            print("Включаем сервер...")
            result = subprocess.run(power_commands['on'], shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("Сервер включен")
        else:
            print(f"Ошибка выключения: {result.stderr}")

def test_inventory():
    result = subprocess.run(
        "ipmitool -I lanplus -H 10.168.44.66 -p 2623 -U root -P 0penBmc fru print",
        shell=True,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, "IPMI команда не сработала"
    
    assert len(result.stdout) > 0, "Нет данных инвентаризации"