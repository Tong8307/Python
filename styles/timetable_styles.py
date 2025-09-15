def get_timetable_styles():
    return """
    /* ===========================
       Timetable Page Styles
       =========================== */

    /* Booking Header */
    QLabel#bookingHeader {
        font-size: 28px;
        font-weight: 700;
        color: #283593;
        border-radius: 6px;
    }

    /* Labels */
    QLabel#formLabel {
        font-size: 18px;
        padding-left:8px;
        font-weight: 600;
        color: #4B4B4C;
        padding-bottom: 3px;
    }

    /* Legend items */
    QLabel#legendItem {
        font-size: 18px;
        font-weight: 600;
        color:#4B4B4C;
        padding: 6px 10px;
    }

    /* DateEdit / SpinBox / ComboBox */
    #dateEdit, #capacitySpin, #featureCombo {
        border: 2px solid #ced4da;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 15px;
        min-height: 34px;
        width: 100px;
        color: black;
        background-color: white;
    }

    /* Hover effects for form controls */
    #dateEdit:hover, #capacitySpin:hover, #featureCombo:hover {
        border: 2px solid #283593;
    }

    QDateEdit QCalendarWidget QToolButton {
        color: #ffffff;
        border: none;
    }

    /* Dropdown buttons - remove left border to show main control's border */
    #dateEdit::drop-down, #capacitySpin::up-button, #capacitySpin::down-button, #featureCombo::drop-down {
        background-color: white;
        border: none; /* Remove border to show main control's border */
        border-radius: 0 4px 4px 0;
        width: 28px;
    }

    #dateEdit::down-arrow {
        image: url(Photo/calendar.png);
        width: 18px;
        height: 18px;
        margin-right: 5px;
    }

    #capacitySpin::up-arrow {
        image: url(Photo/up_arrow.png);
        width: 12px;
        height: 12px;
    }

    #capacitySpin::down-arrow {
        image: url(Photo/down_arrow.png);
        width: 12px;
        height: 12px;
    }

    /* Feature Combo Box */
    #featureCombo {
        width: 200px;  /* Wider to accommodate feature names */
    }

    #featureCombo::drop-down {
        border: none; /* Remove border to show main control's border */
        width: 28px;
    }

    #featureCombo::down-arrow {
        image: url(Photo/down_arrow.png);
        width: 12px;
        height: 12px;
    }
    
    /* Dropdown list styling */
    QComboBox QAbstractItemView {
        background-color: white;
        color: black;
        selection-background-color: #3949ab;
        border: 2px solid #283593;
        border-radius: 4px;
    }

    /* Hover effect for dropdown items */
    QComboBox QAbstractItemView::item:hover {
        background-color: #e3e8ff;
    }

    /* Tooltips */
    QToolTip {
        background-color: #f5f5f5;
        color: #333333;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 13px;
    }
    """