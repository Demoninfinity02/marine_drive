import os
import time
from flask import Flask, Response, request, stream_with_context, jsonify
import cv2
import requests

app = Flask(__name__)

# Configuration via env vars
PHONE_MJPEG_URL = os.environ.get("PHONE_MJPEG_URL")  # e.g., http://<phone-ip>:8080/video
RTSP_URL = os.environ.get("RTSP_URL")  # optional RTSP source
WEBCAM_INDEX = int(os.environ.get("WEBCAM_INDEX", "0"))
FPS = float(os.environ.get("FPS", "60"))
WIDTH = int(os.environ.get("WIDTH", "0"))   # 0 means keep source default
HEIGHT = int(os.environ.get("HEIGHT", "0"))  # 0 means keep source default
# FLIP_CODE: -1 both, 0 vertical, 1 horizontal; any other => no flip
FLIP_CODE = os.environ.get("FLIP_CODE", "").strip()

BOUNDARY = "frame"


def mjpeg_generator_from_http(url: str):
    """Proxy an existing MJPEG HTTP stream and re-emit it with our boundary."""
    with requests.get(url, stream=True, timeout=10) as r:
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "")
        boundary = None
        if "multipart" in content_type and "boundary=" in content_type:
            boundary = content_type.split("boundary=")[-1]
        else:
            # Not multipart; just relay bytes as JPEGs if possible (rare)
            boundary = "frame"

        buf = b""
        for chunk in r.iter_content(chunk_size=4096):
            if not chunk:
                continue
            buf += chunk
            # attempts to find jpeg headers -- very simple split by boundary
            while True:
                sep = buf.find(b"--" + boundary.encode())
                if sep == -1:
                    break
                part = buf[:sep]
                buf = buf[sep + len(boundary) + 2:]
                if b"Content-Type: image/jpeg" in part:
                    # find empty line separating headers and body
                    header_end = part.find(b"\r\n\r\n")
                    if header_end != -1:
                        jpeg = part[header_end + 4:]
                        yield (b"--" + BOUNDARY.encode() + b"\r\n"
                               b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")


def _apply_capture_config(cap: cv2.VideoCapture):
    # Apply optional width/height if provided
    if WIDTH > 0:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    if HEIGHT > 0:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


def mjpeg_generator_from_cv(source):
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video source: {source}")

    _apply_capture_config(cap)

    delay = max(1.0 / FPS, 0.001)
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.05)
                continue
            # Optional flip for front cameras if desired
            if FLIP_CODE:
                try:
                    code = int(FLIP_CODE)
                    frame = cv2.flip(frame, code)
                except Exception:
                    pass
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b"--" + BOUNDARY.encode() + b"\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n")
            time.sleep(delay)
    finally:
        cap.release()


@app.get("/")
def root():
    return {"ok": True, "routes": ["/stream/mjpeg"]}


@app.get("/stream/mjpeg")
def stream_mjpeg():
    source = request.args.get("source")  # optional override
    gen = None
    try:
        if source:
            # Prefer explicit override
            if source.startswith("http"):
                gen = mjpeg_generator_from_http(source)
            else:
                # allow numeric indices via query param
                try:
                    idx = int(source)
                    gen = mjpeg_generator_from_cv(idx)
                except ValueError:
                    gen = mjpeg_generator_from_cv(source)
        elif PHONE_MJPEG_URL:
            gen = mjpeg_generator_from_http(PHONE_MJPEG_URL)
        elif RTSP_URL:
            gen = mjpeg_generator_from_cv(RTSP_URL)
        else:
            gen = mjpeg_generator_from_cv(WEBCAM_INDEX)
    except Exception as e:
        return {"error": str(e)}, 500

    return Response(stream_with_context(gen), mimetype=f"multipart/x-mixed-replace; boundary={BOUNDARY}")


@app.get("/debug/cameras")
def debug_cameras():
    """Probe first N indices and report which open successfully with frame size."""
    max_idx = int(request.args.get("max", 10))
    out = []
    for i in range(max_idx):
        cap = cv2.VideoCapture(i)
        opened = cap.isOpened()
        w = h = None
        if opened:
            _apply_capture_config(cap)
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out.append({"index": i, "opened": opened, "width": w, "height": h})
        cap.release()
    return jsonify(out)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), threaded=True)
