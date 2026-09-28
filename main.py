import cv2
import math
import time
import numpy as np
import subprocess
import os

import win32api
import win32con
import win32gui
import win32process

from config import *
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from steering import SteeringWheel
from keyboard_controller import KeyboardController

# ============================================================
# NEED FOR SPEED MOST WANTED
# ============================================================

EXE_PATH = r"D:\NeedForSpeedMostWantedBlackEdition\Need For Speed Most Wanted Black Edition\Need For Speed Most Wanted Black Edition\speed.exe"

# NFS embedding state
_nfs_pid = None
_nfs_embed_state = {
    "hwnd": None,
    "original_parent": None,
    "original_style": None,
    "original_exstyle": None,
}

# Match the central HUD rectangle in the existing GestureConsole layout.
NFS_EMBED_X = 250
NFS_EMBED_Y = 105
NFS_EMBED_W = 780
NFS_EMBED_H = 465



def launch_need_for_speed():
    """Launch NFS if necessary and remember its PID."""
    global _nfs_pid

    try:
        output = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq speed.exe", "/FO", "CSV", "/NH"],
            text=True,
            stderr=subprocess.DEVNULL
        )

        for line in output.splitlines():
            if "speed.exe" in line.lower():
                parts = [x.strip('"') for x in line.split('","')]
                if len(parts) >= 2:
                    _nfs_pid = int(parts[1])
                    print("Need for Speed Most Wanted is already running.")
                    return True
    except Exception:
        pass

    try:
        proc = subprocess.Popen(
            [EXE_PATH],
            cwd=os.path.dirname(EXE_PATH)
        )
        _nfs_pid = proc.pid
        print(f"Need for Speed Most Wanted launched. PID: {_nfs_pid}")
        return True
    except Exception as e:
        print(f"Could not launch Need for Speed Most Wanted: {e}")
        return False


def find_nfs_window(timeout=15.0):
    """Find the NFS Direct3D proxy/render window belonging to speed.exe.

    NFS Most Wanted can expose its renderer as an invisible D3DProxyWindow
    rather than a normal titled game window.  Therefore we intentionally
    include invisible windows and prefer D3DProxyWindow.
    """
    deadline = time.time() + timeout

    while time.time() < deadline:
        windows = []

        def enum_callback(hwnd, _):
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid != _nfs_pid:
                    return True

                class_name = win32gui.GetClassName(hwnd)
                title = win32gui.GetWindowText(hwnd).strip()

                # Ignore IME/helper windows.
                if class_name in ("IME", "MSCTFIME UI"):
                    return True

                windows.append((hwnd, class_name, title))
            except Exception:
                pass
            return True

        # PID is stored globally when NFS is launched/detected.
        win32gui.EnumWindows(enum_callback, None)

        # Prefer the actual Direct3D renderer window.
        for hwnd, class_name, title in windows:
            if class_name == "D3DProxyWindow":
                return hwnd

        # Fallback to a titled window if the game exposes one.
        for hwnd, class_name, title in windows:
            if title and win32gui.IsWindow(hwnd):
                return hwnd

        # Last fallback: any non-IME window belonging to speed.exe.
        if windows:
            return windows[0][0]

        time.sleep(0.25)

    return None


