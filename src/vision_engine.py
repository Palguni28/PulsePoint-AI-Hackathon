import cv2
import numpy as np

class VisionEngine:
    def __init__(self):
        print("[*] Initializing OpenCV Face Detection (Haar Cascade)...")
        self.cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        if self.face_cascade.empty():
            print("[!] Error: Failed to load Haar Cascade!")

    def get_tracking_function(self, clip, target_aspect_ratio=9/16, sample_rate=0.5):
        """
        Analyzes the clip to create a smooth face tracking function.
        Returns a function x1(t) that returns the left crop coordinate for time t.
        sample_rate: Analyze 1 frame every 'sample_rate' seconds.
        """
        print("[*] Tracking face movement...")
        
        # 1. Analyze Keyframes
        duration = clip.duration
        times = []
        center_xs = []
        
        width = clip.w
        height = clip.h
        new_width = int(height * target_aspect_ratio)
        
        last_center = width // 2
        
        for t in np.arange(0, duration, sample_rate):
            # Safe access to frame
            try:
                frame = clip.get_frame(t)
            except:
                break
                
            # Detect Face
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray_frame, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                fx, fy, fw, fh = largest_face
                center = fx + fw // 2
                last_center = center
            
            times.append(t)
            center_xs.append(last_center)
            
        if not times:
            # Fallback if no frames read
            return lambda t: (width - new_width) // 2, new_width

        # 2. Smooth the trajectory (Moving Average)
        window_size = 5
        smoothed_xs = np.convolve(center_xs, np.ones(window_size)/window_size, mode='same')
        
        # 3. Create Interpolation Function
        def get_crop_x1(t):
            # Find closest index or interpolate
            if t > times[-1]:
                center = smoothed_xs[-1]
            else:
                center = np.interp(t, times, smoothed_xs)
            
            x1 = int(center - new_width // 2)
            
            # Clamp
            if x1 < 0: x1 = 0
            if x1 + new_width > width: x1 = width - new_width
            
            return x1
            
        return get_crop_x1, new_width