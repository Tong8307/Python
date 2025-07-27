from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
    QComboBox, QPushButton, QSpinBox, QScrollArea, QFrame
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
        self.setWindowTitle("GPA and CGPA Calculator")
        self.setMinimumWidth(800)

        self.course_rows = []

        main_layout = QVBoxLayout()

        # Title
        title = QLabel("🎓 GPA and CGPA Calculator")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        desc = QLabel(
            "This is a GPA (Grade Point Average) and CGPA (Cumulative Grade Point Average) calculator.\n"
            "To calculate your GPA, enter the Credit and select the Grade for each course/subject.\n"
            "To calculate your CGPA, enter your current CGPA and Credits Completed prior to this semester."
        )
        desc.setStyleSheet("color: #555; margin-bottom: 10px;")
        main_layout.addWidget(desc)

        # Top fields: Current CGPA & Credits Completed
        top_layout = QHBoxLayout()
        self.cgpa_input = QLineEdit()
        self.cgpa_input.setPlaceholderText("E.g. 3.12")
        self.credits_input = QLineEdit()
        self.credits_input.setPlaceholderText("E.g. 45")

        top_layout.addWidget(self.create_labeled("Current CGPA:", self.cgpa_input))
        top_layout.addWidget(self.create_labeled("Credits Completed:", self.credits_input))
        main_layout.addLayout(top_layout)

        # Course area
        course_label = QLabel("Course (optional)")
        course_label.setStyleSheet("font-weight: bold; font-size: 18px; margin-top: 15px;")
        main_layout.addWidget(course_label)

        self.course_layout = QVBoxLayout()
        for _ in range(5):
            self.add_course_row()

        main_layout.addLayout(self.course_layout)

        # Add Course button
        add_btn = QPushButton("+ Add course")
        add_btn.setStyleSheet("""
            QPushButton {
                border: 2px dashed #673AB7;
                color: #673AB7;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F3E5F5;
            }
        """)
        add_btn.clicked.connect(self.add_course_row)
        main_layout.addWidget(add_btn)

        self.setLayout(main_layout)

    def create_labeled(self, text, widget):
        container = QVBoxLayout()
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold;")
        container.addWidget(label)
        container.addWidget(widget)
        wrapper = QWidget()
        wrapper.setLayout(container)
        return wrapper

    def add_course_row(self):
        row_layout = QHBoxLayout()

        name = QLineEdit()
        name.setPlaceholderText("Course name")

        credits = QSpinBox()
        credits.setRange(0, 10)
        credits.setSuffix(" credits")
        credits.setFixedWidth(120)

        grade = QComboBox()
        grade.addItem("Grade")
        grade.addItems(qualityPoint.keys())

        remove_btn = QPushButton("✕")
        remove_btn.setFixedWidth(30)
        remove_btn.setStyleSheet("color: gray;")
        remove_btn.clicked.connect(lambda: self.remove_course_row(row_layout))

        row_layout.addWidget(name)
        row_layout.addWidget(credits)
        row_layout.addWidget(grade)
        row_layout.addWidget(remove_btn)

        self.course_rows.append((name, credits, grade))
        self.course_layout.addLayout(row_layout)

    def remove_course_row(self, row_layout):
        for i in reversed(range(row_layout.count())):
            widget = row_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.course_layout.removeItem(row_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GPACalculatorWidget()
    window.show()
    sys.exit(app.exec_())