def embed_need_for_speed(console_hwnd):
    """Re-parent the NFS Direct3D renderer into the GestureConsole HUD."""
    global _nfs_pid

    # If already embedded, just make sure the child is still positioned.
    existing = _nfs_embed_state.get("hwnd")
    if existing and win32gui.IsWindow(existing):
        try:
            win32gui.SetWindowPos(
                existing,
                win32con.HWND_TOP,
                NFS_EMBED_X,
                NFS_EMBED_Y,
                NFS_EMBED_W,
                NFS_EMBED_H,
                win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
            )
            return True
        except Exception:
            pass

    nfs_hwnd = find_nfs_window()

    if not nfs_hwnd:
        print("Could not find the Need for Speed game window.")
        return False

    try:
        _nfs_embed_state["hwnd"] = nfs_hwnd
        _nfs_embed_state["original_parent"] = win32gui.GetParent(nfs_hwnd)
        _nfs_embed_state["original_style"] = win32gui.GetWindowLong(
            nfs_hwnd, win32con.GWL_STYLE
        )
        _nfs_embed_state["original_exstyle"] = win32gui.GetWindowLong(
            nfs_hwnd, win32con.GWL_EXSTYLE
        )

        style = _nfs_embed_state["original_style"]
        style &= ~(
            win32con.WS_CAPTION
            | win32con.WS_THICKFRAME
            | win32con.WS_MINIMIZE
            | win32con.WS_MAXIMIZE
            | win32con.WS_SYSMENU
            | win32con.WS_POPUP
        )
        style |= win32con.WS_CHILD

        exstyle = _nfs_embed_state["original_exstyle"]
        exstyle &= ~win32con.WS_EX_APPWINDOW
        exstyle |= win32con.WS_EX_TOOLWINDOW

        win32gui.SetWindowLong(nfs_hwnd, win32con.GWL_STYLE, style)
        win32gui.SetWindowLong(nfs_hwnd, win32con.GWL_EXSTYLE, exstyle)
        win32gui.SetParent(nfs_hwnd, console_hwnd)

        win32gui.SetWindowPos(
            nfs_hwnd,
            win32con.HWND_TOP,
            NFS_EMBED_X,
            NFS_EMBED_Y,
            NFS_EMBED_W,
            NFS_EMBED_H,
            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
        )

        win32gui.ShowWindow(nfs_hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(nfs_hwnd)

        print("NFS Direct3D renderer embedded successfully.")
        print(
            f"NFS renderer: {NFS_EMBED_W}x{NFS_EMBED_H} "
            f"at ({NFS_EMBED_X}, {NFS_EMBED_Y})"
        )
        return True

    except Exception as e:
        print(f"Could not embed Need for Speed: {e}")
        return False


def restore_need_for_speed():
    """Restore NFS renderer as a normal window when GestureConsole exits."""
    hwnd = _nfs_embed_state.get("hwnd")

    if not hwnd or not win32gui.IsWindow(hwnd):
        return

    try:
        original_parent = _nfs_embed_state.get("original_parent") or 0
        original_style = _nfs_embed_state.get("original_style")
        original_exstyle = _nfs_embed_state.get("original_exstyle")

        win32gui.SetParent(hwnd, original_parent)

        if original_style is not None:
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, original_style)
        if original_exstyle is not None:
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, original_exstyle)

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE
            | win32con.SWP_NOSIZE
            | win32con.SWP_NOACTIVATE
            | win32con.SWP_SHOWWINDOW
        )

        print("NFS window restored.")
    except Exception as e:
        print(f"Could not restore NFS window: {e}")


# ============================================================
# GESTURE CONSOLE
# FUTURISTIC SCI-FI HUD
# ============================================================


# ------------------------------------------------------------
# UI COLORS
# ------------------------------------------------------------

HUD_BG = (5, 10, 20)
PANEL_BG = (8, 18, 32)
PANEL_BG_2 = (10, 24, 42)

CYAN_HUD = (255, 220, 0)
BLUE_HUD = (255, 120, 0)
LIGHT_BLUE = (255, 180, 40)

GREEN_HUD = (80, 255, 40)
RED_HUD = (40, 60, 255)
YELLOW_HUD = (0, 235, 255)
MAGENTA_HUD = (255, 0, 220)

WHITE_HUD = (245, 250, 255)
GREY_HUD = (110, 125, 140)
DARK_GREY = (40, 50, 65)
BLACK_HUD = (0, 0, 0)


# ------------------------------------------------------------
# BASIC DRAWING HELPERS
# ------------------------------------------------------------

def draw_glow_line(canvas, pt1, pt2, colour, thickness=2):
    """
    Draw a simple sci-fi glowing line.
    """
    glow = canvas.copy()

    cv2.line(
        glow,
        pt1,
        pt2,
        colour,
        thickness * 4,
        cv2.LINE_AA
    )

    glow = cv2.GaussianBlur(glow, (0, 0), 5)

    canvas[:] = cv2.addWeighted(
        canvas,
        1.0,
        glow,
        0.18,
        0
    )

    cv2.line(
        canvas,
        pt1,
        pt2,
        colour,
        thickness,
        cv2.LINE_AA
    )


