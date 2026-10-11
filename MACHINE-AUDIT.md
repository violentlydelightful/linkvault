# Machine Self-Sufficiency Audit (2026-06-16)

## Self-sufficient on this box? -> With caveats

## Issues found
- Git: repo OK, remote `origin` = github.com/violentlydelightful/linkvault, `main` fully pushed (0/0), clean tree.
- Mac dependency: NONE. No `/Users/` paths, no launchctl/plist/pbcopy/osascript.
- Secrets/auth: no `.env`/token/credential files found in the repo. Nothing Mac-local.
- Runnability: Python project (`requirements.txt` present). No `.venv`/`venv` — dependencies are NOT installed. App will not run until a virtualenv is created and `pip install -r requirements.txt` is done.

## Fixed this pass
- None needed.

## Outstanding (needs Brad)
- Create a venv and `pip install -r requirements.txt` before running.
- If the app needs runtime secrets (e.g. a DB/analytics config), confirm where they come from — none are present in the repo, so verify nothing is silently expected from a Mac-local file.
