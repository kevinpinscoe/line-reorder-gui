#!/usr/bin/env python3
import sys
import os
import shutil
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QStatusBar, QToolBar, QStyle, QMenuBar
)
from PySide6.QtGui import QAction


def make_backup(original_path: str) -> str:
    """Create a timestamped backup next to the original file."""
    base_dir = os.path.dirname(original_path)
    base_name = os.path.basename(original_path)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_name = f"{base_name}.{ts}.bak"
    backup_path = os.path.join(base_dir, backup_name)
    shutil.copy2(original_path, backup_path)
    return backup_path


def read_text_file(path: str):
    """Read file, returning (lines_without_newline, had_trailing_newline, encoding)."""
    # Keep it simple: try utf-8, then fall back to latin-1
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    last_err = None
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc, newline="") as f:
                text = f.read()
            had_trailing_newline = text.endswith("\n")
            lines = text.splitlines()
            return lines, had_trailing_newline, enc
        except Exception as e:
            last_err = e
            continue
    raise last_err


def write_text_file(path: str, lines, had_trailing_newline: bool, encoding: str):
    text = "\n".join(lines)
    if had_trailing_newline and (not text.endswith("\n")):
        text += "\n"
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write(text)


class LineReorderWindow(QMainWindow):
    def __init__(self, file_path: str):
        super().__init__()
        self.setWindowTitle(f"Line Reorder — {file_path}")
        self.file_path = file_path
        self.encoding = "utf-8"
        self.had_trailing_newline = True
        self._dirty = False
        self._backup_path = None

        # Central UI
        central = QWidget(self)
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)

        # List widget with drag & drop reordering
        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.ExtendedSelection)
        self.list.setDragDropMode(QListWidget.InternalMove)
        self.list.setDefaultDropAction(Qt.MoveAction)
        self.list.setAlternatingRowColors(True)
        self.list.setEditTriggers(QListWidget.DoubleClicked | QListWidget.EditKeyPressed)
        self.list.model().rowsMoved.connect(self._on_rows_moved)
        self.list.itemChanged.connect(self._on_item_changed)
        vbox.addWidget(self.list, 1)

        # Buttons
        hbox = QHBoxLayout()
        self.btn_up = QPushButton("Move Up")
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down = QPushButton("Move Down")
        self.btn_down.clicked.connect(self.move_down)
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_file)
        self.btn_reload = QPushButton("Reload")
        self.btn_reload.clicked.connect(self.reload_from_disk)
        hbox.addWidget(self.btn_up)
        hbox.addWidget(self.btn_down)
        hbox.addStretch(1)
        hbox.addWidget(self.btn_reload)
        hbox.addWidget(self.btn_save)
        vbox.addLayout(hbox)

        # Toolbar & menu
        self._build_toolbar_menu()

        # Status bar
        sb = QStatusBar()
        self.setStatusBar(sb)

        # Load file & make a backup upfront
        self.load_file_first_time()

    # ----- Setup helpers -----
    def _build_toolbar_menu(self):
        tb = QToolBar("Main")
        tb.setIconSize(self.style().standardIcon(QStyle.SP_DirIcon).actualSize(tb.iconSize()))
        self.addToolBar(tb)

        act_open = QAction("Open…", self)
        act_open.triggered.connect(self.open_other_file)
        act_save = QAction("Save", self)
        act_save.setShortcut("Ctrl+S")
        act_save.triggered.connect(self.save_file)
        act_reload = QAction("Reload", self)
        act_reload.triggered.connect(self.reload_from_disk)
        act_quit = QAction("Quit", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)

        tb.addAction(act_open)
        tb.addAction(act_save)
        tb.addAction(act_reload)

        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(act_open)
        file_menu.addAction(act_save)
        file_menu.addAction(act_reload)
        file_menu.addSeparator()
        file_menu.addAction(act_quit)
        self.setMenuBar(menubar)

    # ----- File I/O -----
    def load_file_first_time(self):
        if not os.path.isfile(self.file_path):
            QMessageBox.critical(self, "Error", f"Not a file: {self.file_path}")
            sys.exit(2)

        # Backup once at startup (as requested)
        try:
            self._backup_path = make_backup(self.file_path)
            self.statusBar().showMessage(f"Backup created: {self._backup_path}", 7000)
        except Exception as e:
            QMessageBox.warning(self, "Backup failed", f"Could not create backup:\n{e}")

        self._load_into_list()

    def _load_into_list(self):
        try:
            lines, had_newline, enc = read_text_file(self.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file:\n{e}")
            return

        self.encoding = enc
        self.had_trailing_newline = had_newline

        self.list.clear()
        # Allow editing: ItemIsEditable flag
        for ln in lines:
            it = QListWidgetItem(ln)
            it.setFlags(it.flags() | Qt.ItemIsEditable)
            self.list.addItem(it)

        self._dirty = False
        self._update_window_title()

    def reload_from_disk(self):
        if self._dirty:
            r = QMessageBox.question(
                self, "Discard changes?",
                "Reloading will discard unsaved changes. Continue?"
            )
            if r != QMessageBox.Yes:
                return
        self._load_into_list()
        self.statusBar().showMessage("Reloaded from disk", 4000)

    def save_file(self):
        lines = [self.list.item(i).text() for i in range(self.list.count())]
        try:
            write_text_file(self.file_path, lines, self.had_trailing_newline, self.encoding)
            self._dirty = False
            self._update_window_title()
            self.statusBar().showMessage("Saved", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"Could not save file:\n{e}")

    def open_other_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open text file", os.path.dirname(self.file_path), "Text files (*)")
        if not path:
            return
        self.file_path = path
        self.setWindowTitle(f"Line Reorder — {self.file_path}")
        try:
            self._backup_path = make_backup(self.file_path)
            self.statusBar().showMessage(f"Backup created: {self._backup_path}", 7000)
        except Exception as e:
            QMessageBox.warning(self, "Backup failed", f"Could not create backup:\n{e}")
        self._load_into_list()

    # ----- Dirty tracking -----
    def _on_rows_moved(self, *args):
        self._dirty = True
        self._update_window_title()

    def _on_item_changed(self, item):
        self._dirty = True
        self._update_window_title()

    def _update_window_title(self):
        mark = " *" if self._dirty else ""
        self.setWindowTitle(f"Line Reorder — {self.file_path}{mark}")

    # ----- Line movement -----
    def selected_rows(self):
        # Return selected row indices sorted
        rows = sorted({i.row() for i in self.list.selectedIndexes()})
        return rows

    def move_up(self):
        rows = self.selected_rows()
        if not rows or rows[0] == 0:
            return
        for r in rows:
            item = self.list.takeItem(r)
            self.list.insertItem(r - 1, item)
            item.setSelected(True)
        self._on_rows_moved()

    def move_down(self):
        rows = self.selected_rows()
        if not rows:
            return
        # Move from bottom up to avoid index shifting issues
        max_idx = self.list.count() - 1
        if rows[-1] == max_idx:
            return
        for r in reversed(rows):
            item = self.list.takeItem(r)
            self.list.insertItem(r + 1, item)
            item.setSelected(True)
        self._on_rows_moved()

    # ----- Close handling -----
    def closeEvent(self, event):
        if self._dirty:
            r = QMessageBox.question(
                self, "Unsaved changes",
                "You have unsaved changes. Save before quitting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            if r == QMessageBox.Cancel:
                event.ignore()
                return
            elif r == QMessageBox.Yes:
                self.save_file()
        event.accept()


def main():
    if len(sys.argv) != 2:
        print("Usage: line_reorder.py /full/path/to/file.txt", file=sys.stderr)
        sys.exit(1)

    file_path = os.path.abspath(sys.argv[1])
    app = QApplication(sys.argv)
    win = LineReorderWindow(file_path)
    win.resize(900, 600)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