def draw_corner_brackets(
    frame,
    x,
    y,
    w,
    h,
    colour=CYAN_HUD,
    size=28,
    thickness=2
):
    """
    Draw futuristic corner brackets around a rectangle.
    """

    # Top-left
    cv2.line(
        frame,
        (x, y),
        (x + size, y),
        colour,
        thickness,
        cv2.LINE_AA
    )

    cv2.line(
        frame,
        (x, y),
        (x, y + size),
        colour,
        thickness,
        cv2.LINE_AA
    )

    # Top-right
    cv2.line(
        frame,
        (x + w, y),
        (x + w - size, y),
        colour,
        thickness,
        cv2.LINE_AA
    )

    cv2.line(
        frame,
        (x + w, y),
        (x + w, y + size),
        colour,
        thickness,
        cv2.LINE_AA
    )

    # Bottom-left
    cv2.line(
        frame,
        (x, y + h),
        (x + size, y + h),
        colour,
        thickness,
        cv2.LINE_AA
    )

    cv2.line(
        frame,
        (x, y + h),
        (x, y + h - size),
        colour,
        thickness,
        cv2.LINE_AA
    )

    # Bottom-right
    cv2.line(
        frame,
        (x + w, y + h),
        (x + w - size, y + h),
        colour,
        thickness,
        cv2.LINE_AA
    )

    cv2.line(
        frame,
        (x + w, y + h),
        (x + w, y + h - size),
        colour,
        thickness,
        cv2.LINE_AA
    )


def draw_panel_box(
    canvas,
    x,
    y,
    w,
    h,
    title,
    colour=CYAN_HUD
):
    """
    Draw a futuristic information panel.
    """

    # Dark transparent panel
    overlay = canvas.copy()

    cv2.rectangle(
        overlay,
        (x, y),
        (x + w, y + h),
        PANEL_BG,
        -1
    )

    canvas[:] = cv2.addWeighted(
        overlay,
        0.88,
        canvas,
        0.12,
        0
    )

    # Outer border
    cv2.rectangle(
        canvas,
        (x, y),
        (x + w, y + h),
        DARK_GREY,
        1
    )

    # Header line
    cv2.line(
        canvas,
        (x + 12, y + 42),
        (x + w - 12, y + 42),
        colour,
        1,
        cv2.LINE_AA
    )

    # Header accent
    cv2.line(
        canvas,
        (x + 12, y + 42),
        (x + 75, y + 42),
        colour,
        3,
        cv2.LINE_AA
    )

    # Title
    cv2.putText(
        canvas,
        title,
        (x + 16, y + 29),
        cv2.FONT_HERSHEY_DUPLEX,
        0.55,
        colour,
        1,
        cv2.LINE_AA
    )

    draw_corner_brackets(
        canvas,
        x,
        y,
        w,
        h,
        colour,
        18,
        2
    )


def draw_action_item(
    canvas,
    x,
    y,
    label,
    active,
    colour
):
    """
    Draw an action indicator.
    """

    if active:
        circle_colour = colour
        text_colour = WHITE_HUD
        radius = 9
    else:
        circle_colour = GREY_HUD
        text_colour = GREY_HUD
        radius = 7

    # Outer circle
    cv2.circle(
        canvas,
        (x, y),
        12,
        circle_colour,
        1,
        cv2.LINE_AA
    )

    # Inner active circle
    if active:
        cv2.circle(
            canvas,
            (x, y),
            radius,
            circle_colour,
            -1,
        )

    # Label
    cv2.putText(
        canvas,
        label,
        (x + 30, y + 7),
        cv2.FONT_HERSHEY_DUPLEX,
        0.52,
        text_colour,
        1,
        cv2.LINE_AA
    )


def draw_info_text(
    canvas,
    x,
    y,
    label,
    value,
    value_colour=WHITE_HUD
):
    """
    Draw label/value information.
    """

    cv2.putText(
        canvas,
        label,
        (x, y),
        cv2.FONT_HERSHEY_DUPLEX,
        0.43,
        GREY_HUD,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        canvas,
        value,
        (x, y + 24),
        cv2.FONT_HERSHEY_DUPLEX,
        0.52,
        value_colour,
        1,
        cv2.LINE_AA
    )


# ------------------------------------------------------------
# CAMERA VIDEO PANEL
# ------------------------------------------------------------

