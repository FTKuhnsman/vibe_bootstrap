---
description: Security audit. Scan repo for leaked secrets, credentials, PII, and .gitignore gaps.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(git log:*)
  - Bash(git diff:*)
  - Agent
---

# Security Audit

Comprehensive security audit of the repository to detect leaked secrets, credentials, sensitive data, and configuration gaps.

## Process

1. **Scan for secrets and credentials**
   - Search all files for patterns that indicate hardcoded secrets:
     - API keys: `api_key`, `apikey`, `api-key`, `AKIA` (AWS access key prefix)
     - Tokens: `token`, `bearer`, `jwt`, `session`
     - Passwords: `password`, `passwd`, `pwd`, `secret`
     - Connection strings: `://.*:.*@` (URI with embedded credentials), `DATABASE_URL`, `REDIS_URL`
     - Cloud credentials: `aws_secret`, `aws_access`, `gcp`, `azure`, `GOOGLE_APPLICATION_CREDENTIALS`
     - Private keys: `BEGIN RSA PRIVATE KEY`, `BEGIN OPENSSH PRIVATE KEY`, `BEGIN EC PRIVATE KEY`, `BEGIN PGP PRIVATE KEY`
     - OAuth: `client_secret`, `oauth`, `refresh_token`
     - Webhooks: `hooks.slack.com`, `discord.com/api/webhooks`
   - Distinguish real secrets from documentation references, template placeholders, and variable names
   - Check for base64-encoded strings longer than 40 characters that may be obfuscated secrets

2. **Check for committed environment and config files**
   - Search for `.env`, `.env.local`, `.env.production`, `.env.*` files in the working tree
   - Check for config files with embedded credentials: `config.json`, `credentials.json`, `secrets.yaml`, `application.properties`
   - Look for certificate and key files: `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.crt`, `*.der`, `*.jks`
   - Verify no SSH keys (`id_rsa`, `id_ed25519`, etc.) are committed

3. **Audit `.gitignore` coverage**
   - Read `.gitignore` (and any nested `.gitignore` files)
   - Verify these patterns are excluded:
     - `.env*` (environment files)
     - `*.key`, `*.pem`, `*.p12`, `*.pfx`, `*.crt` (certificates and keys)
     - `.aws/`, `.gcp/`, `.azure/` (cloud credential directories)
     - `credentials.json`, `secrets.*` (credential files)
   - Flag any missing patterns as WARNING

4. **Check for PII and internal references**
   - Hardcoded filesystem paths revealing usernames (e.g., `C:\Users\<name>`, `/home/<name>`, `/Users/<name>`)
   - Internal hostnames, private IP addresses (`10.*`, `172.16-31.*`, `192.168.*`)
   - Email addresses outside of standard git config context
   - Phone numbers, physical addresses, or other personal data
   - Internal or proprietary service URLs not meant for public exposure

5. **Review git history for leaked secrets**
   - Run `git log --all --diff-filter=D --name-only` to find deleted files that may have contained secrets
   - Run `git log --all -p -S "password" --since="6 months ago" -- . ":(exclude)*.md"` to search for secrets added then removed
   - Run `git log --all -p -S "BEGIN RSA" --since="6 months ago"` to check for committed private keys
   - Run `git log --all -p -S "AKIA" --since="6 months ago"` to check for AWS keys
   - If any secrets were ever committed and removed, flag as CRITICAL — they are still in git history

6. **Report findings**

## Output Format

```
═══════════════════════════════════════════════════════════════
  SECURITY AUDIT REPORT
═══════════════════════════════════════════════════════════════

CRITICAL (action required):
  🔴 [file:line] Description of finding
     Recommended fix: [what to do]

WARNING (should fix):
  🟡 [file] Description of finding
     Recommended fix: [what to do]

INFO (review recommended):
  🔵 [file] Description of finding

.GITIGNORE COVERAGE:
  ✓ .env* excluded
  ✗ *.pem not excluded — add to .gitignore
  ...

GIT HISTORY:
  ✓ No secrets found in commit history
  — or —
  🔴 Secret found in commit [hash]: [description]
     Recommended fix: Rotate the credential immediately,
     then use git-filter-repo or BFG to purge history

SUMMARY:
  Files scanned: N
  Critical: N | Warning: N | Info: N
  Status: PASS / FAIL

═══════════════════════════════════════════════════════════════
```

## Tips

- A PASS means no CRITICAL findings. Warnings and info items are advisory.
- If secrets were ever committed to git history, they must be rotated even if removed — git history is permanent unless rewritten.
- For repos being made public, also consider: license compliance, internal documentation references, and TODO comments with internal context.
