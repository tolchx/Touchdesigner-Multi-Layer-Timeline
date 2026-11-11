from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class RangeBar:
	"""
	Optimized RangeBar extension for Multi-Layer Timeline.
	Zero layout stalls, clamped smooth dragging, 60 FPS rock-solid.
	"""
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.Bar = self.ownerComp.op('container2')
		self.LAnchor = self.Bar.par.leftanchor
		self.RAnchor = self.Bar.par.rightanchor
		self.LRange = self.ownerComp.par.Lrange
		self.RRange = self.ownerComp.par.Rrange
		self.InitialClickU = 0
		self.InitialInsideClickU = 0
		self.AnchorsOnClick = ()
		self.ButtonClicked = -1
		self._lastU = None

	def ChangeRange(self, channel, val, prev):
		currentU = self.ownerComp.panel.insideu.val
		if self._lastU is not None and abs(currentU - self._lastU) < 1e-6:
			return
		self._lastU = currentU

		delta = currentU - self.InitialClickU

		if self.ButtonClicked == 0:
			# Left handle: trim start / zoom from left
			newVal = max(0.0, min(self.AnchorsOnClick[0] + delta, self.RAnchor.val - 0.025))
			if self.LAnchor.val != newVal:
				self.LAnchor.val = newVal
				self.LRange.val = newVal

		elif self.ButtonClicked == 1:
			# Center track: pan entire range window smoothly
			span = self.AnchorsOnClick[1] - self.AnchorsOnClick[0]
			newVal1 = self.AnchorsOnClick[0] + delta
			newVal2 = self.AnchorsOnClick[1] + delta
			if newVal1 < 0.0:
				newVal1 = 0.0
				newVal2 = min(1.0, span)
			elif newVal2 > 1.0:
				newVal2 = 1.0
				newVal1 = max(0.0, 1.0 - span)
			if self.LAnchor.val != newVal1 or self.RAnchor.val != newVal2:
				self.LAnchor.val = newVal1
				self.RAnchor.val = newVal2
				self.LRange.val = newVal1
				self.RRange.val = newVal2

		elif self.ButtonClicked == 2:
			# Right handle: trim end / zoom from right
			newVal = min(1.0, max(self.AnchorsOnClick[1] + delta, self.LAnchor.val + 0.025))
			if self.RAnchor.val != newVal:
				self.RAnchor.val = newVal
				self.RRange.val = newVal
