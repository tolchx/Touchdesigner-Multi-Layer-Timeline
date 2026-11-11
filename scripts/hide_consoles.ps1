Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;

public class ConsoleHider {
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern int GetClassName(IntPtr hWnd, StringBuilder lpClassName, int nMaxCount);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    public static int HideAllConsoleWindows(HashSet<uint> targetPids) {
        int count = 0;
        EnumWindows((hWnd, lParam) => {
            if (IsWindowVisible(hWnd)) {
                StringBuilder sb = new StringBuilder(256);
                GetClassName(hWnd, sb, sb.Capacity);
                string cls = sb.ToString();

                uint pid;
                GetWindowThreadProcessId(hWnd, out pid);

                // Hide if it is a console window or belongs to cmd/conhost
                if (cls == "ConsoleWindowClass" || targetPids.Contains(pid)) {
                    ShowWindow(hWnd, 0); // 0 = SW_HIDE
                    count++;
                }
            }
            return true;
        }, IntPtr.Zero);
        return count;
    }
}
"@

# Collect all PIDs for cmd and conhost
$pids = [System.Collections.Generic.HashSet[uint]]::new()
Get-Process cmd, conhost -ErrorAction SilentlyContinue | ForEach-Object {
    [void]$pids.Add([uint32]$_.Id)
}

$count = [ConsoleHider]::HideAllConsoleWindows($pids)
Write-Output "Ventanas ocultadas exitosamente: $count"
