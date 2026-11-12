# TD-MTL (TouchDesigner 2025+ & TDMCP Fork)

> Fork of [franklin113/Touchdesigner-Multi-Layer-Timeline](https://github.com/franklin113/Touchdesigner-Multi-Layer-Timeline) updated for **TouchDesigner 2025+** (Vulkan GLSL compatibility, fixed timecode caching, timeline segment engine, clean zero-cue state) with **TDMCP / AgentSDK** automation support, **Dual Independent Video Outputs**, **Spout & NDI Streams**, **Hermite Smoothstep Crossfades**, **Show Control (OSC & MIDI)**, **Marker Track & Wait-for-Go Logic**, **Professional Layer Headers (Mute/Solo/Lock)**, **Asset Manager & Codec Advisor**, and **Web Remote Control for Tablet / iPad**.

---

## Production Suite Overview (`v1.16` — TouchDesigner 2025+ Verified)

```
                       ┌─────────────────────────────────────────────────────────┐
                       │           Multi_Layer_Timeline (Root Component)         │
                       └─────────────────────────────────────────────────────────┘
                                   │                              │
         ┌─────────────────────────┴──────────────┐   ┌───────────┴────────────────────────┐
         │         Timeline3D Rendering Engine    │   │         Show Control & Outputs     │
         ├────────────────────────────────────────┤   ├────────────────────────────────────┤
         │ • 3D GPU Instancing (geo_Cues, Layers) │   │ • Dual Video Outputs (out1, out2)  │
         │ • RenderPick Continuous Streaming      │   │ • Native Spout (spout1, spout2)    │
         │ • Dual-Edge Trimming (Left/Right)      │   │ • Native NDI (ndi1, ndi2)          │
         │ • Razor Tool (C / btn_Split)           │   │ • Bidirectional OSC (Port 7000/7001│
         │ • Fast Duplication (Ctrl+D, Alt+Drag)  │   │ • Hardware MIDI Mapping (CC/Notes) │
         │ • Color Tagging (7 Color Presets)      │   │ • Web Remote (HTML5 / Port 8080)   │
         │ • Marker Track (Wait-for-Go / Loops)   │   │ • Hermite Smoothstep Crossfades    │
         │ • Layer Headers (Mute / Solo / Lock)   │   │ • 4K High-Perf Buffering (24 frms) │
         │ • Dynamic VRAM Collapsing (ProSlate Engine)│   │ • Central Color Tokens (/ui/colors)│
         │ • Live GPU Telemetry HUD (FPS, VRAM %) │   │ • Bahnschrift Condensed Typography │
         └────────────────────────────────────────┘   └────────────────────────────────────┘
```

---

## Feature Matrix & Architectural Systems

### 1. Show Control & External Automation (OSC & MIDI)
- **Bidirectional OSC Engine (`Timeline3D/Input/OSC`):**
  - Ports: Default Input `7000`, Feedback Output `7001` (configurable on page `Show Control`).
  - **Commands:** `/timeline/play`, `/timeline/pause`, `/timeline/stop`, `/timeline/toggle_play`, `/timeline/goto [sec]`, `/timeline/goto_fraction [0..1]`, `/timeline/step [frames]`, `/timeline/split`, `/timeline/duplicate`, `/timeline/go`, `/timeline/marker/jump [name]`, `/timeline/layer/mute`, `/timeline/layer/solo`, `/timeline/layer/opacity`.
  - **Companion / StreamDeck Feedback:** Continuous high-DPI feedback (`/timeline/timecode`, `/timeline/state`, `/timeline/state_str`, `/timeline/seconds`, `/timeline/fraction`, `/timeline/duration`).
- **Hardware MIDI Mapping (`Timeline3D/Input/MIDI`):**
  - Mapped for APC40, nanoKONTROL, X-Touch, and standard MIDI keyboards:
    - Notes `94` (Play), `93` (Stop/Pause), `95` (Split Cue), `60` (GO Trigger), `91`/`92` (Frame Step).
    - CC `1`–`8` (Layer 0–7 Opacity Faders), CC `9` (Master Audio Gain), CC `60` (Jog Wheel Scrubbing), CC `114`/`115` (Stop/Play).

### 2. Marker Track & Show Logic (Wait-for-Go & Loops)
- **Marker Data Engine (`Timeline3D/Markers`):**
  - Table-driven marker system storing `id`, `time`, `name`, `color`, `action`, `target`.
  - **Action Modes:**
    - `Continue`: Normal continuous show playback.
    - `Pause` (*Wait-for-Go*): Playhead halts frame-accurately at the marker and waits for operator input (`GO` button, Enter key, or `/timeline/go` OSC command).
    - `Loop`: Cycles playback between current marker and target/previous marker until released.
    - `Jump`: Instantaneous seek to target marker.
  - **Navigation & Shortcuts:** Key `M` / `m` creates a marker at the playhead; `Shift + Left` / `Shift + Right` jump directly between markers; `Enter` triggers `GO`.
  - **Transport UI:** Dedicated `GO` (large green button) and `+M` buttons in `container_Transport`.

### 3. Professional Layer Headers (Mute, Solo, Lock & Opacity)
- **Per-Layer Controls (`Timeline3D/Layers`):**
  - `Mute` (Toggle): Silences both video and audio of the track without moving cues.
  - `Solo` (Toggle): Isolates the selected track(s), fading all non-solo layers to 0.0 opacity.
  - `Lock` (Toggle): Locks the entire track against accidental mouse movement, stretching, or razor cutting in `RenderPick.py`.
  - `Opacity` (Float 0.0–1.0): Master track opacity fader multiplying underlying cue opacities.
  - `Blendmode` (Menu: *Over, Add, Multiply, Screen, Lighten, Difference*).

### 4. Media Inspector, Missing Media Relinker & Codec Advisor
- **Asset Manager (`Timeline3D/Assets`):**
  - Scans all multimedia cues (`Imagefile`, `Audiofile`, `Scenecomp`, `Moviespec`).
  - Table `table_Assets` flags file existence, missing paths, and codecs.
  - **GPU Codec Advisor:** Inspects video codecs; flags CPU-bound formats (H.264, HEVC) with performance warnings and validates optimal GPU formats (HAP, HAP Q, NotchLC, Apple ProRes).
  - **Batch Relinker:** `RelinkFolder(new_path)` automatically searches and reconnects missing media across directories.
  - Root parameters on page `Assets`: `Scanassets` (Pulse), `Totalassets`, `Missingassets`, `Codecwarnings`.

### 5. Web Remote Control for Tablet / iPad (HTML5 & WebSockets)
- **Embedded Web Server (`Timeline3D/WebRemote`):**
  - Native `webserverDAT` listening on port `8080` (configurable on page `Show Control`).
  - Self-contained, responsive dark-mode touch interface (no Internet connection or CDN required).
  - **Features:**
    - Giant tactile **GO**, **PAUSE**, and **STOP** buttons.
    - Monospace digital timecode clock with live progress scrubber bar.
    - Marker chip carousel for instant one-tap section jumping.
    - Layer master opacity sliders and Mute buttons.
    - Low-latency real-time bidirectional updates via WebSockets and REST JSON API (`/api/status`, `/api/action`).

### 6. Interactive Editing & Ergonomics (Fase 1)
- **Razor Tool / Cuchilla (`C` & `btn_Split`):** Splits cue cleanly at playhead into Part A and Part B, automatically preserving video playback continuity by recalculating `Trimstart = Trimstart + (splitTime - st) * Speed`.
- **Fast Duplication (`Ctrl + D` & `Alt + Drag`):** Contiguous duplication along track (`Ctrl+D`) or instant clone-and-drag with mouse (`Alt+Drag`).
- **Dynamic Cursor Feedback:** `arrowLeftRight` (`↔`) on edge stretch, `arrowAll` (`✥`) on translation, `pointer` on release.
- **Color Tagging:** 7 presets (*DefaultBlue, EmeraldGreen, AmberGold, VioletMagenta, CrimsonRed, CyanElectric, DarkSlate*) driving GPU instanced cue colors via `parexec_cue_colors`.

### 7. Video Outputs & Render Quality (Fase 2)
- **Dual Outputs + Spout & NDI:** Independent `out1`, `out2`, `spout_out1`, `spout_out2`, `ndi_out1`, `ndi_out2` TOPs driven by root parameter page `Outputs`.
- **Hermite Smoothstep Crossfades:** 4 transition curve modes: `Linear`, `Smoothstep` ($3x^2 - 2x^3$), `EaseIn` ($x^2$), and `EaseOut` ($1 - (1-x)^2$).
- **High-Performance 4K Buffering:** 5-slot video engine with `prereadframes = 24`, `highperfread = True`, and `alwaysloadinitial = True`.

### 8. Modulation & Automation Engine (Fase 3)
- **9-Channel `cue_time` Matrix:** Active cues and generative scenes receive:
  `active`, `local_seconds`, `media_seconds`, `fraction`, `length`, `opacity`, `curve`, `audio_react`, `lfo`.
- **Automation Modes:** `Automode` (*Off, RampUp, RampDown, Triangle, Pulse, SineLFO, AudioReact*), `Automin`, `Automax`, `Autospeed`.

### 9. Modern High-Density UI & Performance Architecture (ProSlate Standard)
- **Centralized Design Tokens (`/ui/colors`):** 24 semantic color tokens (`panel_bg`, `panel_base`, `panel_header`, `outline_static`, `button_on`, etc.) driving all timeline panels and dialogs, enabling instant cohesive theme adjustments.
- **Unified Pro Typography (`Bahnschrift Condensed`):** All 62+ text nodes standardized on Windows-native high-density condensed typography for zero label clipping and crisp sub-pixel legibility.
- **Dynamic Universal Parameter Inspector (`parameter1`):** Focus tracking engine that dynamically displays clicked cue parameters with custom-only minimalist rows (`custom = True`, `builtin = False`, `separators = False`).
- **Dynamic VRAM Collapsing Engine (`playback_engine.py`):** Automatic memory purger shrinking inactive `renderTOP`s to 1x1px, `inTOP`s to 1/8th resolution, and bypassing idle geometry to save gigabytes of VRAM during large multi-scene shows. Governed by root parameter page `Performance` (`Enable VRAM Collapse`).
- **Live GPU Telemetry HUD (`container_GPUStats`):** Monospace real-time monitor docked on the transport bar displaying `cookrate`, frame time (`ms`), and percentage of GPU VRAM used with an automatic alert color switch when VRAM exceeds 85%.

### 10. v2.0 UI Modernization & Pro Precision Workstation
- **Top Application Ribbon (`ui_taskbar`):** Dedicated top bar with brand badge, dynamic engine state LED (Green = Playing, Amber = Paused, Slate = Stopped), real-time session readout (`v2.toe • 60 FPS • Duration`), fullscreen toggle, project save button, and 3 layout presets (`STANDARD`, `TIMELINE FOCUS`, `PREVIEW FOCUS`).
- **Universal Inspector Header (`container_InspectorHeader`):** Quick-action bar docked directly above `parameter1` featuring active target breadcrumb, 7 instant 1-click cue color swatches (`DefaultBlue`, `EmeraldGreen`, `AmberGold`, `VioletMagenta`, `CrimsonRed`, `CyanElectric`, `DarkSlate`), and quick editing tools (`DUP`, `CUT`, `DEL`).
- **Tactile Transport Surface & Loop Engine (`btn_Loop`):** Transport ribbon standardized with uniform 1px micro-borders (`outline_static`), hover illumination, and dedicated `LOOP` toggle button for seamless timeline cycling.
- **Output Preview Monitor Modernization (`container_Preview`):** Pinned header with segmented output mode selectors (`OUT 1`, `OUT 2`, `SPLIT`) and live stream/cue overlay text.
- **Unified 1px Geometric Micro-Borders:** Applied systematically across `container_Timecode`, `container_Duration`, `container_AudioHeader`, `container_AudioTrack`, `LayerSettings`, `Timeline3D`, and `container_RangeSlider` creating a cohesive pro DAW visual language.

---

## Keyboard Shortcuts Reference

| Action | Shortcut |
| :--- | :--- |
| **Play / Pause Toggle** | `Space` |
| **GO / Resume from Marker** | `Enter` / `Return` |
| **Add Marker at Playhead** | `M` / `m` |
| **Jump to Previous / Next Marker** | `Shift + Left Arrow` / `Shift + Right Arrow` |
| **Step -1 Frame / +1 Frame** | `Left Arrow` / `Right Arrow` |
| **Razor Tool (Split Cue at Playhead)** | `C` / `c` |
| **Duplicate Selected Cues** | `Ctrl + D` |
| **Clone & Drag Cue** | Hold `Alt` while dragging a cue |
| **Copy / Paste Selected Cues** | `Ctrl + C` / `Ctrl + V` |
| **Delete Selected Cues** | `Delete` / `Backspace` |
| **Home View (Full Timeline 0–100%)** | `H` / `h` |
| **Center View on Playhead** | `G` / `g` |
| **Zoom In / Out** | `Ctrl + =` / `Ctrl + -` (or `Alt + Mouse Wheel`) |

---

## OSC Address Map (Bitfocus Companion & StreamDeck)

| Address | Arguments | Description |
| :--- | :--- | :--- |
| `/timeline/play` | none | Starts playback |
| `/timeline/pause` | none | Pauses playback |
| `/timeline/stop` | none | Stops and resets to 0.0s |
| `/timeline/toggle_play` | none | Toggles play/pause state |
| `/timeline/go` | none | Triggers GO (resumes from Wait-for-Go markers) |
| `/timeline/goto` | `[seconds: float]` | Seeks timeline to specified seconds |
| `/timeline/goto_fraction` | `[fraction: float]` | Seeks timeline to normalized fraction (`0.0`–`1.0`) |
| `/timeline/step` | `[frames: int]` | Steps timeline by `±N` frames |
| `/timeline/home` | none | Resets visible range slider to 0.0–1.0 |
| `/timeline/marker/jump` | `[name_or_id: str]` | Jumps playhead directly to marker |
| `/timeline/marker/next` | none | Jumps to next marker |
| `/timeline/marker/prev` | none | Jumps to previous marker |
| `/timeline/marker/add` | `[name: str]` | Creates a marker at playhead |
| `/timeline/split` | none | Splits cue at playhead |
| `/timeline/duplicate` | none | Duplicates selected cues |
| `/timeline/layer/mute` | `[layer: int, state: 0/1]` | Sets layer Mute state |
| `/timeline/layer/solo` | `[layer: int, state: 0/1]` | Sets layer Solo state |
| `/timeline/layer/opacity` | `[layer: int, value: float]` | Sets layer opacity (`0.0`–`1.0`) |

---

## Installation & Release Files

1. Open reference project `v1.16.toe` (or `v1.14.toe`) in TouchDesigner 2025+ (Build `2025.32460` or later).
2. Master release component: `Release/Multi_Layer_Timeline.tox` (also mirrored at `Tox/Master/Multi_Layer_Timeline.tox`).
3. Connect external control:
   - **Web Remote:** Open `http://<machine-ip>:8080/` in any browser or iPad on the same network.
   - **OSC:** Send UDP OSC commands to port `7000`; listen for feedback on port `7001`.
   - **MIDI:** Connect any MIDI device and toggle `Enable MIDI` on the `Show Control` page.
