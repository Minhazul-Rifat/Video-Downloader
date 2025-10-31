from flask import Flask, render_template, request, jsonify
from yt_dlp import YoutubeDL
import threading
import os

app = Flask(__name__)

progress = {
    "percent": 0,
    "speed": "0 KiB/s",
    "eta": 0,
    "status": "Idle",
    "error": None,
}

cancel_download = False
download_thread = None


def download(url):
    FFMPEG_PATH_RAILWAY = os.path.join(os.getcwd(), 'ffmpeg')
    global progress, cancel_download
    progress = {"percent": 0, "speed": "0 KiB/s",
                "eta": 0, "status": "Starting", "error": None}
    cancel_download = False

    def progress_hook(d):
        global progress, cancel_download
        if cancel_download:
            raise Exception("Download cancelled")

        if d["status"] == "downloading":
            downloaded_bytes = d.get("downloaded_bytes", 0)
            total_bytes = d.get("total_bytes") or d.get(
                "total_bytes_estimate", 1)
            percent = downloaded_bytes / total_bytes * 100 if total_bytes else 0
            progress["percent"] = round(percent, 2)
            speed = d.get("speed")
            if speed:
                progress["speed"] = f"{speed / 1024:.2f} KiB/s"
            else:
                progress["speed"] = "0 KiB/s"
            progress["eta"] = d.get("eta", 0)
            progress["status"] = "Downloading"
        elif d["status"] == "finished":
            progress["percent"] = 100
            progress["speed"] = "0 KiB/s"
            progress["eta"] = 0
            progress["status"] = "Finished"

    ydl_opts = {
        "progress_hooks": [progress_hook],
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "noplaylist": True,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        # "format": "bestvideo+bestaudio/best",
        # "ffmpeg_location": r"C:\Users\WHITE DEVIL\Desktop\pybot\YouTube Downloader\ffmpeg.exe",
        "ffmpeg_location": FFMPEG_PATH_RAILWAY,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        if str(e) == "Download cancelled":
            progress["status"] = "Cancelled"
        else:
            progress["status"] = "Error"
            progress["error"] = str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def start_download():
    global download_thread, cancel_download
    if download_thread and download_thread.is_alive():
        return jsonify({"status": "Download in progress"}), 400
    url = request.form.get("url")
    if not url:
        return jsonify({"status": "No URL provided"}), 400
    download_thread = threading.Thread(target=download, args=(url,))
    download_thread.start()
    cancel_download = False
    return jsonify({"status": "Started"})


@app.route("/progress")
def get_progress():
    return jsonify(progress)


@app.route("/cancel", methods=["POST"])
def cancel():
    global cancel_download
    cancel_download = True
    return jsonify({"status": "Cancelled"})


if __name__ == "__main__":
    import os
    if not os.path.exists("downloads"):
        os.mkdir("downloads")
    app.run(debug=True)
