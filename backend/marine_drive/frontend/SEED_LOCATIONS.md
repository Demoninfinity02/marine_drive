# Seed species locations from your notebook or via curl

Endpoint: POST /api/phytoplankton/locations

Body JSON:
{
  "species": "Leptocylindrus",
  "mode": "replace", // or "append"
  "markers": [
    { "id": "m1", "coords": [72.8777, 19.0760] },
    { "id": "m2", "coords": [73.0, 19.2] }
  ]
}

Notes
- coords format is [lng, lat]
- When mode is omitted, new markers are appended to existing ones for that species.
- Use mode: "replace" to overwrite previous markers for that species.
- GET /api/phytoplankton/locations?species=Leptocylindrus returns { species, markers }

Notebook snippet (Python)
import requests, json
url = "http://localhost:3000/api/phytoplankton/locations"
payload = {
  "species": "Leptocylindrus",
  "mode": "replace",
  "markers": [
    {"id": f"pt-{i}", "coords": [float(lng), float(lat)]}
    for i, (lng, lat) in enumerate(points)
  ]
}
requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"}).raise_for_status()
