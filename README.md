# Openai-Codex-Security — Least Privilege Setup for OpenAI Codex CLI

## Overview

This repository provides security and safety guidance for running OpenAI Codex CLI using least-privilege principles.

Codex operates with strict read-only permissions by default. Additional configuration can further reduce risk and strengthen execution isolation. This documentation describes recommended sandbox policies, command-line safeguards, and operational hardening practices.

This guidance applies **only to the OpenAI Codex CLI**. It does not apply to the Codex application or web interface.

---

## Installation

Install the OpenAI Codex CLI using npm:

```bash
npm i -g @openai/codex
```

---

## Security Principles

- Enforce least privilege
- Restrict write access to the workspace only
- Prefer read-only execution when possible
- Use sandbox isolation for model-generated commands
- Require approval before executing untrusted commands
- Avoid bypassing security protections

---

## Sandbox Security Controls

### Workspace Write Policy

Allow write access only to the workspace directory currently running Codex.

```bash
codex --sandbox workspace-write
```

---

### Read-Only Mode

No write permissions granted to the system.

```bash
codex --sandbox read-only
```

---

### Run Commands Inside Codex Sandboxed Environment

Executes arbitrary commands inside Codex-provided macOS seatbelt or Linux sandbox environments.

Linux uses Landlock by default with optional bubblewrap pipeline.

```bash
codex sandbox
```

---

## Command-Line Permission Controls

Start Codex CLI and configure permission level:

```bash
codex
>/permission
```

Set permission mode to **Read Only** for maximum safety.

---

## Controlled Execution with Approval

Codex can read and edit files but requests approval before executing untrusted commands.

```bash
codex --sandbox workspace-write --ask-for-approval untrusted
```

---

## High-Risk Command to Avoid

Runs all commands without approvals or sandboxing. Only use inside externally hardened environments.

```bash
codex --dangerously-bypass-approvals-and-sandbox
codex --yolo
```

---

## Recommended Isolation Strategies

For maximum security, run Codex CLI inside:

- Containerized environment (Docker)
- Virtual machine
- Dedicated sandboxed host

Combine external isolation with Codex sandbox policies for defense-in-depth protection.

---

## Reference Documentation

- OpenAI Codex Security: https://developers.openai.com/codex/security

---

## Disclaimer

These recommendations are security best practices. Implementation requirements vary depending on system architecture, operational risk tolerance, and organizational security policy.

Always perform independent security validation before production deployment.

---

## License

Specify license for this repository.

Example:

MIT License

---

## Contributions

Security improvements and hardening recommendations are welcome. Submit issues or pull requests to help strengthen operational safety.

## Modify by OpenAI's ChatGPT
