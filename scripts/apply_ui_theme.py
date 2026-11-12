"""
ProSlate UI v2 pass for TD-MTL  (runs INSIDE TouchDesigner via TDMCP).
Usage:  python scripts/td_client.py scripts/apply_ui_theme.py

Idempotent: re-running re-applies the same values, never stacks changes.
Everything is either a token expression bound to UI/colors/out, or a value
documented against that palette.
"""

# ----------------------------------------------------------------------------
# 0. Token table extensions
# ----------------------------------------------------------------------------
TOKENS = [
    # name,              r,      g,      b,      a,     hex
    ('canvas_bg',       0.030, 0.033, 0.039, 1.0, '#08090a'),
    ('grid_line',       0.125, 0.135, 0.155, 1.0, '#202226'),
    ('playhead',        0.450, 0.860, 0.920, 1.0, '#73dbeb'),
    ('snap_accent',     0.280, 0.460, 0.540, 1.0, '#47758a'),
    ('cue_default',     0.114, 0.200, 0.251, 1.0, '#1d3340'),
    ('cue_outline',     0.169, 0.200, 0.231, 1.0, '#2b333b'),
    ('cue_outline_sel', 0.749, 0.902, 0.941, 1.0, '#bfe6f0'),
    ('cue_outline_multi', 0.878, 0.749, 0.290, 1.0, '#e0bf4a'),
    ('ruler_text',      0.520, 0.560, 0.600, 1.0, '#858f99'),
]

COLORS = '/Multi_Layer_Timeline/UI/colors'
ROOT = '/Multi_Layer_Timeline'

# Old (saturated) -> new (ProSlate desaturated) cue presets
CUE_OLD = {
    'DefaultBlue':   (0.000, 0.184, 0.395),
    'EmeraldGreen':  (0.050, 0.380, 0.180),
    'AmberGold':     (0.480, 0.300, 0.040),
    'VioletMagenta': (0.340, 0.080, 0.440),
    'CrimsonRed':    (0.480, 0.060, 0.090),
    'CyanElectric':  (0.020, 0.350, 0.450),
    'DarkSlate':     (0.120, 0.120, 0.160),
}
CUE_NEW = {
    'DefaultBlue':   (0.114, 0.200, 0.251),
    'EmeraldGreen':  (0.086, 0.227, 0.180),
    'AmberGold':     (0.239, 0.184, 0.063),
    'VioletMagenta': (0.200, 0.125, 0.247),
    'CrimsonRed':    (0.239, 0.106, 0.125),
    'CyanElectric':  (0.063, 0.216, 0.259),
    'DarkSlate':     (0.141, 0.153, 0.176),
}

report = []


def C(name):
    """Token value helper."""
    try:
        t = op(COLORS + '/out')
        return (float(t[name, 'r'].val), float(t[name, 'g'].val),
                float(t[name, 'b'].val), float(t[name, 'a'].val))
    except Exception:
        return None


def tok(name):
    return "op('%s/out')['%s', 'r'].val" % (COLORS, name), \
           "op('%s/out')['%s', 'g'].val" % (COLORS, name), \
           "op('%s/out')['%s', 'b'].val" % (COLORS, name)


def paint_bg(o, token, alpha_token=None, alpha=None):
    r, g, b = tok(token)
    o.par.bgcolorr.expr = r
    o.par.bgcolorg.expr = g
    o.par.bgcolorb.expr = b
    if alpha is not None:
        o.par.bgalpha = alpha
    elif alpha_token:
        o.par.bgalpha.expr = "op('/Multi_Layer_Timeline/UI/colors/out')['%s', 'a'].val" % alpha_token


def paint_bg_roll(o, token, roll_token, alpha=1.0):
    """Background that switches token on rollover."""
    r0, g0, b0 = tok(token)
    r1, g1, b1 = tok(roll_token)
    flag = "me.panel.rollover"
    o.par.bgcolorr.expr = "(%s) if %s else (%s)" % (r1, flag, r0)
    o.par.bgcolorg.expr = "(%s) if %s else (%s)" % (g1, flag, g0)
    o.par.bgcolorb.expr = "(%s) if %s else (%s)" % (b1, flag, b0)
    o.par.bgalpha = alpha


def flat_face(btn):
    """Kill the inner text background so buttons read as one flat card."""
    for c in btn.children:
        if c.type == 'text' and c.name in ('text', 'label'):
            c.par.bgalpha = 0


