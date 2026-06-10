from ultralytics import YOLO
import numpy as np

def getDataFileRoute():
    from pathlib import Path
    current_file_path = Path(__file__).resolve()
    project_root_path = current_file_path.parent.parent.parent
    FILE_STORAGE_ROOT = project_root_path / "modelParameter"/"yolov8n.pt"
    print(f"动态计算出的文件存储根目录是: {FILE_STORAGE_ROOT}")
    return FILE_STORAGE_ROOT



class ObjectTracker:
    def __init__(self, total_video_frames, model_path=getDataFileRoute()):
        self.model = YOLO(model_path)
        self.movement_distances = []
        self.prev_centroid = None
        self.total_video_frames = total_video_frames

    def process_frame(self, frame):
        results = self.model.track(frame, persist=True, verbose=False)
        try:
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                bbox = results[0].boxes[0].xywh[0]
                centroid = (bbox[0].item(), bbox[1].item())
                if self.prev_centroid is not None:
                    distance = np.linalg.norm(np.array(centroid) - np.array(self.prev_centroid))
                    self.movement_distances.append(distance)
                self.prev_centroid = centroid
        except Exception: self.prev_centroid = None

    def get_summary(self):
        total_movement = sum(self.movement_distances)
        average_movement = total_movement / self.total_video_frames if self.total_video_frames > 0 else 0
        if average_movement < 5: assessment = "演讲者相对静止。考虑使用更多的手势和身体移动来吸引观众。"
        elif 5 <= average_movement < 15: assessment = "演讲者有适度的身体移动，这对于吸引观众是很好的。"
        else: assessment = "演讲者移动很多。请确保这些移动是有目的性的，而不是分散注意力的。"
        return {"total_movement": total_movement, "average_movement": average_movement, "assessment": assessment}