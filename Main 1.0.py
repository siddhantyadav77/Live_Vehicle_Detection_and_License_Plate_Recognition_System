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

# === Paths & Setup ===
save_directory = r"C:\Users\siddh\OneDrive\Desktop\License Plate Detection\Captured License Plate"
os.makedirs(save_directory, exist_ok=True)
log_file = "vehicle_log.csv"
if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp (IST)", "Vehicle Type", "License Plate", "Image Path"])

# === Load Models ===
vehicle_model = YOLO("yolov8n.pt")
reader = easyocr.Reader(['en'])
ALLOWED_CLASSES = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']

# === GUI Setup ===
root = tk.Tk()
root.title("\ud83d\ude97 Vehicle Detection Dashboard")
root.geometry("1220x720")
root.configure(bg="#f5f5f5")

title = tk.Label(root, text="Live Vehicle Detection & Recognition System", font=("Helvetica", 18, "bold"), bg="#f5f5f5", fg="#1e1e1e")
title.grid(row=0, column=0, columnspan=2, pady=10)

# Left Panel
left_frame = tk.Frame(root, bg="#f5f5f5")
left_frame.grid(row=1, column=0, sticky="nw")

# Right Panel (Log Viewer)
right_frame = tk.LabelFrame(root, text="Recent Logs", font=("Arial", 12, "bold"), bg="#ffffff", padx=10, pady=10)
right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")

search_frame = tk.Frame(right_frame, bg="#ffffff")
search_frame.pack(pady=(0, 10))

search_label = tk.Label(search_frame, text="Search Logs:", font=("Arial", 10), bg="#ffffff")
search_label.pack(side="left", padx=(0, 5))

search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side="left", padx=5)

def search_logs():
    query = search_entry.get().lower()
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
            filtered = [line for line in lines if query in line.lower()]
            if not filtered:
                filtered = ["No results found.\n"]
        log_text.configure(state='normal')
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, f"{'Timestamp':<22} | {'Vehicle Type':<12} | {'License Plate':<12}\n")
        log_text.insert(tk.END, "-" * 55 + "\n")
        for entry in filtered[1:]:
            fields = entry.strip().split(',')
            if len(fields) >= 3:
                log_text.insert(tk.END, f"{fields[0]:<22} | {fields[1]:<12} | {fields[2]:<12}\n")
        log_text.configure(state='disabled')
    except Exception as e:
        print("Search error:", e)

def clear_search():
    search_entry.delete(0, tk.END)
    update_log_display()

def export_logs():
    try:
        export_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if export_path:
            df = pd.read_csv(log_file)
            df.to_excel(export_path, index=False)
            print(f"Logs exported to: {export_path}")
    except Exception as e:
        print("Export error:", e)

search_btn = tk.Button(search_frame, text="Search", command=search_logs, font=("Arial", 9), bg="#1e90ff", fg="white")
search_btn.pack(side="left", padx=5)

clear_btn = tk.Button(search_frame, text="Clear", command=clear_search, font=("Arial", 9), bg="#aaaaaa")
clear_btn.pack(side="left", padx=5)

export_btn = tk.Button(search_frame, text="Export Logs", command=export_logs, font=("Arial", 9), bg="#28a745", fg="white")
export_btn.pack(side="left", padx=5)

log_text = scrolledtext.ScrolledText(right_frame, width=60, height=40, font=("Courier", 10))
log_text.pack()
log_text.configure(state='disabled')

# Live Video Feed
video_label = tk.Label(left_frame, bg="#f5f5f5")
video_label.grid(row=0, column=0, padx=10, pady=10)

# Last captured image
image_frame = tk.LabelFrame(left_frame, text="Last Detected Vehicle", font=("Arial", 12, "bold"), bg="#ffffff", padx=10, pady=10)
image_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")
image_label = tk.Label(image_frame)
image_label.pack()

# Vehicle Details
info_frame = tk.LabelFrame(left_frame, text="Detection Info", font=("Arial", 12, "bold"), bg="#ffffff", padx=10, pady=10)
info_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")

vehicle_type_label = tk.Label(info_frame, text="Vehicle Type: ", font=("Arial", 14), bg="#ffffff")
vehicle_type_label.pack(anchor="w", pady=5)

plate_text_label = tk.Label(info_frame, text="License Plate: ", font=("Arial", 14), bg="#ffffff")
plate_text_label.pack(anchor="w", pady=5)

# === Global Variables ===
last_plate = "Unknown"
last_vehicle_type = "Unknown"
last_image_path = None

def clean_license_plate(text):
    return re.sub(r'[^A-Za-z0-9]', '', text)

def detect_license_plate(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    results = reader.readtext(gray)
    for (bbox, text, prob) in results:
        if prob > 0.5:
            return clean_license_plate(text)
    return "Unknown"

def detect_and_stream():
    global last_plate, last_vehicle_type, last_image_path
    cap = cv2.VideoCapture(0)
    ist = pytz.timezone('Asia/Kolkata')

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        results = vehicle_model(frame)
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                vehicle_type = result.names[cls_id]

                if vehicle_type in ALLOWED_CLASSES:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    vehicle_roi = frame[y1:y2, x1:x2]

                    license_plate = detect_license_plate(vehicle_roi)

                    timestamp = datetime.now(ist).strftime("%Y%m%d_%H%M%S")
                    image_filename = f"{timestamp}_{license_plate}.jpg"
                    image_path = os.path.join(save_directory, image_filename)
                    cv2.imwrite(image_path, vehicle_roi)

                    with open(log_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S"),
                                         vehicle_type, license_plate, image_path])

                    last_plate = license_plate
                    last_vehicle_type = vehicle_type
                    last_image_path = image_path

                    break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb).resize((640, 400))
        imgtk = ImageTk.PhotoImage(pil_img)
        video_label.imgtk = imgtk
        video_label.config(image=imgtk)

        time.sleep(0.03)

    cap.release()

def update_last_captured():
    global last_image_path, last_plate, last_vehicle_type
    if last_image_path and os.path.exists(last_image_path):
        img = Image.open(last_image_path).resize((300, 200))
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.image = img_tk
        plate_text_label.config(text=f"License Plate: {last_plate}")
        vehicle_type_label.config(text=f"Vehicle Type: {last_vehicle_type}")
    root.after(3000, update_last_captured)

def update_log_display():
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
            last_entries = lines[-20:] if len(lines) > 20 else lines
        log_text.configure(state='normal')
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, f"{'Timestamp':<22} | {'Vehicle Type':<12} | {'License Plate':<12}\n")
        log_text.insert(tk.END, "-" * 55 + "\n")
        for entry in last_entries[1:]:
            fields = entry.strip().split(',')
            if len(fields) >= 3:
                log_text.insert(tk.END, f"{fields[0]:<22} | {fields[1]:<12} | {fields[2]:<12}\n")
        log_text.configure(state='disabled')
    except Exception as e:
        print("Log read error:", e)
    root.after(5000, update_log_display)

threading.Thread(target=detect_and_stream, daemon=True).start()
update_last_captured()
update_log_display()
root.mainloop()
