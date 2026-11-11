"""
osc_feedback.py — Sends real-time OSC status back to Bitfocus Companion / StreamDeck

Transmits:
- /timeline/state (int: 0=Stopped, 1=Playing, 2=Paused)
- /timeline/state_str (str: "STOPPED", "PLAYING", "PAUSED")
- /timeline/timecode (str: "HH:MM:SS:FF")
- /timeline/seconds (float)
- /timeline/fraction (float)
- /timeline/duration (float)
"""

def _format_timecode(seconds: float, rate: float = 60.0) -> str:
    total_frames = int(seconds * rate)
    frames = total_frames % int(rate)
    total_sec = int(seconds)
    secs = total_sec % 60
    mins = (total_sec // 60) % 60
    hours = total_sec // 3600
    return f"{hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}"

def send_status():
    mlt = parent.Timeline if hasattr(parent, 'Timeline') else op('/Multi_Layer_Timeline')
    if not mlt or not hasattr(mlt.par, 'Enableosc') or not mlt.par.Enableosc.eval():
        return

    oscout = op('oscout1')
    if not oscout or not oscout.par.active.eval():
        return

    tc = mlt.op('Timeline3D/Time')
    if not tc:
        return
    timer = tc.op('timer1')
    if not timer:
        return

    # Evaluate current state
    is_playing = bool(timer.par.play.eval())
    is_ready = float(timer['ready0'].eval()) > 0.5 if timer['ready0'] is not None else False
    is_done = float(timer['done0'].eval()) > 0.5 if timer['done0'] is not None else False
    cur_sec = float(timer['timer_seconds0'].eval()) if timer['timer_seconds0'] is not None else 0.0
    tot_len = float(timer.par.length.eval()) if hasattr(timer.par, 'length') else 30.0
    frac = cur_sec / max(0.001, tot_len)

    if is_playing:
        state = 1
        state_str = "PLAYING"
    elif is_ready or is_done:
        state = 0
        state_str = "STOPPED"
    else:
        state = 2
        state_str = "PAUSED"

    fps = me.time.rate if hasattr(me, 'time') and hasattr(me.time, 'rate') else 60.0
    tc_str = _format_timecode(cur_sec, fps)

    try:
        oscout.sendOSC('/timeline/state', [state])
        oscout.sendOSC('/timeline/state_str', [state_str])
        oscout.sendOSC('/timeline/timecode', [tc_str])
        oscout.sendOSC('/timeline/seconds', [round(cur_sec, 3)])
        oscout.sendOSC('/timeline/fraction', [round(frac, 4)])
        oscout.sendOSC('/timeline/duration', [round(tot_len, 3)])
    except Exception:
        pass
