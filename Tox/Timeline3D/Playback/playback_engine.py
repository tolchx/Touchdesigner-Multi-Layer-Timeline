# PlaybackEngine for TouchDesigner Multi-Layer Timeline
# Evaluates active cues under the green playhead line, updates per-cue base_Scene/cue_time,
# and composites active layers to out1 and out2, plus audio to out_audio.

DEFAULT_THUMB_PATH = '/Multi_Layer_Timeline/Timeline3D/Cues/moviefilein1'

_state = {
    'opacities': {},
    'active_scenes': set(),
    'active_cue_names': set(),
}


def _pb():
    return me.parent()


def _tl():
    return _pb().parent()


def _default_thumb_op():
    cues = _tl().op('Cues')
    if cues:
        t = cues.op('moviefilein1')
        if t is not None:
            return t
    return op(DEFAULT_THUMB_PATH)


def _resolve_custom_top(cue, default_thumb):
    if not hasattr(cue.par, 'Thumbnail'):
        return None
    raw = str(cue.par.Thumbnail.eval() or '').strip()
    if not raw:
        return None
    target = cue.op(raw) or op(raw)
    if target is None or target == default_thumb:
        return None
    if getattr(target, 'isTOP', False):
        return target
    if getattr(target, 'isCOMP', False):
        out_op = target.op('out1')
        if out_op is not None and getattr(out_op, 'isTOP', False):
            return out_op
        outs = target.findChildren(type=outTOP, depth=1)
        if outs:
            return outs[0]
    return None


def _get_slot_count(pb):
    slots = 0
    while pb.op(f'switch_slot{slots}') is not None:
        slots += 1
    return slots


