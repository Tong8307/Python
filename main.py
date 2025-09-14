import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QMessageBox, QGridLayout, QStackedWidget
)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QBrush
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QEvent

from styles.styles import *
from login import LoginWidget
from database.db_manager import get_connection, get_profile_picture

# Room booking features
from room_booking_function.location_selection import LocationSelectionWidget
from room_booking_function.room_booking_widget import RoomBookingWidget
from room_booking_function.feature_button import FeatureButton
from room_booking_function.guidelines import GuidelinesPage

# Notes features
from notes_organizer_function.dashboard import DashboardWidget
from notes_organizer_function.notes_organizer import NoteOrganizerWidget


class SlidingMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("slidingMenu")
        self.setFixedWidth(350)
        self.is_logged_in = False
        self.current_user_id = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 40, 0, 0)
        layout.setSpacing(0)

        # Profile area
        profile_widget = QWidget()
        profile_widget.setObjectName("profileWidget")
        profile_layout = QVBoxLayout(profile_widget)
        profile_layout.setContentsMargins(0, 70, 0, 70)

        self.avatar = QLabel()
        self.avatar.setObjectName("avatarLabel")
        self.avatar.setFixedSize(150, 150)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setCursor(Qt.PointingHandCursor)

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

        self.name_label = QLabel("Please Login")
        self.name_label.setObjectName("profileName")
        self.id_label = QLabel("ID: Not logged in")
        self.id_label.setObjectName("profileID")

        profile_layout.addWidget(self.avatar, 0, Qt.AlignCenter)
        profile_layout.addWidget(self.name_label, 0, Qt.AlignCenter)
        profile_layout.addWidget(self.id_label, 0, Qt.AlignCenter)
        layout.addWidget(profile_widget)

        # Menu
        menu_items = [
            ("Home", "home"),
            ("Notes", "notes"),
            ("Booking Guidelines", "guidelines"),
            ("My Bookings (All Locations)", "all_bookings"),
            ("Logout", "logout"),
        ]
        for text, action in menu_items:
            btn = QPushButton(text)
            btn.setObjectName("menuOptions")
            btn.setCursor(Qt.PointingHandCursor)
            if action == "logout":
                btn.clicked.connect(self.show_logout_dialog)
            elif action == "home":
                btn.clicked.connect(self.go_to_home)
            elif action == "guidelines":
                btn.clicked.connect(self.show_guidelines)
            elif action == "all_bookings":
                btn.clicked.connect(self.show_all_bookings)
            elif action == "notes":
                btn.clicked.connect(self.go_to_notes)
            else:
                btn.clicked.connect(lambda _, a=action: self._need_login_then_print(a))
            layout.addWidget(btn)

        layout.addStretch()

    def _need_login_then_print(self, action):
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", "Please login first.")
            return
        print(f"Menu action: {action}")

    def show_logout_dialog(self):
        if not self.is_logged_in:
            QMessageBox.information(self, "Already Logged Out", "You are already logged out.")
            return
        if QMessageBox.question(self, "Logout", "Log out now?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.parent().logout()

    def go_to_home(self):
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", "Please login first.")
            return
        mw = self.parent()
        mw.pages.setCurrentWidget(mw.feature_grid_page)
        mw.hide_menu()

    def go_to_notes(self):
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", "Please login first.")
            return
        mw = self.parent()
        if not hasattr(mw, 'dashboard_page'):
            mw.dashboard_page = DashboardWidget(
                on_add_note_clicked=mw.open_notes_page,
                on_back_home=mw.back_to_home,
                on_note_deleted=mw._on_dashboard_note_deleted, 
                user_id=mw.user_id 
            )
            mw.pages.addWidget(mw.dashboard_page)
        mw.pages.setCurrentWidget(mw.dashboard_page)
        mw.hide_menu()

    def show_guidelines(self):
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", "Please login first.")
            return
        mw = self.parent()
        mw.show_guidelines()

    def show_all_bookings(self):
        if not self.is_logged_in:
            QMessageBox.warning(self, "Login Required", "Please login first.")
            return
        mw = self.parent()
        mw.hide_menu()
        mw.pages.setCurrentWidget(mw.all_bookings_page)
        mw.all_bookings_page.load_bookings()

    def load_profile_picture(self, filename):
        if filename:
            path = f"Photo/{filename}"
            if os.path.exists(path):
                pix = QPixmap(path)
                if not pix.isNull():
                    circular = QPixmap(150, 150)
                    circular.fill(Qt.transparent)
                    p = QPainter(circular)
                    p.setRenderHint(QPainter.Antialiasing)
                    p.setBrush(QBrush(pix.scaled(150, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
                    p.setPen(Qt.NoPen)
                    p.drawEllipse(0, 0, 150, 150)
                    p.end()
                    self.avatar.setPixmap(circular)
                    return
        self.avatar.setPixmap(self.default_avatar)

    def update_profile_info(self, name, student_id):
        self.name_label.setText(name)
        self.id_label.setText(f"ID: {student_id}")
        self.is_logged_in = True
        self.current_user_id = student_id
        self.load_profile_picture(get_profile_picture(student_id))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initialize_database()

        self.user_id = None
        self.user_name = None

        self.setWindowTitle("Student Assistant")
        self.setFixedSize(800, 900)

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
        self.menu_btn.setVisible(False)

        title = QLabel("Student Assistant")
        title.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(self.menu_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Pages
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(header)

        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages)

        # Login first
        self.login_page = LoginWidget(self)
        self.login_page.login_successful.connect(self.handle_login_success)
        self.pages.addWidget(self.login_page)

        # Pre-create static pages
        self.guidelines_page = GuidelinesPage(self)
        self.pages.addWidget(self.guidelines_page)

        
        # Lazy pages
        self.feature_grid_page = None
        self.location_selection_page = None

        # Sliding menu + overlay
        self.sliding_menu = SlidingMenu(self)
        self.sliding_menu.move(-self.sliding_menu.width(), 60)
        self.sliding_menu.setFixedHeight(self.height() - 60)
        self.menu_shown = False

        self.installEventFilter(self)
        self.pages.installEventFilter(self)

        self.overlay = QWidget(self)
        self.overlay.setObjectName("menuOverlay")
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 30);")
        self.overlay.hide()
        self.overlay.installEventFilter(self)

        self.pages.setCurrentWidget(self.login_page)

    def initialize_database(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            if cur.fetchone()[0] == 0:
                QMessageBox.warning(self, "Database", "Database is empty. Run init_db.py first.")
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def handle_login_success(self, student_id, name):
        self.user_id = student_id
        self.user_name = name
        self.initialize_main_app()
        self.sliding_menu.update_profile_info(name, student_id)
        self.menu_btn.setVisible(True)
        self.pages.setCurrentWidget(self.feature_grid_page)

    def initialize_main_app(self):
        if self.feature_grid_page is None:
            self.feature_grid_page = self.create_feature_grid()
            self.pages.addWidget(self.feature_grid_page)
        if self.location_selection_page is None:
            self.location_selection_page = LocationSelectionWidget(self)
            self.pages.addWidget(self.location_selection_page)

    def create_feature_grid(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(30)

        features = [
            ("Photo/note_icon.png", "Note Organizer"),
            ("Photo/discussion.png", "Room Booking"),
            ("Photo/gpa_icon.png", "GPA Calculator"),
            ("Photo/QA_icon.png", "Q & A sessions"),
        ]
        for i, (icon, text) in enumerate(features):
            btn = FeatureButton(icon, text, size_type="main")
            btn.clicked.connect(lambda _, t=text: self.handle_feature_click(t))
            r, c = divmod(i, 2)
            grid.addWidget(btn, r, c)

        layout.addLayout(grid)
        layout.addStretch()
        return page

    def handle_feature_click(self, feature_name):
        if feature_name == "Room Booking":
            self.pages.setCurrentWidget(self.location_selection_page)
        elif feature_name == "Note Organizer":
            if not hasattr(self, 'dashboard_page'):
                self.dashboard_page = DashboardWidget(
                    on_add_note_clicked=self.open_notes_page,
                    on_back_home=self.back_to_home,
                    on_note_deleted=self._on_dashboard_note_deleted,  
                    user_id=self.user_id,
                )
                self.pages.addWidget(self.dashboard_page)
            self.pages.setCurrentWidget(self.dashboard_page)
        else:
            print(f"{feature_name} clicked!")

    # Notes: open editor (optionally a specific note)
    def open_notes_page(self, note_id=None):
        if not hasattr(self, 'notes_page'):
            self.notes_page = NoteOrganizerWidget(on_return_callback=self.back_to_dashboard)
            self.pages.addWidget(self.notes_page)
        self.pages.setCurrentWidget(self.notes_page)
        if note_id is not None and hasattr(self.notes_page, "_open_by_id"):
            try:
                self.notes_page._open_by_id(note_id)
            except Exception as e:
                QMessageBox.information(self, "Open Note", f"Could not open the selected note.\n{e}")

    def back_to_dashboard(self):
        if hasattr(self, 'dashboard_page'):
            self.pages.setCurrentWidget(self.dashboard_page)

    def back_to_home(self):
        if self.feature_grid_page is None:
            self.initialize_main_app()
        self.pages.setCurrentWidget(self.feature_grid_page)
        self.hide_menu()

    # NEW: callback invoked by DashboardWidget after a note is deleted
    def _on_dashboard_note_deleted(self, note_id: int):
        if hasattr(self, 'notes_page') and hasattr(self.notes_page, 'close_tab_for_note'):
            try:
                self.notes_page.close_tab_for_note(note_id)
            except Exception:
                pass

    # Sliding menu
    def toggle_menu(self):
        if not self.user_id:
            QMessageBox.information(self, "Login Required", "Please login first.")
            return
        self.hide_menu() if self.menu_shown else self.show_menu()

    def show_menu(self):
        self.anim = QPropertyAnimation(self.sliding_menu, b"pos")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.setStartValue(self.sliding_menu.pos())
        self.anim.setEndValue(QPoint(0, 60))
        self.anim.start()
        self.menu_shown = True
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay.show()
        self.overlay.raise_()
        self.sliding_menu.raise_()

    def hide_menu(self):
        self.anim = QPropertyAnimation(self.sliding_menu, b"pos")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.setStartValue(self.sliding_menu.pos())
        self.anim.setEndValue(QPoint(-self.sliding_menu.width(), 60))
        self.anim.start()
        self.menu_shown = False
        self.overlay.hide()

    def eventFilter(self, obj, event):
        if self.menu_shown and event.type() == QEvent.MouseButtonPress:
            mouse_pos = event.globalPos()
            menu_rect = self.sliding_menu.frameGeometry()
            menu_rect.moveTopLeft(self.sliding_menu.mapToGlobal(QPoint(0, 0)))
            if not menu_rect.contains(mouse_pos):
                self.hide_menu()
                return True
        return super().eventFilter(obj, event)

    def show_guidelines(self):
        self.pages.setCurrentWidget(self.guidelines_page)
        self.hide_menu()

    def open_room_booking_page(self, location_id):
        if hasattr(self, 'room_booking_widget_by_location'):
            self.pages.removeWidget(self.room_booking_widget_by_location)
            self.room_booking_widget_by_location.deleteLater()
        self.room_booking_widget_by_location = RoomBookingWidget(self, location_id, self.user_id)
        self.pages.addWidget(self.room_booking_widget_by_location)
        self.pages.setCurrentWidget(self.room_booking_widget_by_location)

    def logout(self):
        self.user_id = None
        self.user_name = None
        self.sliding_menu.name_label.setText("Please Login")
        self.sliding_menu.id_label.setText("ID: Not logged in")
        self.sliding_menu.is_logged_in = False
        self.sliding_menu.current_user_id = None
        self.sliding_menu.avatar.setPixmap(self.sliding_menu.default_avatar)
        self.menu_btn.setVisible(False)

        # Remove lazy pages
        for attr in ("feature_grid_page", "location_selection_page", "dashboard_page", "notes_page"):
            if hasattr(self, attr):
                w = getattr(self, attr)
                self.pages.removeWidget(w)
                w.deleteLater()
                delattr(self, attr)

        self.hide_menu()
        self.pages.setCurrentWidget(self.login_page)
        self.login_page.clear_form()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    app.setFont(QFont("Segoe UI", 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
