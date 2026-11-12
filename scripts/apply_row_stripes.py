"""
ProSlate pass 2 for TD-MTL (runs INSIDE TouchDesigner via TDMCP):
  - subtle alternate-row striping in the timeline (world-space, no extra geometry)
  - per-layer colour accent rail in the scene header cards
Usage: python scripts/td_client.py scripts/apply_row_stripes.py

Everything is token-driven from /Multi_Layer_Timeline/UI/colors.
Idempotent: re-running reuses the ops it created.
"""

ROOT = '/Multi_Layer_Timeline'
COLORS = ROOT + '/UI/colors'
T3 = ROOT + '/Timeline3D'
CANVAS = T3 + '/Canvas'
LAYERS = T3 + '/Layers'

TOKENS = [
    ('row_alt', 0.055, 0.060, 0.072, 1.0, '#0e0f12'),
    ('layer_accent_1', 0.328, 0.472, 0.520, 1.0, '#547885'),
    ('layer_accent_2', 0.720, 0.580, 0.220, 1.0, '#b89438'),
    ('layer_accent_3', 0.450, 0.360, 0.580, 1.0, '#735c94'),
    ('layer_accent_4', 0.280, 0.520, 0.420, 1.0, '#47856b'),
    ('layer_accent_5', 0.660, 0.360, 0.340, 1.0, '#a85c57'),
]

CANVAS_VERT = """out Vertex
{
    vec4 color;
    vec3 worldSpacePos;
    vec3 worldSpaceNorm;
    vec2 texCoord0;
    flat int cameraIndex;
} oVert;

void main()
{
    vec2 texcoord = uv[0].st;
    oVert.texCoord0.st = texcoord.st;

    vec4 worldSpacePos = TDDeform(P);
    vec3 uvUnwrapCoord = TDUVUnwrapCoord();
    gl_Position = TDWorldToProj(worldSpacePos, uvUnwrapCoord);

#ifndef TD_PICKING_ACTIVE
    oVert.cameraIndex = TDCameraIndex();
    oVert.worldSpacePos.xyz = worldSpacePos.xyz;
    oVert.color = vec4(1.0);
    oVert.worldSpaceNorm.xyz = normalize(TDDeformNorm(N));
#else
    TDWritePickingValues();
#endif
}
"""

CANVAS_PIXEL = """uniform float uRows;
uniform float uLower;
uniform float uRowH;
uniform vec4 uBase;
uniform vec4 uAlt;

in Vertex
{
    vec4 color;
    vec3 worldSpacePos;
    vec3 worldSpaceNorm;
    vec2 texCoord0;
    flat int cameraIndex;
} iVert;

layout(location = 0) out vec4 oFragColor[TD_NUM_COLOR_BUFFERS];

void main()
{
    TDCheckDiscard();

    // ProSlate row striping: alternate rows lifted by uAlt, computed in world space
    float y = iVert.worldSpacePos.y;
    float band = floor((y - uLower) / max(uRowH, 0.0001));
    float inside = step(uLower, y) * step(y, uLower + uRows * uRowH);
    float alt = mod(band, 2.0) * inside;

    vec4 col = mix(uBase, uAlt, alt);
    col.a = 1.0;

    oFragColor[0] = TDOutputSwizzle(col);
    for (int i = 1; i < TD_NUM_COLOR_BUFFERS; i++)
    {
        oFragColor[i] = vec4(0.0);
    }
}
"""

ACCENT_EXPR = ("op('" + COLORS + "/out')['layer_accent_' + str((int(''.join(ch for ch in "
               "parent().name if ch.isdigit()) or 0) % 5) + 1), '{ch}'].val")

ACCENT_PIXEL = """uniform vec4 uColor;
uniform float uWidth;

out vec4 fragColor;

void main()
{
    // thin left rail of the layer card, token coloured per layer.
    // premultiplied rail: over TOP expects src.rgb already scaled by alpha
    float a = step(vUV.s, uWidth);
    float alpha = uColor.a * a;
    fragColor = TDOutputSwizzle(vec4(uColor.rgb * alpha, alpha));
}
"""

report = []


def C(name):
    t = op(COLORS + '/out')
    return (float(t[name, 'r'].val), float(t[name, 'g'].val),
            float(t[name, 'b'].val), float(t[name, 'a'].val))


def token_expr(name, chan):
    return "op('%s/out')['%s', '%s'].val" % (COLORS, name, chan)


def step_tokens():
    t = op(COLORS + '/table_colors')
    have = {t[i, 'name'].val: i for i in range(1, t.numRows)}
    for name, r, g, b, a, hx in TOKENS:
        i = have.get(name)
        if i is None:
            i = t.numRows
            t.appendRow([name, r, g, b, a, hx])
        for col, val in (('r', r), ('g', g), ('b', b), ('a', a), ('hex', hx)):
            t[i, col] = val
    report.append('tokens: row_alt + layer_accent_1..5')