def draw_video_panel(canvas, video):
    """
    Place the camera image in the center of the HUD.
    """

    canvas_h, canvas_w = canvas.shape[:2]

    # Central video rectangle
    video_x = 250
    video_y = 105
    video_w = 780
    video_h = 465

    # Resize video while preserving aspect ratio
    source_h, source_w = video.shape[:2]

    scale = min(
        video_w / source_w,
        video_h / source_h
    )

    new_w = int(source_w * scale)
    new_h = int(source_h * scale)

    resized = cv2.resize(
        video,
        (new_w, new_h),
        interpolation=cv2.INTER_LINEAR
    )

    # Create video background
    video_area = canvas[
        video_y:video_y + video_h,
        video_x:video_x + video_w
    ]

    video_area[:] = (3, 8, 15)

    # Center image
    offset_x = (video_w - new_w) // 2
    offset_y = (video_h - new_h) // 2

    video_area[
        offset_y:offset_y + new_h,
        offset_x:offset_x + new_w
    ] = resized

    # Outer border
    cv2.rectangle(
        canvas,
        (video_x, video_y),
        (video_x + video_w, video_y + video_h),
        CYAN_HUD,
        2,
        cv2.LINE_AA
    )

    # Inner border
    cv2.rectangle(
        canvas,
        (video_x + 7, video_y + 7),
        (video_x + video_w - 7, video_y + video_h - 7),
        DARK_GREY,
        1,
        cv2.LINE_AA
    )

    # Corner brackets
    draw_corner_brackets(
        canvas,
        video_x,
        video_y,
        video_w,
        video_h,
        CYAN_HUD,
        30,
        3
    )

    # Camera label
    cv2.rectangle(
        canvas,
        (video_x + 18, video_y + 15),
        (video_x + 125, video_y + 42),
        HUD_BG,
        -1
    )

    cv2.putText(
        canvas,
        "CAMERA",
        (video_x + 28, video_y + 34),
        cv2.FONT_HERSHEY_DUPLEX,
        0.42,
        CYAN_HUD,
        1,
        cv2.LINE_AA
    )

    # LIVE indicator
    cv2.circle(
        canvas,
        (video_x + video_w - 70, video_y + 28),
        5,
        RED_HUD,
        -1
    )

    cv2.putText(
        canvas,
        "LIVE",
        (video_x + video_w - 58, video_y + 34),
        cv2.FONT_HERSHEY_DUPLEX,
        0.40,
        WHITE_HUD,
        1,
        cv2.LINE_AA
    )

    return (
        video_x,
        video_y,
        video_w,
        video_h
    )


# ------------------------------------------------------------
# CROSSHAIR
# ------------------------------------------------------------

def draw_crosshair(
    frame,
    x,
    y,
    colour=CYAN_HUD
):
    """
    Draw futuristic targeting crosshair.
    """

    length = 24
    gap = 8

    # Left
    cv2.line(
        frame,
        (x - length, y),
        (x - gap, y),
        colour,
        2,
        cv2.LINE_AA
    )

    # Right
    cv2.line(
        frame,
        (x + gap, y),
        (x + length, y),
        colour,
        2,
        cv2.LINE_AA
    )

    # Top
    cv2.line(
        frame,
        (x, y - length),
        (x, y - gap),
        colour,
        2,
        cv2.LINE_AA
    )

    # Bottom
    cv2.line(
        frame,
        (x, y + gap),
        (x, y + length),
        colour,
        2,
        cv2.LINE_AA
    )

    cv2.circle(
        frame,
        (x, y),
        4,
        GREEN_HUD,
        -1,
        cv2.LINE_AA
    )


# ------------------------------------------------------------
# STEERING GAUGE
# ------------------------------------------------------------

def draw_steering_gauge(
    canvas,
    cx,
    cy,
    angle
):
    """
    Futuristic steering wheel gauge.
    """

    radius = 65

    # Outer glow
    cv2.circle(
        canvas,
        (cx, cy),
        radius + 8,
        DARK_GREY,
        1,
        cv2.LINE_AA
    )

    # Main circle
    cv2.circle(
        canvas,
        (cx, cy),
        radius,
        CYAN_HUD,
        2,
        cv2.LINE_AA
    )

    # Tick marks
    for tick_angle in range(-60, 61, 30):

        radians = math.radians(tick_angle)

        x1 = int(
            cx + (radius - 8) * math.sin(radians)
        )

        y1 = int(
            cy - (radius - 8) * math.cos(radians)
        )

        x2 = int(
            cx + radius * math.sin(radians)
        )

        y2 = int(
            cy - radius * math.cos(radians)
        )

        cv2.line(
            canvas,
            (x1, y1),
            (x2, y2),
            GREY_HUD,
            1,
            cv2.LINE_AA
        )

    # Needle
    radians = math.radians(angle)

    x = int(
        cx + (radius - 12) * math.sin(radians)
    )

    y = int(
        cy - (radius - 12) * math.cos(radians)
    )

    cv2.line(
        canvas,
        (cx, cy),
        (x, y),
        YELLOW_HUD,
        4,
        cv2.LINE_AA
    )

    # Center
    cv2.circle(
        canvas,
        (cx, cy),
        7,
        GREEN_HUD,
        -1,
        cv2.LINE_AA
    )

    # Angle
    cv2.putText(
        canvas,
        f"{int(angle)}°",
        (cx - 22, cy + radius + 28),
        cv2.FONT_HERSHEY_DUPLEX,
        0.45,
        WHITE_HUD,
        1,
        cv2.LINE_AA
    )


