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
    - **Zoom invariant:** `sx = op('null_CamScale')['Scale']` (the visible-fraction range published by `base_GetCamScale`; `Scale == 1` shows the whole timeline). Do not replace it with a constant — the layout is already normalised by `Scale`, so a constant `sx` makes the wheel scroll compress the timeline instead of zooming it. `tx = op('null_FinalCamTX')['CamTX']` and `ty = op('null_CamYPos')['Camypos']` are filtered CHOP chains: after changing the range programmatically, wait ~2 s (real time) before capturing, or `tx` is still stale and the frame is off-centre.
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

### ProSlate Theme System (`UI/colors` + `scripts/apply_ui_theme.py` + `scripts/apply_row_stripes.py`)

**Single source of truth:** `Multi_Layer_Timeline/UI/colors` → `table_colors` (columns `name, r, g, b, a, hex`), published through its `out` DAT. Never hardcode a UI colour that already has a token: bind an expression to
`op('/Multi_Layer_Timeline/UI/colors/out')['<token>', 'r'].val` (also `'g'`, `'b'`, `'a'`).
Do **not** use or edit `/ui/colors` at the project root — that is TouchDesigner's own internal palette, unrelated to this system.

**Tokens added by the ProSlate restyle** (15 of the 39 tokens; `table_colors` has 40 rows including its header. The other 24 predate the restyle and keep their names/values):

| token | hex | used by |
|---|---|---|
| `canvas_bg` | `#08090a` | timeline background plane (flat constant material) |
| `grid_line` | `#202226` | grid / row separator lines (`Canvas/constant2`) |
| `playhead` | `#73dbeb` | playhead bar (`Canvas/constant1`) |
| `snap_accent` | `#47758a` | snapping line (`Canvas/line1`, was red) |
| `cue_default` | `#1d3340` | default cue card fill / preset `DefaultBlue` |
| `cue_outline` | `#2b333b` | idle cue outline reference (shader uses `0.190,0.222,0.255`, see below) |
| `cue_outline_sel` | `#bfe6f0` | selected cue outline reference (shader `0.749,0.902,0.941`) |
| `cue_outline_multi` | `#e0bf4a` | outline of the 2nd and later cues of a multi-selection (shader index 2) |
| `ruler_text` | `#858f99` | ruler label tint |
| `row_alt` | `#0e0f12` | alternate-row striping |
| `layer_accent_1..5` | `#547885` `#b89438` `#735c94` `#47856b` `#a85c57` | per-layer accent rail (cycled by card index `% 5`) |

**Materials / nodes that implement the look**

- `Timeline3D/Canvas/mat_canvas_bg` — `constantMAT`, flat `canvas_bg` fill for the timeline backdrop (pass 1). Kept in the comp as the plain fallback material.
- `Timeline3D/Canvas/glsl_mat_canvas` (+ `glsl_canvas_vertex`, `glsl_canvas_pixel`) — alternate-row striping. Since pass 2 it is the material on `geo_Timeline_Bg`. Bands are computed in **world space** from `iVert.worldSpacePos.y` (no UVs, no extra geometry), with `uRows ← ipar.UserSettings.Layercount`, `uLower ← ipar.SystemSettings.Computedlowerbounds`, `uRowH ← ipar.SystemSettings.Computedlayerheight`, `uBase ← canvas_bg`, `uAlt ← row_alt`. Layer count/height changes are picked up automatically — do not duplicate the striping with geometry.
- `Timeline3D/Layers/Template_layer1` and `base_Layer0..4` — per-layer accent rail: `glsl_accent` (glslTOP, fixed 256×256, `uColor ← layer_accent_N` derived from the card name, `uWidth = 0.040`) → `over_accent` (overTOP) between `over1` and `null_bg`. The rail writes **premultiplied** colour (`rgb * alpha`) because `overTOP` expects premultiplied input; without it the whole card tints.

**Scripts** (run inside TouchDesigner through TDMCP, both idempotent — re-running re-applies values and never stacks ops):

1. `python scripts/td_client.py scripts/apply_ui_theme.py` — pass 1: tokens, canvas/grid/playhead/snap, cue shader patch, ruler tint, 3D typography, cue palette map + migration of already-coloured cues, 2D buttons, duration card, audio header, duration popup, inspector swatches.
2. `python scripts/td_client.py scripts/apply_row_stripes.py` — pass 2: `row_alt` + `layer_accent_*`, striping material, accent rails.

