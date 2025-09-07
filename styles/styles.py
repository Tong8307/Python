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
        padding: 30px 30px;  
        font-size: 16px;
        border: none;
        color: #283593;
        font-weight: 500;
        margin: 0; 
    }

    #menuOptions:hover {
        background-color: #283593; 
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

    QLabel#bookingHeader {
        font-size: 30px;
        font-weight: 700;
        color: #283593;
        padding: 5px 0 0 5px;
        letter-spacing: 0.3px;
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