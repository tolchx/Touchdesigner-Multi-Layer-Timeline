"""
osc_handler.py — Show Control OSC Engine for Multi-Layer Timeline (TD-MTL)

Handles bidirectional OSC communication with Bitfocus Companion, StreamDeck,
and digital lighting/sound consoles (GrandMA, Chamsys, ETC).
"""

from typing import List, Any

def _get_mlt():
    return parent.Timeline if hasattr(parent, 'Timeline') else op('/Multi_Layer_Timeline')

def _get_time_comp():
    mlt = _get_mlt()
    return mlt.op('Timeline3D/Time') if mlt else None

def _get_timer():
    tc = _get_time_comp()
    return tc.op('timer1') if tc else None

def _get_manager():
    mlt = _get_mlt()
    proj = mlt.op('Timeline3D/Project') if mlt else None
    if proj and hasattr(proj.ext, 'Manager'):
        return proj.ext.Manager
    return proj

def _get_markers():
    mlt = _get_mlt()
    m_comp = mlt.op('Timeline3D/Markers') if mlt else None
    if m_comp and hasattr(m_comp.ext, 'Markers'):
        return m_comp.ext.Markers
    return None

def onReceiveOSC(dat: 'oscinDAT', rowIndex: int, message: str, 
                 byteData: bytes, timeStamp: float, address: str, 
                 args: List[Any], peer: 'Peer'):
    """
    Main OSC dispatcher for Show Control.
    """
    try:
        addr = address.lower().strip()
        mlt = _get_mlt()
        timer = _get_timer()
        tc = _get_time_comp()
        mgr = _get_manager()
        markers = _get_markers()

        if not mlt or not timer:
            return

        # --- Transport Controls ---
        if addr in ['/timeline/play', '/play']:
            if timer['done0'].eval() > 0.5 or timer['ready0'].eval() > 0.5:
                timer.par.start.pulse()
            timer.par.play = True
            try: mlt.Callbacks.OnPlayStateChange(1)
            except Exception: pass

        elif addr in ['/timeline/pause', '/pause']:
            timer.par.play = False
            try: mlt.Callbacks.OnPlayStateChange(2)
            except Exception: pass

        elif addr in ['/timeline/stop', '/stop']:
            timer.par.play = False
            if tc and hasattr(tc, 'GotoTime'):
                tc.GotoTime(seconds=0.0)
            else:
                timer.par.initialize.pulse()
            try: mlt.Callbacks.OnPlayStateChange(0)
            except Exception: pass

        elif addr in ['/timeline/toggle_play', '/timeline/play_pause', '/toggle']:
            if timer.par.play.eval():
                timer.par.play = False
                try: mlt.Callbacks.OnPlayStateChange(2)
                except Exception: pass
            else:
                if timer['done0'].eval() > 0.5 or timer['ready0'].eval() > 0.5:
                    timer.par.start.pulse()
                timer.par.play = True
                try: mlt.Callbacks.OnPlayStateChange(1)
                except Exception: pass

        # --- Navigation & Seeking ---
        elif addr in ['/timeline/goto', '/timeline/seek', '/goto']:
            if args:
                target_sec = max(0.0, float(args[0]))
                tot_len = float(timer.par.length.eval()) if hasattr(timer.par, 'length') else 30.0
                target_sec = min(tot_len, target_sec)
                if tc and hasattr(tc, 'GotoTime'):
                    tc.GotoTime(seconds=target_sec)

        elif addr in ['/timeline/goto_fraction', '/goto_fraction']:
            if args:
                frac = max(0.0, min(1.0, float(args[0])))
                tot_len = float(timer.par.length.eval()) if hasattr(timer.par, 'length') else 30.0
                target_sec = frac * tot_len
                if tc and hasattr(tc, 'GotoTime'):
                    tc.GotoTime(seconds=target_sec)

        elif addr in ['/timeline/step', '/step']:
            frames = int(args[0]) if args else 1
            if tc and hasattr(tc, 'StepFrame'):
                tc.StepFrame(frames)

        elif addr in ['/timeline/home', '/home']:
            rs = mlt.op('container_RangeSlider')
            if rs:
                rs.par.Lrange = 0.0
                rs.par.Rrange = 1.0

        # --- Markers & Show Control Actions ---
        elif addr in ['/timeline/go', '/go', '/timeline/marker/go']:
            if markers:
                markers.TriggerGo()
            else:
                if timer['done0'].eval() > 0.5 or timer['ready0'].eval() > 0.5:
                    timer.par.start.pulse()
                timer.par.play = True

        elif addr in ['/timeline/marker/jump', '/marker/jump']:
            if args and markers:
                markers.JumpToMarker(args[0])

        elif addr in ['/timeline/marker/next', '/marker/next']:
            if markers:
                markers.NextMarker()

        elif addr in ['/timeline/marker/prev', '/marker/prev']:
            if markers:
                markers.PrevMarker()

        elif addr in ['/timeline/marker/add', '/marker/add']:
            if markers:
                name = str(args[0]) if args else None
                markers.AddMarker(name=name)

        # --- Editing Actions ---
        elif addr in ['/timeline/split', '/split']:
            if mgr and hasattr(mgr, 'SplitCueAtPlayhead'):
                mgr.SplitCueAtPlayhead()

        elif addr in ['/timeline/duplicate', '/duplicate']:
            if mgr and hasattr(mgr, 'DuplicateSelectedCues'):
                mgr.DuplicateSelectedCues()

        # --- Layer Control ---
        elif addr.startswith('/timeline/layer/'):
            parts = addr.split('/')
            if len(parts) >= 4:
                sub = parts[3]
                if sub == 'mute' and len(args) >= 2:
                    _set_layer_param(int(args[0]), 'Mute', bool(args[1]))
                elif sub == 'solo' and len(args) >= 2:
                    _set_layer_param(int(args[0]), 'Solo', bool(args[1]))
                elif sub == 'opacity' and len(args) >= 2:
                    _set_layer_param(int(args[0]), 'Opacity', float(args[1]))

    except Exception as e:
        print(f'[OSC Error] {address}: {e}')

def _set_layer_param(layer_idx: int, param_name: str, value: Any):
    mlt = _get_mlt()
    layers_comp = mlt.op('Timeline3D/Layers') if mlt else None
    if layers_comp:
        layer_op = layers_comp.op(f'base_Layer{layer_idx}')
        if layer_op and hasattr(layer_op.par, param_name):
            setattr(layer_op.par, param_name, value)
