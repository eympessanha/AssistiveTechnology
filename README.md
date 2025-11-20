# Assistive Technology - Smart Vision for the Visually Impaired

This repository contains the source code and configuration scripts for a Raspberry Pi-based assistive technology device. The project's goal is to increase the autonomy of visually impaired individuals by capturing images of the environment, processing them with Artificial Intelligence, and providing an audio description via bone conduction headphones.

## About the Project

The system operates in "headless" mode (without a monitor) and functions as a central server that receives images via Wi-Fi, generates contextual descriptions, and reproduces them as audio.

### Workflow:
1.  **Capture & Sending:** A client (ESP32 with camera, Smartphone, or PC) captures an image and sends it via Wi-Fi (HTTP POST) to the Flask server running on the Raspberry Pi.
2.  **Processing (AI):** The server receives the image and uses the **Google Gemini API** to generate a detailed and accessible textual description of the environment.
3.  **Voice Synthesis (TTS):** The generated text is converted into natural audio using the **Google Cloud Text-to-Speech API**.
4.  **Audio Output:** The audio file is automatically played on the Bluetooth headset connected to the Raspberry Pi.

---

## Repository Structure

```text
AssistiveTechnology/
├── boot.sh                 # Initialization script (Manages Bluetooth + Flask)
├── tcc_gemini.service      # Systemd service file (Boot automation)
└── image-captioning/       # Source code of the main application
    ├── app.py              # Flask Server, Gemini Logic, and TTS
    ├── requirements.txt    # Python dependencies
    └── .gitignore          # Rules to ignore sensitive files (.env, json)
```

## File Description

### 1. `image-captioning/app.py`
It is the "brain" of the project. This Python script:
* Starts a Flask Web Server on port `5000`.
* Accepts image uploads on the `/` route (web interface) and via POST.
* Converts images to ensure compatibility (e.g., removes MPO layers from Android photos).
* Communicates with **Google Gemini** to describe the scene.
* Communicates with **Google Cloud TTS** to generate the MP3.
* Plays the audio using the system's `mpg123` player.

### 2. `boot.sh`
Shell script (bash) responsible for orchestration at startup:
* Waits for the sound system to load.
* Attempts to automatically reconnect to the specific Bluetooth headset (retry loop).
* Activates the Python virtual environment.
* Starts `app.py`.

### 3. `tcc_gemini.service`
Systemd configuration file. It ensures that `boot.sh` is executed automatically as soon as the Raspberry Pi is powered on, running in the background as a system service.

---

## Installation and Configuration

### System Prerequisites
On the Raspberry Pi, install the necessary packages for audio and playback:
```bash
sudo apt update
sudo apt install mpg123 pulseaudio pulseaudio-module-bluetooth
```

### Project Configuration
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/eympessanha/AssistiveTechnology.git](https://github.com/eympessanha/AssistiveTechnology.git)
    cd AssistiveTechnology/image-captioning
    ```

2.  **Create the Virtual Environment and Install Dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Credential Configuration (Security):**
    *These files are not in the repository for security reasons. You must create them manually in the `image-captioning` folder.*

    * Create a `.env` file with your Gemini key:
        ```text
        GEMINI_KEY=your_api_key_here
        ```
    * Place the Google Cloud credentials JSON file (for TTS) in the folder and rename it to `gen-lang-client.json` (or adjust the name in `app.py`).

---

## Automation (Headless Mode)

For the project to run by itself when the board is powered on:

1.  **Edit `boot.sh`:**
    Open the file and place your Bluetooth headset's **MAC Address** in the indicated variable.

2.  **Move and Enable the Service:**
    ```bash
    # Copy the service file to the system
    sudo cp tcc_gemini.service /etc/systemd/system/

    # Reload the daemon
    sudo systemctl daemon-reload

    # Enable the service on boot
    sudo systemctl enable tcc_gemini.service

    # Start now (to test)
    sudo systemctl start tcc_gemini.service
    ```

3.  **Configure User (Linger):**
    To ensure audio works without login:
    ```bash
    loginctl enable-linger ibmec
    ```

---

## How to Send Images

With the server running, you can send images from any device on the same Wi-Fi network.

**Via Browser:**
Access `http://RPI_IP:5000`

**Via Script (Python/ESP32):**
Make a `POST` request to `http://RPI_IP:5000/` sending the file in the `image` field.

---

## Security Notes

* The `.gitignore` file is configured to prevent your API keys (`.env` and `*.json`) from being sent to GitHub. **Never remove these rules.**



