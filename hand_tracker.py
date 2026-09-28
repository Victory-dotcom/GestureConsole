"""
hand_tracker.py
-----------------------------------
MediaPipe Hand Tracker
Used by GestureConsole

Author: GestureConsole
"""

import cv2
import mediapipe as mp


class HandTracker:

    def __init__(
        self,
        max_hands=2,
        detection_confidence=0.7,
        tracking_confidence=0.7
    ):

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

    # ------------------------------------------
    # Detect hands
    # ------------------------------------------

    def process(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return self.hands.process(rgb)

    # ------------------------------------------
    # Draw landmarks
    # ------------------------------------------

    def draw(self, frame, results):

        if not results.multi_hand_landmarks:
            return frame

        for hand in results.multi_hand_landmarks:

            self.mp_draw.draw_landmarks(
                frame,
                hand,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(
                    color=(0, 255, 0),
                    thickness=2,
                    circle_radius=3
                ),
                self.mp_draw.DrawingSpec(
                    color=(255, 0, 255),
                    thickness=2
                )
            )

        return frame

    # ------------------------------------------
    # Get wrist positions
    # ------------------------------------------

    def wrists(self, results, width, height):

        positions = []

        if not results.multi_hand_landmarks:
            return positions

        for hand in results.multi_hand_landmarks:

            wrist = hand.landmark[0]

            positions.append((
                int(wrist.x * width),
                int(wrist.y * height)
            ))

        return positions

    # ------------------------------------------
    # Get hand centres
    # ------------------------------------------

    def centres(self, results, width, height):

        centres = []

        if not results.multi_hand_landmarks:
            return centres

        for hand in results.multi_hand_landmarks:

            x = 0
            y = 0

            for lm in hand.landmark:
                x += lm.x
                y += lm.y

            x /= 21
            y /= 21

            centres.append((
                int(x * width),
                int(y * height)
            ))

        return centres

    # ------------------------------------------
    # Get handedness (Left / Right)
    # ------------------------------------------

    def handedness(self, results):

        hands = []

        if not results.multi_handedness:
            return hands

        for hand in results.multi_handedness:

            hands.append(hand.classification[0].label)

        return hands

    # ------------------------------------------
    # Get all hand data
    # ------------------------------------------

    def get_hand_data(self, results, width, height):

        data = []

        if not results.multi_hand_landmarks:
            return data

        handed = self.handedness(results)

        for index, hand in enumerate(results.multi_hand_landmarks):

            x = 0
            y = 0

            for lm in hand.landmark:
                x += lm.x
                y += lm.y

            x /= 21
            y /= 21

            wrist = hand.landmark[0]

            data.append({

                "index": index,

                "label": handed[index] if index < len(handed) else "Unknown",

                "landmarks": hand,

                "centre": (
                    int(x * width),
                    int(y * height)
                ),

                "wrist": (
                    int(wrist.x * width),
                    int(wrist.y * height)
                )
            })

        return data

    # ------------------------------------------
    # Release MediaPipe resources
    # ------------------------------------------

    def close(self):
        self.hands.close()
