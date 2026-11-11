"""
saveRestore.py - Unified Show Serializer for TouchDesigner Multi-Layer Timeline (TD-MTL)
Exports and imports entire show definitions to and from clean, human-readable JSON files.
Includes: Timeline duration, FPS, Subrange, View Zoom, Audio Layer, Layer Names, and complete Cue Parameters.
"""

import json
import os
import datetime

class ShowManager:
    def __init__(self, ownerComp):
        self.owner = ownerComp

    def _mlt(self):
        # /Multi_Layer_Timeline
        return parent.Timeline if hasattr(parent, 'Timeline') else op('/Multi_Layer_Timeline')

    def _tl(self):
        # /Multi_Layer_Timeline/Timeline3D
        mlt = self._mlt()
        return mlt.op('Timeline3D') if mlt else None

    def GetShowDict(self):
        mlt = self._mlt()
        tl = self._tl()
        if not mlt or not tl:
            return None

        time_comp = tl.op('Time')
        timer1 = time_comp.op('timer1') if time_comp else None
        cues_comp = tl.op('Cues')
        layers_comp = tl.op('Layers')
        us = tl.op('iparUserSettings')
        at = mlt.op('container_AudioTrack')

        dur = float(us.par.Timelinelength.eval()) if us and hasattr(us.par, 'Timelinelength') else 30.0
        fps = float(us.par.Fps.eval()) if us and hasattr(us.par, 'Fps') else 60.0

        sub_active = bool(time_comp.par.Playsubrange.eval()) if time_comp and hasattr(time_comp.par, 'Playsubrange') else False
        sub_start = float(time_comp.par.Substart.eval()) if time_comp and hasattr(time_comp.par, 'Substart') else 0.0
        sub_end = float(time_comp.par.Subend.eval()) if time_comp and hasattr(time_comp.par, 'Subend') else 10.0
        sub_action = str(time_comp.par.Subendaction.eval()) if time_comp and hasattr(time_comp.par, 'Subendaction') else 'loop'

        rs = mlt.op('container_RangeSlider')
        l_range = float(rs.par.Lrange.eval()) if rs and hasattr(rs.par, 'Lrange') else 0.0
        r_range = float(rs.par.Rrange.eval()) if rs and hasattr(rs.par, 'Rrange') else 1.0

        afile = str(at.par.Audiofile.eval() or '') if at and hasattr(at.par, 'Audiofile') else ''
        avol = round(float(at.par.Volume.eval()), 3) if at and hasattr(at.par, 'Volume') else 1.0
        apan = round(float(at.par.Pan.eval()), 3) if at and hasattr(at.par, 'Pan') else 0.0
        amute = bool(at.par.Mute.eval()) if at and hasattr(at.par, 'Mute') else False
        asolo = bool(at.par.Solo.eval()) if at and hasattr(at.par, 'Solo') else False
        avismode = str(at.par.Vismode.eval() or 'both') if at and hasattr(at.par, 'Vismode') else 'both'
        avisint = round(float(at.par.Visintensity.eval()), 2) if at and hasattr(at.par, 'Visintensity') else 1.0
        aautofit = bool(at.par.Autofit.eval()) if at and hasattr(at.par, 'Autofit') else True

        show = {
            'format': 'TD-MTL-Show',
            'version': '1.0',
            'generator': f'TouchDesigner {app.build} - TD-MTL v0.8',
            'timestamp': datetime.datetime.now().isoformat(),
            'timeline': {
                'duration': dur,
                'fps': fps,
                'subrange': {
                    'active': sub_active,
                    'start': sub_start,
                    'end': sub_end,
                    'action': sub_action
                },
                'view': {
                    'lrange': l_range,
                    'rrange': r_range
                }
            },
            'audio_layer': {
                'audiofile': afile,
                'volume': avol,
                'pan': apan,
                'mute': amute,
                'solo': asolo,
                'vismode': avismode,
                'visintensity': avisint,
                'autofit': aautofit
            },
            'layers': [],
            'cues': []
        }

        # Layers
        if layers_comp:
            layer_items = layers_comp.findChildren(tags=['LayerItem'])
            layer_items.sort(key=lambda x: x.digits)
            for l in layer_items:
                show['layers'].append({
                    'index': l.digits,
                    'name': str(l.par.Layername.eval()) if hasattr(l.par, 'Layername') else f'Layer {l.digits}',
                    'output': str(l.par.Output.eval()) if hasattr(l.par, 'Output') else 'out1',
                    'aspect_ratio': str(l.par.Aspectratio.eval()) if hasattr(l.par, 'Aspectratio') else 'auto',
                    'custom_w': int(l.par.Customw.eval()) if hasattr(l.par, 'Customw') else 1920,
                    'custom_h': int(l.par.Customh.eval()) if hasattr(l.par, 'Customh') else 1080,
                    'fit_mode': str(l.par.Fitmode.eval()) if hasattr(l.par, 'Fitmode') else 'fit'
                })

        # Cues
        cue_items = cues_comp.findChildren(tags=['CueItem']) if cues_comp else []
        cue_items.sort(key=lambda x: (float(x.par.Starttime.eval()), int(x.par.Layer.eval())))
        for c in cue_items:
            cue_dict = {
                'name': c.name,
                'title': str(c.par.Title.eval()) if hasattr(c.par, 'Title') else c.name,
                'type': str(c.par.Type.eval()) if hasattr(c.par, 'Type') else 'Movie',
                'layer': int(c.par.Layer.eval()) if hasattr(c.par, 'Layer') else 0,
                'starttime': round(float(c.par.Starttime.eval()), 4) if hasattr(c.par, 'Starttime') else 0.0,
                'cuelength': round(float(c.par.Cuelength.eval()), 4) if hasattr(c.par, 'Cuelength') else 5.0,
                'fadein': round(float(c.par.Fadeinout1.eval()), 4) if hasattr(c.par, 'Fadeinout1') else 0.5,
                'fadeout': round(float(c.par.Fadeinout2.eval()), 4) if hasattr(c.par, 'Fadeinout2') else 0.5,
                'loop': bool(c.par.Loop.eval()) if hasattr(c.par, 'Loop') else False,
                'imagefile': str(c.par.Imagefile.eval() or '') if hasattr(c.par, 'Imagefile') else '',
                'thumbnail': str(c.par.Thumbnail.eval() or '') if hasattr(c.par, 'Thumbnail') else '',
                'moviespec': str(c.par.Moviespec.eval() or '') if hasattr(c.par, 'Moviespec') else '',
                'trimstart': round(float(c.par.Trimstart.eval()), 4) if hasattr(c.par, 'Trimstart') else 0.0,
                'trimend': round(float(c.par.Trimend.eval()), 4) if hasattr(c.par, 'Trimend') else 0.0,
                'speed': round(float(c.par.Speed.eval()), 4) if hasattr(c.par, 'Speed') else 1.0,
                'text': str(c.par.Text.eval() or '') if hasattr(c.par, 'Text') else '',
                'font': str(c.par.Font.eval() or 'Arial') if hasattr(c.par, 'Font') else 'Arial',
                'fontsize': round(float(c.par.Fontsize.eval()), 2) if hasattr(c.par, 'Fontsize') else 48.0,
                'fontcolor': [
                    round(float(c.par.Fontcolorr.eval()), 3) if hasattr(c.par, 'Fontcolorr') else 1.0,
                    round(float(c.par.Fontcolorg.eval()), 3) if hasattr(c.par, 'Fontcolorg') else 1.0,
                    round(float(c.par.Fontcolorb.eval()), 3) if hasattr(c.par, 'Fontcolorb') else 1.0,
                    round(float(c.par.Fontcolora.eval()), 3) if hasattr(c.par, 'Fontcolora') else 1.0,
                ],
                'commandon': str(c.par.Commandon.eval() or '') if hasattr(c.par, 'Commandon') else '',
                'commandoff': str(c.par.Commandoff.eval() or '') if hasattr(c.par, 'Commandoff') else '',
                'audiofile': str(c.par.Audiofile.eval() or '') if hasattr(c.par, 'Audiofile') else '',
                'audiovolume': round(float(c.par.Audiovolume.eval()), 3) if hasattr(c.par, 'Audiovolume') else 1.0,
                'output': str(c.par.Output.eval()) if hasattr(c.par, 'Output') else 'inherit',
                'fit_mode': str(c.par.Fitmode.eval()) if hasattr(c.par, 'Fitmode') else 'inherit',
                'bgcolor': [
                    round(float(c.par.Backgroundcolorr.eval()), 3) if hasattr(c.par, 'Backgroundcolorr') else 0.0,
                    round(float(c.par.Backgroundcolorg.eval()), 3) if hasattr(c.par, 'Backgroundcolorg') else 0.184,
                    round(float(c.par.Backgroundcolorb.eval()), 3) if hasattr(c.par, 'Backgroundcolorb') else 0.395,
                ],
                'scenecomp': str(c.par.Scenecomp.eval() or '') if hasattr(c.par, 'Scenecomp') else '',
                'lock': bool(c.par.Lock.eval()) if hasattr(c.par, 'Lock') else False,
            }
            show['cues'].append(cue_dict)

        return show

    def LoadShowDict(self, show, clearExisting=True):
        if not isinstance(show, dict):
            raise ValueError("Invalid show data: expected a dictionary")
        if show.get('format') != 'TD-MTL-Show':
            raise ValueError(f"Unknown show format: {show.get('format')}")

        mlt = self._mlt()
        tl = self._tl()
        if not mlt or not tl:
            return False

        proj = tl.op('Project')
        time_comp = tl.op('Time')
        cues_comp = tl.op('Cues')
        layers_comp = tl.op('Layers')
        us = tl.op('iparUserSettings')
        at = mlt.op('container_AudioTrack')
        se = cues_comp.op('SceneEditor').module if cues_comp and cues_comp.op('SceneEditor') else None

        # 1. Timeline Duration & FPS
        t_info = show.get('timeline', {})
        new_dur = float(t_info.get('duration', 30.0))
        if us and hasattr(us.par, 'Timelinelength'):
            us.par.Timelinelength = new_dur
            dur_helper = mlt.op('container_Duration/duration_helper')
            if dur_helper:
                dur_helper.module.sync_ui()

        if us and hasattr(us.par, 'Fps') and 'fps' in t_info:
            us.par.Fps = float(t_info['fps'])

        # 2. Subrange
        sub_info = t_info.get('subrange', {})
        if time_comp and hasattr(time_comp.par, 'Playsubrange'):
            time_comp.par.Playsubrange = bool(sub_info.get('active', False))
            time_comp.par.Substart = float(sub_info.get('start', 0.0))
            time_comp.par.Subend = float(sub_info.get('end', min(10.0, new_dur)))
            time_comp.par.Subendaction = str(sub_info.get('action', 'loop'))

        # 3. View Range
        view_info = t_info.get('view', {})
        rs = mlt.op('container_RangeSlider')
        if rs and hasattr(rs.par, 'Lrange') and hasattr(rs.par, 'Rrange'):
            rs.par.Lrange = float(view_info.get('lrange', 0.0))
            rs.par.Rrange = float(view_info.get('rrange', 1.0))

        # 4. Audio Layer
        al = show.get('audio_layer', {})
        if at:
            afile = str(al.get('audiofile', al.get('file', '')) or '').strip()
            if afile and hasattr(at.par, 'Audiofile'):
                if str(at.par.Audiofile.eval() or '') != afile:
                    at.par.Audiofile = afile
            if 'volume' in al and hasattr(at.par, 'Volume'):
                at.par.Volume = float(al['volume'])
            if 'pan' in al and hasattr(at.par, 'Pan'):
                at.par.Pan = float(al['pan'])
            if 'mute' in al and hasattr(at.par, 'Mute'):
                at.par.Mute = bool(al['mute'])
            if 'solo' in al and hasattr(at.par, 'Solo'):
                at.par.Solo = bool(al['solo'])
            if 'vismode' in al and hasattr(at.par, 'Vismode'):
                at.par.Vismode = str(al['vismode'])
            if 'visintensity' in al and hasattr(at.par, 'Visintensity'):
                at.par.Visintensity = float(al['visintensity'])
            if 'autofit' in al and hasattr(at.par, 'Autofit'):
                at.par.Autofit = bool(al['autofit'])

        # 5. Layer Names and Dual-Output Routing
        if layers_comp:
            for l_data in show.get('layers', []):
                idx = l_data.get('index')
                lname = l_data.get('name')
                l_op = layers_comp.op(f'base_Layer{idx}')
                if l_op:
                    if lname and hasattr(l_op.par, 'Layername'):
                        l_op.par.Layername = lname
                    if 'output' in l_data and hasattr(l_op.par, 'Output'):
                        l_op.par.Output = l_data['output']
                    if 'aspect_ratio' in l_data and hasattr(l_op.par, 'Aspectratio'):
                        l_op.par.Aspectratio = l_data['aspect_ratio']
                    if 'custom_w' in l_data and hasattr(l_op.par, 'Customw'):
                        l_op.par.Customw = int(l_data['custom_w'])
                    if 'custom_h' in l_data and hasattr(l_op.par, 'Customh'):
                        l_op.par.Customh = int(l_data['custom_h'])
                    if 'fit_mode' in l_data and hasattr(l_op.par, 'Fitmode'):
                        l_op.par.Fitmode = l_data['fit_mode']

        # 6. Cues
        if clearExisting and hasattr(proj, 'RemoveCues'):
            proj.RemoveCues(clearAll=True)

        new_cues = []
        for cd in show.get('cues', []):
            new_cue = proj.AddCue()
            if not new_cue:
                continue

            # Populate parameters
            if hasattr(new_cue.par, 'Title') and 'title' in cd:
                new_cue.par.Title = cd['title']
            if hasattr(new_cue.par, 'Type') and 'type' in cd:
                new_cue.par.Type = cd['type']
            if hasattr(new_cue.par, 'Layer') and 'layer' in cd:
                new_cue.par.Layer = int(cd['layer'])
            if hasattr(new_cue.par, 'Starttime') and 'starttime' in cd:
                new_cue.par.Starttime = float(cd['starttime'])
            if hasattr(new_cue.par, 'Cuelength') and 'cuelength' in cd:
                new_cue.par.Cuelength = float(cd['cuelength'])
            if hasattr(new_cue.par, 'Fadeinout1') and 'fadein' in cd:
                new_cue.par.Fadeinout1 = float(cd['fadein'])
            if hasattr(new_cue.par, 'Fadeinout2') and 'fadeout' in cd:
                new_cue.par.Fadeinout2 = float(cd['fadeout'])
            if hasattr(new_cue.par, 'Loop') and 'loop' in cd:
                new_cue.par.Loop = bool(cd['loop'])
            if hasattr(new_cue.par, 'Imagefile') and 'imagefile' in cd:
                new_cue.par.Imagefile = cd['imagefile']
            if hasattr(new_cue.par, 'Moviespec') and 'moviespec' in cd:
                new_cue.par.Moviespec = cd['moviespec']
            if hasattr(new_cue.par, 'Trimstart') and 'trimstart' in cd:
                new_cue.par.Trimstart = float(cd['trimstart'])
            if hasattr(new_cue.par, 'Trimend') and 'trimend' in cd:
                new_cue.par.Trimend = float(cd['trimend'])
            if hasattr(new_cue.par, 'Speed') and 'speed' in cd:
                new_cue.par.Speed = float(cd['speed'])
            if hasattr(new_cue.par, 'Text') and 'text' in cd:
                new_cue.par.Text = cd['text']
            if hasattr(new_cue.par, 'Font') and 'font' in cd:
                new_cue.par.Font = cd['font']
            if hasattr(new_cue.par, 'Fontsize') and 'fontsize' in cd:
                new_cue.par.Fontsize = float(cd['fontsize'])
            if 'fontcolor' in cd and hasattr(new_cue.par, 'Fontcolorr'):
                fc = cd['fontcolor']
                if len(fc) >= 4:
                    new_cue.par.Fontcolorr = fc[0]
                    new_cue.par.Fontcolorg = fc[1]
                    new_cue.par.Fontcolorb = fc[2]
                    new_cue.par.Fontcolora = fc[3]
            if hasattr(new_cue.par, 'Commandon') and 'commandon' in cd:
                new_cue.par.Commandon = cd['commandon']
            if hasattr(new_cue.par, 'Commandoff') and 'commandoff' in cd:
                new_cue.par.Commandoff = cd['commandoff']
            if hasattr(new_cue.par, 'Audiofile') and 'audiofile' in cd:
                new_cue.par.Audiofile = cd['audiofile']
            if hasattr(new_cue.par, 'Audiovolume') and 'audiovolume' in cd:
                new_cue.par.Audiovolume = float(cd['audiovolume'])
            if hasattr(new_cue.par, 'Output') and 'output' in cd:
                new_cue.par.Output = cd['output']
            if hasattr(new_cue.par, 'Fitmode') and 'fit_mode' in cd:
                new_cue.par.Fitmode = cd['fit_mode']
            if 'bgcolor' in cd and hasattr(new_cue.par, 'Backgroundcolorr'):
                bg = cd['bgcolor']
                if len(bg) >= 3:
                    new_cue.par.Backgroundcolorr = bg[0]
                    new_cue.par.Backgroundcolorg = bg[1]
                    new_cue.par.Backgroundcolorb = bg[2]
            if hasattr(new_cue.par, 'Scenecomp') and 'scenecomp' in cd:
                new_cue.par.Scenecomp = cd['scenecomp']
            if hasattr(new_cue.par, 'Lock') and 'lock' in cd:
                new_cue.par.Lock = bool(cd['lock'])
            if hasattr(new_cue.par, 'Thumbnail') and cd.get('thumbnail'):
                new_cue.par.Thumbnail = cd['thumbnail']

            if se is not None:
                try:
                    se.refresh_cue_thumb(new_cue)
                except Exception:
                    pass

            new_cues.append(new_cue)

        # 7. Update bounds and playback
        if hasattr(tl.op('RenderPick'), 'UpdateAllBounds'):
            tl.op('RenderPick').UpdateAllBounds()

        pb = tl.op('Playback')
        if pb and hasattr(pb.op('playback_engine').module, 'rebuild'):
            pb.op('playback_engine').module.rebuild()

        if time_comp and hasattr(time_comp, 'GotoTime'):
            time_comp.GotoTime(seconds=0.0)

        if pb and hasattr(pb.op('playback_engine').module, 'update_playback'):
            pb.op('playback_engine').module.update_playback()

        print(f"Show successfully loaded! {len(new_cues)} cues restored.")
        return True

    def ExportShowJSON(self, filepath=None):
        if not filepath:
            filepath = ui.chooseFile(load=False, fileTypes=['json'], defaultFile='show_export.json', title='Export Show JSON')
        if not filepath:
            return False

        if not os.path.isabs(filepath):
            filepath = os.path.normpath(os.path.join(project.folder, filepath))

        show = self.GetShowDict()
        if not show:
            print("Failed to build show dictionary")
            return False

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(show, f, indent=2)

        print(f"Show successfully exported to: {filepath}")
        return filepath

    def ImportShowJSON(self, filepath=None, clearExisting=True):
        if not filepath:
            filepath = ui.chooseFile(load=True, fileTypes=['json'], title='Import Show JSON')
        if not filepath:
            return False

        if not os.path.isabs(filepath):
            filepath = os.path.normpath(os.path.join(project.folder, filepath))

        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False

        with open(filepath, 'r', encoding='utf-8') as f:
            show = json.load(f)

        return self.LoadShowDict(show, clearExisting=clearExisting)
