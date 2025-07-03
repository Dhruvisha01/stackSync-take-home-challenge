FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    git make gcc g++ flex bison \
    libprotobuf-dev libnl-route-3-dev \
    protobuf-compiler libcap-dev libseccomp-dev \
    pkg-config curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone and build NSJail
RUN git clone https://github.com/google/nsjail.git /nsjail && \
    cd /nsjail && make && cp nsjail /usr/local/bin/

# Set working directory and copy app code
WORKDIR /app
COPY . /app

# Overwrite nsjail.cfg with a working config for ARM64
RUN printf '%s\n' \
'name: "python_executor"' \
'mode: ONCE' \
'hostname: "sandbox"' \
'cwd: "/tmp"' \
'time_limit: 5' \
'rlimit_as: 512' \
'rlimit_cpu: 5' \
'rlimit_fsize: 1024' \
'envar: "LD_LIBRARY_PATH=/usr/local/lib"' \
'exec_bin {' \
'  path: "/usr/local/bin/python3"' \
'}' \
'mount {' \
'  src: "/usr/local/bin/python3"' \
'  dst: "/usr/local/bin/python3"' \
'  is_bind: true' \
'  rw: false' \
'}' \
'mount {' \
'  src: "/usr/local/lib"' \
'  dst: "/usr/local/lib"' \
'  is_bind: true' \
'  rw: false' \
'}' \
'mount {' \
'  src: "/usr/lib"' \
'  dst: "/usr/lib"' \
'  is_bind: true' \
'  rw: false' \
'}' \
'mount {' \
'  src: "/lib"' \
'  dst: "/lib"' \
'  is_bind: true' \
'  rw: false' \
'}' \
'mount {' \
'  src: "/lib/aarch64-linux-gnu"' \
'  dst: "/lib/aarch64-linux-gnu"' \
'  is_bind: true' \
'  rw: false' \
'}' \
'mount {' \
'  src: "/usr/lib/aarch64-linux-gnu"' \
'  dst: "/usr/lib/aarch64-linux-gnu"' \
'  is_bind: true' \
'  rw: false' \
'}' \
'mount {' \
'  src: "/lib/ld-linux-aarch64.so.1"' \
'  dst: "/lib/ld-linux-aarch64.so.1"' \
'  is_bind: true' \
'  rw: false' \
'}' \
'mount {' \
'  src: "/tmp"' \
'  dst: "/tmp"' \
'  is_bind: true' \
'  rw: true' \
'}' \
'mount {' \
'  src: "/app"' \
'  dst: "/app"' \
'  is_bind: true' \
'  rw: false' \
'}' \
> /app/nsjail.cfg

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "app.py"]
