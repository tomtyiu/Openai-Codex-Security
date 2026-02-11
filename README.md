# Openai-Codex-Security
Setup for least privilege OpenAI's Codex in local systems

## Install
Follow procedure to install OpenAI's Codex
npm
```
npm i -g @openai/codex
```


## Command for security
### Sandbox policy for model-generated commands. Defaults to configuration.
allow only write on workspace folder currently running codex
```
codex --sandbox workspace-write ## workspace write
```

### read-only
Read only, do not write permissions on the system
```
codex --sandbox read-only 
```
### Run arbitrary commands inside Codex-provided macOS seatbelt or Linux sandboxes (Landlock by default, optional bubblewrap pipeline).
```
codex sandbox
```

## For codex's command line security:
```
codex
>/permission #set to Read Only
```

## Codex can read and edit files but asks for approval before running untrusted commands.
```
codex --sandbox workspace-write --ask-for-approval untrusted
```

### to avoid any security issues, please do not run:
Run every command without approvals or sandboxing. **Only use inside an externally hardened environment.**
```
codex --dangerously-bypass-approvals-and-sandbox, --yolo
```

Reference:
- (OpenAI's Codex Security)[https://developers.openai.com/codex/security]
