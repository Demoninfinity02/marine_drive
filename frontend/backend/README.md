# Simple MJPEG Streaming Backend (Flask)

This Flask server exposes a single endpoint to stream MJPEG video for your frontend `LiveFeed` component.

## Endpoints

- `GET /stream/mjpeg` — Streams multipart MJPEG. Source resolution order:
  1. `?source=` query param (HTTP MJPEG, RTSP URL, or webcam index)
  2. `PHONE_MJPEG_URL` environment variable (e.g. IP Webcam: `http://<phone-ip>:8080/video`)
  3. `RTSP_URL` environment variable
  4. `WEBCAM_INDEX` (default `0`)

## Quick Start (macOS)

```bash
# 1) Create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run server
export PHONE_MJPEG_URL="http://<phone-ip>:8080/video"  # IP Webcam or similar
export PORT=5001
python app.py
```

Now open in browser:
- `http://localhost:5001/stream/mjpeg`
- You should see a continuously loading image (browser displays it as a live stream)

## Testing with Postman
- Send `GET http://localhost:5001/stream/mjpeg` — the response will continuously stream; Postman won’t render video but the transfer won’t finish.
- You can also test a direct override: `GET /stream/mjpeg?source=http://<phone-ip>:8080/video`

## Notes
- For iOS/Android, use apps that provide an MJPEG URL (e.g., Android “IP Webcam”).
- For RTSP-only apps, switch to `RTSP_URL` and we’ll capture via OpenCV.
- Long-lived responses require a standard Python runtime (not serverless).
