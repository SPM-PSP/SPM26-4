import cv2, mediapipe as mp, numpy as np


class HandMovementDetector:
    def __init__(self, total_video_frames):
        self.prev_landmarks = None
        self.hands_processor = mp.solutions.hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7,
                                                        max_num_hands=2)
        self.total_movement = 0.0
        self.total_video_frames = total_video_frames

    def process_frame(self, frame):

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.hands_processor.process(image)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                current_landmarks = np.array([(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark])
                if self.prev_landmarks is not None:
                    movement = np.linalg.norm(current_landmarks - self.prev_landmarks, axis=1)
                    self.total_movement += np.sum(movement)
                self.prev_landmarks = current_landmarks

    def get_summary(self):
        avg_movement = self.total_movement / self.total_video_frames if self.total_video_frames > 0 else 0
        return {"total_movement": self.total_movement, "average_movement_per_frame": avg_movement}

    def close(self):
        self.hands_processor.close()