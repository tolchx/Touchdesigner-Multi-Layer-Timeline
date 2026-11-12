# Script to modernize container_Preview header and viewport
prev = op('/Multi_Layer_Timeline/container_Preview')
if not prev:
    raise Exception('container_Preview not found')

hb = prev.op('header_bar')
vp = prev.op('viewport')

if hb and vp:
    # Anchor header_bar at top of preview
    hb.par.leftanchor = 0.0
    hb.par.rightanchor = 1.0
    hb.par.bottomanchor = 0.915
    hb.par.topanchor = 1.0
    hb.par.align = 'horizlr'
    hb.par.marginl = 6.0
    hb.par.marginr = 6.0
    hb.par.marginb = 0.0
    hb.par.margint = 0.0

    # Styling header_bar
    hb.par.bgcolorr.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'r'].val"
    hb.par.bgcolorg.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'g'].val"
    hb.par.bgcolorb.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['panel_header', 'b'].val"
    hb.par.bgalpha = 0.95

    hb.par.borderar.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
    hb.par.borderag.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
    hb.par.borderab.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
    hb.par.borderaalpha = 0.8
    hb.par.bottomborderi = 'bordera'
    hb.par.borderover = True

    # Style buttons inside header_bar
    btn_defs = [
        ('btn_out1', 'OUT 1', 'out1', 0.0),
        ('btn_out2', 'OUT 2', 'out2', 1.0),
        ('btn_split1', 'SPLIT', 'split', 2.0),
    ]

    for bname, blabel, bmode, aorder in btn_defs:
        b = hb.op(bname)
        if b:
            b.par.w = 64
            b.par.h = 22
            b.par.alignorder = aorder
            b.par.marginb = 4.0
            b.par.margint = 4.0
            b.par.marginr = 4.0

            # Dynamic background color depending on Previewmode
            b.par.bgcolorr.expr = f"op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'r'].val if parent(2).par.Previewmode.eval() == '{bmode}' else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'r'].val"
            b.par.bgcolorg.expr = f"op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'g'].val if parent(2).par.Previewmode.eval() == '{bmode}' else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'g'].val"
            b.par.bgcolorb.expr = f"op('/Multi_Layer_Timeline/UI/colors/out')['button_on', 'b'].val if parent(2).par.Previewmode.eval() == '{bmode}' else op('/Multi_Layer_Timeline/UI/colors/out')['button_off', 'b'].val"
            b.par.bgalpha = 0.9

            b.par.borderar.expr = f"op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'r'].val if parent(2).par.Previewmode.eval() == '{bmode}' else op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'r'].val"
            b.par.borderag.expr = f"op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'g'].val if parent(2).par.Previewmode.eval() == '{bmode}' else op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'g'].val"
            b.par.borderab.expr = f"op('/Multi_Layer_Timeline/UI/colors/out')['outline_active', 'b'].val if parent(2).par.Previewmode.eval() == '{bmode}' else op('/Multi_Layer_Timeline/UI/colors/out')['outline_static', 'b'].val"
            b.par.borderaalpha = 0.8
            b.par.leftborderi = 'bordera'
            b.par.rightborderi = 'bordera'
            b.par.bottomborderi = 'bordera'
            b.par.topborderi = 'bordera'
            b.par.borderover = True

            # If button has textCOMP inside, update font & label
            txt_child = b.findChildren(type=textCOMP)
            if txt_child:
                txt_child[0].par.font = 'Bahnschrift Condensed'
                txt_child[0].par.text = blabel
                txt_child[0].par.fontsize = 9
                txt_child[0].par.bold = True
            elif hasattr(b.par, 'label'):
                b.par.label = blabel

    # Add or update live text readout in header_bar
    info_txt = hb.op('text_live_info')
    if info_txt is None:
        info_txt = hb.create(textCOMP, 'text_live_info')

    info_txt.nodeX = 500
    info_txt.nodeY = 0
    info_txt.par.w = 550
    info_txt.par.h = 24
    info_txt.par.alignorder = 3.0
    info_txt.par.marginl = 15.0
    info_txt.par.font = 'Bahnschrift Condensed'
    info_txt.par.text.expr = "op('/Multi_Layer_Timeline/container_Preview/text_header').par.text.eval() if op('/Multi_Layer_Timeline/container_Preview/text_header') else 'PREVIEW LIVE'"
    info_txt.par.fontsize = 9
    info_txt.par.bold = False
    info_txt.par.fontcolorr = 0.65
    info_txt.par.fontcolorg = 0.68
    info_txt.par.fontcolorb = 0.72
    info_txt.par.alignx = 'left'
    info_txt.par.aligny = 'center'
    info_txt.par.bgalpha = 0.0

    # Anchor viewport below header_bar
    vp.par.leftanchor = 0.0
    vp.par.rightanchor = 1.0
    vp.par.bottomanchor = 0.0
    vp.par.topanchor = 0.915

print('container_Preview header bar and viewport modernized')
