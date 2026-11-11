---
name: td-multi-layer-timeline
description: Specialized guide for using, integrating, customizing, and automating the TouchDesigner Multi-Layer Timeline (TD-MTL) system. Covers 3D GPU instanced timeline architecture, cue lifecycles, Timer CHOP / Segment DAT engine, playback synchronization with TOPs/DMX/OSC, callbacks, and TDMCP remote control.
---

# TouchDesigner Multi-Layer Timeline (TD-MTL) Skill

## Overview
**TD-MTL** is a GPU-accelerated, multi-layer sequencing timeline for TouchDesigner created by Tim Franklin and Brian Alexander, modernized with advanced live-performance and multi-screen orchestration features. Rather than using conventional heavy 2D UI components, it renders the entire timeline canvas, tracks, and cues in a **3D GPU instanced environment**, delivering high performance (60 fps), precise scrubbing, and multi-track orchestration.

---

## Architecture & Core Mechanics

### 1. 3D Instanced Rendering Architecture
- **Zero-UI-Overhead Instancing:** Cues, layers, grid lines, and playhead are not individual COMP nodes. They are instanced geometry (`Geometry COMP` + instancing tables/CHOPs) driven by an `instance id`.
- **Dual-Camera Layout:**
  - `Main Camera`: Controls the timeline canvas and cues. Supports zoom and horizontal scrubbing following the playhead.
  - `Settings / Layers Camera`: Orthographic camera focused on the left sidebar track headers. It locks horizontal movement while mirroring vertical camera scroll.
- **Procedural Shaders:**
  - **Outlines:** Cue selection outlines (White = active selected cue, Yellow = multi-selected cues) are evaluated directly in GLSL fragment shaders without requiring additional texture passes.
  - **Tweens / Fades:** Fade-in and fade-out ramps use an instanced 4-point line primitive deformed in the vertex shader via custom attributes (`FadeIn`, `FadeOut`, `Length`, `Height`).
- **Picking via `RenderPick`:** User interactions (click, drag, multi-select, resize) are resolved through `RenderPick` querying the `instance id` directly on the GPU render buffer.

### 2. Timing & Transport Engine
- **Timer Component (`Time.tox`):**
  - Uses TouchDesigner's `Timer CHOP` backed by a dynamic `Segment DAT`.
  - Automatically maps each cue's start time and duration to discrete segments.
  - Generates:
    - `preload pulse`: Pre-roll trigger sent ahead of the cue to pre-buffer media (`Movie File In TOP`) and avoid dropped frames.
    - `trigger pulse`: Fires on cue boundary for OSC/sACN/DMX/MIDI dispatch.
    - `normalized time / ramp`: Normalized 0.0 to 1.0 progress for crossfading and parameter animation.
  - Outputs timecodes (`SMPTE / frames / milliseconds`) synchronized across the project.

### 3. Dual-Screen Video Routing & Aspect Ratio System
- **Output Routing:** Every cue or scene can be independently assigned to **Output 1**, **Output 2**, or both simultaneously.
- **Aspect Ratio Modes:**
  - `Fit`: Letterboxed/pillarboxed preserving original aspect ratio.
  - `Fill`: Stretched to target display resolution.
  - `Fill Outside`: Scaled to cover the entire canvas without distortion (cropped edges).
  - `Custom Pixels`: Exact custom resolution mapping.
- **Preview Monitoring:** `container_Preview` provides an integrated split-screen preview (`switch_preview` / `layout_split`) displaying Output 1 and Output 2 side-by-side or individually.

### 4. Dedicated Audio Track & Visualizer Engine
- **Component Path:** `/Multi_Layer_Timeline/container_AudioTrack`
- **Waveform & Spectrogram GLSL Engine:**
  - `glsl_view`: Procedural shader rendering time-domain waveform and frequency-domain spectrogram in real time with high-DPI resolution.
  - Viewport coordinates (`uTimelineView.xy`) automatically bind to `cam1` zoom and pan coordinates for pixel-perfect scrub alignment.
