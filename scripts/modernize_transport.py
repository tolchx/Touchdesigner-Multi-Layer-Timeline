# Modernize Transport Controls to ProSlate UI standard
ct = op('/Multi_Layer_Timeline/container_Transport')
if not ct:
    raise Exception('container_Transport not found')

# 1. Bind button state constants to ProSlate tokens
colors = op('/Multi_Layer_Timeline/UI/colors/out')

c1 = ct.op('constant1')
if c1:
    c1.par.colorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
    c1.par.colorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
    c1.par.colorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"

c2 = ct.op('constant2')
if c2:
    c2.par.colorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_offroll', 'r'].val"
    c2.par.colorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_offroll', 'g'].val"
    c2.par.colorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_offroll', 'b'].val"

c3 = ct.op('constant3')
if c3:
    c3.par.colorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'r'].val"
    c3.par.colorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'g'].val"
    c3.par.colorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'b'].val"

c4 = ct.op('constant4')
if c4:
    c4.par.colorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_onroll', 'r'].val"
    c4.par.colorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_onroll', 'g'].val"
    c4.par.colorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_onroll', 'b'].val"

# 2. Add or update btn_Loop
timer_op = op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')
btn_loop = ct.op('btn_Loop')
if btn_loop is None:
    btn_loop = ct.create(containerCOMP, 'btn_Loop')

btn_loop.nodeX = 500
btn_loop.nodeY = -400
btn_loop.par.w = 38
btn_loop.par.h = 32
btn_loop.par.alignorder = 6.5
btn_loop.par.marginr = 3.0
btn_loop.par.margint = 0.0
btn_loop.par.marginb = 0.0

# Dynamic color based on loop state
btn_loop.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'r'].val if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
btn_loop.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'g'].val if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
btn_loop.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'b'].val if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"
btn_loop.par.bgalpha = 0.9

btn_loop.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'r'].val if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
btn_loop.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'g'].val if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
btn_loop.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'b'].val if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
btn_loop.par.borderaalpha = 0.85
btn_loop.par.leftborderi = 'bordera'
btn_loop.par.rightborderi = 'bordera'
btn_loop.par.bottomborderi = 'bordera'
btn_loop.par.topborderi = 'bordera'
btn_loop.par.borderover = True

for c in list(btn_loop.children):
    c.destroy()

txt_loop = btn_loop.create(textCOMP, 'label')
txt_loop.nodeX = 0
txt_loop.nodeY = 0
txt_loop.par.w = 36
txt_loop.par.h = 30
txt_loop.par.font = 'Bahnschrift Condensed'
txt_loop.par.text = 'LOOP'
txt_loop.par.fontsize = 9
txt_loop.par.bold = True
txt_loop.par.fontcolorr.expr = "0.95 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else 0.70"
txt_loop.par.fontcolorg.expr = "0.98 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else 0.72"
txt_loop.par.fontcolorb.expr = "1.00 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.cycle.eval() else 0.75"
txt_loop.par.alignx = 'center'
txt_loop.par.aligny = 'center'
txt_loop.par.bgalpha = 0.0

pex_loop = btn_loop.create(panelexecuteDAT, 'exec')
pex_loop.nodeX = 150
pex_loop.nodeY = 0
pex_loop.par.panels = btn_loop.path
pex_loop.par.panelvalue = 'select'
pex_loop.par.offtoon = True
pex_loop.text = '''def onOffToOn(panelValue):
    t = op('/Multi_Layer_Timeline/Timeline3D/Time/timer1')
    if t:
        t.par.cycle = not t.par.cycle
        print("Timeline loop mode:", t.par.cycle.eval())
'''

# 3. Standardize button borders and styling across container_Transport
buttons_to_style = [
    ('btn_Home', 36, 0.0),
    ('btn_StepPrev', 38, 1.0),
    ('button1', 50, 2.0), # Stop
    ('button2', 50, 3.0), # Pause
    ('button3', 50, 4.0), # Play
    ('btn_StepNext', 38, 5.0),
    ('btn_PlaySub', 54, 6.0),
    ('btn_Loop', 38, 6.5),
    ('btn_Goto', 36, 7.0),
    ('btn_Split', 42, 8.0),
    ('btn_Marker1', 38, 8.5),
    ('btn_GO1', 52, 9.0),
]

for bname, width, aorder in buttons_to_style:
    b = ct.op(bname)
    if b:
        b.par.w = width
        b.par.alignorder = aorder
        b.par.marginr = 3.0
        if hasattr(b.par, 'borderar'):
            b.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
            b.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
            b.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
            b.par.borderaalpha = 0.7
            b.par.leftborderi = 'bordera'
            b.par.rightborderi = 'bordera'
            b.par.bottomborderi = 'bordera'
            b.par.topborderi = 'bordera'
            b.par.borderover = True

# Stylize btn_GO1 with accent glow
go = ct.op('btn_GO1')
if go:
    go.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_accent', 'r'].val"
    go.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_accent', 'g'].val"
    go.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_accent', 'b'].val"
    go.par.bgalpha = 0.95
    go.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'r'].val"
    go.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'g'].val"
    go.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'b'].val"
    go.par.borderaalpha = 1.0

# Stylize btn_Split with razor accent
split = ct.op('btn_Split')
if split:
    split.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
    split.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
    split.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"
    split.par.bgalpha = 0.9

# Telemetry HUD on far right
hud = ct.op('container_GPUStats')
if hud:
    hud.par.w = 118
    hud.par.alignorder = 10.0
    hud.par.marginl = 6.0
    hud.par.marginr = 6.0

print('Transport controls standardized and btn_Loop installed')
