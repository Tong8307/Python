def load_stylesheet():
    return """
    /* ===== Global Styles ===== */
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #333333;
    }

    /* ===== Main Window ===== */
    QMainWindow {
        background-color: #f5f7fa;
    }

    /* ===== Header ===== */
    #headerWidget {
        background-color: #283593;
        height: 100px;
        border: none;
    }

    #headerWidget QLabel {
        color: white;
        font-size: 28px;
        font-weight: 600;
        padding: 30px;
        margin: 0;
    }

    /* ===== Sliding Menu ===== */
    #slidingMenu {
        background-color: white;
        color: #283593;
        border: none;
        border-right: 2px solid #1a252f;
    }

    /* ===== Profile Section ===== */
    #profileWidget {
        background-color: white;
        border-bottom: 2px solid #3d566e;
    }

    #avatarLabel {
        border: 3px solid #315FB5;
        border-radius: 75px;
        min-width: 150px;
        min-height: 150px;
        max-width: 150px;
        max-height: 150px;
    }

    #profileName {
        font-size: 28px;
        font-weight: 600;
        color: #283593;
        margin-top: 10px;
    }

    #profileID {
        font-size: 20px;
        color: #283593;
        margin-top: 5px;
    }

    /* ===== Menu Options ===== */
    #menuOptions {
        background-color: white;
        text-align: left;
        padding: 28px 30px;
        font-size: 16px;
        border: none;
        color: #283593;
        font-weight:500;
    }

    #menuOptions:hover {
        background-color: #303F9F; 
        color: white;
    }

    /* ===== Feature Buttons ===== */
    #FeatureButton {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
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
    
    /* ===== GPA Calculator ===== */
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
        margin-bottom: 10px;
    }

    QLabel {
        font-size: 14px;
    }

    QPushButton {
        background-color: #3949AB;
        color: white;
        padding: 10px;
        border-radius: 6px;
    }

    QPushButton:hover {
        background-color: #5C6BC0;
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