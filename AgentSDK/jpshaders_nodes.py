"""
JPShaders GLSL Node Factory & WebGL-to-TouchDesigner Transpiler
===============================================================
Fuente de Shaders: Librería JPShaders (FullScreenCode / jpupper)
Web Original:      https://fullscreencode.com/jpshadereditor/
Documentación API: https://fullscreencode.com/jpconnect/documentacion/#jpshader
Endpoint API VPS:  https://vps-4455523-x.dattaweb.com/jpshadereditor/api

Este módulo permite a un Agente de IA (vía TDMCP `execute_code`) o al usuario
dentro de TouchDesigner:
1. Consultar los 770+ shaders de la librería JPShaders en vivo o desde el catálogo local.
2. Transpilar automáticamente shaders WebGL de JPShader Editor a GLSL 3.30+ de TouchDesigner
   cumpliendo los contratos verificados C1-C23 (`out vec4 fragColor;`, `TDOutputSwizzle()`,
   `uTDOutputInfo.res.zw`, secuencia `vec` con `numBlocks`).
3. Instanciar nodos GLSL parametrizados listos para usar en TouchDesigner y en el
   Multi-Layer Timeline (TD-MTL), incluyendo en la sección de nodos GLSL:
   - Créditos oficiales a JPShaders y al autor original.
   - Botón interactivo "🌐 Visitar Web Original JPShaders" (`ui.viewFile`).
   - Sliders personalizados (0..1, colores RGB, pads XY) conectados en tiempo real al shader.
"""

import json
import os
import re
import urllib.request
import webbrowser

JPSHADER_WEB_URL = "https://fullscreencode.com/jpshadereditor/"
JPCONNECT_DOCS_URL = "https://fullscreencode.com/jpconnect/documentacion/#jpshader"
JPSHADER_API_BASE = "https://vps-4455523-x.dattaweb.com/jpshadereditor/api"
JPCONNECT_API_BASE = "https://vps-4455523-x.dattaweb.com/jpconnect/api"

_CATALOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jpshaders_catalog.json")


