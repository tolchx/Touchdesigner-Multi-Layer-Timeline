# keyboardin1_callbacks
# Keyboard shortcut handler for Multi-Layer Timeline

userSettings = ipar.UserSettings
systemSettings = ipar.SystemSettings
manager = parent.Main.op('Project')

def _home_view():
    mlt = parent.Main.parent()
    rs = mlt.op('container_RangeSlider') if mlt else None
    if rs is not None:
        rs.par.Lrange = 0.0
        rs.par.Rrange = 1.0

def _center_playhead_view():
    mlt = parent.Main.parent()
    rs = mlt.op('container_RangeSlider') if mlt else None
    time_comp = parent.Main.op('Time')
    if rs is not None and time_comp is not None:
        timer = time_comp.op('timer1')
        cur_sec = float(timer['timer_seconds0'].eval()) if timer and timer['timer_seconds0'] is not None else 0.0
        tot_len = float(timer.par.length.eval()) if timer and hasattr(timer.par, 'length') else 30.0
        frac = cur_sec / max(0.001, tot_len)
        span = float(rs.par.Rrange.eval()) - float(rs.par.Lrange.eval())
        span = max(0.01, min(1.0, span))
        half = span * 0.5
        new_l = max(0.0, frac - half)
        new_r = min(1.0, frac + half)
        if new_l == 0.0:
            new_r = min(1.0, span)
        elif new_r == 1.0:
            new_l = max(0.0, 1.0 - span)
        rs.par.Lrange = new_l
        rs.par.Rrange = new_r

def onKey(dat, key, character, alt, lAlt, rAlt, ctrl, lCtrl, rCtrl, shift, lShift, rShift, state, time, cmd, lCmd, rCmd):
    if state == 1: # only trigger on release
        return

    # Delete cues
    if key in ['delete', 'backspace']:
        if hasattr(manager, 'RemoveCues'):
            manager.RemoveCues()
        return

    # Home view (H)
    if key in ['h', 'H'] and not ctrl and not alt:
        _home_view()
        return

    # Center view on playhead (G)
    if key in ['g', 'G'] and not ctrl and not alt:
        _center_playhead_view()
        return

    # Space: Play/Pause toggle
    if key == 'space':
        time_comp = parent.Main.op('Time')
        if time_comp and hasattr(time_comp, 'TogglePlay'):
            time_comp.TogglePlay()
        return

    # Left / Right arrows: Frame stepping
    if key == 'left':
        step = -5 if shift else -1
        time_comp = parent.Main.op('Time')
        if time_comp and hasattr(time_comp, 'StepFrame'):
            time_comp.StepFrame(step)
        return

    if key == 'right':
        step = 5 if shift else 1
        time_comp = parent.Main.op('Time')
        if time_comp and hasattr(time_comp, 'StepFrame'):
            time_comp.StepFrame(step)
        return

    return

def onShortcut(dat, shortcutName, time):
    if shortcutName == 'ctrl.-': # zoom out
        curZoom = userSettings.Zoom.eval()
        userSettings.Zoom = max(1, curZoom - .1)
    elif shortcutName == 'ctrl.=':
        curZoom = userSettings.Zoom.eval()
        userSettings.Zoom = min(2, curZoom + .1)
    elif shortcutName == 'ctrl.c':
        manager.CopyOperation()
    elif shortcutName == 'ctrl.v':
        manager.PasteOperation()
    return
