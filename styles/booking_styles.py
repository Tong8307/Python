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

    /*submit Button*/
    QPushButton#submitButton {
        background-color: #009688;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        min-width: 670px;
    }

    QPushButton#submitButton:hover {
        background-color: #006158;
    }

    QPushButton#submitButton:pressed {
        background-color: #006158;
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

    /* Expand button for student info */
    QWidget#bookingWidget QPushButton#expandButton {
        background-color: #5c6bc0;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        min-width: 160px;
        max-width: 180px;
    }
    
    QWidget#bookingWidget QPushButton#expandButton:hover {
        background-color: #3f51b5;
    }
    
    QWidget#bookingWidget QPushButton#expandButton:pressed {
        background-color: #3949ab;
    }
    
    /* ===========================
       Student Info Page Styles (GLOBAL - outside bookingWidget)
       =========================== */
    QLabel#instructionsLabel {
        font-size: 16px;
        font-weight: 600;
        color: #2b2f36;
        margin: 0;
        min-width:100px;
        padding-bottom: 3px;
    }

    QLabel#studentNumber {
        font-weight: bold;
        color: #283593;
        font-size: 16px;
        min-width: 30px;
        text-align: center;
    }

    /* Student Info Scroll Area - Matching booking style */
    QScrollArea#studentScroll {
        border: 1px solid #e9ecef;
        border-radius: 8px;
        background: #fafafa;
        padding: 5px;
    }

    /* Student frames in info page - matching booking style */
    QFrame#studentFrame {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 12px;
        margin: 5px;
    }

    QFrame#studentFrame:hover {
        border: 1px solid #cdd6ff;
        background: #fafbff;
    }

    /* Input fields in student info page */
    QLineEdit {
        border: 1px solid #ced4da;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 14px;
        min-height: 36px;
        background: #ffffff;
        min-width: 150px;
    }

    QLineEdit:focus {
        border: 2px solid #283593;
        background: #ffffff;
    }

    QLineEdit:read-only {
        background: #f4f6ff;
        border: 1px solid #e1e6ff;
        color: #1f2a56;
    }

    /* Form labels in student info page */
    QLabel#formLabel {
        font-size: 16px;
        font-weight: 600;
        color: #2b2f36;
        margin: 0;
        min-width:100px;
        padding-bottom: 3px;
    }

    /* Buttons for student info page */
    QPushButton#saveChanges {
        background-color: #009688;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        min-width: 120px;
    }

    QPushButton#saveChanges:hover {
        background-color: #006158;
    }

    QPushButton#saveChanges:pressed {
        background-color: #006158;
    }

    QPushButton#cancelButton {
        background-color: #6c757d;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        min-width: 120px;
    }

    QPushButton#cancelButton:hover {
        background-color: #5a6268;
    }

    QPushButton#cancelButton:pressed {
        background-color: #495057;
    }
    """