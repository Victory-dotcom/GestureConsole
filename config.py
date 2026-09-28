"""
config.py
--------------------------------
Configuration file for GestureConsole
"""

# ==========================================
# CAMERA SETTINGS
# ==========================================

CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

MIRROR_CAMERA = True

SHOW_LANDMARKS = True
SHOW_HUD = True
SHOW_STEERING_LINE = True
FULLSCREEN = False

# ==========================================
# MEDIAPIPE SETTINGS
# ==========================================

MAX_HANDS = 2

MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7

# ==========================================
# STEERING SETTINGS
# ==========================================

STEERING_THRESHOLD = 70

MAX_STEERING_ANGLE = 90

STEERING_SMOOTHING = 0.20

DEAD_ZONE = 20

# ==========================================
# ACCELERATION SETTINGS
# ==========================================

ACCELERATE_KEY = "w"
BRAKE_KEY = "s"

AUTO_RELEASE_ACCELERATOR = True

# ==========================================
# STEERING KEYS
# ==========================================

LEFT_KEY = "a"
RIGHT_KEY = "d"

# ==========================================
# GAME CONTROLS (Future Features)
# ==========================================

NITRO_KEY = "shift"

HANDBRAKE_KEY = "space"

GEAR_UP_KEY = "e"

GEAR_DOWN_KEY = "q"

PAUSE_KEY = "esc"

# ==========================================
# GESTURE SETTINGS
# ==========================================

MIN_FISTS_FOR_ACCELERATION = 1

MIN_FISTS_FOR_STEERING = 2

FIST_REQUIRED_FOLDED_FINGERS = 4

# ==========================================
# DISPLAY SETTINGS
# ==========================================

WINDOW_NAME = "Gesture Console"

FPS_FONT_SCALE = 0.8

HUD_FONT_SCALE = 0.8

HUD_THICKNESS = 2

# ==========================================
# COLOURS (BGR)
# ==========================================

GREEN = (0, 255, 0)

RED = (0, 0, 255)

BLUE = (255, 0, 0)

CYAN = (255, 255, 0)

MAGENTA = (255, 0, 255)

YELLOW = (0, 255, 255)

WHITE = (255, 255, 255)

BLACK = (0, 0, 0)

# ==========================================
# PERFORMANCE
# ==========================================

TARGET_FPS = 60

ENABLE_FPS_LIMIT = False

# ==========================================
# DEBUG
# ==========================================

DEBUG = False

PRINT_GESTURES = False

PRINT_FPS = False

# ==========================================
# AUDIO (Future)
# ==========================================

ENABLE_SOUNDS = False

SOUND_VOLUME = 0.7

# ==========================================
# VIRTUAL STEERING WHEEL
# ==========================================

DRAW_STEERING_WHEEL = True

STEERING_WHEEL_RADIUS = 120

STEERING_WHEEL_THICKNESS = 5

# ==========================================
# FILES
# ==========================================

ICON_PATH = "assets/icon.png"

STEERING_WHEEL_IMAGE = "assets/steering_wheel.png"

LOG_FILE = "gesture_console.log"
