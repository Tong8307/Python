from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QListWidget, QStackedWidget
)
from PyQt5.QtCore import Qt


class DashboardWidget(QWidget):
    def __init__(self, on_add_note_clicked=None):
        super().__init__()
        self.on_add_note_clicked = on_add_note_clicked
        self.setWindowTitle("Note Organizer Dashboard")

        self.setMinimumSize(700, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setup_top_nav()
        self.setup_folder_and_note_area()
        self.setup_footer()

    def setup_top_nav(self):
        top_bar = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setFixedWidth(300)

        self.add_button = QPushButton("+")
        self.add_button.setFixedSize(30, 30)
        self.add_button.setToolTip("Add Note / Folder / Import")
        self.add_button.clicked.connect(self.handle_add_note_click)

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.search_bar)
        top_bar.addWidget(self.add_button)

        self.layout.addLayout(top_bar)

    def handle_add_note_click(self):
        if self.on_add_note_clicked:
            self.on_add_note_clicked()

    def setup_folder_and_note_area(self):
        main_area = QHBoxLayout()

        self.folder_list = QListWidget()
        self.folder_list.setFixedWidth(150)
        self.folder_list.setStyleSheet("QListWidget { background-color: #f8f8f8; }")
        self.folder_list.addItem("All Notes")
        self.folder_list.addItem("Uncategorized")

        notes_area = QVBoxLayout()

        filter_bar = QHBoxLayout()

        self.filter_dropdown = QComboBox()
        self.filter_dropdown.setFixedWidth(120)
        self.filter_dropdown.addItems(["Sort by Date", "Sort by Name", "Sort by Type"])

        self.view_toggle_button = QPushButton("View")
        self.view_toggle_button.setFixedWidth(60)

        self.edit_button = QPushButton("Edit")
        self.edit_button.setFixedWidth(60)

        filter_bar.addWidget(QLabel("Filter:"))
        filter_bar.addWidget(self.filter_dropdown)
        filter_bar.addStretch()
        filter_bar.addWidget(self.view_toggle_button)
        filter_bar.addWidget(self.edit_button)

        self.notes_container = QStackedWidget()
        self.grid_view = QLabel("📋 Grid View (to be added)")
        self.list_view = QLabel("📄 List View (to be added)")
        self.notes_container.addWidget(self.grid_view)
        self.notes_container.addWidget(self.list_view)

        notes_area.addLayout(filter_bar)
        notes_area.addWidget(self.notes_container)

        main_area.addWidget(self.folder_list)
        main_area.addLayout(notes_area)

        self.layout.addLayout(main_area)

    def setup_footer(self):
        footer = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 11px;")
        footer.addWidget(self.status_label)
        self.layout.addLayout(footer)
