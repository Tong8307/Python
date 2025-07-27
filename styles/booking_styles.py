def get_booking_styles():
    return """
    /* ===== Main Booking Container ===== */
    QWidget#bookingWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #333333;
    }

    /* ===== Header Styles ===== */
    QLabel#bookingHeader {
        font-size: 30px;
        font-weight: bold;
        color: #283593;
        padding: 5px 0px 0px 5px;
    }

    /* ===== Sub Header Styles ===== */
    QLabel#bookingSubheader {
        font-size: 18px;
        font-weight: 500;
        color: #4B4B4C;
        padding: 0px 0px 0px 10px;
    }

    /* ===== Room Table Styles ===== */
    QTableWidget {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        gridline-color: #e9ecef;
        font-size: 16px;
    }

    QTableWidget QHeaderView::section {
        background-color: #343a40;
        color: white;
        padding: 10px;
        font-size: 16px;
        border: none;
    }

    QTableWidget::item {
        padding: 12px;
        border-bottom: 1px solid #e9ecef;
    }

    /* ===== Book Button Styles ===== */
    QPushButton#bookButton {
        background-color: white;
        color: #283593;
        border: 2px solid #283593;
        border-radius: 8px;
        padding: 15px;
        font-size: 20px;
        font-weight: 500;
        min-width: 250px;
        margin: 5px;        
    }
            
    QPushButton#bookButton:hover {
        background-color: #E8EAF6;
        border: 2px solid #1A237E;
    }            
            
    /* ===== Back Button Styles ===== */
    QPushButton#iconBackButton {
        background-color: #283593;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 15px 8px 10px;
        spacing: 8px;
        text-align: center;
    }

    QPushButton#iconBackButton:hover {
        background-color: #1A237E;
    }

    /* ===== Status Message Styles ===== */
    QLabel#statusMessage {
        font-size: 14px;
        color: #6c757d;
        padding: 10px;
        border-radius: 4px;
    }

    QLabel#successMessage {
        background-color: #d4edda;
        color: #155724;
    }

    QLabel#errorMessage {
        background-color: #f8d7da;
        color: #721c24;
    }

    /* ===== Form Field Styles ===== */
    QLineEdit, QComboBox, QDateTimeEdit {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 8px;
        font-size: 15px;
        min-height: 35px;
    }

    QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus {
        border: 2px solid #80bdff;
    }

    /* ===== Section Dividers ===== */
    QFrame#divider {
        border: 1px solid #e9ecef;
        margin: 15px 0;
    }

    /* ===== Scroll Container ===== */
    QScrollArea#scroll{
        border: none;
        background: transparent;
    }
    QScrollBar:vertical, QScrollBar:horizontal {
        width: 0px;
        height: 0px;
        background: transparent;
    }
    """

