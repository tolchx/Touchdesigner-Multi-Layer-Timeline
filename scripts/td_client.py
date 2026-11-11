import sys
import json
import urllib.request

URL = "http://127.0.0.1:13316/mcp"

def run_td_code(code_str):
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
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
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
        print(f"Connection error: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Check if arg is a file
        import os
        if os.path.exists(arg) and arg.endswith('.py'):
            with open(arg, 'r', encoding='utf-8') as f:
                code_to_run = f.read()
        else:
            code_to_run = arg
        run_td_code(code_to_run)
    else:
        print("Usage: python td_client.py <code> or <file.py>")
