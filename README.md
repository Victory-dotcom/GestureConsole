# GestureConsole

A Python-based gesture-control application that combines **computer
vision, hand tracking, gesture recognition, keyboard control, steering
input, and a custom HUD interface**.

GestureConsole is designed to provide a hands-free control layer for
desktop applications and games. The current project integrates
**MediaPipe hand tracking** and **OpenCV** for real-time camera
processing and includes Windows keyboard/control integration.

The project also contains experimental integration for **Need for Speed:
Most Wanted Black Edition**, where the game's Direct3D renderer can be
embedded into the GestureConsole HUD.

------------------------------------------------------------------------

## Table of Contents

-   [Overview](#overview)
-   [Features](#features)
-   [How It Works](#how-it-works)
-   [Project Structure](#project-structure)
-   [Requirements](#requirements)
-   [Python Version](#python-version)
-   [Installation](#installation)
-   [Virtual Environment](#virtual-environment)
-   [Dependencies](#dependencies)
-   [Configuration](#configuration)
-   [Running the Application](#running-the-application)
-   [Gesture Detection](#gesture-detection)
-   [Steering Control](#steering-control)
-   [Keyboard Control](#keyboard-control)
-   [Need for Speed Integration](#need-for-speed-integration)
-   [NFS Embedding Architecture](#nfs-embedding-architecture)
-   [Important NFS Requirements](#important-nfs-requirements)
-   [Troubleshooting](#troubleshooting)
-   [Performance](#performance)
-   [Development](#development)
-   [Building the Application](#building-the-application)
-   [Git and GitHub](#git-and-github)
-   [Security and Repository Hygiene](#security-and-repository-hygiene)
-   [Known Limitations](#known-limitations)
-   [Future Improvements](#future-improvements)
-   [License](#license)

------------------------------------------------------------------------

## Overview

GestureConsole uses a webcam to detect a user's hand and interpret hand
movements as control input.

The application is built around the following pipeline:

``` text
Webcam
   │
   ▼
OpenCV
   │
   ▼
MediaPipe Hand Tracking
   │
   ▼
Gesture Detection
   │
   ├──► Keyboard Controls
   │
   └──► Steering Control
            │
            ▼
      Desktop / Game
```

The application also renders a custom dashboard-style interface
containing the camera/visual area, gesture information, steering
information, status information, and other HUD elements.

For the NFS integration, the architecture becomes:

``` text
Need for Speed
      │
      ▼
speed.exe
      │
      ▼
Direct3D Renderer
      │
      ▼
D3DProxyWindow
      │
      ▼
Windows API / pywin32
      │
      ▼
GestureConsole HUD
```

------------------------------------------------------------------------

# Features

## Real-Time Hand Tracking

GestureConsole uses MediaPipe to detect hand landmarks from a webcam
stream.

The hand tracker provides positional information that can be used by the
gesture detector and steering system.

## Gesture Recognition

The project contains a dedicated gesture detection module:

``` text
gesture_detector.py
```

This module is responsible for interpreting hand landmark information
and converting it into application-level gestures.

## Steering Control

The steering system is implemented in:

``` text
steering.py
```

The steering module is designed to translate hand movement into steering
input.

This allows the user's hand position to act as a virtual steering wheel.

## Keyboard Control

Keyboard interaction is handled by:

``` text
keyboard_controller.py
```

The project uses Windows input functionality to allow detected gestures
to trigger keyboard controls.

## Custom HUD

The main application renders a custom dashboard/HUD using OpenCV.

The interface includes:

-   Header area
-   Central display area
-   Left information panel
-   Right information panel
-   Steering visualization
-   Status information
-   Gesture information
-   Camera/visual processing area

The central display area is currently designed around:

``` text
Position:
X = 250
Y = 105

Size:
Width  = 780
Height = 465
```

## Need for Speed Integration

The project includes experimental Windows integration for:

**Need for Speed: Most Wanted Black Edition**

The application can locate the running `speed.exe` process and interact
with its Direct3D rendering window.

The current integration identifies the game's:

``` text
D3DProxyWindow
```

and embeds/repositions it into the GestureConsole central display area.

------------------------------------------------------------------------

# How It Works

The application starts by initializing the required computer-vision and
control components.

The general execution flow is:

``` text
Start GestureConsole
       │
       ▼
Initialize Camera
       │
       ▼
Initialize HandTracker
       │
       ▼
Initialize GestureDetector
       │
       ▼
Initialize SteeringWheel
       │
       ▼
Initialize KeyboardController
       │
       ▼
Launch / Detect Need for Speed
       │
       ▼
Find NFS Direct3D Window
       │
       ▼
Embed Renderer
       │
       ▼
Start Real-Time Processing Loop
       │
       ├── Capture Camera Frame
       ├── Detect Hand
       ├── Detect Gesture
       ├── Calculate Steering
       ├── Send Keyboard/Input Events
       └── Render HUD
       │
       ▼
Display GestureConsole
```

------------------------------------------------------------------------

# Project Structure

``` text
GestureConsole/
│
├── main.py
├── config.py
├── hand_tracker.py
├── gesture_detector.py
├── steering.py
├── keyboard_controller.py
├── requirements.txt
├── README.md
├── cpu.png
├── .gitignore
│
└── .venv/
```

### `main.py`

The main application entry point.

Responsibilities include:

-   Starting the application
-   Initializing OpenCV
-   Initializing the hand tracker
-   Initializing gesture detection
-   Initializing steering
-   Initializing keyboard control
-   Rendering the HUD
-   Processing camera frames
-   Integrating the NFS renderer
-   Handling application shutdown

### `config.py`

Contains application configuration and constants used by the other
modules.

### `hand_tracker.py`

Contains the hand-tracking implementation.

This module works with MediaPipe to detect hand landmarks from camera
frames.

### `gesture_detector.py`

Contains gesture-recognition logic.

The detected hand landmarks are interpreted to determine the current
gesture/control state.

### `steering.py`

Contains virtual steering functionality.

The module converts hand movement into steering information.

### `keyboard_controller.py`

Contains keyboard input functionality used to send controls to Windows
applications.

### `requirements.txt`

Contains Python dependencies required by the application.

### `cpu.png`

Project image/resource currently included in the repository.

------------------------------------------------------------------------

# Requirements

## Operating System

The current project is designed primarily for:

**Windows 10 / Windows 11**

Windows is required for the current keyboard/input and NFS
window-management integration.

## Hardware

Recommended:

-   Webcam
-   Modern CPU
-   At least 8 GB RAM
-   Dedicated GPU recommended for gaming
-   Functional keyboard

A 720p or better webcam is recommended for reliable hand tracking.

------------------------------------------------------------------------

# Python Version

The project should currently be run with:

``` text
Python 3.12
```

Python 3.12 was selected because the project's MediaPipe setup works
with this environment.

The project should not be assumed to support every newer Python version
without testing.

Check your Python version:

``` powershell
python --version
```

Or:

``` powershell
py -3.12 --version
```

------------------------------------------------------------------------

# Installation

Clone the repository:

``` powershell
git clone https://github.com/YOUR_USERNAME/GestureConsole.git
```

Enter the project:

``` powershell
cd GestureConsole
```

Create a Python 3.12 virtual environment:

``` powershell
py -3.12 -m venv .venv
```

------------------------------------------------------------------------

# Virtual Environment

Activate the virtual environment if your PowerShell execution policy
allows it:

``` powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run Python directly from the
virtual environment without activating it:

``` powershell
.\.venv\Scripts\python.exe
```

This method works without changing the system PowerShell execution
policy.

------------------------------------------------------------------------

# Dependencies

The project uses packages including:

-   OpenCV
-   MediaPipe
-   NumPy
-   PyDirectInput
-   Matplotlib
-   pywin32

Install dependencies using:

``` powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If MediaPipe compatibility requires the project-tested version, install:

``` powershell
.\.venv\Scripts\python.exe -m pip install mediapipe==0.10.21
```

Install Windows API support:

``` powershell
.\.venv\Scripts\python.exe -m pip install pywin32
```

------------------------------------------------------------------------

# Configuration

Before running the application, review:

``` text
config.py
```

Configuration may include:

-   Camera settings
-   Display settings
-   Gesture thresholds
-   HUD settings
-   Window settings
-   Control settings

The exact configuration should be kept centralized so that the main
application does not need to be modified for every parameter change.

------------------------------------------------------------------------

# Running the Application

From the project directory:

``` powershell
.\.venv\Scripts\python.exe main.py
```

The application should initialize:

1.  OpenCV
2.  Webcam
3.  MediaPipe
4.  Hand tracking
5.  Gesture detection
6.  Steering
7.  Keyboard control
8.  HUD rendering

If NFS integration is enabled, the application will also attempt to
locate or launch the configured NFS executable.

------------------------------------------------------------------------

# Gesture Detection

Gesture processing is handled by the combination of:

``` text
hand_tracker.py
gesture_detector.py
```

The hand tracker detects the hand and produces landmark coordinates.

The gesture detector then interprets those coordinates.

Conceptually:

``` text
Camera Frame
     │
     ▼
Hand Detection
     │
     ▼
21 Hand Landmarks
     │
     ▼
Gesture Analysis
     │
     ▼
Gesture State
```

The resulting gesture state can then be used by:

``` text
KeyboardController
```

and:

``` text
SteeringWheel
```

------------------------------------------------------------------------

# Steering Control

The steering system provides a virtual steering mechanism.

The user's hand position can be interpreted as:

``` text
Left        Center        Right
  ◄───────────┼───────────►
```

The steering module converts the detected position into control values.

This is particularly useful for driving games where the user's hand acts
as a virtual steering wheel.

------------------------------------------------------------------------

# Keyboard Control

The keyboard controller is responsible for translating detected gestures
into keyboard input.

The project uses Windows-compatible input functionality.

Typical architecture:

``` text
Gesture
   │
   ▼
GestureDetector
   │
   ▼
KeyboardController
   │
   ▼
Windows Keyboard Input
   │
   ▼
Application / Game
```

------------------------------------------------------------------------

# Need for Speed Integration

GestureConsole contains experimental integration with:

**Need for Speed: Most Wanted Black Edition**

The executable used during development is:

``` text
speed.exe
```

The game executable should remain installed separately from this
repository.

Example local installation path:

``` text
D:\NeedForSpeedMostWantedBlackEdition\
Need For Speed Most Wanted Black Edition\
Need For Speed Most Wanted Black Edition\
speed.exe
```

Do **not** commit the game executable or game installation files to
GitHub.

------------------------------------------------------------------------

# NFS Embedding Architecture

The NFS integration uses Windows window-management APIs through
`pywin32`.

The application detects the NFS process:

``` text
speed.exe
```

and obtains its process ID.

It then enumerates Windows belonging to that process.

During testing, the renderer was identified as:

``` text
Title:
D3DProxyWindow

Class:
D3DProxyWindow

Original size:
1920 × 1080
```

The renderer can then be re-parented into the GestureConsole window.

The target HUD area is:

``` text
X = 250
Y = 105
Width = 780
Height = 465
```

Therefore:

``` text
NFS Renderer
┌──────────────────────────────────────────────┐
│                                              │
│              780 × 465                       │
│                                              │
└──────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# Important NFS Requirements

The NFS game is external software and is **not included in this
repository**.

You must have your own legally obtained installation of the game.

GestureConsole expects the game executable to exist at the configured
path.

If your installation is somewhere else, update the executable path in
the application configuration/code.

For example:

``` python
EXE_PATH = r"D:\Path\To\speed.exe"
```

Do not commit personal absolute paths containing sensitive information
if the repository is public.

For a public repository, it is preferable to use a configurable path
rather than hard-coding a developer-specific drive.

------------------------------------------------------------------------

# Troubleshooting

## MediaPipe does not install

Check Python:

``` powershell
py -0p
```

Use Python 3.12:

``` powershell
py -3.12 -m venv .venv
```

Then:

``` powershell
.\.venv\Scripts\python.exe -m pip install mediapipe==0.10.21
```

------------------------------------------------------------------------

## PowerShell refuses to activate `.venv`

You may see an execution-policy error.

You can avoid activation completely:

``` powershell
.\.venv\Scripts\python.exe main.py
```

------------------------------------------------------------------------

## NFS is not running

Check:

``` powershell
Get-Process speed -ErrorAction SilentlyContinue
```

You can test the executable directly:

``` powershell
Test-Path "D:\Path\To\speed.exe"
```

A successful result is:

``` text
True
```

------------------------------------------------------------------------

## NFS process exists but no normal game window is found

NFS may expose a Direct3D rendering window rather than a conventional
visible top-level game window.

During development, the renderer was identified as:

``` text
D3DProxyWindow
```

The application therefore needs to account for the renderer window
instead of relying only on a visible window title.

------------------------------------------------------------------------

## NFS embedding reports success but the center is black

This can occur with older DirectX applications when their rendering
context does not behave normally after window re-parenting.

Possible causes include:

-   Fullscreen rendering
-   DirectX compatibility behavior
-   Window re-parenting
-   Rendering context changes
-   GPU driver behavior
-   Game-specific restrictions

Try running the game in windowed mode if supported.

------------------------------------------------------------------------

## GestureConsole becomes slow

Real-time processing combines:

-   Webcam capture
-   MediaPipe inference
-   OpenCV rendering
-   HUD effects
-   Windows input
-   NFS Direct3D rendering

This can create significant CPU/GPU load.

Potential improvements include:

-   Lowering camera resolution
-   Reducing HUD transparency effects
-   Reducing frame-processing frequency
-   Avoiding unnecessary `cv2.addWeighted()` operations
-   Rendering static HUD elements less frequently
-   Using GPU acceleration where supported

------------------------------------------------------------------------

# Performance

GestureConsole performs real-time computer vision, so performance
depends on:

-   CPU
-   GPU
-   Webcam resolution
-   Camera frame rate
-   MediaPipe processing time
-   OpenCV rendering
-   Number of HUD effects
-   Game rendering settings

For better performance:

``` text
Lower resolution
      +
Efficient gesture processing
      +
Reduced unnecessary redraws
      +
Appropriate game graphics settings
```

can significantly reduce system load.

------------------------------------------------------------------------

# Development

Create a development environment:

``` powershell
py -3.12 -m venv .venv
```

Install dependencies:

``` powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run:

``` powershell
.\.venv\Scripts\python.exe main.py
```

Check Git:

``` powershell
git status
```

Create a branch for new work:

``` powershell
git checkout -b feature/my-feature
```

Commit changes:

``` powershell
git add .
git commit -m "Add my feature"
```

Push:

``` powershell
git push -u origin feature/my-feature
```

------------------------------------------------------------------------

# Building the Application

The repository contains PyInstaller-related files from development.

If you want to build an executable, first install PyInstaller:

``` powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
```

A build can then be created using an appropriate PyInstaller
configuration.

Generated folders such as:

``` text
build/
dist/
```

should normally not be committed to Git.

They are generated artifacts and are already excluded through
`.gitignore`.

------------------------------------------------------------------------

# Git and GitHub

Initialize Git:

``` powershell
git init
```

Check the repository:

``` powershell
git status
```

Add files:

``` powershell
git add .
```

Commit:

``` powershell
git commit -m "Initial GestureConsole implementation"
```

Create the GitHub repository with GitHub CLI:

``` powershell
gh repo create GestureConsole --public --source=. --remote=origin --push
```

Open it:

``` powershell
gh repo view --web
```

------------------------------------------------------------------------

# Security and Repository Hygiene

Do not commit:

-   `.venv/`
-   `.venv312/`
-   `build/`
-   `dist/`
-   `.env`
-   API keys
-   passwords
-   private tokens
-   personal credentials
-   game installation files
-   copyrighted game binaries

Use `.gitignore` to prevent accidental commits.

Check before pushing:

``` powershell
git status
```

If you accidentally staged a sensitive file:

``` powershell
git restore --staged filename
```

------------------------------------------------------------------------

# Known Limitations

The current project has several areas that may require additional
development.

### DirectX Embedding

Embedding an older DirectX game into another application can be
dependent on how the game creates and manages its rendering context.

### Windows Dependency

The current input and window-embedding functionality is
Windows-specific.

### MediaPipe Compatibility

The currently tested environment uses Python 3.12 and MediaPipe 0.10.21.

### Performance

The combination of real-time computer vision, HUD rendering, and game
rendering can increase CPU/GPU usage.

### Hard-Coded Paths

The NFS executable path may need to be made configurable before the
project is distributed to other users.

------------------------------------------------------------------------

# Future Improvements

Potential future improvements include:

-   Configurable NFS executable path
-   Automatic NFS installation detection
-   Better DirectX embedding compatibility
-   Windowed/fullscreen mode detection
-   Improved gesture calibration
-   Gesture sensitivity settings
-   Multiple gesture profiles
-   Game-specific control profiles
-   Improved steering smoothing
-   FPS monitoring
-   CPU/GPU usage monitoring
-   Reduced HUD rendering overhead
-   Settings interface
-   User-configurable keyboard mappings
-   Support for additional games
-   Better error handling
-   Logging system
-   Automatic environment setup
-   Cross-application gesture profiles

------------------------------------------------------------------------

# Example Workflow

A typical session can look like:

``` text
1. Connect webcam
        │
        ▼
2. Start GestureConsole
        │
        ▼
3. Open / detect NFS
        │
        ▼
4. Detect user's hand
        │
        ▼
5. Calculate gesture
        │
        ▼
6. Calculate steering
        │
        ▼
7. Send keyboard/input commands
        │
        ▼
8. Render HUD
        │
        ▼
9. Continue real-time control
```

------------------------------------------------------------------------

# Project Status

GestureConsole is an active development project.

Current components include:

-   [x] Python application
-   [x] OpenCV camera processing
-   [x] MediaPipe hand tracking
-   [x] Gesture detection
-   [x] Steering module
-   [x] Keyboard controller
-   [x] Custom HUD
-   [x] Python 3.12 environment
-   [x] MediaPipe 0.10.21 environment
-   [x] Windows `pywin32` integration
-   [x] NFS process detection
-   [x] NFS Direct3D renderer detection
-   [x] Experimental NFS renderer embedding
-   [ ] Fully portable NFS configuration
-   [ ] Cross-game support
-   [ ] Advanced performance optimization

------------------------------------------------------------------------

# License

No license has been specified for this project yet.

Until a license is added, the repository should not be assumed to grant
broad permission to copy, modify, distribute, or sublicense the project.

If you intend to publish the project as open source, add an appropriate
license file such as:

``` text
LICENSE
```

and update this section accordingly.

------------------------------------------------------------------------

# Author

**GestureConsole Project**

Built as a Windows-based computer-vision and gesture-control application
using Python, OpenCV, MediaPipe, and Windows input/window-management
APIs.
