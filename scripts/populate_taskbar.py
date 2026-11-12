# Script to populate ui_taskbar with ProSlate widgets
taskbar = op('/Multi_Layer_Timeline/ui_taskbar')
if not taskbar:
    raise Exception('ui_taskbar not found')

# Clean existing children
for c in list(taskbar.children):
    c.destroy()

# Common styles
font_family = 'Bahnschrift Condensed'

# --- 1. LOGO & BRAND BADGE ---
logo = taskbar.create(containerCOMP, 'comp_Logo')
logo.nodeX = 0
logo.nodeY = 0
logo.par.w = 175
logo.par.h = 30
logo.par.align = 'horizlr'
logo.par.alignorder = 0.0
logo.par.marginl = 6.0
logo.par.marginr = 6.0
logo.par.marginb = 0.0
logo.par.margint = 0.0
logo.par.bgalpha = 0.0

txt_logo = logo.create(textCOMP, 'text_logo')
txt_logo.nodeX = 0
txt_logo.nodeY = 0
txt_logo.par.w = 95
txt_logo.par.h = 28
txt_logo.par.font = font_family
txt_logo.par.text = 'TD-MTL v2.0'
txt_logo.par.fontsize = 12
txt_logo.par.bold = True
txt_logo.par.fontcolorr = 0.95
txt_logo.par.fontcolorg = 0.96
txt_logo.par.fontcolorb = 0.98
txt_logo.par.alignx = 'left'
txt_logo.par.aligny = 'center'
txt_logo.par.bgalpha = 0.0

pill_badge = logo.create(containerCOMP, 'pill_engine')
pill_badge.nodeX = 150
pill_badge.nodeY = 0
pill_badge.par.w = 68
pill_badge.par.h = 18
pill_badge.par.marginb = 5.0
pill_badge.par.margint = 5.0
pill_badge.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'r'].val"
pill_badge.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'g'].val"
pill_badge.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'b'].val"
pill_badge.par.bgalpha = 0.8
pill_badge.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'r'].val"
pill_badge.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'g'].val"
pill_badge.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'b'].val"
pill_badge.par.borderaalpha = 0.8
pill_badge.par.leftborderi = 'bordera'
pill_badge.par.rightborderi = 'bordera'
pill_badge.par.bottomborderi = 'bordera'
pill_badge.par.topborderi = 'bordera'
pill_badge.par.borderover = True

txt_pill = pill_badge.create(textCOMP, 'text_badge')
txt_pill.nodeX = 0
txt_pill.nodeY = 0
txt_pill.par.w = 66
txt_pill.par.h = 16
txt_pill.par.font = font_family
txt_pill.par.text = 'PROSLATE'
txt_pill.par.fontsize = 8
txt_pill.par.bold = True
txt_pill.par.fontcolorr = 0.85
txt_pill.par.fontcolorg = 0.98
txt_pill.par.fontcolorb = 1.0
txt_pill.par.alignx = 'center'
txt_pill.par.aligny = 'center'
txt_pill.par.bgalpha = 0.0

# --- 2. LIVE ENGINE STATUS BADGE ---
status_comp = taskbar.create(containerCOMP, 'comp_Status')
status_comp.nodeX = 350
status_comp.nodeY = 0
status_comp.par.w = 120
status_comp.par.h = 30
status_comp.par.align = 'horizlr'
status_comp.par.alignorder = 1.0
status_comp.par.marginl = 10.0
status_comp.par.marginr = 10.0
status_comp.par.marginb = 0.0
status_comp.par.margint = 0.0
status_comp.par.bgalpha = 0.0

led = status_comp.create(containerCOMP, 'led_dot')
led.nodeX = 0
led.nodeY = 0
led.par.w = 10
led.par.h = 10
led.par.marginb = 9.0
led.par.margint = 9.0
led.par.bgcolorr.expr = "0.15 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['running'].eval() > 0.5 else (0.95 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['cue'].eval() > 0.5 else 0.45)"
led.par.bgcolorg.expr = "0.95 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['running'].eval() > 0.5 else (0.65 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['cue'].eval() > 0.5 else 0.48)"
led.par.bgcolorb.expr = "0.35 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['running'].eval() > 0.5 else (0.15 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['cue'].eval() > 0.5 else 0.52)"
led.par.bgalpha = 1.0

