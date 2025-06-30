from flask import Flask, render_template, request, send_file, redirect, url_for, flash 
import yt_dlp
import os
import uuid

app = Flask(__name__)
app.secret_key = "descargasbm_secreta"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def descargar_video(url, formato='mp4'):
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s")

    opciones = {
        'format': 'bestaudio/best' if formato == 'mp3' else 'mp4',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True
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
    if request.method == "POST":
        url = request.form["url"]
        formato = request.form["formato"]
        try:
            filepath = descargar_video(url, formato)
            filename = os.path.basename(filepath)
            return redirect(url_for('descargar', filename=filename))
        except Exception as e:
            flash(f"Error al descargar: {e}")
            return redirect(url_for('index'))

    return render_template("index.html")

@app.route("/descargar/<filename>")
def descargar(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



