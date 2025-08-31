# booking_styles.py

def get_booking_styles():
    return """
    /* ===========================
       Global + Shared (safe for both pages)
       =========================== */

    /* ----- Main headers used on both pages ----- */
    QLabel#bookingHeader {
        font-size: 30px;
        font-weight: 700;
        color: #283593;
        padding: 5px 0 0 5px;
        letter-spacing: 0.3px;
    }

    QLabel#bookingSubheader {
        font-size: 18px;
        font-weight: 500;
        color: #4B4B4C;
        padding: 0 0 0 10px;
    }

    /* Divider bar used on both pages */
    QFrame#divider {
        border: 1px solid #e9ecef;
        margin: 16px 0;
    }

    /* Back buttons (used on both pages) */
    QPushButton#iconBackButton {
        background-color: #283593;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 15px;
        font-weight: 600;
    }
    QPushButton#iconBackButton:hover {
        background-color: #1A237E;
    }
    QPushButton#iconBackButton:pressed {
        background-color: #141b5e;
    }

    /* Scroll areas (hide scrollbars but keep scrolling) */
    QScrollArea#scroll,
    QScrollArea#studentScroll {
        border: none;
        background: transparent;
    }
    QScrollBar:vertical, QScrollBar:horizontal {
        width: 0px;
        height: 0px;
        background: transparent;
    }

    /* Status message helpers (optional reuse) */
    QLabel#statusMessage {
        font-size: 14px;
        color: #6c757d;
        padding: 10px;
        border-radius: 6px;
    }
    QLabel#successMessage {
        background-color: #d4edda;
        color: #155724;
    }
    QLabel#errorMessage {
        background-color: #f8d7da;
        color: #721c24;
    }

    /* ===========================
       New Booking page specific
       Scoped under #bookingWidget to avoid clashes
       =========================== */

    QWidget#bookingWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #333333;
        background: transparent;
    }

    /* Section/field labels */
    QWidget#bookingWidget QLabel#formLabel {
        font-size: 15px;
        font-weight: 600;
        color: #2b2f36;
        padding: 4px 2px;
        margin-top: 6px;
    }

    /* Read-only value chips (e.g., your student name/id) */
    QWidget#bookingWidget QLabel#readOnlyField {
        font-size: 14px;
        color: #1f2a56;
        background: #f4f6ff;
        border: 1px solid #e1e6ff;
        border-radius: 999px;
        padding: 6px 10px;
        margin-left: 6px;
    }

    /* Frame cards for current user and additional students */
    QWidget#bookingWidget QFrame#userFrame,
    QWidget#bookingWidget QFrame#studentFrame {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 10px;
    }
    /* Slightly highlight the current user frame */
    QWidget#bookingWidget QFrame#userFrame {
        border: 1px solid #dbe2ff;
        background: #fafbff;
    }

    /* Inputs: LineEdit, ComboBox, Date/Time, SpinBox */
    QWidget#bookingWidget QLineEdit,
    QWidget#bookingWidget QComboBox,
    QWidget#bookingWidget QDateEdit,
    QWidget#bookingWidget QTimeEdit,
    QWidget#bookingWidget QSpinBox {
        border: 1px solid #ced4da;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 15px;
        min-height: 36px;
        background: #ffffff;
    }
    QWidget#bookingWidget QLineEdit:focus,
    QWidget#bookingWidget QComboBox:focus,
    QWidget#bookingWidget QDateEdit:focus,
    QWidget#bookingWidget QTimeEdit:focus,
    QWidget#bookingWidget QSpinBox:focus {
        border: 2px solid #80bdff;
        outline: none;
        background: #ffffff;
    }

    /* Specific widgets (optional fine-tuning) */
    QWidget#bookingWidget QComboBox#featureCombo {
        min-width: 260px;
    }
    QWidget#bookingWidget QSpinBox#studentsSpin {
        min-width: 120px;
    }

    /* Calendar popup aesthetics */
    QWidget#bookingWidget QCalendarWidget QWidget {
        alternate-background-color: #f6f8ff;
    }
    QWidget#bookingWidget QCalendarWidget QToolButton {
        color: #283593;
        font-weight: 600;
    }
    QWidget#bookingWidget QCalendarWidget QAbstractItemView:enabled {
        selection-background-color: #283593;
        selection-color: #ffffff;
    }

    /* Terms & Conditions checkbox */
    QWidget#bookingWidget QCheckBox#termsCheckbox {
        font-size: 14px;
        color: #2b2f36;
        padding: 4px 0;
        margin-top: 4px;
    }
    /* Error state applied dynamically via setProperty("class", "error") */
    QWidget#bookingWidget QCheckBox#termsCheckbox[class="error"] {
        color: #dc3545;
        font-weight: 600;
    }
    QWidget#bookingWidget QCheckBox#termsCheckbox[class="error"]::indicator {
        width: 16px;
        height: 16px;
        border: 2px solid #dc3545;
        border-radius: 3px;
        background: #fff5f5;
    }

    /* Submit button */
    QWidget#bookingWidget QPushButton#submitButton {
        background-color: #28a745;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 12px 18px;
        font-size: 16px;
        font-weight: 700;
        min-width: 180px;
    }
    QWidget#bookingWidget QPushButton#submitButton:hover:enabled {
        background-color: #218838;
    }
    QWidget#bookingWidget QPushButton#submitButton:pressed:enabled {
        background-color: #1a6f2f;
    }
    QWidget#bookingWidget QPushButton#submitButton:disabled {
        background-color: #b9e2c0;
        color: #f3f7f4;
    }

    /* Table styling (kept for any table usage on booking pages) */
    QWidget#bookingWidget QTableWidget {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        gridline-color: #e9ecef;
        font-size: 15px;
    }
    QWidget#bookingWidget QTableWidget QHeaderView::section {
        background-color: #343a40;
        color: #ffffff;
        padding: 10px;
        font-size: 15px;
        border: none;
    }
    QWidget#bookingWidget QTableWidget::item {
        padding: 12px;
        border-bottom: 1px solid #e9ecef;
    }

    /* Nice focus ring for better accessibility (fallback if border not supported) */
    QWidget#bookingWidget QLineEdit:focus:!read-only,
    QWidget#bookingWidget QComboBox:focus,
    QWidget#bookingWidget QDateEdit:focus,
    QWidget#bookingWidget QTimeEdit:focus,
    QWidget#bookingWidget QSpinBox:focus {
        border: 2px solid #80bdff;
        background: #ffffff;
    }
"""