# ------------------------------------------------------------
# TOP HEADER
# ------------------------------------------------------------

def draw_header(canvas, fps):
    """
    Draw main Gesture Console header.
    """

    width = canvas.shape[1]

    # Header background
    cv2.rectangle(
        canvas,
        (20, 18),
        (width - 20, 85),
        PANEL_BG,
        -1
    )

    # Header border
    cv2.rectangle(
        canvas,
        (20, 18),
        (width - 20, 85),
        DARK_GREY,
        1
    )

    # Cyan center line
    cv2.line(
        canvas,
        (260, 82),
        (1020, 82),
        CYAN_HUD,
        2,
        cv2.LINE_AA
    )

    # Title
    cv2.putText(
        canvas,
        "GESTURE CONSOLE",
        (45, 60),
        cv2.FONT_HERSHEY_DUPLEX,
        1.05,
        CYAN_HUD,
        2,
        cv2.LINE_AA
    )

    # FPS colour
    fps_colour = GREEN_HUD

    if fps < 25:
        fps_colour = YELLOW_HUD

    if fps < 15:
        fps_colour = RED_HUD

    # FPS box
    cv2.rectangle(
        canvas,
        (1080, 32),
        (1215, 68),
        PANEL_BG_2,
        -1
    )

    cv2.rectangle(
        canvas,
        (1080, 32),
        (1215, 68),
        fps_colour,
        1
    )

    cv2.putText(
        canvas,
        f"{int(fps)} FPS",
        (1095, 57),
        cv2.FONT_HERSHEY_DUPLEX,
        0.55,
        fps_colour,
        1,
        cv2.LINE_AA
    )


# ------------------------------------------------------------
# LEFT ACTION PANEL
# ------------------------------------------------------------

def draw_left_panel(
    canvas,
    accelerate,
    brake,
    nitro,
    direction,
    angle,
    hands
):
    """
    Draw actions and status.
    """

    x = 20
    y = 105
    w = 215
    h = 465

    draw_panel_box(
        canvas,
        x,
        y,
        w,
        h,
        "ACTIONS",
        CYAN_HUD
    )

    # Actions
    draw_action_item(
        canvas,
        x + 25,
        y + 78,
        "ACCELERATE",
        accelerate,
        GREEN_HUD
    )

    draw_action_item(
        canvas,
        x + 25,
        y + 125,
        "BRAKE",
        brake,
        RED_HUD
    )

    draw_action_item(
        canvas,
        x + 25,
        y + 172,
        "NITRO",
        nitro,
        YELLOW_HUD
    )

    # Separator
    cv2.line(
        canvas,
        (x + 15, y + 205),
        (x + w - 15, y + 205),
        DARK_GREY,
        1
    )

    # STATUS
    cv2.putText(
        canvas,
        "STATUS",
        (x + 16, y + 235),
        cv2.FONT_HERSHEY_DUPLEX,
        0.48,
        LIGHT_BLUE,
        1
    )

    # Direction
    direction_colour = WHITE_HUD

    if direction == "LEFT":
        direction_colour = GREEN_HUD

    elif direction == "RIGHT":
        direction_colour = GREEN_HUD

    elif direction == "BRAKE":
        direction_colour = RED_HUD

    cv2.putText(
        canvas,
        "DIRECTION",
        (x + 16, y + 270),
        cv2.FONT_HERSHEY_DUPLEX,
        0.36,
        GREY_HUD,
        1
    )

    cv2.putText(
        canvas,
        direction,
        (x + 16, y + 293),
        cv2.FONT_HERSHEY_DUPLEX,
        0.47,
        direction_colour,
        1
    )

    # Wheel
    cv2.putText(
        canvas,
        "WHEEL",
        (x + 16, y + 327),
        cv2.FONT_HERSHEY_DUPLEX,
        0.36,
        GREY_HUD,
        1
    )

    cv2.putText(
        canvas,
        f"{angle:.1f}°",
        (x + 16, y + 350),
        cv2.FONT_HERSHEY_DUPLEX,
        0.47,
        MAGENTA_HUD,
        1
    )

    # Hands
    cv2.putText(
        canvas,
        "HANDS",
        (x + 16, y + 384),
        cv2.FONT_HERSHEY_DUPLEX,
        0.36,
        GREY_HUD,
        1
    )

    cv2.putText(
        canvas,
        str(hands),
        (x + 16, y + 408),
        cv2.FONT_HERSHEY_DUPLEX,
        0.47,
        CYAN_HUD,
        1
    )


