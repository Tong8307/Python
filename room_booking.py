from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import sqlite3

class RoomBookingWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.layout = QVBoxLayout(self)

        title_label = QLabel("🗓️ My Room Bookings")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        self.layout.addWidget(title_label)

        self.load_bookings()

        back_btn = QPushButton("← Back to Home")
        back_btn.clicked.connect(self.go_back)
        back_btn.setStyleSheet("margin-top: 20px; padding: 8px;")
        self.layout.addWidget(back_btn)

    def go_back(self):
        self.main_window.pages.setCurrentWidget(self.main_window.feature_grid_page)
