# Full UI Modernization & Overhaul for v2.0
mlt = op('/Multi_Layer_Timeline')
if not mlt:
    raise Exception('Multi_Layer_Timeline not found')

colors = op('/Multi_Layer_Timeline/UI/colors/out')

# =========================================================================
# 1. WINDOW RESOLUTION & PERFORMANCE FULLSCREEN FIX
# =========================================================================
win = op('/perform')
if win:
    win.par.size = 'fill'
    print("Set /perform size to 'fill'")

# =========================================================================
# 2. TRANSPORT BUTTONS: COMPLETE OVERHAUL & GLYPH RESTORATION
# =========================================================================
ct = op('/Multi_Layer_Timeline/container_Transport')
if ct:
    ct.par.align = 'horizlr'
    ct.par.justifyv = 'center'
    ct.par.marginl = 6.0
    ct.par.marginr = 6.0
    ct.par.marginb = 0.0
    ct.par.margint = 0.0

    # Ensure background uses panel_header
    ct.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'r'].val"
    ct.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'g'].val"
    ct.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'b'].val"
    ct.par.bgalpha = 1.0

    # 1px border
    ct.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    ct.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    ct.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    ct.par.borderaalpha = 0.8
    ct.par.leftborderi = 'bordera'
    ct.par.rightborderi = 'bordera'
    ct.par.bottomborderi = 'bordera'
    ct.par.topborderi = 'bordera'
    ct.par.borderover = True

    # Complete list of transport buttons with widths, orders, and glyphs
    btn_configs = [
        ('btn_Home',     34, 0.0, '|◀',   'Home / Rewind (0s)'),
        ('btn_StepPrev', 36, 1.0, '◀',    'Step -1 Frame'),
        ('button1',      44, 2.0, '⏹',    'Stop'),
        ('button2',      44, 3.0, '⏸',    'Pause'),
        ('button3',      44, 4.0, '▶',    'Play'),
        ('btn_StepNext', 36, 5.0, '▶',    'Step +1 Frame'),
        ('btn_PlaySub',  44, 6.0, '▶▶',   'Fast Forward'),
        ('btn_Loop',     46, 6.5, '🔁 LOOP', 'Loop Mode Toggle'),
        ('btn_Goto',     42, 7.0, '⌖ GOTO', 'Goto Timecode'),
        ('btn_Split',    46, 8.0, '✂ CUT', 'Split Cue at Playhead'),
        ('btn_Marker1',  38, 8.5, '+M',    'Add Marker'),
        ('btn_GO1',      52, 9.0, 'GO ▶', 'Trigger Cue (GO)'),
    ]

    for bname, width, aorder, glyph, tip in btn_configs:
        b = ct.op(bname)
        if b:
            b.par.w = width
            b.par.h = 28
            b.par.alignorder = aorder
            b.par.marginr = 4.0
            b.par.marginb = 0.0
            b.par.margint = 0.0

            # 1px border
            if hasattr(b.par, 'borderar'):
                b.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
                b.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
                b.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
                b.par.borderaalpha = 0.8
                b.par.leftborderi = 'bordera'
                b.par.rightborderi = 'bordera'
                b.par.bottomborderi = 'bordera'
                b.par.topborderi = 'bordera'
                b.par.borderover = True

            # If button is container with text TOP
            t_op = b.op('text')
            if t_op and t_op.isTOP:
                t_op.par.text = glyph
                t_op.par.font = 'Bahnschrift Condensed'
                t_op.par.bold = True
                t_op.par.fontsizex = 10.0
                t_op.par.alignx = 'center'
                t_op.par.aligny = 'center'
                t_op.par.fontcolorr = 0.88
                t_op.par.fontcolorg = 0.90
                t_op.par.fontcolorb = 0.94
                t_op.par.outputresolution = 'custom'
                t_op.par.resolutionw.expr = 'parent().width'
                t_op.par.resolutionh.expr = 'parent().height'
                b.par.top = t_op
            elif hasattr(b.par, 'label'):
                b.par.label = glyph

    # Accent on GO
    go = ct.op('btn_GO1')
    if go:
        go.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_accent', 'r'].val"
        go.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_accent', 'g'].val"
        go.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_accent', 'b'].val"
        go.par.bgalpha = 1.0

    # Accent on Loop
    loop = ct.op('btn_Loop')
    if loop:
        loop.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'r'].val if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
        loop.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'g'].val if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
        loop.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'b'].val if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"

    # Telemetry HUD
    hud = ct.op('container_GPUStats')
    if hud:
        hud.par.w = 115
        hud.par.h = 28
        hud.par.alignorder = 10.0
        hud.par.marginl = 10.0
        hud.par.marginr = 6.0

