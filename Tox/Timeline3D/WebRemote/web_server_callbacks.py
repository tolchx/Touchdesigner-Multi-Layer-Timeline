"""
web_server_callbacks.py — Web Server Callbacks for TD-MTL Web Remote

Handles HTTP requests (HTML5 app, JSON REST API) and real-time WebSockets
for tablet/iPad remote control.
"""

import json
import os
from typing import Dict, Any

_connected_clients = set()

def _get_mlt():
    return parent.Timeline if hasattr(parent, 'Timeline') else op('/Multi_Layer_Timeline')

def _get_time_comp():
    mlt = _get_mlt()
    return mlt.op('Timeline3D/Time') if mlt else None

def _get_timer():
    tc = _get_time_comp()
    return tc.op('timer1') if tc else None

def _get_markers_ext():
    mlt = _get_mlt()
    m = mlt.op('Timeline3D/Markers') if mlt else None
    return m.ext.Markers if (m and hasattr(m.ext, 'Markers')) else None

def _format_timecode(seconds: float, rate: float = 60.0) -> str:
    total_frames = int(seconds * rate)
    frames = total_frames % int(rate)
    total_sec = int(seconds)
    secs = total_sec % 60
    mins = (total_sec // 60) % 60
    hours = total_sec // 3600
    return f"{hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}"

def get_status_dict() -> Dict[str, Any]:
    mlt = _get_mlt()
    timer = _get_timer()
    markers_ext = _get_markers_ext()

    if not timer:
        return {'state_str': 'STOPPED', 'timecode': '00:00:00:00', 'seconds': 0.0, 'fraction': 0.0}

    is_playing = bool(timer.par.play.eval())
    is_ready = float(timer['ready0'].eval()) > 0.5 if timer['ready0'] is not None else False
    is_done = float(timer['done0'].eval()) > 0.5 if timer['done0'] is not None else False
    cur_sec = float(timer['timer_seconds0'].eval()) if timer['timer_seconds0'] is not None else 0.0
    tot_len = float(timer.par.length.eval()) if hasattr(timer.par, 'length') else 30.0
    frac = cur_sec / max(0.001, tot_len)

    if is_playing:
        state_str = "PLAYING"
    elif is_ready or is_done:
        state_str = "STOPPED"
    else:
        state_str = "PAUSED"

    fps = me.time.rate if hasattr(me, 'time') and hasattr(me.time, 'rate') else 60.0
    tc_str = _format_timecode(cur_sec, fps)

    # Current marker
    cur_marker_name = "None"
    markers_list = []
    if markers_ext:
        prev_m = markers_ext.GetPrevMarker(cur_sec + 0.01)
        if prev_m:
            cur_marker_name = prev_m['name']
        markers_list = markers_ext.GetMarkers()

    # Layers info
    layers_list = []
    layers_comp = mlt.op('Timeline3D/Layers') if mlt else None
    if layers_comp:
        for idx in range(5):
            lop = layers_comp.op(f'base_Layer{idx}')
            if lop:
                layers_list.append({
                    'index': idx,
                    'name': str(lop.par.Layername.eval() if hasattr(lop.par, 'Layername') else f'Layer {idx}'),
                    'opacity': float(lop.par.Opacity.eval() if hasattr(lop.par, 'Opacity') else 1.0),
                    'mute': bool(lop.par.Mute.eval() if hasattr(lop.par, 'Mute') else False)
                })

    return {
        'type': 'status',
        'state_str': state_str,
        'timecode': tc_str,
        'seconds': round(cur_sec, 2),
        'fraction': round(frac, 4),
        'duration': round(tot_len, 2),
        'current_marker': cur_marker_name,
        'markers': markers_list,
        'layers': layers_list
    }

def execute_action(action_data: Dict[str, Any]):
    action = action_data.get('action', '').lower()
    timer = _get_timer()
    tc = _get_time_comp()
    mlt = _get_mlt()
    markers_ext = _get_markers_ext()

    if not timer:
        return

    if action in ['go', 'play']:
        if markers_ext:
            markers_ext.TriggerGo()
        else:
            if timer['done0'].eval() > 0.5 or timer['ready0'].eval() > 0.5:
                timer.par.start.pulse()
            timer.par.play = True
            try: mlt.Callbacks.OnPlayStateChange(1)
            except Exception: pass

    elif action == 'pause':
        timer.par.play = False
        try: mlt.Callbacks.OnPlayStateChange(2)
        except Exception: pass

    elif action == 'stop':
        timer.par.play = False
        if tc and hasattr(tc, 'GotoTime'):
            tc.GotoTime(seconds=0.0)
        else:
            timer.par.initialize.pulse()
        try: mlt.Callbacks.OnPlayStateChange(0)
        except Exception: pass

    elif action == 'next_marker':
        if markers_ext:
            markers_ext.NextMarker()

    elif action == 'prev_marker':
        if markers_ext:
            markers_ext.PrevMarker()

    elif action == 'jump_marker':
        target = action_data.get('target', '')
        if markers_ext and target:
            markers_ext.JumpToMarker(target)

    elif action == 'goto_fraction':
        frac = float(action_data.get('fraction', 0.0))
        tot_len = float(timer.par.length.eval()) if hasattr(timer.par, 'length') else 30.0
        if tc and hasattr(tc, 'GotoTime'):
            tc.GotoTime(seconds=frac * tot_len)

    elif action == 'layer_opacity':
        l_idx = int(action_data.get('layer', 0))
        val = float(action_data.get('value', 1.0))
        layers_comp = mlt.op('Timeline3D/Layers') if mlt else None
        if layers_comp:
            lop = layers_comp.op(f'base_Layer{l_idx}')
            if lop and hasattr(lop.par, 'Opacity'):
                lop.par.Opacity = max(0.0, min(1.0, val))

    elif action == 'layer_mute':
        l_idx = int(action_data.get('layer', 0))
        state = bool(action_data.get('state', False))
        layers_comp = mlt.op('Timeline3D/Layers') if mlt else None
        if layers_comp:
            lop = layers_comp.op(f'base_Layer{l_idx}')
            if lop and hasattr(lop.par, 'Mute'):
                lop.par.Mute = state

def onHTTPRequest(dat: 'webserverDAT', request: Dict[str, Any], 
                  response: Dict[str, Any]) -> Dict[str, Any]:
    uri = request.get('uri', '/')
    method = request.get('method', 'GET').upper()

    if uri in ['/', '/index.html'] and method == 'GET':
        html_dat = dat.parent().op('web_remote_app')
        if html_dat:
            content = html_dat.text
        else:
            base_dir = project.folder
            html_path = os.path.join(base_dir, 'Tox', 'Timeline3D', 'WebRemote', 'web_remote_app.html')
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()

        response['statusCode'] = 200
        response['statusReason'] = 'OK'
        response['content-type'] = 'text/html; charset=utf-8'
        response['data'] = content
        return response

    elif uri == '/api/status' and method == 'GET':
        status = get_status_dict()
        response['statusCode'] = 200
        response['statusReason'] = 'OK'
        response['content-type'] = 'application/json'
        response['data'] = json.dumps(status)
        return response

    elif uri == '/api/action' and method == 'POST':
        try:
            body = request.get('data', '{}')
            if isinstance(body, bytes):
                body = body.decode('utf-8')
            data = json.loads(body)
            execute_action(data)
            response['statusCode'] = 200
            response['statusReason'] = 'OK'
            response['content-type'] = 'application/json'
            response['data'] = json.dumps({'success': True})
        except Exception as e:
            response['statusCode'] = 400
            response['statusReason'] = 'Bad Request'
            response['data'] = json.dumps({'error': str(e)})
        return response

    response['statusCode'] = 404
    response['statusReason'] = 'Not Found'
    response['data'] = 'Not Found'
    return response

def onWebSocketOpen(dat: 'webserverDAT', client: str, uri: str):
    global _connected_clients
    _connected_clients.add(client)
    # Send immediate state on connect
    status = get_status_dict()
    dat.webSocketSendText(client, json.dumps(status))

def onWebSocketClose(dat: 'webserverDAT', client: str):
    global _connected_clients
    if client in _connected_clients:
        _connected_clients.remove(client)

def onWebSocketReceiveText(dat: 'webserverDAT', client: str, data: str):
    try:
        payload = json.loads(data)
        execute_action(payload)
        # Broadcast updated state
        broadcast_status(dat)
    except Exception as e:
        print(f'[WebRemote WS Error]: {e}')

def broadcast_status(dat: 'webserverDAT'):
    global _connected_clients
    if not _connected_clients:
        return
    status_json = json.dumps(get_status_dict())
    dead_clients = []
    for client in _connected_clients:
        try:
            dat.webSocketSendText(client, status_json)
        except Exception:
            dead_clients.append(client)
    for c in dead_clients:
        _connected_clients.remove(c)
