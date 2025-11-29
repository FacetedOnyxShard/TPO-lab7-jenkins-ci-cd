import pytest
import requests

base_url = "https://localhost:2443/redfish/v1"
auth_data = {
    "UserName": "root",
    "Password": "0penBmc"
}

def test_create_session():
    url = f"{base_url}/SessionService/Sessions"

    response = requests.post(
        url,
        json=auth_data,
        verify=False,
        timeout=10
    )

    assert response.ok
    assert 'X-Auth-Token' in response.headers, "Токен сессии отсутствует в заголовках"

def test_system():
    session_url = f"{base_url}/SessionService/Sessions"
    session_response = requests.post(
        session_url,
        json=auth_data,
        verify=False,
        timeout=10
    )
    
    assert session_response.ok, "Не удалось создать сессию"
    auth_token = session_response.headers['X-Auth-Token']
    
    url = f"{base_url}/Systems/system"
    
    headers = {
        'X-Auth-Token': auth_token
    }
    
    response = requests.get(
        url,
        headers=headers,
        verify=False,
        timeout=10
    )
    
    assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
    
    data = response.json()
    
    assert 'Status' in data, "В ответе отсутствует поле Status"
    assert 'PowerState' in data, "В ответе отсутствует поле PowerState"

def test_power():
    session_url = f"{base_url}/SessionService/Sessions"
    session_response = requests.post(
        session_url,
        json=auth_data,
        verify=False,
        timeout=10
    )

    assert session_response.ok, "Не удалось создать сессию"
    auth_token = session_response.headers['X-Auth-Token']

    reset_url = f"{base_url}/Systems/system/Actions/ComputerSystem.Reset"

    reset_data = {
        "ResetType": "On"
    }
    
    headers = {
        'X-Auth-Token': auth_token,
        'Content-Type': 'application/json'
    }

    response = requests.post(
        reset_url,
        json=reset_data,
        headers=headers,
        verify=False,
        timeout=10
    )

    assert response.status_code in [200, 202, 204], f"Ожидался код 200, 202 или 204, получен {response.status_code}"