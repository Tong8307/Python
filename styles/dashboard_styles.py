def get_dashboard_styles():
    return """
    /* Root */
    QWidget#dashboardRoot {
        background: #f6f8ff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 60px;
    }

    /* Title */
    QLabel#dashTitle { color:#0b1f5e; font-size:20px; font-weight:800; padding:0 0 4px 0; }

    /* Search */
    QLineEdit#searchField {
        background:#fff; border:2px solid #1e3a8a; border-radius:12px;
        padding:6px 12px; min-height:32px; color:#0b1f5e;
    }
    QLineEdit#searchField:focus { border-color:#0b1f5e; }

    /* View toggle */
    QWidget#segWrap { background:#fff; border:2px solid #1e3a8a; border-radius:12px; padding:0; }
    QPushButton#viewBtnLeft, QPushButton#viewBtnRight {
        min-width:58px; min-height:32px; padding:6px 12px; border:none; color:#0b1f5e; font-weight:700; border-radius:10px;
    }
    QPushButton#viewBtnLeft:checked, QPushButton#viewBtnRight:checked { background:#1e3a8a; color:#fff; }
    QPushButton#viewBtnLeft:hover,  QPushButton#viewBtnRight:hover  { background:#e9eef7; color:#0b1f5e; }

    /* Filter & Add buttons */
    QToolButton#filterBtn { background:#fff; border:2px solid #1e3a8a; border-radius:12px; padding:6px 12px; min-height:32px; }
    QToolButton#filterBtn:hover { background:#e9eef7; }
    QToolButton#addButton {
        background:#1e3a8a; color:#fff; border:2px solid #1e3a8a; border-radius:12px; padding:6px 12px; min-height:32px; font-weight:800;
    }
    QToolButton#addButton:hover { background:#2947a9; border-color:#2947a9; }
    QToolButton#addButton:pressed { background:#163078; border-color:#163078; }

    /* Sidebar list (ensures selection palette) */
    QListWidget#folderList {
        background:#fff; border:2px solid #1e3a8a; border-radius:10px; padding:4px;
        selection-background-color:#1e3a8a; selection-color:#ffffff;
    }
    QListWidget#folderList::item { padding:2px 4px; color:#0b1f5e; border-radius:6px; }
    QListWidget#folderList::item:hover { background:#e9eef7; color:#0b1f5e; }
    QListWidget#folderList::item:selected,
    QListWidget#folderList::item:selected:hover { background:#1e3a8a; color:#ffffff; }

    /* Custom row widget used inside the list */
    QWidget#folderRow { border-radius:6px; }
    QLabel#folderText { color:#0b1f5e; }

    /* Hover (for non-selected rows) */
    QWidget#folderRow:hover { background:#e9eef7; }
    QWidget#folderRow:hover QLabel#folderText { color:#0b1f5e; }

    /* white text even when hovered */
    QListWidget#folderList QWidget#folderRow[selected="true"] { background:#1e3a8a; border-radius:6px; }
    QListWidget#folderList QWidget#folderRow[selected="true"] QLabel#folderText { color:#ffffff; }
    QListWidget#folderList QWidget#folderRow[selected="true"]:hover { background:#1e3a8a; }
    QListWidget#folderList QWidget#folderRow[selected="true"]:hover QLabel#folderText { color:#ffffff; }

    /* Menus */
    QMenu#addMenu, QMenu#popupMenu, QMenu#rowMenu { background:#fff; border:1px solid #cfd8dc; border-radius:10px; padding:6px; }
    QMenu#addMenu::separator, QMenu#popupMenu::separator, QMenu#rowMenu::separator { height:1px; background:#e5edf6; margin:6px 8px; }
    QMenu#addMenu::item, QMenu#popupMenu::item, QMenu#rowMenu::item { padding:8px 12px; border-radius:8px; color:#0b1f5e; font-weight:600; }
    QMenu#addMenu::item:selected, QMenu#popupMenu::item:selected, QMenu#rowMenu::item:selected { background:#e9eef7; color:#0b1f5e; }

    /* Notes table */
    QTableWidget#notesTable { background:#fff; border:2px solid #1e3a8a; border-radius:10px; gridline-color:#e2e8f0; alternate-background-color:#f7fafc; }
    QHeaderView::section { background:#eef2ff; padding:6px 8px; border:none; border-right:1px solid #dbe3f2; font-weight:700; color:#0b1f5e; min-height:28px; }
    QTableView::item { padding:2px 4px; }
    QTableView::item:hover { background:#e9eef7; }
    QTableView::item:selected { background:#e9eef7; color:#0b1f5e; }

    /* Row actions button */
    QToolButton#rowActionsBtn { border:none; background:transparent; min-width:20px; min-height:20px; padding:0; margin:0; }
    QToolButton#rowActionsBtn:hover { background:#eef2ff; border-radius:4px; }

    /* Grid view */
    QListWidget#gridView { border:2px solid #1e3a8a; border-radius:10px; background:#ffffff; }

    /* Empty label */
    QLabel#emptyLabel { color:#64748b; padding:10px; }
    """
