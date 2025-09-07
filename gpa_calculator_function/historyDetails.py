from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGroupBox, QGridLayout, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from datetime import datetime
from styles.gpa_styles import gpa_styles

class GPAHistoryDetails(QWidget):
    def __init__(self, parent, record):
        super().__init__()
        self.record = record
        self.parent = parent

        self.setStyleSheet(gpa_styles())
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20) 

        # Title
        title = QLabel("History Details")
        title.setObjectName("gpaHeader")
        layout.addWidget(title)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addSpacing(20)

        # Date - create a simple layout for better spacing
        date_layout = QVBoxLayout()
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(2)
        
        date_obj = datetime.fromisoformat(self.record['timestamp'].replace('Z', '+00:00'))
        date_label = QLabel(f"Date: {date_obj.strftime('%Y-%m-%d %H:%M')}")
        date_layout.addWidget(date_label)
        
        layout.addLayout(date_layout)
        layout.addSpacing(20)

        # Results section
        results_group = QGroupBox("Results")
        results_group.setContentsMargins(10, 20, 10, 10)  # Reduce group box internal margins
        results_layout = QGridLayout(results_group)
        results_layout.setSpacing(15)  # Reduced spacing between grid items
        results_layout.setContentsMargins(15, 15, 15, 15)  # Internal margins

        results_layout.addWidget(QLabel("Input CGPA:"), 0, 0)
        results_layout.addWidget(QLabel(f"{self.record['current_cgpa']:.2f}"), 0, 1)

        results_layout.addWidget(QLabel("Completed Credits:"), 1, 0)
        results_layout.addWidget(QLabel(str(self.record['completed_credits'])), 1, 1)

        results_layout.addWidget(QLabel("Semester Credits:"), 2, 0)
        results_layout.addWidget(QLabel(str(self.record['semester_credits'])), 2, 1)

        results_layout.addWidget(QLabel("GPA:"), 3, 0)
        results_layout.addWidget(QLabel(f"{self.record['gpa']:.2f}"), 3, 1)

        results_layout.addWidget(QLabel("Total Credits:"), 4, 0)
        results_layout.addWidget(QLabel(str(self.record['total_credits'])), 4, 1)

        results_layout.addWidget(QLabel("CGPA:"), 5, 0)
        results_layout.addWidget(QLabel(f"{self.record['cgpa']:.2f}"), 5, 1)

        layout.addWidget(results_group)

        # Courses section
        courses_group = QGroupBox("Courses")
        courses_group.setContentsMargins(10, 20, 10, 10)
        courses_layout = QVBoxLayout(courses_group)
        courses_layout.setSpacing(15)
        courses_layout.setContentsMargins(15, 15, 15, 15)

        if self.record['courses_data']:
            for course in self.record['courses_data']:
                course_text = f"{course['name']} - {course['credits']} credits - Grade: {course['grade']}"
                course_label = QLabel(course_text)
                courses_layout.addWidget(course_label)
        else:
            courses_layout.addWidget(QLabel("No course data available"))

        layout.addSpacing(20)
        layout.addWidget(courses_group)

        # Add a spacer to push everything to the top if needed
        layout.addStretch()