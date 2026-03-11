import cv2
import time
import numpy as np
from ultralytics import YOLO
import tkinter as tk 
from tkinter import messagebox


# CONFIG

MODEL_PATH = "best.pt"       
CONF_THRESHOLD = 0.7          # confidence to consider phone
PHONE_STREAK_REQUIRED = 12    # consecutive frames to count phone distraction
MIN_TIME = 10                 # minutes
MAX_TIME = 420                # 7 hours


# GET STUDY TIME

def get_study_time():
    root = tk.Tk()
    root.title("Study Time Setup")
    tk.Label(root, text="Enter study time (10 - 420 minutes)").pack()
    entry = tk.Entry(root)
    entry.pack()

    def submit():
        try:
            mins = int(entry.get())
            if mins < MIN_TIME or mins > MAX_TIME:
                messagebox.showerror("Error", "Time must be between 10 and 420 minutes.")
            else:
                root.study_time = mins * 60
                root.destroy()
        except:
            messagebox.showerror("Error", "Enter valid number.")

    tk.Button(root, text="Start", command=submit).pack()
    root.mainloop()
    return getattr(root, "study_time", None)

SESSION_TIME = get_study_time()
if SESSION_TIME is None:
    exit()


# LOAD MODEL

model = YOLO(MODEL_PATH)
print("Model classes:", model.names)


# CAMERA SETUP

cap = cv2.VideoCapture(0)

focus_time = 0.0
paused_time = 0.0
pause_start = None
phone_streak = 0


# FULL SCREEN

cv2.namedWindow("Focus Plant", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Focus Plant", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


# PLANT DRAWING FUNCTION

def draw_plant(frame, progress):
    h, w, _ = frame.shape
    base_x = w - 120
    base_y = h - 40

    max_height = 250
    stem_height = int(progress * max_height)

    # Stem
    cv2.line(frame, (base_x, base_y),
             (base_x, base_y - stem_height),
             (0, 200, 0), 6)

    # Leaves
    if progress > 0.3:
        cv2.ellipse(frame,
                    (base_x - 20, base_y - int(stem_height * 0.5)),
                    (25, 12), 0, 0, 360,
                    (0, 255, 0), -1)
    if progress > 0.6:
        cv2.ellipse(frame,
                    (base_x + 20, base_y - int(stem_height * 0.7)),
                    (25, 12), 0, 0, 360,
                    (0, 255, 0), -1)

    # Flower at end
    if progress > 0.95:
        cv2.circle(frame,
                   (base_x, base_y - stem_height),
                   18, (255, 0, 255), -1)


# MAIN LOOP

while True:
    ret, frame = cap.read()
    if not ret:
        break

    distraction = False
    results = model(frame, verbose=False)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls]

            if name.lower() == "phone" and conf > CONF_THRESHOLD:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                area = (x2 - x1) * (y2 - y1)
                frame_area = frame.shape[0] * frame.shape[1]

                if area < frame_area * 0.2:
                    phone_streak += 1
                else:
                    phone_streak = 0

                if phone_streak > PHONE_STREAK_REQUIRED:
                    distraction = True
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, "PHONE DETECTED", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


    # TIMER & PLANT LOGIC

    current_time = time.time()
    if not distraction:
        # Resume counting focus time
        if pause_start:
            paused_time += current_time - pause_start
            pause_start = None
        focus_time += 1 / 30     # grow ~1 unit per frame
    else:
        # Phone detected → plant shrinks, timer paused
        focus_time -= 1 / 30
        if focus_time < 0:
            focus_time = 0
        if not pause_start:
            pause_start = current_time

    remaining = SESSION_TIME - focus_time
    if remaining <= 0:
        break

    # Plant progress (0 → 1)
    progress = focus_time / SESSION_TIME
    progress = max(0, min(progress, 1))
    draw_plant(frame, progress)


    # DISPLAY TIMER & INFO

    mins = int(remaining // 60)
    secs = int(remaining % 60)

    cv2.putText(frame,
                f"Time Remaining: {mins:02}:{secs:02}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2)

    if distraction:
        cv2.putText(frame,
                    "Phone Detected - Plant Shrinking",
                    (30, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2)

    cv2.putText(frame,
                "Press ESC to end session",
                (30, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,      # smaller font
                (200, 200, 200),
                2)

    cv2.imshow("Focus Plant", frame)
    if cv2.waitKey(1) == 27:   # ESC to exit
        break


# CLEANUP

cap.release()
cv2.destroyAllWindows()