def ensure_slots(num_slots):
    pb = _pb()
    num_slots = max(1, int(num_slots))

    # --- Output 1 Background ---
    bg1 = pb.op('constant_bg')
    if bg1 is None:
        bg1 = pb.create(constantTOP, 'constant_bg')
        bg1.nodeX = 0
        bg1.nodeY = 0
        bg1.par.colorr = 0.0
        bg1.par.colorg = 0.0
        bg1.par.colorb = 0.0
        bg1.par.alpha = 1.0
        bg1.par.outputresolution = 'custom'
    bg1.par.resolutionw.expr = 'parent().par.Out1resw'
    bg1.par.resolutionh.expr = 'parent().par.Out1resh'

    # --- Output 2 Background ---
    bg2 = pb.op('constant_bg2')
    if bg2 is None:
        bg2 = pb.create(constantTOP, 'constant_bg2')
        bg2.nodeX = 0
        bg2.nodeY = -1200
        bg2.par.colorr = 0.0
        bg2.par.colorg = 0.0
        bg2.par.colorb = 0.0
        bg2.par.alpha = 1.0
        bg2.par.outputresolution = 'custom'
    bg2.par.resolutionw.expr = 'parent().par.Out2resw'
    bg2.par.resolutionh.expr = 'parent().par.Out2resh'

    # --- Output 1 Final Nodes ---
    null_out1 = pb.op('null_out')
    if null_out1 is None:
        null_out1 = pb.create(nullTOP, 'null_out')
    out_top1 = pb.op('out1')
    if out_top1 is None:
        out_top1 = pb.create(outTOP, 'out1')

    # --- Output 2 Final Nodes ---
    null_out2 = pb.op('null_out2')
    if null_out2 is None:
        null_out2 = pb.create(nullTOP, 'null_out2')
    out_top2 = pb.op('out2')
    if out_top2 is None:
        out_top2 = pb.create(outTOP, 'out2')

    # --- Audio Final Nodes ---
    out_audio = pb.op('out_audio')
    if out_audio is None:
        out_audio = pb.create(outCHOP, 'out_audio')
        out_audio.nodeX = 1540
        out_audio.nodeY = -600

    merge_audio = pb.op('merge_audio')
    if merge_audio is None:
        merge_audio = pb.create(mergeCHOP, 'merge_audio')
        merge_audio.nodeX = 1340
        merge_audio.nodeY = -600
        merge_audio.outputConnectors[0].connect(out_audio.inputConnectors[0])

    prev_op_out1 = bg1
    prev_op_out2 = bg2

    for i in range(num_slots):
        y = -240 * (i + 1)

        mfi = pb.op(f'mfi_slot{i}')
        if mfi is None:
            mfi = pb.create(moviefileinTOP, f'mfi_slot{i}')
            mfi.nodeX = 0
            mfi.nodeY = y
            mfi.par.playmode = 'specify'
            mfi.par.indexunit = 'seconds'
            mfi.par.play = True
            mfi.par.index = 0.0
            mfi.par.alwaysloadinitial = True
            mfi.par.loadingerrorimage = 'zero'
            mfi.par.file = ''
        mfi.par.prereadframes = 24
        mfi.par.highperfread = True

        info = pb.op(f'info_slot{i}')
        if info is None:
            info = pb.create(infoCHOP, f'info_slot{i}')
            info.nodeX = 0
            info.nodeY = y - 120
            info.par.op = mfi.name

        txt_op = pb.op(f'text_slot{i}')
        if txt_op is None:
            txt_op = pb.create(textTOP, f'text_slot{i}')
            txt_op.nodeX = 0
            txt_op.nodeY = y - 60
            txt_op.par.outputresolution = 'custom'
            txt_op.par.resolutionw.expr = 'parent().par.Out1resw'
            txt_op.par.resolutionh.expr = 'parent().par.Out1resh'
            txt_op.par.alignx = 'center'
            txt_op.par.aligny = 'center'
            txt_op.par.bgcolorr = 0.0
            txt_op.par.bgcolorg = 0.0
            txt_op.par.bgcolorb = 0.0
            txt_op.par.bgalpha = 0.0

        sel = pb.op(f'select_slot{i}')
        if sel is None:
            sel = pb.create(selectTOP, f'select_slot{i}')
            sel.nodeX = 220
            sel.nodeY = y
            sel.par.top = mfi.name

        fit = pb.op(f'fit_slot{i}')
        if fit is None:
            fit = pb.create(fitTOP, f'fit_slot{i}')
            fit.nodeX = 440
            fit.nodeY = y
            fit.par.fit = 'fit'
            fit.par.bgcolorr = 0.0
            fit.par.bgcolorg = 0.0
            fit.par.bgcolorb = 0.0
            fit.par.bgcolora = 0.0
            fit.par.premultrgbbyalpha = True
            fit.par.outputresolution = 'custom'
            fit.par.resolutionw.expr = 'parent().par.Out1resw'
            fit.par.resolutionh.expr = 'parent().par.Out1resh'
        if not fit.inputs or fit.inputs[0] != sel:
            sel.outputConnectors[0].connect(fit.inputConnectors[0])

        lvl = pb.op(f'level_slot{i}')
        if lvl is None:
            lvl = pb.create(levelTOP, f'level_slot{i}')
            lvl.nodeX = 660
            lvl.nodeY = y
            lvl.par.opacity = 1.0
        if not lvl.inputs or lvl.inputs[0] != fit:
            fit.outputConnectors[0].connect(lvl.inputConnectors[0])

        # --- Output 1 Over & Switch ---
        ovr1 = pb.op(f'over_slot{i}')
        if ovr1 is None:
            ovr1 = pb.create(overTOP, f'over_slot{i}')
            ovr1.nodeX = 880
            ovr1.nodeY = y
            ovr1.par.size = 'input2'
            ovr1.par.prefit = 'fill'
        if len(ovr1.inputs) < 2 or ovr1.inputs[0] != lvl:
            lvl.outputConnectors[0].connect(ovr1.inputConnectors[0])
        if len(ovr1.inputs) < 2 or ovr1.inputs[1] != prev_op_out1:
            prev_op_out1.outputConnectors[0].connect(ovr1.inputConnectors[1])

        sw1 = pb.op(f'switch_slot{i}')
        if sw1 is None:
            sw1 = pb.create(switchTOP, f'switch_slot{i}')
            sw1.nodeX = 1100
            sw1.nodeY = y
            sw1.par.index = 0
        if len(sw1.inputs) < 2 or sw1.inputs[0] != prev_op_out1:
            prev_op_out1.outputConnectors[0].connect(sw1.inputConnectors[0])
        if len(sw1.inputs) < 2 or sw1.inputs[1] != ovr1:
            ovr1.outputConnectors[0].connect(sw1.inputConnectors[1])

        prev_op_out1 = sw1

        # --- Output 2 Over & Switch ---
        ovr2 = pb.op(f'over_slot{i}_out2')
        if ovr2 is None:
            ovr2 = pb.create(overTOP, f'over_slot{i}_out2')
            ovr2.nodeX = 880
            ovr2.nodeY = y - 1200
            ovr2.par.size = 'input2'
            ovr2.par.prefit = 'fill'
        if len(ovr2.inputs) < 2 or ovr2.inputs[0] != lvl:
            lvl.outputConnectors[0].connect(ovr2.inputConnectors[0])
        if len(ovr2.inputs) < 2 or ovr2.inputs[1] != prev_op_out2:
            prev_op_out2.outputConnectors[0].connect(ovr2.inputConnectors[1])

        sw2 = pb.op(f'switch_slot{i}_out2')
        if sw2 is None:
            sw2 = pb.create(switchTOP, f'switch_slot{i}_out2')
            sw2.nodeX = 1100
            sw2.nodeY = y - 1200
            sw2.par.index = 0
        if len(sw2.inputs) < 2 or sw2.inputs[0] != prev_op_out2:
            prev_op_out2.outputConnectors[0].connect(sw2.inputConnectors[0])
        if len(sw2.inputs) < 2 or sw2.inputs[1] != ovr2:
            ovr2.outputConnectors[0].connect(sw2.inputConnectors[1])

        prev_op_out2 = sw2

        # --- Audio slot CHOPs ---
        ain = pb.op(f'audio_slot{i}')
        if ain is None:
            ain = pb.create(audiofileinCHOP, f'audio_slot{i}')
            ain.nodeX = 900
            ain.nodeY = -600 - (i * 60)
            ain.par.file = ''
            ain.par.play = False

        amath = pb.op(f'math_audio_slot{i}')
        if amath is None:
            amath = pb.create(mathCHOP, f'math_audio_slot{i}')
            amath.nodeX = 1120
            amath.nodeY = -600 - (i * 60)
            amath.par.gain = 0.0
            ain.outputConnectors[0].connect(amath.inputConnectors[0])

        if amath not in merge_audio.inputs:
            amath.outputConnectors[0].connect(merge_audio.inputConnectors[0])

    null_out1.nodeX = 1340
    null_out1.nodeY = -240
    out_top1.nodeX = 1540
    out_top1.nodeY = -240
    if not null_out1.inputs or null_out1.inputs[0] != prev_op_out1:
        prev_op_out1.outputConnectors[0].connect(null_out1.inputConnectors[0])
    if not out_top1.inputs or out_top1.inputs[0] != null_out1:
        null_out1.outputConnectors[0].connect(out_top1.inputConnectors[0])

    null_out2.nodeX = 1340
    null_out2.nodeY = -1440
    out_top2.nodeX = 1540
    out_top2.nodeY = -1440
    if not null_out2.inputs or null_out2.inputs[0] != prev_op_out2:
        prev_op_out2.outputConnectors[0].connect(null_out2.inputConnectors[0])
    if not out_top2.inputs or out_top2.inputs[0] != null_out2:
        null_out2.outputConnectors[0].connect(out_top2.inputConnectors[0])


