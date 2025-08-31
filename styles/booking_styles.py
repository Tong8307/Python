def get_booking_styles():
    return """
    /* ===========================
       Global + Shared
       =========================== */

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

    QFrame#divider {
        border: 1px solid #e9ecef;
        margin: 16px 0;
    }

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

    /* ===========================
       New Booking form styling
       =========================== */

    QWidget#bookingWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #333333;
        background: transparent;
    }

    /* Form labels */
    QWidget#bookingWidget QLabel#formLabel {
        font-size: 16px;
        font-weight: 600;
        color: #2b2f36;
        margin: 0;
        padding-bottom: 3px;
    }

    /* Inputs (shared) */
    QWidget#bookingWidget QLineEdit,
    QWidget#bookingWidget QComboBox,
    QWidget#bookingWidget QTimeEdit,
    QWidget#bookingWidget QDateEdit,
    QWidget#bookingWidget QSpinBox {
        border: 1px solid #ced4da;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 15px;
        min-height: 34px;
        background: #ffffff;
    }

    QWidget#bookingWidget QLineEdit:focus,
    QWidget#bookingWidget QComboBox:focus,
    QWidget#bookingWidget QTimeEdit:focus,
    QWidget#bookingWidget QDateEdit:focus,
    QWidget#bookingWidget QSpinBox:focus {
        border: 2px solid #283593;
        background: #ffffff;
    }

    /* Dropdown list */
    QWidget#bookingWidget QComboBox::drop-down {
        border: none;
        width: 22px;
    }
    QWidget#bookingWidget QComboBox::down-arrow {
        image: url(Photo/down_arrow.png);
        width: 12px;
        height: 12px;
    }
    QWidget#bookingWidget QComboBox QAbstractItemView {
        border: 1px solid #283593;
        background: #ffffff;
        selection-background-color: #283593;
        selection-color: #ffffff;
    }

    /* Time + Spin arrows */
    QWidget#bookingWidget QTimeEdit::up-button,
    QWidget#bookingWidget QSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 18px;
        border-left: 1px solid #ced4da;
    }
    QWidget#bookingWidget QTimeEdit::down-button,
    QWidget#bookingWidget QSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 18px;
        border-left: 1px solid #ced4da;
    }
    QWidget#bookingWidget QTimeEdit::up-arrow,
    QWidget#bookingWidget QSpinBox::up-arrow {
        image: url(Photo/up_arrow.png);
        width: 10px;
        height: 10px;
    }
    QWidget#bookingWidget QTimeEdit::down-arrow,
    QWidget#bookingWidget QSpinBox::down-arrow {
        image: url(Photo/down_arrow.png);
        width: 10px;
        height: 10px;
    }

    /* DateEdit (calendar icon) */
    QWidget#bookingWidget QDateEdit::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 28px;
        border-left: 1px solid #ced4da;
        background: #f5f6ff;
    }
    QWidget#bookingWidget QDateEdit::down-arrow {
        image: url(Photo/calendar.png);   /* must exist */
        width: 18px;
        height: 18px;
        margin-right: 5px;
    }

    /* Calendar popup */
    QWidget#bookingWidget QCalendarWidget {
        border: 1px solid #283593;
        border-radius: 6px;
        background: #ffffff;
    }
    QWidget#bookingWidget QCalendarWidget QToolButton {
        color: #ffffff;
        font-weight: 600;
        background: transparent;
    }
    QWidget#bookingWidget QCalendarWidget QAbstractItemView:enabled {
        selection-background-color: #283593;
        selection-color: #ffffff;
    }
    QWidget#bookingWidget QCalendarWidget QAbstractItemView:item:hover {
        background: #e8eaf6;
    }

    /* Read-only values */
    QWidget#bookingWidget QLabel#readOnlyField {
        font-size: 14px;
        color: #1f2a56;
        background: #f4f6ff;
        border: 1px solid #e1e6ff;
        border-radius: 12px;
        padding: 6px 12px;
        margin-left: 6px;
    }

    /* Frames for student info */
    QWidget#bookingWidget QFrame#userFrame,
    QWidget#bookingWidget QFrame#studentFrame {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 8px;
    }
    QWidget#bookingWidget QFrame#userFrame {
        border: 1px solid #cdd6ff;
        background: #fafbff;
    }

    /* Checkbox (bigger + purple) */
    QWidget#bookingWidget QCheckBox#termsCheckbox {
        font-size: 16px;
        font-weight: 600;
        color: #2b2f36;
        spacing: 10px;
    }
    QWidget#bookingWidget QCheckBox#termsCheckbox::indicator {
        width: 22px;
        height: 22px;
        border: 2px solid #6A5ACD;
        border-radius: 5px;
        background: #ffffff;
    }
    QWidget#bookingWidget QCheckBox#termsCheckbox::indicator:checked {
        background-color: #6A5ACD;
        border: 2px solid #6A5ACD;
        image: url(Photo/check_icon.png); /* optional custom tick */
    }
    QWidget#bookingWidget QCheckBox#termsCheckbox::indicator:hover {
        border: 2px solid #4B3CBF;
    }

    /* Submit button (purple theme) */
    QWidget#bookingWidget QPushButton#submitButton {
        background-color: #283593;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 15px;
        font-weight: 700;
        min-width: 160px;
    }
    QWidget#bookingWidget QPushButton#submitButton:hover:enabled {
        background-color: #1A237E;
    }
    QWidget#bookingWidget QPushButton#submitButton:pressed:enabled {
        background-color: #141b5e;
    }
    QWidget#bookingWidget QPushButton#submitButton:disabled {
        background-color: #c7c9f1;
        color: #f3f3f7;
    }
    """