txt_status = status_comp.create(textCOMP, 'text_status')
txt_status.nodeX = 150
txt_status.nodeY = 0
txt_status.par.w = 95
txt_status.par.h = 28
txt_status.par.font = font_family
txt_status.par.text.expr = "'PLAYING' if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['running'].eval() > 0.5 else ('PAUSED' if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['play'].eval() == 0 and op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['timer_seconds'].eval() > 0.05 else 'STOPPED')"
txt_status.par.fontsize = 10
txt_status.par.bold = True
txt_status.par.fontcolorr.expr = "0.25 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['running'].eval() > 0.5 else 0.7"
txt_status.par.fontcolorg.expr = "0.95 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['running'].eval() > 0.5 else 0.72"
txt_status.par.fontcolorb.expr = "0.45 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')['running'].eval() > 0.5 else 0.75"
txt_status.par.alignx = 'left'
txt_status.par.aligny = 'center'
txt_status.par.bgalpha = 0.0

# --- 3. QUICK VIEW LAYOUT PRESETS ---
layouts_comp = taskbar.create(containerCOMP, 'comp_Layouts')
layouts_comp.nodeX = 700
layouts_comp.nodeY = 0
layouts_comp.par.w = 270
layouts_comp.par.h = 30
layouts_comp.par.align = 'horizlr'
layouts_comp.par.alignorder = 2.0
layouts_comp.par.marginl = 20.0
layouts_comp.par.marginr = 20.0
layouts_comp.par.marginb = 0.0
layouts_comp.par.margint = 0.0
layouts_comp.par.bgalpha = 0.0

def create_layout_btn(name, label, align_order, layout_mode):
    btn = layouts_comp.create(containerCOMP, name)
    btn.nodeX = align_order * 150
    btn.nodeY = 0
    btn.par.w = 82
    btn.par.h = 22
    btn.par.marginb = 3.0
    btn.par.margint = 3.0
    btn.par.marginr = 4.0
    btn.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
    btn.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
    btn.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"
    btn.par.bgalpha = 0.8
    btn.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    btn.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    btn.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    btn.par.borderaalpha = 0.7
    btn.par.leftborderi = 'bordera'
    btn.par.rightborderi = 'bordera'
    btn.par.bottomborderi = 'bordera'
    btn.par.topborderi = 'bordera'
    btn.par.borderover = True

    txt = btn.create(textCOMP, 'label')
    txt.nodeX = 0
    txt.nodeY = 0
    txt.par.w = 80
    txt.par.h = 20
    txt.par.font = font_family
    txt.par.text = label
    txt.par.fontsize = 9
    txt.par.fontcolorr = 0.75
    txt.par.fontcolorg = 0.78
    txt.par.fontcolorb = 0.82
    txt.par.alignx = 'center'
    txt.par.aligny = 'center'
    txt.par.bgalpha = 0.0

    pex = btn.create(panelexecuteDAT, 'exec')
    pex.nodeX = 150
    pex.nodeY = 0
    pex.par.panels = btn.path
    pex.par.panelvalue = 'select'
    pex.par.offtoon = True
    pex.text = f'''def onOffToOn(panelValue):
    mlt = op('/Multi_Layer_Timeline')
    mode = "{layout_mode}"
    if mode == "standard":
        mlt.op('container_Preview').par.bottomanchor = 0.608
        mlt.op('container_Preview').par.topanchor = 0.955
        mlt.op('parameter1').par.bottomanchor = 0.533
        mlt.op('parameter1').par.topanchor = 0.915
        mlt.op('Timeline3D').par.bottomanchor = 0.055
        mlt.op('Timeline3D').par.topanchor = 0.421
        mlt.op('LayerSettings').par.bottomanchor = 0.055
        mlt.op('LayerSettings').par.topanchor = 0.421
    elif mode == "timeline":
        mlt.op('container_Preview').par.bottomanchor = 0.780
        mlt.op('container_Preview').par.topanchor = 0.955
        mlt.op('parameter1').par.bottomanchor = 0.620
        mlt.op('parameter1').par.topanchor = 0.915
        mlt.op('Timeline3D').par.bottomanchor = 0.055
        mlt.op('Timeline3D').par.topanchor = 0.520
        mlt.op('LayerSettings').par.bottomanchor = 0.055
        mlt.op('LayerSettings').par.topanchor = 0.520
    elif mode == "preview":
        mlt.op('container_Preview').par.bottomanchor = 0.450
        mlt.op('container_Preview').par.topanchor = 0.955
        mlt.op('parameter1').par.bottomanchor = 0.450
        mlt.op('parameter1').par.topanchor = 0.915
        mlt.op('Timeline3D').par.bottomanchor = 0.055
        mlt.op('Timeline3D').par.topanchor = 0.280
        mlt.op('LayerSettings').par.bottomanchor = 0.055
        mlt.op('LayerSettings').par.topanchor = 0.280
'''
    return btn

