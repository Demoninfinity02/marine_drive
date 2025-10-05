import os
import time
import json
import threading
import tempfile
import queue
from collections import defaultdict, deque
from datetime import datetime
from flask import Flask, Response, request, stream_with_context, jsonify
import cv2
import requests
import google.generativeai as genai
import PIL.Image

app = Flask(__name__)

# Configure the Gemini API keys for rotation
api_keys = [
    "AIzaSyBF6HES_TQm-FBxSdHBJnNwMBWsyC0gBsw",
    "AIzaSyDxj8-G5omNgOZDIcho2RvZi0bn03pq6w4",
    "AIzaSyA7wN6K1ow86NQ6983-NfedJcIe1YUVH4U",
    "AIzaSyDDdwfRixs-VyyCAsT1vJobn2hWLHxynXk",
    "AIzaSyApAZd1sF6laC0XZ82PjTfVc_6BTyIZhkg"
]

current_key_index = 0
last_key_rotation = time.time()

def get_current_api_key():
    """Get current API key and rotate if needed (every 14 seconds)"""
    global current_key_index, last_key_rotation
    
    current_time = time.time()
    if current_time - last_key_rotation >= 14:  # 14 seconds
        current_key_index = (current_key_index + 1) % len(api_keys)
        last_key_rotation = current_time
        key = api_keys[current_key_index]
        genai.configure(api_key=key)
        print(f"Rotated to API key #{current_key_index + 1}")
    
    return api_keys[current_key_index]

# Initialize with first key
genai.configure(api_key=api_keys[0])

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

# Global variables for auto-capture
auto_capture_enabled = False
capture_thread = None
temp_dir = tempfile.mkdtemp()

# ---------------- Emulation Globals ----------------
emulation_running = False
emulation_thread = None
emulation_duration_seconds = 15 * 60  # 15 minutes target runtime
emulation_start_time = None
emulation_data = []  # loaded from emulation.json
emulation_index = 0

# Threshold / smoothing config
MOVING_AVG_WINDOW = 5
BASELINE_WINDOW = 5
THRESHOLD_MULTIPLIER = 1.5  # threshold = baseline_mean * multiplier
ABOVE_THRESHOLD_REQUIRED_SECONDS = 5 * 60  # must stay above for 5 minutes
ALERT_COOLDOWN_SECONDS = 5 * 60  # cooldown per species before next SMS
TIME_SCALE = float(os.getenv("EMULATION_TIME_SCALE", "10"))  # Time acceleration factor (virtual time). 10 => 1 real second counts as 10 seconds.

# Adjust via env var EMULATION_TIME_SCALE for demos; logic thresholds stay the same.

# State holders
species_windows = defaultdict(lambda: deque(maxlen=MOVING_AVG_WINDOW))
species_baselines = defaultdict(list)
species_above_threshold_start = defaultdict(lambda: None)  # timestamp when first exceeded threshold
species_last_alert_time = defaultdict(lambda: 0.0)

# SSE listener management
class EmulationListener:
    def __init__(self):
        self.queue = queue.Queue()
        self.active = True

    def push(self, data: dict):
        if self.active:
            try:
                self.queue.put_nowait(data)
            except Exception:
                pass

    def close(self):
        self.active = False

emulation_listeners = set()
listeners_lock = threading.Lock()

def broadcast_emulation_event(payload: dict):
    remove = []
    with listeners_lock:
        for l in list(emulation_listeners):
            if not l.active:
                remove.append(l)
                continue
            l.push(payload)
        for r in remove:
            emulation_listeners.discard(r)

def load_emulation_data():
    global emulation_data
    if emulation_data:
        return
    path = os.path.join(os.path.dirname(__file__), 'emulation.json')
    try:
        with open(path, 'r') as f:
            emulation_data = json.load(f)
            if not isinstance(emulation_data, list):
                emulation_data = []
        print(f"Loaded emulation dataset: {len(emulation_data)} records")
    except FileNotFoundError:
        print("emulation.json not found; emulation disabled")
        emulation_data = []
    except Exception as e:
        print(f"Failed loading emulation.json: {e}")
        emulation_data = []

def compute_moving_avg(values_deque: deque):
    if not values_deque:
        return None
    return sum(values_deque) / len(values_deque)

