import subprocess
import uuid
import json
import os
import ast

WORKDIR = "/tmp/scripts"
is_cloud_run = 'K_SERVICE' in os.environ  # Detect Cloud Run because NS Jail fails in Google Cloud Run

def execute_script(script: str):
    # Check for main function existence
    if "def main" not in script:
        raise Exception("The script must contain a main() function.")

    # Basic syntax validation
    try:
        ast.parse(script)
    except SyntaxError:
        raise Exception("Invalid Python syntax.")
    
    script_id = str(uuid.uuid4())
    filepath = f"{WORKDIR}/{script_id}.py"

    os.makedirs(WORKDIR, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(script)
        f.write(
            "\n\nif __name__ == '__main__':\n"
            "    import json\n"
            "    result = main()\n"
            "    print(json.dumps(result))\n"
        )
    # Running directly using Python in Google Cloud, else use NSJail
    cmd = ["python3", filepath] if is_cloud_run else [
        "nsjail",
        "--config", "/app/nsjail.cfg",
        "--",
        "python3", filepath
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)

    if result.returncode != 0:
        raise Exception(result.stderr.decode())

    stdout = result.stdout.decode().strip()
    lines = stdout.splitlines()

    if not lines:
        raise Exception("No output produced by script")

    
    try:
        result_json = json.loads(lines[-1])
    except json.JSONDecodeError:
        raise Exception("main() did not return a valid JSON")

   
    return {
        "result": result_json,
        "stdout": "\n".join(lines[:-1]) + ("\n" if len(lines) > 1 else "")
    }
