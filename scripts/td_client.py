import sys
import json
import urllib.request
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

DEFAULT_PORT = 13316

def run_td_code(code_str, port=DEFAULT_PORT):
    url = f"http://127.0.0.1:{port}/mcp"
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "execute_code",
            "arguments": {"code": code_str}
        },
        "id": 1
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            if "result" in res and "content" in res["result"]:
                txt = res["result"]["content"][0].get("text", "")
                parsed = json.loads(txt)
                if parsed.get("output"):
                    print(parsed["output"], end="")
                if not parsed.get("success", False) and parsed.get("error"):
                    print(f"Error: {parsed['error']}", file=sys.stderr)
                return parsed
            else:
                print(res)
                return res
    except Exception as e:
        print(f"Connection error to {url}: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    port = int(os.environ.get("TD_PORT", DEFAULT_PORT))
    args = sys.argv[1:]
    
    if len(args) >= 2 and args[0] in ['-p', '--port']:
        port = int(args[1])
        args = args[2:]
    elif len(args) >= 1 and args[0].isdigit() and len(args[0]) == 5:
        port = int(args[0])
        args = args[1:]
        
    if args:
        arg = args[0]
        if os.path.exists(arg) and arg.endswith('.py'):
            with open(arg, 'r', encoding='utf-8') as f:
                code_to_run = f.read()
        else:
            code_to_run = arg
        run_td_code(code_to_run, port=port)
    else:
        print(f"Usage: python td_client.py [-p PORT] <code> or <file.py>")
