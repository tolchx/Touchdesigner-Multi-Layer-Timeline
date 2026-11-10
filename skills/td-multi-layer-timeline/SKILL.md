---
name: td-multi-layer-timeline
description: Specialized guide for using, integrating, customizing, and automating the TouchDesigner Multi-Layer Timeline (TD-MTL) system. Covers 3D GPU instanced timeline architecture, cue lifecycles, Timer CHOP / Segment DAT engine, playback synchronization with TOPs/DMX/OSC, callbacks, and TDMCP remote control.
---

# TouchDesigner Multi-Layer Timeline (TD-MTL) Skill

## Overview
**TD-MTL** is a GPU-accelerated, multi-layer sequencing timeline for TouchDesigner created by Tim Franklin and Brian Alexander. Rather than using conventional heavy 2D UI components, it renders the entire timeline canvas, tracks, and cues in a **3D GPU instanced environment**, delivering high performance (60 fps), precise scrubbing, and multi-track orchestration.

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

---

## Component Layout & File Map

```
Touchdesigner-Multi-Layer-Timeline/
├── Release/
│   └── Multi_Layer_Timeline.tox     # Self-contained master component (drag & drop into TD)
├── TD_Multi-Layer-Timeline.V7.toe   # Reference master project
├── Tox/
│   ├── Master/                      # Master timeline container and subcomponents
│   ├── Timeline3D/
│   │   ├── Project/                 # Project state, CueSpec, Manager.py, ParWriter, Saver
│   │   ├── Render/                  # GLSL shaders, SOP instancing, dual-camera render setup
│   │   ├── Render Pick/             # Mouse interaction: Bounds, Transformer, Snapper, Selection
│   │   ├── Time/                    # Segment DAT builder & Timer CHOP transport
│   │   ├── Layers/                  # Track definitions & layer properties
│   │   └── Playback/                # Playback state sync
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

### Adding & Modifying Cues via Python
Inside TouchDesigner (or via TDMCP `run_python`):
```python
# Access the Manager extension
manager = op('Multi_Layer_Timeline').op('Project').ext.Manager

# Create a cue using a CueSpec
spec = op('Multi_Layer_Timeline').op('Project').mod.CueSpec.CueSpec(
    Title='IntroClip',
    Cuetype='Media',
    Starttime=0.0,
    Cuelength=10.0,
    Fadeinoutduration=(1.0, 1.0),
    Layer=0,
    Backgroundcolor=(0.2, 0.6, 0.9, 1.0)
)

manager.AddCue(cueType='Media', name='cue_intro', cueSpec=spec)
```

---

## Connecting Playback to TouchDesigner Networks

### 1. Video / Media Compositing
1. Route the `Segment DAT` or `Time` component CHOP outputs into your media player block.
2. Use the `preload` pulse to cue a `Movie File In TOP` before playback arrives at the cut point.
3. Drive the `opacity` or `cross TOP` blend parameter using the fade ramp channel (`0.0 -> 1.0`).

### 2. External Commands (OSC, DMX, MIDI, Python)
Implement callback logic inside `Main_Callbacks_Template.py`:
```python
def OnPlayStateChange(value):
    # 0: Stop, 1: Play, 2: Pause
    if value == 1:
        op('d鐘_out').sendOSC('/transport/play', [1])
    elif value == 0:
        op('d鐘_out').sendOSC('/transport/stop', [1])

def OnCueTrigger(cueInfo):
    # Fired when playhead crosses a cue start
    cueType = cueInfo.get('type')
    if cueType == 'OSC':
        op('oscout1').sendOSC(cueInfo['address'], cueInfo['args'])
```

---

## Keyboard Shortcuts & Navigation

| Action | Shortcut |
| :--- | :--- |
| **Zoom In / Out** | `Alt + Mouse Wheel` or `Ctrl + + / -` |
| **Pan Canvas** | `Shift + Mouse Wheel` (horizontal) / `Mouse Wheel` (vertical) |
| **Multi-Select** | Hold `Shift` while clicking cues |
| **Snap to Playhead** | Hold `Ctrl + Alt` while dragging a cue |
| **Snap to Increments** | Hold `Ctrl` while dragging a cue |
| **Copy Selected Cues** | `Ctrl + C` (pastes starting at current playhead) |
| **Delete Selected Cues** | `Delete` |
| **Undo Action** | `Ctrl + Z` |

---

## Automation via TDMCP (Agent Operations)

When `TDMCP.tox` is active on port `13316`:
1. **Inspect Timeline State:**
   - Query operators: `mcp_touchdesigner_get_operator(path='/project1/Multi_Layer_Timeline')`
   - Read cue table: `mcp_touchdesigner_get_dat_content(path='/project1/Multi_Layer_Timeline/Project/table_cues')`
2. **Control Transport Remotely:**
   - Pulse play/pause: `mcp_touchdesigner_pulse_parameter(path='/project1/Multi_Layer_Timeline/Transport', parameter='Play')`
3. **Automate Cue Generation:**
   - Run Python snippets via `mcp_touchdesigner_run_python` to script bulk cue placements from external timelines (EDL, CSV, JSON).
