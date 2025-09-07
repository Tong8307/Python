from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, 
                             QFrame, QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class GuidelinesPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
            
        title = QLabel("Booking Guidelines & Terms of Use")
        title.setObjectName("bookingHeader")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create scroll area for guidelines
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("guidelinesScroll")
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for guidelines content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Guidelines sections
        guidelines = [
            {
                "title": "⏰ Time Restrictions",
                "content": [
                    "• Bookings are available from 8:00 AM to 6:00 PM only",
                    "• Maximum booking duration: 2 hours per session",
                    "• Time slots are in 30-minute intervals (e.g., 08:00, 08:30, 09:00)"
                ]
            },
            {
                "title": "📅 Advance Booking",
                "content": [
                    "• Bookings can be made up to 1 week in advance",
                    "• Same-day bookings are allowed subject to availability",
                    "• Bookings must be made at least 1 hour in advance"
                ]
            },
            {
                "title": "❌ Cancellation Policy",
                "content": [
                    "• Bookings can be cancelled up to 1 hour before the scheduled time"
                ]
            },
            {
                "title": "🏫 Room Usage",
                "content": [
                    "• Please leave the room in the same condition as you found it",
                    "• Report any issues or damages immediately to facility staff",
                    "• No food or drinks allowed in computer labs and special equipment rooms",
                    "• Keep noise levels appropriate for academic environments"
                ]
            },
            {
                "title": "🎓 Student Requirements",
                "content": [
                    "• All attendees must be valid students with active IDs",
                    "• The booking student is responsible for the room during the booked time",
                    "• Maximum of 10 students per booking (including the booker)",
                    "• Student IDs must be presented upon request"
                ]
            },
            {
                "title": "⚖️ Compliance & Regulations",
                "content": [
                    "• Users must comply with all institutional policies and codes of conduct",
                    "• Misuse of facilities may result in disciplinary action",
                    "• Rooms must be used for academic purposes only",
                    "• Commercial activities are strictly prohibited"
                ]
            },
            {
                "title": "🔰 General Information",
                "content": [
                    "• Technical support available during office hours",
                    "• For emergencies, contact campus security at extension 09123456789"
                ]
            }
        ]
        
        # Add guidelines sections
        for section in guidelines:
            section_frame = QFrame()
            section_frame.setObjectName("guidelineSection")
            section_frame.setStyleSheet("""
                QFrame#guidelineSection {
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            
            section_layout = QVBoxLayout(section_frame)
            section_layout.setSpacing(10)
            
            # Section title
            title_label = QLabel(section["title"])
            title_label.setObjectName("guidelineTitle")
            title_label.setStyleSheet("""
                QLabel#guidelineTitle {
                    font-size: 16px;
                    font-weight: bold;
                    color: #283593;
                    padding-bottom: 5px;
                }
            """)
            section_layout.addWidget(title_label)
            
            # Section content
            for point in section["content"]:
                point_label = QLabel(point)
                point_label.setObjectName("guidelinePoint")
                point_label.setStyleSheet("""
                    QLabel#guidelinePoint {
                        font-size: 14px;
                        color: #495057;
                        padding-left: 10px;
                        margin: 2px;
                    }
                """)
                point_label.setWordWrap(True)
                section_layout.addWidget(point_label)
            
            content_layout.addWidget(section_frame)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

    def show_guidelines(self):
        """Method to show guidelines - called when page is displayed"""
        # This method is called when the page is shown, so we don't need to do anything extra
        # since the content is already displayed in the layout
        pass