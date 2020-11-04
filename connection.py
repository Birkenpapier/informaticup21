import requests
import json

resp = requests.get('https://covidapi.info/api/v1/country/DEU')

if resp.status_code != 200:
    print("Error")
    exit()

data = json.loads(resp.text)
print(data['result']['2020-10-26'])
