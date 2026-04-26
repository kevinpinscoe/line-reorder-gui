# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file PySide6 GUI tool (`line_reorder.py`) for visually reordering lines in a plain-text file. Its primary use case is reordering Pandoc book manifest files (ordered lists of Markdown source paths).

## Running

```bash
# Install dependency (Fedora)
sudo dnf install python3-pyside6
# or
pip install --user PySide6

# Run
python line_reorder.py /full/path/to/your.txt
```

## Architecture

Everything lives in `line_reorder.py`. There are no tests, no build system, and no configuration files.

**Module-level helpers:**
- `make_backup()` — copies the file with a `YYYYMMDD-HHMMSS.bak` timestamp suffix on first open
- `read_text_file()` — tries utf-8, utf-8-sig, latin-1 in order; preserves trailing-newline state
- `write_text_file()` — reconstructs the file from the list, restoring the original trailing-newline

**`LineReorderWindow(QMainWindow)`** — the entire UI:
- `QListWidget` with `InternalMove` drag-and-drop for reordering; items are also double-click editable
- `_dirty` flag drives the `*` window-title marker and save-on-close prompt
- Backup is created once at startup (or when opening another file via the dialog); subsequent saves overwrite the original in place
- `move_up()` / `move_down()` handle multi-selection correctly by iterating in the safe direction

**Key behaviors to preserve:**
- A backup is always made before any user edits are possible
- `reload_from_disk()` prompts before discarding unsaved changes
- `closeEvent()` offers Save / Discard / Cancel when dirty
- The encoding detected on read is round-tripped on write
