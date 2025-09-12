# styles/notes_organizer_styles.py
# White editor, dark-blue surroundings, cute buttons, styled image panel.

def get_notes_organizer_styles():
    return """
/* ===== Container ===== */
QWidget#notesOrganizer {
    background: #ffffff;
}

/* ===== Non-canvas area around editor ===== */
QFrame#noteBG {
    background: #0b1f5e;       /* dark blue surround */
    border-radius: 14px;
    padding: 6px;
}

/* ===== Tabs (fixed width + current dark blue) ===== */
QTabWidget#notesTabs QTabBar::tab {
  padding: 6px 12px;
  background: #e9eef7;
  color: #1e293b;
  border: 0px;
  border-radius: 8px;
  margin: 4px 3px;
  min-width: 120px;
  max-width: 160px;
}
QTabWidget#notesTabs QTabBar::tab:selected {
  background: #1e3a8a;
  color: white;
}
QTabWidget#notesTabs::pane { border: 0px; }

/* ===== Toolbar buttons (top) ===== */
QToolButton#notesTB {
    background: #ffffff;
    border: 2px solid #0b1f5e;
    color: #0b1f5e;
    border-radius: 14px;
    padding: 6px;
}
QToolButton#notesTB:hover { background: #f6f8ff; }

/* ===== Title input (cute) ===== */
QLineEdit#cuteTitleInput {
    background: #ffffff;
    border: 2px solid #0b1f5e;
    border-radius: 12px;
    padding: 10px 12px;
    font-size: 14px;
}
QLabel#titleCounter {
    color: #0b1f5e;
    font-weight: 600;
    padding-left: 8px;
}

/* ===== Editor scrollbars (blue handle) ===== */
QTextEdit#notesEditor {
  background: #ffffff;
  border-radius: 10px;
}
QTextEdit#notesEditor QScrollBar:vertical,
QTextEdit#notesEditor QScrollBar:horizontal {
  background: #e9eef7;
  width: 12px; height: 12px; border: none; margin: 0px;
}
QTextEdit#notesEditor QScrollBar::handle:vertical,
QTextEdit#notesEditor QScrollBar::handle:horizontal {
  background: #1e3a8a; border-radius: 6px; min-height: 24px; min-width: 24px;
}
QTextEdit#notesEditor QScrollBar::add-page:vertical,
QTextEdit#notesEditor QScrollBar::sub-page:vertical,
QTextEdit#notesEditor QScrollBar::add-page:horizontal,
QTextEdit#notesEditor QScrollBar::sub-page:horizontal {
  background: transparent;
}

/* ===== Floating crop buttons ===== */
QPushButton#cropFloatBtn {
    background: #0b1f5e; color: white; border: 0; border-radius: 8px;
    font-weight: 700;
}
QPushButton#cropFloatBtn:hover { background: #132a7a; }

/* ===== Image panel (white with blue border) ===== */
QFrame#imgPanel {
    background: #ffffff;
    border: 2px solid #0b1f5e;
    border-radius: 14px;
}
QLabel#imgPanelTitle {
    color: #0b1f5e; font-weight: 700; font-size: 16px;
}
QFrame#imgCard {
    background: #f9fbff;
    border: 2px solid #e1e8ff;
    border-radius: 12px;
}
QFrame#imgCard QLabel { color: #0b1f5e; }

/* Primary button look used in the Crop Start button */
QToolButton#primaryBtn {
    background: #0b1f5e; color: white; border: 0; border-radius: 12px; padding: 6px 10px;
    font-weight: 700;
}
QToolButton#primaryBtn:hover { background: #132a7a; }

/* Segment buttons for shape */
QToolButton#segmentBtn {
    background: #ffffff; color: #0b1f5e;
    border: 2px solid #0b1f5e; border-radius: 10px; padding: 4px 10px;
}
QToolButton#segmentBtn:checked {
    background: #0b1f5e; color: white;
}

/* Combo + Spin */
QComboBox, QSpinBox {
    background: #ffffff; border: 2px solid #0b1f5e; border-radius: 10px; padding: 4px 8px;
}

/* Sliders */
QSlider::groove:horizontal {
  height: 6px; background: #e1e8ff; border-radius: 3px;
}
QSlider::handle:horizontal {
  width: 16px; height: 16px;
  margin: -6px 0; border-radius: 8px;
  background: #0b1f5e; border: 2px solid #ffffff;
}

/* Reset button */
QPushButton#resetBtn {
    background: #ffffff; color: #0b1f5e; border: 2px solid #0b1f5e; border-radius: 12px; padding: 6px 10px; font-weight: 700;
}
QPushButton#resetBtn:hover { background: #f6f8ff; }
"""
