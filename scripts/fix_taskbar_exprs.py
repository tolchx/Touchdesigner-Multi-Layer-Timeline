tb = op('/Multi_Layer_Timeline/ui_taskbar')
if tb:
    led = tb.op('comp_Status/led_dot')
    if led:
        led.par.bgcolorr.expr = "0.15 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.play.eval() else (0.95 if op('/Multi_Layer_Timeline/Timeline3D/Time/null_CountupSeconds')['Timelinelength'].eval() > 0.05 else 0.45)"
        led.par.bgcolorg.expr = "0.95 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.play.eval() else (0.65 if op('/Multi_Layer_Timeline/Timeline3D/Time/null_CountupSeconds')['Timelinelength'].eval() > 0.05 else 0.48)"
        led.par.bgcolorb.expr = "0.35 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.play.eval() else (0.15 if op('/Multi_Layer_Timeline/Timeline3D/Time/null_CountupSeconds')['Timelinelength'].eval() > 0.05 else 0.52)"

    txt = tb.op('comp_Status/text_status')
    if txt:
        txt.par.text.expr = "'PLAYING' if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.play.eval() else ('PAUSED' if op('/Multi_Layer_Timeline/Timeline3D/Time/null_CountupSeconds')['Timelinelength'].eval() > 0.05 else 'STOPPED')"
        txt.par.fontcolorr.expr = "0.25 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.play.eval() else 0.70"
        txt.par.fontcolorg.expr = "0.95 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.play.eval() else 0.72"
        txt.par.fontcolorb.expr = "0.45 if op('/Multi_Layer_Timeline/Timeline3D/Time/timer1').par.play.eval() else 0.75"

    sess = tb.op('text_Session')
    if sess:
        sess.par.text.expr = "f'{project.name}  •  1920x1080  •  60 FPS  •  {op(\"/Multi_Layer_Timeline/container_Duration/field_Duration/string\")[0,0].val}'"

print('Updated taskbar expressions cleanly')