# ----------------------------------------------------------------------------
# 1. Tokens
# ----------------------------------------------------------------------------
def step_tokens():
    t = op(COLORS + '/table_colors')
    existing = {t[i, 'name'].val: i for i in range(1, t.numRows)}
    for name, r, g, b, a, hx in TOKENS:
        if name in existing:
            i = existing[name]
        else:
            i = t.numRows
            t.appendRow([name, r, g, b, a, hx])
        for col, val in (('r', r), ('g', g), ('b', b), ('a', a), ('hex', hx)):
            t[i, col] = val
    report.append('tokens: %d rows' % t.numRows)


# ----------------------------------------------------------------------------
# 2. 3D canvas: background, grid, playhead, snap line
# ----------------------------------------------------------------------------
def step_canvas():
    t3 = op(ROOT + '/Timeline3D')

    # --- timeline background plane: constant material instead of black phong
    canvas = t3.op('Canvas')
    mat = canvas.op('mat_canvas_bg')
    if not mat:
        mat = canvas.create(constantMAT, 'mat_canvas_bg')
    mat.nodeX, mat.nodeY = 900, 400
    mat.par.colorr, mat.par.colorg, mat.par.colorb, mat.par.alpha = C('canvas_bg')
    bg_geo = canvas.op('geo_Timeline_Bg')
    if bg_geo:
        bg_geo.par.material = mat
        bg_geo.par.render = True
    report.append('canvas bg -> constant #08090a')

    # --- grid / row separator lines
    c2 = canvas.op('constant2')
    c2.par.colorr, c2.par.colorg, c2.par.colorb = C('grid_line')[:3]

    # --- playhead
    c1 = canvas.op('constant1')
    c1.par.colorr, c1.par.colorg, c1.par.colorb = C('playhead')[:3]

    # --- snap line (was red)
    ln = canvas.op('line1')
    if ln:
        c = C('snap_accent')
        for p in ('linenearcolorr', 'linefarcolorr'):
            setattr(ln.par, p, c[0])
        for p in ('linenearcolorg', 'linefarcolorg'):
            setattr(ln.par, p, c[1])
        for p in ('linenearcolorb', 'linefarcolorb'):
            setattr(ln.par, p, c[2])

    report.append('grid/playhead/snap recoloured to slate + cyan')


# ----------------------------------------------------------------------------
# 3. Cue shader: hairline idle outline, accent selection, shading
# ----------------------------------------------------------------------------
CUE_SHADER_OLD = """	float alpha;

	vec3 selectionColors[3] = vec3[](vec3(0.1843, 0.1843, 0.1843),vec3(1.0,1.0,1.0),vec3(1.0, 0.9882, 0.3882));
	float outline = Outline(vec2(outlineUV.x * uZoom, newUV.y), .03);

	if (outline == 1.0) {
		outcol.rgb = selectionColors[iVert.selectionIndex] ;
		alpha = 1.0;

	} 
	else if (texCoord0.x < 1.5 / uvAspect && texCoord0.x > .5 / uvAspect){		// the head of the cue

		outcol += colorMapColor;
		alpha = colorMapColor.a ;

	}
	else {										// the rest of the cue
		outcol += instanceColor;
		alpha = 1.0;
	}"""

CUE_SHADER_NEW = """	float alpha;

	// ProSlate: hairline idle outline, light-cyan selection, gold multi-selection
	vec3 selectionColors[3] = vec3[](vec3(0.169, 0.200, 0.231),vec3(0.749, 0.902, 0.941),vec3(0.878, 0.749, 0.290));
	float outline = Outline(vec2(outlineUV.x * uZoom, newUV.y), .022);

	if (outline == 1.0) {
		outcol.rgb = selectionColors[iVert.selectionIndex] ;
		alpha = 1.0;

	} 
	else {
		// subtle vertical shading gives cue cards depth without extra passes
		float shade = mix(0.88, 1.07, clamp(texCoord0.y, 0.0, 1.0));

		if (texCoord0.x < 1.5 / uvAspect && texCoord0.x > .5 / uvAspect){		// the head of the cue

			outcol += colorMapColor;
			alpha = colorMapColor.a ;

		}
		else {										// the rest of the cue
			outcol += instanceColor * shade;
			alpha = 1.0;
		}
	}"""

BADGE_OLD = """			vec3 bgCol = mix(outcol.rgb, vec3(0.06, 0.11, 0.20), 0.90);
			vec3 borderCol = (iVert.selectionIndex > 0) ? vec3(0.55, 0.85, 1.0) : vec3(0.38, 0.66, 0.96);"""

