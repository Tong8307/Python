from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QGroupBox, QGridLayout, QHBoxLayout)
from PyQt5.QtCore import Qt
from datetime import datetime
from styles.gpa_styles import gpa_styles # Import database functions
from gpa_calculator_function.historyDetails import GPAHistoryDetails

class GPAHistory(QWidget):
    def __init__(self, parent, history_data, gpa_calculator_page):
        super().__init__()
        self.parent = parent
        self.history_data = history_data
        self.gpa_calculator_page = gpa_calculator_page
        
        self.setStyleSheet(gpa_styles())
        self.init_ui()

    def init_ui(self):
        if self.layout():
            QWidget().setLayout(self.layout())

        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("GPA Calculation History")
        title.setObjectName("gpaHeader")
        layout.addWidget(title)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if not self.history_data:
            layout.addWidget(QLabel("No history found."))
            return
        
        # Table setup
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Date", "Semester\nCredits", "Semester\nGPA", "Total\nCredits", "Current\nCGPA", "Previous\nCGPA", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        # Populate table
        for i, record in enumerate(self.history_data):
            self.table.insertRow(i)
            date_obj = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
            date_str = date_obj.strftime("%Y-%m-%d %H:%M")
            
            self.table.setItem(i, 0, QTableWidgetItem(date_str))
            self.table.setItem(i, 1, QTableWidgetItem(str(record['semester_credits'])))
            self.table.setItem(i, 2, QTableWidgetItem(f"{record['gpa']:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(str(record['total_credits'])))
            self.table.setItem(i, 4, QTableWidgetItem(f"{record['cgpa']:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{record['current_cgpa']:.2f} ({record['completed_credits']} credits)"))
            
            view_btn = QPushButton("Details")
            view_btn.clicked.connect(lambda checked, r=record: self.view_details(r))
            self.table.setCellWidget(i, 6, view_btn)

        layout.addWidget(self.table)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def view_details(self, record):
        details_page = GPAHistoryDetails(self.parent, record)
        self.parent.pages.addWidget(details_page)
        self.parent.pages.setCurrentWidget(details_page)

    def refresh_data(self, new_history_data):
        """Refresh the table with new data"""
        self.history_data = new_history_data
        self.init_ui()  # this method is to rebuild the table

    def go_back(self):
        self.parent.pages.setCurrentWidget(self.gpa_calculator_page)
        self.parent.pages.removeWidget(self)
        self.deleteLater()