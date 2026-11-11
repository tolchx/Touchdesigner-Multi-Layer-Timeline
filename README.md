# TD-MTL (TouchDesigner 2025+ & TDMCP Fork)

> Fork of [franklin113/Touchdesigner-Multi-Layer-Timeline](https://github.com/franklin113/Touchdesigner-Multi-Layer-Timeline) updated for **TouchDesigner 2025+** (Vulkan GLSL compatibility, fixed timecode caching, timeline segment engine, clean zero-cue state) with **TDMCP / AgentSDK** automation support, **Dual Independent Video Outputs**, **Audio Track with Waveform Visualizer & Auto-Fit**, and **Enhanced 60 FPS GPU Interactive Cue Dragging & Edge Trimming**.

---

## What's New in `v1.10` (TouchDesigner 2025+ Verified)

### 1. Dual Independent Video Outputs (Multi-Screen Projection)
- **Per-Cue & Per-Layer Output Routing:** Route individual cues or entire layers to `out1` (Output 1), `out2` (Output 2), or `both` (simultaneous multi-screen projection).
- **Independent Aspect Ratios & Fit Modes:**
  - Presets: `16:9`, `16:10`, `4:3`, `21:9`, `9:16`, `1:1`, and `Custom` (with user-defined pixel resolution `Customw` x `Customh`).
  - Fit modes: `fit` (Fit Best / Letterbox), `fill` (Fit Outside / Crop), `fitoutside`, and `native` (Native resolution).
- **GUI Preview Switcher:** One-click preview toggle buttons (`[OUT 1]`, `[OUT 2]`, `[SPLIT]`) with live status in the timeline header.
- **Physical Display Outputs:** Master-level `out1` and `out2` TOPs ready for Window COMP routing to separate physical projectors or LED screens.

### 2. Audio Track, Live Waveform & Timeline Auto-Fit
- **Dedicated Audio Header & Track:** Audio track strip with volume fader, live stereo VU meters, Mute, Solo, and Pan controls.
- **GLSL Visualizer Modes:** Switch between `Waveform`, `Spectrogram`, and `Lissajous` visualizations.
- **Duration Auto-Fit:** Automatically scales the entire timeline duration (`Timelinelength`) to perfectly match the loaded audio file without clipping.

### 3. Smooth 60 FPS GPU Interactive Dragging & Dual-Edge Trimming
- **RenderPick Continuous Streaming:** Switched `renderpick1.par.strategy` to `select` (*While Select*), ensuring fluid 60 FPS coordinate streaming during mouse interaction.
- **Dual-Edge Trimming:**
  - **Right-Edge Stretch:** Drag the right handle to adjust cue duration (`Cuelength`) while keeping the start time fixed.
  - **Left-Edge Stretch:** Drag the left handle to adjust start time (`Starttime`) and duration while keeping the end time fixed.
- **World-Space Scale-Independent Calculations:** Edge detection evaluates directly in seconds, immune to camera zoom, window scaling, or DPI mismatches.
- **Vertical Layer Transitions:** Procedural layer calculation using `Computedlowerbounds` and `Computedlayerheight` relative to the initial touch layer, providing responsive, jitter-free layer switching with boundary protection.
- **Magnetic Snapping:** Snaps cue boundaries to the playhead, subrange markers, and neighboring cues with real-time `geo_SnapLine` visual feedback.
- **Self-Healing Selection:** Upgraded `Selection.py` (`DoSelection`) to guarantee clean single-cue white selection outlines and eliminate duplicate selection artifacts.

### 4. TimeBase Parity Features
- **Subrange Playback:** Define In/Out boundaries (`Subrangein`, `Subrangeout`, `Enablesubrange`) for looped rehearsal or section editing.
- **Frame-Accurate Stepping:** Dedicated `±1F` buttons and `Left`/`Right` arrow shortcuts for single-frame precision.
- **Navigation Shortcuts:** `Home` (go to start / 0s) and `Goto` timecode jump.
- **Per-Cue Looping:** Individual cue loop toggle (`Loopcue`).
- **Movie Trim & Playback Speed:** In-cue video trimming (`Trimstart`, `Trimend`) and variable playback `Speed` multiplier.
- **Extended Cue Types:** Support for Media, Tox, TCP/IP, OSC, Text, Event, and Audio cues.
- **JSON Show Serializer:** Portable show export and import (`Shows/show_default.json`) for backing up and transferring multi-track shows.

### 5. Inline Renaming
- **Track Renaming:** Double-click any layer track header in `LayerSettings` to edit track names inline.
- **Cue Renaming:** Double-click any cue in `Timeline3D` to rename cues directly on the timeline canvas.

---

## TouchDesigner 2025+ Compatibility Fixes (`v0.8`, Build `2025.32460`)

Opening the original `.toe`/`.tox` components in modern TouchDesigner 2025+ builds introduced Vulkan GLSL and timing regressions. The following foundational fixes were applied:

- **Vulkan Instanced Texturing (`Cues` & `Layers` GLSL MATs):**
  - Updated `Timeline3D/Cues/phong1GLSL_CueMat` (`Vertex` & `Pixel`) and `Timeline3D/Layers/phong1GLSL_CueMat` (`Vertex` & `Pixel`) from legacy OpenGL bindless handles (`uint64_t` / `TDInstanceTexture2D()`) to Vulkan `flat uint instanceTextureIndex`, `TDInstanceTextureIndex()`, and `TDInstanceTexture(iVert.instanceTextureIndex, ...)`.
  - Restores track headers (`Layer 0`–`Layer 4`) in `LayerSettings` and cue rendering (thumbnails, titles, selection outlines) in `Timeline3D`.
- **Zero-Cue Rendering & Warnings (`Cues`):**
  - Driven `render`, `display`, and `instancing` on `Timeline3D/Cues/geo_Cues` and `geo_Keyframe_Lines` with `op('null_InstanceInfo').numChans > 0` so no uninstanced placeholder box or missing-attribute warnings appear when there are 0 cues.
- **Timecode & Scrub Bar Labels (`container_Timecode` & `geo_TimeIcons`):**
  - Rewrote `container_Timecode/CACHE/execute1` (`_populate_cache()` on `onStart` / `onCreate`) to synchronously populate all 60 `tex3d1` slices (`00`–`59` at `256x256`) using `prefill` + `replacesingle` / `replacesinglepulse`.
  - Removed the legacy OpenGL `gl_PointCoord.y` inversion in `Timeline3D/Canvas/geo_TimeIcons/phong4GLSLPixel` and updated `geo_TimeIcons.par.ty` so scrub bar timecode markers render upright and inside the camera frustum.
- **Timing Engine & Playback (`Time` & `RenderPick`):**
  - Aligned `Timeline3D/Time/insert1` `contents` with `select_Library` columns (`begin = 0.0`, `length = Timelinelength` for master segment `0`), preventing `timer1` from jumping immediately to `done0 = 1.0` when cues exist.
  - Fixed `ext.Player.StartPlaying` → `ext.Player.Play` in `Timeline3D/Time/timerCallbacks`.
  - Added null guards in `RenderPick.py`.

---

## AI Automation & TDMCP Bridge

- [`TDMCP.tox`](TDMCP.tox) & [`.mcp.json`](.mcp.json) — Embedded TDMCP server bridge (`http://127.0.0.1:13316/mcp`) for inspecting and editing the live TouchDesigner network via MCP.
- [`AgentSDK/`](AgentSDK/) — Python helpers (`TimelineSceneEngine`, `jpshaders_nodes`, `jpshaders_catalog.json`) for scripting scenes, fades, and JPShaders GLSL nodes synchronized with the timeline.
- [`skills/`](skills/) — Agent skills (`td-multi-layer-timeline`, `td-glsl-jpshaders-expert`, `td-pops-tops-scene-builder`, `td-timeline-scene-orchestrator`).
- [`docs/TUTORIAL_TRANSCRIPTION.md`](docs/TUTORIAL_TRANSCRIPTION.md) — Technical breakdown and architecture transcription of the TD-MTL tutorial.

---

## Installation & Usage

1. Open `Release/Multi_Layer_Timeline.tox` or load `v1.10.toe` in TouchDesigner 2025+.
2. Drop media into layers or click **Add Cue** in the settings page.
3. Use the **Transport Bar** to play, pause, stop, step frames (`±1F`), and scrub.
4. Route layers/cues to `Output 1` and `Output 2` for multi-display projection.

### Keyboard Shortcuts

| Action | Shortcut |
| :--- | :--- |
| **Zoom In / Out** | `Alt + Mouse Wheel` |
| **Pan Canvas** | `Shift + Mouse Wheel` (horizontal) / `Mouse Wheel` (vertical) |
| **Step -1 Frame / +1 Frame** | `Left Arrow` / `Right Arrow` |
| **Go to Start (0s)** | `Home` |
| **Multi-Select** | Hold `Shift` while clicking cues |
| **Snap to Playhead** | Hold `Ctrl + Alt` while dragging a cue |
| **Snap to Increments** | Hold `Ctrl` while dragging a cue |
| **Copy Selected Cues** | `Ctrl + C` (pastes starting at current playhead) |
| **Delete Selected Cues** | `Delete` |
| **Undo Action** | `Ctrl + Z` |

---

## Credits

- **Tim Franklin** — Original Architecture & Concept
- **Brian Alexander** — Timing & Transport Engine
- **Lucas Morgan** — Box Select & Matrix Transforms
- **Tolch.x** — TouchDesigner 2025+ Vulkan Modernization, Dual Output Engine, Audio Track & Waveform Visualizer, TDMCP Integration, and Interactive Dragging/Trimming Engine

## License

MIT / Derivative TouchDesigner Community Asset