BADGE_NEW = """			vec3 bgCol = mix(outcol.rgb, vec3(0.059, 0.071, 0.086), 0.92);
			vec3 borderCol = (iVert.selectionIndex > 1) ? vec3(0.878, 0.749, 0.290) : ((iVert.selectionIndex > 0) ? vec3(0.749, 0.902, 0.941) : vec3(0.360, 0.430, 0.480));"""

# The badge border was first patched with a single "> 0" test (cyan for every selected
# cue); upgrade that intermediate form so a re-run still ends in the gold multi state.
BADGE_SEL_ONLY = """			vec3 bgCol = mix(outcol.rgb, vec3(0.059, 0.071, 0.086), 0.92);
			vec3 borderCol = (iVert.selectionIndex > 0) ? vec3(0.749, 0.902, 0.941) : vec3(0.360, 0.430, 0.480);"""

ICON_OLD = """				if (inOutNode) {
					iconCol = vec3(0.32, 0.86, 1.0);
				} else if (inTopNode || inBotNode) {
					iconCol = vec3(0.92, 0.96, 1.0);
				} else if (onWireTop || onWireBot) {
					iconCol = vec3(0.65, 0.84, 0.98);
				}"""

ICON_NEW = """				if (inOutNode) {
					iconCol = vec3(0.451, 0.800, 0.863);
				} else if (inTopNode || inBotNode) {
					iconCol = vec3(0.800, 0.860, 0.900);
				} else if (onWireTop || onWireBot) {
					iconCol = vec3(0.520, 0.640, 0.700);
				}"""


def step_cue_shader():
    d = op(ROOT + '/Timeline3D/Cues/phong1GLSL_CueMatPixel')
    txt = d.text
    changed = 0
    # idle cues: subtle slate hairline (selection 1), selected: light cyan (selection 2)
    for old, new in (
        ('vec3(0.1843, 0.1843, 0.1843),vec3(1.0,1.0,1.0),vec3(1.0, 0.9882, 0.3882)',
         'vec3(0.190, 0.222, 0.255),vec3(0.749, 0.902, 0.941),vec3(0.878, 0.749, 0.290)'),
        # intermediate state: cyan was used for both selected and multi-selected cues
        ('vec3(0.190, 0.222, 0.255),vec3(0.749, 0.902, 0.941),vec3(0.749, 0.902, 0.941)',
         'vec3(0.190, 0.222, 0.255),vec3(0.749, 0.902, 0.941),vec3(0.878, 0.749, 0.290)'),
        (BADGE_SEL_ONLY, BADGE_NEW),
        ('newUV.y), .03);', 'newUV.y), .022);'),
        ('outcol += instanceColor;', 'outcol += instanceColor * mix(0.88, 1.07, clamp(texCoord0.y, 0.0, 1.0));'),
        (BADGE_OLD, BADGE_NEW),
        (ICON_OLD, ICON_NEW),
    ):
        if new not in txt and old in txt:
            txt = txt.replace(old, new)
            changed += 1
    if changed:
        d.text = txt
    report.append('cue shader: %d patches applied' % changed)


# ----------------------------------------------------------------------------
# 4. Ruler: smaller labels, dimmer tint
# ----------------------------------------------------------------------------
def step_ruler():
    t3 = op(ROOT + '/Timeline3D')
    v = t3.op('Canvas/geo_TimeIcons/phong4GLSLVertex')
    # NOTE: the glyph atlas layout is coupled to this sprite size, keep 70
    if '62. * visible' in v.text:
        v.text = v.text.replace('gl_PointSize = 62. * visible', 'gl_PointSize = 70. * visible')
    f = t3.op('Canvas/geo_TimeIcons/phong4GLSLPixel')
    if 'ProSlate ruler tint' not in f.text:
        f.text = f.text.replace(
            "\toutcol.a = alpha;\n\toFragColor[0] = TDOutputSwizzle(outcol);\n\n}",
            "\t// ProSlate ruler tint: labels recede behind the content\n\toutcol.rgb *= vec3(0.560, 0.600, 0.640);\n\toutcol.a = alpha;\n\toFragColor[0] = TDOutputSwizzle(outcol);\n\n}")
    report.append('ruler: 62px sprites, dim tint')


