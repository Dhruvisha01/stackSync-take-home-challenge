import subprocess
import uuid
import json
import os

WORKDIR = "/tmp/scripts"
is_cloud_run = 'K_SERVICE' in os.environ  # Detect Cloud Run because NS Jail fails in Google Cloud Run

def execute_script(script: str):
    if "def main" not in script:
        raise Exception("The script must contain a main() function.")

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

    # Parse the last line as JSON result
    try:
        result_json = json.loads(lines[-1])
    except json.JSONDecodeError:
        raise Exception("main() did not return a valid JSON")

    # All lines except the last are treated as stdout
    return {
        "result": result_json,
        "stdout": "\n".join(lines[:-1]) + ("\n" if len(lines) > 1 else "")
    }
