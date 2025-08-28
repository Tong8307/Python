def gpa_styles():
    return """
        QWidget#GPACalculatorWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #333333;
        }

        /* ===== Header Styles ===== */
        QLabel#gpaHeader {
            font-size: 30px;
            font-weight: bold;
            color: #283593;
            padding: 5px 0px 0px 5px;
        }

        /* ===== Sub Header Styles ===== */
        QLabel#gpaSubheader {
            font-size: 16px;
            font-weight: 500;
            color: #4B4B4C;
            padding: 0px 0px 0px 10px;
            margin-bottom: 10px;
        }

        /* Global styles */
        QLineEdit {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px;
            font-size: 14px;
            background-color: white;
        }

        QGroupBox {
            font-weight: bold;
            border: 1px solid #F3E5F5;
            border-radius: 5px;
            margin-top: 20px;
            padding-top: 15px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        #statusGroup, #courseGroup {
            background-color: white;
            padding: 10px;
        }

        QComboBox {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px;
            font-size: 14px;
            background-color: white;
            color: black;
        }

        QComboBox QAbstractItemView {
            border: 1px solid #ccc;
            background-color: white;
            selection-background-color: #3949AB;
            color: black;
        }

        QComboBox QAbstractItemView::item {
            padding: 4px;
        }

        QComboBox QAbstractItemView::item:selected {
            background-color: #3949AB;
            color: white;
        }

        QPushButton {
            background-color: #3949AB;
            color: white;
            border-radius: 4px;
            padding: 8px;
            font-weight: 500;
            font-size: 14px;
            border: none;
        }

        QPushButton:hover {
            background-color: #5C6BC0;
        }

        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #4B4B4C;
            padding: 0px 0px 0px 10px;
        }

        QLabel#course_header {
            font-weight: bold;
            font-size: 18px;
            color: #4B4B4C;
        }

        /* Add Course Button */
        QPushButton#addCourseButton {
            border: 2px dashed #673AB7;
            color: #673AB7;
            padding: 8px;
            font-weight: bold;
            background-color: transparent;
            font-size: 18px;
            border-radius: 8px;
        }

        QPushButton#addCourseButton:hover {
            background-color: #F3E5F5;
        }

        /* Reset Button */
        QPushButton#resetButton {
            border: 2px dashed #673AB7;
            color: #673AB7;
            padding: 8px;
            font-weight: bold;
            background-color: transparent;
            font-size: 18px;
            border-radius: 8px;
        }

        QPushButton#resetButton:hover {
            background-color: #F3E5F5;
        }

        /* Back Button */
        QPushButton#iconBackButton {
            background-color: #283593;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 15px 8px 10px;
        }

        QPushButton#iconBackButton:hover {
            background-color: #1A237E;
        }

        /* Remove Course Button */
        QPushButton#removeCourseButton {
            color: #ff4444;
            font-size: 18px;
            font-weight: bold;
            border: 1px solid #ffcccc;
            border-radius: 3px;
            background-color: transparent;
        }
        
        /* Result Card */
        QFrame#resultCard {
            background-color: white;
            border: 1px solid #F3E5F5;
            border-radius: 6px;
            padding: 5px; /* REDUCED from default */
        }
        
        /* Result Card Header - Tighter */
        QLabel#resultTitle {
            font-size: 24px;
            font-weight: bold;
            color: #673AB7;
            background-color: #F3E5F5;
            padding: 8px 12px; /* REDUCED vertical padding */
            border-radius: 4px;
            margin: 5px; /* ADD margin to separate from edges */
        }

        QLabel#resultItemLabel {
            font-weight: bold;
            color: #555;
            font-size: 20px;
            padding: 2px;
            margin: 0;
        }

        QLabel#resultValue {
            font-weight: bold;
            font-size: 22px;
            padding: 2px;
            margin: 0;
            color: #283593;
        }

        /* Separators */
        QFrame#resultSeparator {
            background-color: #ddd;
            margin: 5px 0;
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