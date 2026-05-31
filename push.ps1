# Usage: .\push.ps1 "your commit message"
# Stages all changes, commits, and pushes to GitHub in one step.
param([string]$msg = "")

if (-not $msg) {
    $msg = "update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

git add app.py pages/ utils/ requirements.txt AGENTS.md CLAUDE.md docs/
git commit -m $msg
git push