# ----------------------------------------------------------------------------
# 5. Layer header cards + cue titles typography
# ----------------------------------------------------------------------------
def step_typography_3d():
    t3 = op(ROOT + '/Timeline3D')
    lay = t3.op('Layers/base_Layer0/text1')
    if lay:
        lay.par.font = 'Bahnschrift Condensed'
        lay.par.fontsizex = 11.5
        lay.par.bold = 0
        lay.par.fontcolorr, lay.par.fontcolorg, lay.par.fontcolorb = (0.62, 0.66, 0.72)
        lay.par.fontalpha = 1.0
    cue_txt = t3.op('Cues/base_Cue0/base_Textures/text0')
    if cue_txt:
        cue_txt.par.font = 'Bahnschrift Condensed'
        cue_txt.par.fontsizex = 26
        cue_txt.par.bold = 0
        cue_txt.par.alignx = 'left'
        cue_txt.par.fontcolorr, cue_txt.par.fontcolorg, cue_txt.par.fontcolorb = (0.88, 0.91, 0.94)
    report.append('3D typography: dim layer labels, lighter cue titles')


# ----------------------------------------------------------------------------
# 6. Cue palette: preset map + migrate existing cues
# ----------------------------------------------------------------------------
PRESET_CODE = '''def onValueChange(par, prev):
    # ProSlate cue palette: desaturated cards, readable at 60 FPS under stage light
    COLOR_MAP = {
        'DefaultBlue':   (0.114, 0.200, 0.251),
        'EmeraldGreen':  (0.086, 0.227, 0.180),
        'AmberGold':     (0.239, 0.184, 0.063),
        'VioletMagenta': (0.200, 0.125, 0.247),
        'CrimsonRed':    (0.239, 0.106, 0.125),
        'CyanElectric':  (0.063, 0.216, 0.259),
        'DarkSlate':     (0.141, 0.153, 0.176),
    }
    val = par.eval()
    if val in COLOR_MAP:
        rgb = COLOR_MAP[val]
        cue = par.owner
        cue.par.Backgroundcolorr = rgb[0]
        cue.par.Backgroundcolorg = rgb[1]
        cue.par.Backgroundcolorb = rgb[2]
    return
'''


def step_cue_palette():
    pe = op(ROOT + '/Timeline3D/Cues/parexec_cue_colors')
    if pe and 'ProSlate cue palette' not in pe.text:
        pe.text = PRESET_CODE

    migrated = 0
    scanned = 0

    def walk(o, depth=0):
        nonlocal migrated, scanned
        if depth > 12:
            return
        try:
            col = (o.par.Backgroundcolorr.eval(), o.par.Backgroundcolorg.eval(),
                   o.par.Backgroundcolorb.eval())
        except Exception:
            col = None
        if col is not None:
            scanned += 1
            for name, old in CUE_OLD.items():
                if all(abs(a - b) < 0.02 for a, b in zip(col, old)):
                    new = CUE_NEW[name]
                    o.par.Backgroundcolorr = new[0]
                    o.par.Backgroundcolorg = new[1]
                    o.par.Backgroundcolorb = new[2]
                    migrated += 1
                    break
        for c in getattr(o, 'children', []):
            walk(c, depth + 1)

    walk(op(ROOT))
    report.append('cue palette: map rewritten, %d/%d cue ops migrated' % (migrated, scanned))


# ----------------------------------------------------------------------------
# 7. 2D chrome: flat buttons, tokens, typography
# ----------------------------------------------------------------------------
def step_buttons_2d():
    r = op(ROOT)
    literal_btns = []
    for parent_name in ('container_Transport', 'container_Duration', 'container_AudioHeader'):
        p = r.op(parent_name)
        if not p:
            continue
        for c in p.children:
            if c.type == 'container' and c.name.startswith('btn_'):
                # only repaint faces that are still literal colours
                if not c.par.bgcolorr.expr:
                    literal_btns.append(c)
                flat_face(c)
    for c in literal_btns:
        paint_bg_roll(c, 'button_off', 'button_offroll', alpha=0.9)
    report.append('2D buttons: %d flat faces tokenised' % len(literal_btns))


def step_duration_card():
    r = op(ROOT)
    d = r.op('container_Duration')
    for name in ('btn_Settings', 'btn_PresetMenu'):
        c = d.op(name)
        if not c:
            continue
        paint_bg_roll(c, 'button_off', 'button_offroll', alpha=0.95)
        for k in c.children:
            if k.type == 'text':
                k.par.fontsizex = 12
                k.par.fontcolorr, k.par.fontcolorg, k.par.fontcolorb = (0.72, 0.78, 0.84)
    lbl = d.op('text_dur_label')
    if lbl:
        lbl.par.fontsizex = 9
        lbl.par.fontcolorr, lbl.par.fontcolorg, lbl.par.fontcolorb = (0.42, 0.44, 0.46)
    report.append('duration card: buttons + label tokenised')


