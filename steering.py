"""
steering.py
--------------------
Calculates steering based on two detected fists.

Author: GestureConsole
"""

import math


class SteeringWheel:

    def __init__(self, frame_width, threshold=70, smoothing=0.8):
        self.frame_width = frame_width
        self.threshold = threshold
        self.smoothing = smoothing

        self.smoothed_angle = 0

    def update_frame_width(self, width):
        self.frame_width = width

    def calculate(self, left_hand, right_hand):
        """
        Calculate steering using the angle of the line
        between the left and right hands.

        Returns:
            angle (-90 to 90)
            direction
            centre
        """

        dx = right_hand[0] - left_hand[0]
        dy = right_hand[1] - left_hand[1]

        # Steering wheel rotation
        angle = math.degrees(math.atan2(dy, dx))

        # Convert to steering angle
        steering_angle = angle

        # Horizontal hands = 0°
        # Rotate left  = negative
        # Rotate right = positive

        if steering_angle > 90:
            steering_angle -= 180

        elif steering_angle < -90:
            steering_angle += 180

        # Instant response
        self.smoothed_angle = steering_angle

        # Dead zone
        if self.smoothed_angle < -5:
            direction = "LEFT"

        elif self.smoothed_angle > 5:
            direction = "RIGHT"

        else:
            direction = "STRAIGHT"

        centre = (
            int((left_hand[0] + right_hand[0]) / 2),
            int((left_hand[1] + right_hand[1]) / 2)
        )

        return (
            round(self.smoothed_angle, 2),
            direction,
            centre
        )

    def steering_strength(self):
        """
        Returns value between 0 and 1.
        Useful for analog steering.
        """

        return min(abs(self.smoothed_angle) / 90.0, 1.0)

    def reset(self):
        self.smoothed_angle = 0
