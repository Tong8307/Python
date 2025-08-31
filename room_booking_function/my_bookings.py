from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class MyBookingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
            
        title = QLabel("My Bookings")
        title.setObjectName("bookingHeader")
        layout.addWidget(title)
            
        # TODO: Add actual bookings list
        layout.addWidget(QLabel("Your bookings will appear here"))