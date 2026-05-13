import pickle, pandas as pd, numpy as np, mediapipe as mp, cv2
from collections import defaultdict
import warnings

warnings.filterwarnings("ignore", message="X does not have valid feature names")
warnings.filterwarnings("ignore", category=UserWarning, message="SymbolDatabase.GetPrototype() is deprecated")
def getDataFileRoute():
    from pathlib import Path
    current_file_path = Path(__file__).resolve()
    project_root_path = current_file_path.parent.parent.parent
    FILE_STORAGE_ROOT = project_root_path / "modelParameter"/"body_language.pkl"
    print(f"动态计算出的文件存储根目录是: {FILE_STORAGE_ROOT}")
    return FILE_STORAGE_ROOT
if __name__ == "__main__":
    getDataFileRoute()

class BodyLanguageRecognizer:
    ALL_POSSIBLE_CLASSES = ["Head looks down", "Hand on waist", "Normal", "Hands clasped"]

    def __init__(self, model_path=getDataFileRoute()):
        self.class_counts = defaultdict(int)
        self.processed_frames_count = 0
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"模型文件未找到: {model_path}")
        self.mp_holistic = mp.solutions.holistic
        self.holistic_processor = self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def process_frame(self, frame):
        self.processed_frames_count += 1
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.holistic_processor.process(image)
        try:
            pose = results.pose_landmarks.landmark
            pose_row = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in pose]).flatten().tolist()
            face = results.face_landmarks.landmark
            face_row = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in face]).flatten().tolist()
            row = pose_row + face_row
            X = pd.DataFrame([row])
            body_language_class = self.model.predict(X)[0]
            self.class_counts[body_language_class] += 1
        except Exception:
            pass

    def get_summary(self):
        summary = {}
        if self.processed_frames_count == 0: return {name: 0.0 for name in self.ALL_POSSIBLE_CLASSES}
        for class_name in self.ALL_POSSIBLE_CLASSES:
            count = self.class_counts.get(class_name, 0)
            summary[class_name] = (count / self.processed_frames_count) * 100
        return summary

    def close(self):
        self.holistic_processor.close()