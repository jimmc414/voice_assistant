import os
import sys
import queue
import threading
import webbrowser
import subprocess
import time

import pyaudio
import pvporcupine  # Picovoice Porcupine
from vosk import Model, KaldiRecognizer
import struct
import winsound
import json

# ------------------------------------------------------------------------------
# Command List
##
POSSIBLE_COMMANDS = [
    "open command prompt",
    "open cmd",
    "open youtube",
    "open google",
    "open notepad",
    "open notepadplusplus",
    "work",
    "one file",
    "open server",
    "open tasks",
    "open four",
    "open three",
    "open pro",
    "kill tasks"
]

# ------------------------------------------------------------------------------
# CONFIGURATION

# Set paths to your Porcupine keyword file (.ppn) and model file (.pv)change filenames to your actual filenames.
# You can obtain a free key & .ppn file from Picovoice console and put it in porcupine/ folder.
PORCUPINE_ACCESS_KEY = "insert API key here from https://picovoice.ai/console/"
PORCUPINE_KEYWORD_PATH = "./porcupine/hotword_en_windows_v3_0_0.ppn"
PORCUPINE_MODEL_PATH   = "./porcupine/porcupine_params.pv"

# Path to Vosk offline model (unzip the Vosk model folder here):
VOSK_MODEL_PATH = "C:/python/voice_assistant/vosk-model/"

# Audio settings
RATE = 16000         # Sample rate for both Porcupine & Vosk
CHANNELS = 1
FRAME_LENGTH = 512   # Number of frames per chunk for Porcupine (depends on the model)
                     # Typically Porcupine uses 512 or 1024 for 16kHz.

# Duration to listen for a command (seconds) after hotword is detected
COMMAND_LISTEN_DURATION = 5.0

# ------------------------------------------------------------------------------
# GLOBALS
audio_queue = queue.Queue()
stop_event = threading.Event()
hotword_detected_event = threading.Event()

listening_enabled = True  # Toggle to enable/disable listening altogether

# ------------------------------------------------------------------------------
# AUDIO CAPTURE THREAD

def audio_capture_loop():
    """Continuously capture audio from the default microphone in shared mode (Windows)
    and place frames into the audio_queue."""
    pa = pyaudio.PyAudio()

    # Try to open default input device in "shared" mode.
    # PyAudio typically opens shared mode by default unless exclusive is forced.
    stream = pa.open(
        rate=RATE,
        channels=CHANNELS,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=FRAME_LENGTH,
        input_device_index=None,  # Default device
        stream_callback=None
    )

    stream.start_stream()
    print("[Audio Capture] Microphone stream opened in shared mode.")

    while not stop_event.is_set():
        # Read raw PCM data from mic
        data = stream.read(FRAME_LENGTH, exception_on_overflow=False)
        audio_queue.put(data)

    stream.stop_stream()
    stream.close()
    pa.terminate()
    print("[Audio Capture] Exiting audio capture thread...")

# ------------------------------------------------------------------------------
# HOTWORD DETECTION THREAD

def hotword_detection_loop(porcupine_handle):
    print("[Hotword] Starting hotword detection loop...")
    while not stop_event.is_set():
        try:
            data = audio_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        if not listening_enabled:
            continue

        # Check that we have exactly 2 * porcupine_handle.frame_length bytes
        if len(data) != 2 * porcupine_handle.frame_length:
            # Skip if partial chunk or mismatch
            continue

        # Convert raw bytes -> tuple of 16-bit samples
        pcm = struct.unpack_from("h" * porcupine_handle.frame_length, data)

        # Now pass the *array of int16 samples* to Porcupine
        keyword_index = porcupine_handle.process(pcm)
        if keyword_index >= 0:
            print("[Hotword] Hotword detected!")
            hotword_detected_event.set()

# ------------------------------------------------------------------------------
# COMMAND RECOGNITION FUNCTION

def recognize_command(vosk_model):
    """
    Listens for a short duration of audio after hotword detection
    and returns transcribed text using a small grammar-based list.
    """
    print("[Command] Starting command recognition...")

    # Convert your command list to JSON
    grammar_json = json.dumps(POSSIBLE_COMMANDS)

    # Pass grammar_json as the 3rd argument to KaldiRecognizer
    recognizer = KaldiRecognizer(vosk_model, RATE, grammar_json)
    recognizer.SetWords(True)

    start_time = time.time()

    # Flush stale audio from the queue
    while not audio_queue.empty():
        audio_queue.get()

    # Capture audio for COMMAND_LISTEN_DURATION seconds
    while (time.time() - start_time) < COMMAND_LISTEN_DURATION:
        if not listening_enabled:
            break
        try:
            data = audio_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        if recognizer.AcceptWaveform(data):
            # We don't explicitly handle partial or final result here
            pass

    # Get final result
    result_json = recognizer.FinalResult()
    parsed_result = json.loads(result_json)
    recognized_text = parsed_result.get("text", "")
    print(f"[Command] Recognized text: {recognized_text}")
    return recognized_text

