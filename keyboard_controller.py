"""
keyboard_controller.py
---------------------------------------
Gesture Console Keyboard Controller

Uses PyAutoGUI to emulate a keyboard.

Author: GestureConsole
"""
import pydirectinput

pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0


class KeyboardController:

    def __init__(self):
        self.held = set()

    # -----------------------------------
    # Internal
    # -----------------------------------

    def _hold(self, key):
        """Hold a key only once."""
        if key not in self.held:
            pydirectinput.keyDown(key)
            self.held.add(key)

    def _release(self, key):
        """Release a held key."""
        if key in self.held:
            pydirectinput.keyUp(key)
            self.held.remove(key)

    # -----------------------------------
    # Driving
    # -----------------------------------

    def accelerate(self):
        self._hold("w")

    def stop_accelerating(self):
        self._release("w")

    def brake(self):
        self._hold("s")

    def release_brake(self):
        self._release("s")

    # -----------------------------------
    # Steering
    # -----------------------------------

    def steer_left(self):
        self._release("d")
        self._hold("a")

    def steer_right(self):
        self._release("a")
        self._hold("d")

    def straighten(self):
        self._release("a")
        self._release("d")

    # -----------------------------------
    # Steering By Angle
    # -----------------------------------

    def steer(self, angle):

        # Dead zone
        if -12 <= angle <= 12:
            self.straighten()
            return

        # Left
        if angle < -12:

            self._release("d")
            self._hold("a")

        # Right
        else:

            self._release("a")
            self._hold("d")

    # -----------------------------------
    # Extras
    # -----------------------------------

    def nitro(self):
        self._hold("x")

    def release_nitro(self):
        self._release("x")

    def handbrake(self):
        self._hold("space")

    def release_handbrake(self):
        self._release("space")

    # -----------------------------------
    # One-time key presses
    # -----------------------------------

    def gear_up(self):
        pydirectinput.press("e")

    def gear_down(self):
        pydirectinput.press("q")

    def pause(self):
        pydirectinput.press("esc")

    # -----------------------------------
    # Driving modes
    # -----------------------------------

    def drive_straight(self):
        """
        Hold W only.
        """
        self.accelerate()
        self.straighten()

    def drive_left(self):
        """
        Hold W + A.
        """
        self.accelerate()
        self.steer_left()

    def drive_right(self):
        """
        Hold W + D.A
        """
        self.accelerate()
        self.steer_right()

    def stop(self):
        """
        Release movement keys.
        """
        self.stop_accelerating()
        self.straighten()

    # -----------------------------------
    # Cleanup
    # -----------------------------------

    def release_all(self):
        """
        Release every held key.
        """
        for key in list(self.held):
            pydirectinput.keyUp(key)

        self.held.clear()

    # -----------------------------------
    # Debug
    # -----------------------------------

    def held_keys(self):
        return sorted(self.held)
