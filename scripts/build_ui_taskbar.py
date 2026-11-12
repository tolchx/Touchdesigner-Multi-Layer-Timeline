# Script to build ui_taskbar in /Multi_Layer_Timeline
mlt = op('/Multi_Layer_Timeline')
if not mlt:
    raise Exception('Multi_Layer_Timeline not found')

# 1. Adjust top anchors of preview and parameter1
prev = mlt.op('container_Preview')
if prev:
    prev.par.topanchor = 0.955

param = mlt.op('parameter1')
if param:
    param.par.topanchor = 0.915

# 2. Create ui_taskbar
taskbar = mlt.op('ui_taskbar')
if taskbar is None:
    taskbar = mlt.create(containerCOMP, 'ui_taskbar')

taskbar.nodeX = -200
taskbar.nodeY = 1400

# Positioning & Anchors
taskbar.par.leftanchor = 0.008
taskbar.par.rightanchor = 0.992
taskbar.par.bottomanchor = 0.962
taskbar.par.topanchor = 0.995
taskbar.par.align = 'horizlr'
taskbar.par.alignorder = 0.0
taskbar.par.marginl = 0.0
taskbar.par.marginr = 0.0
taskbar.par.marginb = 0.0
taskbar.par.margint = 0.0

# Styling
taskbar.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'r'].val"
taskbar.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'g'].val"
taskbar.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'b'].val"
taskbar.par.bgalpha = 1.0

# 1px border
taskbar.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
taskbar.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
taskbar.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
taskbar.par.borderaalpha = 0.8
taskbar.par.leftborderi = 'bordera'
taskbar.par.rightborderi = 'bordera'
taskbar.par.bottomborderi = 'bordera'
taskbar.par.topborderi = 'bordera'
taskbar.par.borderover = True

print('ui_taskbar created and styled')