# ------------------------------------------------------------
# RIGHT CONTROL PANEL
# ------------------------------------------------------------

def draw_right_panel(
    canvas,
    accelerate,
    brake,
    nitro,
    direction,
    angle,
    hands,
    fps
):
    """
    Draw controls and information.
    """

    x = 1045
    y = 105
    w = 215
    h = 465

    draw_panel_box(
        canvas,
        x,
        y,
        w,
        h,
        "CONTROLS",
        BLUE_HUD
    )

    # Controls
    draw_action_item(
        canvas,
        x + 25,
        y + 78,
        "ACCELERATE",
        accelerate,
        GREEN_HUD
    )

    draw_action_item(
        canvas,
        x + 25,
        y + 125,
        "BRAKE",
        brake,
        RED_HUD
    )

    draw_action_item(
        canvas,
        x + 25,
        y + 172,
        "NITRO",
        nitro,
        YELLOW_HUD
    )

    # Separator
    cv2.line(
        canvas,
        (x + 15, y + 205),
        (x + w - 15, y + 205),
        DARK_GREY,
        1
    )

    # INFO
    cv2.putText(
        canvas,
        "INFO",
        (x + 16, y + 235),
        cv2.FONT_HERSHEY_DUPLEX,
        0.48,
        LIGHT_BLUE,
        1
    )

    # Direction
    cv2.putText(
        canvas,
        "DIRECTION",
        (x + 16, y + 270),
        cv2.FONT_HERSHEY_DUPLEX,
        0.36,
        GREY_HUD,
        1
    )

    cv2.putText(
        canvas,
        direction,
        (x + 16, y + 293),
        cv2.FONT_HERSHEY_DUPLEX,
        0.47,
        WHITE_HUD,
        1
    )

    # Wheel
    cv2.putText(
        canvas,
        "WHEEL",
        (x + 16, y + 327),
        cv2.FONT_HERSHEY_DUPLEX,
        0.36,
        GREY_HUD,
        1
    )

    cv2.putText(
        canvas,
        f"{angle:.1f}°",
        (x + 16, y + 350),
        cv2.FONT_HERSHEY_DUPLEX,
        0.47,
        MAGENTA_HUD,
        1
    )

    # Hands
    cv2.putText(
        canvas,
        "HANDS",
        (x + 16, y + 384),
        cv2.FONT_HERSHEY_DUPLEX,
        0.36,
        GREY_HUD,
        1
    )

    cv2.putText(
        canvas,
        str(hands),
        (x + 16, y + 408),
        cv2.FONT_HERSHEY_DUPLEX,
        0.47,
        CYAN_HUD,
        1
    )

    # FPS
    cv2.putText(
        canvas,
        f"{int(fps)} FPS",
        (x + 16, y + 445),
        cv2.FONT_HERSHEY_DUPLEX,
        0.40,
        GREEN_HUD,
        1
    )


# ------------------------------------------------------------
# BOTTOM STATUS BAR
# ------------------------------------------------------------

