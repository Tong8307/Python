def gpa_styles():
    return """
        /* Global styles */
        QLineEdit {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px;
            font-size: 14px;
            background-color: white;
        }

        QComboBox {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px;
            font-size: 14px;
            background-color: white;
        }

        QPushButton {
            background-color: #3949AB;
            color: white;
            border-radius: 4px;
            padding: 8px;
            font-weight: 500;
            font-size: 14px;
        }

        QPushButton:hover {
            background-color: #5C6BC0;
        }

        QLabel {
            font-size: 14px;
        }

        /* Specific element styles */
        QLabel#title {
            font-size: 22px;
            font-weight: bold;
            color: #283593;
            margin-bottom: 5px;
        }

        QLabel#desc {
            color: #555;
            margin-bottom: 15px;
            font-size: 14px;
            padding: 5px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }

        QLabel#course_header {
            font-weight: bold;
            font-size: 16px;
            margin-top: 5px;
            color: #333;
        }

        /* Add Course Button */
        QPushButton#addCourseButton {
            border: 2px dashed #673AB7;
            color: #673AB7;
            padding: 8px;
            font-weight: bold;
            background-color: transparent;
            font-size: 16px;
            border-radius: 8px;
        }

        QPushButton#addCourseButton:hover {
            background-color: #F3E5F5;
        }

        /* Back Button */
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

        /* Result Card */
        QFrame#resultCard {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 6px;
        }
        
        /* Result Card Header */
        QLabel#resultTitle {
            font-size: 18px;
            font-weight: bold;
            color: #673AB7;
            background-color: #F3E5F5;
            padding: 12px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }

        /* Result Items */
        QLabel#resultItemLabel {
            font-weight: bold;
            color: #555;
            font-size: 15px;
        }

        QLabel#resultValue {
            color: #2E7D32;
            font-weight: bold;
            font-size: 18px;
            padding: 5px;
        }

        /* Scroll Area */
        QScrollArea {
            background-color: transparent;
            border: none;
        }

        QScrollArea QWidget {
            background-color: transparent;
        }
        
    """

def get_menu_button_style():
    return """
    QPushButton#menuButton {
        background-color: #283593;
        color: white;
        border: none;
        font-size: 20px;
    }
    
    QPushButton#menuButton:hover {
        color: #C5CAE9;
    }
    """