create_layout_btn('btn_Std', 'STANDARD', 0, 'standard')
create_layout_btn('btn_TL', 'TIMELINE FOCUS', 1, 'timeline')
create_layout_btn('btn_Prev', 'PREVIEW FOCUS', 2, 'preview')

# --- 4. SESSION INFO READOUT ---
info_comp = taskbar.create(textCOMP, 'text_Session')
info_comp.nodeX = 1050
info_comp.nodeY = 0
info_comp.par.w = 260
info_comp.par.h = 28
info_comp.par.font = font_family
info_comp.par.alignorder = 3.0
info_comp.par.marginl = 20.0
info_comp.par.text.expr = "f'{project.name}  \u2022  1920x1080  \u2022  60 FPS  \u2022  {op(\"/Multi_Layer_Timeline\").par.Duration.eval():0.0f}s'"
info_comp.par.fontsize = 10
info_comp.par.fontcolorr = 0.45
info_comp.par.fontcolorg = 0.48
info_comp.par.fontcolorb = 0.52
info_comp.par.alignx = 'left'
info_comp.par.aligny = 'center'
info_comp.par.bgalpha = 0.0

# --- 5. ACTION BUTTONS: SAVE & FULLSCREEN ---
actions_comp = taskbar.create(containerCOMP, 'comp_Actions')
actions_comp.nodeX = 1350
actions_comp.nodeY = 0
actions_comp.par.w = 200
actions_comp.par.h = 30
actions_comp.par.align = 'horizlr'
actions_comp.par.alignorder = 4.0
actions_comp.par.marginl = 40.0
actions_comp.par.bgalpha = 0.0

def create_action_btn(name, label, code):
    btn = actions_comp.create(containerCOMP, name)
    btn.nodeX = 0
    btn.nodeY = 0
    btn.par.w = 90
    btn.par.h = 22
    btn.par.marginb = 3.0
    btn.par.margint = 3.0
    btn.par.marginr = 6.0
    btn.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
    btn.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
    btn.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"
    btn.par.bgalpha = 0.85
    btn.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    btn.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    btn.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    btn.par.borderaalpha = 0.8
    btn.par.leftborderi = 'bordera'
    btn.par.rightborderi = 'bordera'
    btn.par.bottomborderi = 'bordera'
    btn.par.topborderi = 'bordera'
    btn.par.borderover = True

    txt = btn.create(textCOMP, 'label')
    txt.nodeX = 0
    txt.nodeY = 0
    txt.par.w = 88
    txt.par.h = 20
    txt.par.font = font_family
    txt.par.text = label
    txt.par.fontsize = 9
    txt.par.fontcolorr = 0.85
    txt.par.fontcolorg = 0.88
    txt.par.fontcolorb = 0.92
    txt.par.alignx = 'center'
    txt.par.aligny = 'center'
    txt.par.bgalpha = 0.0

    pex = btn.create(panelexecuteDAT, 'exec')
    pex.nodeX = 150
    pex.nodeY = 0
    pex.par.panels = btn.path
    pex.par.panelvalue = 'select'
    pex.par.offtoon = True
    pex.text = f'''def onOffToOn(panelValue):
{code}
'''
    return btn

create_action_btn('btn_Save', '💾 SAVE (v2)', "    project.save()\n    print('Saved project as', project.name)")
create_action_btn('btn_FS', '⛶ FULLSCREEN', "    ui.performMode = not ui.performMode\n    print('Toggled performMode:', ui.performMode)")

print('ui_taskbar successfully populated with all widgets')
