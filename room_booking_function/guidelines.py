from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox

class GuidelinesPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
            
        title = QLabel("Guidelines")
        title.setObjectName("bookingHeader")
        layout.addWidget(title)
        
        # TODO: Add guidelines content
        layout.addWidget(QLabel("Booking guidelines will be shown here"))
    
    def show_guidelines(self):
        guidelines = """
        Booking Guidelines & Terms of Use:
        
        1. Time Restrictions:
           - Bookings are available from 8:00 AM to 6:00 PM only
           - Maximum booking duration: 2 hours
        
        2. Advance Booking:
           - Bookings can be made up to 1 week in advance
           - Same-day bookings are allowed
        
        3. Cancellation Policy:
           - Bookings can be cancelled up to 1 hour before the scheduled time
           - Frequent no-shows may result in booking privileges being suspended
        
        4. Room Usage:
           - Please leave the room in the same condition as you found it
           - Report any issues or damages immediately
        
        5. Student Requirements:
           - All attendees must be valid students
           - The booking student is responsible for the room during the booked time
        
        6. Compliance:
           - Users must comply with all institutional policies
           - Misuse of facilities may result in disciplinary action
        """
        QMessageBox.information(self, "Booking Guidelines", guidelines)