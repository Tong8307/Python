from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
from database.db_manager import get_user
from styles.login_styles import get_login_styles

class LoginWidget(QWidget):
    login_successful = pyqtSignal(str, str)  # student_id, name
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setObjectName("loginWidget")
        self.setStyleSheet(get_login_styles())
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title = QLabel("Login")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form container
        form_container = QWidget()
        form_container.setObjectName("formContainer")
        form_container.setFixedWidth(500)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(30, 30, 30, 30)
        
        # Student ID input
        id_label = QLabel("Student ID:")
        id_label.setObjectName("formLabel")
        self.id_input = QLineEdit()
        self.id_input.setObjectName("inputField")
        self.id_input.setPlaceholderText("Enter your student ID (e.g., 00WMD0000)")
        
        # Convert to uppercase as user types
        self.id_input.textChanged.connect(self.convert_to_uppercase)
        
        # Password input
        password_label = QLabel("Password:")
        password_label.setObjectName("formLabel")
        self.password_input = QLineEdit()
        self.password_input.setObjectName("inputField")
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # Error message label
        self.error_label = QLabel()
        self.error_label.setObjectName("errorMessage")
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("loginButton")
        login_btn.setCursor(QCursor(Qt.PointingHandCursor))
        login_btn.clicked.connect(self.handle_login)
        
        # Add widgets to form
        form_layout.addWidget(title)
        form_layout.addWidget(id_label)
        form_layout.addWidget(self.id_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(login_btn)
        
        layout.addWidget(form_container, alignment=Qt.AlignCenter)
        
        # Connect return key to login
        self.id_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def convert_to_uppercase(self, text):
        """Convert input to uppercase as user types"""
        # Get current cursor position
        cursor_position = self.id_input.cursorPosition()
        
        # Convert text to uppercase
        uppercase_text = text.upper()
        
        # Only update if the text has actually changed (to avoid infinite loop)
        if uppercase_text != text:
            self.id_input.setText(uppercase_text)
            # Restore cursor position
            self.id_input.setCursorPosition(cursor_position)

    def handle_login(self):
        # Student ID is already uppercase due to textChanged signal
        student_id = self.id_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not student_id:
            self.show_error("Please enter your student ID")
            return
            
        if not password:
            self.show_error("Please enter your password")
            return
            
        # Clear previous errors
        self.hide_error()
        
        # Attempt login
        try:
            result = get_user(student_id, password)
            if result:
                student_id, name = result
                self.login_successful.emit(student_id, name)
            else:
                self.show_error("Invalid student ID or password")
        except Exception as e:
            self.show_error(f"Login error: {str(e)}")

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def hide_error(self):
        self.error_label.setVisible(False)

    def clear_form(self):
        self.id_input.clear()
        self.password_input.clear()
        self.hide_error()