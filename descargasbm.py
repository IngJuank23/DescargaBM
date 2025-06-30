from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
import yt_dlp
import os
import uuid
import random

app = Flask(__name__)
app.secret_key = "descargasbm_secreta"
DOWNLOAD_FOLDER = "downloads"
COUNTER_FILE = "contador.txt"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Función para leer el contador desde archivo
def leer_contador():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            return int(f.read())
    return 0

# Función para incrementar el contador
def incrementar_contador():
    count = leer_contador() + 1
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(count))

def descargar_video(url, formato='mp4'):
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s")

    opciones = {
        'format': 'bestaudio/best' if formato == 'mp3' else 'mp4',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt'
    }

    if formato == 'mp3':
        opciones['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return os.path.splitext(filename)[0] + ('.mp3' if formato == 'mp3' else '.mp4')

@app.route("/", methods=["GET", "POST"])
def index():
    mensaje_error = None
    contador = leer_contador()

    # Generar CAPTCHA
    if "captcha" not in session:
        a, b = random.randint(1, 10), random.randint(1, 10)
        session["captcha"] = {"a": a, "b": b}

    if request.method == "POST":
        url = request.form["url"]
        formato = request.form["formato"]
        respuesta = request.form["captcha"]
        a = session["captcha"]["a"]
        b = session["captcha"]["b"]

        # Validar CAPTCHA
        if respuesta != str(a + b):
            mensaje_error = "❌ Respuesta incorrecta en el CAPTCHA. Intenta de nuevo."
            session.pop("captcha", None)
            return render_template("index.html", error=mensaje_error, contador=contador)

        try:
            filepath = descargar_video(url, formato)
            filename = os.path.basename(filepath)
            incrementar_contador()
            session.pop("captcha", None)  # Reset CAPTCHA
            return redirect(url_for('descargar', filename=filename))
        except Exception as e:
            flash(f"Error al descargar: {e}")
            session.pop("captcha", None)

    return render_template("index.html", contador=contador, captcha=session.get("captcha"))

@app.route("/descargar/<filename>")
def descargar(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
