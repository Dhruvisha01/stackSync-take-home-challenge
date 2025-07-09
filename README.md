# Python Executor

## File Structure

### app.py 

This file is the entry point into the code execution that defines the API endpoint `/execute` used for executing the python code.

If the user does not provide a script, then it throws an error.


### executer.py

This file handles the execution of the python code. We first check whether the execution happens in the cloud environment or is NS jail. This is essential because Google Cloud Run does not allow some core linux commands that are needed while using NSJail. We also verify if the main function is present in the script or not. The other check we are doing is to make sure use enters the right python syntax using ast library. Finally we run the program and return the output as an object containing the result and the stdout. 

### Dockerfile
This Dockerfile sets up a secure Python execution sandbox using NSJail, designed to safely run user-submitted Python scripts with resource and system call restrictions. It supports both local execution with NSJail and Cloud Run fallback execution when NSJail is not supported (e.g., on Google Cloud Run).

## What's included? 
- **Base Image:** `python:3.11-slim` — lightweight, secure base.
- **Dependencies Installed:** 
    1. **Build tools:** `make`, `gcc`, `g++`, `flex`, `bison`
    2. **Security Libs:**  `libseccomp-dev`, `libcap-dev`
    3. **Protocol Buffers:** `libprotobuf-dev`, `protobuf-compiler`
    4. **Networking:** `libnl-route-3-dev`
    5. **Others:** `curl`, `pkg-config`, `ca-certificates`

- **NSJail:**
    1. Cloned and built from source
    2. Installed to `/usr/local/bin/nsjail`

- **NSJail Config:**
    1. Auto-generated at /app/nsjail.cfg
    2. Custom mount and resource limits for secure sandboxing (ARM64-friendly)

- **App Setup:**
    1. Sets working directory to `/app`
    2. Copies your code
    3. Installs Python dependencies via `requirements.txt`

## Run Instructions:

1. **Build the Docker image**

```
docker build -t python-sandbox .
```

2. **Run the container**
```
docker run --rm -it --privileged -p 8080:8080 stacksync
```

3. **Test the API**

```
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main(): return {\"message\": \"Hello from sandbox\"}"}'
```

4. **Test the Deployed Version**

Link for deployed version is `https://stacksync-235910813111.us-east1.run.app/execute`
```
curl -X POST https://stacksync-235910813111.us-east1.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    result = 3 * 4\n    print(\"Multiplication:\", result)\n    return {\"product\": result}"}'
```

