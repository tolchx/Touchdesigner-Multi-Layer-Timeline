tc = op('/Multi_Layer_Timeline/container_Timecode')
el = tc.op('card_Elapsed/txt_digits')
if el:
    el.par.text.expr = "f\"{int(op('/Multi_Layer_Timeline/container_Timecode/null_Countup')['Hour']):02d}:{int(op('/Multi_Layer_Timeline/container_Timecode/null_Countup')['Minute']):02d}:{int(op('/Multi_Layer_Timeline/container_Timecode/null_Countup')['Seconds']):02d}:{int(op('/Multi_Layer_Timeline/container_Timecode/null_Countup')['Frames']):02d}\""

rem = tc.op('card_Remaining/txt_digits')
if rem:
    rem.par.text.expr = "f\"{int(op('/Multi_Layer_Timeline/container_Timecode/null_Countdown')['Hour']):02d}:{int(op('/Multi_Layer_Timeline/container_Timecode/null_Countdown')['Minute']):02d}:{int(op('/Multi_Layer_Timeline/container_Timecode/null_Countdown')['Seconds']):02d}:{int(op('/Multi_Layer_Timeline/container_Timecode/null_Countdown')['Frames']):02d}\""

print('Fixed timecode paths cleanly')