def step_audio_header():
    r = op(ROOT)
    a = r.op('container_AudioHeader')
    if not a:
        return
    # volume slider + meters
    sv = a.op('slider_vol')
    if sv:
        paint_bg(sv, 'slider_base', alpha=1.0)
        fb = sv.op('fill_bar')
        if fb:
            c = C('slider_fill')
            fb.par.bgcolorr.expr = "op('%s/out')['slider_fill', 'r'].val" % COLORS
            fb.par.bgcolorg.expr = "op('%s/out')['slider_fill', 'g'].val" % COLORS
            fb.par.bgcolorb.expr = "op('%s/out')['slider_fill', 'b'].val" % COLORS
            fb.par.bgalpha = 0.9
    mc = a.op('meter_comp')
    if mc:
        for ch in ('ch_l_bg', 'ch_r_bg'):
            b = mc.op(ch)
            if b:
                paint_bg(b, 'slider_base', alpha=1.0)
    # section label + destructive action
    t = a.op('text_title')
    if t:
        t.par.bold = 0
        t.par.fontcolorr, t.par.fontcolorg, t.par.fontcolorb = (0.52, 0.56, 0.60)
    clr = a.op('text_Clear')
    if clr:
        clr.par.fontcolorr, clr.par.fontcolorg, clr.par.fontcolorb = (0.70, 0.32, 0.32)
    # secondary action labels: not bold-white
    for nm in ('text_Load', 'text_Fit'):
        o = a.op(nm)
        if o:
            o.par.bold = 0
            o.par.fontcolorr, o.par.fontcolorg, o.par.fontcolorb = (0.80, 0.84, 0.88)
    report.append('audio header: slider/meter/labels tokenised')


def step_popup():
    r = op(ROOT)
    p = r.op('menu_DurationPopup')
    if not p:
        return
    paint_bg(p, 'panel_header', alpha=1.0)
    for c in p.children:
        if c.type != 'container':
            continue
        c.par.bgcolorr.expr = "op('%s/out')['panel_active', 'r'].val if me.fetch('selected', False) else (op('%s/out')['panel_roll', 'r'].val if me.panel.rollover else op('%s/out')['panel_bg', 'r'].val)" % (COLORS, COLORS, COLORS)
        c.par.bgcolorg.expr = "op('%s/out')['panel_active', 'g'].val if me.fetch('selected', False) else (op('%s/out')['panel_roll', 'g'].val if me.panel.rollover else op('%s/out')['panel_bg', 'g'].val)" % (COLORS, COLORS, COLORS)
        c.par.bgcolorb.expr = "op('%s/out')['panel_active', 'b'].val if me.fetch('selected', False) else (op('%s/out')['panel_roll', 'b'].val if me.panel.rollover else op('%s/out')['panel_bg', 'b'].val)" % (COLORS, COLORS, COLORS)
        for k in c.children:
            if k.type == 'text':
                k.par.fontsizex = 12
                k.par.fontcolorr, k.par.fontcolorg, k.par.fontcolorb = (0.78, 0.82, 0.86)
    report.append('duration popup: slate menu rows')


def step_swatches():
    r = op(ROOT)
    sw = r.op('container_InspectorHeader/comp_Swatches')
    if not sw:
        return
    for c in sw.children:
        name = c.name.replace('dot_', '')
        if name in CUE_NEW:
            col = CUE_NEW[name]
            c.par.bgcolorr, c.par.bgcolorg, c.par.bgcolorb = col
            c.par.bgalpha = 1.0
    report.append('inspector swatches: new cue palette')


# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
for fn in (step_tokens, step_canvas, step_cue_shader, step_ruler,
           step_typography_3d, step_cue_palette, step_buttons_2d,
           step_duration_card, step_audio_header, step_popup, step_swatches):
    try:
        fn()
    except Exception as e:
        report.append('ERROR in %s: %s' % (fn.__name__, e))

for t3geo in (op(ROOT + '/Timeline3D/Render/render1'),
              op(ROOT + '/Timeline3D/Render/render_LayerSettings')):
    try:
        t3geo.cook(force=True)
    except Exception:
        pass

print('\n'.join(report))