def rebuild():
    pb = _pb()
    tl = _tl()
    layers_comp = tl.op('Layers')
    layer_count = len(layers_comp.findChildren(tags=['LayerItem'])) if layers_comp else 5
    ensure_slots(max(5, layer_count))
    _state['opacities'].clear()
    _state['active_scenes'].clear()
    _state['active_cue_names'].clear()


def _set_slot_active(pb, slot_idx, active_out1, active_out2):
    sw1 = pb.op(f'switch_slot{slot_idx}')
    if sw1 is not None:
        target1 = 1 if active_out1 else 0
        if int(sw1.par.index.val) != target1:
            sw1.par.index = target1

    sw2 = pb.op(f'switch_slot{slot_idx}_out2')
    if sw2 is not None:
        target2 = 1 if active_out2 else 0
        if int(sw2.par.index.val) != target2:
            sw2.par.index = target2


def _compute_media_time(info, cue, local_t):
    speed = float(cue.par.Speed.eval()) if hasattr(cue.par, 'Speed') else 1.0
    if speed <= 0.0:
        speed = 1.0
    trim_start = max(0.0, float(cue.par.Trimstart.eval())) if hasattr(cue.par, 'Trimstart') else 0.0
    trim_end = max(0.0, float(cue.par.Trimend.eval())) if hasattr(cue.par, 'Trimend') else 0.0

    eff_local_t = local_t * speed

    length_ch = info['length'] if info else None
    rate_ch = info['sample_rate'] if info else None
    length_val = float(length_ch.eval() if hasattr(length_ch, 'eval') else (length_ch.val if hasattr(length_ch, 'val') else length_ch)) if length_ch is not None else 0.0
    rate_val = float(rate_ch.eval() if hasattr(rate_ch, 'eval') else (rate_ch.val if hasattr(rate_ch, 'val') else rate_ch)) if rate_ch is not None else 0.0

    if length_val > 1.0 and rate_val > 0.0:
        file_dur = length_val / rate_val
        actual_end = trim_end if (trim_end > trim_start and trim_end <= file_dur) else file_dur
        loop_span = max(0.001, actual_end - trim_start)
        loop = bool(cue.par.Loop.eval()) if hasattr(cue.par, 'Loop') else False
        if loop and loop_span > 0.0:
            return trim_start + (eff_local_t % loop_span)
        if actual_end > trim_start:
            return trim_start + min(eff_local_t, max(0.0, loop_span - (1.0 / rate_val)))
        return trim_start + eff_local_t
    if length_val == 1.0:
        return 0.0
    return trim_start + eff_local_t


def _apply_fade_curve(x, mode='Smoothstep'):
    x = max(0.0, min(1.0, x))
    if mode == 'Smoothstep':
        return x * x * (3.0 - 2.0 * x)
    elif mode == 'EaseIn':
        return x * x
    elif mode == 'EaseOut':
        return x * (2.0 - x)
    return x # Linear


