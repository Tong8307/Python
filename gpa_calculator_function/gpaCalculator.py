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

        # Create main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 5)
        main_layout.setSpacing(0)

        # Create a scroll area for the content (will scroll)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create a container widget for the scroll area
        container_widget = QWidget()
        scroll_area.setWidget(container_widget)
        
        # Main container layout for scrollable content
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(15, 10, 15, 10)

        title = QLabel("GPA and CGPA Calculator")
        title.setObjectName("gpaHeader")
        container_layout.addWidget(title)

        subtitle = QLabel(
            "To calculate your GPA, enter the Credit and select the Grade for each course/subject.\n"
            "To calculate your CGPA, enter your current CGPA and Credits Completed prior to this semester.")
        subtitle.setObjectName("gpaSubheader")
        subtitle.setWordWrap(True)
        container_layout.addWidget(subtitle)

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

        input_grid.addWidget(QLabel("Current CGPA\t:"), 0, 0)
        input_grid.addWidget(self.cgpa_input, 0, 1)
        input_grid.addWidget(QLabel("Credits Completed :"), 1, 0)
        input_grid.addWidget(self.credits_input, 1, 1)

        left_layout.addLayout(input_grid)

        # Course section header
        course_header = QHBoxLayout()

        # Courses label on the left
        course_label = QLabel("Courses (optional)")
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

        # Create widget for courses
        course_content = QWidget()
        self.course_layout = QVBoxLayout(course_content)
        self.course_layout.setAlignment(Qt.AlignTop)
        self.course_layout.setSpacing(5)
        self.course_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add initial course rows
        for _ in range(6):
            self.add_course_row()

        left_layout.addWidget(course_content)

        # Add course button with better placement
        button_container = QHBoxLayout()
        add_btn = QPushButton("+ Add Course")
        add_btn.setObjectName("addCourseButton")
        add_btn.setFixedWidth(390)
        add_btn.clicked.connect(self.add_course_row)
        button_container.addWidget(add_btn)
        button_container.addStretch()
        left_layout.addLayout(button_container)
        
        content_container.addWidget(left_widget, 60)
        
        # Right side - results card (smaller)
        result_card = QFrame()
        result_card.setObjectName("resultCard")
        result_card.setFixedWidth(150)
        result_card.setFixedHeight(500)
        result_card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        result_layout = QVBoxLayout(result_card)
        result_layout.setAlignment(Qt.AlignCenter)
        result_layout.setSpacing(20)
        result_layout.setContentsMargins(0, 10, 0, 5)
        
        # Add title to result card
        result_title = QLabel("Results")
        result_title.setObjectName("resultTitle")
        result_title.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(result_title)
        
        # Add stretch at the top to push content to middle
        result_layout.addStretch()
        
        # Add result items with centered values
        result_items = [
            ("Semester Credits", self.semester_credits_label),
            ("GPA", self.gpa_label),
            ("Total Credits", self.total_credits_label),
            ("CGPA", self.cgpa_label)
        ]
        
        for label_text, value_label in result_items:
            # Create a container for each result item
            item_container = QVBoxLayout()
            item_container.setSpacing(15)
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
                small_separator.setFrameShadow(QFrame.Plain)
                small_separator.setStyleSheet("background-color: #eee;")
                small_separator.setFixedHeight(1)
                result_layout.addWidget(small_separator)
        
        # Add stretch at the bottom to center the content vertically
        result_layout.addStretch()
        
        content_container.addWidget(result_card, 40)
        
        container_layout.addLayout(content_container)
        
        # Add scroll area to main layout (this will scroll)
        main_layout.addWidget(scroll_area, 1)  # 1 = stretch factor to expand
        
        # Back button
        back_btn = QPushButton()
        back_btn.setIcon(QIcon("Photo/back.png"))
        back_btn.setText(" Back to Home")
        back_btn.setFixedSize(750, 40)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setObjectName("iconBackButton")
        back_btn.setIconSize(QSize(16, 16))
        back_btn.clicked.connect(self.go_back)
        main_layout.addWidget(back_btn, 0, Qt.AlignCenter)
        
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
        credits.setFixedWidth(75)
        credits.valueChanged.connect(self.update_results)

        grade = QComboBox()
        grade.addItem("Grade")
        grade.addItems(qualityPoint.keys())
        grade.setFixedWidth(80)
        grade.currentIndexChanged.connect(self.update_results)

        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(35, 35)
        remove_btn.setObjectName("removeCourseButton")
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
            QMessageBox.warning(self, "Cannot Remove", 
                               "You must have at least one course row.")
            return

        # Find and remove the row from course_rows
        for i, (name, credits, grade, widget) in enumerate(self.course_rows):
            if widget == row_widget:
                # Disconnect signals first
                try:
                    credits.valueChanged.disconnect(self.update_results)
                    grade.currentIndexChanged.disconnect(self.update_results)
                except:
                    pass
                
                # Remove from list and delete widget
                self.course_rows.pop(i)
                widget.deleteLater()
                break
        
        self.update_results()

    def validate_numeric_input(self, text, field_name, is_float=False):
        """Validate numeric input and show error message if invalid"""
        try:
            if is_float:
                value = float(text)
                if value < 0 or value > 4.0:
                    raise ValueError(f"{field_name} must be between 0 and 4.0")
            else:
                value = int(text)
                if value < 0:
                    raise ValueError(f"{field_name} must be positive")
            return True, value
        except ValueError as e:
            if text:  # Only show error if field is not empty
                QMessageBox.warning(self, "Invalid Input", str(e))
            return False, None

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

        # Validate inputs before calculation
        current_cgpa = 0
        completed_credits = 0
        cgpa_valid = True
        credits_valid = True
        
        if self.cgpa_input.text():
            cgpa_valid, current_cgpa = self.validate_numeric_input(
                self.cgpa_input.text(), "CGPA", is_float=True
            )
        
        if self.credits_input.text():
            credits_valid, completed_credits = self.validate_numeric_input(
                self.credits_input.text(), "Completed Credits"
            )

        if cgpa_valid and credits_valid:
            try:
                total_completed = completed_credits + total_credits
                overall_points = current_cgpa * completed_credits + gpa * total_credits
                new_cgpa = overall_points / total_completed if total_completed > 0 else 0
                self.total_credits_label.setText(str(total_completed))
                self.cgpa_label.setText(f"{new_cgpa:.2f}")
            except:
                self.total_credits_label.setText(str(total_credits))
                self.cgpa_label.setText(f"{gpa:.2f}")
        else:
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