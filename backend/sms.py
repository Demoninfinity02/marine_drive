
import time
import requests

time.sleep(300)

url = "http://172.19.112.176:8082"
headers = {
    "Authorization": "dbedcd7f-81b2-4168-9b00-107b809981ba",
    "Content-Type": "application/json"
}

numbers = [
    "+919876543210",
    "+918318740001",
    "+917359070892",
    "+917819050632",
    "+919534183275",
    "+916387924254"
]

for number in numbers:
    payload = {
        "to": number,
        "message": "ALERT DIATOMS ARE INCREASING EXPONENTIALY, IT IS NOT SAFE DON'T GO FOR FISHING"
    }
    r = requests.post(url, headers=headers, json=payload)
    print(f"Sent to {number}: {r.status_code}, {r.text}")


# 1602