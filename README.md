# 🚗 Live Vehicle Detection & License Plate Recognition System

This is a real-time vehicle detection and license plate recognition system using YOLOv8, EasyOCR, and a GUI built with Tkinter. The system can detect vehicles from a webcam feed, recognize their license plates, log entries/exits with timestamps, and display/search/export the logs.

---

## 🔧 Features

- 🧠 **YOLOv8-Based Vehicle Detection**
- 🪪 **License Plate Recognition using EasyOCR**
- ↔️ **Entry/Exit Detection (In/Out)**
- 📝 **CSV Logging with Timestamp & Image Path**
- 🔍 **Searchable Log Viewer**
- 📤 **Export Logs to Excel**
- 🖼️ **Live Feed & Latest Detection Display**
- ⚙️ **Threaded Operation for Smooth GUI Performance**

---

## 📁 File Structure

```
├── Captured License Plate/     # Folder to save cropped images of detected vehicles
├── vehicle_log.csv             # Auto-generated log file with detection data
├── Main 1.1 Updated.py         # Main script for running the application
```

---

## 📦 Requirements

Install the following Python packages before running:

```bash
pip install opencv-python-headless easyocr ultralytics pandas pillow pytz
```

Note: Also ensure `tkinter` is installed (included by default in most Python distributions).

---

## ▶️ How to Run

1. Clone this repository:

```bash
git clone https://github.com/yourusername/vehicle-detection-recognition.git
cd vehicle-detection-recognition
```

2. Run the Python script:

```bash
python "Main 1.1 Updated.py"
```

3. The application will:
   - Open a GUI window.
   - Start the webcam.
   - Detect vehicles and extract license plates.
   - Log entries in `vehicle_log.csv` and save images in `Captured License Plate/`.

---

## 📋 Output Format

Each detection is logged with:

- `Timestamp (IST)`
- `Vehicle Type`
- `License Plate`
- `Direction` (In/Out)
- `Image Path`

---

## 📤 Export Logs

You can export detection logs to an Excel `.xlsx` file using the **Export Logs** button in the GUI.

---

## 🛠️ Customization

- Change the list of detectable vehicle types via `ALLOWED_CLASSES`.
- Modify detection thresholds or OCR confidence in the `detect_license_plate` function.
- Adjust UI layout in the Tkinter section as per your needs.

---

## 🚀 Future Improvements

- Improved OCR for angled or low-quality license plates
- Direction detection using multi-frame analysis
- Web-based interface using Flask or Django
- Vehicle count analytics

---

## 📸 Demo

*Coming soon: GIF or video preview of the system in action.*

---

## 📝 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

---

## 🙌 Acknowledgements

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- Python Community

---

## 👨‍💻 Author

**Your Name** – [siddhantyadav77](https://github.com/siddhantyadav77)
```
