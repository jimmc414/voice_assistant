# Voice Command Launcher

This project is a free, offline voice assistant that runs 100% locally on your machine. It leverages two efficient engines for rapid performance:

- **Picovoice Porcupine:** For fast, low-overhead hotword detection.
- **Vosk:** For quick command recognition using a restricted grammar-based command list and a 40MB voice recognition model.

At present, no ongoing internet connection is required—the API key is only needed to download your custom, pre-trained wake word model. Once set up, the assistant can execute any command or command string you could type into a cmd window or a browser address bar.

---

## Features

- **Local and Free:**  
  The entire system operates offline and is free to use. The only time you'll need an internet connection is when obtaining the trained wake word model from Picovoice.

- **Mic Access Sharing:**  
  Uses the microphone in shared mode, so it won’t monopolize your mic. It works simultaneously with other applications that are using the microphone.

- **Hotword Detection:**  
  Uses Picovoice Porcupine local model to continuously listen for a custom hotword (e.g., "Hey Computer") with minimal resource usage.

- **Command Recognition:**  
  After detecting the hotword, the assistant beeps and listens for a short period (e.g., 5 seconds) and transcribes speech using Vosk. The restricted command list ensures both fast recognition and high accuracy.

- **Extensive Command Execution:**  
  Capable of issuing any command string you can type into a cmd window or browser address bar. Whether it's launching an application, opening a website, or running a custom script, you can extend its functionality as needed.

- **Customizable and Extensible:**  
  Easily update the command list to add new commands or modify existing actions. Adjust the logic in the code to execute virtually any system or web-based command.

---

## Setup and Installation

### 1. Clone or Download the Repository

Place the project in your desired directory. For example, on Windows:

```bash
git clone https://github.com/jimmc414/voice_assistant.git
```

### 2. Install Python Dependencies

Ensure you have Python 3 installed. Install the required packages using:

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `pyaudio==0.2.13`
- `pvporcupine==3.0.5`
- `vosk==0.3.45`

### 3. Download the Necessary Models and API Key

#### Vosk Offline Model
- **What:** A 40MB model optimized for local speech recognition.  
- **Download:** [Vosk Models](https://alphacephei.com/vosk/models)  
- **Setup:** Download the 40MB model, unzip it, and place the folder in your project (e.g., `C:\python\voice_assistant\vosk-model\`).

#### Porcupine Hotword Model Files
- **API Key:**  
  Obtain a free API key from the [Picovoice Console](https://picovoice.ai/console/). This key is only necessary for downloading your custom trained wake word model.

- **Trained Hotword File (.ppn):**  
  Create and download your custom wake word file from the [Picovoice PPN Console](https://console.picovoice.ai/ppn). Save it (e.g., `hotword_en_windows_v3_0_0.ppn`) in the `porcupine` folder within your project.

- **Model Parameter File (.pv):**  
  Download the corresponding parameter file (e.g., `porcupine_params.pv`) from the same console and place it in the same directory as your `.ppn` file.

> **Note:** Ensure the file paths in `voice_assistant.py` for `PORCUPINE_KEYWORD_PATH`, `PORCUPINE_MODEL_PATH`, and `VOSK_MODEL_PATH` reflect the actual locations on your system.

### 4. Configure the Project

Open `voice_assistant.py` and update the configuration section:
- **API Key:** Replace `"insert api key here"` with your Picovoice API key.
- **Paths:** Confirm that the paths for the Porcupine `.ppn` and `.pv` files, as well as the Vosk model, are correct.
- **Command List:** The `POSSIBLE_COMMANDS` list defines the recognized commands. Modify or extend it as needed.

---

## Running the Voice Assistant

Run the main script from the command line:

```bash
python voice_assistant.py
```

When running, the system will:
1. Continuously listen for your custom hotword.
2. Emit a beep when the hotword is detected.
3. Listen for a command for a short duration.
4. Process and execute the corresponding action, such as launching an application or opening a webpage.

Press `Ctrl+C` to exit the application.

---

## Adding New Commands

To extend the assistant’s capabilities:

1. **Update the Command List:**  
   - Add new command phrases to the `POSSIBLE_COMMANDS` list in `voice_assistant.py`.

2. **Implement New Actions:**  
   - In the `process_command_text()` function, add a new conditional branch to map the recognized command text to your desired action. For example, to open a browser:

     ```python
     elif "open browser" in text:
         print("[Action] Opening default browser...")
         webbrowser.open("https://example.com")
     ```

3. **Test Your Changes:**  
   - Restart the assistant and verify that your new command is recognized and executed correctly.
