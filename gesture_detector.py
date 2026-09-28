"""
gesture_detector.py
-------------------------------------
Gesture detection for GestureConsole

Features:
- Fist detection
- Open hand detection
- Thumbs up detection
- Left/Right hand recognition
"""

import math


class GestureDetector:

    def __init__(self):

        self.tip_ids = [4, 8, 12, 16, 20]
        self.pip_ids = [2, 6, 10, 14, 18]

    # -------------------------------------------------
    # Distance
    # -------------------------------------------------

    def distance(self, hand, id1, id2):

        x1 = hand.landmark[id1].x
        y1 = hand.landmark[id1].y

        x2 = hand.landmark[id2].x
        y2 = hand.landmark[id2].y

        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # -------------------------------------------------
    # Finger folded
    # -------------------------------------------------

    def finger_folded(self, hand, tip, pip):

        return hand.landmark[tip].y > hand.landmark[pip].y

    # -------------------------------------------------
    # Count folded fingers
    # -------------------------------------------------

    def folded_fingers(self, hand):

        folded = 0

        fingers = [
            (8, 6),
            (12, 10),
            (16, 14),
            (20, 18)
        ]

        for tip, pip in fingers:

            if self.finger_folded(hand, tip, pip):
                folded += 1

        return folded

    # -------------------------------------------------
    # Fist
    # -------------------------------------------------

    def is_fist(self, hand):

        folded = self.folded_fingers(hand)

        thumb_closed = (
            self.distance(hand, 4, 5)
            <
            self.distance(hand, 4, 2)
        )

        return folded >= 4 and thumb_closed

    # -------------------------------------------------
    # Open Hand
    # -------------------------------------------------

    def is_open_hand(self, hand):

        fingers = [
            (8, 6),
            (12, 10),
            (16, 14),
            (20, 18)
        ]

        for tip, pip in fingers:

            if hand.landmark[tip].y > hand.landmark[pip].y:
                return False

        return True

    # -------------------------------------------------
    # Thumbs Up
    # -------------------------------------------------

    def is_thumbs_up(self, hand):

        thumb_up = hand.landmark[4].y < hand.landmark[3].y

        index_folded = hand.landmark[8].y > hand.landmark[6].y
        middle_folded = hand.landmark[12].y > hand.landmark[10].y
        ring_folded = hand.landmark[16].y > hand.landmark[14].y
        pinky_folded = hand.landmark[20].y > hand.landmark[18].y

        return (
            thumb_up and
            index_folded and
            middle_folded and
            ring_folded and
            pinky_folded
        )

    # -------------------------------------------------
    # Hand Centre
    # -------------------------------------------------
    def hand_center(self, hand, width, height):

        x = 0
        y = 0

        for lm in hand.landmark:

            x += lm.x
            y += lm.y

        x /= 21
        y /= 21

        return (
            int(x * width),
            int(y * height)
        )

    # -------------------------------------------------
    # Detect
    # -------------------------------------------------

    def detect(self,
               hand_landmarks,
               handedness,
               width,
               height):

        data = {

            "left_open": False,
            "right_open": False,

            "left_fist": False,
            "right_fist": False,

            "thumbs_up": 0,

            "fists": [],
            "palms": [],

            "fist_count": 0,
            "palm_count": 0
        }

        for i, hand in enumerate(hand_landmarks):

            label = handedness[i].classification[0].label

            centre = self.hand_center(
                hand,
                width,
                height
            )

            # -----------------------
            # Fist
            # -----------------------

            if self.is_fist(hand):
                data["fists"].append(centre)

                data["fist_count"] += 1

                # Camera is mirrored
                if label == "Left":
                    data["right_fist"] = True
                else:
                    data["left_fist"] = True

            # -----------------------
            # Open Hand (Mirrored Camera)
            # -----------------------

            if self.is_open_hand(hand):

                data["palms"].append(centre)

                data["palm_count"] += 1

                # Camera is mirrored, so swap left/right
                if label == "Left":
                    data["right_open"] = True
                else:
                    data["left_open"] = True

            # -----------------------
            # Thumbs Up
            # -----------------------

            if self.is_thumbs_up(hand):

                data["thumbs_up"] += 1

        # ---------------------------------------
        # Derived gesture states
        # ---------------------------------------

        data["accelerate"] = data["fist_count"] >= 1

        data["brake"] = data["palm_count"] == 2

        data["nitro"] = data["thumbs_up"] == 2

        data["steering_wheel"] = data["fist_count"] == 2

        return data
