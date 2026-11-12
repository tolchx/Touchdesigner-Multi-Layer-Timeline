"""Bottom-up save per AGENTS.md §4.3.

1. Abort if the project has any errors (Zero Errors Mandate).
2. Save every component that declares an `externaltox`, deepest first, so parents
   capture already-saved children.
3. Save the root to Release/Multi_Layer_Timeline.tox (and its own Master tox above).
4. Save the project to a new versioned .toe.

Usage: python scripts/save_bottom_up.py [toe_version]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from td_client import run_td_code

ROOT = 'C:/Users/Tolch/Documents/AI_Code/Touchdesigner-Multi-Layer-Timeline/'
RELEASE = 'Release/Multi_Layer_Timeline.tox'
DEFAULT_TOE = 'v2.3.toe'

TEMPLATE = r'''
import os
import td

ROOT = '__ROOT__'
RELEASE = '__RELEASE__'
TOE = '__TOE__'
r = td.op('/Multi_Layer_Timeline')
out = []

errs = []
def walk(o, d=0):
    if d > 16:
        return
    try:
        e = o.errors()
        if e:
            errs.append(o.path)
    except Exception:
        pass
    for c in getattr(o, 'children', []):
        walk(c, d + 1)

walk(r)
if errs:
    print('ABORT: %d components with errors: %s' % (len(errs), errs[:6]))
else:
    jobs = []
    def collect(o, d=0):
        if d > 16:
            return
        p = getattr(o.par, 'externaltox', None)
        if p is not None:
            try:
                v = p.eval()
            except Exception:
                v = ''
            if v:
                jobs.append((o.path, os.path.join(ROOT, v.replace('/', os.sep))))
        for c in getattr(o, 'children', []):
            collect(c, d + 1)

    collect(r)
    jobs.sort(key=lambda j: j[0].count('/'), reverse=True)
    saved = 0
    for path, dest in jobs:
        o = td.op(path)
        try:
            o.save(dest)
            saved += 1
            out.append('saved %-52s %d KB' % (os.path.basename(dest), os.path.getsize(dest) // 1024))
        except Exception as ex:
            out.append('FAILED %s -> %s' % (path, str(ex)[:90]))

    try:
        r.save(os.path.join(ROOT, RELEASE.replace('/', os.sep)))
        out.append('saved release tox %d KB' % (os.path.getsize(os.path.join(ROOT, RELEASE.replace('/', os.sep))) // 1024))
    except Exception as ex:
        out.append('FAILED release tox: %s' % str(ex)[:90])

    toe = os.path.join(ROOT, TOE)
    try:
        project.save(toe)
        out.append('saved project %s %d KB' % (TOE, os.path.getsize(toe) // 1024))
    except Exception as ex:
        out.append('FAILED project save: %s' % str(ex)[:120])

    out.insert(0, 'components saved: %d / %d' % (saved, len(jobs)))
print(chr(10).join(out))
'''

if __name__ == '__main__':
    toe = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TOE
    with open(os.path.join(ROOT, 'scripts', 'td_client.py'), encoding='utf-8'):
        pass
    code = TEMPLATE.replace('__ROOT__', ROOT).replace('__RELEASE__', RELEASE).replace('__TOE__', toe)
    print(run_td_code(code))
