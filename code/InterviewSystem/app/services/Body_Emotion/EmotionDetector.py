import os
from deepface import DeepFace
import cv2


os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


class EmotionDetector:
    ALL_POSSIBLE_EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

    def __init__(self):
        import numpy as np

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.emotions = []
        try:  # 预热 DeepFace
            _ = DeepFace.analyze(np.zeros((100, 100, 3), dtype=np.uint8), actions=['emotion'], enforce_detection=False,
                                 silent=True)
            print("DeepFace 初始化完成。")
        except Exception as e:
            print(f"DeepFace 预热失败(不影响后续): {e}")

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            face_roi = frame[y:y + h, x:x + w]
            try:
                result = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False, silent=True)
                dominant_emotion = result[0]['dominant_emotion'] if isinstance(result, list) else result[
                    'dominant_emotion']
                self.emotions.append(dominant_emotion)
            except Exception:
                pass

    def get_summary(self):
        from collections import Counter

        report = {}
        if not self.emotions: return {emotion: 0.0 for emotion in self.ALL_POSSIBLE_EMOTIONS}
        emotion_counts = Counter(self.emotions)
        total_predictions = len(self.emotions)
        for emotion in self.ALL_POSSIBLE_EMOTIONS:
            count = emotion_counts.get(emotion, 0)
            report[emotion] = (count / total_predictions) * 100
        return report