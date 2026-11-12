"""Ruler label thresholds (`uBecomesVisibleAt`) — one label class per tick density.

`uBecomesVisibleAt[i]` is compared to `uStepValue` (the current tick length, in seconds):
a class is drawn while `uStepValue <= threshold[i]`. Classes are assigned per second
(coarsest match wins), so the *finest visible class* decides the label spacing: if it is
finer than the tick step, several labels crowd into one tick gap.

Measured mapping in this project (cam1.sx = 1.0): `StepValue ~= 25 * visible_fraction`
and `px/s = 4.363 / visible_fraction`, so a class of interval I gets

    spacing_px = I * px/s = I * 4.363 / visible_fraction ~= I * 109 / StepValue

Keeping spacing >= ~70 px means a class may only appear while `StepValue <= 1.5 * I`.
With the old preset the 10s class had a threshold of 30 and the 5s class 15, so at a
10s tick step both were drawn (5s labels every ~55 px — the crowding).

Thresholds are therefore 1.5 x interval. The preset tables live in
`Canvas/base_Settings_Processing/base_GetPattern` (table1..table15); `switch1` picks one,
and its index is currently pinned to 2 = `datto2_30Sec` (table2).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from td_client import run_td_code

# class order: 2h, 1h, 30m, 15m, 10m, 5m, 1m, 30s, 10s, 5s, 1s
INTERVALS = [7200, 3600, 1800, 900, 600, 300, 60, 30, 10, 5, 1]
MARGIN = 1.5
THRESHOLDS = [round(i * MARGIN, 2) for i in INTERVALS]

CODE = r'''
import td
gp = td.op('/Multi_Layer_Timeline/Timeline3D/Canvas/base_Settings_Processing/base_GetPattern')
sw = gp.op('switch1')
active = sw.inputs[sw.par.index.eval()]
tbl = td.op(active.par.dat.eval())
vals = %r
for i, v in enumerate(vals):
    tbl[i, 0] = ('%%g' %% v)
sp = td.op('/Multi_Layer_Timeline/Timeline3D/Canvas/base_Settings_Processing')
sp.op('null_BecomesVisibleAt').cook(force=True)
print('preset: %%s (switch index %%d)' %% (tbl.name, sw.par.index.eval()))
print('thresholds:', [tbl[i, 0].val for i in range(tbl.numRows)])
print('active array:', [round(x, 2) for x in sp.op('null_BecomesVisibleAt')['BecomesVisibleAt'].vals])
''' % (THRESHOLDS,)

if __name__ == '__main__':
    print(run_td_code(CODE))