print('Transport buttons fully overhauled with vector glyphs and 1px borders')

# =========================================================================
# 3. MODERN TIMECODE CARDS (ELAPSED & REMAINING)
# =========================================================================
tc = op('/Multi_Layer_Timeline/container_Timecode')
if tc:
    tc.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'r'].val"
    tc.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'g'].val"
    tc.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'b'].val"
    tc.par.bgalpha = 1.0
    tc.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    tc.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    tc.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    tc.par.borderaalpha = 0.8
    tc.par.leftborderi = 'bordera'
    tc.par.rightborderi = 'bordera'
    tc.par.bottomborderi = 'bordera'
    tc.par.topborderi = 'bordera'
    tc.par.borderover = True

    # Hide old GLSL readouts that were squashed and floating
    old_c1 = tc.op('TimecodeReadout_Countdown')
    old_c2 = tc.op('TimecodeReadout_Countdown1')
    if old_c1: old_c1.par.display = False
    if old_c2: old_c2.par.display = False

    # Create Left Card: ELAPSED
    card_el = tc.op('card_Elapsed')
    if card_el is None:
        card_el = tc.create(containerCOMP, 'card_Elapsed')
    card_el.nodeX = 0
    card_el.nodeY = 0
    card_el.par.leftanchor = 0.03
    card_el.par.rightanchor = 0.48
    card_el.par.bottomanchor = 0.10
    card_el.par.topanchor = 0.90
    card_el.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'r'].val"
    card_el.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'g'].val"
    card_el.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'b'].val"
    card_el.par.bgalpha = 0.95
    card_el.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    card_el.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    card_el.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    card_el.par.borderaalpha = 0.7
    card_el.par.leftborderi = 'bordera'
    card_el.par.rightborderi = 'bordera'
    card_el.par.bottomborderi = 'bordera'
    card_el.par.topborderi = 'bordera'
    card_el.par.borderover = True

    # Sub-label: ELAPSED
    sub_el = card_el.op('lbl_sub')
    if sub_el is None: sub_el = card_el.create(textCOMP, 'lbl_sub')
    sub_el.par.leftanchor = 0.0
    sub_el.par.rightanchor = 1.0
    sub_el.par.bottomanchor = 0.60
    sub_el.par.topanchor = 0.98
    sub_el.par.font = 'Bahnschrift Condensed'
    sub_el.par.text = 'ELAPSED PLAYHEAD'
    sub_el.par.fontsize = 8
    sub_el.par.fontcolorr = 0.45
    sub_el.par.fontcolorg = 0.48
    sub_el.par.fontcolorb = 0.52
    sub_el.par.alignx = 'center'
    sub_el.par.aligny = 'center'
    sub_el.par.bgalpha = 0.0

    # Digits: ELAPSED
    val_el = card_el.op('txt_digits')
    if val_el is None: val_el = card_el.create(textCOMP, 'txt_digits')
    val_el.par.leftanchor = 0.0
    val_el.par.rightanchor = 1.0
    val_el.par.bottomanchor = 0.05
    val_el.par.topanchor = 0.65
    val_el.par.font = 'Bahnschrift Condensed'
    val_el.par.bold = True
    val_el.par.fontsize = 15
    val_el.par.text.expr = "f\"{int(op('null_Countup')['Hour']):02d}:{int(op('null_Countup')['Minute']):02d}:{int(op('null_Countup')['Seconds']):02d}:{int(op('null_Countup')['Frames']):02d}\""
    val_el.par.fontcolorr = 0.88
    val_el.par.fontcolorg = 0.96
    val_el.par.fontcolorb = 1.00
    val_el.par.alignx = 'center'
    val_el.par.aligny = 'center'
    val_el.par.bgalpha = 0.0

    # Create Right Card: REMAINING
    card_rem = tc.op('card_Remaining')
    if card_rem is None:
        card_rem = tc.create(containerCOMP, 'card_Remaining')
    card_rem.nodeX = 300
    card_rem.nodeY = 0
    card_rem.par.leftanchor = 0.52
    card_rem.par.rightanchor = 0.97
    card_rem.par.bottomanchor = 0.10
    card_rem.par.topanchor = 0.90
    card_rem.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'r'].val"
    card_rem.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'g'].val"
    card_rem.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'b'].val"
    card_rem.par.bgalpha = 0.95
    card_rem.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    card_rem.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    card_rem.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    card_rem.par.borderaalpha = 0.7
    card_rem.par.leftborderi = 'bordera'
    card_rem.par.rightborderi = 'bordera'
    card_rem.par.bottomborderi = 'bordera'
    card_rem.par.topborderi = 'bordera'
    card_rem.par.borderover = True

    # Sub-label: REMAINING
    sub_rem = card_rem.op('lbl_sub')
    if sub_rem is None: sub_rem = card_rem.create(textCOMP, 'lbl_sub')
    sub_rem.par.leftanchor = 0.0
    sub_rem.par.rightanchor = 1.0
    sub_rem.par.bottomanchor = 0.60
    sub_rem.par.topanchor = 0.98
    sub_rem.par.font = 'Bahnschrift Condensed'
    sub_rem.par.text = 'REMAINING TIME'
    sub_rem.par.fontsize = 8
    sub_rem.par.fontcolorr = 0.45
    sub_rem.par.fontcolorg = 0.48
    sub_rem.par.fontcolorb = 0.52
    sub_rem.par.alignx = 'center'
    sub_rem.par.aligny = 'center'
    sub_rem.par.bgalpha = 0.0

    # Digits: REMAINING
    val_rem = card_rem.op('txt_digits')
    if val_rem is None: val_rem = card_rem.create(textCOMP, 'txt_digits')
    val_rem.par.leftanchor = 0.0
    val_rem.par.rightanchor = 1.0
    val_rem.par.bottomanchor = 0.05
    val_rem.par.topanchor = 0.65
    val_rem.par.font = 'Bahnschrift Condensed'
    val_rem.par.bold = True
    val_rem.par.fontsize = 15
    val_rem.par.text.expr = "f\"{int(op('null_Countdown')['Hour']):02d}:{int(op('null_Countdown')['Minute']):02d}:{int(op('null_Countdown')['Seconds']):02d}:{int(op('null_Countdown')['Frames']):02d}\""
    val_rem.par.fontcolorr = 0.95
    val_rem.par.fontcolorg = 0.82
    val_rem.par.fontcolorb = 0.45
    val_rem.par.alignx = 'center'
    val_rem.par.aligny = 'center'
    val_rem.par.bgalpha = 0.0

