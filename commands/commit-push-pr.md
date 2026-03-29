---
description: Stage changes, create conventional commit, push, and open/update PR
allowed-tools:
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git push:*)
  - Bash(git branch:*)
  - Bash(gh pr:*)
  - Read
---

# Commit, Push & Create PR

Automates the git workflow: review changes, stage, commit with conventional message, push, and create or update PR.

## Process

1. **Check current state**
   - Run `git status` to see all untracked files (never use -uall flag)
   - Run `git diff HEAD` to see staged and unstaged changes
   - Run `git branch` to confirm current branch

2. **Review the diff**
   - Analyze changes for correctness and scope
   - Ensure changes align with a single feature/fix

3. **Generate commit message**
   - Use conventional commit format: `type(scope): description`
   - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
   - Include feature/bug IDs if applicable
   - Summary under 70 chars, detailed body if needed

4. **Stage and commit**
   - Run `git add` for specific files (avoid `git add .`)
   - Create commit with message via heredoc
   - Include co-author footer

5. **Push to remote**
   - Run `git push` (use `-u` flag if branch doesn't track remote)

6. **Create or update PR**
   - Check if PR exists for current branch
   - If exists, notify user that changes are pushed
   - If not, create PR using `gh pr create` with title and body
   - Body includes: summary, test plan, and generation note
