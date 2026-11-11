"""
midi_handler.py — Show Control MIDI Engine for Multi-Layer Timeline (TD-MTL)

Maps MIDI hardware controllers (APC40, nanoKONTROL, X-Touch, Launchpad):
- Transport: Play, Pause, Stop, Step Frames
- Jog Wheel: Scrubbing (CC 60)
- Faders: CC 1-8 -> Layer 0-7 Opacity
- Master: CC 9 -> Audio Track Gain
- Notes: Note 94 (Play), 93 (Stop), 95 (Split), 60 (GO)
"""

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

def onReceiveMIDI(dat: 'midieventDAT', event):
    """
    Called when MIDI data is received.
    event: NamedTuple (message, channel, index, value, value14, input, byteData)
    """
    try:
        mlt = _get_mlt()
        if not mlt or not hasattr(mlt.par, 'Enablemidi') or not mlt.par.Enablemidi.eval():
            return

        timer = _get_timer()
        tc = _get_time_comp()
        mgr = _get_manager()
        if not timer:
            return

        msg = event.message
        idx = event.index
        val = event.value

        # --- Note On Events ---
        if msg == 'Note On' and val > 0:
            if idx in [94, 115]:  # Play
                if timer['done0'].eval() > 0.5 or timer['ready0'].eval() > 0.5:
                    timer.par.start.pulse()
                timer.par.play = True
                try: mlt.Callbacks.OnPlayStateChange(1)
                except Exception: pass

            elif idx in [93, 114]:  # Stop / Pause
                if timer.par.play.eval():
                    timer.par.play = False
                    try: mlt.Callbacks.OnPlayStateChange(2)
                    except Exception: pass
                else:
                    timer.par.initialize.pulse()
                    try: mlt.Callbacks.OnPlayStateChange(0)
                    except Exception: pass

            elif idx in [60]:  # Middle C / GO
                if timer['done0'].eval() > 0.5 or timer['ready0'].eval() > 0.5:
                    timer.par.start.pulse()
                timer.par.play = True
                try: mlt.Callbacks.OnPlayStateChange(1)
                except Exception: pass

            elif idx in [95, 116]:  # Split Cue
                if mgr and hasattr(mgr, 'SplitCueAtPlayhead'):
                    mgr.SplitCueAtPlayhead()

            elif idx in [91, 112]:  # Step Prev (-1 frame)
                if tc and hasattr(tc, 'StepFrame'):
                    tc.StepFrame(-1)

            elif idx in [92, 113]:  # Step Next (+1 frame)
                if tc and hasattr(tc, 'StepFrame'):
                    tc.StepFrame(1)

        # --- Control Change (CC) Events ---
        elif msg == 'Control Change':
            # Transport CC
            if idx == 115 and val > 64:  # Play CC
                if timer['done0'].eval() > 0.5 or timer['ready0'].eval() > 0.5:
                    timer.par.start.pulse()
                timer.par.play = True
                try: mlt.Callbacks.OnPlayStateChange(1)
                except Exception: pass

            elif idx == 114 and val > 64:  # Stop CC
                timer.par.play = False
                timer.par.initialize.pulse()
                try: mlt.Callbacks.OnPlayStateChange(0)
                except Exception: pass

            # Jog Wheel / Scrubbing (CC 60)
            elif idx == 60:
                # Relative encoder: >64 forward, <64 backward, or 127/1
                step = 1 if val < 64 else -1
                if tc and hasattr(tc, 'StepFrame'):
                    tc.StepFrame(step)

            # Layer Opacity Faders: CC 1 to 8 -> Layers 0 to 7
            elif 1 <= idx <= 8:
                layer_num = idx - 1
                norm_val = val / 127.0
                layers_comp = mlt.op('Timeline3D/Layers')
                if layers_comp:
                    lop = layers_comp.op(f'base_Layer{layer_num}')
                    if lop and hasattr(lop.par, 'Opacity'):
                        lop.par.Opacity = norm_val

            # Master Audio Gain: CC 9
            elif idx == 9:
                norm_gain = val / 127.0
                at = mlt.op('container_AudioTrack')
                if at:
                    gain_op = at.op('math_gain')
                    if gain_op and hasattr(gain_op.par, 'gain'):
                        gain_op.par.gain = norm_gain

    except Exception as e:
        print(f'[MIDI Error]: {e}')
