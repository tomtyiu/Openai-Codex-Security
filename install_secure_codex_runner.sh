#!/usr/bin/env bash

# ============================================================
# Enterprise Zero-Trust Codex Runner Installer
# Target: Ubuntu/Debian Linux
# Installs:
#   - Docker
#   - Optional gVisor runtime
#   - Python3 + pip
#   - Secure Codex runner files
#   - Seccomp profile
#   - Workspace directory
#   - Audit secret
# ============================================================

set -e

echo "\n🔐 Starting Secure Codex Runner Installation...\n"

# ------------------------------------------------------------
# 1. Install Docker
# ------------------------------------------------------------

echo "Installing Docker..."

sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

ARCH=$(dpkg --print-architecture)
CODENAME=$(lsb_release -cs)

echo \
  "deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $CODENAME stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER

echo "Docker installed."

# ------------------------------------------------------------
# 2. Install Optional gVisor Runtime
# ------------------------------------------------------------

read -p "Install gVisor runtime (recommended for enterprise)? (y/n): " INSTALL_GVISOR

if [[ "$INSTALL_GVISOR" == "y" ]]; then
  echo "Installing gVisor..."
  sudo apt install -y runsc
  echo "gVisor installed."
fi

# ------------------------------------------------------------
# 3. Install Python
# ------------------------------------------------------------

echo "Installing Python..."
sudo apt install -y python3 python3-pip

# ------------------------------------------------------------
# 4. Create Project Structure
# ------------------------------------------------------------

echo "Creating project files..."

mkdir -p secure-codex-runner
cd secure-codex-runner
mkdir -p workspace

# ------------------------------------------------------------
# 5. Create Seccomp Profile
# ------------------------------------------------------------

cat <<EOF > seccomp-restrict.json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "read", "write", "exit", "exit_group",
        "fstat", "mmap", "munmap", "brk",
        "rt_sigaction", "rt_sigprocmask",
        "clone", "execve", "arch_prctl",
        "set_tid_address", "set_robust_list",
        "prlimit64", "getrandom"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
EOF

# ------------------------------------------------------------
# 6. Create Secure Codex Runner
# ------------------------------------------------------------

cat <<'EOF' > secure_codex_runner.py
# (PASTE FULL PYTHON SCRIPT FROM PREVIOUS MESSAGE HERE)
EOF

# ------------------------------------------------------------
# 7. Generate Audit Secret
# ------------------------------------------------------------

echo "Generating audit signing secret..."
AUDIT_SECRET=$(openssl rand -hex 32)
echo "export CODEX_AUDIT_SECRET=$AUDIT_SECRET" >> ~/.bashrc

echo "\nAudit secret added to ~/.bashrc"

# ------------------------------------------------------------
# 8. Final Instructions
# ------------------------------------------------------------

echo "\n✅ Installation Complete"
echo ""
echo "Next Steps:"
echo "1. Log out and log back in (for Docker group permissions)."
echo "2. cd secure-codex-runner"
echo "3. python3 secure_codex_runner.py"
echo ""
echo "Workspace directory: secure-codex-runner/workspace"
echo "Audit log file: secure-codex-runner/codex_audit.log"
echo ""
echo "🔐 Secure Codex Runner Ready."
