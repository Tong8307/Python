from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QSizePolicy, QScrollArea)
from PyQt5.QtCore import Qt
from database.db_manager import get_student_name

class StudentInfoPage(QWidget):
    def __init__(self, main_window, student_inputs):
        """
        main_window: reference to parent window (to return back)
        student_inputs: list of tuples (id_input, name_input) from booking page
        """
        super().__init__()
        self.main_window = main_window
        self.original_student_inputs = student_inputs
        self.student_widgets = []

        self.studentInfo()
        self.apply_styles()

    def studentInfo(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        title = QLabel("Student Information")
        title.setObjectName("bookingHeader")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel("Enter student IDs and names will auto-fill. Click Save to confirm changes.")
        instructions.setWordWrap(True)
        instructions.setObjectName("instructionsLabel")
        layout.addWidget(instructions)

        # Scroll area for many students
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        scroll_area.setObjectName("studentScroll")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Add all student input rows
        for i, (id_input, name_input) in enumerate(self.original_student_inputs):
            student_frame = QFrame()
            student_frame.setObjectName("studentFrame")
            student_layout = QHBoxLayout(student_frame)
            student_layout.setContentsMargins(15, 10, 15, 10)

            # Student number
            number_label = QLabel(f"{i+1}.")
            number_label.setObjectName("studentNumber")
            number_label.setFixedWidth(30)
            
            # ID field
            id_label = QLabel("Student ID:")
            id_label.setObjectName("formLabel")
            id_label.setFixedWidth(80)
            id_field = QLineEdit(id_input.text())
            id_field.setPlaceholderText("Enter student ID")
            id_field.setMinimumWidth(150)
            # Connect textChanged signal to convert to uppercase
            id_field.textChanged.connect(self.convert_to_uppercase)

            # Name field
            name_label = QLabel("Name:")
            name_label.setObjectName("formLabel")
            name_label.setFixedWidth(50)
            name_field = QLineEdit(name_input.text())
            name_field.setReadOnly(True)
            name_field.setMinimumWidth(200)

            # Auto-fill name when ID changes
            id_field.textChanged.connect(lambda text, nf=name_field: self.update_name_field(text, nf))

            student_layout.addWidget(number_label)
            student_layout.addWidget(id_label)
            student_layout.addWidget(id_field)
            student_layout.addWidget(name_label)
            student_layout.addWidget(name_field)
            student_layout.addStretch()

            scroll_layout.addWidget(student_frame)
            self.student_widgets.append((id_field, name_field))
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Buttons at bottom
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("saveChanges")
        save_btn.setFixedWidth(150)
        save_btn.clicked.connect(self.save_student_info)

        back_btn = QPushButton("Cancel")
        back_btn.setObjectName("cancelButton")
        back_btn.setFixedWidth(150)
        back_btn.clicked.connect(self.go_back)

        button_layout.addStretch()
        button_layout.addWidget(back_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def convert_to_uppercase(self):
        """Convert student ID input to uppercase in real-time"""
        sender = self.sender()
        if isinstance(sender, QLineEdit):
            cursor_pos = sender.cursorPosition()
            text = sender.text().upper()
            sender.setText(text)
            sender.setCursorPosition(cursor_pos)

    def update_name_field(self, student_id, name_field):
        #Check the student id are empty or not, if yes = retrieve data from database and save to name_field
        student_name = get_student_name(student_id.strip()) if student_id.strip() else ""
        name_field.setText(student_name or "")

    def save_student_info(self):
        """Save edits back to original booking page inputs"""
        for i, (id_field, name_field) in enumerate(self.student_widgets):
            orig_id_input, orig_name_input = self.original_student_inputs[i]
            orig_id_input.setText(id_field.text())
            orig_name_input.setText(name_field.text())
        self.go_back()

    def go_back(self):
        """Return to the new booking page"""
        # Navigate back to the booking page in the RoomBookingWidget
        self.main_window.pages.setCurrentWidget(self.main_window.new_booking_page)

    def apply_styles(self):
        """Apply the same CSS style as booking page"""
        from styles.booking_styles import get_booking_styles
        self.setStyleSheet(get_booking_styles())