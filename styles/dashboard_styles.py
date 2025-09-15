def get_dashboard_styles():
    """
    QSS rules for the dashboard screen.
    Kept simple and consistent with the editor styles.
    """
    return """
    QWidget#dashboardRoot {
        background: #f6f8ff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 60px;
    }

    QLabel#dashTitle {
        color:#0b1f5e;
        font-size:20px;
        font-weight:800;
        padding:0 0 4px 0;
    }

    QLineEdit#searchField {
        background:#fff;
        border:2px solid #1e3a8a;
        border-radius:12px;
        padding:6px 12px;
        min-height:32px;
        color:#0b1f5e;
    }
    QLineEdit#searchField:focus { border-color:#0b1f5e; }

    QWidget#segWrap {
        background:#fff;
        border:2px solid #1e3a8a;
        border-radius:12px;
        padding:1px;
    }
    QPushButton#viewBtnLeft,
    QPushButton#viewBtnRight {
        min-width:70px;
        min-height:36px;
        padding:6px 14px;
        margin:0;
        border:none;
        background:transparent;
        color:#0b1f5e;
        font-weight:700;
        border-top-left-radius:11px;  border-bottom-left-radius:11px;
        border-top-right-radius:11px; border-bottom-right-radius:11px;
    }
    QPushButton#viewBtnLeft  { border-top-right-radius:0; border-bottom-right-radius:0; }
    QPushButton#viewBtnRight { border-top-left-radius:0;  border-bottom-left-radius:0;  }
    QPushButton#viewBtnLeft:hover,
    QPushButton#viewBtnRight:hover { background:transparent; color:#0b1f5e; }
    QPushButton#viewBtnLeft:pressed,
    QPushButton#viewBtnRight:pressed { background:#dde6fb; color:#0b1f5e; }
    QPushButton#viewBtnLeft:checked,
    QPushButton#viewBtnRight:checked,
    QPushButton#viewBtnLeft:checked:hover,
    QPushButton#viewBtnRight:checked:hover,
    QPushButton#viewBtnLeft:checked:pressed,
    QPushButton#viewBtnRight:checked:pressed {
        background:#1e3a8a;
        color:#ffffff;
    }

    QToolButton#filterBtn {
        background:#fff;
        border:2px solid #1e3a8a;
        border-radius:12px;
        padding:6px 12px;
        min-height:32px;
    }
    QToolButton#filterBtn:hover { background:#e9eef7; }

    QToolButton#addButton {
        background:#1e3a8a;
        color:#fff;
        border:2px solid #1e3a8a;
        border-radius:12px;
        padding:6px 12px;
        min-height:32px;
        font-weight:800;
    }
    QToolButton#addButton:hover  { background:#2947a9; border-color:#2947a9; }
    QToolButton#addButton:pressed{ background:#163078; border-color:#163078; }

    QListWidget#folderList {
        background:#fff;
        border:2px solid #1e3a8a;
        border-radius:10px;
        padding:4px;
    }
    QListWidget#folderList::item {
        padding:2px 4px;
        color:#0b1f5e;
        border-radius:6px;
    }
    QListWidget#folderList::item:hover { background:#e9eef7; color:#0b1f5e; }
    QListWidget#folderList::item:selected,
    QListWidget#folderList::item:selected:hover {
        background:#1e3a8a;
        color:#ffffff;
    }
    QWidget#folderRow { border-radius:6px; }
    QListWidget#folderList QWidget#folderRow QLabel#folderText { color:#0b1f5e; }
    QListWidget#folderList QWidget#folderRow:hover { background:#e9eef7; }
    QListWidget#folderList QWidget#folderRow:hover QLabel#folderText { color:#0b1f5e; }
    QListWidget#folderList QWidget#folderRow[selected="true"] { background:#1e3a8a; border-radius:6px; }
    QListWidget#folderList QWidget#folderRow[selected="true"] QLabel#folderText { color:#ffffff; }
    QListWidget#folderList QWidget#folderRow[selected="true"]:hover { background:#1e3a8a; }
    QListWidget#folderList QWidget#folderRow[selected="true"]:hover QLabel#folderText { color:#ffffff; }

    QMenu#addMenu, QMenu#popupMenu, QMenu#rowMenu {
        background:#fff;
        border:1px solid #cfd8dc;
        border-radius:12px;
        padding:6px;
    }
    QMenu#addMenu::separator, QMenu#popupMenu::separator, QMenu#rowMenu::separator {
        height:1px;
        background:#e5edf6;
        margin:6px 8px;
    }
    QMenu#addMenu::item, QMenu#popupMenu::item, QMenu#rowMenu::item {
        padding:8px 12px;
        border-radius:8px;
        color:#0b1f5e;
        font-weight:600;
    }
    QMenu#addMenu::item:selected, QMenu#popupMenu::item:selected, QMenu#rowMenu::item:selected {
        background:#e9eef7;
        color:#0b1f5e;
    }

    QTableWidget#notesTable {
        background:#fff;
        border:2px solid #1e3a8a;
        border-radius:10px;
        gridline-color:#e2e8f0;
        alternate-background-color:#f7fafc;
    }
    QTableWidget#notesTable QHeaderView { background: transparent; }
    QTableWidget#notesTable QHeaderView::section {
        background:#eef2ff;
        padding:6px 8px;
        margin-top: 2px;
        border:none;
        border-right:1px solid #dbe3f2;
        border-radius:0;
        font-weight:700;
        color:#0b1f5e;
        min-height:28px;
    }
    QTableWidget#notesTable QHeaderView::section:horizontal:first { margin-left:2px; }
    QTableWidget#notesTable QHeaderView::section:horizontal:last  { margin-right:2px; border-right:none; }
    QTableWidget#notesTable QTableCornerButton::section {
        background:#eef2ff;
        border:none;
        border-top-left-radius:10px;
    }

    QTableView::item { padding:2px 4px; }
    QTableView::item:hover { background:#e9eef7; }
    QTableView::item:selected { background:#e9eef7; color:#0b1f5e; }

    QToolButton#rowActionsBtn {
        border:none;
        background:transparent;
        min-width:20px;
        min-height:20px;
        padding:0;
        margin:0;
    }
    QToolButton#rowActionsBtn:hover { background:#eef2ff; border-radius:4px; }

    QListWidget#gridView {
        border:2px solid #1e3a8a;
        border-radius:10px;
        background:#ffffff;
        padding:8px;
    }
    QListWidget#gridView::item { margin:8px; padding:8px; border-radius:10px; }
    QListWidget#gridView::item:hover   { background:#f6f8ff; }
    QListWidget#gridView::item:selected{ background:#e9eef7; color:#0b1f5e; }

    QLabel#emptyLabel { color:#64748b; padding:10px; }

    QPushButton#iconBackButton {
        background-color: #283593;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 15px;
        font-weight: 600;
    }
    QPushButton#iconBackButton:hover { background-color: #1A237E; }
    QPushButton#iconBackButton:pressed { background-color: #141b5e; }
    """
