# Update container_InspectorHeader swatches with direct synchronous RGB + Colorpreset assignment
header = op('/Multi_Layer_Timeline/container_InspectorHeader')
swatches = header.op('comp_Swatches')

COLOR_MAP = {
    'DefaultBlue':    (0.0, 0.184, 0.395),
    'EmeraldGreen':   (0.05, 0.38, 0.18),
    'AmberGold':      (0.48, 0.30, 0.04),
    'VioletMagenta':  (0.34, 0.08, 0.44),
    'CrimsonRed':     (0.48, 0.06, 0.09),
    'CyanElectric':   (0.02, 0.35, 0.45),
    'DarkSlate':      (0.12, 0.12, 0.16),
}

for name, rgb in COLOR_MAP.items():
    sw = swatches.op(f'dot_{name}')
    if sw and sw.op('exec'):
        sw.op('exec').text = f'''def onOffToOn(panelValue):
    focus_op = op('/Multi_Layer_Timeline/UI/null_focuspath')
    if focus_op and focus_op.numRows > 0 and focus_op[0, 0].val:
        target = op(focus_op[0, 0].val)
        if target and hasattr(target.par, 'Colorpreset'):
            target.par.Colorpreset = "{name}"
            target.par.Backgroundcolorr = {rgb[0]}
            target.par.Backgroundcolorg = {rgb[1]}
            target.par.Backgroundcolorb = {rgb[2]}
            print("Set color of", target.name, "to {name} ({rgb[0]}, {rgb[1]}, {rgb[2]})")
'''

print('Swatches updated with synchronous Colorpreset and RGB assignment')