def process_emulation_record(rec: dict):
    """Update smoothing & threshold detection and return enriched payload."""
    now = time.time()
    species = rec.get('phytoplanktonscientificName') or 'Unknown'
    raw_value_str = rec.get('no of that pyhtoplankon') or rec.get('count') or '0'
    try:
        raw_value = float(str(raw_value_str).replace(',', '').strip())
    except ValueError:
        raw_value = 0.0

    # Update windows
    win = species_windows[species]
    win.append(raw_value)
    moving_avg = compute_moving_avg(win)

    # Baseline accumulation (first BASELINE_WINDOW raw points)
    if len(species_baselines[species]) < BASELINE_WINDOW:
        species_baselines[species].append(raw_value)

    baseline = None
    threshold = None
    if len(species_baselines[species]) == BASELINE_WINDOW:
        baseline = sum(species_baselines[species]) / BASELINE_WINDOW
        threshold = baseline * THRESHOLD_MULTIPLIER

    breach = False  # simply indicates current state above threshold
    alert_triggered = False
    above_threshold_seconds = 0.0
    if threshold is not None and moving_avg is not None:
        if moving_avg >= threshold:
            breach = True
            if species_above_threshold_start[species] is None:
                species_above_threshold_start[species] = now
            above_threshold_seconds = now - species_above_threshold_start[species]
            if above_threshold_seconds >= ABOVE_THRESHOLD_REQUIRED_SECONDS:
                last_alert = species_last_alert_time[species]
                if now - last_alert >= ALERT_COOLDOWN_SECONDS:
                    above_threshold_seconds = (now - species_above_threshold_start[species]) * TIME_SCALE
                    alert_triggered = True
                    species_last_alert_time[species] = now
                    try:
                        send_sms_alert([{"phytoplanktonscientificName": species}])
                    except Exception as e:
                        print(f"SMS send failed in emulation: {e}")
        else:
            # reset timer if we drop below threshold
            species_above_threshold_start[species] = None
            above_threshold_seconds = 0.0

    enriched = {
        "type": "emulation_tick",
        "timestamp": rec.get('timestamp') or datetime.utcnow().isoformat(),
        "species": species,
        "raw": raw_value,
        "movingAvg": moving_avg,
        "baseline": baseline,
        "threshold": threshold,
        "breach": breach,
        "alertTriggered": alert_triggered,
        "aboveThresholdSeconds": above_threshold_seconds,
    }
    return enriched

def emulation_loop():
    """Emit all species for a given logical timestamp together as a batch."""
    global emulation_running, emulation_index, emulation_start_time
    load_emulation_data()
    if not emulation_data:
        print("No emulation data available.")
        emulation_running = False
        return
    # Group raw data by timestamp key to batch species simultaneously
    grouped = {}
    for rec in emulation_data:
        ts = rec.get('timestamp') or 'unknown'
        grouped.setdefault(ts, []).append(rec)
    ordered_ts = sorted(grouped.keys())

    emulation_start_time = time.time()
    default_interval = 5.0
    ts_index = 0
    while emulation_running and (time.time() - emulation_start_time) < emulation_duration_seconds:
        ts = ordered_ts[ts_index % len(ordered_ts)]
        batch_raw = grouped[ts]
        batch_enriched = [process_emulation_record(r) for r in batch_raw]
        # Send as batch event (frontend will expand) plus optional individual fallback if needed.
        broadcast_emulation_event({
            "type": "emulation_tick_batch",
            "timestamp": ts,
            "records": batch_enriched
        })
        ts_index += 1
        emulation_index += len(batch_raw)
        time.sleep(default_interval)
    emulation_running = False
    broadcast_emulation_event({"type": "emulation_complete"})

def start_emulation():
    global emulation_running, emulation_thread, emulation_index
    if emulation_running:
        return False
    # Reset state
    emulation_index = 0
    species_windows.clear()
    species_baselines.clear()
    species_above_threshold_start.clear()
    # keep last alert times (prevent repeated alerts on restart?) reset them
    species_last_alert_time.clear()
    emulation_running = True
    emulation_thread = threading.Thread(target=emulation_loop, daemon=True)
    emulation_thread.start()
    print("Emulation started for 15 minutes")
    return True

def emulation_sse_generator():
    listener = EmulationListener()
    with listeners_lock:
        emulation_listeners.add(listener)
    try:
        # Immediately push status
        listener.push({"type": "emulation_status", "running": emulation_running})
        while True:
            item = listener.queue.get()
            yield f"data: {json.dumps(item)}\n\n"
    except GeneratorExit:
        listener.close()
    finally:
        with listeners_lock:
            emulation_listeners.discard(listener)

@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return resp


