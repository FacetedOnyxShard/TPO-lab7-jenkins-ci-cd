import requests
from requests.auth import HTTPBasicAuth
import os
import json
import pytest
import time
import subprocess
import logging

# настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'redfish_test.log')
file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


BASE_URL = 'https://localhost:2443/redfish/v1'
SESSION_URL = F'{BASE_URL}/SessionService/Sessions'
SYSTEM_URL = F'{BASE_URL}/Systems/system'
POWER_URL = F'{SYSTEM_URL}/Actions/ComputerSystem.Reset'
USERNAME = 'root'
PASSWORD = '0penBmc'
VALID_CREDENTIALS = {"UserName": USERNAME, "Password": PASSWORD}

def get_auth_token():
  logger.info("Получение токена...")
  response = requests.post(
    SESSION_URL,
    json=VALID_CREDENTIALS,
    verify=False,
  )
  data = response.json()
  token = data.get('X-Auth-Token')
  logger.info("Токен получен успешно")
  return token

@pytest.fixture(scope="session")
def redfish_session():
  logger.info("Создание сессии...")
  session = requests.Session()
  session.auth = (USERNAME, PASSWORD)
  session.verify = False

  session_token = get_auth_token()
  session.headers.update({'X-Auth-Token': session_token})
  logger.info("Сессия создана успешно")

  yield session

  session.close()
  logger.info("Сессия закрыта")

def get_system_data(redfish_session):
  try:
    response = redfish_session.get(SYSTEM_URL)
    data = response.json()
    return data
  except Exception as e:
    logger.error(f"Не удалось получить данные о системе: {e}")
    pass

def test_success_auth():
  logger.info("Отправка запроса на аутентификацию...")
  response = requests.post(
    SESSION_URL,
    json=VALID_CREDENTIALS,
    verify=False,
  )

  data = response.headers
  session_token = data.get('X-Auth-Token')

  assert response.status_code in [200, 201], "Статус код не 200"

  logger.info("Аутентификация прошла успешно")
  
  assert session_token is not None, "Токен сессии не получен"
  assert len(session_token) > 0, "Токен сессии пустой"

  logger.info("Токен получен")


def test_get_system_info(redfish_session):
  logger.info("Тест получения информации о системе...")

  try:
    response = redfish_session.get(SYSTEM_URL)
    data = response.json()
    assert response.status_code in [200, 201], "Статус код не 200"
    assert "Status" in data, "Нет поля Status у ответа"
    assert "PowerState" in data, "Нет поля PowerState у ответа"
    logger.info("Тест получения информации о системе пройден")
  except Exception as e:
    logger.error(f"Ошибка при получении информации о системе: {e}")
    pytest.fail(f"Не удалось выполнить GET запрос по этому URL: {SYSTEM_URL}")


def test_poweronoff(redfish_session):
  logger.info("Тест включения сервера...")
  response = redfish_session.post(
    POWER_URL,
    json={"ResetType": "On"},
  )

  state_changed = 0

  start_time = time.time()
  current_time = time.time()

  timeout = 30
  logger.info(f"Начало timeout для получения PowerState длительностью {timeout} сек.")
  while current_time - start_time < timeout:
    new_state = get_system_data(redfish_session).get('PowerState')
    if new_state != "Off":
      state_changed = 1
      break
    
    time.sleep(1)
    current_time = time.time()

  assert response.status_code in [200, 201, 202, 204], "Статус код не 200"
  assert state_changed == 1, "Состояние не изменилось"
  logger.info("Тест включения сервера прошел успешно")


def test_cpu_temperatures_normal(redfish_session):
  """Тест, что температуры CPU в норме"""
  url = f"{BASE_URL}/Chassis/1/Thermal"
  response = redfish_session.get(url,verify=False)
  
  assert response.status_code == 200, "Не удалось подключиться к Redfish"
  
  data = response.json()
  cpu_temps = []
  
  for sensor in data.get('Temperatures', []):
    if 'cpu' in sensor.get('Name', '').lower():
      temp = sensor.get('ReadingCelsius')
      if temp is not None:
        cpu_temps.append(temp)
  
  assert cpu_temps, "Не найдены датчики CPU"
  
  for temp in cpu_temps:
    assert temp < 80, f"Температура CPU {temp}°C превышает норму"

def get_redfish_cpu_temps(redfish_session):
  """Получить температуры CPU из Redfish"""
  url = f"{BASE_URL}/Chassis/1/Thermal"
  response = redfish_session.get(url, verify=False)
  
  if response.status_code != 200:
    return {}
      
  data = response.json()
  temps = {}
  
  for sensor in data.get('Temperatures', []):
    name = sensor.get('Name', '')
    temp = sensor.get('ReadingCelsius')
    if temp is not None and 'cpu' in name.lower():
      temps[name] = temp
          
  return temps

def get_ipmi_cpu_temps():
  """Получить температуры CPU из IPMI"""
  try:
    result = subprocess.run(
      ['ipmitool', 'sensor', 'list'], 
      capture_output=True, text=True, timeout=10
    )
    
    temps = {}
    for line in result.stdout.split('\n'):
      if 'CPU' in line and 'degrees C' in line:
        parts = line.split('|')
        if len(parts) >= 2:
          name = parts[0].strip()
          temp_str = parts[1].strip()
          # Ищем число в строке
          for word in temp_str.split():
            try:
              temp = float(word)
              temps[name] = temp
              break
            except ValueError:
              continue
    return temps
  except:
    return {}

def test_redfish_ipmi_temperature_match(redfish_session):
  """Тест, что температуры в Redfish и IPMI совпадают"""
  
  redfish_temps = get_redfish_cpu_temps(redfish_session)
  ipmi_temps = get_ipmi_cpu_temps()
  
  assert redfish_temps, "Нет данных из Redfish"
  assert ipmi_temps, "Нет данных из IPMI"
  
  for name, redfish_temp in redfish_temps.items():
    for ipmi_name, ipmi_temp in ipmi_temps.items():
      if any(keyword in ipmi_name for keyword in ['CPU', 'Proc']):
        diff = abs(redfish_temp - ipmi_temp)
        assert diff <= 5, f"Большое расхождение: Redfish {redfish_temp}°C vs IPMI {ipmi_temp}°C"

