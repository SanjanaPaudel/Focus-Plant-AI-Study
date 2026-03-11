# Focus Plant AI Study Monitor

**Focus Plant** is a computer vision-based application designed to help students stay focused while studying. The system uses a YOLOv8 model to detect mobile phones and monitors the student's focus in real time using a webcam.

### Key Features

* **Custom Study Timer:** Set your study session duration (10 minutes to 7 hours).
* **Phone Detection:** The system detects when a mobile phone is in use.
* **Focus Tracking:** Timer tracks how long the student has been focused; pauses or decreases when distractions are detected.
* **Visual Feedback:** An animated plant grows as the student stays focused and decreases if a phone is detected.
* **Session Summary:** At the end of the session, the focus time and distractions are recorded for self-assessment.

### How It Works

1. Student sets the study duration via a simple interface.
2. The webcam monitors the study environment using YOLOv8 for phone detection.
3. When the student is focused, the plant grows, and the timer counts up.
4. If a phone is detected, the timer pauses or the plant decreases to indicate distraction.
5. The session continues until the set study duration is reached, encouraging better focus habits.

### Requirements

* Python 3.8 or higher
* OpenCV
* Ultralytics YOLOv8
* Tkinter
* NumPy

### Usage

1. Run the `focus_ai.py` script.
2. Enter your study duration.
3. The system will open a full-screen window showing the timer and plant animation.
4. Focus on your work and avoid using your phone to see the plant grow.

### Demo Video
<!-- Uploading "demo_video (2).mp4"... -->