def _compute_automation_curve(cue, frac, local_t, audio_val):
    mode = str(cue.par.Automode.eval()) if hasattr(cue.par, 'Automode') else 'Off'
    if mode == 'Off':
        return 1.0
    min_v = float(cue.par.Automin.eval()) if hasattr(cue.par, 'Automin') else 0.0
    max_v = float(cue.par.Automax.eval()) if hasattr(cue.par, 'Automax') else 1.0
    spd = max(0.01, float(cue.par.Autospeed.eval())) if hasattr(cue.par, 'Autospeed') else 1.0
    span = max_v - min_v

    raw = 1.0
    if mode == 'RampUp':
        raw = frac
    elif mode == 'RampDown':
        raw = 1.0 - frac
    elif mode == 'Triangle':
        raw = 1.0 - abs(2.0 * frac - 1.0)
    elif mode == 'Pulse':
        raw = 1.0 if (frac % (1.0 / spd)) < (0.5 / spd) else 0.0
    elif mode == 'SineLFO':
        import math
        raw = 0.5 + 0.5 * math.sin(local_t * spd * 2.0 * math.pi)
    elif mode == 'AudioReact':
        raw = audio_val
    return min_v + span * max(0.0, min(1.0, raw))


def _set_cue_time(ct, active, local_t, media_t, length, opacity, curve_val=1.0, audio_val=0.0, lfo_val=0.0):
    if ct is None:
        return
    frac = max(0.0, min(1.0, local_t / length)) if length > 0.0 else 0.0
    vals = (
        1.0 if active else 0.0,
        float(local_t),
        float(media_t),
        float(frac),
        float(length),
        float(opacity),
        float(curve_val),
        float(audio_val),
        float(lfo_val),
    )
    if hasattr(ct, 'seq') and hasattr(ct.seq, 'const') and ct.seq.const.numBlocks < len(vals):
        ct.seq.const.numBlocks = len(vals)
        cnames = ['active', 'local_seconds', 'media_seconds', 'fraction', 'length', 'opacity', 'curve', 'audio_react', 'lfo']
        for idx, cn in enumerate(cnames):
            setattr(ct.par, f'const{idx}name', cn)

    for idx, v in enumerate(vals):
        par_name = f'const{idx}value'
        if hasattr(ct.par, par_name):
            p = getattr(ct.par, par_name)
            if abs(float(p.val) - v) > 1e-6:
                p.val = v



def _collapse_cue_vram(cue_op):
    """Collapses VRAM footprint for an inactive cue (AAVJ standard)."""
    if not cue_op or not getattr(cue_op, 'isCOMP', False):
        return
    for r in cue_op.findChildren(type=renderTOP):
        try:
            r.par.resolution1 = 1
            r.par.resolution2 = 1
            r.bypass = True
            r.cook()
        except:
            pass
    for i in cue_op.findChildren(type=inTOP):
        try:
            if hasattr(i.par, 'outputresolution'):
                i.par.outputresolution = 'eighth'
            i.bypass = True
            i.cook()
        except:
            pass
    for g in cue_op.findChildren(type=geometryCOMP):
        try:
            g.bypass = True
            g.cook()
        except:
            pass
    for m in cue_op.findChildren(type=moviefileinTOP):
        try:
            if hasattr(m.par, 'active'):
                m.par.active = 0
        except:
            pass


def _restore_cue_vram(cue_op, res_x=1920, res_y=1080):
    """Restores full resolution and unbypasses an active cue (AAVJ standard)."""
    if not cue_op or not getattr(cue_op, 'isCOMP', False):
        return
    for i in cue_op.findChildren(type=inTOP):
        try:
            if hasattr(i.par, 'outputresolution'):
                i.par.outputresolution = 'useinput'
            i.bypass = False
            i.cook()
        except:
            pass
    for r in cue_op.findChildren(type=renderTOP):
        try:
            r.par.resolution1 = res_x
            r.par.resolution2 = res_y
            r.bypass = False
            r.cook()
        except:
            pass
    for f in cue_op.findChildren(type=feedbackTOP):
        try:
            f.bypass = False
            f.cook()
            if hasattr(f.par, 'resetpulse'):
                f.par.resetpulse.pulse()
        except:
            pass
    for g in cue_op.findChildren(type=geometryCOMP):
        try:
            g.bypass = False
            g.cook()
        except:
            pass
    for m in cue_op.findChildren(type=moviefileinTOP):
        try:
            if hasattr(m.par, 'active'):
                m.par.active = 1
        except:
            pass


