# TouchDesigner Multi-Layer Timeline (TD-MTL) — Agent Guidelines & Knowledge Base

This document serves as the persistent knowledge base and operational manual for AI agents working in this repository. All conventions, performance contracts, and architectural patterns documented here have been empirically verified in TouchDesigner 2025+ (Vulkan render pipeline).

---

## 1. Project Overview & Release Files

- **Current Reference File:** `v1.11.toe`
- **Release Component:** `Release/Multi_Layer_Timeline.tox` (and `Tox/Master/Multi_Layer_Timeline.tox`)
- **TDMCP Bridge:** `TDMCP.tox` running on port `13316` via native WebSocket/HTTP MCP.
- **Root Component Path:** `/Multi_Layer_Timeline`

---

## 2. Architecture & Core Systems

### 3D GPU Instanced Engine
- All cues, layer tracks, playhead, and grid lines are rendered in a **3D GPU instanced environment** (`Geometry COMP` + instancing tables/CHOPs).
- **Dual Camera Setup:**
  - `cam1` (`Timeline3D/Render/cam1`): Main timeline camera. Controls horizontal zoom/pan (`tx`, `sx`) and vertical scroll (`ty`).
  - `cam_LayerSettings` (`Timeline3D/Render/cam_LayerSettings`): Orthographic camera locked to track headers on the left sidebar.
- **Picking via `RenderPick`:** User interactions are resolved by querying `instance id` directly on GPU render buffers.

### Dual Output Video Routing & Aspect Ratio
- Every cue / scene can be routed to **Output 1**, **Output 2**, or both simultaneously.
- Supported Aspect Ratio modes: `Fit`, `Fill`, `Fill Outside`, and `Custom Resolution`.
- Preview Monitor (`container_Preview`): Integrated split-screen and full-screen preview switcher (`layout_split`, `switch_preview`).

### Dedicated Audio Track Engine (`container_AudioTrack`)
- **Real-Time GLSL Waveform & Spectrogram:** `glsl_view` renders high-DPI waveform and spectrogram bound directly to `cam1` viewport bounds (`uTimelineView.xy`).
- **Metering & Mixing:** `meter_comp` provides hardware-accelerated stereo peak meters. Gain (`math_gain`) and Pan (`math_pan`) controls.
- **Auto-Fit:** Timeline duration automatically matches loaded audio file length via `op.Timeline.par.Duration`.

### Interactive Cue Trimming & Dragging (`Transformer.py`)
- **Left Edge Drag ($\le 6$px):** Trims cue start time without moving end point (`CanStretchLeft`).
- **Right Edge Drag ($\ge \text{width} - 6$px):** Trims cue duration (`CanStretch`).
- **Body Drag:** Translates cue across time and layers.
- **Click Precedence:** Edge trimming takes strict priority over scene open buttons to prevent accidental window popups.

---

## 3. Verified Performance Contracts (60 FPS Guaranteed)

### Contract 1: Vulkan Dynamic Texture Reallocation Trap (CRITICAL)
- **Rule:** NEVER set `outputresolution = parpanel` on TOPs inside interactively resizable COMPs (sliders, range bars, dividers).
- **Reason:** In Vulkan, modifying panel width/height pixel-by-pixel destroys and re-allocates textures every single frame, causing GPU pipeline stalls and dropping FPS from 60 to 15-20.
- **Solution (Fixed-Resolution Shader Pattern):**
  - Use a fixed custom resolution (e.g. `512x32` or `1024x32`) with `outputresolution = custom`.
  - Set `topfill = horizontal` or `stretch` on the parent Container COMP.
  - Pass the panel pixel width as a uniform float `uParams.x = parent().width`.
  - Compute normalized pixel coordinates in GLSL: `float px = vUV.st.x * uParams.x;`.
  - Texture is allocated once in VRAM and never reallocated during drag.

### Contract 2: Avoid Synchronous CPU Panel Layout Stalls
- **Rule:** NEVER read `.width` or `.height` on a Container COMP inside per-frame scripts (`whileOn`, drag callbacks) right after modifying parameters or anchors.
- **Reason:** Querying layout dimensions mid-frame forces TouchDesigner to synchronously solve the CPU layout tree, stalling the render thread.
- **Solution:** Calculate widths procedurally from normalized coordinates (`parent(2).width * (rAnchor - lAnchor)`), or read it once on `onOffToOn`.

### Contract 3: Motion Guard on Per-Frame Callbacks
- **Rule:** Always check if the cursor has actually moved before modifying parameters or running calculations in `whileOn`:
  ```python
  currentU = self.ownerComp.panel.insideu.val
  if self._lastU is not None and abs(currentU - self._lastU) < 1e-6:
      return
  self._lastU = currentU
  ```
  Reset `_lastU = None` in `onOffToOn` and `onOnToOff`.

### Contract 4: Smooth Range Clamping
- When panning the visible time window in `RangeBar.py`, clamp to `0.0` and `1.0` smoothly so the slider glides cleanly against boundaries without sticking or freezing.

---

## 4. Verification & Testing Standards

1. **Zero Errors Mandate:**
   Run `get_errors(path='/', recurse=True)` via TDMCP. There must be **0 errors** across the entire project before committing or releasing.
2. **Cook Performance Monitoring:**
   Verify interactive drag loops stay below **2 ms/frame** (target is 16.6 ms for 60 FPS).
3. **Bottom-Up Saving Protocol:**
   1. Save subcomponent `.tox` files (`Tox/...`).
   2. Save master component `Release/Multi_Layer_Timeline.tox` and `Tox/Master/Multi_Layer_Timeline.tox`.
   3. Save project `.toe` file (`v1.11.toe`).
4. **Git Hygiene:**
   Always inspect `git diff`, commit with clear technical summaries, and push to `origin/master`.
