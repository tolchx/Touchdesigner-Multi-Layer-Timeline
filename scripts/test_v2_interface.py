# Comprehensive Automated Verification Suite for v2.0 UI
mlt = op('/Multi_Layer_Timeline')
if not mlt:
    raise Exception('Multi_Layer_Timeline not found')

results = []

def record(test_name, success, detail=""):
    results.append({'test': test_name, 'ok': success, 'detail': detail})
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {test_name}: {detail}")

# --- TEST 1: Zero Errors Mandate ---
errs = [o.path + ': ' + o.errors() for o in mlt.findChildren() if o.errors()]
record("Zero Errors Check", len(errs) == 0, f"{len(errs)} errors found: {errs[:3]}")

# --- TEST 2: Transport Play / Pause / Rewind via Time Extension ---
time_ext = mlt.op('Timeline3D/Time').ext.Time
timer = mlt.op('Timeline3D/Time/timer1')

# Jump to 0.0s
time_ext.GotoTime(seconds=0.0)
s0 = timer['timer_seconds0'].eval()

# Jump to 10.0s
time_ext.GotoTime(seconds=10.0)
s1 = timer['timer_seconds0'].eval()

# Jump back to 0.0s
time_ext.GotoTime(seconds=0.0)
s2 = timer['timer_seconds0'].eval()

goto_ok = (s0 == 0.0) and (s1 == 10.0) and (s2 == 0.0)
record("Transport Goto & Seek", goto_ok, f"s0={s0:.1f}s -> s1={s1:.1f}s -> s2={s2:.1f}s")

# --- TEST 3: Frame Stepping (+1F, -1F) ---
time_ext.GotoTime(seconds=5.0)
t_init = timer['timer_seconds0'].eval()
time_ext.StepFrame(1)
t_plus1 = timer['timer_seconds0'].eval()
time_ext.StepFrame(-1)
t_minus1 = timer['timer_seconds0'].eval()

step_ok = (abs(t_plus1 - t_init - (1.0/60.0)) < 1e-4) and (abs(t_minus1 - t_init) < 1e-4)
record("Frame Stepping (+1F / -1F)", step_ok, f"init={t_init:.4f}s -> +1F={t_plus1:.4f}s -> -1F={t_minus1:.4f}s")

# --- TEST 4: Loop Mode Toggle ---
btn_loop = mlt.op('container_Transport/btn_Loop')
init_cycle = bool(timer.par.cycle.eval())
if btn_loop and btn_loop.op('exec'):
    btn_loop.op('exec').module.onOffToOn(None)
    cycle_toggled = bool(timer.par.cycle.eval())
    btn_loop.op('exec').module.onOffToOn(None)
    cycle_restored = bool(timer.par.cycle.eval())
    loop_ok = (cycle_toggled != init_cycle) and (cycle_restored == init_cycle)
    record("Transport Loop Toggle", loop_ok, f"initial={init_cycle} -> toggled={cycle_toggled} -> restored={cycle_restored}")
else:
    record("Transport Loop Toggle", False, "btn_Loop/exec not found")

# --- TEST 5: Layout Presets Switching ---
taskbar = mlt.op('ui_taskbar')
btn_std = taskbar.op('comp_Layouts/btn_Std/exec') if taskbar else None
btn_tl = taskbar.op('comp_Layouts/btn_TL/exec') if taskbar else None
btn_prev_l = taskbar.op('comp_Layouts/btn_Prev/exec') if taskbar else None

if btn_tl and btn_std and btn_prev_l:
    btn_tl.module.onOffToOn(None)
    ta_tl = mlt.op('Timeline3D').par.topanchor.eval()
    btn_prev_l.module.onOffToOn(None)
    ta_prev = mlt.op('Timeline3D').par.topanchor.eval()
    btn_std.module.onOffToOn(None)
    ta_std = mlt.op('Timeline3D').par.topanchor.eval()
    layout_ok = (ta_tl == 0.520) and (ta_prev == 0.280) and (ta_std == 0.421)
    record("Taskbar Layout Presets", layout_ok, f"TL_Focus={ta_tl} -> Prev_Focus={ta_prev} -> Standard={ta_std}")
else:
    record("Taskbar Layout Presets", False, "Layout preset buttons not found")