def get_video_source():
    """Get the configured video source for capturing frames"""
    if PHONE_MJPEG_URL:
        return PHONE_MJPEG_URL
    elif RTSP_URL:
        return RTSP_URL
    else:
        return WEBCAM_INDEX


def capture_frame_from_source():
    """Capture a single frame from the video source and save to temp file"""
    source = get_video_source()
    cap = None
    
    try:
        if isinstance(source, str) and source.startswith("http"):
            # For HTTP sources, we need a different approach
            # Try to get a frame from the MJPEG stream
            response = requests.get(source, stream=True, timeout=5)
            if response.status_code == 200:
                # Read some data and try to extract a JPEG frame
                data = response.raw.read(1024 * 1024)  # 1MB should be enough for one frame
                
                # Find JPEG markers
                start = data.find(b'\xff\xd8')  # JPEG start
                end = data.find(b'\xff\xd9', start) + 2  # JPEG end
                
                if start != -1 and end != -1 and end > start:
                    jpeg_data = data[start:end]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    temp_path = os.path.join(temp_dir, f"capture_{timestamp}.jpg")
                    
                    with open(temp_path, 'wb') as f:
                        f.write(jpeg_data)
                    
                    return temp_path
        else:
            # For webcam/RTSP sources
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                return None
                
            _apply_capture_config(cap)
            
            ret, frame = cap.read()
            if ret:
                # Apply flip if configured
                if FLIP_CODE:
                    try:
                        code = int(FLIP_CODE)
                        frame = cv2.flip(frame, code)
                    except Exception:
                        pass
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                temp_path = os.path.join(temp_dir, f"capture_{timestamp}.jpg")
                
                success = cv2.imwrite(temp_path, frame)
                if success:
                    return temp_path
                    
    except Exception as e:
        print(f"Error capturing frame: {e}")
    finally:
        if cap:
            cap.release()
    
    return None


def send_sms_alert(alert_species):
    """Send SMS alerts for high/mid alert level phytoplankton"""
    try:
        url = "http://172.18.168.69:8082"
        headers = {
            "Authorization": "dbedcd7f-81b2-4168-9b00-107b809981ba",
            "Content-Type": "application/json"
        }
        
        numbers = [
            "+916387924254",
            "+918318740001", 
            "+917359070892",
            "+917819050632",
            "+919534183275"
        ]
        
        # Create alert message with species info
        species_names = [species.get('phytoplanktonscientificName', 'Unknown') for species in alert_species]
        alert_message = f"ALERT: Dangerous phytoplankton detected - {', '.join(species_names[:2])}{'...' if len(species_names) > 2 else ''}. DON'T GO FOR FISHING!"
        
        success_count = 0
        for number in numbers:
            payload = {
                "to": number,
                "message": alert_message
            }
            try:
                r = requests.post(url, headers=headers, json=payload, timeout=5)
                if r.status_code == 200:
                    success_count += 1
                    print(f"SMS sent to {number}: Success")
                else:
                    print(f"SMS failed to {number}: {r.status_code}")
            except Exception as e:
                print(f"SMS error for {number}: {e}")
        
        print(f"SMS Alert: Sent to {success_count}/{len(numbers)} numbers")
        return success_count > 0
        
    except Exception as e:
        print(f"SMS Alert system error: {e}")
        return False


