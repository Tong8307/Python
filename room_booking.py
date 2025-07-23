from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class RoomBookingWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)

        label = QLabel("📅 Room Booking Page")
        label.setStyleSheet("font-size: 24px;")
        layout.addWidget(label)

        back_btn = QPushButton("← Back to Home")
        back_btn.clicked.connect(self.go_back)
        layout.addWidget(back_btn)

    def go_back(self):
        self.main_window.pages.setCurrentWidget(self.main_window.feature_grid_page)
