from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
    QComboBox, QPushButton, QSpinBox
)
from PyQt5.QtCore import Qt
import sys
from styles.gpa_styles import gpa_styles

qualityPoint = {
    "A+": 4.00, "A": 4.00, "A-": 3.67,
    "B+": 3.33, "B": 3.00, "B-": 2.67,
    "C+": 2.33, "C": 2.00, "F": 0.00
}

class GPACalculatorWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        self.setStyleSheet(gpa_styles())

        # Main layout with proper spacing
        main_layout = QVBoxLayout(self)
        self.setWindowTitle("GPA and CGPA Calculator")  
        self.course_rows = []

        main_layout = QVBoxLayout(self)

        title = QLabel("GPA and CGPA Calculator")
        title.setObjectName("title")

        desc = QLabel(
            "This is a GPA (Grade Point Average) and CGPA (Cumulative Grade Point Average) calculator.\n"
            "To calculate your GPA, enter the Credit and select the Grade for each course/subject.\n"
            "To calculate your CGPA, enter your current CGPA and Credits Completed prior to this semester."
        )
        desc.setObjectName("desc")

        main_layout.addWidget(title)  # ✅ Not a string
        main_layout.addWidget(desc)

        top_layout = QHBoxLayout()
        self.cgpa_input = QLineEdit()
        self.cgpa_input.setPlaceholderText("E.g. 3.75")
        self.cgpa_input.textChanged.connect(self.update_results)

        self.credits_input = QLineEdit()
        self.credits_input.setPlaceholderText("E.g. 45")
        self.credits_input.textChanged.connect(self.update_results)

        top_layout.addWidget(self.create_labeled("Current CGPA:", self.cgpa_input))
        top_layout.addWidget(self.create_labeled("Credits Completed:", self.credits_input))
        main_layout.addLayout(top_layout)

        course_label = QLabel("Courses (optional):")
        course_label.setObjectName("course_label")
        main_layout.addWidget(course_label)

        # Result panel
        result_panel = QVBoxLayout()

        self.semester_credits_label = QLabel("0")
        self.semester_credits_label.setObjectName("resultLabel")
        self.gpa_label = QLabel("0")
        self.gpa_label.setObjectName("resultLabel")
        self.total_credits_label = QLabel("0")
        self.total_credits_label.setObjectName("resultLabel")
        self.cgpa_label = QLabel("0")
        self.cgpa_label.setObjectName("resultLabel")

        result_panel.addWidget(QLabel("Semester Credits:"))
        result_panel.addWidget(self.semester_credits_label)
        result_panel.addWidget(QLabel("GPA:"))
        result_panel.addWidget(self.gpa_label)
        result_panel.addWidget(QLabel("Total Credits:"))
        result_panel.addWidget(self.total_credits_label)
        result_panel.addWidget(QLabel("CGPA:"))
        result_panel.addWidget(self.cgpa_label)

        layout_wrapper = QHBoxLayout()
        layout_wrapper.addLayout(main_layout, 3)
        layout_wrapper.addLayout(result_panel, 1)

        self.setLayout(layout_wrapper)
        self.update_results()

        self.course_layout = QVBoxLayout()

        for _ in range(5):
            self.add_course_row()

        main_layout.addLayout(self.course_layout)

        add_btn = QPushButton("+ Add course")
        add_btn.setObjectName("addCourseButton")
        add_btn.clicked.connect(self.add_course_row)
        main_layout.addWidget(add_btn)

    def create_labeled(self, text, widget):
        self.setStyleSheet(gpa_styles())
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
        credits.valueChanged.connect(self.update_results)

        grade = QComboBox()
        grade.addItem("Grade")
        grade.addItems(qualityPoint.keys())
        grade.currentIndexChanged.connect(self.update_results)

        remove_btn = QPushButton("\u2715")
        remove_btn.setFixedWidth(30)
        remove_btn.setStyleSheet("color: gray;")
        remove_btn.clicked.connect(lambda: self.remove_course_row(row_layout))

        row_layout.addWidget(name)
        row_layout.addWidget(credits)
        row_layout.addWidget(grade)
        row_layout.addWidget(remove_btn)

        self.course_rows.append((name, credits, grade))
        self.course_layout.addLayout(row_layout)
        self.update_results()

    def remove_course_row(self, row_layout):
        for i in reversed(range(row_layout.count())):
            widget = row_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.course_layout.removeItem(row_layout)
        self.update_results()

    def update_results(self):
        total_quality_points = 0
        total_credits = 0

        for name, credits, grade in self.course_rows:
            selected_grade = grade.currentText()
            credit_val = credits.value()

            if selected_grade in qualityPoint and credit_val > 0:
                gp = qualityPoint[selected_grade]
                total_quality_points += gp * credit_val
                total_credits += credit_val

        self.semester_credits_label.setText(str(total_credits))
        gpa = total_quality_points / total_credits if total_credits > 0 else 0
        self.gpa_label.setText(f"{gpa:.2f}")

        try:
            current_cgpa = float(self.cgpa_input.text())
            completed_credits = int(self.credits_input.text())
            total_completed = completed_credits + total_credits
            overall_points = current_cgpa * completed_credits + gpa * total_credits
            new_cgpa = overall_points / total_completed if total_completed > 0 else 0
            self.total_credits_label.setText(str(total_completed))
            self.cgpa_label.setText(f"{new_cgpa:.2f}")
        except:
            self.total_credits_label.setText(str(total_credits))
            self.cgpa_label.setText(f"{gpa:.2f}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    from styles import load_stylesheet
    app.setStyleSheet(load_stylesheet())
    window = GPACalculatorWidget()
    window.show()
    sys.exit(app.exec_())
