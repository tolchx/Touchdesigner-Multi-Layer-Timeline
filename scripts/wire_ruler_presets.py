"""Wire the ruler preset switch to the current zoom.

`Canvas/base_Settings_Processing/base_GetPattern/switch1` selects one of 16 threshold
tables (`datto2_10Sec` … `datto_1200Min`, backed by `table1..table15`). Its index was a
constant, so only one preset was ever used.

This script:
  1. rewrites every preset with the same rule already validated for the 30 s preset:
     threshold = 1.5 x class interval (guarantees >= ~70 px between labels),
  2. drives `switch1.index` from the current tick step (`uStepValue`), picking the
     preset whose nominal step is the smallest one >= the current step.

Both steps are idempotent. Run inside TouchDesigner:
    python scripts/td_client.py scripts/wire_ruler_presets.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from td_client import run_td_code

INTERVALS = [7200, 3600, 1800, 900, 600, 300, 60, 30, 10, 5, 1]
MARGIN = 1.5
THRESHOLDS = [round(i * MARGIN, 2) for i in INTERVALS]

# nominal tick step each preset was authored for, in switch input order
NOMINALS = [10, 15, 30, 60, 300, 600, 900, 1200, 1800, 2700, 3600, 5400, 7200, 10800, 21600, 72000]

STEP_EXPR = "parent(2).op('null_StepValue')['StepValue']"


def index_expr(tolerance=1.06):
    """Python expression: smallest nominal step >= current step (6% tolerance, since
    StepValue lands slightly above the nominal, e.g. 30.03 for the 30 s band)."""
    expr = str(len(NOMINALS) - 1)
    for i in range(len(NOMINALS) - 2, -1, -1):
        expr = "(%d if %s <= %g else %s)" % (i, STEP_EXPR, NOMINALS[i] * tolerance, expr)
    return expr


TEMPLATE = r'''
import td
gp = td.op('/Multi_Layer_Timeline/Timeline3D/Canvas/base_Settings_Processing/base_GetPattern')
sp = td.op('/Multi_Layer_Timeline/Timeline3D/Canvas/base_Settings_Processing')
sw = gp.op('switch1')
vals = __VALS__
out = []

for i, d in enumerate(sw.inputs):
    if not d:
        continue
    tbl = td.op(d.par.dat.eval())
    for r, v in enumerate(vals):
        tbl[r, 0] = ('%g' % v)
out.append('presets normalised: %d' % len([d for d in sw.inputs if d]))

EXPR = "__EXPR__"
if sw.par.index.expr != EXPR:
    sw.par.index.expr = EXPR
out.append('switch1.index expr set (%d chars)' % len(sw.par.index.expr))

rend = td.op('/Multi_Layer_Timeline/Timeline3D/Render')
cg = rend.op('base_GetCamScale')
for rng in (1.0, 0.7, 0.6, 0.4, 0.35):
    rend.ext.Render.SetRange(0.0, rng)
    for _ in range(3):
        cg.cook(force=True)
        rend.op('null_CamScale').cook(force=True)
        sp.op('null_StepValue').cook(force=True)
    sp.op('null_BecomesVisibleAt').cook(force=True)
    step = sp.op('null_StepValue')['StepValue'].eval()
    idx = sw.par.index.eval()
    name = sw.inputs[int(round(idx))].name if sw.inputs[int(round(idx))] else '?'
    out.append('range=%.2f step=%7.2f -> idx %d (%s)' % (rng, step, int(round(idx)), name))
rend.ext.Render.SetRange(0.0, 1.0)
for _ in range(3):
    cg.cook(force=True)
    rend.op('null_CamScale').cook(force=True)
    sp.op('null_StepValue').cook(force=True)
out.append('presets/thresholds: ' + str([round(v, 1) for v in sp.op('null_BecomesVisibleAt')['BecomesVisibleAt'].vals]))
print(chr(10).join(out))
'''

if __name__ == '__main__':
    code = TEMPLATE.replace('__VALS__', repr(THRESHOLDS)).replace('__EXPR__', index_expr())
    print(run_td_code(code))
