from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit,
    QComboBox, QPushButton, QSpinBox, QMessageBox, QFrame, QSizePolicy, 
    QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
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

        # Create result labels first with larger fonts
        self.semester_credits_label = QLabel("0")
        self.gpa_label = QLabel("0.00")
        self.total_credits_label = QLabel("0")
        self.cgpa_label = QLabel("0.00")
        
        # Set larger fonts for result values
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        self.semester_credits_label.setFont(value_font)
        self.gpa_label.setFont(value_font)
        self.total_credits_label.setFont(value_font)
        self.cgpa_label.setFont(value_font)

        # Main container layout
        container_layout = QVBoxLayout()
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(20, 15, 20, 15)
        
        # Title and description (full width)
        title = QLabel("GPA and CGPA Calculator")
        title.setObjectName("title")

        desc = QLabel(
            "To calculate your GPA, enter the Credit and select the Grade for each course/subject.\n"
            "To calculate your CGPA, enter your current CGPA and Credits Completed prior to this semester."
        )
        desc.setObjectName("desc")
        desc.setWordWrap(True)

        container_layout.addWidget(title)
        container_layout.addWidget(desc)
        
        # Create a container for the main content and results
        content_container = QHBoxLayout()
        content_container.setSpacing(20)
        
        # Left side - inputs (takes more space)
        left_widget = QWidget()
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        self.course_rows = []

        # Top input section - use grid layout for better alignment
        input_grid = QGridLayout()
        input_grid.setVerticalSpacing(10)
        input_grid.setHorizontalSpacing(15)

        self.cgpa_input = QLineEdit()
        self.cgpa_input.setPlaceholderText("E.g. 3.75")
        self.cgpa_input.textChanged.connect(self.update_results)

        self.credits_input = QLineEdit()
        self.credits_input.setPlaceholderText("E.g. 45")
        self.credits_input.textChanged.connect(self.update_results)

        input_grid.addWidget(QLabel("Current CGPA:"), 0, 0)
        input_grid.addWidget(self.cgpa_input, 0, 1)
        input_grid.addWidget(QLabel("Credits Completed:"), 1, 0)
        input_grid.addWidget(self.credits_input, 1, 1)

        left_layout.addLayout(input_grid)

        # Course section header with Credits and Grade on the same row
        course_header = QHBoxLayout()

        # Courses label on the left
        course_label = QLabel("Courses (optional):")
        course_label.setObjectName("course_header")
        course_header.addWidget(course_label)

        # Add stretch to push the other headers to the right
        course_header.addStretch()

        # Credits header
        credits_label = QLabel("Credits")
        credits_label.setObjectName("course_header")
        credits_label.setAlignment(Qt.AlignCenter)
        credits_label.setFixedWidth(80)
        course_header.addWidget(credits_label)

        # Add some spacing between Credits and Grade
        course_header.addSpacing(10)

        # Grade header
        grade_label = QLabel("Grade")
        grade_label.setObjectName("course_header")
        grade_label.setAlignment(Qt.AlignCenter)
        grade_label.setFixedWidth(80)
        course_header.addWidget(grade_label)

        # Add space for the remove button
        course_header.addSpacing(40)

        left_layout.addLayout(course_header)

        # Create scroll area for courses
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)
        scroll_area.setMinimumHeight(150)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create widget for scroll area content
        scroll_content = QWidget()
        self.course_layout = QVBoxLayout(scroll_content)
        self.course_layout.setAlignment(Qt.AlignTop)
        self.course_layout.setSpacing(5)
        self.course_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add initial course rows
        for _ in range(5):
            self.add_course_row()
        
        scroll_area.setWidget(scroll_content)
        left_layout.addWidget(scroll_area)

        # Add course button with better placement
        button_container = QHBoxLayout()
        button_container.addStretch()
        add_btn = QPushButton("+ Add Course")
        add_btn.setObjectName("addCourseButton")
        add_btn.setFixedWidth(590)
        add_btn.clicked.connect(self.add_course_row)
        button_container.addWidget(add_btn)
        button_container.addStretch()
        left_layout.addLayout(button_container)
        
        content_container.addWidget(left_widget, 70)  # 70% space for left side
        
        # Right side - results card (smaller)
        result_card = QFrame()
        result_card.setObjectName("resultCard")
        result_card.setFixedWidth(150)
        result_card.setFixedHeight(500)
        result_card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        result_layout = QVBoxLayout(result_card)
        result_layout.setAlignment(Qt.AlignCenter)  # Center content vertically
        result_layout.setSpacing(15)
        result_layout.setContentsMargins(15, 15, 15, 20)
        
        # Add title to result card
        result_title = QLabel("Results")
        result_title.setObjectName("resultTitle")
        result_title.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(result_title)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #ddd; margin: 5px 0;")
        result_layout.addWidget(separator)
        
        # Add result items with centered values and better distribution
        result_items = [
            ("Semester Credits", self.semester_credits_label),
            ("GPA", self.gpa_label),
            ("Total Credits", self.total_credits_label),
            ("CGPA", self.cgpa_label)
        ]
        
        for label_text, value_label in result_items:
            # Create a container for each result item
            item_container = QVBoxLayout()
            item_container.setSpacing(5)
            item_container.setAlignment(Qt.AlignCenter)
            
            # Label for the item
            label = QLabel(label_text)
            label.setObjectName("resultItemLabel")
            label.setAlignment(Qt.AlignCenter)
            
            # Value for the item (centered)
            value_label.setObjectName("resultValue")
            value_label.setAlignment(Qt.AlignCenter)
            
            item_container.addWidget(label)
            item_container.addWidget(value_label)
            result_layout.addLayout(item_container)
            
            # Add small separator between items (except after the last one)
            if label_text != "CGPA":
                small_separator = QFrame()
                small_separator.setFrameShape(QFrame.HLine)
                small_separator.setFrameShadow(QFrame.Sunken)
                small_separator.setStyleSheet("background-color: #eee; margin: 5px 10px;")
                small_separator.setFixedHeight(1)
                result_layout.addWidget(small_separator)
        
        # Add stretch to distribute content evenly
        result_layout.addStretch()
        
        content_container.addWidget(result_card, 30)  # 30% space for right side
        
        container_layout.addLayout(content_container)
        
        # Back button
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("Photo/back.png"))
        back_btn.setText(" Back to Home")
        back_btn.setFixedSize(750, 40)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setObjectName("iconBackButton")
        back_btn.setIconSize(QSize(16, 16))
        back_btn.clicked.connect(self.go_back)

        container_layout.addWidget(back_btn)
        
        self.setLayout(container_layout)
        self.update_results()

    def add_course_row(self):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 5, 0, 5)
        row_layout.setSpacing(8)

        name = QLineEdit()
        name.setPlaceholderText("Course name")
        name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        credits = QSpinBox()
        credits.setRange(0, 10)
        credits.setSuffix(" credits")
        credits.setFixedWidth(80)
        credits.valueChanged.connect(self.update_results)

        grade = QComboBox()
        grade.addItem("Grade")
        grade.addItems(qualityPoint.keys())
        grade.setFixedWidth(80)
        grade.currentIndexChanged.connect(self.update_results)

        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(25, 25)
        remove_btn.setStyleSheet("""
            QPushButton {
                color: #ff4444;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #ffcccc;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #ffeeee;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_course_row(row_widget))

        row_layout.addWidget(name, 1)
        row_layout.addWidget(credits, 0)
        row_layout.addWidget(grade, 0)
        row_layout.addWidget(remove_btn, 0)

        self.course_rows.append((name, credits, grade, row_widget))
        self.course_layout.addWidget(row_widget)
        self.update_results()

    def remove_course_row(self, row_widget):
        if len(self.course_rows) <= 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Cannot Remove")
            msg.setText("You must have at least one course row.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        # Find and remove the row from course_rows
        for i, (name, credits, grade, widget) in enumerate(self.course_rows):
            if widget == row_widget:
                self.course_rows.pop(i)
                break
        
        # Remove the widget from layout
        row_widget.setParent(None)
        self.update_results()

    def update_results(self):
        total_quality_points = 0
        total_credits = 0

        for name, credits, grade, widget in self.course_rows:
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

    def go_back(self):
        self.main_window.pages.setCurrentWidget(self.main_window.feature_grid_page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    from styles import load_stylesheet
    app.setStyleSheet(load_stylesheet())
    window = GPACalculatorWidget()
    window.show()
    sys.exit(app.exec_())