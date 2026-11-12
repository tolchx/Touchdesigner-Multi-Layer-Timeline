# Script to style container_AudioHeader with ProSlate tokens
ah = op('/Multi_Layer_Timeline/container_AudioHeader')
tr = op('/Multi_Layer_Timeline/container_AudioTrack')
if not ah:
    raise Exception('container_AudioHeader not found')

# 1. Background and border of container_AudioHeader
ah.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'r'].val"
ah.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'g'].val"
ah.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'b'].val"
ah.par.bgalpha = 1.0

ah.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
ah.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
ah.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
ah.par.borderaalpha = 0.8
ah.par.leftborderi = 'bordera'
ah.par.rightborderi = 'bordera'
ah.par.bottomborderi = 'bordera'
ah.par.topborderi = 'bordera'
ah.par.borderover = True

# 2. Dynamic Mute button
mute = ah.op('btn_Mute')
if mute:
    mute.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['warning_red', 'r'].val if op('/Multi_Layer_Timeline/container_AudioTrack').par.Mute.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
    mute.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['warning_red', 'g'].val if op('/Multi_Layer_Timeline/container_AudioTrack').par.Mute.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
    mute.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['warning_red', 'b'].val if op('/Multi_Layer_Timeline/container_AudioTrack').par.Mute.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"
    mute.par.bgalpha = 0.95
    mute.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    mute.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    mute.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    mute.par.borderaalpha = 0.8
    mute.par.leftborderi = 'bordera'
    mute.par.rightborderi = 'bordera'
    mute.par.bottomborderi = 'bordera'
    mute.par.topborderi = 'bordera'
    mute.par.borderover = True

# 3. Dynamic Solo button
solo = ah.op('btn_Solo')
if solo:
    solo.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['solo_gold', 'r'].val if op('/Multi_Layer_Timeline/container_AudioTrack').par.Solo.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
    solo.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['solo_gold', 'g'].val if op('/Multi_Layer_Timeline/container_AudioTrack').par.Solo.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
    solo.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['solo_gold', 'b'].val if op('/Multi_Layer_Timeline/container_AudioTrack').par.Solo.eval() else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"
    solo.par.bgalpha = 0.95
    solo.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    solo.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    solo.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    solo.par.borderaalpha = 0.8
    solo.par.leftborderi = 'bordera'
    solo.par.rightborderi = 'bordera'
    solo.par.bottomborderi = 'bordera'
    solo.par.topborderi = 'bordera'
    solo.par.borderover = True

# 4. Fit, Load, Mode, Clear buttons
for bname in ['btn_Fit', 'btn_Load', 'btn_Mode', 'btn_Clear']:
    b = ah.op(bname)
    if b:
        b.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
        b.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
        b.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"
        b.par.bgalpha = 0.85
        b.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
        b.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
        b.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
        b.par.borderaalpha = 0.7
        b.par.leftborderi = 'bordera'
        b.par.rightborderi = 'bordera'
        b.par.bottomborderi = 'bordera'
        b.par.topborderi = 'bordera'
        b.par.borderover = True

# 5. Audio track waveform container border
if tr:
    tr.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'r'].val"
    tr.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'g'].val"
    tr.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'b'].val"
    tr.par.bgalpha = 1.0

    tr.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    tr.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    tr.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    tr.par.borderaalpha = 0.8
    tr.par.leftborderi = 'bordera'
    tr.par.rightborderi = 'bordera'
    tr.par.bottomborderi = 'bordera'
    tr.par.topborderi = 'bordera'
    tr.par.borderover = True

print('container_AudioHeader and container_AudioTrack styled with ProSlate tokens')
