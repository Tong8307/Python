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

    /* DateEdit / SpinBox */
    #dateEdit, #capacitySpin {
        border: 1px solid #ced4da;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 15px;
        min-height: 34px;
        width: 100px;
        background: #ffffff;
    }

    QDateEdit QCalendarWidget QToolButton {
    color: #ffffff;
    border: none;
    }


    #dateEdit::drop-down, #capacitySpin::up-button, #capacitySpin::down-button {
        background-color: #ffffff;      /* Match DateEdit */
        border-left: 1px solid #ced4da;
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
