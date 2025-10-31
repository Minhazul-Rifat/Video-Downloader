import os
import sys
import threading
from tkinter import *
from tkinter import ttk
from yt_dlp import YoutubeDL
from PIL import Image, ImageTk

# ---------- Constants ---------- #
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 650
FONT_TITLE = ("Arial", 18, "bold")
FONT_LABEL = ("Arial", 12)
FONT_BUTTON = ("Arial", 12, "bold")
FONT_PROGRESS_TEXT = ("Arial", 10, "bold")
COLOR_BG = "#0F111A"
COLOR_FG = "#FFFFFF"
COLOR_BUTTON = "#1DB954"
COLOR_PROGRESS_TROUGH = "#D3D3D3"
COLOR_PROGRESS_FILL = "#1DB954"
COLOR_PROGRESS_TEXT = "#000000"
PROGRESS_BAR_WIDTH = 400
PROGRESS_BAR_HEIGHT = 30

# ---------- Helper Functions ---------- #


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# ---------- Download Function ---------- #


def download_video():
    url = link.get()
    if not url:
        return

    # Clear canvas
    progress_canvas_frame.pack(pady=(20, 10))
    progress_canvas.delete("all")

    # Draw trough (white background)
    progress_canvas.create_rectangle(
        0, 0, PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT, fill=COLOR_PROGRESS_TROUGH, width=0
    )

    # Green progress bar
    progress_bar_canvas_id = progress_canvas.create_rectangle(
        0, 0, 0, PROGRESS_BAR_HEIGHT, fill=COLOR_PROGRESS_FILL, width=0
    )

    # Percentage text
    progress_text_id = progress_canvas.create_text(
        PROGRESS_BAR_WIDTH / 2, PROGRESS_BAR_HEIGHT / 2, text="0.0%", fill=COLOR_PROGRESS_TEXT, font=FONT_PROGRESS_TEXT
    )

    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                percent = downloaded_bytes / total_bytes * 100
                bar_width = PROGRESS_BAR_WIDTH * percent / 100
                progress_canvas.coords(
                    progress_bar_canvas_id, 0, 0, bar_width, PROGRESS_BAR_HEIGHT)
                progress_canvas.itemconfigure(
                    progress_text_id, text=f"{percent:.1f}%")

    ffmpeg_path = resource_path("ffmpeg_bin")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'ffmpeg_location': ffmpeg_path,
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [progress_hook]
    }

    def run_download():
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    threading.Thread(target=run_download).start()


# ---------- UI Setup ---------- #
root = Tk()
root.title("YouTube Video Downloader")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.configure(bg=COLOR_BG)
root.resizable(False, False)

# Background Image
bg_image_path = resource_path("robot_bg.png")
if os.path.exists(bg_image_path):
    bg_image = Image.open(bg_image_path)
    bg_image = bg_image.resize((WINDOW_WIDTH, 300))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1)

# Logo
logo_image_path = resource_path("logo.png")
if os.path.exists(logo_image_path):
    logo_image = Image.open(logo_image_path)
    logo_image = logo_image.resize((80, 80))
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = Label(root, image=logo_photo, bg=COLOR_BG)
    logo_label.pack(pady=(310, 10))

# Entry field
link = StringVar()
entry = Entry(root, textvariable=link, font=FONT_LABEL, width=40, bd=2)
entry.pack(pady=10)

# Download Button
download_button = Button(root, text="Download", command=download_video,
                         font=FONT_BUTTON, bg=COLOR_BUTTON, fg="white", padx=10, pady=5)
download_button.pack(pady=10)

# Progress Canvas Frame
progress_canvas_frame = Frame(root, bg=COLOR_BG)
progress_canvas = Canvas(progress_canvas_frame, width=PROGRESS_BAR_WIDTH,
                         height=PROGRESS_BAR_HEIGHT, bg=COLOR_BG, highlightthickness=0)
progress_canvas.pack()

root.mainloop()