- **Stereo Metering & Level Control:**
  - `meter_comp`: Hardware-accelerated stereo peak meter with peak hold indicators.
  - Gain and panning controlled through `math_gain` and `math_pan`.
  - Solo, Mute, and dynamic playhead scrubbing synchronization.
- **Auto-Fit Timeline Duration:**
  - Automatically analyzes loaded audio files and sets `Timeline.par.Duration` to match the exact duration of the audio, preventing truncated playback.

---

## Performance Engineering & Vulkan Contracts (60 FPS Guaranteed)

### 1. The Vulkan Dynamic Texture Reallocation Trap
- **Antipattern:** Setting `outputresolution = parpanel` on TOPs inside Container COMPs whose width or height changes interactively (such as sliders, range bars, splitters, or resizable panels).
- **Why it Fails:** In TouchDesigner 2025+ (Vulkan), every pixel change triggers texture destruction (`vkDestroyImage`, `vkFreeMemory`) and new texture allocation (`vkCreateImage`, `vkAllocateMemory`). At 60 Hz, this causes massive GPU pipeline flushes and drops frame rates from 60 to 15 FPS.
- **Contract / Solution (Fixed-Resolution Shader Pattern):**
  - UI TOPs must use a **fixed custom resolution** (e.g. `512x32`) with `outputresolution = custom`.
  - Parent Container COMP sets `topfill = horizontal` (or `stretch`).
  - Pass the panel's physical width as a uniform float `uParams.x = parent().width`.
  - In GLSL, compute pixel coordinates as `float px = vUV.st.x * uParams.x;`.
  - Handles, borders, and grips are evaluated in pixel space in GLSL.
  - **Result:** 0 texture reallocations, 0.01 ms GPU cook time, rock-solid 60 FPS.

### 2. Synchronous Panel Layout Stall in Python
- **Antipattern:** Reading `.width` or `.height` on a Container COMP inside per-frame scripts (`whileOn`, mouse drag callbacks) right after setting parameters or anchors (e.g. `parent().par.Sliderwidth.val = self.Bar.width`).
- **Why it Fails:** Reading layout attributes mid-frame forces TouchDesigner to synchronously solve the CPU layout hierarchy, interrupting the render loop.
- **Contract / Solution:** Never query `.width` or `.height` inside `whileOn` loops for unused parameters. Compute widths procedurally from normalized coordinates (`parent(2).width * (rAnchor - lAnchor)`), or read it once on mouse-down (`onOffToOn`).

### 3. Redundant Parameter Dirtying (`whileOn` Motion Guard)
- **Antipattern:** Calling parameter modifications in `whileOn` callbacks every frame even when the mouse is stationary.
- **Contract / Solution:** Always implement a motion guard:
  ```python
  currentU = self.ownerComp.panel.insideu.val
  if self._lastU is not None and abs(currentU - self._lastU) < 1e-6:
      return
  self._lastU = currentU
  ```
  Reset `_lastU = None` in `onOffToOn` and `onOnToOff`.

### 4. Interactive Cue Trimming & Dragging (`Transformer.py`)
- **Dual-Edge Trimming:**
  - Left edge drag ($\le 6$ px): Trims cue start time without moving end time (`CanStretchLeft`).
  - Right edge drag ($\ge \text{width} - 6$ px): Trims cue duration (`CanStretch`).
  - Body drag: Moves the entire cue across time and layers.
- **Click Precedence:** Edge clicks must strictly supersede scene button triggers (`is_scene_btn = False`) to prevent accidental editor window launches during cue resizing.

---

## Component Layout & File Map

