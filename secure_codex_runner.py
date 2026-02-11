import os
import subprocess
import shlex
import tempfile
import shutil
import hashlib
import hmac
import json
from datetime import datetime
from pathlib import Path

# ==============================
# CONFIGURATION
# ==============================

DOCKER_IMAGE = "node:20-slim"
CODEX_PACKAGE = "@openai/codex"
SECCOMP_PROFILE = "./seccomp-restrict.json"
AUDIT_LOG = "codex_audit.log"
HMAC_SECRET = os.environ.get("CODEX_AUDIT_SECRET", "change_this_secret")
WORKSPACE_SOURCE = "./workspace"
ALLOW_NETWORK_DEFAULT = False
USE_GVISOR = False  # Set True if runsc installed

# ==============================
# SECURITY UTILITIES
# ==============================

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def sign_log(entry: str) -> str:
    return hmac.new(
        HMAC_SECRET.encode(),
        entry.encode(),
        hashlib.sha256
    ).hexdigest()

def append_audit(entry_dict):
    entry_json = json.dumps(entry_dict, sort_keys=True)
    signature = sign_log(entry_json)

    with open(AUDIT_LOG, "a") as f:
        f.write(entry_json + "\n")
        f.write("SIGNATURE:" + signature + "\n")

# ==============================
# VALIDATION
# ==============================

def validate_prompt(prompt: str):
    forbidden = [
        "sudo",
        "rm -rf",
        "mkfs",
        "shutdown",
        "reboot",
        "dd if=",
        ":(){",
        "forkbomb"
    ]

    for token in forbidden:
        if token in prompt.lower():
            raise ValueError(f"Blocked dangerous token detected: {token}")

# ==============================
# EPHEMERAL WORKSPACE
# ==============================

def create_ephemeral_workspace():
    temp_dir = tempfile.mkdtemp(prefix="codex_ephemeral_")
    source_path = Path(WORKSPACE_SOURCE).resolve()

    if source_path.exists():
        shutil.copytree(source_path, Path(temp_dir) / "workspace")

    return temp_dir

# ==============================
# DOCKER COMMAND BUILDER
# ==============================

def build_docker_command(prompt, ephemeral_dir, allow_network=False):

    network_mode = "bridge" if allow_network else "none"
    runtime = ["--runtime=runsc"] if USE_GVISOR else []

    container_command = f"""
    useradd -m codexuser &&
    chown -R codexuser /workspace &&
    su codexuser -c "
    npm install -g {CODEX_PACKAGE} &&
    codex --suggest {shlex.quote(prompt)}
    "
    """

    cmd = [
        "docker", "run", "--rm",
        "--network", network_mode,
        "--memory=512m",
        "--cpus=1.0",
        "--pids-limit=128",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt", "no-new-privileges",
        "--security-opt", f"seccomp={os.path.abspath(SECCOMP_PROFILE)}",
        "-v", f"{ephemeral_dir}/workspace:/workspace:rw",
        "-w", "/workspace",
    ] + runtime + [
        DOCKER_IMAGE,
        "bash", "-c", container_command
    ]

    return cmd

# ==============================
# MAIN EXECUTION
# ==============================

def run_codex_secure(prompt, allow_network=False):

    validate_prompt(prompt)

    prompt_hash = sha256(prompt)
    timestamp = datetime.utcnow().isoformat()

    ephemeral_dir = create_ephemeral_workspace()

    docker_cmd = build_docker_command(prompt, ephemeral_dir, allow_network)

    print("\n🔐 Launching hardened Codex container...\n")

    result = subprocess.run(
        docker_cmd,
        capture_output=True,
        text=True
    )

    output_hash = sha256(result.stdout)

    audit_entry = {
        "timestamp": timestamp,
        "prompt_hash": prompt_hash,
        "output_hash": output_hash,
        "return_code": result.returncode,
        "network_enabled": allow_network
    }

    append_audit(audit_entry)

    print("=== STDOUT ===")
    print(result.stdout)

    print("=== STDERR ===")
    print(result.stderr)

    shutil.rmtree(ephemeral_dir, ignore_errors=True)

# ==============================
# ENTRYPOINT
# ==============================

if __name__ == "__main__":

    print("\nZero-Trust Codex Runner\n")

    user_prompt = input("Enter Codex prompt: ").strip()

    full_auto = input("Enable full-auto? (yes/no): ").lower().startswith("y")
    allow_network = input("Allow network access? (yes/no): ").lower().startswith("y")

    if full_auto:
        confirm = input(
            "⚠️ Full-auto allows autonomous edits. Confirm? (type YES): "
        )
        if confirm != "YES":
            print("Aborted.")
            exit()

    run_codex_secure(user_prompt, allow_network=allow_network)
