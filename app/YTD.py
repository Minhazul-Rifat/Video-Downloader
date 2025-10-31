from tkinter import *
import threading
import os
import sys
from yt_dlp import YoutubeDL
from PIL import Image, ImageTk
import re

# Globals
should_stop = False
progress_bar_canvas_id = None
progress_text_id = None
global_logo_photo = None
PROGRESS_BAR_WIDTH = 520
PROGRESS_BAR_HEIGHT = 30

# Root window setup
root = Tk()
root.geometry("576x768")
root.title("Video Downloader")
root.resizable(0, 0)
COLOR_BG = "#000000"
root.configure(bg=COLOR_BG)

# Fonts & colors
FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_LABEL = ("Segoe UI", 14)
FONT_BUTTON = ("Segoe UI", 14, "bold")
FONT_STATUS = ("Segoe UI", 13)
FONT_PROGRESS_TEXT = ("Segoe UI", 12, "bold")

COLOR_TEXT_DARK = "#000000"
COLOR_TEXT_LIGHT = "#eeeeee"
COLOR_ACCENT = "#00aaff"
COLOR_BUTTON_TEXT_DEFAULT = "#000000"
COLOR_BUTTON_TEXT_HOVER = "#00aaff"
COLOR_BOX_BG = "#ffffff"
COLOR_BOX_HOVER = "#e0e0e0"
COLOR_SHADOW = COLOR_BG
COLOR_ENTRY_PLACEHOLDER = "#cccccc"

COLOR_PROGRESS_TROUGH = "#ffffff"
COLOR_PROGRESS_FILL = "#00cc99"
COLOR_PROGRESS_TEXT = "#000000"

link = StringVar()


def strip_ansi(text):
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text)


def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "ffmpeg.exe")
    else:
        return os.path.abspath("ffmpeg.exe")


def hook(d):
    global should_stop, progress_bar_canvas_id, progress_text_id
    if should_stop:
        raise Exception("Download cancelled by user.")

    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total and progress_canvas.winfo_exists():
            percent = downloaded / total * 100
            fill_width = PROGRESS_BAR_WIDTH * (percent / 100)
            progress_canvas.coords(
                progress_bar_canvas_id, 0, 0, fill_width, PROGRESS_BAR_HEIGHT)
            progress_canvas.itemconfigure(
                progress_text_id, text=f"{percent:.1f}%")

            eta = strip_ansi(d.get('_eta_str', '?'))
            speed = strip_ansi(d.get('_speed_str', '?'))
            status_label.config(
                text=f"Remain: {eta}    Speed: {speed}", fg=COLOR_ACCENT)
            root.update_idletasks()

    elif d['status'] == 'finished':
        status_label.config(text="✅ Download completed!", fg=COLOR_ACCENT)
        progress_canvas.coords(progress_bar_canvas_id, 0,
                               0, PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT)
        progress_canvas.itemconfigure(progress_text_id, text="100.0%")
    elif d['status'] == 'error':
        status_label.config(
            text=f"⛔ Download error: {d.get('error', 'Unknown error')}", fg="red")


def download_video():
    global should_stop, progress_bar_canvas_id, progress_text_id
    url = link.get().strip()
    if not url or url == "Paste your link here":
        status_label.config(text="❌ Please enter a YouTube URL", fg="red")
        return

    download_button_wrapper.canvas.itemconfigure(
        download_button_wrapper.main_shape_id, fill=COLOR_BOX_HOVER)
    download_button.config(fg=COLOR_BUTTON_TEXT_HOVER)

    cancel_button_wrapper.canvas.itemconfigure(
        cancel_button_wrapper.main_shape_id, fill=COLOR_BOX_BG)
    cancel_button.config(fg=COLOR_BUTTON_TEXT_DEFAULT)

    download_button.config(state=DISABLED)
    cancel_button.config(state=NORMAL)
    status_label.config(text="Starting download...", fg=COLOR_ACCENT)
    should_stop = False

    progress_canvas_frame.pack(pady=(20, 10))
    progress_canvas.delete("all")

    # Draw trough (white background) - simple rectangle
    progress_canvas.create_rectangle(
        0, 0, PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT, fill=COLOR_PROGRESS_TROUGH, width=0)

    # Draw initial green fill (width 0) - simple rectangle
    progress_bar_canvas_id = progress_canvas.create_rectangle(
        0, 0, 0, PROGRESS_BAR_HEIGHT, fill=COLOR_PROGRESS_FILL, width=0)

    # Progress text in center
    progress_text_id = progress_canvas.create_text(
        PROGRESS_BAR_WIDTH/2, PROGRESS_BAR_HEIGHT/2, text="0.0%", fill=COLOR_PROGRESS_TEXT, font=FONT_PROGRESS_TEXT)

    def run_dl():
        ffmpeg_path = get_ffmpeg_path()
        opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'ffmpeg_location': ffmpeg_path,
            'progress_hooks': [hook],
            'outtmpl': '%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4'
        }
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
        except Exception as e:
            status_label.config(
                text=f"⛔ Download stopped.\n{str(e)}", fg="red")
        finally:
            download_button.config(state=NORMAL)
            cancel_button.config(state=DISABLED)
            download_button_wrapper.canvas.itemconfigure(
                download_button_wrapper.main_shape_id, fill=COLOR_BOX_BG)
            download_button.config(fg=COLOR_BUTTON_TEXT_DEFAULT)
            cancel_button_wrapper.canvas.itemconfigure(
                cancel_button_wrapper.main_shape_id, fill=COLOR_BOX_BG)
            cancel_button.config(fg=COLOR_BUTTON_TEXT_DEFAULT)

    threading.Thread(target=run_dl, daemon=True).start()


