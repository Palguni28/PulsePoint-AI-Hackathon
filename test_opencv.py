import cv2
import os

print(f"OpenCV Version: {cv2.__version__}")

try:
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    print(f"Cascade Path: {cascade_path}")
    
    if not os.path.exists(cascade_path):
        print("Error: Cascade file not found in cv2.data")
    else:
        face_cascade = cv2.CascadeClassifier(cascade_path)
        if face_cascade.empty():
            print("Error: Failed to load cascade classifier")
        else:
            print("SUCCESS: Cascade Classifier Loaded")
except Exception as e:
    print(f"Error: {e}")
