def gpa_styles():
    return """
        QWidget#GPACalculatorWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #333333;
        }

        /* ===========================
            Global + Shared
            =========================== */

        QLabel#gpaHeader {
            font-size: 30px;
            font-weight: 700;
            color: #283593;
            padding: 5px 0 0 5px;
            letter-spacing: 0.3px;
        }

        QLabel#gpaSubheader {
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
            border: 2px solid #F3E5F5;
            border-radius: 5px;
            margin-top: 20px;
            padding-top: 15px;
            background-color: white;
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
            selection-color: white;
            color: black;
        }

        QComboBox QAbstractItemView::item {
            background-color: white;
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
            border: 1px solid #673AB7;
            color: #673AB7;
            padding: 7px;
            font-weight: bold;
            background-color: #FFF0F5;
            font-size: 18px;
            border-radius: 8px;
        }

        QPushButton#addCourseButton:hover {
            background-color: #fae8ee;
        }

        /* Reset Button */
        QPushButton#resetButton {
            border: 1px solid #3949AB;
            color: #3949AB;
            padding: 7px;
            font-weight: bold;
            background-color: #E6E6FA;
            font-size: 18px;
            border-radius: 8px;
        }

        QPushButton#resetButton:hover {
            background-color: #DCDCF0;
        }

        /* History Button */
        QPushButton#historyButton {
            border: 1px solid #3949AB;
            color: #3949AB;
            padding: 7px;
            font-weight: bold;
            background-color: #E6E6FA;
            font-size: 18px;
            border-radius: 8px;
        }

        QPushButton#historyButton:hover {
            background-color: #DCDCF0;
        }

        /* Save Button */
        QPushButton#saveButton {
            border: 2px solid #673AB7;
            color: #673AB7;
            padding: 7px;
            font-weight: bold;
            background-color: #f3e9fd;
            font-size: 18px;
            border-radius: 8px;
        }

        QPushButton#saveButton:hover {
            background-color: #F3E5F5;
        }

        /* Calculate Button */
        QPushButton#calculateButton {
            border: 2px solid #673AB7;
            color: #673AB7;
            padding: 7px;
            font-weight: bold;
            background-color: #f3e9fd;
            font-size: 18px;
            border-radius: 8px;
        }

        QPushButton#calculateButton:hover {
            background-color: #F3E5F5;
        }

        /* Details Button */
        QPushButton#detailsButton {
            border: 1px solid #3949AB;
            color: #3949AB;
            padding: 6px;
            font-weight: 500;
            background-color: #E6E6FA;
            font-size: 18px;
            border-radius: 8px;
        }

        QPushButton#detailsButton:hover {
            background-color: #DCDCF0;
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
            border: 1px solid #BBDEFB;
            border-radius: 6px;
            padding: 5px; 
        }
        
        /* Result Card Header */
        QLabel#resultTitle {
            font-size: 26px;
            font-weight: bold;
            color: #1565C0;         
            background-color: #E3F2FD;  
            padding: 8px 12px;
            border-radius: 4px;
            margin: 5px;
            border: 1px solid #BBDEFB; 
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

        /* Table styles */
        QTableWidget {
            background-color: #ffffff;
            border: 1px solid #E1D7F6;
            gridline-color: #f0f0f0;
            alternate-background-color: #faf8fd;
            selection-color: white;
            font-weight: 600;
            font-size: 14px;
            outline: 0;
        }

        /* Table items */
        QTableWidget::item {
            padding: 10px 8px;
            border-bottom: 1px solid #f0f0f0;
            color: #4B4B4C;
        }

        /* Hover effect */
        QTableWidget::item:hover {
            background-color: #f3e9fd;
        }

        /* Header */
        QHeaderView::section {
            background-color: #f3e9fd;
            color: #673AB7;
            font-weight: bold;
            padding: 12px;
            border: none;
            font-size: 17px;
            text-align: center;
            min-height: 40px; 
        }

        /* Scroll bar styles */
        QScrollBar:vertical {
            border: none;
            background-color: #f8f9fa;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #3949AB;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #5C6BC0;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        /* ===== Feature Buttons ===== */
        #FeatureButton {
            background-color: white;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            padding: 15px;
        }

        #FeatureButton:hover {
            background-color: #E8EAF6;
            border: 1px solid #283593;
        }
        
        #iconLabel {
            min-width: 150px;
            min-height: 150px;
        }

        #textLabel {
            font-size: 28px;
            font-weight: 500;
        }
        
    """