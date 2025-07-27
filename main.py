import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QFileDialog, QMessageBox, QGridLayout, QStackedWidget
)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QBrush # Graphics handling
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QEvent # Core Qt functionality

from styles.styles import *
from room_booking_function.room_booking import *

#Create class to enable reusability because if function need to use public variable to keep track
# self is used in class methods to refer to the current instance of the class (to avoid global settings), can be call by using passed references 
class FeatureButton(QPushButton): 
    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent) # Initialize QPushButton
        self.setObjectName("FeatureButton") # CSS identifier
        self.setFixedSize(350, 350)
        self.setCursor(Qt.PointingHandCursor) # Mouse cursor style

        # Container for icon + text
        container = QWidget(self)
        container.setGeometry(0, 0, 350, 350)

        layout = QVBoxLayout(container) # Vertical layout
        layout.setContentsMargins(70, 70, 70, 70) # Padding
        layout.setSpacing(10)

        # Icon setup
        icon_label = QLabel()
        icon_label.setObjectName("iconLabel")
        icon_pixmap = QPixmap(icon_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation) # Load/resize image
        icon_label.setPixmap(icon_pixmap) # Display icon
        icon_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel(text)
        text_label.setObjectName("textLabel")
        text_label.setWordWrap(True)  # breaking long lines of text into multiple lines
        text_label.setAlignment(Qt.AlignCenter) 

        # Widget: Any visual element (buttons, labels, layouts, etc.)
        # Add widget insert all the visual element to the layout
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

        profile_widget = QWidget() # Profile picture holder
        profile_widget.setObjectName("profileWidget")
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setContentsMargins(0, 70, 0, 70)

        self.avatar = QLabel()
        self.avatar.setObjectName("avatarLabel")
        self.avatar.setFixedSize(150, 150)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setCursor(Qt.PointingHandCursor)
        self.avatar.mousePressEvent = self.upload_avatar

        self.default_avatar = QPixmap(150, 150) ## Fallback image
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

        name_label = QLabel("John Doe")
        name_label.setObjectName("profileName")
        id_label = QLabel("ID: S1234567")
        id_label.setObjectName("profileID")

        profile_layout.addWidget(self.avatar, 0, Qt.AlignCenter)
        profile_layout.addWidget(name_label, 0, Qt.AlignCenter)
        profile_layout.addWidget(id_label, 0, Qt.AlignCenter)
        layout.addWidget(profile_widget)

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
            elif action == "home":
                btn.clicked.connect(self.go_to_home)
            layout.addWidget(btn)

        layout.addStretch() #Pushes content upward

    def upload_avatar(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
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
    
    def go_to_home(self):
        # Access the parent MainWindow and switch to home page
        main_window = self.parent()
        if isinstance(main_window, MainWindow):
            main_window.pages.setCurrentWidget(main_window.feature_grid_page)
            main_window.hide_menu()  # Also hide the menu when navigating


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_id = 1001 #Temporary set Only
        self.setWindowTitle("Student Assistant")
        self.setFixedSize(800, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Creates a header bar 
        header = QWidget()
        header.setObjectName("headerWidget")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)

        self.menu_btn = QPushButton("☰")
        self.menu_btn.setObjectName("menuButton")
        self.menu_btn.setStyleSheet(get_menu_button_style())
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.clicked.connect(self.toggle_menu) #Connect to the toggle menu function

        title = QLabel("Student Assistant")
        title.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(self.menu_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addWidget(header)

        self.pages = QStackedWidget() # QStackedWidget is used to switch between different pages (views)
        main_layout.addWidget(self.pages)

        self.feature_grid_page = self.create_feature_grid() #Connect with the function
        self.pages.addWidget(self.feature_grid_page)

        # Initialize location selection page
        self.location_selection_page = LocationSelectionWidget(self)
        self.pages.addWidget(self.location_selection_page)

        self.sliding_menu = SlidingMenu(self)
        self.sliding_menu.move(-self.sliding_menu.width(), 60) #Places it offscreen initially (hidden).
        self.sliding_menu.setFixedHeight(self.height() - 60) #Starts from top offset of 60px (to stay below header)
        self.menu_shown = False # track whether the menu is currently shown or hidden

        self.installEventFilter(self) #clicking outside the menu to hide it

    def create_feature_grid(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

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
            btn.clicked.connect(lambda checked, t=text: self.handle_feature_click(t)) #Connects the button’s click signal to the handle_feature_click() method
            row = i // 2 #This creates 2 columns per row.
            col = i % 2 #Determines the column for the grid layout.
            grid_layout.addWidget(btn, row, col)

        layout.addLayout(grid_layout)
        layout.addStretch()
        return page #Returns the complete QWidget page that holds the feature grid

    def handle_feature_click(self, feature_name):
        if feature_name == "Room Booking":
            self.pages.setCurrentWidget(self.location_selection_page)
        elif feature_name == "Note Organizer":
            print("Future: Go to Note Organizer")
        else:
            print(f"{feature_name} clicked!")

    def toggle_menu(self):
        if self.menu_shown:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        self.anim = QPropertyAnimation(self.sliding_menu, b"pos") #Creates a new animation object that targets the position
        self.anim.setDuration(300) #The animation lasts for 300 milliseconds
        self.anim.setEasingCurve(QEasingCurve.OutQuad) #Applies a smooth easing curve — it starts quickly and slows down near the end.
        self.anim.setStartValue(self.sliding_menu.pos()) #Sets the starting position as wherever the menu currently is.
        self.anim.setEndValue(QPoint(0, 60)) #The ending position is (0, 60) — meaning it slides into view from the left and aligns just below the top header 
        self.anim.start() #Starts the animation.
        self.menu_shown = True

    def hide_menu(self):
        self.anim = QPropertyAnimation(self.sliding_menu, b"pos")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.setStartValue(self.sliding_menu.pos())
        self.anim.setEndValue(QPoint(-self.sliding_menu.width(), 60)) #Slides the menu leftward out of view by setting the to negative its own width.
        self.anim.start()
        self.menu_shown = False

    def eventFilter(self, obj, event):
        if self.menu_shown and event.type() == QEvent.MouseButtonPress and not self.sliding_menu.geometry().contains(event.globalPos()):
            self.hide_menu()
            return True
        return super().eventFilter(obj, event)
    
    def open_room_booking_page(self, location_id):
        # Clean up previous booking widget if exists
        if hasattr(self, 'room_booking_widget_by_location'): #Check if exist 
            self.pages.removeWidget(self.room_booking_widget_by_location) #Remove from UI
            self.room_booking_widget_by_location.deleteLater() #Schedule deletion

        """Why need to clean up
        Prevents Memory Leaks: Each time you create a new RoomBookingWidget, it consumes memory. 
        Without cleanup, old widgets remain in memory."""

        # Create and show new booking page
        self.room_booking_widget_by_location = RoomBookingWidget(self, location_id)
        self.pages.addWidget(self.room_booking_widget_by_location)
        self.pages.setCurrentWidget(self.room_booking_widget_by_location)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
