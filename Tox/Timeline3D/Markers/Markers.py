"""
Markers.py — Show Control Marker & Section Engine for Multi-Layer Timeline (TD-MTL)

Manages timeline cue markers:
- Actions: 'Continue', 'Pause' (Wait-for-Go), 'Loop', 'Jump'
- Storage: table_Markers (id, time, name, color, action, target)
- Trigger detection during playback
"""

class Markers:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        self.table = ownerComp.op('table_Markers')
        self._ensure_table_header()
        self._last_checked_time = None
        self._in_loop = False

    def _ensure_table_header(self):
        if self.table is None:
            return
        if self.table.numRows == 0:
            self.table.appendRow(['id', 'time', 'name', 'color', 'action', 'target'])

    def _get_mlt(self):
        return parent.Timeline if hasattr(parent, 'Timeline') else op('/Multi_Layer_Timeline')

    def _get_time_comp(self):
        mlt = self._get_mlt()
        return mlt.op('Timeline3D/Time') if mlt else None

    def _get_timer(self):
        tc = self._get_time_comp()
        return tc.op('timer1') if tc else None

    def _get_current_seconds(self):
        timer = self._get_timer()
        if timer and timer['timer_seconds0'] is not None:
            return float(timer['timer_seconds0'].eval())
        return 0.0

    def AddMarker(self, time=None, name=None, action='Continue', target='', color='1.0 0.8 0.1'):
        """
        Adds a new marker at the given time (or current playhead if None).
        """
        self._ensure_table_header()
        if time is None:
            time = self._get_current_seconds()
        time = round(float(time), 3)

        existing_ids = [int(self.table[r, 'id'].val) for r in range(1, self.table.numRows) if self.table[r, 'id'].val.isdigit()]
        new_id = (max(existing_ids) + 1) if existing_ids else 1

        if not name:
            name = f"Marker_{new_id}"

        self.table.appendRow([str(new_id), str(time), str(name), str(color), str(action), str(target)])
        self.SortMarkers()
        print(f"[Markers] Added '{name}' at {time:.2f}s (Action: {action})")
        return new_id

    def DeleteMarker(self, markerId=None, name=None):
        """
        Deletes a marker by ID or name.
        """
        if self.table is None:
            return False
        for r in range(1, self.table.numRows):
            if (markerId is not None and self.table[r, 'id'].val == str(markerId)) or \
               (name is not None and self.table[r, 'name'].val == str(name)):
                self.table.deleteRow(r)
                print(f"[Markers] Deleted marker ID={markerId} Name={name}")
                return True
        return False

    def ClearMarkers(self):
        """
        Clears all markers.
        """
        if self.table:
            self.table.clear()
            self._ensure_table_header()

    def SortMarkers(self):
        """
        Sorts table rows ascending by time.
        """
        if self.table is None or self.table.numRows <= 2:
            return
        rows = []
        for r in range(1, self.table.numRows):
            try:
                t = float(self.table[r, 'time'].val)
            except Exception:
                t = 0.0
            rows.append((t, [self.table[r, c].val for c in range(self.table.numCols)]))
        rows.sort(key=lambda x: x[0])

        self.table.clear()
        self._ensure_table_header()
        for _, row_vals in rows:
            self.table.appendRow(row_vals)

    def GetMarkers(self):
        """
        Returns list of marker dicts.
        """
        self._ensure_table_header()
        markers = []
        for r in range(1, self.table.numRows):
            try:
                markers.append({
                    'id': self.table[r, 'id'].val,
                    'time': float(self.table[r, 'time'].val),
                    'name': self.table[r, 'name'].val,
                    'color': self.table[r, 'color'].val,
                    'action': self.table[r, 'action'].val,
                    'target': self.table[r, 'target'].val
                })
            except Exception:
                pass
        return markers

    def GetNextMarker(self, curTime=None):
        """
        Returns the closest marker ahead of curTime.
        """
        if curTime is None:
            curTime = self._get_current_seconds()
        markers = self.GetMarkers()
        for m in markers:
            if m['time'] > curTime + 0.02:
                return m
        return None

    def GetPrevMarker(self, curTime=None):
        """
        Returns the closest marker behind curTime.
        """
        if curTime is None:
            curTime = self._get_current_seconds()
        markers = self.GetMarkers()
        for m in reversed(markers):
            if m['time'] < curTime - 0.02:
                return m
        return None

    def JumpToMarker(self, nameOrId):
        """
        Seeks the timeline to the given marker's time using native GotoTime.
        """
        markers = self.GetMarkers()
        target = None
        for m in markers:
            if str(m['id']) == str(nameOrId) or m['name'].lower() == str(nameOrId).lower():
                target = m
                break
        if target:
            tc = self._get_time_comp()
            if tc and hasattr(tc, 'GotoTime'):
                tc.GotoTime(seconds=target['time'])
                print(f"[Markers] Jumped to '{target['name']}' ({target['time']:.2f}s)")
                return True
        return False

    def NextMarker(self):
        m = self.GetNextMarker()
        if m:
            self.JumpToMarker(m['id'])

    def PrevMarker(self):
        m = self.GetPrevMarker()
        if m:
            self.JumpToMarker(m['id'])

    def TriggerGo(self):
        """
        GO Button: Resumes playback from a Pause marker or starts the show.
        """
        timer = self._get_timer()
        mlt = self._get_mlt()
        if not timer:
            return

        if timer['done0'].eval() > 0.5 or timer['ready0'].eval() > 0.5:
            timer.par.start.pulse()
        timer.par.play = True
        try:
            if mlt and hasattr(mlt, 'Callbacks'):
                mlt.Callbacks.OnPlayStateChange(1)
        except Exception:
            pass
        print("[Markers] GO Triggered!")

    def CheckMarkerCrossing(self, prevTime: float, curTime: float):
        """
        Called on playback tick to evaluate marker actions.
        """
        if prevTime is None or curTime <= prevTime:
            return

        # Avoid triggering if user jumped / scrubbed across timeline
        if curTime - prevTime > 0.5:
            return

        timer = self._get_timer()
        tc = self._get_time_comp()
        mlt = self._get_mlt()
        markers = self.GetMarkers()

        for m in markers:
            m_time = m['time']
            if prevTime < m_time <= curTime:
                action = m['action']
                print(f"[Markers] Crossed '{m['name']}' at {m_time:.2f}s (Action: {action})")

                # Send OSC notification
                osc_out = mlt.op('Timeline3D/Input/OSC/oscout1') if mlt else None
                if osc_out and osc_out.par.active.eval():
                    try:
                        osc_out.sendOSC('/timeline/marker_reached', [m['name'], action, m_time])
                    except Exception:
                        pass

                if action == 'Pause':
                    # Wait-for-Go: pause playback exactly at marker
                    if timer:
                        timer.par.play = False
                    if tc and hasattr(tc, 'GotoTime'):
                        tc.GotoTime(seconds=m_time)
                    try:
                        if mlt and hasattr(mlt, 'Callbacks'):
                            mlt.Callbacks.OnPlayStateChange(2)
                    except Exception:
                        pass
                    break

                elif action == 'Loop':
                    # Loop back to target or previous marker
                    target_time = 0.0
                    if m['target']:
                        try:
                            target_time = float(m['target'])
                        except ValueError:
                            for prev_m in markers:
                                if prev_m['name'].lower() == m['target'].lower():
                                    target_time = prev_m['time']
                                    break
                    else:
                        prev_m = self.GetPrevMarker(m_time)
                        if prev_m:
                            target_time = prev_m['time']

                    if tc and hasattr(tc, 'GotoTime'):
                        tc.GotoTime(seconds=target_time)
                    break

                elif action == 'Jump':
                    if m['target']:
                        self.JumpToMarker(m['target'])
                    break
