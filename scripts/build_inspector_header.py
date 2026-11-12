# Script to build container_InspectorHeader in /Multi_Layer_Timeline
mlt = op('/Multi_Layer_Timeline')
if not mlt:
    raise Exception('Multi_Layer_Timeline not found')

header = mlt.op('container_InspectorHeader')
if header is None:
    header = mlt.create(containerCOMP, 'container_InspectorHeader')

header.nodeX = 1400
header.nodeY = 1400

# Positioning & Anchors
header.par.leftanchor = 0.742
header.par.rightanchor = 0.992
header.par.bottomanchor = 0.920
header.par.topanchor = 0.955
header.par.align = 'horizlr'
header.par.alignorder = 0.0
header.par.marginl = 0.0
header.par.marginr = 0.0
header.par.marginb = 0.0
header.par.margint = 0.0

# Styling
header.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'r'].val"
header.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'g'].val"
header.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'b'].val"
header.par.bgalpha = 1.0

# 1px border
header.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
header.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
header.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
header.par.borderaalpha = 0.8
header.par.leftborderi = 'bordera'
header.par.rightborderi = 'bordera'
header.par.bottomborderi = 'bordera'
header.par.topborderi = 'bordera'
header.par.borderover = True

# Clean children
for c in list(header.children):
    c.destroy()

font_family = 'Bahnschrift Condensed'

# 1. Target Label
txt_target = header.create(textCOMP, 'text_Target')
txt_target.nodeX = 0
txt_target.nodeY = 0
txt_target.par.w = 160
txt_target.par.h = 28
txt_target.par.marginl = 8.0
txt_target.par.font = font_family
txt_target.par.text.expr = "f'INSPECT: {op(\"/Multi_Layer_Timeline/UI/null_focuspath\")[0, 0].val.split(\"/\")[-1] if op(\"/Multi_Layer_Timeline/UI/null_focuspath\").numRows > 0 and op(\"/Multi_Layer_Timeline/UI/null_focuspath\")[0, 0].val else \"TIMELINE\"}'"
txt_target.par.fontsize = 10
txt_target.par.bold = True
txt_target.par.fontcolorr = 0.88
txt_target.par.fontcolorg = 0.90
txt_target.par.fontcolorb = 0.94
txt_target.par.alignx = 'left'
txt_target.par.aligny = 'center'
txt_target.par.bgalpha = 0.0

# 2. Color Swatches Strip
swatches = header.create(containerCOMP, 'comp_Swatches')
swatches.nodeX = 250
swatches.nodeY = 0
swatches.par.w = 150
swatches.par.h = 28
swatches.par.align = 'horizlr'
swatches.par.marginl = 4.0
swatches.par.bgalpha = 0.0

color_presets = [
    ('DefaultBlue',    (0.18, 0.38, 0.62)),
    ('EmeraldGreen',   (0.12, 0.52, 0.32)),
    ('AmberGold',      (0.78, 0.56, 0.12)),
    ('VioletMagenta',  (0.52, 0.18, 0.58)),
    ('CrimsonRed',     (0.68, 0.14, 0.14)),
    ('CyanElectric',   (0.08, 0.65, 0.72)),
    ('DarkSlate',      (0.24, 0.28, 0.32)),
]

for idx, (preset_name, rgb) in enumerate(color_presets):
    sw = swatches.create(containerCOMP, f'dot_{preset_name}')
    sw.nodeX = idx * 100
    sw.nodeY = 0
    sw.par.w = 16
    sw.par.h = 16
    sw.par.marginb = 6.0
    sw.par.margint = 6.0
    sw.par.marginr = 4.0
    sw.par.bgcolorr = rgb[0]
    sw.par.bgcolorg = rgb[1]
    sw.par.bgcolorb = rgb[2]
    sw.par.bgalpha = 1.0
    sw.par.borderar = 0.7
    sw.par.borderag = 0.7
    sw.par.borderab = 0.7
    sw.par.borderaalpha = 0.6
    sw.par.leftborderi = 'bordera'
    sw.par.rightborderi = 'bordera'
    sw.par.bottomborderi = 'bordera'
    sw.par.topborderi = 'bordera'
    sw.par.borderover = True

    pex = sw.create(panelexecuteDAT, 'exec')
    pex.nodeX = 100
    pex.nodeY = 0
    pex.par.panels = sw.path
    pex.par.panelvalue = 'select'
    pex.par.offtoon = True
    pex.text = f'''def onOffToOn(panelValue):
    focus_op = op('/Multi_Layer_Timeline/UI/null_focuspath')
    if focus_op and focus_op.numRows > 0 and focus_op[0, 0].val:
        target = op(focus_op[0, 0].val)
        if target and hasattr(target.par, 'Colorpreset'):
            target.par.Colorpreset = "{preset_name}"
            print("Set color preset of", target.name, "to {preset_name}")
'''

# 3. Quick Action Buttons: DUP, CUT, DEL
actions = header.create(containerCOMP, 'comp_QuickTools')
actions.nodeX = 450
actions.nodeY = 0
actions.par.w = 140
actions.par.h = 28
actions.par.align = 'horizlr'
actions.par.marginl = 6.0
actions.par.bgalpha = 0.0

def create_quick_tool(name, label, code):
    btn = actions.create(containerCOMP, name)
    btn.nodeX = 0
    btn.nodeY = 0
    btn.par.w = 42
    btn.par.h = 20
    btn.par.marginb = 4.0
    btn.par.margint = 4.0
    btn.par.marginr = 4.0
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
    txt.par.w = 40
    txt.par.h = 18
    txt.par.font = font_family
    txt.par.text = label
    txt.par.fontsize = 8
    txt.par.bold = True
    txt.par.fontcolorr = 0.80
    txt.par.fontcolorg = 0.82
    txt.par.fontcolorb = 0.86
    txt.par.alignx = 'center'
    txt.par.aligny = 'center'
    txt.par.bgalpha = 0.0

    pex = btn.create(panelexecuteDAT, 'exec')
    pex.nodeX = 100
    pex.nodeY = 0
    pex.par.panels = btn.path
    pex.par.panelvalue = 'select'
    pex.par.offtoon = True
    pex.text = f'''def onOffToOn(panelValue):
{code}
'''
    return btn

create_quick_tool('btn_Dup', 'DUP', '''    proj = op('/Multi_Layer_Timeline/Timeline3D/Project')
    if proj and hasattr(proj.ext, 'Manager'):
        proj.ext.Manager.DuplicateSelectedCues()''')

create_quick_tool('btn_Cut', 'CUT', '''    proj = op('/Multi_Layer_Timeline/Timeline3D/Project')
    if proj and hasattr(proj.ext, 'Manager'):
        proj.ext.Manager.SplitCueAtPlayhead()''')

create_quick_tool('btn_Del', 'DEL', '''    focus_op = op('/Multi_Layer_Timeline/UI/null_focuspath')
    if focus_op and focus_op.numRows > 0 and focus_op[0, 0].val:
        target = op(focus_op[0, 0].val)
        if target and target.name.startswith('cue_') and target.parent.name == 'Cues':
            target.destroy()
            op('/Multi_Layer_Timeline/UI/table_focuspath')[0, 0] = '/Multi_Layer_Timeline'
            print('Deleted cue:', target.path)''')

print('container_InspectorHeader created and wired successfully')
