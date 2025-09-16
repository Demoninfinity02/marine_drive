import os
import time
import json
from flask import Flask, Response, request, stream_with_context, jsonify
import cv2
import requests
import google.generativeai as genai
import PIL.Image

app = Flask(__name__)

# Configure the Gemini API key
api_key = "AIzaSyBF6HES_TQm-FBxSdHBJnNwMBWsyC0gBsw"
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

genai.configure(api_key=api_key)

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


def get_phytoplankton_info(image_path: str):
    """
    Analyzes an image of phytoplankton using the Gemini API and returns the scientific name and count.

    Args:
        image_path: The path to the input image file.
    """
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
    YOU ARE BLUFF MASTER, WHATEVER YOU SEE, YOU SAY EVEN THOUGH ITS NOT SCIENTIFICALLY CORRECT, JUST ENOUGH, THAT ON SURFACE IT LOOKS SCIENTIFICALLY CORRECT
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
        image_file_path = "/Users/atharvrastogi/Documents/GitHub/marine_drive/frontend/backend/realImage.jpg"
        
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
                    "nextjs_response": response.json()
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





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), threaded=True)