def step_stripes():
    cv = op(CANVAS)

    # drop the first (geometry based) attempt
    for legacy in ('geo_RowStripes', 'mat_row_stripes', 'glsl_row_stripes',
                   'glsl_rows_pixel', 'mat_stripe_test'):
        old = cv.op(legacy)
        if old:
            old.destroy()

    vdat = cv.op('glsl_canvas_vertex')
    if not vdat:
        vdat = cv.create(textDAT, 'glsl_canvas_vertex')
        vdat.nodeX, vdat.nodeY = 700, -260
    try:
        vdat.par.language = 'glsl'
    except Exception:
        pass
    if 'oVert.color = vec4(1.0);' not in vdat.text:
        vdat.text = CANVAS_VERT

    pdat = cv.op('glsl_canvas_pixel')
    if not pdat:
        pdat = cv.create(textDAT, 'glsl_canvas_pixel')
        pdat.nodeX, pdat.nodeY = 700, -340
    try:
        pdat.par.language = 'glsl'
    except Exception:
        pass
    if 'ProSlate row striping' not in pdat.text:
        pdat.text = CANVAS_PIXEL

    mat = cv.op('glsl_mat_canvas')
    if not mat:
        mat = cv.create(glslMAT, 'glsl_mat_canvas')
        mat.nodeX, mat.nodeY = 900, -300
    mat.par.vdat = vdat
    mat.par.pdat = pdat

    # geometry of the rows
    mat.par.vec0name = 'uRows'
    mat.par.vec0valuex.expr = 'ipar.UserSettings.Layercount'
    mat.par.vec1name = 'uLower'
    mat.par.vec1valuex.expr = 'ipar.SystemSettings.Computedlowerbounds'
    mat.par.vec2name = 'uRowH'
    mat.par.vec2valuex.expr = 'ipar.SystemSettings.Computedlayerheight'

    # colours from the token table
    mat.par.vec3name = 'uBase'
    mat.par.vec4name = 'uAlt'
    for idx, token in ((3, 'canvas_bg'), (4, 'row_alt')):
        for chan, comp in (('r', 'x'), ('g', 'y'), ('b', 'z'), ('a', 'w')):
            getattr(mat.par, 'vec%dvalue%s' % (idx, comp)).expr = token_expr(token, chan)

    bg = cv.op('geo_Timeline_Bg')
    bg.par.material = mat
    report.append('stripes: glsl_mat_canvas on geo_Timeline_Bg (world space bands)')


def step_layer_accent():
    t = op(LAYERS)
    cards = ['Template_layer1'] + ['base_Layer%d' % i for i in range(5)]
    done = 0
    for name in cards:
        c = t.op(name)
        if not c:
            continue
        for legacy in ('constant_accent', 'crop_accent'):
            old = c.op(legacy)
            if old:
                old.destroy()

        pix = c.op('glsl_accent_pixel')
        if not pix:
            pix = c.create(textDAT, 'glsl_accent_pixel')
        try:
            pix.par.language = 'glsl'
        except Exception:
            pass
        if 'premultiplied rail' not in pix.text:
            pix.text = ACCENT_PIXEL

        rail = c.op('glsl_accent')
        if not rail:
            rail = c.create(glslTOP, 'glsl_accent')
        rail.par.pixeldat = pix
        rail.par.outputresolution = 'custom'
        rail.par.resolutionw = 256
        rail.par.resolutionh = 256
        rail.par.vec0name = 'uColor'
        for comp, ch in (('x', 'r'), ('y', 'g'), ('z', 'b'), ('w', 'a')):
            getattr(rail.par, 'vec0value' + comp).expr = ACCENT_EXPR.format(ch=ch)
        rail.par.vec1name = 'uWidth'
        rail.par.vec1valuex = 0.040

        # keep the layer label clear of the accent rail
        label = c.op('text1')
        if label:
            label.par.alignx = 'left'
            label.par.positionunit = 'fraction'
            label.par.positionx = 0.075
            label.par.fontsizex = 11.5
            label.par.bold = 0
            label.par.fontcolorr, label.par.fontcolorg, label.par.fontcolorb = (0.62, 0.66, 0.72)

        ov = c.op('over_accent')
        if not ov:
            ov = c.create(overTOP, 'over_accent')
        ov.par.outputresolution = 'custom'
        ov.par.resolutionw = 256
        ov.par.resolutionh = 256
        want = [rail, c.op('over1')]
        cur = list(ov.inputs)
        for i, src in enumerate(want):
            if len(cur) > i and cur[i] == src:
                continue
            if len(cur) > i:
                ov.inputConnectors[i].disconnect()
            ov.inputConnectors[i].connect(src)

        nb = c.op('null_bg')
        if nb:
            if nb.inputs and nb.inputs[0] != ov:
                nb.inputConnectors[0].disconnect()
            if not nb.inputs:
                nb.inputConnectors[0].connect(ov)
        done += 1
    report.append('layer accent rail: %d cards wired' % done)


for fn in (step_tokens, step_stripes, step_layer_accent):
    try:
        fn()
    except Exception as e:
        report.append('ERROR in %s: %s' % (fn.__name__, e))

for op_path, fname in (('Timeline3D/Render/render1', 'rows_after_timeline.png'),
                       ('Timeline3D/Render/render_LayerSettings', 'rows_after_layers.png')):
    try:
        p = op(ROOT + '/' + op_path)
        p.cook(force=True)
        p.save('C:/Users/Tolch/Documents/AI_Code/Touchdesigner-Multi-Layer-Timeline/tmp/' + fname)
        report.append('saved tmp/' + fname)
    except Exception as e:
        report.append('capture error: %s' % e)

mat = op(CANVAS + '/glsl_mat_canvas')
if mat:
    report.append('mat errors: %r' % (mat.errors() or 'none'))

print('\n'.join(report))
