from flask import Flask, request, redirect, url_for
import google.generativeai as genai
import PIL.Image
import os
import sys
import subprocess
import time
from google.cloud import texttospeech
from dotenv import load_dotenv

load_dotenv()

API_KEY_GEMINI = os.getenv("GEMINI_KEY")

if not API_KEY_GEMINI:
    print("Error: The API_KEY_GEMINI key was not found in the .env file")
    sys.exit(1)
FILE_JSON_GOOGLE = "/home/ibmec/tcc/gen-lang-client.json"
FOLDER_UPLOAD = "/home/ibmec/tcc/uploads_web"

app = Flask(__name__)
if not os.path.exists(FOLDER_UPLOAD):
    os.makedirs(FOLDER_UPLOAD)

# Setting Gemini
try:
    genai.configure(api_key=API_KEY_GEMINI)
except Exception as e:
    print(f"Error setting Gemini (verify API Key): {e}")
    sys.exit(1)
model_gemini = genai.GenerativeModel('gemini-2.5-flash')

# Setting Google TTS
try:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = FILE_JSON_GOOGLE
    client_tts = texttospeech.TextToSpeechClient()
except Exception as e:
    print(f"Error setting Google TTS (verify JSON file): {e}")
    sys.exit(1)

def play_text(texto):
    # Use Google TTS to generate an MP3 and play it on the default audio device (Bluetooth headset)
    try:
        synthesis_input = texttospeech.SynthesisInput(text=texto)
        voice = texttospeech.VoiceSelectionParams(language_code="pt-BR", name="pt-BR-Wavenet-A")
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client_tts.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        # Save and play
        temp_audio = f"/tmp/tts_{int(time.time())}.mp3"
        with open(temp_audio, "wb") as out:
            out.write(response.audio_content)

        print("Playing audio...")
        subprocess.run(['mpg123', '-q', temp_audio], check=True)
        os.remove(temp_audio) # Cleans file
    except Exception as e:
        print(f"Error in the TTS or while playing audio (verify 'mpg123'): {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        if file:
            # Save received image (jpg, png, heic, mpo...)
            img_path = os.path.join(FOLDER_UPLOAD, f"raw_{int(time.time())}")
            file.save(img_path)
            print(f"Received image: {img_path}")

            try:
                # Converts the image if it is in a complex format (like MPO/Portrait Mode) to ensure compatibility with Gemini
                # Opens original image
                img_original = PIL.Image.open(img_path)

                # Converts to RGB (removes transparency, 3D layers, etc)
                img_rgb = img_original.convert('RGB')

                # Save it again as a clean standard JPG
                path_jpg_final = os.path.join(FOLDER_UPLOAD, f"upload_{int(time.time())}.jpg")
                img_rgb.save(path_jpg_final, format="JPEG")

                # Load the clean JPG to send to Gemini
                img_final = PIL.Image.open(path_jpg_final)

                response = model_gemini.generate_content(["Descreva esta imagem em uma frase curta para um deficiente visual. Caso seja uma página de livro, só me responda a transcrição do conteúdo aparente, nada além disso, se o conteúdo não estiver totalmente visível, avise de forma breve e não faça a transcrição. se for uma placa, identifique o direcionamento. Se for uma estação de metrô ou trêm, tente identificar o nome da estação também", img_final])
                ''' English version: Describe this image in a short sentence for a visually impaired person. If it is a book page, respond only with the transcription of the visible content;
                 if the content is not fully visible, inform that briefly and do not transcribe. If it is a sign, identify the direction. If it is a subway or
                 train station, try to identify the station name as well.'''

                description = response.text.strip()

                # "Plays" text (Google TTS)
                play_text(description)

                # Cleans file
                try:
                    os.remove(img_path)
                    os.remove(path_jpg_final)
                except:
                    pass

                return f"""
                <h1>Sucesso!</h1>
                <p><b>Descrição:</b> {description}</p>
                <a href='/'>Enviar outra imagem</a>
                """

                '''
                English version:
                <h1>Success!</h1>
                <p><b>Description:</b> {description}</p>
                <a href='/'>Send another image</a>
                '''
            except Exception as e:
                print(f"Error processing image: {e}")
                return f"Error processing image: {e}", 500

    return '''
    <!doctype html>
    <title>TCC - Descrição de Imagem</title>
    <h1>Enviar foto para análise</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=imagem accept="image/*">
      <br><br>
      <input type=submit value="Enviar e Descrever">
    </form>
    '''

    '''
    English version:
    <!doctype html>
    <title>TCC - Image Description</title>
    <h1>Send photo for analysis</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=imagem accept="image/*">
      <br><br>
      <input type=submit value="Send and Describe">
    </form>
    '''

if __name__ == '__main__':
    # Runs the server in the local network
    print("Starting Flask Server...")
    print("To access, open browser and type: http://192.168.1.42:5000")
    app.run(host='0.0.0.0', port=5000)
