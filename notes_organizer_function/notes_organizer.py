import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QLineEdit, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class NoteOrganizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes = {}
        self.load_notes()

        main_layout = QVBoxLayout(self)

        # Button layout
        button_layout = QHBoxLayout()
        self.new_button = QPushButton("New Note")
        self.new_button.clicked.connect(self.add_note)
        self.new_button.setStyleSheet("background-color: #5bc0de; color: white; font-weight: bold; padding: 6px;")

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_note)
        self.delete_button.setStyleSheet("background-color: #0275d8; color: white; font-weight: bold; padding: 6px;")

        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.delete_button)
        main_layout.addLayout(button_layout)

        # Notebook setup
        self.notebook = QTabWidget()
        self.notebook.setStyleSheet("QTabBar::tab { font: bold 14px; padding: 8px; }")
        main_layout.addWidget(self.notebook)

        self.load_notes_into_tabs()

    def load_notes(self):
        try:
            with open("notes.json", "r") as f:
                self.notes = json.load(f)
        except FileNotFoundError:
            self.notes = {}

    def load_notes_into_tabs(self):
        for title, content in self.notes.items():
            self.create_note_tab(title, content)

    def create_note_tab(self, title, content):
        note_widget = QWidget()
        layout = QVBoxLayout(note_widget)

        note_content = QTextEdit()
        note_content.setText(content)
        note_content.setReadOnly(True)

        layout.addWidget(note_content)
        self.notebook.addTab(note_widget, title)

    def add_note(self):
        note_widget = QWidget()
        layout = QVBoxLayout(note_widget)

        title_input = QLineEdit()
        title_input.setPlaceholderText("Enter Title")
        title_input.setFont(QFont("Segoe UI", 12))

        content_input = QTextEdit()
        content_input.setPlaceholderText("Enter Content")

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("background-color: #f0ad4e; font-weight: bold; color: white; padding: 6px;")

        def save():
            title = title_input.text().strip()
            content = content_input.toPlainText().strip()

            if not title:
                QMessageBox.warning(self, "Missing Title", "Please enter a note title.")
                return

            self.notes[title] = content
            with open("notes.json", "w") as f:
                json.dump(self.notes, f)

            self.notebook.removeTab(self.notebook.currentIndex())
            self.create_note_tab(title, content)

        save_btn.clicked.connect(save)

        layout.addWidget(QLabel("Title:"))
        layout.addWidget(title_input)
        layout.addWidget(QLabel("Content:"))
        layout.addWidget(content_input)
        layout.addWidget(save_btn)

        self.notebook.addTab(note_widget, "New Note")
        self.notebook.setCurrentWidget(note_widget)

    def delete_note(self):
        index = self.notebook.currentIndex()
        if index == -1:
            return

        title = self.notebook.tabText(index)
        confirm = QMessageBox.question(self, "Delete Note",
                                       f"Are you sure you want to delete '{title}'?",
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            self.notebook.removeTab(index)
            if title in self.notes:
                self.notes.pop(title)
                with open("notes.json", "w") as f:
                    json.dump(self.notes, f)