def cancel_download():
    global should_stop
    should_stop = True
    cancel_button.config(state=DISABLED)
    download_button.config(state=NORMAL)
    status_label.config(text="Cancelling download...", fg=COLOR_ACCENT)
    if progress_text_id and progress_canvas.winfo_exists():
        progress_canvas.itemconfigure(progress_text_id, text="")
    if progress_bar_canvas_id and progress_canvas.winfo_exists():
        progress_canvas.coords(progress_bar_canvas_id, 0,
                               0, 0, PROGRESS_BAR_HEIGHT)
    # Reset button colors
    download_button_wrapper.canvas.itemconfigure(
        download_button_wrapper.main_shape_id, fill=COLOR_BOX_BG)
    download_button.config(fg=COLOR_BUTTON_TEXT_DEFAULT)
    cancel_button_wrapper.canvas.itemconfigure(
        cancel_button_wrapper.main_shape_id, fill=COLOR_BOX_BG)
    cancel_button.config(fg=COLOR_BUTTON_TEXT_DEFAULT)


def on_entry_click(event):
    if link.get() == "Paste your link here":
        link.set("")
        link_entry.config(fg=COLOR_TEXT_DARK)


def on_focusout(event):
    if not link.get():
        link.set("Paste your link here")
        link_entry.config(fg=COLOR_ENTRY_PLACEHOLDER)


class RoundedWidget:
    def __init__(self, master, width, height, radius, shadow_offset, bg_color, shadow_color, **kwargs):
        from math import cos, sin, pi
        self.canvas = Canvas(master, width=width + shadow_offset, height=height + shadow_offset,
                             bg=master['bg'], highlightthickness=0, bd=0)

        def create_rounded_rect(cnv, x1, y1, x2, y2, r, **opts):
            points = [
                x1+r, y1,
                x2-r, y1,
                x2, y1,
                x2, y1+r,
                x2, y2-r,
                x2, y2,
                x2-r, y2,
                x1+r, y2,
                x1, y2,
                x1, y2-r,
                x1, y1+r,
                x1, y1
            ]
            return cnv.create_polygon(points, smooth=True, **opts)
        self.shadow_id = create_rounded_rect(self.canvas,
                                             shadow_offset, shadow_offset,
                                             width + shadow_offset, height + shadow_offset,
                                             radius, fill=shadow_color, outline="")
        self.main_shape_id = create_rounded_rect(self.canvas,
                                                 0, 0, width, height,
                                                 radius, fill=bg_color, outline="", **kwargs)
        self.widget = None
        self.width = width
        self.height = height
        self.shadow_offset = shadow_offset

    def place_widget(self, widget_instance, x=None, y=None, anchor=None, **kwargs):
        self.widget = widget_instance
        final_x = x if x is not None else self.shadow_offset
        final_y = y if y is not None else 0
        final_anchor = anchor if anchor is not None else "nw"

        self.canvas.create_window(final_x,
                                  final_y,
                                  window=widget_instance,
                                  anchor=final_anchor,
                                  width=self.width,
                                  height=self.height,
                                  **kwargs)
        widget_instance.config(
            bg=self.canvas.itemcget(self.main_shape_id, "fill"))

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

    def grid(self, **kwargs):
        self.canvas.grid(**kwargs)

    def bind_hover_effects(self, widget_instance, default_bg, hover_bg, default_fg, hover_fg):
        if isinstance(widget_instance, Button):
            widget_instance.bind("<Enter>", lambda e: (
                self.canvas.itemconfigure(self.main_shape_id, fill=hover_bg),
                widget_instance.config(fg=hover_fg)
            ))
            widget_instance.bind("<Leave>", lambda e: (
                self.canvas.itemconfigure(self.main_shape_id, fill=default_bg),
                widget_instance.config(fg=default_fg)
            ))
            widget_instance.config(
                activebackground=hover_bg, activeforeground=hover_fg)
        else:
            widget_instance.bind("<Enter>", lambda e: self.canvas.itemconfigure(
                self.main_shape_id, fill=hover_bg))
            widget_instance.bind("<Leave>", lambda e: self.canvas.itemconfigure(
                self.main_shape_id, fill=default_bg))

        self.canvas.tag_bind(self.main_shape_id, "<Enter>", lambda e: self.canvas.itemconfigure(
            self.main_shape_id, "fill", hover_bg))
        self.canvas.tag_bind(self.main_shape_id, "<Leave>", lambda e: self.canvas.itemconfigure(
            self.main_shape_id, "fill", default_bg))


