def gpa_styles():
    return """
    QLineEdit {
        border: 1px solid #bbb;
        border-radius: 6px;
        padding: 6px;
        font-size: 16px;
    }

    QComboBox {
        border: 1px solid #bbb;
        border-radius: 6px;
        padding: 4px;
        font-size: 16px;
        background-color: white;
    }

    QPushButton {
        background-color: #3949AB;
        color: white;
        border-radius: 6px;
        padding: 10px;
        font-weight: 500;
    }

    QPushButton:hover {
        background-color: #5C6BC0;
    }

    QLabel {
        font-size: 16px;
    }

    QLabel#resultLabel {
        font-size: 20px;
        font-weight: bold;
        color: #2E7D32;
        margin-top: 20px;
    }

    QLabel#title {
        font-size: 24px;
        font-weight: bold;
        color: #283593;
        margin-bottom: 15px;
    }

    QLabel#desc {
        color: #555;
        margin-bottom: 12px;
    }

    QLabel#course_label {
        font-weight: bold;
        font-size: 18px;
        margin-top: 15px;
    }

    QLabel {
        font-size: 14px;
    }

    QPushButton {
        border: 2px dashed #673AB7;
        color: #673AB7;
        padding: 10px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #F3E5F5;
    }

    #addCourseButton {
    border: 2px dashed #673AB7;
    color: #673AB7;
    padding: 10px;
    font-weight: bold;
    background-color: transparent;
    }

    #addCourseButton:hover {
        background-color: #F3E5F5;
    }
    """

def get_menu_button_style():
    return """
    QPushButton#menuButton {
        background-color: transparent;
        color : white;
        border: none;
        font-size: 20px;
    }
    #menuButton:hover {
        color: #C5CAE9;
    }
    """