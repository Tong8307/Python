def get_login_styles():
    return """
    /* ===== Login Container ===== */
    QWidget#loginWidget {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                  stop: 0 #283593, stop: 1 #1A237E);
        font-family: 'Segoe UI', Arial, sans-serif;
    }

    /* ===== Title Styles ===== */
    QLabel#loginTitle {
        font-size: 50px;
        font-weight: bold;
        color: #283593;
        padding: 20px 0;
    }

    /* ===== Form Container ===== */
    QWidget#formContainer {
        background-color: white;
        border-radius: 12px;
        padding: 30px;
        border: 2px solid #E8EAF6;
    }

    /* ===== Form Label Styles ===== */
    QLabel#formLabel {
        font-size: 20px;
        font-weight: 600;
        color: #283593;
    }

    /* ===== Input Field Styles ===== */
    QLineEdit#inputField {
        border: 2px solid #E8EAF6;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        background-color: #FAFAFA;
        min-height: 40px;
    }

    QLineEdit#inputField:focus {
        border: 2px solid #283593;
        background-color: white;
    }

    QLineEdit#inputField:placeholder {
        color: #9E9E9E;
    }

    /* ===== Login Button Styles ===== */
    QPushButton#loginButton {
        background-color: #283593;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 15px;
        font-size: 16px;
        font-weight: 600;
        min-height: 20px;
    }

    QPushButton#loginButton:hover {
        background-color: #1A237E;
    }

    QPushButton#loginButton:pressed {
        background-color: #303F9F;
    }

    QPushButton#loginButton:disabled {
        background-color: #C5CAE9;
        color: #757575;
    }

    /* ===== Error Message Styles ===== */
    QLabel#errorMessage {
        background-color: #FFEBEE;
        color: #C62828;
        border: 1px solid #EF9A9A;
        border-radius: 6px;
        padding: 10px;
        font-size: 13px;
        margin: 10px 0;
    }

    /* ===== Success Message Styles ===== */
    QLabel#successMessage {
        background-color: #E8F5E8;
        color: #2E7D32;
        border: 1px solid #A5D6A7;
        border-radius: 6px;
        padding: 10px;
        font-size: 13px;
        margin: 10px 0;
    }

    /* ===== Link Styles ===== */
    QLabel#linkLabel {
        color: #283593;
        font-size: 13px;
        text-decoration: underline;
    }

    QLabel#linkLabel:hover {
        color: #1A237E;
        cursor: pointer;
    }

    
    """