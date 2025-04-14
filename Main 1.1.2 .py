import cv2
import os
import csv
import time
import threading
import re
from datetime import datetime
import pytz
import tkinter as tk
from tkinter import scrolledtext, filedialog
from PIL import Image, ImageTk
import easyocr
from ultralytics import YOLO
import pandas as pd

# === Setup Paths ===
save_directory = r"C:\Users\siddh\OneDrive\Desktop\License Plate Detection\Captured License Plate"
os.makedirs(save_directory, exist_ok=True)
log_file = "vehicle_log.csv"
if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp (IST)", "Vehicle Type", "License Plate", "Direction", "Image Path"])

vehicle_model = YOLO("yolov8n.pt")
reader = easyocr.Reader(['en'])
ALLOWED_CLASSES = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']

THEME = {
    "light": {"bg": "#f5f5f5", "fg": "#1e1e1e", "log_bg": "#ffffff", "btn": "#1e90ff"},
    "dark": {"bg": "#2d2d2d", "fg": "#ffffff", "log_bg": "#3c3c3c", "btn": "#007acc"}
}
current_theme = "light"

root = tk.Tk()
root.title("🚗 Vehicle Detection Dashboard")
root.geometry("1350x780")

def apply_theme():
    theme = THEME[current_theme]
    root.configure(bg=theme["bg"])
    title.config(bg=theme["bg"], fg=theme["fg"])
    video_label.config(bg=theme["bg"])
    left_frame.config(bg=theme["bg"])
    right_frame.config(bg=theme["log_bg"])

    def safe_config(widget, **kwargs):
        for key in list(kwargs.keys()):
            try:
                widget.config(**{key: kwargs[key]})
            except tk.TclError:
                pass

    widgets = [
        search_label, search_entry, search_frame, export_btn, search_btn,
        clear_btn, image_frame, info_frame, vehicle_type_label,
        plate_text_label, direction_label, log_text
    ]
    for widget in widgets:
        safe_config(widget, bg=theme["log_bg"], fg=theme["fg"])
    safe_config(canvas, bg=theme["log_bg"])

def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()

# === Top Title ===
title = tk.Label(root, text="Live Vehicle Detection & Recognition System", font=("Helvetica", 18, "bold"))
title.grid(row=0, column=0, columnspan=2, pady=10)

theme_btn = tk.Button(root, text="Toggle Theme 🌗", command=toggle_theme, font=("Arial", 10))
theme_btn.grid(row=0, column=2, padx=10)

left_frame = tk.Frame(root)
left_frame.grid(row=1, column=0, sticky="nw")

right_frame = tk.LabelFrame(root, text="Recent Logs", font=("Arial", 12, "bold"), padx=10, pady=10)
right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")

video_label = tk.Label(left_frame)
video_label.pack()

# === Time + Minimap Canvas ===
canvas = tk.Canvas(right_frame, width=400, height=150)
canvas.pack(pady=(5, 15))

vehicle_icon = canvas.create_rectangle(10, 60, 30, 80, fill="blue")
direction = "right"

def update_minimap():
    global direction
    x1, y1, x2, y2 = canvas.coords(vehicle_icon)
    if direction == "right" and x2 < 400:
        canvas.move(vehicle_icon, 5, 0)
    elif direction == "right":
        direction = "left"
    elif direction == "left" and x1 > 0:
        canvas.move(vehicle_icon, -5, 0)
    else:
        direction = "right"
    root.after(100, update_minimap)

# === Log Panel ===
search_frame = tk.Frame(right_frame)
search_frame.pack()
search_label = tk.Label(search_frame, text="Search Plate:")
search_label.pack(side=tk.LEFT)

search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT)

def search_log():
    plate = search_entry.get().strip().upper()
    with open(log_file, "r") as f:
        reader = csv.reader(f)
        next(reader)
        results = [row for row in reader if plate in row[2].upper()]
        log_text.delete("1.0", tk.END)
        for row in results:
            log_text.insert(tk.END, " | ".join(row) + "\n")

search_btn = tk.Button(search_frame, text="Search", command=search_log)
search_btn.pack(side=tk.LEFT)

clear_btn = tk.Button(search_frame, text="Clear", command=lambda: log_text.delete("1.0", tk.END))
clear_btn.pack(side=tk.LEFT)

log_text = scrolledtext.ScrolledText(right_frame, height=10, width=60)
log_text.pack()

image_frame = tk.Frame(right_frame)
image_frame.pack(pady=5)
plate_image_label = tk.Label(image_frame)
plate_image_label.pack()

info_frame = tk.Frame(right_frame)
info_frame.pack(pady=5)
vehicle_type_label = tk.Label(info_frame, text="Vehicle Type:")
vehicle_type_label.pack()
plate_text_label = tk.Label(info_frame, text="License Plate:")
plate_text_label.pack()
direction_label = tk.Label(info_frame, text="Direction:")
direction_label.pack()

def export_log():
    df = pd.read_csv(log_file)
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if file_path:
        df.to_excel(file_path, index=False)

export_btn = tk.Button(right_frame, text="Export to Excel", command=export_log)
export_btn.pack(pady=5)

def is_valid_plate(plate):
    return re.match(r"^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$", plate)

def log_detection(vehicle_type, plate_text, direction, plate_image):
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    filename = f"{plate_text}_{timestamp.replace(':','-')}.png"
    image_path = os.path.join(save_directory, filename)
    cv2.imwrite(image_path, plate_image)
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, vehicle_type, plate_text, direction, image_path])
    log_text.insert(tk.END, f"{timestamp} | {vehicle_type} | {plate_text} | {direction} | Saved\n")
    img = Image.open(image_path).resize((150, 50))
    img = ImageTk.PhotoImage(img)
    plate_image_label.configure(image=img)
    plate_image_label.image = img
    vehicle_type_label.config(text=f"Vehicle Type: {vehicle_type}")
    plate_text_label.config(text=f"License Plate: {plate_text}")
    direction_label.config(text=f"Direction: {direction}")

def detect_vehicles():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = vehicle_model(frame)
        boxes = results[0].boxes
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = vehicle_model.names[cls]
            if label not in ALLOWED_CLASSES:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            vehicle_crop = frame[y1:y2, x1:x2]
            plate_result = reader.readtext(vehicle_crop)
            for (bbox, text, conf) in plate_result:
                plate_text = text.upper().replace(" ", "")
                if is_valid_plate(plate_text):
                    log_detection(label, plate_text, direction, vehicle_crop)
        now = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, now, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    cap.release()
    cv2.destroyAllWindows()

# Start everything
apply_theme()
update_minimap()
threading.Thread(target=detect_vehicles, daemon=True).start()
root.mainloop()
