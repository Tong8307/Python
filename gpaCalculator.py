from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QApplication, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt
import sys

qualityPoint = {
    "A+": 4.00, "A": 4.00, "A-": 3.67,
    "B+": 3.33, "B": 3.00, "B-": 2.67,
    "C+": 2.33, "C": 2.00, "F": 0.00
}

class GPACalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Current CGPA section
        self.current_cgpa_label = QLabel("Enter current CGPA:")
        self.current_cgpa_input = QLineEdit()
        layout.addWidget(self.current_cgpa_label)
        layout.addWidget(self.current_cgpa_input)

        self.completed_credit_label = QLabel("Enter completed credit hours:")
        self.completed_credit_input = QLineEdit()
        layout.addWidget(self.completed_credit_label)
        layout.addWidget(self.completed_credit_input)

        self.new_gpa_label = QLabel("Enter GPA for new semester:")
        self.new_gpa_input = QLineEdit()
        layout.addWidget(self.new_gpa_label)
        layout.addWidget(self.new_gpa_input)

        self.new_credit_label = QLabel("Enter credit hours for new semester:")
        self.new_credit_input = QLineEdit()
        layout.addWidget(self.new_credit_label)
        layout.addWidget(self.new_credit_input)

        self.calculate_btn = QPushButton("Calculate CGPA")
        self.calculate_btn.clicked.connect(self.calculate_gpa)
        layout.addWidget(self.calculate_btn)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def add_subject_row(self):
        h_layout = QHBoxLayout()

        name_input = QLineEdit()
        name_input.setPlaceholderText("Subject Name")
        credit_input = QLineEdit()
        credit_input.setPlaceholderText("Credit Hours")
        grade_input = QComboBox()
        grade_input.addItems(qualityPoint.keys())

        h_layout.addWidget(name_input)
        h_layout.addWidget(credit_input)
        h_layout.addWidget(grade_input)

        self.subject_rows.append((name_input, credit_input, grade_input))
        self.entry_area.addLayout(h_layout)

    def calculate_gpa(self):
        try:
            current_cgpa = float(self.current_cgpa_input.text())
            completed_credits = float(self.completed_credit_input.text())
            new_gpa = float(self.new_gpa_input.text())
            new_credits = float(self.new_credit_input.text())

            total_points = current_cgpa * completed_credits + new_gpa * new_credits
            total_credits = completed_credits + new_credits
            new_cgpa = total_points / total_credits

            self.result_label.setText(f"Your new CGPA is: {new_cgpa:.2f}")
        except:
            self.result_label.setText("Please enter valid numbers.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GPACalculatorWidget()
    window.show()
    sys.exit(app.exec_())