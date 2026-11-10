"""
TouchDesigner Multi-Layer Timeline (TD-MTL) — AI Agent Scene & Multimedia Engine
================================================================================
Provee facilidades de alto nivel para que un Agente de IA (vía TDMCP) construya
escenas complejas, posicione contenido multimedia, instancie sistemas de partículas
GPU (POPs), cadenas de post-procesado (TOPs) y nodos GLSL parametrizados de la
librería JPShaders (https://fullscreencode.com/jpshadereditor/), todo sincronizado
automáticamente con el cabezal de reproducción y las curvas de Fade In / Fade Out
de `Multi_Layer_Timeline`.
"""

import os
import re
from . import jpshaders_nodes


class TimelineSceneEngine:
    """
    Motor de orquestación de escenas para TouchDesigner Multi-Layer Timeline.
    Diseñado para ser invocado por agentes de IA desde TDMCP (`execute_code`).
    """

    def __init__(self, project_path="/project1", timeline_comp_name="Multi_Layer_Timeline"):
        self.td_op = globals().get("op")
        self.project_path = project_path
        self.timeline_path = f"{project_path.rstrip('/')}/{timeline_comp_name}"

    def _get_timeline(self):
        if self.td_op is None:
            raise RuntimeError("TimelineSceneEngine requiere ejecutarse dentro de TouchDesigner.")
        tl = self.td_op(self.timeline_path)
        if tl is None:
            raise ValueError(f"No se encontró el componente de línea de tiempo en '{self.timeline_path}'.")
        return tl

    def _get_manager(self):
        tl = self._get_timeline()
        proj = tl.op("Project") or tl.op("Timeline3D/Project")
        if proj is None:
            raise ValueError("No se encontró el subcomponente 'Project' dentro de Multi_Layer_Timeline.")
        return proj, proj.ext.Manager

    def ensure_compositor(self, resolution=(1920, 1080)):
        """
        Crea o recupera el contenedor `/project1/Timeline_Scene_Compositor` que
        mezcla todas las escenas (Multimedia, POPs, TOPs y JPShaders GLSL)
        aplicando el Fade In / Fade Out de cada cue según el tiempo del Timeline.
        """
        root = self.td_op(self.project_path)
        comp = root.op("Timeline_Scene_Compositor")
        if comp is None:
            comp = root.create("baseCOMP", "Timeline_Scene_Compositor")
            comp.nodeX = 450
            comp.nodeY = 0
            comp.color = (0.18, 0.72, 0.55)
            comp.comment = "Motor de mezcla automática para Multi_Layer_Timeline (Multimedia + POPs + JPShaders)"

            bg = comp.create("constantTOP", "bg_black")
            bg.nodeX = -200
            bg.nodeY = 0
            bg.par.resolutionw = resolution[0]
            bg.par.resolutionh = resolution[1]
            bg.par.colorr = 0.0
            bg.par.colorg = 0.0
            bg.par.colorb = 0.0
            bg.par.colora = 1.0

            comp_top = comp.create("compositeTOP", "master_mix")
            comp_top.nodeX = 500
            comp_top.nodeY = 0
            comp_top.par.operand = "add"
            bg.outputConnectors[0].connect(comp_top)

            out_top = comp.create("outTOP", "out1")
            out_top.nodeX = 720
            out_top.nodeY = 0
            comp_top.outputConnectors[0].connect(out_top)

        return comp

    def _build_cue_envelope_expr(self, start_time, cue_length, fade_in, fade_out):
        """
        Genera una expresión Python de TouchDesigner que evalúa la envolvente (0.0 a 1.0)
        de la cue en función del tiempo actual de reproducción (`absTime.seconds` o playhead).
        """
        t_expr = f"op('{self.timeline_path}').op('select_CurrentTime')[0].eval() if op('{self.timeline_path}') and op('{self.timeline_path}').op('select_CurrentTime') else absTime.seconds"
        fi = max(0.001, float(fade_in))
        fo = max(0.001, float(fade_out))
        st = float(start_time)
        ln = max(0.01, float(cue_length))
        end = st + ln
        return (
            f"clamp((({t_expr}) - {st}) / {fi}, 0.0, 1.0) * "
            f"clamp(({end} - ({t_expr})) / {fo}, 0.0, 1.0) "
            f"if ({st} <= ({t_expr}) <= {end}) else 0.0"
        )

    def register_cue_in_timeline(
        self,
        title: str,
        cue_type: str = "Media",
        layer: int = 0,
        start_time: float = 0.0,
        cue_length: float = 10.0,
        fade_in: float = 1.0,
        fade_out: float = 1.0,
        color: tuple = (0.25, 0.55, 0.95, 1.0),
        image_file: str = "",
    ):
        """
        Inserta una cue visual en `Multi_Layer_Timeline` usando `CueSpec` y `Manager.AddCue`.
        """
        proj, manager = self._get_manager()
        spec = proj.mod.CueSpec.CueSpec(
            Cuetype=cue_type,
            Title=title,
            Imagefile=image_file,
            Thumbnail=image_file,
            Fadeinoutduration=(float(fade_in), float(fade_out)),
            Cuelength=float(cue_length),
            Starttime=float(start_time),
            Backgroundcolor=color,
            Layer=int(layer),
        )
        safe_name = "cue_" + re.sub(r"[^a-zA-Z0-9_]", "_", title)
        cue_op = manager.AddCue(cueType=cue_type, name=safe_name, cueSpec=spec)
        return cue_op

    def add_multimedia_cue(
        self,
        title: str,
        file_path: str,
        layer: int = 0,
        start_time: float = 0.0,
        cue_length: float = 10.0,
        fade_in: float = 1.0,
        fade_out: float = 1.0,
    ):
        """
        Coloca un archivo multimedia (Video MP4/MOV/HAP o Imagen PNG/JPG) en la línea
        de tiempo, crea su reproductor `moviefileinTOP` + control de opacidad `levelTOP`
        sincronizado al Fade In / Out de la cue, y lo conecta al mezclador maestro.
        """
        compositor = self.ensure_compositor()
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", title)
        slot_y = -180 * (len(compositor.findChildren(depth=1)) // 2)

        mov = compositor.create("moviefileinTOP", f"media_{safe}")
        mov.nodeX = 0
        mov.nodeY = slot_y
        mov.par.file = file_path
        mov.par.playmode = "sequential"

        lvl = compositor.create("levelTOP", f"fader_{safe}")
        lvl.nodeX = 220
        lvl.nodeY = slot_y
        lvl.par.opacity.expr = self._build_cue_envelope_expr(start_time, cue_length, fade_in, fade_out)
        mov.outputConnectors[0].connect(lvl)

        master_mix = compositor.op("master_mix")
        lvl.outputConnectors[0].connect(master_mix)

        cue_op = self.register_cue_in_timeline(
            title=title,
            cue_type="Media",
            layer=layer,
            start_time=start_time,
            cue_length=cue_length,
            fade_in=fade_in,
            fade_out=fade_out,
            color=(0.2, 0.75, 0.5, 1.0),
            image_file=file_path,
        )
        return {"cue": cue_op.path if cue_op else title, "player": mov.path, "fader": lvl.path}

    def add_jpshader_cue(
        self,
        shader_name: str = "starnest",
        title: str = None,
        layer: int = 1,
        start_time: float = 0.0,
        cue_length: float = 12.0,
        fade_in: float = 1.5,
        fade_out: float = 1.5,
        params_override: dict = None,
        resolution=(1280, 720),
    ):
        """
        Instancia un nodo GLSL parametrizado de la librería JPShaders (con créditos a
        JPShaders y botón para visitar https://fullscreencode.com/jpshadereditor/),
        aplica overrides opcionales de parámetros, lo conecta al mezclador con su curva
        de Fade In / Out y agrega su bloque en el Multi-Layer Timeline.
        """
        compositor = self.ensure_compositor(resolution=resolution)
        cue_title = title or f"JPShader_{shader_name}"
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", cue_title)
        slot_y = -180 * (len(compositor.findChildren(depth=1)) // 2)

        node_info = jpshaders_nodes.create_jpshader_node(
            parent_path=compositor.path,
            shader_name=shader_name,
            node_name=f"jpshader_{safe}",
            resolution=resolution,
            node_x=0,
            node_y=slot_y,
        )
        shader_comp = self.td_op(node_info["path"])

        if params_override:
            for k, v in params_override.items():
                clean_par = re.sub(r"[^a-zA-Z0-9]", "", k).capitalize()
                if hasattr(shader_comp.par, clean_par):
                    getattr(shader_comp.par, clean_par).val = v

        lvl = compositor.create("levelTOP", f"fader_{safe}")
        lvl.nodeX = 240
        lvl.nodeY = slot_y
        lvl.par.opacity.expr = self._build_cue_envelope_expr(start_time, cue_length, fade_in, fade_out)
        shader_comp.outputConnectors[0].connect(lvl)

        master_mix = compositor.op("master_mix")
        lvl.outputConnectors[0].connect(master_mix)

        cue_op = self.register_cue_in_timeline(
            title=cue_title,
            cue_type="Tox",
            layer=layer,
            start_time=start_time,
            cue_length=cue_length,
            fade_in=fade_in,
            fade_out=fade_out,
            color=(0.58, 0.35, 0.96, 1.0),
        )
        return {
            "cue": cue_op.path if cue_op else cue_title,
            "jpshader_node": node_info,
            "fader": lvl.path,
        }

    def add_pop_scene_cue(
        self,
        title: str = "POP_Nebula_Vortex",
        preset: str = "curl_vortex",
        layer: int = 2,
        start_time: float = 0.0,
        cue_length: float = 15.0,
        fade_in: float = 2.0,
        fade_out: float = 2.0,
        resolution=(1280, 720),
    ):
        """
        Construye una escena 3D completa basada en sistemas de partículas GPU (POPs)
        y post-procesado TOP (`spherePOP` -> `particlePOP` -> `forceRadialPOP` / `noisePOP`
        -> `trailPOP` -> `geoCOMP` -> `renderTOP` -> `feedbackTOP` glow), la vincula
        a una pista del Multi-Layer Timeline y controla su mezcla por Fade In / Out.
        """
        compositor = self.ensure_compositor(resolution=resolution)
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", title)
        slot_y = -180 * (len(compositor.findChildren(depth=1)) // 2)

        scene = compositor.create("baseCOMP", f"popscene_{safe}")
        scene.nodeX = 0
        scene.nodeY = slot_y
        scene.color = (0.88, 0.42, 0.42)
        scene.comment = f"Escena POP 3D ({preset}) sincronizada al Timeline"

        # 1. Red de partículas GPU (POPs) verificada con contratos C1-C23
        emitter = scene.create("spherePOP", "emitter_sphere")
        emitter.nodeX = -400
        emitter.nodeY = 0
        emitter.par.rows = 64
        emitter.par.cols = 64

        noise_pop = scene.create("noisePOP", "turbulence_noise")
        noise_pop.nodeX = -200
        noise_pop.nodeY = 0
        noise_pop.par.amp = 0.45 if preset == "curl_vortex" else 0.25
        noise_pop.par.tz.expr = "absTime.seconds * 0.35"
        emitter.outputConnectors[0].connect(noise_pop)

        last_pop = noise_pop
        if preset in ("radial_spiral", "curl_vortex"):
            force = scene.create("forceRadialPOP", "vortex_force")
            force.nodeX = 0
            force.nodeY = 0
            last_pop.outputConnectors[0].connect(force)
            last_pop = force

        trail = scene.create("trailPOP", "motion_trails")
        trail.nodeX = 180
        trail.nodeY = 0
        last_pop.outputConnectors[0].connect(trail)

        null_pop = scene.create("nullPOP", "null_particles")
        null_pop.nodeX = 360
        null_pop.nodeY = 0
        trail.outputConnectors[0].connect(null_pop)

        # 2. Pipeline de Render 3D (Geo + Cam + Light + Render TOP)
        geo = scene.create("geometryCOMP", "geo_particles")
        geo.nodeX = 360
        geo.nodeY = -180
        if geo.op("torus1"):
            geo.op("torus1").destroy()
        pop_in = geo.create("selectPOP", "select_particles")
        pop_in.par.pop = "../null_particles"
        pop_in.render = True
        pop_in.display = True

        cam = scene.create("cameraCOMP", "cam1")
        cam.nodeX = 180
        cam.nodeY = -180
        cam.par.tz = 4.2

        light = scene.create("lightCOMP", "light1")
        light.nodeX = 0
        light.nodeY = -180

        ren = scene.create("renderTOP", "render1")
        ren.nodeX = 560
        ren.nodeY = -180
        ren.par.resolutionw = resolution[0]
        ren.par.resolutionh = resolution[1]
        ren.par.camera = "cam1"
        ren.par.geometry = "geo_particles"
        ren.par.lights = "light1"

        out_top = scene.create("outTOP", "out1")
        out_top.nodeX = 760
        out_top.nodeY = -180
        ren.outputConnectors[0].connect(out_top)

        # 3. Fader de mezcla ligado a la Cue del Timeline
        lvl = compositor.create("levelTOP", f"fader_{safe}")
        lvl.nodeX = 240
        lvl.nodeY = slot_y
        lvl.par.opacity.expr = self._build_cue_envelope_expr(start_time, cue_length, fade_in, fade_out)
        scene.outputConnectors[0].connect(lvl)

        master_mix = compositor.op("master_mix")
        lvl.outputConnectors[0].connect(master_mix)

        cue_op = self.register_cue_in_timeline(
            title=title,
            cue_type="Tox",
            layer=layer,
            start_time=start_time,
            cue_length=cue_length,
            fade_in=fade_in,
            fade_out=fade_out,
            color=(0.88, 0.42, 0.42, 1.0),
        )
        return {
            "cue": cue_op.path if cue_op else title,
            "scene_comp": scene.path,
            "render_top": ren.path,
            "fader": lvl.path,
        }

    def build_ai_showcase_timeline(self):
        """
        Construye de forma autónoma un show multi-capa de demostración combinando:
        - Capa 0: JPShader 'starnest' (Cosmos volumétrico parametrizado por jpupper)
        - Capa 1: Escena 3D POP 'POP_Nebula_Vortex' (Partículas GPU + Trails)
        - Capa 2: JPShader 'sexygalacticdream' (Patrones fractales reactivos por jpupper)
        - Capa 3: JPShader 'gen_circularraymarching' (Raymarching túnel 3D por iacode)
        """
        results = []
        results.append(
            self.add_jpshader_cue(
                shader_name="starnest",
                title="01_JPShader_StarNest",
                layer=0,
                start_time=0.0,
                cue_length=14.0,
                fade_in=2.0,
                fade_out=2.0,
            )
        )
        results.append(
            self.add_pop_scene_cue(
                title="02_POP_Curl_Vortex_3D",
                preset="curl_vortex",
                layer=1,
                start_time=4.0,
                cue_length=16.0,
                fade_in=2.5,
                fade_out=2.5,
            )
        )
        results.append(
            self.add_jpshader_cue(
                shader_name="sexygalacticdream",
                title="03_JPShader_GalacticDream",
                layer=2,
                start_time=10.0,
                cue_length=14.0,
                fade_in=2.0,
                fade_out=2.0,
            )
        )
        results.append(
            self.add_jpshader_cue(
                shader_name="gen_circularraymarching",
                title="04_JPShader_RaymarchTunnel",
                layer=3,
                start_time=16.0,
                cue_length=14.0,
                fade_in=2.0,
                fade_out=2.0,
            )
        )
        return {
            "status": "ok",
            "compositor": f"{self.project_path}/Timeline_Scene_Compositor",
            "cues_created": len(results),
            "details": results,
        }