print('Timecode displays modernized with high-density digital cards')

# =========================================================================
# 4. PARAMETER INSPECTOR & INSPECTOR HEADER MODERNIZATION
# =========================================================================
param = mlt.op('parameter1')
if param:
    param.par.header = False      # Completely remove ugly Base base_Cue2 ? i + @ bar
    param.par.pagenames = False   # Remove ugly generic grey Settings tab
    param.par.separators = False  # Compact sleek layout
    param.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'r'].val"
    param.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'g'].val"
    param.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'b'].val"
    param.par.bgalpha = 1.0
    param.par.bottomanchor = 0.533
    param.par.topanchor = 0.920

header = mlt.op('container_InspectorHeader')
if header:
    header.par.bottomanchor = 0.920
    header.par.topanchor = 0.955
    header.par.leftanchor = 0.742
    header.par.rightanchor = 0.992

# =========================================================================
# 5. LAYER TRACK HEADERS: HIGH-DENSITY DAW CHANNEL STRIPS
# =========================================================================
layers = mlt.op('Timeline3D/Layers')
if layers:
    for idx in range(5):
        l_comp = layers.op(f'base_Layer{idx}')
        if l_comp:
            # Card background
            c_bg = l_comp.op('constant1')
            if c_bg:
                c_bg.par.colorr = 0.045
                c_bg.par.colorg = 0.048
                c_bg.par.colorb = 0.055

            # Text node
            t_node = l_comp.op('text1')
            if t_node:
                t_node.par.font = 'Bahnschrift Condensed'
                t_node.par.bold = True
                t_node.par.fontsizex = 12.0
                t_node.par.fontcolorr = 0.85
                t_node.par.fontcolorg = 0.88
                t_node.par.fontcolorb = 0.92
                t_node.par.alignx = 'left'
                t_node.par.positionx = 0.05

print('All 5 UI regions fully modernized to ProSlate Standard!')