Order matters (pass 2 replaces the background material installed by pass 1). Only `apply_row_stripes.py` can write images, and only when its `CAPTURE` flag is set to `True`: it then saves `rows_after_timeline.png` / `rows_after_layers.png` into `<project folder>/tmp/` (path resolved from TouchDesigner, not a hardcoded absolute path). By default it writes no files. Neither script saves anything: after re-styling, save bottom-up (`scripts/save_bottom_up.py`) or the look is lost when TouchDesigner closes. The restyle lives in `Tox/Timeline3D/Canvas/Canvas.tox`, `.../Layers/Layers.tox`, `.../Cues/Cues.tox`, `.../Render/Render.tox` and `Tox/UI/UI.tox`.

**Deliberately hardcoded** (there is no token access from inside GLSL, or the value is coupled to geometry):

- `Timeline3D/Cues/phong1GLSL_CueMatPixel`: outline width `.022`, selection colours `vec3(0.190,0.222,0.255)` (index 0, idle) / `(0.749,0.902,0.941)` (index 1, primary selection) / `(0.878,0.749,0.290)` (index 2, every further cue of a multi-selection); the index is `min(2, cue.par.Selectionindex + 1)` from the vertex shader, and the badge border uses the same three-state test. Badge `(0.059,0.071,0.086)`, wire icon colours, vertical shade `mix(0.88, 1.07, …)`. These are patched as text by `apply_ui_theme.py` (`CUE_SHADER_*`, `BADGE_*`, `ICON_*`) — a palette change means editing those blocks and re-running; the idle literal is close to but not identical to the `cue_outline` token, so keep them in sync by hand.
- `geo_TimeIcons/phong4GLSLVertex`: `gl_PointSize = 70.` — the glyph atlas layout is coupled to this sprite size, **do not resize** it to fit more labels (adjust the ruler thresholds instead, see below). The label tint is the literal `outcol.rgb *= vec3(0.560, 0.600, 0.640)` in `phong4GLSLPixel`.
- 3D typography: font `Bahnschrift Condensed` everywhere; layer label 11.5 px `(0.62,0.66,0.72)` at `positionx 0.075`; cue title 26 px `(0.88,0.91,0.94)`.
- Cue preset map is duplicated: `COLOR_MAP` inside `Timeline3D/Cues/parexec_cue_colors` **and** `CUE_NEW`/`CUE_OLD` in `apply_ui_theme.py` (the old values are only used to migrate cues painted before the restyle). Change both, otherwise menu presets and existing cues drift apart.
- 2D chrome label colours are literal greys, e.g. `(0.72,0.78,0.84)` on duration buttons, `(0.42,0.44,0.46)` on `text_dur_label`, `(0.70,0.32,0.32)` on `text_Clear`, `(0.78,0.82,0.86)` on popup rows.
- Accent rail `uWidth = 0.040` and its 256×256 resolution; fixed resolution is mandatory (see Contract 1) — never switch these TOPs to `parpanel`.

**Related but separate:** ruler label *density* is not part of the theme. It is driven by the 16 `uBecomesVisibleAt` presets in `Timeline3D/Canvas/base_Settings_Processing/base_GetPattern` (`datto2_10Sec` … `datto_1200Min`, backed by `table1..15`), selected by `switch1`:

- Rule for every preset: threshold = 1.5 × class interval, so a class of interval `I` only draws while `uStepValue <= 1.5·I` and labels stay ≥ ~70 px apart.
- `switch1.index` is an expression on `uStepValue` that picks the preset whose nominal step is the smallest one `>=` the current step (6 % tolerance, because the step lands slightly above the nominal — 30.03 for the 30 s band). Verified: step 8.75 → `10Sec` (10 s labels), 30.03 → `30Sec` (30 s), 57 → `60Sec` (1 m).
- Scripts: `scripts/apply_ruler_thresholds.py` (single active preset) and `scripts/wire_ruler_presets.py` (normalises all 16 and installs the expression; idempotent).
- Do **not** fix label crowding by shrinking `gl_PointSize`; the glyph atlas is coupled to 70 px.

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
