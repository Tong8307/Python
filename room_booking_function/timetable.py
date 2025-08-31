from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox

class TimetablePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
            
        title = QLabel("Timetable")
        title.setObjectName("bookingHeader")
        layout.addWidget(title)
        
        # TODO: Add timetable functionality
        layout.addWidget(QLabel("Timetable view will be implemented in the next version"))
    
    def show_timetable(self):
        QMessageBox.information(self, "Coming Soon", "Timetable view will be implemented in the next version")