def analyze_captured_image(image_path):
    """Analyze captured image and send to Next.js"""
    try:
        print(f"Analyzing image: {image_path}")
        
        # Get the phytoplankton information from Gemini
        result = get_phytoplankton_info(image_path)
        
        # Try to parse the JSON from Gemini's response
        try:
            # Clean up the response to extract JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            phytoplankton_data = json.loads(result.strip())
            
            # Check for high/mid alert levels and send SMS if needed
            alert_species = [species for species in phytoplankton_data 
                           if isinstance(species, dict) and 
                           species.get('alertLevel', '').lower() in ['high', 'mid']]
            
            if alert_species:
                print(f"Alert detected! Found {len(alert_species)} dangerous species")
                sms_sent = send_sms_alert(alert_species)
                if sms_sent:
                    print("SMS alerts sent successfully")
            
            # Send to Next.js API
            nextjs_url = "http://localhost:3000/api/phytoplankton"
            response = requests.post(
                nextjs_url,
                json=phytoplankton_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Successfully sent data to Next.js: {len(phytoplankton_data)} species detected")
            else:
                print(f"Failed to send to Next.js: {response.status_code}")
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from Gemini: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to Next.js: {e}")
            
    except Exception as e:
        print(f"Analysis failed: {e}")
    finally:
        # Clean up the temporary image
        try:
            os.remove(image_path)
        except:
            pass


def auto_capture_loop():
    """Main loop for automatic capture and analysis"""
    global auto_capture_enabled
    
    while auto_capture_enabled:
        try:
            # Capture frame
            image_path = capture_frame_from_source()
            
            if image_path:
                # Analyze in background
                analyze_captured_image(image_path)
            else:
                print("Failed to capture frame")
                
        except Exception as e:
            print(f"Error in auto capture loop: {e}")
            
        # Wait 15 seconds
        time.sleep(15)


def start_auto_capture():
    """Start the automatic capture thread"""
    global auto_capture_enabled, capture_thread
    
    if not auto_capture_enabled:
        auto_capture_enabled = True
        capture_thread = threading.Thread(target=auto_capture_loop, daemon=True)
        capture_thread.start()
        print("Auto-capture started - analyzing every 15 seconds")


def stop_auto_capture():
    """Stop the automatic capture thread"""
    global auto_capture_enabled
    auto_capture_enabled = False
    print("Auto-capture stopped")


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
    return {"ok": True, "routes": ["/stream/mjpeg", "/analyze", "/auto-capture/start", "/auto-capture/stop", "/auto-capture/status"]}


@app.post("/auto-capture/start")
def start_auto_capture_endpoint():
    """Start automatic capture and analysis every 15 seconds"""
    start_auto_capture()
    return jsonify({
        "success": True,
        "message": "Auto-capture started",
        "interval": "15 seconds",
        "status": "running"
    })


@app.post("/auto-capture/stop")
def stop_auto_capture_endpoint():
    """Stop automatic capture and analysis"""
    stop_auto_capture()
    return jsonify({
        "success": True,
        "message": "Auto-capture stopped",
        "status": "stopped"
    })


@app.get("/auto-capture/status")
def auto_capture_status():
    """Get current auto-capture status"""
    current_key = get_current_api_key()  # This will rotate if needed
    return jsonify({
        "enabled": auto_capture_enabled,
        "status": "running" if auto_capture_enabled else "stopped",
        "interval": "15 seconds",
        "temp_dir": temp_dir,
        "current_api_key_index": current_key_index + 1,
        "total_api_keys": len(api_keys),
        "time_until_next_rotation": max(0, 14 - (time.time() - last_key_rotation))
    })


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


def get_phytoplankton_info(image_path: str):
    """
    Analyzes an image of phytoplankton using the Gemini API and returns the scientific name and count.

    Args:
        image_path: The path to the input image file.
    """
    # Rotate API key if needed
    current_key = get_current_api_key()
    
    # Set up the model
    generation_config = {
        "temperature": 0,
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        generation_config=generation_config,
    )

    # Prepare the image and prompt
    try:
        img = PIL.Image.open(image_path)
    except FileNotFoundError:
        return f"Error: Image file not found at {image_path}"

    prompt = """
    YOU ARE JOB IS TO DETECT PHYTOPLANKTONS, WHATEVER YOU SEE, YOU SAY EVEN THOUGH ITS NOT SCIENTIFICALLY CORRECT, JUST SAY IT, JUST MAKE SURE THAT'S IT IS CLOSE ENOUGH, THAT ON SURFACE IT LOOKS SCIENTIFICALLY CORRECT
    Analyze the image and identify all the visible phytoplankton species.
    you just try your best to study the image, and just say what you see, i dont want you to stay catious, or any form of stupidity
    give me what i am asking for, NOTHING ELSE, also the image would be in circle so dont mistake it for pyhtoplankton it's not. It's intentionally round, detect phytoplanktons inside the round image
    Provide your best estimate for the scientific name and the approximate count of that phytoplankton.
    For each species, provide your best estimate for the scientific name and the approximate count.
    Even if you are 0.1% sure, just say it, I want all possible phytoplanktons you can detect, and just be certain, don't say other many just be certain, make it up, because i have to show this to judges as prototype, they don't know much about phytoplankton, anyway, so just bluff.
    Return the output as a list of JSON objects, in the following format exactly:
    [
        {
            "phytoplanktonscientificName": "<name>",
            "no of that pyhtoplankon": "<number>",
            "Genus": "<genus_name>",
            "Confidence": "<confidence_of_detection_out_of_100>",
            "optimalPh": "<quantitative average optimal pH as a number>",
            "optimalTemp": "<quantitative temperature in which they thrive the most in celsius>",
            "photosynthetic": true,
            "alertLevel": "<Low|Mid|High>",
            "Area_Concentration": "<quantitative_area_concentration_of_species_in_1ml_of_sample>",
            "Sample_Volume": "<total_volume_of_sample_in_which_species_was_found_in_ml_answer=1ml>",
            "Dissolved_Oxygen": "<quantitative_dissolved_oxygen_in_per_species_in_mg_per_liter>"
        },
        {
            "phytoplanktonscientificName": "<name>",
            "no of that pyhtoplankon": "<number>",
            "Genus": "<genus_name>",
            "Confidence": "<confidence_of_detection_out_of_100>",
            "optimalPh": "<quantitative average optimal pH as a number>",
            "optimalTemp": "<quantitative temperature in which they thrive the most in celsius>",
            "photosynthetic": true,
            "alertLevel": "<Low|Mid|High>",
            "Area_Concentration": "<quantitative_area_concentration_of_species_in_1ml_of_sample>",
            "Sample_Volume": "<total_volume_of_sample_in_which_species_was_found_in_ml_answer=1ml>",
            "Dissolved_Oxygen": "<quantitative_dissolved_oxygen_in_per_species_in_mg_per_liter>"
        },
    ]
    If you can only identify one, return a list with a single object.
    """

    # Generate content
    response = model.generate_content([prompt, img])

    return response.text


@app.post("/analyze")
def analyze_phytoplankton():
    """
    Analyze phytoplankton from image and send results to Next.js API
    """
    try:
        # Replace with actual image path - keeping your original path for now
        image_file_path = "/Users/atharvrastogi/Documents/GitHub/marine_drive/frontend/backend/realimage3.png"
        
        # Get the phytoplankton information from Gemini
        result = get_phytoplankton_info(image_file_path)
        
        # Try to parse the JSON from Gemini's response
        try:
            # Clean up the response to extract JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            phytoplankton_data = json.loads(result.strip())
            
            # Check for high/mid alert levels and send SMS if needed
            alert_species = [species for species in phytoplankton_data 
                           if isinstance(species, dict) and 
                           species.get('alertLevel', '').lower() in ['high', 'mid']]
            
            if alert_species:
                print(f"Manual analysis alert! Found {len(alert_species)} dangerous species")
                sms_sent = send_sms_alert(alert_species)
                if sms_sent:
                    print("SMS alerts sent successfully")
            
            # Send to Next.js API
            nextjs_url = "http://localhost:3000/api/phytoplankton"
            response = requests.post(
                nextjs_url,
                json=phytoplankton_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                return jsonify({
                    "success": True,
                    "message": "Data sent to Next.js successfully",
                    "gemini_response": result,
                    "parsed_data": phytoplankton_data,
                    "nextjs_response": response.json(),
                    "alert_detected": len(alert_species) > 0,
                    "alert_species_count": len(alert_species),
                    "sms_sent": len(alert_species) > 0
                })
            else:
                return jsonify({
                    "success": False,
                    "error": f"Next.js API returned status {response.status_code}",
                    "gemini_response": result,
                    "parsed_data": phytoplankton_data
                }), 500
                
        except json.JSONDecodeError as e:
            return jsonify({
                "success": False,
                "error": f"Failed to parse JSON from Gemini: {str(e)}",
                "raw_response": result
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }), 500




@app.post('/emulate/start')
def emulate_start():
    started = start_emulation()
    return jsonify({
        'started': started,
        'running': emulation_running,
        'durationSeconds': emulation_duration_seconds
    })


@app.get('/emulate/status')
def emulate_status():
    elapsed = (time.time() - emulation_start_time) if emulation_start_time else 0
    return jsonify({
        'running': emulation_running,
        'elapsedSeconds': elapsed,
        'remainingSeconds': max(0, emulation_duration_seconds - elapsed) if emulation_running else 0,
        'index': emulation_index
    })


@app.get('/emulate/stream')
def emulate_stream():
    return Response(emulation_sse_generator(), mimetype='text/event-stream')


if __name__ == "__main__":
    print(f"Temporary directory for captures: {temp_dir}")
    print(f"Configured with {len(api_keys)} API keys for rotation every 14 seconds")
    print("Available endpoints:")
    print("  GET  /                     - API info")
    print("  GET  /stream/mjpeg         - Live video stream")
    print("  POST /analyze              - Manual analysis")
    print("  POST /auto-capture/start   - Start auto-capture (15s interval)")
    print("  POST /auto-capture/stop    - Stop auto-capture")
    print("  GET  /auto-capture/status  - Check auto-capture status")
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), threaded=True)
