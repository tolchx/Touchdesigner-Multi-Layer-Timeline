"""
# events - a list of named tuples with the fields listed below.
# eventsPrev - a list of events holding the eventsPrev values.
#
#	u				- The selection u coordinate.			(float)
#	v				- The selection v coordinate.			(float)
#	select			- True when a selection is ongoing.		(bool)
#	selectStart		- True at the start of a selection.		(bool)
#	selectEnd		- True at the end of a selection.		(bool)
#	selectedOp		- First picked operator.				(OP)
#	selectedTexture	- Texture coordinate of seleectedOp.	(Position)
#	pickOp			- Currently picked operator.			(OP)
#	pos				- 3D position of picked point.			(Position)
#	texture			- Texture coordinate of picked point.	(Position)
#	color			- Color of picked point.				(4-tuple)
#	normal			- Geometry normal of picked point.		(Vector)
#	depth			- Post projection space depth.			(float)
#	instanceId		- Instance ID of the object.			(int)
#	row				- The row associated with this event	(float)
#	inValues		- Dictionary of input DAT strings for the given row, where keys are column headers. (dict)
#	c


"""
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
from collections import namedtuple
class RenderPick:
	"""
	RenderPick description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp

		self.AllCueBounds = self.myOp.fetch('AllCueBounds', dict(), storeDefault=True)
		self.SelectedBounds = None
		
		self.InstanceId = -1

		self.ObjectPrefix = {
			'Cue' : 'base_Cue',
			'Layer' : 'base_Layer',
			'Bg' : 'geo_Timeline_'
		}

		self.PageScope = {
			'Cue' : 'Settings',
			'Layer' : 'Layer',
			'Bg' : 'Settings Camera Project'
		}

		self.RickClickCallbackInfo = {
			'Tag' : None,
			'Op' : None
		}

		self.PreviousTag = ''

		self.System = ipar.SystemSettings
		self.User = ipar.UserSettings

		self.StartTimes = []
		self.Durations = []
		self.EndTimes = []
		self.InitialLayers = []

		self.ClickPosition = tdu.Position()
		self.ClickMapUV = tdu.Position()

		self.MainOp = parent.Main
		self.MasterComp = parent.Timeline

		self.UserSettingsOp = self.MainOp.op('iparUserSettings')
		self.ParComp = self.MainOp.par.Parametercomp.eval()
		self.KeyboardOp = parent.Main.op('Input/Keyboard')
		self.TimeComp = parent.Main.op('Time')
		self.Timer = self.TimeComp.op('timer1')
		self.CueDB = parent.Main.op('Cues/null_CueDB')

		self.CanDragVertically = True
		self.CanStretch = False
		self.CanStretchLeft = False
		self.CanTranslate = True

		self.VerticalDragRegion = (.2, .8)
		self.HorizontalStretchRegion = 1
		self.LayerIncrementThreshold = .0
		# in pixels, the amount of screen space from the right edge of a cue, that can be selected for edge grab.
		self.edgeGrabWidthInPixels = 10

		self.ClickType = 0
		self.MouseOp = self.MainOp.op('Input/Mouse')
		self.BoxSelectOp = self.MainOp.op('Canvas/geo_BoxSelect')

		self.currentClickPosition = None

		self.DeleteRightPar = parent.Main.op('Cues/base_Snapping/base_GetLeftSideOfStart/delete_Right_Of').par.value1
		self.DeleteLeftPar = parent.Main.op('Cues/base_Snapping/base_GetRightSideOfStart/delete_Left_Of').par.value1
		self.DeleteRightPar2 = parent.Main.op('Cues/base_Snapping/base_GetLeftSideOfEnd/delete_Right_Of2').par.value1
		self.DeleteLeftPar2 = parent.Main.op('Cues/base_Snapping/base_GetRightSideOfEnd/delete_Left_Of2').par.value1

		self.ProposedStartPar = parent.Main.op('Cues/base_Snapping/constant_ProposedStartTime').par.value0
		self.ProposedEndPar = parent.Main.op('Cues/base_Snapping/constant_ProposedStartTime').par.value1

	def _GetSnapThreshold(self):
		"""Returns snapping threshold in world time (seconds), matching ~8 screen pixels."""
		try:
			val = abs(ext.Transformer.ScreenSpaceToWorldspace(x=100, y=0, offset=(8, 0)).x)
			if 0.001 < val < 1.5:
				return val
		except Exception:
			pass
		return 0.15

	def _GetSnapTargets(self, exclude_selection=True):
		"""Collects snap target times (seconds) across the timeline."""
		targets = [0.0]
		# Playhead
		try:
			if self.Timer is not None:
				targets.append(float(self.Timer['timer_seconds0']))
		except Exception:
			pass
		# Subrange markers if active
		try:
			if self.User.Enablesubrange.eval():
				targets.append(float(self.User.Subrangein.eval()))
				targets.append(float(self.User.Subrangeout.eval()))
		except Exception:
			pass
		# Other cues (start and end times)
		try:
			all_cues = self.MainOp.op('Project').GetOps(cue=True)
			sel = ext.Selection.Selection if exclude_selection else []
			for c in all_cues:
				if c not in sel:
					targets.append(float(c.par.Starttime.eval()))
					targets.append(float(c.par.Computedendtime.eval()))
		except Exception:
			pass
		return sorted(list(set(targets)))

	def _CalculateSnap(self, proposed_start, cue):
		"""Snaps proposed cue start time to nearby targets within ~12 screen pixels."""
		if not ipar.UserSettings.Snapping.eval():
			self._HideSnapLine()
			return proposed_start
		if self.KeyboardOp.par.Ctrl.eval() or self.KeyboardOp.par.Alt.eval() or self.KeyboardOp.par.Ctrlalt.eval():
			self._HideSnapLine()
			return proposed_start

		thresh = self._GetSnapThreshold()
		targets = self._GetSnapTargets(exclude_selection=True)
		dur = cue.par.Cuelength.eval()
		proposed_end = proposed_start + dur

		best_target = None
		best_diff = thresh + 1.0
		best_start = proposed_start

		for t in targets:
			# Snap start to target
			d_start = abs(t - proposed_start)
			if d_start < thresh and d_start < best_diff:
				best_diff = d_start
				best_start = t
				best_target = t
			# Snap end to target
			d_end = abs(t - proposed_end)
			if d_end < thresh and d_end < best_diff:
				best_diff = d_end
				best_start = max(0.0, t - dur)
				best_target = t

		if best_target is not None:
			self._ShowSnapLine(best_target)
			return best_start
		else:
			self._HideSnapLine()
			return proposed_start

	def _CalculateSnapEnd(self, proposed_end, cue):
		"""Snaps proposed cue end time during right-edge stretch."""
		if not ipar.UserSettings.Snapping.eval():
			self._HideSnapLine()
			return proposed_end
		if self.KeyboardOp.par.Ctrl.eval() or self.KeyboardOp.par.Alt.eval():
			self._HideSnapLine()
			return proposed_end

		thresh = self._GetSnapThreshold()
		targets = self._GetSnapTargets(exclude_selection=True)
		try:
			targets.append(float(self.User.Timelinelength.eval()))
		except Exception:
			pass

		best_target = None
		best_diff = thresh + 1.0
		best_end = proposed_end

		for t in targets:
			d = abs(t - proposed_end)
			if d < thresh and d < best_diff:
				best_diff = d
				best_end = t
				best_target = t

		if best_target is not None:
			self._ShowSnapLine(best_target)
			return best_end
		else:
			self._HideSnapLine()
			return proposed_end

	def _ShowSnapLine(self, x_pos):
		try:
			sl = self.MainOp.op('Canvas/geo_SnapLine')
			if sl:
				sl.par.tx = x_pos
				sl.par.render = True
		except Exception:
			pass

	def _HideSnapLine(self):
		try:
			sl = self.MainOp.op('Canvas/geo_SnapLine')
			if sl:
				sl.par.render = False
		except Exception:
			pass

	def _ProcessVerticalLayerDrag(self, current_y):
		try:
			gi = self.MainOp.op('Cues/null_GlobalInfo')
			if not gi:
				return
			lower_bounds = float(gi['Computedlowerbounds'].eval())
			layer_h = float(gi['Computedlayerheight'].eval())
			layer_count = int(self.User.Layercount.eval())

			target_layer = int(round((current_y - lower_bounds - 0.5 * layer_h) / layer_h))
			target_layer = max(0, min(layer_count - 1, target_layer))

			primary_init_layer = self.InitialLayers[0] if len(self.InitialLayers) > 0 else ext.Selection.Selection[0].par.Layer.eval()
			layer_delta = target_layer - primary_init_layer
			if layer_delta == 0:
				return

			can_move = True
			for ind, obj in enumerate(ext.Selection.Selection):
				init_l = self.InitialLayers[ind] if ind < len(self.InitialLayers) else obj.par.Layer.eval()
				dest_l = init_l + layer_delta
				if dest_l < 0 or dest_l >= layer_count:
					can_move = False
					break

			if can_move:
				for ind, obj in enumerate(ext.Selection.Selection):
					if not obj.par.Lock.eval():
						init_l = self.InitialLayers[ind] if ind < len(self.InitialLayers) else obj.par.Layer.eval()
						dest_l = init_l + layer_delta
						if obj.par.Layer.eval() != dest_l:
							obj.par.Layer = dest_l
				self.Layers = [x.par.Layer.eval() for x in ext.Selection.Selection]
		except Exception:
			pass

	def EventSelectStart(self, renderPickDat, event, eventPrev):
		'''	
			Description: Here we handle interactions on initial click

			A Cue, Layer, BG, or Scrubbar can be selected.

			Cue: 
				A cue item, assign parameters values based on conditions
			
				Parameters:
					Start Time -> (tx)
					Cue Length -> (sx)

				How do we know what cue is selected? 
					self.InstanceId -> event.instanceId

				Types of interactions:
					Translate -> Change time position
					Stretch -> Change length

		'''

		self.ClickType = int(event.inValues['aux'])
		if not event.selectedOp:	# sometimes this gets called without an object
			return
		selectedOp = event.selectedOp
		if not any(t in selectedOp.tags for t in ['Cue', 'Layer', 'Bg', 'Scrub']):
			if selectedOp.parent() is not None and any(t in selectedOp.parent().tags for t in ['Cue', 'Layer', 'Bg', 'Scrub']):
				selectedOp = selectedOp.parent()
		if not selectedOp:
			return

		self.InstanceId = event.instanceId
		ext.Selection.OldSelection = list(ext.Selection.Selection)
		self.ClickMapUV = event.texture
		self.ClickPosition = event.pos
		self.IsScrubBar = False
		self.IsTimelineItem = False  # we will use this to determine what kinds of interactions we need to perform
		self.IsBoxSelect = False
		open_scene_item = None

		if 'Cue' in selectedOp.tags: # Selection is a cue
			tag = 'Cue'
			objPrefix = self.ObjectPrefix[tag]
			self.PreviousTag = tag

			selectedItem = self.GetObject(selectedOp, self.InstanceId, tag) # retrieve the component this cue represents
			if not selectedItem:
				return

			self.ParComp.par.pagescope = self.PageScope[tag]	# change our UI page
			self.IsTimelineItem = True	# we use this during our next render pick stage

			if self.ClickType == 4:
				self.RickClickCallbackInfo.update( {
					'Tag' : tag,
					'Op' : selectedItem
				})
				try:
					self.MasterComp.Callbacks.OnRightClick(self.RickClickCallbackInfo)
				except:
					pass
				return
			
			elif self.ClickType == 2:
				self.SetTimer(gotoTime=True, seconds=selectedItem.par.Starttime.eval())
				return
			
			uvAspect = selectedItem.par.Uvaspect.eval()

			# Edge and scene button calculations in world seconds (scale & DPI independent)
			cue_start_time = selectedItem.par.Starttime.eval()
			cue_dur = selectedItem.par.Cuelength.eval()
			cue_end_time = cue_start_time + cue_dur
			click_time = self.ClickPosition.x

			cam = self.MainOp.op('Render/cam1')
			ren = self.MainOp.op('Render/render1')
			ortho_w = cam.par.orthowidth.eval() if (cam and hasattr(cam.par, 'orthowidth')) else 200.0
			ren_w = max(1.0, float(ren.width)) if ren else 1280.0
			sec_per_px = ortho_w / ren_w
			edge_margin_sec = max(0.05, min(cue_dur * 0.20, 8.0 * sec_per_px))

			dist_left = abs(click_time - cue_start_time)
			dist_right = abs(click_time - cue_end_time)

			is_right_edge = (dist_right <= edge_margin_sec and dist_right <= dist_left)
			is_left_edge = (dist_left <= edge_margin_sec and not is_right_edge)

			# Check Scene Edit icon hit (only inside cue body when wide enough and NOT on an edge)
			is_scene_btn = False
			if not is_right_edge and not is_left_edge:
				uZoom = 1.0
				za = self.MainOp.op('Cues/null_ZoomAdjust')
				if za is not None and za.numChans > 0:
					uZoom = max(0.0001, float(za['CamZoom'].eval()))
				ci = selectedItem.op('null_CueInfo')
				shader_uv_aspect = float(ci['uvAspect'].eval()) if ci is not None and ci['uvAspect'] is not None else float(uvAspect)
				w_norm = shader_uv_aspect / uZoom
				p_x = float(self.ClickMapUV.x) * w_norm
				p_y = float(self.ClickMapUV.y)
				bx1 = w_norm - 0.14
				bx0 = bx1 - 0.28
				by1 = 1.0 - 0.09
				by0 = by1 - 0.28
				is_scene_btn = (self.ClickType == 1 and w_norm >= 0.48 and bx0 <= p_x <= bx1 and by0 <= p_y <= by1)

			if is_scene_btn:
				open_scene_item = selectedItem
				self.IsTimelineItem = False
				self.CanStretch = False
				self.CanStretchLeft = False
				self.CanDragVertically = False
				self.CanTranslate = False
			elif is_right_edge:
				self.IsTimelineItem = True
				self.CanStretch = True
				self.CanStretchLeft = False
				self.CanDragVertically = False
				self.CanTranslate = False
			elif is_left_edge:
				self.IsTimelineItem = True
				self.CanStretch = False
				self.CanStretchLeft = True
				self.CanDragVertically = False
				self.CanTranslate = False
			else:
				self.IsTimelineItem = True
				self.CanStretch = False
				self.CanStretchLeft = False
				self.CanDragVertically = True
				self.CanTranslate = True

		elif 'Layer' in selectedOp.tags:
			tag = 'Layer'
			objPrefix = self.ObjectPrefix[tag]
			selectedItem = self.GetObject(selectedOp, self.InstanceId, tag)
			self.PreviousTag = tag
			
			if self.ClickType == 4:
				self.RickClickCallbackInfo.update( {
					'Tag' : tag,
					'Op' : selectedItem
				})
				try:
					self.MasterComp.Callbacks.OnRightClick(self.RickClickCallbackInfo)
				except:
					pass
				return

			self.ParComp.par.pagescope = self.PageScope[tag]

		elif 'Bg' in selectedOp.tags:
			tag = 'Bg'
			self.PreviousTag = tag
			if self.ClickType == 1:
				self.ParComp.par.op = self.UserSettingsOp
				self.ParComp.par.pagescope = self.PageScope[tag]
				ext.Selection.Selection.clear()
				ext.Selection.DoSelection(ext.Selection.Selection, ext.Selection.OldSelection, select = True)
				return
			elif self.ClickType == 4:
				ext.Selection.PerformBoxSelect((event.u,event.v))
				self.BoxSelectOp.par.tx, self.BoxSelectOp.par.ty = event.pos.x , event.pos.y
				run("op('{}').render = True".format(self.BoxSelectOp),delayFrames= 1)
				self.IsBoxSelect = True
				return

		elif 'Scrub' in selectedOp.tags:
			self.IsScrubBar = True
			if self.ClickType == 4:
				self.RickClickCallbackInfo.update( {
					'Tag' : 'Scrubbar',
					'Op' : None
				})
				try:
					self.MasterComp.Callbacks.OnRightClick(self.RickClickCallbackInfo)
				except:
					pass
				return
			return

		else:
			ext.Selection.Selection.clear()
			ext.Selection.DoSelection(ext.Selection.Selection, ext.Selection.OldSelection, select = True)
			selectedItem = None
			return

		self.ParComp.par.op = selectedItem

		if not self.System.Multiselect.eval() and not self.KeyboardOp.par.Shift.eval():
			ext.Selection.Selection = [selectedItem]
		else:
			if selectedItem in ext.Selection.Selection:
				pass
			else:
				ext.Selection.Selection.insert(0, selectedItem)

		ext.Selection.DoSelection(ext.Selection.Selection, select = True)

		selectionNames = [x.name for x in ext.Selection.Selection]
		chans = []
		selectedChop = parent.Main.op('Cues/base_Snapping/constant_SelectedPoints')

		for i in selectionNames:
			chans.extend([i + ':' + 'Starttime', i + ':' + 'Computedendtime'])

		finalChanNames = chans
		parent.Main.op('Cues/base_Snapping/delete_Selection').par.delscope.expr = finalChanNames

		if self.IsTimelineItem:
			# Alt + Drag: Duplicate cues and drag the new clones
			if getattr(self, 'CanTranslate', False) and (self.KeyboardOp.par.Alt.eval() or self.KeyboardOp.par.Onlyalt.eval()):
				mgr = self.MainOp.op('Project')
				if mgr and hasattr(mgr.ext, 'Manager'):
					clones = []
					for c in list(ext.Selection.Selection):
						try:
							new_c = mgr.ext.Manager.AddCue(copyOp=c)
							clones.append(new_c)
						except Exception as e:
							print(f'Alt+Drag clone error: {e}')
					if clones:
						ext.Selection.OldSelection = list(ext.Selection.Selection)
						ext.Selection.Selection = list(clones)
						ext.Selection.DoSelection(ext.Selection.Selection, select=True)
						selectedItem = clones[0]
						self.ParComp.par.op = selectedItem

			# Dynamic cursor feedback
			t3d = self.MainOp
			if t3d and hasattr(t3d.par, 'cursor'):
				if getattr(self, 'CanStretch', False) or getattr(self, 'CanStretchLeft', False):
					t3d.par.cursor = 'arrowLeftRight'
				elif getattr(self, 'CanTranslate', False):
					t3d.par.cursor = 'arrowAll'

			self.ProcessSelectedCues(event.pos)

		if open_scene_item is not None:
			se = self.MainOp.op('Cues/SceneEditor')
			if se is not None:
				se.module.open_cue_scene(open_scene_item)

	def EventSelect(self, renderPickDat, event, eventPrev):
		currentClickPosition = event.pos
		self.currentClickPosition = event.pos
		if currentClickPosition is None:
			return

		if not self.IsTimelineItem and not self.IsScrubBar and not self.IsBoxSelect:
			return

		outsideX, outsideY, directionX, directionY = False, False, 0, 0

		if self.ClickType == 1: # Left Click
			if self.IsTimelineItem:
				if not ext.Selection.Selection:
					return

				pass

				delta_x = currentClickPosition.x - self.ClickPosition.x

				# base_Snapping parameters bypassed for smooth 60 FPS translation
				pass

				# 1. Right-edge Stretch (modify Cuelength, keep Starttime fixed)
				if getattr(self, 'CanStretch', False):
					primary = ext.Selection.Selection[0]
					orig_st0 = self.StartTimes[0] if len(self.StartTimes) > 0 else primary.par.Starttime.eval()
					orig_du0 = self.Durations[0] if len(self.Durations) > 0 else primary.par.Cuelength.eval()
					raw_end = max(orig_st0 + 0.05, orig_st0 + orig_du0 + delta_x)
					snapped_end = self._CalculateSnapEnd(raw_end, primary)
					snap_delta = snapped_end - (orig_st0 + orig_du0 + delta_x)

					for ind, obj in enumerate(ext.Selection.Selection):
						if obj.par.Lock.eval():
							continue
						st = self.StartTimes[ind] if ind < len(self.StartTimes) else obj.par.Starttime.eval()
						du = self.Durations[ind] if ind < len(self.Durations) else obj.par.Cuelength.eval()
						new_end = max(st + 0.05, st + du + delta_x + snap_delta)
						new_len = max(0.05, new_end - st)
						self.SetLength(obj, new_len, addTo=False)

				# 2. Left-edge Stretch (modify Starttime & Cuelength, keep Endtime fixed)
				elif getattr(self, 'CanStretchLeft', False):
					primary = ext.Selection.Selection[0]
					orig_st0 = self.StartTimes[0] if len(self.StartTimes) > 0 else primary.par.Starttime.eval()
					orig_du0 = self.Durations[0] if len(self.Durations) > 0 else primary.par.Cuelength.eval()
					orig_ed0 = orig_st0 + orig_du0
					raw_start = max(0.0, min(orig_ed0 - 0.05, orig_st0 + delta_x))
					snapped_start = self._CalculateSnap(raw_start, primary)
					snapped_start = max(0.0, min(orig_ed0 - 0.05, snapped_start))
					snap_delta = snapped_start - (orig_st0 + delta_x)

					for ind, obj in enumerate(ext.Selection.Selection):
						if obj.par.Lock.eval():
							continue
						st = self.StartTimes[ind] if ind < len(self.StartTimes) else obj.par.Starttime.eval()
						du = self.Durations[ind] if ind < len(self.Durations) else obj.par.Cuelength.eval()
						fixed_end = st + du
						new_start = max(0.0, min(fixed_end - 0.05, st + delta_x + snap_delta))
						new_len = max(0.05, fixed_end - new_start)
						self.SetStartTime(new_start, obj)
						self.SetLength(obj, new_len, addTo=False)

				# 3. Continuous Translation (smooth 60 FPS real-time dragging)
				elif getattr(self, 'CanTranslate', False):
					snap_offset = 0.0
					if ipar.UserSettings.Snapping.eval() and len(ext.Selection.Selection) > 0:
						primary = ext.Selection.Selection[0]
						p_offset = self.ClickPositionOffsets[0].x if len(self.ClickPositionOffsets) > 0 else 0.0
						raw_primary_start = max(0.0, currentClickPosition.x + p_offset)
						snapped_primary_start = self._CalculateSnap(raw_primary_start, primary)
						snap_offset = snapped_primary_start - raw_primary_start

					for ind, obj in enumerate(ext.Selection.Selection):
						if obj.par.Lock.eval():
							continue
						if ind < len(self.ClickPositionOffsets):
							raw_start = max(0.0, currentClickPosition.x + self.ClickPositionOffsets[ind].x)
						else:
							orig_st = self.StartTimes[ind] if ind < len(self.StartTimes) else obj.par.Starttime.eval()
							raw_start = max(0.0, orig_st + delta_x)

						final_start = max(0.0, raw_start + snap_offset)
						self.SetStartTime(final_start, obj)

				# 4. Vertical Layer Dragging (smooth layer change using procedural layer math)
				if getattr(self, 'CanDragVertically', False):
					self._ProcessVerticalLayerDrag(currentClickPosition.y)

			elif self.IsScrubBar:
				if self.KeyboardOp.par.Onlyalt.eval():
					self.User.Cameraposition = event.pos.x
				else:
					timePosition = self.myOp.PositionToTime(currentClickPosition.x)
					timePosition = max(0.0, min(self.User.Timelinelength.eval(), timePosition))
					if self.KeyboardOp.par.Ctrl.eval():
						timePosition = ext.Transformer.IncrementalTransform([timePosition])[0]
					self.TimeComp.GotoTime(seconds=timePosition)

		elif self.ClickType == 4: # Right Click
			if self.IsBoxSelect:
				delta = self.ClickPosition - currentClickPosition
				self.BoxSelectOp.par.sx = delta[0]
				self.BoxSelectOp.par.sy = delta[1]

	def EventSelectEnd(self, renderPickDat, event, eventPrev):
		self._HideSnapLine()
		self.CanStretch = False
		self.CanStretchLeft = False
		self.CanTranslate = False
		self.CanDragVertically = False

		# Reset cursor to standard pointer
		t3d = self.MainOp
		if t3d and hasattr(t3d.par, 'cursor'):
			t3d.par.cursor = 'pointer'

		try:
			ext.Bounds.UpdateAllBounds()
		except Exception:
			pass

		if self.IsBoxSelect:
			self.BoxSelectOp.render = False
			ext.Selection.EndBoxSelect((event.u, event.v), clearOld=not self.KeyboardOp.par.Shift.eval())
			self.ClickType = 0
			ext.Selection.GetInstancePositions()
			self.BoxSelectOp.par.Offsetx, self.BoxSelectOp.par.Offsety = 0, 0
			self.BoxSelectOp.par.tx, self.BoxSelectOp.par.ty = 0, 0
			self.IsBoxSelect = False

		if self.IsScrubBar:
			ext.Transformer.UpdateAllBounds()
			self.IsScrubBar = False

		self.IsTimelineItem = False

	def SetAllSelectionStartTimes(self, timeOffset = 0):
		'''
			This operation sets the start time for all the cues in the selection
			this is actually getting called from the script_SnappingCallbacks located here-
			/Multi_Layer_Timeline/Timeline3D/Cues/base_Snapping

			We have a chop network that is checking for snaps.

			params: timeOffset - the value coming from the snapping callbacks 
				This will offset our cues by a value to lock it in place.

		'''

		for ind, obj in enumerate(ext.Selection.Selection):
			if getattr(self, 'CanTranslate', False): # Translate our cue
				newGeoPosition = self.currentClickPosition + self.ClickPositionOffsets[ind]  # TDU.Position
				proposedStartTime = newGeoPosition.x
				if timeOffset != None and timeOffset != 0.0 and ipar.UserSettings.Snapping.eval():
					proposedStartTime -= timeOffset		
				self.SetStartTime(proposedStartTime, obj)

	def SetStartTime(self, startTime, Cue):
		if Cue.par.Lock.eval():
			return

		realStartTime = max(0.0, startTime)
		realStartTime = min(realStartTime, self.User.Timelinelength.eval() - 1)

		if self.KeyboardOp.par.Ctrlalt.eval():
			realStartTime = min(self.User.Timelinelength.eval()-1, self.Timer['timer_seconds0'].eval())

		elif self.KeyboardOp.par.Ctrl.eval():		# snap to seconds
			realStartTime = ext.Transformer.IncrementalTransform([realStartTime])[0]

		elif self.KeyboardOp.par.Alt.eval():		# snap to frames
			frameLength = 1000 / self.User.Fps.eval() * .001
			realStartTime = self.myOp.IncrementalTransform([realStartTime], frameLength)[0]

		if abs(Cue.par.Starttime.eval() - realStartTime) > 1e-4:
			Cue.par.Starttime = realStartTime

	def SetLength(self, obj, time, addTo = False):
		if obj.par.Lock.eval():
			return

		realLength = time

		if self.KeyboardOp.par.Ctrl.eval():		# snap to seconds
			realLength = max(1.0, round(realLength))

		elif self.KeyboardOp.par.Alt.eval():		# snap to frames
			frameLength = 1000 / self.User.Fps.eval() * .001
			realLength = self.myOp.IncrementalTransform([realLength], frameLength)[0]

		realLength = max(0.05, realLength)

		if addTo:
			new_len = max(0.05, obj.par.Cuelength.eval() + realLength)
			if abs(obj.par.Cuelength.eval() - new_len) > 1e-4:
				obj.par.Cuelength = new_len
		else:
			if abs(obj.par.Cuelength.eval() - realLength) > 1e-4:
				obj.par.Cuelength = realLength

	def GetObject(self, selectedOp, instanceId, tag):
		prefix = self.ObjectPrefix[tag]
		if tag == 'Cue':
			opName = self.CueDB[instanceId+2,'name']
		else:
			opName = prefix + str(instanceId)
		return selectedOp.parent().op(opName)

	def SetTimer(self, gotoTime=None, segment = None, seconds = None, frame = None, fraction = None):
		if gotoTime:
			self.Timer.goTo(segment = segment, seconds = seconds, frame = frame, fraction = fraction)

	def ProcessSelectedCues(self, eventPos):
		self.StartTimes = []
		self.Durations = []
		self.EndTimes = []
		self.InitialLayers = []
		self.OriginalPositions = []
		self.ClickPositionOffsets = []
		self.Layers = []
		self.OffsetFromEndTime = []
		self.ClickPosition = eventPos		# tdu.Position
		
		for i in ext.Selection.Selection:
			curStartTime = i.par.Starttime.eval()
			curCueLength = i.par.Cuelength.eval()
			curObjPositionX = i.par.Tx.eval()
			curObjPositionY = i.par.Ty.eval()
			curLayer = i.par.Layer.eval()
			curEndTimePos = i.par.Computedendtime.eval()

			self.Layers.append(curLayer)
			self.InitialLayers.append(curLayer)
			self.StartTimes.append(curStartTime)
			self.Durations.append(curCueLength)
			self.EndTimes.append(curStartTime + curCueLength)
			self.OriginalPositions.append((curObjPositionX, curObjPositionY))
			self.ClickPositionOffsets.append(tdu.Vector(curObjPositionX - self.ClickPosition.x, curObjPositionY - self.ClickPosition.y, 0))
			self.OffsetFromEndTime.append(tdu.Vector(curEndTimePos - self.ClickPosition.x, 0, 0))
