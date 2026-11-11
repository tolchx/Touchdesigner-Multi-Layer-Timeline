# TouchDesigner Multi-Layer Timeline (TD-MTL) — Agent Guidelines & Knowledge Base

This document serves as the persistent knowledge base and operational manual for AI agents working in this repository. All conventions, performance contracts, and architectural patterns documented here have been empirically verified in TouchDesigner 2025+ (Vulkan render pipeline).

---

## 1. Project Overview & Release Files

- **Current Reference File:** `v1.14.toe` (and `v1.13.toe`)
- **Release Component:** `Release/Multi_Layer_Timeline.tox` (and `Tox/Master/Multi_Layer_Timeline.tox`)
- **TDMCP Bridge:** `TDMCP.tox` running on port `13316` via native WebSocket/HTTP MCP.
- **Client Helper:** `scripts/td_client.py` for direct HTTP JSON-RPC execution (`python scripts/td_client.py "<code>"`) with 30s timeout.
- **Root Component Path:** `/Multi_Layer_Timeline`

---

## 2. Architecture & Core Systems

### 3D GPU Instanced Engine
- All cues, layer tracks, playhead, and grid lines are rendered in a **3D GPU instanced environment** (`Geometry COMP` + instancing tables/CHOPs).
- **Dual Camera Setup:**
  - `cam1` (`Timeline3D/Render/cam1`): Main timeline camera. Controls horizontal zoom/pan (`tx`, `sx`) and vertical scroll (`ty`).
  - `cam_LayerSettings` (`Timeline3D/Render/cam_LayerSettings`): Orthographic camera locked to track headers on the left sidebar.
- **Picking via `RenderPick`:** User interactions are resolved by querying `instance id` directly on GPU render buffers.

### Show Control & External Automation (Fase 4)
- **Bidirectional OSC (`Timeline3D/Input/OSC`):**
  - Serves OSC messages on port 7000, transmits real-time feedback (timecode, state, fraction, seconds) to port 7001 for Bitfocus Companion and StreamDeck.
  - Native `osc_handler.py` and `osc_feedback.py`.
- **Hardware MIDI Mapping (`Timeline3D/Input/MIDI`):**
  - Maps APC40, nanoKONTROL, and X-Touch hardware notes and CC faders to transport, layer opacities, master audio, and frame stepping.

### Marker Track & Show Logic (Fase 5)
- **Marker Engine (`Timeline3D/Markers`):**
  - Table-driven marker system (`table_Markers`) with action types: `Continue`, `Pause` (*Wait-for-Go*), `Loop`, and `Jump`.
  - Frame-accurate crossing monitor via `chopexec_monitor` calling `CheckMarkerCrossing`.
  - Keyboard shortcuts: `M` creates marker at playhead, `Shift + Left / Right` jumps between markers, `Enter` triggers `GO`.
  - Transport UI: `btn_GO` and `btn_Marker` in `container_Transport`.

### Professional Layer Headers (Fase 6)
- **Layer Parameters:** `Mute`, `Solo`, `Lock`, `Opacity`, `Blendmode` on `Template_layer1` and `base_Layer*`.
- **Playback Compositing Integration:** `playback_engine.py` evaluates layer `Mute`, `Solo`, and scales `Opacity`.
- **Interaction Lock:** `RenderPick.py` checks layer `Lock` and disables translation, stretching, and edge dragging for locked cues.

### Media Inspector & Codec Advisor (Fase 7)
- **Asset Manager (`Timeline3D/Assets`):**
  - Scans all cues for missing files (`os.path.exists`), reports missing count and warnings.
  - Inspects video codecs, warning against CPU-heavy H.264/HEVC and validating optimal GPU formats (HAP, NotchLC, Apple ProRes).
  - Batch relinking function: `RelinkFolder(new_path)`.

### Web Remote Control for Tablet / iPad (Fase 8)
- **HTML5 Web App (`Timeline3D/WebRemote`):**
  - Served on port 8080 by native `webserverDAT` (`webserver1`).
  - Self-contained offline dark-mode touch interface with big tactile GO/PAUSE/STOP buttons, digital timecode clock, marker jumper carousel, and layer faders.
  - Bidirectional communication via WebSockets (`/ws`) and REST JSON API (`/api/status`, `/api/action`).