def load_local_catalog():
    """Carga el catálogo curado y pre-transpilado de JPShaders."""
    if os.path.exists(_CATALOG_PATH):
        with open(_CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def list_jpshaders(online=False):
    """
    Lista los shaders disponibles. Si online=True, consulta el VPS de JPShader Editor
    (770+ shaders); de lo contrario devuelve el catálogo local pre-validado.
    """
    if online:
        try:
            req = urllib.request.Request(f"{JPSHADER_API_BASE}/shaders", headers={"User-Agent": "TDMCP-Agent/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [s for s in data if s.get("compiles")]
        except Exception:
            pass
    return load_local_catalog()


def fetch_jpshader(shader_name: str):
    """
    Obtiene un shader por nombre (primero busca en el catálogo local curado;
    si no está, lo descarga en vivo desde la API de JPShader Editor).
    """
    local = load_local_catalog()
    for item in local:
        if item["name"].lower() == shader_name.lower() or item["id"].lower() == shader_name.lower():
            return item

    # Descarga en vivo desde el VPS de FullScreenCode
    url = f"{JPSHADER_API_BASE}/shaders/{shader_name}"
    req = urllib.request.Request(url, headers={"User-Agent": "TDMCP-Agent/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    code = raw.get("contenido") or ""
    if not code.strip():
        passes = raw.get("passesData") or {}
        if "main" in passes and passes["main"].get("code"):
            code = passes["main"]["code"]

    uniforms = raw.get("uniforms") or {}
    author = raw.get("autor", "jpupper")
    td_glsl = transpile_jpshader_to_td(code, uniforms)
    return {
        "id": f"jpshader-{shader_name.lower()}",
        "name": raw.get("nombre", shader_name),
        "author": author,
        "credits": f"JPShaders Library ({author}) — {JPSHADER_WEB_URL}",
        "webUrl": f"{JPSHADER_WEB_URL}shader.html?shader={shader_name}",
        "editorUrl": JPSHADER_WEB_URL,
        "docsUrl": JPCONNECT_DOCS_URL,
        "thumbnail": raw.get("imagePath", ""),
        "uniforms": uniforms,
        "uniformFormats": raw.get("uniformFormats") or {},
        "passCounter": raw.get("passCounter", 0),
        "webglCode": code,
        "tdGlslCode": td_glsl,
    }


def transpile_jpshader_to_td(code: str, uniforms: dict = None) -> str:
    """
    Convierte un fragment shader WebGL de JPShader Editor a GLSL 3.30+ nativo
    de TouchDesigner (glslmultiTOP / glslTOP).
    """
    uniforms = uniforms or {}
    lines = code.replace("\r\n", "\n").split("\n")
    cleaned_lines = []
    skip_ifdef = False

    builtin_pattern = re.compile(
        r"^\s*uniform\s+(vec2|float|sampler2D|sampler2DRect)\s+(resolution|u_resolution|time|u_time|backbuffer|intext|camara)\s*;"
    )
    precision_pattern = re.compile(r"^\s*precision\s+(lowp|mediump|highp)\s+float\s*;")
    uniform_decl_re = re.compile(r"^\s*uniform\s+(\w+)\s+(\w+)\s*;")
    declared_uniforms = set()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#ifdef GL_ES"):
            skip_ifdef = True
            continue
        if skip_ifdef and stripped.startswith("#endif"):
            skip_ifdef = False
            continue
        if precision_pattern.match(stripped):
            continue
        if builtin_pattern.match(stripped):
            continue

        m = uniform_decl_re.match(stripped)
        if m:
            declared_uniforms.add(m.group(2))

        cleaned_lines.append(line)

    body = "\n".join(cleaned_lines)
    body = re.sub(r"\btexture2DRect\s*\(", "texture(", body)
    body = re.sub(r"\btexture2D\s*\(", "texture(", body)

    def repl_fragcolor(match):
        expr = match.group(1).strip()
        if expr.startswith("vec4"):
            return f"fragColor = TDOutputSwizzle({expr});"
        return f"fragColor = TDOutputSwizzle(vec4({expr}));"

    body = re.sub(r"\bgl_FragColor\s*=\s*([^;]+);", repl_fragcolor, body)

    missing_uniform_decls = []
    for u_name, u_val in uniforms.items():
        if u_name in ("time", "u_time", "resolution", "u_resolution"):
            continue
        if u_name not in declared_uniforms:
            if isinstance(u_val, list):
                dim = max(2, min(4, len(u_val)))
                missing_uniform_decls.append(f"uniform vec{dim} {u_name};")
            else:
                missing_uniform_decls.append(f"uniform float {u_name};")

    header = [
        "// ============================================================================",
        "// Nodo GLSL Generado desde JPShaders (https://fullscreencode.com/jpshadereditor/)",
        "// Créditos: JPShaders por jpupper / FullScreenCode",
        "// Documentación: https://fullscreencode.com/jpconnect/documentacion/#jpshader",
        "// ============================================================================",
        "layout(location = 0) out vec4 fragColor;",
        "uniform float u_time;",
        "#define time u_time",
        "#define resolution (uTDOutputInfo.res.zw)",
        "#define u_resolution (uTDOutputInfo.res.zw)",
        "#define backbuffer sTD2DInputs[0]",
        "#define intext sTD2DInputs[0]",
        "#define camara sTD2DInputs[0]",
    ]
    if missing_uniform_decls:
        header.append("// Uniforms parametrizados de JPShader:")
        header.extend(missing_uniform_decls)

    return "\n".join(header) + "\n\n" + body


def create_jpshader_node(
    parent_path="/project1",
    shader_name="starnest",
    node_name=None,
    resolution=(1280, 720),
    node_x=0,
    node_y=0,
):
    """
    Crea en TouchDesigner un nodo COMP de shader GLSL parametrizado a partir de la
    librería JPShaders, incluyendo:
    - Página de parámetros personalizados "JPShaders GLSL" (Sección de Shaders GLSL Nodos).
    - Créditos visibles a JPShaders y al autor del shader.
    - Botón interactivo "Visitar Web Original JPShaders" que abre la web oficial.
    - Sliders de parámetros conectados automáticamente a los uniforms del glslmultiTOP.

    NOTA: Debe ejecutarse dentro del entorno Python de TouchDesigner (o vía TDMCP `execute_code`).
    """
    # `op` y `ui` existen en el scope global de TouchDesigner
    td_op = globals().get("op")
    if td_op is None:
        raise RuntimeError("create_jpshader_node debe invocarse dentro de TouchDesigner (o vía TDMCP execute_code).")

    shader_info = fetch_jpshader(shader_name)
    safe_shader = re.sub(r"[^a-zA-Z0-9_]", "_", shader_info["name"])
    comp_name = node_name or f"jpshader_{safe_shader}"

    parent_comp = td_op(parent_path)
    if parent_comp is None:
        raise ValueError(f"No existe el contenedor padre: {parent_path}")

    existing = parent_comp.op(comp_name)
    if existing is not None:
        existing.destroy()

    # 1. Crear baseCOMP contenedor del nodo JPShader
    comp = parent_comp.create("baseCOMP", comp_name)
    comp.nodeX = node_x
    comp.nodeY = node_y
    comp.color = (0.55, 0.38, 0.96)
    comp.comment = f"JPShaders GLSL: {shader_info['name']} by {shader_info['author']} | fullscreencode.com/jpshadereditor"

    # 2. Crear página "JPShaders GLSL" con Créditos, Botón Web Original y Parámetros
    page = comp.appendCustomPage("JPShaders GLSL")

    p_cred = page.appendStr("Creditos", label="Créditos JPShaders")[0]
    p_cred.val = f"JPShaders ({shader_info['author']}) — fullscreencode.com"
    p_cred.readOnly = True

    p_url = page.appendStr("Weburl", label="URL Shader Original")[0]
    p_url.val = shader_info["webUrl"]
    p_url.readOnly = True
    p_url.startSection = True

    p_btn = page.appendPulse("Visitarweb", label="🌐 Visitar Web Original JPShaders")[0]
    p_btn.help = "Abre el shader original en JPShader Editor (fullscreencode.com/jpshadereditor/)"

    p_docs = page.appendPulse("Visitardocs", label="📖 Docs JPConnect #jpshader")[0]
    p_docs.help = "Abre https://fullscreencode.com/jpconnect/documentacion/#jpshader"

    p_speed = page.appendFloat("Timespeed", label="Velocidad Tiempo")[0]
    p_speed.default = 1.0
    p_speed.val = 1.0
    p_speed.min = 0.0
    p_speed.max = 4.0
    p_speed.startSection = True

    # 3. Crear el glslmultiTOP + textDAT de código + outTOP dentro del componente
    glsl = comp.create("glslmultiTOP", f"glsl_{safe_shader}")
    glsl.nodeX = 0
    glsl.nodeY = 0
    glsl.par.outputresolution = "custom"
    glsl.par.resolutionw = resolution[0]
    glsl.par.resolutionh = resolution[1]
    glsl.par.format = "rgba16float"

    # Escribir el código GLSL transpilado en el DAT pixel dockeado o en un textDAT dedicado
    pixel_dat = comp.op(f"glsl_{safe_shader}_pixel")
    if pixel_dat is None:
        pixel_dat = comp.create("textDAT", f"glsl_{safe_shader}_pixel")
        pixel_dat.nodeX = 0
        pixel_dat.nodeY = -150
        glsl.par.pixeldat = pixel_dat.name
    pixel_dat.text = shader_info["tdGlslCode"]

    out_top = comp.create("outTOP", "out1")
    out_top.nodeX = 220
    out_top.nodeY = 0
    glsl.outputConnectors[0].connect(out_top)

    # 4. Configurar los bloques de uniforms `vec` y crear sliders en la página "JPShaders GLSL"
    uniforms = shader_info.get("uniforms") or {}
    scalar_uniforms = [(k, v) for k, v in uniforms.items() if isinstance(v, (int, float))]

    # Bloque 0 es siempre u_time; bloques 1..N son los parámetros de JPShader
    total_blocks = 1 + len(scalar_uniforms)
    glsl.par.vec.sequence.numBlocks = total_blocks

    glsl.par.vec0name = "u_time"
    glsl.par.vec0valuex.expr = "absTime.seconds * parent().par.Timespeed"

    for idx, (u_name, u_val) in enumerate(scalar_uniforms, start=1):
        # TouchDesigner requiere que los nombres de Custom Par empiecen con mayúscula (solo letras/números)
        clean_par = re.sub(r"[^a-zA-Z0-9]", "", u_name).capitalize()
        if not clean_par or not clean_par[0].isalpha():
            clean_par = f"Par{idx}{clean_par}"
        par_obj = page.appendFloat(clean_par, label=f"{u_name}")[0]
        par_obj.default = float(u_val)
        par_obj.val = float(u_val)
        par_obj.min = 0.0
        par_obj.max = 1.0
        par_obj.clampMin = False
        par_obj.clampMax = False

        setattr(glsl.par, f"vec{idx}name", u_name)
        getattr(glsl.par, f"vec{idx}valuex").expr = f"parent().par.{clean_par}"

    # 5. Crear Parameter Execute DAT para que el botón "Visitar Web Original JPShaders" abra el navegador
    parexec = comp.create("parameterexecuteDAT", "parexec_jpshader_web")
    parexec.nodeX = 220
    parexec.nodeY = -150
    parexec.par.op = ".."
    parexec.par.pars = "Visitarweb Visitardocs"
    parexec.par.onpulse = True
    parexec.text = f'''import webbrowser

def onPulse(par):
    if par.name == 'Visitarweb':
        url = parent().par.Weburl.eval() or "{JPSHADER_WEB_URL}"
        try:
            ui.viewFile(url)
        except Exception:
            webbrowser.open(url)
    elif par.name == 'Visitardocs':
        url = "{JPCONNECT_DOCS_URL}"
        try:
            ui.viewFile(url)
        except Exception:
            webbrowser.open(url)
    return
'''

    glsl.cook(force=True)
    out_top.cook(force=True)
    return {
        "path": comp.path,
        "glsl_path": glsl.path,
        "out_path": out_top.path,
        "shader": shader_info["name"],
        "author": shader_info["author"],
        "credits": shader_info["credits"],
        "webUrl": shader_info["webUrl"],
        "uniforms_bound": [k for k, _ in scalar_uniforms],
    }