```
Touchdesigner-Multi-Layer-Timeline/
├── Release/
│   └── Multi_Layer_Timeline.tox     # Self-contained master component (drag & drop into TD)
├── TD_Multi-Layer-Timeline.V7.toe   # Reference master project
├── v1.11.toe                        # Current production release TOE
├── Tox/
│   ├── Master/                      # Master timeline container and subcomponents
│   ├── Timeline3D/
│   │   ├── Project/                 # Project state, CueSpec, Manager.py, ParWriter, Saver
│   │   ├── Render/                  # GLSL shaders, SOP instancing, dual-camera render setup
│   │   ├── Render Pick/             # Mouse interaction: Bounds, Transformer, Snapper, Selection
│   │   ├── Time/                    # Segment DAT builder & Timer CHOP transport
│   │   ├── Layers/                  # Track definitions & layer properties
│   │   └── Playback/                # Playback state sync & dual output routing
│   ├── Callbacks/
│   │   └── Main_Callbacks_Template.py # Hook script for application triggers
│   └── Transport/                   # Transport bar controls (Play, Pause, Stop, Scrub)
└── TDMCP.tox                        # Agent MCP server bridge for AI-driven inspection/edits
```

---

## Working with Cues (`CueSpec` & `Manager`)

### Cue Attributes (`CueSpec`)
Each cue instance stores:
- `Cuetype`: `'Media'`, `'Tox'`, `'TCP/IP'`, `'OSC'`, `'Custom'`
- `Title`: Label rendered above or inside the cue
- `Starttime`: Timestamp/frame where the cue begins
- `Cuelength`: Total duration of the cue
- `Fadeinoutduration`: Tuple `(fade_in_time, fade_out_time)`
- `Layer`: Zero-based track index
- `Backgroundcolor`: RGBA tuple
- `Imagefile` / `Thumbnail`: Media asset reference path
- `Output`: `1` (Output 1) or `2` (Output 2)
- `Aspect`: `'fit'`, `'fill'`, `'fill_outside'`, or `'custom'`

### Adding & Modifying Cues via Python
```python
manager = op('/Multi_Layer_Timeline/Timeline3D/Project').ext.Manager

spec = op('/Multi_Layer_Timeline/Timeline3D/Project').mod.CueSpec.CueSpec(
    Title='StageVisual',
    Cuetype='Media',
    Starttime=0.0,
    Cuelength=12.0,
    Fadeinoutduration=(1.0, 1.0),
    Layer=0,
    Backgroundcolor=(0.15, 0.45, 0.85, 1.0)
)

manager.AddCue(cueType='Media', name='cue_visual1', cueSpec=spec)
```

---

## Keyboard Shortcuts & Navigation

| Action | Shortcut |
| :--- | :--- |
| **Zoom In / Out** | Range slider right/left handles, `Alt + Mouse Wheel`, or `Ctrl + + / -` |
| **Pan Canvas** | Range slider center track, `Shift + Mouse Wheel` (horizontal) / `Mouse Wheel` (vertical) |
| **Trim Cue Start** | Click & drag within 6px of the left edge of a cue |
| **Trim Cue End** | Click & drag within 6px of the right edge of a cue |
| **Multi-Select** | Hold `Shift` while clicking cues |
| **Snap to Playhead** | Hold `Ctrl + Alt` while dragging a cue |
| **Snap to Increments** | Hold `Ctrl` while dragging a cue |
| **Copy Selected Cues** | `Ctrl + C` (pastes starting at current playhead) |
| **Delete Selected Cues** | `Delete` |
| **Undo Action** | `Ctrl + Z` |

---

## Automation via TDMCP (Agent Operations)

When `TDMCP.tox` is active on port `13316`:
1. **Inspect Errors:**
   `mcp_touchdesigner_get_errors(path='/', recurse=True)`
2. **Execute Verified Python:**
   `mcp_touchdesigner_execute_code(code="...")`
3. **Inspect Performance:**
   `mcp_touchdesigner_get_cook_performance(path='/Multi_Layer_Timeline')`
4. **Bottom-Up TOX & TOE Saving:**
   Always save modified subcomponents, then `Multi_Layer_Timeline.tox`, then named `.toe`.