def draw_bottom_bar(
    canvas,
    accelerate,
    brake,
    nitro,
    hands
):
    """
    Draw bottom system status.
    """

    width = canvas.shape[1]
    height = canvas.shape[0]

    x = 250
    y = 595
    w = 780
    h = 85

    # Determine system status
    if hands == 0:
        status = "READY"
        colour = WHITE_HUD

    elif brake:
        status = "BRAKING"
        colour = RED_HUD

    elif nitro:
        status = "NITRO BOOST"
        colour = YELLOW_HUD

    elif accelerate:
        status = "DRIVING"
        colour = GREEN_HUD

    elif hands >= 2:
        status = "VIRTUAL STEERING"
        colour = CYAN_HUD

    else:
        status = "ACTIVE"
        colour = CYAN_HUD

    # Main panel
    cv2.rectangle(
        canvas,
        (x, y),
        (x + w, y + h),
        PANEL_BG,
        -1
    )

    cv2.rectangle(
        canvas,
        (x, y),
        (x + w, y + h),
        DARK_GREY,
        1
    )

    draw_corner_brackets(
        canvas,
        x,
        y,
        w,
        h,
        colour,
        20,
        2
    )

    # Status text
    cv2.putText(
        canvas,
        status,
        (x + 32, y + 53),
        cv2.FONT_HERSHEY_DUPLEX,
        0.82,
        colour,
        2,
        cv2.LINE_AA
    )

    # Decorative bars
    bar_x = x + w - 250

    for i in range(5):
        cv2.rectangle(
            canvas,
            (
                bar_x + i * 38,
                y + 32
            ),
            (
                bar_x + i * 38 + 25,
                y + 48
            ),
            colour if i < 3 else DARK_GREY,
            -1
        )


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    # Launch Need for Speed Most Wanted automatically.
    launch_need_for_speed()

    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("Camera could not be opened.")
        return

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        FRAME_WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        FRAME_HEIGHT
    )

    tracker = HandTracker(
        max_hands=MAX_HANDS,
        detection_confidence=MIN_DETECTION_CONFIDENCE,
        tracking_confidence=MIN_TRACKING_CONFIDENCE
    )

    detector = GestureDetector()

    steering = SteeringWheel(
        frame_width=FRAME_WIDTH,
        threshold=STEERING_THRESHOLD,
        smoothing=STEERING_SMOOTHING
    )

    keyboard = KeyboardController()

    previous = time.time()

    while True:

        success, frame = cap.read()

        if not success:
            break

        # Mirror camera
        if MIRROR_CAMERA:
            frame = cv2.flip(frame, 1)

        height, width = frame.shape[:2]

        steering.update_frame_width(width)

        # ----------------------------------------------------
        # HAND TRACKING
        # ----------------------------------------------------

        results = tracker.process(frame)

        if SHOW_LANDMARKS:
            tracker.draw(frame, results)

        fists = []

        angle = 0

        direction = "STRAIGHT"

        accelerate = False
        brake = False
        nitro = False

        # ----------------------------------------------------
        # GESTURE PROCESSING
        # ----------------------------------------------------

        if results.multi_hand_landmarks:

            data = detector.detect(
                results.multi_hand_landmarks,
                results.multi_handedness,
                width,
                height
            )

            fists = data["fists"]

            # ------------------------------------------------
            # ACCELERATE
            # ------------------------------------------------

            if data["accelerate"]:

                keyboard.accelerate()

                accelerate = True

            else:

                keyboard.stop_accelerating()

            # ------------------------------------------------
            # BRAKE
            # ------------------------------------------------

            if data["brake"]:

                keyboard.brake()

                brake = True

            else:

                keyboard.release_brake()

            # ------------------------------------------------
            # NITRO
            # ------------------------------------------------

            if data["nitro"]:

                keyboard.nitro()

                nitro = True

            else:

                keyboard.release_nitro()

            # ------------------------------------------------
            # VIRTUAL STEERING
            # ------------------------------------------------

            if data["steering_wheel"]:

                fists = sorted(
                    fists,
                    key=lambda p: p[0]
                )

                if len(fists) >= 2:

                    left = fists[0]
                    right = fists[1]

                    angle, _, centre = steering.calculate(
                        left,
                        right
                    )

                    keyboard.steer(angle)

                    if angle < -8:

                        direction = "LEFT"

                    elif angle > 8:

                        direction = "RIGHT"

                    else:

                        direction = "STRAIGHT"

                    # Steering line
                    if SHOW_STEERING_LINE:

                        cv2.line(
                            frame,
                            left,
                            right,
                            CYAN_HUD,
                            4,
                            cv2.LINE_AA
                        )

                    # Left hand
                    cv2.circle(
                        frame,
                        left,
                        15,
                        GREEN_HUD,
                        -1,
                        cv2.LINE_AA
                    )

                    # Right hand
                    cv2.circle(
                        frame,
                        right,
                        15,
                        GREEN_HUD,
                        -1,
                        cv2.LINE_AA
                    )

                    # Centre
                    cv2.circle(
                        frame,
                        centre,
                        10,
                        YELLOW_HUD,
                        -1,
                        cv2.LINE_AA
                    )

            else:

                steering.reset()

                if brake:

                    keyboard.straighten()

                    direction = "BRAKE"

                elif data["left_open"]:

                    keyboard.steer_left()

                    direction = "LEFT"

                elif data["right_open"]:

                    keyboard.steer_right()

                    direction = "RIGHT"

                else:

                    keyboard.straighten()

                    direction = "STRAIGHT"

            # ------------------------------------------------
            # DRAW HAND POSITIONS
            # ------------------------------------------------

            for x, y in fists:

                cv2.circle(
                    frame,
                    (x, y),
                    15,
                    GREEN_HUD,
                    -1,
                    cv2.LINE_AA
                )

        else:

            keyboard.release_all()

            steering.reset()

            accelerate = False
            brake = False
            nitro = False

            angle = 0

            direction = "NO HANDS"

        # ----------------------------------------------------
        # FPS
        # ----------------------------------------------------

        now = time.time()

        fps = 1 / max(
            now - previous,
            0.0001
        )

        previous = now

        # ====================================================
        # CREATE SCI-FI HUD CANVAS
        # ====================================================

        canvas_width = 1280
        canvas_height = 720

        canvas = np.zeros(
            (
                canvas_height,
                canvas_width,
                3
            ),
            dtype="uint8"
        )

        # Background
        canvas[:] = HUD_BG

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        draw_header(
            canvas,
            fps
        )

        # ----------------------------------------------------
        # CENTRAL CAMERA
        # ----------------------------------------------------

        video_x, video_y, video_w, video_h = draw_video_panel(
            canvas,
            frame
        )

        # Crosshair in video
        crosshair_x = video_x + video_w // 2
        crosshair_y = video_y + video_h // 2

        draw_crosshair(
            canvas,
            crosshair_x,
            crosshair_y
        )

        # ----------------------------------------------------
        # LEFT PANEL
        # ----------------------------------------------------

        draw_left_panel(
            canvas,
            accelerate,
            brake,
            nitro,
            direction,
            angle,
            len(fists)
        )

        # ----------------------------------------------------
        # RIGHT PANEL
        # ----------------------------------------------------

        draw_right_panel(
            canvas,
            accelerate,
            brake,
            nitro,
            direction,
            angle,
            len(fists),
            fps
        )

        # ----------------------------------------------------
        # STEERING GAUGE
        # ----------------------------------------------------

        draw_steering_gauge(
            canvas,
            640,
            635,
            angle
        )

        # ----------------------------------------------------
        # BOTTOM STATUS
        # ----------------------------------------------------

        draw_bottom_bar(
            canvas,
            accelerate,
            brake,
            nitro,
            len(fists)
        )

        # ----------------------------------------------------
        # DIRECTION INDICATORS
        # ----------------------------------------------------

        if direction == "LEFT":

            cv2.arrowedLine(
                canvas,
                (470, 315),
                (425, 315),
                GREEN_HUD,
                4,
                cv2.LINE_AA,
                tipLength=0.35
            )

        elif direction == "RIGHT":

            cv2.arrowedLine(
                canvas,
                (810, 315),
                (855, 315),
                GREEN_HUD,
                4,
                cv2.LINE_AA,
                tipLength=0.35
            )

        # ----------------------------------------------------
        # SMALL SYSTEM TEXT
        # ----------------------------------------------------

        cv2.putText(
            canvas,
            "GESTURE ENGINE // ONLINE",
            (35, 705),
            cv2.FONT_HERSHEY_DUPLEX,
            0.35,
            GREY_HUD,
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            canvas,
            "MEDIAPIPE",
            (1100, 705),
            cv2.FONT_HERSHEY_DUPLEX,
            0.35,
            GREY_HUD,
            1,
            cv2.LINE_AA
        )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        cv2.namedWindow(
            WINDOW_NAME,
            cv2.WINDOW_NORMAL
        )

        cv2.setWindowProperty(
            WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )

        cv2.imshow(
            WINDOW_NAME,
            canvas
        )

        # Create/update the OpenCV window before attempting to embed NFS.
        # Only perform the actual re-parenting once; after re-parenting, the
        # NFS renderer is a child window and no longer appears in EnumWindows.
        if not _nfs_embed_state.get("hwnd"):
            console_hwnd = win32gui.FindWindow(None, WINDOW_NAME)
            if console_hwnd:
                embed_need_for_speed(console_hwnd)
            else:
                print(f"Could not find GestureConsole window: {WINDOW_NAME}")

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == 27 or key == ord("q"):
            break

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    restore_need_for_speed()

    keyboard.release_all()

    tracker.close()

    cap.release()

    cv2.destroyAllWindows()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()