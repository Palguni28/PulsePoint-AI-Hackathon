import mediapipe as mp
import cv2
import sys

print(f"Python: {sys.version}")
try:
    import mediapipe
    print(f"MediaPipe Version: {mediapipe.__version__}")
except:
    print("MediaPipe import failed")

print(f"File: {mp.__file__}")
print(f"Dir: {dir(mp)}")

print("Initializing Face Detection...")
try:
    import mediapipe.python.solutions.face_detection as mp_face
    print("Direct import successful")
    
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)
    print("SUCCESS: Face Detection Initialized")
    face_detection.close()
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