def update_playback():
    pb = _pb()
    tl = _tl()
    if tl is None:
        return

    timer_chop = tl.op('Time/timer1')
    if timer_chop is not None and timer_chop['timer_seconds0'] is not None:
        t = float(timer_chop['timer_seconds0'].eval())
    else:
        cur_chop = tl.op('select_CurrentTime')
        if cur_chop is None or cur_chop.numChans == 0:
            return
        t = float(cur_chop[0].eval())

    cues_comp = tl.op('Cues')
    layers_comp = tl.op('Layers')

    audio_level = 0.0
    mlt_parent = tl.parent() if tl else None
    if mlt_parent is not None:
        at_comp = mlt_parent.op('container_AudioTrack')
        if at_comp is not None:
            fl = at_comp.op('filter_level')
            if fl is not None and fl.numChans > 0:
                audio_level = max(0.0, min(1.0, float(fl[0].eval())))
    se_dat = cues_comp.op('SceneEditor') if cues_comp else None
    se = se_dat.module if se_dat is not None else None
    cues = cues_comp.findChildren(tags=['CueItem']) if cues_comp else []

    # Refresh live thumbnail cleanly if the user currently has the CueSceneEditor floating window open
    editor_pane = ui.panes['CueSceneEditor']
    if editor_pane is not None and se is not None:
        ed_owner = getattr(editor_pane, 'owner', None)
        if ed_owner is not None:
            for c in cues:
                sc = se.resolve_scene_comp(c)
                if sc is not None and (ed_owner == sc or sc.path in ed_owner.path):
                    sel_tex = c.op('base_Textures/select1')
                    if sel_tex is not None:
                        desired = se.get_cue_thumb_top(c)
                        if sel_tex.par.top.eval() != desired:
                            se.refresh_cue_thumb(c)

    max_layer = 0
    if layers_comp:
        layer_items = layers_comp.findChildren(tags=['LayerItem'])
        if layer_items:
            max_layer = max(max_layer, len(layer_items) - 1)

    active_by_layer = {}
    upcoming_by_layer = {}
    past_by_layer = {}
    current_active_cues = set()

    for cue in cues:
        try:
            st = float(cue.par.Starttime.eval())
            length = float(cue.par.Cuelength.eval())
            if length <= 0.0:
                continue
            end = st + length
            layer_idx = max(0, int(round(cue.par.Layer.eval())))
            max_layer = max(max_layer, layer_idx)

            inst_id = int(cue.par.Instanceid.eval()) if hasattr(cue.par, 'Instanceid') else 0
            sort_key = (st, inst_id, cue.name)

            if st <= t < end:
                current_active_cues.add(cue)
                prev = active_by_layer.get(layer_idx)
                if prev is None or sort_key > prev[0]:
                    active_by_layer[layer_idx] = (sort_key, cue, st, end, length)
            elif st > t:
                prev_up = upcoming_by_layer.get(layer_idx)
                if prev_up is None or st < prev_up[0]:
                    upcoming_by_layer[layer_idx] = (st, cue)
            else:
                prev_past = past_by_layer.get(layer_idx)
                if prev_past is None or st > prev_past[0]:
                    past_by_layer[layer_idx] = (st, cue)
        except Exception:
            continue

    # Event cues: trigger Commandon on enter and Commandoff on exit
    prev_names = _state.get('active_cue_names', set())
    cur_names = {c.name for c in current_active_cues}
    entered_cues = [c for c in current_active_cues if c.name not in prev_names]
    exited_names = prev_names - cur_names

    # VRAM Collapsing Engine (AAVJ Pattern)
    mlt_root = op('/Multi_Layer_Timeline')
    vram_collapse_on = bool(mlt_root.par.Enablevramcollapse.eval()) if mlt_root and hasattr(mlt_root.par, 'Enablevramcollapse') else True

    for ec in entered_cues:
        if vram_collapse_on:
            _restore_cue_vram(ec, o1w, o1h)
        cmd = str(getattr(ec.par, 'Commandon', '') or '').strip()
        if cmd:
            try:
                exec(cmd, {'me': ec, 'op': op, 'parent': ec.parent, 'ui': ui, 'ext': ext})
            except Exception as e:
                print(f"Error executing Commandon on {ec.name}: {e}")

    for ex_name in exited_names:
        c_op = cues_comp.op(ex_name) if cues_comp else None
        if c_op is not None:
            if vram_collapse_on:
                _collapse_cue_vram(c_op)
            cmd = str(getattr(c_op.par, 'Commandoff', '') or '').strip()
            if cmd:
                try:
                    exec(cmd, {'me': c_op, 'op': op, 'parent': c_op.parent, 'ui': ui, 'ext': ext})
                except Exception as e:
                    print(f"Error executing Commandoff on {ex_name}: {e}")

    _state['active_cue_names'] = cur_names

    num_layers = max(5, max_layer + 1)
    if _get_slot_count(pb) < num_layers:
        ensure_slots(num_layers)

    total_slots = _get_slot_count(pb)
    if not bool(pb.par.Active.eval()):
        for s in range(total_slots):
            _set_slot_active(pb, s, False, False)
        return

    descending = (str(pb.par.Layerorder.eval()) == 'Descending')
    layer_order = list(range(num_layers - 1, -1, -1)) if descending else list(range(num_layers))
    default_thumb = _default_thumb_op()
    do_preload = bool(pb.par.Preload.eval())

    new_active_scenes = set()

    # Output master resolutions
    o1w = int(pb.par.Out1resw.eval()) if hasattr(pb.par, 'Out1resw') else 1920
    o1h = int(pb.par.Out1resh.eval()) if hasattr(pb.par, 'Out1resh') else 1080
    o2w = int(pb.par.Out2resw.eval()) if hasattr(pb.par, 'Out2resw') else 1920
    o2h = int(pb.par.Out2resh.eval()) if hasattr(pb.par, 'Out2resh') else 1080

    for slot_idx in range(total_slots):
        if slot_idx >= len(layer_order):
            _set_slot_active(pb, slot_idx, False, False)
            continue

        layer_idx = layer_order[slot_idx]
        layer_comp = layers_comp.op(f'base_Layer{layer_idx}') if layers_comp else None

        # Layer parameters
        layer_out = str(layer_comp.par.Output.eval()) if layer_comp and hasattr(layer_comp.par, 'Output') else 'out1'
        layer_aspect = str(layer_comp.par.Aspectratio.eval()) if layer_comp and hasattr(layer_comp.par, 'Aspectratio') else 'auto'
        layer_fit = str(layer_comp.par.Fitmode.eval()) if layer_comp and hasattr(layer_comp.par, 'Fitmode') else 'fit'
        custom_w = int(layer_comp.par.Customw.eval()) if layer_comp and hasattr(layer_comp.par, 'Customw') else 1920
        custom_h = int(layer_comp.par.Customh.eval()) if layer_comp and hasattr(layer_comp.par, 'Customh') else 1080

        mfi = pb.op(f'mfi_slot{slot_idx}')
        info = pb.op(f'info_slot{slot_idx}')
        sel = pb.op(f'select_slot{slot_idx}')
        fit = pb.op(f'fit_slot{slot_idx}')
        lvl = pb.op(f'level_slot{slot_idx}')
        txt_op = pb.op(f'text_slot{slot_idx}')
        ain = pb.op(f'audio_slot{slot_idx}')
        amath = pb.op(f'math_audio_slot{slot_idx}')

        active_entry = active_by_layer.get(layer_idx)
        if active_entry is None:
            _set_slot_active(pb, slot_idx, False, False)
            if amath is not None:
                amath.par.gain = 0.0
            if ain is not None and bool(ain.par.play.eval()):
                ain.par.play = False
            if do_preload and mfi is not None:
                candidate = upcoming_by_layer.get(layer_idx) or past_by_layer.get(layer_idx)
                if candidate is not None:
                    pre_cue = candidate[1]
                    if _resolve_custom_top(pre_cue, default_thumb) is None and hasattr(pre_cue.par, 'Imagefile'):
                        pre_file = str(pre_cue.par.Imagefile.eval() or '').strip()
                        if pre_file and mfi.par.file.val != pre_file:
                            mfi.par.file = pre_file
                            mfi.par.index = 0.0
            continue

        _, cue, st, end, cue_len = active_entry

        # Cue level overrides
        target_output = str(cue.par.Output.eval()) if hasattr(cue.par, 'Output') and cue.par.Output.eval() != 'inherit' else layer_out
        final_fit = str(cue.par.Fitmode.eval()) if hasattr(cue.par, 'Fitmode') and cue.par.Fitmode.eval() != 'inherit' else layer_fit

        # Calculate slot resolution based on aspect / custom
        if layer_aspect == '16x9':
            lw, lh = 1920, 1080
        elif layer_aspect == '16x10':
            lw, lh = 1920, 1200
        elif layer_aspect == '4x3':
            lw, lh = 1440, 1080
        elif layer_aspect == '21x9':
            lw, lh = 2560, 1080
        elif layer_aspect == '9x16':
            lw, lh = 1080, 1920
        elif layer_aspect == '1x1':
            lw, lh = 1080, 1080
        elif layer_aspect == 'custom':
            lw, lh = max(16, custom_w), max(16, custom_h)
        else: # 'auto' / Output Default
            if target_output == 'out2':
                lw, lh = o2w, o2h
            else:
                lw, lh = o1w, o1h

        if fit is not None:
            if fit.par.fit.val != final_fit:
                fit.par.fit = final_fit
            if int(fit.par.resolutionw.val) != lw:
                fit.par.resolutionw = lw
            if int(fit.par.resolutionh.val) != lh:
                fit.par.resolutionh = lh
            fit.par.bgcolora = 0.0
            fit.par.premultrgbbyalpha = True

        fi = max(0.0, float(cue.par.Fadeinout1.eval())) if hasattr(cue.par, 'Fadeinout1') else 0.0
        fo = max(0.0, float(cue.par.Fadeinout2.eval())) if hasattr(cue.par, 'Fadeinout2') else 0.0
        fade_mode = str(cue.par.Fadecurve.eval()) if hasattr(cue.par, 'Fadecurve') else 'Smoothstep'
        local_t = max(0.0, t - st)
        rem_t = max(0.0, end - t)
        fade_in = _apply_fade_curve(local_t / fi, fade_mode) if fi > 1e-6 else 1.0
        fade_out = _apply_fade_curve(rem_t / fo, fade_mode) if fo > 1e-6 else 1.0
        opacity = max(0.0, min(1.0, min(fade_in, fade_out)))

        # Layer evaluation: Mute, Solo, and Layer Opacity
        layer_num = int(cue.par.Layer.eval()) if hasattr(cue.par, 'Layer') else 0
        layer_opacity = 1.0
        mlt_root = parent.Timeline if hasattr(parent, 'Timeline') else op('/Multi_Layer_Timeline')
        layers_comp = mlt_root.op('Timeline3D/Layers') if mlt_root else None
        if layers_comp:
            layer_op = layers_comp.op(f'base_Layer{layer_num}')
            if layer_op:
                if hasattr(layer_op.par, 'Mute') and layer_op.par.Mute.eval():
                    layer_opacity = 0.0
                elif hasattr(layer_op.par, 'Solo'):
                    any_solo = any(bool(l.par.Solo.eval()) for l in layers_comp.children if l.name.startswith('base_Layer') and hasattr(l.par, 'Solo'))
                    if any_solo and not bool(layer_op.par.Solo.eval()):
                        layer_opacity = 0.0
                    else:
                        layer_opacity = float(layer_op.par.Opacity.eval()) if hasattr(layer_op.par, 'Opacity') else 1.0
                else:
                    layer_opacity = float(layer_op.par.Opacity.eval()) if hasattr(layer_op.par, 'Opacity') else 1.0

        opacity = opacity * max(0.0, min(1.0, layer_opacity))

        cue_type = str(cue.par.Type.eval() or '') if hasattr(cue.par, 'Type') else ''

        # Audio Clip handling per layer
        has_audio = False
        if (cue_type == 'Audio' or (hasattr(cue.par, 'Audiofile') and bool(cue.par.Audiofile.eval()))) and ain is not None:
            afile = str(cue.par.Audiofile.eval() or '').strip()
            if afile:
                if ain.bypass:
                    ain.bypass = False
                if ain.par.file.val != afile:
                    ain.par.file = afile
                if not bool(ain.par.play.eval()):
                    ain.par.play = True
                avol = float(cue.par.Audiovolume.eval()) if hasattr(cue.par, 'Audiovolume') else 1.0
                if amath is not None:
                    amath.par.gain = avol * opacity
                has_audio = True

        if not has_audio:
            if amath is not None:
                amath.par.gain = 0.0
            if ain is not None and not ain.bypass:
                ain.bypass = True

        scene_comp = se.resolve_scene_comp(cue) if se is not None else cue.op('base_Scene')
        scene_out = se.resolve_scene_out_top(cue) if se is not None else None
        scene_is_custom = se.is_custom_scene(cue) if se is not None else False
        custom_top = _resolve_custom_top(cue, default_thumb)

        if scene_comp is not None:
            ct = scene_comp.op('cue_time')
            scene_info = scene_comp.op('info1')
            scene_media_t = _compute_media_time(scene_info, cue, local_t)
            cue_frac = max(0.0, min(1.0, local_t / max(0.001, cue_len)))
            auto_val = _compute_automation_curve(cue, cue_frac, local_t, audio_level)
            import math
            lfo_now = 0.5 + 0.5 * math.sin(local_t * 2.0 * math.pi)
            _set_cue_time(ct, True, local_t, scene_media_t, cue_len, opacity, auto_val, audio_level, lfo_now)
            if ct is not None:
                new_active_scenes.add(ct.path)

        has_media = False

        # Text Cue
        if cue_type == 'Text' and txt_op is not None:
            raw_text = str(cue.par.Text.eval() or '') if hasattr(cue.par, 'Text') else cue.name
            font_name = str(cue.par.Font.eval() or 'Arial') if hasattr(cue.par, 'Font') else 'Arial'
            fsize = float(cue.par.Fontsize.eval()) if hasattr(cue.par, 'Fontsize') else 48.0
            fr = float(cue.par.Fontcolorr.eval()) if hasattr(cue.par, 'Fontcolorr') else 1.0
            fg = float(cue.par.Fontcolorg.eval()) if hasattr(cue.par, 'Fontcolorg') else 1.0
            fb = float(cue.par.Fontcolorb.eval()) if hasattr(cue.par, 'Fontcolorb') else 1.0
            fa = float(cue.par.Fontcolora.eval()) if hasattr(cue.par, 'Fontcolora') else 1.0

            if txt_op.par.text.val != raw_text:
                txt_op.par.text = raw_text
            if txt_op.par.font.val != font_name:
                txt_op.par.font = font_name
            if abs(float(txt_op.par.fontsizex.val) - fsize) > 1e-4:
                txt_op.par.fontsizex = fsize
            txt_op.par.fontcolorr = fr
            txt_op.par.fontcolorg = fg
            txt_op.par.fontcolorb = fb
            txt_op.par.fontalpha = fa

            if sel.par.top.val != txt_op.name:
                sel.par.top = txt_op.name
            has_media = True

        # Custom scene output
        elif scene_is_custom and scene_out is not None:
            if sel.par.top.val != scene_out.path:
                sel.par.top = scene_out.path
            has_media = True

        # Custom thumbnail / linked TOP
        elif custom_top is not None:
            if sel.par.top.val != custom_top.path:
                sel.par.top = custom_top.path
            has_media = True

        # Standalone scene editor out
        elif scene_out is not None and hasattr(cue.par, 'Imagefile') and str(cue.par.Imagefile.eval() or '').strip():
            if sel.par.top.val != scene_out.path:
                sel.par.top = scene_out.path
            has_media = True

        # Shared Movie Spec or Imagefile
        elif hasattr(cue.par, 'Moviespec') and str(cue.par.Moviespec.eval() or '').strip() and op(cue.par.Moviespec.eval()) is not None and getattr(op(cue.par.Moviespec.eval()), 'isTOP', False):
            spec_top = op(cue.par.Moviespec.eval())
            if sel.par.top.val != spec_top.path:
                sel.par.top = spec_top.path
            has_media = True

        elif hasattr(cue.par, 'Imagefile'):
            img_file = str(cue.par.Imagefile.eval() or '').strip()
            if img_file:
                if mfi.par.file.val != img_file:
                    mfi.par.file = img_file
                if mfi.par.playmode.val != 'specify':
                    mfi.par.playmode = 'specify'
                if mfi.par.indexunit.val != 'seconds':
                    mfi.par.indexunit = 'seconds'
                if not bool(mfi.par.play.eval()):
                    mfi.par.play = True
                if sel.par.top.val != mfi.name:
                    sel.par.top = mfi.name

                mfi.par.index = _compute_media_time(info, cue, local_t)
                has_media = True

        if not has_media or opacity <= 1e-6:
            _set_slot_active(pb, slot_idx, False, False)
            continue

        last_op = _state['opacities'].get(slot_idx)
        if last_op is None or abs(last_op - opacity) > 1e-5:
            lvl.par.opacity = opacity
            _state['opacities'][slot_idx] = opacity

        act_out1 = target_output in ('out1', 'both')
        act_out2 = target_output in ('out2', 'both')
        _set_slot_active(pb, slot_idx, act_out1, act_out2)

    # Clear active flag cleanly on scenes that just left the playhead
    for ct_path in (_state['active_scenes'] - new_active_scenes):
        ct = op(ct_path)
        if ct is not None and hasattr(ct.par, 'const0value'):
            ct.par.const0value.val = 0.0
            if hasattr(ct.par, 'const5value'):
                ct.par.const5value.val = 0.0
    _state['active_scenes'] = new_active_scenes

    # Update preview header text
    mlt = tl.parent()
    if mlt is not None:
        hdr = mlt.op('container_Preview/text_header')
        if hdr is not None:
            prev_mode = str(mlt.op('container_Preview').par.Previewmode.eval()) if hasattr(mlt.op('container_Preview').par, 'Previewmode') else 'out1'
            if prev_mode == 'out2':
                out_t = mlt.op('Timeline3D/out2')
                prefix = "OUTPUT 2 PREVIEW"
            elif prev_mode == 'split':
                out_t = mlt.op('container_Preview/layout_split')
                prefix = "DUAL OUTPUT PREVIEW (SPLIT)"
            else:
                out_t = mlt.op('Timeline3D/out1')
                prefix = "OUTPUT 1 PREVIEW"

            res_str = f'{out_t.width}x{out_t.height}' if out_t is not None else '1920x1080'
            if active_by_layer:
                active_names = []
                for lidx in sorted(active_by_layer.keys()):
                    c_op = active_by_layer[lidx][1]
                    c_title = str(c_op.par.Title.eval()) if hasattr(c_op.par, 'Title') else c_op.name
                    l_comp = layers_comp.op(f'base_Layer{lidx}') if layers_comp else None
                    l_out = str(l_comp.par.Output.eval()) if l_comp and hasattr(l_comp.par, 'Output') else 'out1'
                    active_names.append(f'{c_title} [L{lidx} → {l_out.upper()}]')
                label = f"{prefix}  •  {res_str}  •  LIVE: {', '.join(active_names)}"
            else:
                label = f"{prefix}  •  {res_str}  •  NEGRO (Sin Cue Activo)"
            if hdr.par.text.val != label:
                hdr.par.text = label