# --- TEST 6: Preview Monitor Mode Switching ---
prev_comp = mlt.op('container_Preview')
hb = prev_comp.op('header_bar') if prev_comp else None
if hb and hb.op('panelexec_buttons'):
    pex = hb.op('panelexec_buttons').module
    class DummyPanel:
        def __init__(self, owner): self.owner = owner

    pex.onOffToOn(DummyPanel(hb.op('btn_out2')))
    m_out2 = prev_comp.par.Previewmode.eval()
    pex.onOffToOn(DummyPanel(hb.op('btn_split1')))
    m_split = prev_comp.par.Previewmode.eval()
    pex.onOffToOn(DummyPanel(hb.op('btn_out1')))
    m_out1 = prev_comp.par.Previewmode.eval()
    
    prev_ok = (m_out2 == 'out2') and (m_split == 'split') and (m_out1 == 'out1')
    record("Preview Monitor Switching", prev_ok, f"out2={m_out2}, split={m_split}, out1={m_out1}")
else:
    record("Preview Monitor Switching", False, "header_bar panelexec not found")

# --- TEST 7: Inspector Color Swatches ---
c0 = mlt.op('Timeline3D/Cues/base_Cue0')
focus_tab = mlt.op('UI/table_focuspath')
insp = mlt.op('container_InspectorHeader')

if c0 and focus_tab and insp:
    focus_tab[0, 0] = c0.path
    sw_green = insp.op('comp_Swatches/dot_EmeraldGreen/exec')
    sw_blue = insp.op('comp_Swatches/dot_DefaultBlue/exec')
    
    sw_green.module.onOffToOn(None)
    g_preset = c0.par.Colorpreset.eval()
    g_rgb = (round(c0.par.Backgroundcolorr.eval(), 2), round(c0.par.Backgroundcolorg.eval(), 2), round(c0.par.Backgroundcolorb.eval(), 2))
    
    sw_blue.module.onOffToOn(None)
    b_preset = c0.par.Colorpreset.eval()
    b_rgb = (round(c0.par.Backgroundcolorr.eval(), 2), round(c0.par.Backgroundcolorg.eval(), 2), round(c0.par.Backgroundcolorb.eval(), 2))
    
    swatch_ok = (g_preset == 'EmeraldGreen' and g_rgb == (0.05, 0.38, 0.18)) and (b_preset == 'DefaultBlue' and b_rgb == (0.0, 0.18, 0.4))
    record("Inspector Color Swatches", swatch_ok, f"EmeraldGreen={g_rgb} -> DefaultBlue={b_rgb}")
else:
    record("Inspector Color Swatches", False, "c0 or swatches not found")

# --- TEST 8: Audio Header Mute & Solo ---
ah = mlt.op('container_AudioHeader')
tr = mlt.op('container_AudioTrack')
if ah and tr and ah.op('panelexec_header'):
    ah_pex = ah.op('panelexec_header').module
    ah_pex.onOffToOn(DummyPanel(ah.op('btn_Mute')))
    m_on = bool(tr.par.Mute.eval())
    ah_pex.onOffToOn(DummyPanel(ah.op('btn_Mute')))
    m_off = bool(tr.par.Mute.eval())
    
    ah_pex.onOffToOn(DummyPanel(ah.op('btn_Solo')))
    s_on = bool(tr.par.Solo.eval())
    ah_pex.onOffToOn(DummyPanel(ah.op('btn_Solo')))
    s_off = bool(tr.par.Solo.eval())
    
    audio_ok = (m_on and not m_off) and (s_on and not s_off)
    record("Audio Header Mute & Solo", audio_ok, f"Mute={m_on}->{m_off}, Solo={s_on}->{s_off}")
else:
    record("Audio Header Mute & Solo", False, "Audio header/track not found")

# --- TEST 9: Playback Engine & Video Outputs ---
out1 = mlt.op('Timeline3D/out1')
out2 = mlt.op('Timeline3D/out2')
pb_ok = (out1 is not None and out1.width == 1920 and out1.height == 1080) and (out2 is not None and out2.width == 1920 and out2.height == 1080)
record("Playback 1080p Video Outputs", pb_ok, f"out1={out1.width}x{out1.height}, out2={out2.width}x{out2.height}")

# --- TEST 10: Performance & 60 FPS Verification ---
perf = mlt.op('container_Transport/container_GPUStats/null_perf')
fps = perf['cookrate'].eval()
msec = perf['msec'].eval()
vram = perf['gpu_mem_used'].eval()
perf_ok = (fps >= 58.0) and (msec < 20.0)
record("Live 60 FPS Performance", perf_ok, f"FPS={fps:.1f}, CookTime={msec:.2f}ms, VRAM={vram:.0f}MB")

# Final Summary
pass_count = sum(1 for r in results if r['ok'])
print(f"\n==========================================")
print(f"VERIFICATION SUITE: {pass_count}/{len(results)} TESTS PASSED")
print(f"==========================================")
