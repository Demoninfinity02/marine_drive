import requests

url = "http://172.18.181.148:8082"
headers = {
    "Authorization": "dbedcd7f-81b2-4168-9b00-107b809981ba",
    "Content-Type": "application/json"
}

numbers = [
    "+919876543210",
    "+918318740001",
    "+917359070892",
    "+917819050632",
    "+919534183275"
]

for number in numbers:
    payload = {
        "to": number,
        "message": "Hello! This is a test message. ALERT PHYTOPLANKTON NOT SAFE DONT DO FISHING"
    }
    r = requests.post(url, headers=headers, json=payload)
    print(f"Sent to {number}: {r.status_code}, {r.text}")
