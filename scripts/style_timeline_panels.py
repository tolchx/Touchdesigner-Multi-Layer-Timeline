# Script to style LayerSettings, Timeline3D, and container_RangeSlider
mlt = op('/Multi_Layer_Timeline')

panels_to_border = [
    mlt.op('LayerSettings'),
    mlt.op('Timeline3D'),
    mlt.op('container_RangeSlider'),
    mlt.op('parameter1'),
]

for p in panels_to_border:
    if p and hasattr(p.par, 'borderar'):
        p.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
        p.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
        p.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
        p.par.borderaalpha = 0.8
        p.par.leftborderi = 'bordera'
        p.par.rightborderi = 'bordera'
        p.par.bottomborderi = 'bordera'
        p.par.topborderi = 'bordera'
        p.par.borderover = True

# Also ensure Timeline3D canvas background uses panel_base
tl_render = mlt.op('Timeline3D/Render/render1')
if tl_render:
    tl_render.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'r'].val"
    tl_render.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'g'].val"
    tl_render.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'b'].val"
    tl_render.par.bgcolora = 1.0

# LayerSettings render background uses panel_header
ls_render = mlt.op('Timeline3D/Render/render_LayerSettings')
if ls_render:
    ls_render.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'r'].val"
    ls_render.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'g'].val"
    ls_render.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'b'].val"
    ls_render.par.bgcolora = 1.0

print('Timeline panels styled with ProSlate tokens and 1px outlines')