### Interactive Editing & Ergonomics (Fase 1)
- **Razor Tool / Cuchilla (`C` & `btn_Split`):**
  - Shortcut `c` / `C` and UI button `/Multi_Layer_Timeline/container_Transport/btn_Split` execute `op.Manager.SplitCueAtPlayhead()`.
  - Splits cue cleanly at playhead or given time into Part A (`[st, splitTime]`) and Part B (`[splitTime, et]`).
  - Automatically preserves video playback continuity by recalculating `Trimstart = Trimstart + (splitTime - st) * Speed`.
- **Fast Duplication (`Ctrl + D` & `Alt + Drag`):**
  - Shortcut `Ctrl + D` executes `DuplicateSelectedCues()`, cloning selected cue(s) contiguously immediately after their end time on their respective layers.
  - Mouse `Alt + Drag` in `RenderPick.py` instantly clones the clicked cue and drags the clone to a new position.
- **Dynamic Cursor Feedback:**
  - `arrowLeftRight` (`↔`) on edge stretch ($\le 6$px or $\ge \text{width} - 6$px).
  - `arrowAll` (`✥`) on cue body translation / drag.
  - `pointer` automatically restored on drag release (`EventSelectEnd`).
- **Color Tagging:**
  - `Colorpreset` custom menu parameter on all cues (`DefaultBlue`, `EmeraldGreen`, `AmberGold`, `VioletMagenta`, `CrimsonRed`, `CyanElectric`, `DarkSlate`).
  - Monitored by `parexec_cue_colors` (`parameterexecuteDAT`) which immediately updates `Backgroundcolorr, g, b` driving `geo_Cues` GPU instance colors.

### Professional Output Engine & Render Quality (Fase 2)
- **Native Spout & NDI Video Outputs:**
  - `spout_out1`, `spout_out2` (`syphonspoutoutTOP`) and `ndi_out1`, `ndi_out2` (`ndioutTOP`) wired directly to `out1` and `out2` in `/Multi_Layer_Timeline`.
  - Governed by custom page `Outputs` on the root component with toggle parameters (`Enablespout1`, `Enablespout2`, `Enablendi1`, `Enablendi2`) and configurable stream names.
- **Hermite Smoothstep Crossfades:**
  - `playback_engine.py` supports 4 transition curve modes: `Linear`, `Smoothstep` ($3x^2 - 2x^3$), `EaseIn` ($x^2$), and `EaseOut` ($1 - (1-x)^2$).
  - Per-cue setting via `Fadecurve` menu parameter.
- **High-Performance 4K Video Buffering:**
  - Playback slots configured with `prereadframes = 24`, `highperfread = True`, and `alwaysloadinitial = True` to eliminate frame drops and stuttering on 4K multi-layer playback.

### Modulation & Automation Engine (Fase 3)
- **9-Channel `cue_time` Matrix:**
  - Generative scenes and video cues receive 9 synchronized real-time modulation channels:
    1. `active`: 1.0 when playhead intersects cue, 0.0 otherwise.
    2. `local_seconds`: Cue-relative elapsed time.
    3. `media_seconds`: Trim- and speed-adjusted media playback time.
    4. `fraction`: Normalized progress ($0.0 \to 1.0$).
    5. `length`: Total cue duration in seconds.
    6. `opacity`: Current evaluated opacity considering fade-in/out and crossfades.
    7. `curve`: Hermite-evaluated curve value.
    8. `audio_react`: Normalized real-time peak audio volume from `container_AudioTrack/filter_level`.
    9. `lfo`: Sinusoidal or cyclical LFO modulation based on `Autospeed`.
- **Cue Automation Modes:**
  - Custom parameters: `Automode` (`Off`, `RampUp`, `RampDown`, `Triangle`, `Pulse`, `SineLFO`, `AudioReact`), `Automin`, `Automax`, `Autospeed`.
  - Default scene creation in `SceneEditor` automatically builds the 9-channel constant CHOP.

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
