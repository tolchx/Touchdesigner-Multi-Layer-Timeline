dur = op('/Multi_Layer_Timeline/container_Duration')
for c in [dur.op('btn_Settings'), dur.op('btn_PresetMenu')]:
    if c and hasattr(c.par, 'borderar'):
        c.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
        c.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
        c.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
        c.par.borderaalpha = 0.7
        c.par.leftborderi = 'bordera'
        c.par.rightborderi = 'bordera'
        c.par.bottomborderi = 'bordera'
        c.par.topborderi = 'bordera'
        c.par.borderover = True

print('Updated container_Duration borders cleanly')
