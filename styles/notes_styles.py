def get_notes_organizer_styles():
    return """
    /* ===== Main Notes Organizer Container ===== */
    QWidget#notesWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #333333;
    }

    /* ===== Header ===== */
    QLabel#notesHeader {
        font-size: 28px;
        font-weight: bold;
        color: #283593;
        padding: 8px 0px 0px 10px;
    }

    /* ===== Category Label ===== */
    QLabel#categoryLabel {
        font-size: 16px;
        font-weight: 500;
        color: #4B4B4C;
        padding: 4px 0px 0px 10px;
    }

    /* ===== Notes List / Table ===== */
    QListWidget#notesList {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        font-size: 15px;
        padding: 5px;
    }

    QListWidget::item {
        padding: 10px;
        border-bottom: 1px solid #e9ecef;
    }

    QListWidget::item:selected {
        background-color: #E8EAF6;
        color: #283593;
    }

    /* ===== Buttons ===== */
    QPushButton#addNoteButton,
    QPushButton#editNoteButton,
    QPushButton#deleteNoteButton {
        background-color: white;
        color: #283593;
        border: 2px solid #283593;
        border-radius: 6px;
        padding: 10px;
        font-size: 15px;
        font-weight: 500;
        min-width: 150px;
        margin: 5px;
    }

    QPushButton#addNoteButton:hover,
    QPushButton#editNoteButton:hover,
    QPushButton#deleteNoteButton:hover {
        background-color: #E8EAF6;
        border: 2px solid #1A237E;
    }

    QPushButton#backButton {
        background-color: #f5f5f5;
        color: #555;
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 8px 15px;
        font-size: 14px;
        font-weight: 500;
        min-width: 120px;
    }

    QPushButton#backButton:hover {
        background-color: #e0e0e0;
        border-color: #ccc;
        color: #333;
    }

    QPushButton#backButton:pressed {
        background-color: #d0d0d0;
        border-color: #bbb;
        padding: 9px 15px 7px 15px;
    }

    /* ===== Note Content Area ===== */
    QTextEdit#noteContent {
        background-color: white;
        border: 1px solid #ced4da;
        border-radius: 6px;
        padding: 10px;
        font-size: 15px;
        min-height: 200px;
    }

    QTextEdit#noteContent:focus {
        border: 2px solid #80bdff;
    }

    /* ===== Input Fields ===== */
    QLineEdit#noteTitle, QComboBox#noteCategory {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 6px;
        font-size: 15px;
        min-height: 30px;
    }

    QLineEdit#noteTitle:focus, QComboBox#noteCategory:focus {
        border: 2px solid #80bdff;
    }

    /* ===== Message Labels ===== */
    QLabel#statusMessage {
        font-size: 13px;
        color: #6c757d;
        padding: 8px;
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

    /* ===== Scroll Container ===== */
    QScrollArea#scroll {
        border: none;
        background: transparent;
    }

    QScrollBar:vertical, QScrollBar:horizontal {
        width: 0px;
        height: 0px;
        background: transparent;
    }

    /* ===== Section Divider ===== */
    QFrame#divider {
        border: 1px solid #e9ecef;
        margin: 15px 0;
    }
    """
