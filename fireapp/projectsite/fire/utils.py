# fireapp/utils.py
import requests

PSUSPHERE_API_URL = 'https://your-psusphere-domain/api/yourmodel/'

def get_data_from_psusphere():
    response = requests.get(PSUSPHERE_API_URL)
    if response.status_code == 200:
        return response.json()
    return None

def send_data_to_psusphere(data):
    response = requests.post(PSUSPHERE_API_URL, json=data)
    if response.status_code == 201:
        return response.json()
    return None
