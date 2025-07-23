import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QHBoxLayout, QFileDialog,
                             QMessageBox, QGridLayout)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPainter, QBrush
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QEvent
from styles import *

class FeatureButton(QPushButton):
    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent)
        self.setObjectName("FeatureButton")
        self.setFixedSize(350, 350)
        self.setCursor(Qt.PointingHandCursor)
        
        # Container widget
        container = QWidget(self)
        container.setGeometry(0, 0, 350, 350)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(70, 70, 70, 70)
        layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel()
        icon_label.setObjectName("iconLabel")
        icon_pixmap = QPixmap(icon_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Text
        text_label = QLabel(text)
        text_label.setObjectName("textLabel")
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)

class SlidingMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("slidingMenu")
        self.setFixedWidth(350)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 40, 0, 0)
        layout.setSpacing(0)

        # Profile section
        profile_widget = QWidget()
        profile_widget.setObjectName("profileWidget")
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setContentsMargins(0,82, 0, 80)
        profile_layout.setSpacing(7)
        
        # Avatar
        self.avatar = QLabel()
        self.avatar.setObjectName("avatarLabel")
        self.avatar.setFixedSize(150, 150)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setCursor(Qt.PointingHandCursor)
        self.avatar.mousePressEvent = self.upload_avatar
        
        # Default avatar
        self.default_avatar = QPixmap(150, 150)
        self.default_avatar.fill(Qt.transparent)
        painter = QPainter(self.default_avatar)
        painter.setBrush(QBrush(Qt.gray))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 150, 150)
        painter.setFont(QFont("Arial", 40))
        painter.setPen(Qt.white)
        painter.drawText(self.default_avatar.rect(), Qt.AlignCenter, "👤")
        painter.end()
        self.avatar.setPixmap(self.default_avatar)
        
        # Profile info
        name_label = QLabel("John Doe")
        name_label.setObjectName("profileName")
        id_label = QLabel("ID: S1234567")
        id_label.setObjectName("profileID")
        
        profile_layout.addWidget(self.avatar, 0, Qt.AlignCenter)
        profile_layout.addWidget(name_label, 0, Qt.AlignCenter)
        profile_layout.addWidget(id_label, 0, Qt.AlignCenter)
        layout.addWidget(profile_widget)

        # Menu buttons
        menu_items = [
            ("Home", "home"),
            ("Notes", "notes"),
            ("Schedule", "schedule"),
            ("Settings", "settings"),
            ("Logout", "logout")
        ]
        
        for text, action in menu_items:
            btn = QPushButton(text)
            btn.setObjectName("menuOptions")
            btn.setCursor(Qt.PointingHandCursor)
            if action == "logout":
                btn.clicked.connect(self.show_logout_dialog)
            layout.addWidget(btn)

        layout.addStretch()
    
    def upload_avatar(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Picture", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.load_avatar(file_path)
    
    def load_avatar(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            circular = QPixmap(150, 150)
            circular.fill(Qt.transparent)
            painter = QPainter(circular)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(pixmap.scaled(150, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 150, 150)
            painter.end()
            self.avatar.setPixmap(circular)
    
    def show_logout_dialog(self):
        reply = QMessageBox.question(self, "Logout", 
                                   "Are you sure you want to log out?",
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.parent().close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Assistant")
        self.setFixedSize(800, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setObjectName("headerWidget")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        self.menu_btn = QPushButton("☰")
        self.menu_btn.setObjectName("menuButton")
        self.menu_btn.setStyleSheet(get_menu_button_style())
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.clicked.connect(self.toggle_menu)
        
        title = QLabel("Student Assistant")
        title.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.menu_btn)
        header_layout.addSpacing(5)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addWidget(header)
        
        # Content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Features grid
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(30)
        grid_layout.setVerticalSpacing(30)
        
        features = [
            ("Photo/note_icon.png", "Note Organizer"),
            ("Photo/room_icon.png", "Room Booking"),
            ("Photo/gpa_icon.png", "GPA Calculator"),
            ("Photo/QA_icon.png", "Q & A sessions"),
        ]
        
        for i, (icon, text) in enumerate(features):
            btn = FeatureButton(icon, text)
            btn.clicked.connect(lambda checked, t=text: self.handle_feature_click(t))
            row = i // 2
            col = i % 2
            grid_layout.addWidget(btn, row, col)
        
        content_layout.addLayout(grid_layout)
        content_layout.addStretch()
        main_layout.addWidget(content)
        
        # Sliding menu
        self.sliding_menu = SlidingMenu(self)
        self.sliding_menu.move(-self.sliding_menu.width(), 60)  # Below header
        self.sliding_menu.setFixedHeight(self.height() - 60)  # Window height - header height
        self.menu_shown = False
        
        # Event filter
        self.installEventFilter(self)
    
    def handle_feature_click(self, feature_name):
        print(f"{feature_name} clicked!")
        # Add your feature handling code here
        if feature_name == "Note Organizer":
            self.open_note_organizer()
        elif feature_name == "Room Booking":
            self.open_room_booking()
        # Add other features...
    
    def open_note_organizer(self):
        print("Opening Note Organizer...")
        # Implement your note organizer functionality
    
    def open_room_booking(self):
        print("Opening Room Booking...")
        # Implement your room booking functionality
    
    def eventFilter(self, obj, event):
        if (self.menu_shown and 
            event.type() == QEvent.MouseButtonPress and 
            not self.sliding_menu.geometry().contains(event.globalPos())):
            self.hide_menu()
            return True
        return super().eventFilter(obj, event)
    
    def toggle_menu(self):
        if self.menu_shown:
            self.hide_menu()
        else:
            self.show_menu()
    
    def show_menu(self):
        self.anim = QPropertyAnimation(self.sliding_menu, b"pos")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.setStartValue(self.sliding_menu.pos())
        self.anim.setEndValue(QPoint(0, 60))  # Below header
        self.anim.start()
        self.menu_shown = True
    
    def hide_menu(self):
        self.anim = QPropertyAnimation(self.sliding_menu, b"pos")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.setStartValue(self.sliding_menu.pos())
        self.anim.setEndValue(QPoint(-self.sliding_menu.width(), 60))  # Below header
        self.anim.start()
        self.menu_shown = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())