# Background image (robot_bg.png)
try:
    if getattr(sys, 'frozen', False):
        image_path = os.path.join(sys._MEIPASS, "robot_bg.png")
    else:
        image_path = "robot_bg.png"
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((576, 768), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = Label(root, image=bg_photo, bg=COLOR_BG)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception:
    bg_label = Label(root, bg=COLOR_BG)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Title/logo wrapper
title_width = 400
title_height = 100
title_radius = 25
shadow_offset = 0
title_wrapper = RoundedWidget(root, title_width, title_height, title_radius,
                              shadow_offset, COLOR_BOX_BG, COLOR_SHADOW)
title_wrapper.pack(pady=(30, 20))

try:
    if getattr(sys, 'frozen', False):
        logo_image_path = os.path.join(sys._MEIPASS, "logo.png")
    else:
        logo_image_path = "logo.png"
    logo_image = Image.open(logo_image_path)
    logo_image.thumbnail(
        (title_width - 20, title_height - 20), Image.Resampling.LANCZOS)
    global_logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = Label(title_wrapper.canvas, image=global_logo_photo,
                       bg=COLOR_BOX_BG, relief=FLAT, bd=0, highlightthickness=0)
    logo_label.image = global_logo_photo
    title_wrapper.place_widget(
        logo_label, x=title_width/2, y=title_height/2, anchor="center")
except Exception:
    title_label = Label(title_wrapper.canvas, text="Video Downloader", font=FONT_TITLE,
                        fg=COLOR_ACCENT, bg=COLOR_BOX_BG, relief=FLAT, bd=0, highlightthickness=0)
    title_wrapper.place_widget(
        title_label, x=title_width/2, y=title_height/2, anchor="center")

# Entry wrapper
entry_width = 500
entry_height = 40
entry_radius = 20
shadow_offset = 0
entry_wrapper = RoundedWidget(root, entry_width, entry_height, entry_radius,
                              shadow_offset, COLOR_BOX_BG, COLOR_SHADOW)
entry_wrapper.pack(pady=10)

link_entry = Entry(entry_wrapper.canvas, textvariable=link, font=FONT_LABEL,
                   fg=COLOR_ENTRY_PLACEHOLDER, insertbackground=COLOR_TEXT_DARK,
                   relief=FLAT, bd=0, highlightthickness=0)
entry_wrapper.place_widget(link_entry)
link.set("Paste your link here")
link_entry.bind("<FocusIn>", on_entry_click)
link_entry.bind("<FocusOut>", on_focusout)

# Buttons frame
buttons_frame = Frame(root, bg=COLOR_BG)
buttons_frame.pack(pady=15)

button_width = 150
button_height = 40
button_radius = 20
shadow_offset = 0

download_button_wrapper = RoundedWidget(buttons_frame, button_width, button_height, button_radius,
                                        shadow_offset, COLOR_BOX_BG, COLOR_SHADOW)
download_button_wrapper.grid(row=0, column=0, padx=10)

download_button = Button(download_button_wrapper.canvas, text="Download", font=FONT_BUTTON,
                         fg=COLOR_BUTTON_TEXT_DEFAULT, relief=FLAT, bd=0, highlightthickness=0,
                         command=download_video)
download_button_wrapper.place_widget(download_button)
download_button_wrapper.bind_hover_effects(download_button,
                                           COLOR_BOX_BG, COLOR_BOX_HOVER,
                                           COLOR_BUTTON_TEXT_DEFAULT, COLOR_BUTTON_TEXT_HOVER)

cancel_button_wrapper = RoundedWidget(buttons_frame, button_width, button_height, button_radius,
                                      shadow_offset, COLOR_BOX_BG, COLOR_SHADOW)
cancel_button_wrapper.grid(row=0, column=1, padx=10)

cancel_button = Button(cancel_button_wrapper.canvas, text="Cancel", font=FONT_BUTTON,
                       fg=COLOR_BUTTON_TEXT_DEFAULT, relief=FLAT, bd=0, highlightthickness=0,
                       command=cancel_download, state=DISABLED)
cancel_button_wrapper.place_widget(cancel_button)
cancel_button_wrapper.bind_hover_effects(cancel_button,
                                         COLOR_BOX_BG, COLOR_BOX_HOVER,
                                         COLOR_BUTTON_TEXT_DEFAULT, COLOR_BUTTON_TEXT_HOVER)

# Progress bar canvas
progress_canvas_frame = Frame(root, bg=COLOR_BG)
progress_canvas = Canvas(progress_canvas_frame, width=PROGRESS_BAR_WIDTH, height=PROGRESS_BAR_HEIGHT,
                         bg=COLOR_PROGRESS_TROUGH, highlightthickness=0, bd=0)
progress_canvas.pack()
progress_canvas_frame.pack_forget()  # Hide initially

# Status label
status_label = Label(root, text="", font=FONT_STATUS, bg=COLOR_BG,
                     fg=COLOR_ACCENT, wraplength=500, justify=CENTER)
status_label.pack(pady=(20, 10))

root.mainloop()
