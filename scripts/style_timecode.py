tc = op('/Multi_Layer_Timeline/container_Timecode')
for c in [tc.op('TimecodeReadout_Countdown'), tc.op('TimecodeReadout_Countdown1')]:
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

print('Styled TimecodeReadout containers')