def process_command_text(text):
    """Map recognized text to actions. Expand with your own logic."""
    text = text.lower().strip()
    if not text:
        print("[Command] No speech detected or recognition failed.")
        return

    # Simple keyword-based command detection
    if "open command prompt" in text or "open cmd" in text:
        print("[Action] Launching Command Prompt...")
        subprocess.Popen("cmd.exe")  # Non-blocking
    elif "open youtube" in text:
        print("[Action] Opening YouTube...")
        webbrowser.open("https://youtube.com")
    elif "open google" in text:
        print("[Action] Opening Google...")
        webbrowser.open("https://google.com")
    elif "open notepad" in text:
        print("[Action] Opening Notepad...")
        subprocess.Popen("notepad.exe")
    elif "open notepadplusplus" in text:
        print("[Action] Opening NotepadPlusPlus...")
        subprocess.Popen("npp.cmd")
    elif "work" in text:
        print("[Action] Opening work...")
        subprocess.Popen(["cmd.exe", "/k", "conda", "activate", "work"])
    elif "one file" in text:
        print("[Action] Opening 1file...")
        subprocess.Popen("1file.cmd")
    elif "open server" in text:
        print("[Action] Opening MP-CP...")
        subprocess.Popen("mstsc -v mp-cp")
    elif "open tasks" in text:
        print("[Action] Opening Scheduled Tasks...")
        webbrowser.open("https://chatgpt.com/?model=gpt-4o-jawbone")
    elif "open four" in text:
        print("[Action] Opening gpt-4o...")
        webbrowser.open("https://chatgpt.com/?model=gpt-4o")
    elif "open three" in text:
        print("[Action] Opening o3-mini-high...")
        webbrowser.open("https://chatgpt.com/?model=o3-mini-high")
    elif "open pro" in text:
        print("[Action] Opening o1-Pro...")
        webbrowser.open("https://chatgpt.com/?model=o1-pro")
    elif "kill tasks" in text:
        print("[Action] Killing all tasks...")
        subprocess.Popen(["taskkill", "/F", "/FI", "STATUS eq RUNNING"], shell=True)   
    else:
        print(f"[Action] No matching command for: {text}")


# ------------------------------------------------------------------------------
# MAIN

def main():
    # 1) Initialize Porcupine for hotword detection
    print("[Init] Loading Porcupine for hotword detection...")
    porcupine_handle = pvporcupine.create(
        access_key=PORCUPINE_ACCESS_KEY,
        keyword_paths=[PORCUPINE_KEYWORD_PATH],
        model_path=PORCUPINE_MODEL_PATH
    )

    # 2) Load Vosk model
    if not os.path.isdir(VOSK_MODEL_PATH):
        print("[Error] Vosk model folder not found. Please download/unzip model into:", VOSK_MODEL_PATH)
        sys.exit(1)
    print("[Init] Loading Vosk model (this may take a few seconds)...")
    vosk_model = Model(VOSK_MODEL_PATH)
    print("[Init] Vosk model loaded.")

    # 3) Start threads
    audio_thread = threading.Thread(target=audio_capture_loop, daemon=True)
    hotword_thread = threading.Thread(target=hotword_detection_loop, 
                                      args=(porcupine_handle,), daemon=True)

    audio_thread.start()
    hotword_thread.start()

    print("[Main] System is ready. Say your hotword to begin (e.g., 'Hey Computer').")
    print("[Main] Press Ctrl+C to exit.")

    try:
        while True:
            # Wait for hotword detection
            hotword_detected_event.wait()
            hotword_detected_event.clear()  # reset for next detection

            # --- Beep to indicate "listening" ---
            winsound.Beep(880, 200)  
            # 880 Hz for 200 ms, tweak as desired

            if not listening_enabled:
                continue

            # 4) Recognize the command
            command_text = recognize_command(vosk_model)

            # 5) Execute the mapped action
            process_command_text(command_text)

            print("[Main] Returning to hotword listening...")

    except KeyboardInterrupt:
        print("\n[Main] KeyboardInterrupt received. Shutting down...")
    finally:
        stop_event.set()
        audio_thread.join()
        # Gracefully release Porcupine resources
        porcupine_handle.delete()
        print("[Main] Cleanup complete. Exiting.")


if __name__ == "__main__":
    main()
