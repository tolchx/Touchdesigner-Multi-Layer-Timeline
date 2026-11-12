# Modernize container_AudioHeader strip
ah = op('/Multi_Layer_Timeline/container_AudioHeader')
if not ah:
    raise Exception('container_AudioHeader not found')

colors = op('/Multi_Layer_Timeline/UI/colors/out')

# 1. Accent bar on left edge
ab = ah.op('accent_bar')
if ab:
    ab.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'r'].val"
    ab.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'g'].val"
    ab.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'b'].val"
    ab.par.bgalpha = 1.0

# 2. Track Title Label
lbl_t = ah.op('lbl_title')
if lbl_t:
    lbl_t.par.borderover = False
    lbl_t.par.leftborder = 'off'
    lbl_t.par.rightborder = 'off'
    lbl_t.par.topborder = 'off'
    lbl_t.par.bottomborder = 'off'
    lbl_t.par.bgalpha = 0.0
    txt_t = lbl_t.op('text_title')
    if txt_t:
        txt_t.par.font = 'Bahnschrift Condensed'
        txt_t.par.bold = True
        txt_t.par.text = 'A1  AUDIO MASTER'
        txt_t.par.fontsizex = 10.5
        txt_t.par.fontcolorr = 0.88
        txt_t.par.fontcolorg = 0.90
        txt_t.par.fontcolorb = 0.95

# 3. Duration & Sample Rate badge
lbl_d = ah.op('lbl_dur')
if lbl_d:
    lbl_d.par.borderover = False
    lbl_d.par.leftborder = 'off'
    lbl_d.par.rightborder = 'off'
    lbl_d.par.topborder = 'off'
    lbl_d.par.bottomborder = 'off'
    lbl_d.par.bgalpha = 0.0
    txt_d = lbl_d.op('text_dur')
    if txt_d:
        txt_d.par.font = 'Bahnschrift Condensed'
        txt_d.par.fontsizex = 9.0
        txt_d.par.fontcolorr = 0.50
        txt_d.par.fontcolorg = 0.53
        txt_d.par.fontcolorb = 0.58

# 4. Audio File name badge
box_f = ah.op('box_file')
if box_f:
    box_f.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'r'].val"
    box_f.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'g'].val"
    box_f.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_base', 'b'].val"
    box_f.par.bgalpha = 0.95
    box_f.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    box_f.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    box_f.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    box_f.par.borderaalpha = 0.7
    box_f.par.leftborderi = 'bordera'
    box_f.par.rightborderi = 'bordera'
    box_f.par.topborderi = 'bordera'
    box_f.par.bottomborderi = 'bordera'
    box_f.par.borderover = True
    txt_f = box_f.op('text_file')
    if txt_f:
        txt_f.par.font = 'Bahnschrift Condensed'
        txt_f.par.fontsizex = 8.5
        txt_f.par.fontcolorr = 0.65
        txt_f.par.fontcolorg = 0.68
        txt_f.par.fontcolorb = 0.72

# 5. Buttons styling
for bname, glyph in [('btn_Load', '+ LOAD'), ('btn_Mode', 'WAVE/SPEC'), ('btn_Fit', 'FIT TL'), ('btn_Clear', 'CLR')]:
    b = ah.op(bname)
    if b:
        b.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
        b.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
        b.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"
        b.par.bgalpha = 0.9
        b.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
        b.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
        b.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
        b.par.borderaalpha = 0.8
        b.par.leftborderi = 'bordera'
        b.par.rightborderi = 'bordera'
        b.par.topborderi = 'bordera'
        b.par.bottomborderi = 'bordera'
        b.par.borderover = True

print('Audio header modernized with sleek DAW track styling')
