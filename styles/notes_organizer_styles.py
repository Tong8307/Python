# styles/notes_organizer_styles.py
import os

def get_notes_organizer_styles() -> str:
    """
    QSS rules for the editor/organizer screen.
    Looks up a down-arrow asset if present for the font size combobox.
    """
    app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # find down.png in common asset folders
    arrow_png = ""
    for d in ("Photo", "assets", "icons", "images"):
        p = os.path.join(app_root, d, "down.png")
        if os.path.exists(p):
            arrow_png = p.replace("\\", "/")
            break
    arrow_rule = f"image: url({arrow_png});" if arrow_png else "image: none;"

    return f"""
QWidget#notesOrganizer {{
  background: #ffffff;
}}

QFrame#noteBG {{
  background: #0b1f5e;
  border-radius: 12px;
  padding: 6px;
}}

QToolButton#tabStepper {{
  padding: 0px 6px 8px;
  margin: 3px 1px 3px 4px;
  min-width: 10px;
  min-height: 14px;
  max-height: 14px;
  border: 1.5px solid #0b1f5e;
  border-radius: 6px;
  background: #ffffff;
  color: #0b1f5e;
  font: 500 20px "Segoe UI","Inter",system-ui,sans-serif;
}}
QToolButton#tabStepper:hover   {{ background: #f6f8ff; }}
QToolButton#tabStepper:pressed {{ background: #ffffff; }}
QToolButton#tabStepper:disabled {{
  background: #eaf0ff;
  border-color: #c6d3ff;
  color: #b8c1d4;
}}

QTabWidget#notesTabs::pane {{ border: 0; }}
QTabWidget#notesTabs QTabBar::tab {{
  padding: 2px 8px;
  margin: 2px 2px;
  min-width: 84px;
  max-width: 140px;
  background: #eef2ff;
  color: #1f2a44;
  border: 1px solid #d7defa;
  border-radius: 6px;
  font: 600 12px "Segoe UI","Inter",system-ui,sans-serif;
}}
QTabWidget#notesTabs QTabBar::tab:selected {{
  background: #1e3a8a;
  color: #ffffff;
  border-color: #1e3a8a;
}}
QTabWidget#notesTabs QTabBar::tab:hover:!selected {{ background: #e6ecff; }}
QTabWidget#notesTabs QTabBar::close-button {{
  subcontrol-position: right;
  width: 12px; height: 12px;
  margin-left: 4px;
}}
QTabWidget#notesTabs QTabBar::close-button:hover {{
  background: #ffffff;
  border: 1px solid #1e3a8a;
  border-radius: 6px;
}}
QTabWidget#notesTabs QTabBar::scroller {{ width: 0px; }}
QTabWidget#notesTabs QTabBar QToolButton {{
  width: 0px; height: 0px;
  margin: 0; padding: 0; border: none;
  background: transparent;
}}
QTabWidget#notesTabs::right-corner,
QTabWidget#notesTabs::left-corner {{
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
}}
QTabWidget#notesTabs QTabBar {{
  border: none;
  background: transparent;
}}

QWidget#tabCornerPanel {{ background: transparent; }}
QToolButton#cornerNew,
QToolButton#cornerNew:hover,
QToolButton#cornerNew:pressed,
QToolButton#cornerNew:checked,
QToolButton#cornerNew:focus {{
  min-width: 35px;
  min-height: 35px;
  max-height: 35px;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
}}

*[toolbarControl="true"] {{
  background: #ffffff;
  border: 2px solid #0b1f5e;
  color: #0b1f5e;
  border-radius: 14px;
  min-height: 32px;
  min-width: 36px;
  padding: 0 8px;
  font: 600 13px "Segoe UI", "Inter", system-ui, sans-serif;
  outline: 0;
}}
*[toolbarControl="true"]:hover   {{ background: #f1f5ff; }}
*[toolbarControl="true"]:pressed {{ background: #e6f0ff; }}
*[toolbarControl="true"]:disabled{{
  color: rgba(11,31,94,0.45);
  border-color: rgba(11,31,94,0.35);
  background: #fafbff;
}}
QToolButton[toolbarControl="true"]::menu-indicator {{ width: 0px; height: 0px; }}

QToolButton[toolbarControl="true"][bigText="true"] {{ font-size: 20px; }}
QComboBox[toolbarControl="true"][bigText="true"]   {{ font-size: 20px; }}

QComboBox[toolbarControl="true"] {{
  padding: 2px 14px 2px 2px;
  border-radius: 14px;
}}
QComboBox[toolbarControl="true"]::drop-down {{
  subcontrol-origin: padding;
  subcontrol-position: center right;
  width: 2px;
  border: 0;
  margin: 0;
}}
QComboBox[toolbarControl="true"]::down-arrow {{
  width: 10px; height: 10px;
  {arrow_rule}
  right: 10px;
}}
QComboBox[toolbarControl="true"] QAbstractItemView {{
  border: 1px solid #0b1f5e; border-radius: 8px; background: #fff; outline: 0;
  color: #0b1f5e; font: 600 12px "Segoe UI","Inter",system-ui,sans-serif;
}}
QComboBox[toolbarControl="true"] QAbstractItemView::item {{
  height: 20px; padding: 0 6px; border-radius: 4px;
}}
QComboBox[toolbarControl="true"] QAbstractItemView::item:hover    {{ background: #f1f5ff; }}
QComboBox[toolbarControl="true"] QAbstractItemView::item:selected {{ background: #e3eaff; }}

QTextEdit#notesEditor {{ background: #ffffff; border-radius: 10px; }}
QTextEdit#notesEditor QScrollBar:vertical,
QTextEdit#notesEditor QScrollBar:horizontal {{
  background: #e9eef7; width: 12px; height: 12px; border: none; margin: 0;
}}
QTextEdit#notesEditor QScrollBar::handle:vertical,
QTextEdit#notesEditor QScrollBar::handle:horizontal {{
  background: #1e3a8a; border-radius: 6px; min-height: 24px; min-width: 24px;
}}
QTextEdit#notesEditor QScrollBar::add-page:vertical,
QTextEdit#notesEditor QScrollBar::sub-page:vertical,
QTextEdit#notesEditor QScrollBar::add-page:horizontal,
QTextEdit#notesEditor QScrollBar::sub-page:horizontal {{ background: transparent; }}

QLineEdit#cuteTitleInput {{
  background: #ffffff; border: 2px solid #0b1f5e; border-radius: 12px;
  padding: 8px 10px; font-size: 14px;
}}
QLabel#titleCounter {{ color: #0b1f5e; font-weight: 600; padding-left: 6px; }}
QLabel#noteTitle    {{ color: #0b1f5e; font-weight: 700; font-size: 14px; }}

QMenu[toolbarMenu="true"] {{
  padding: 10px 12px;
  border: 1px solid #0b1f5e;
  border-radius: 10px;
  background: #ffffff;
}}
QMenu[toolbarMenu="true"] QWidget {{
  margin-top: 2px;
  margin-bottom: 2px;
}}
QMenu[toolbarMenu="true"] QLabel[toolPopup="true"],
QMenu[toolbarMenu="true"] QPushButton[toolPopup="true"] {{
  color: #0b1f5e;
  font-weight: 700;
}}
QMenu[toolbarMenu="true"] QPushButton[toolPopup="true"] {{
  padding: 0;
  min-width: 30px;
  min-height: 30px;
  border: 1px solid #0b1f5e;
  border-radius: 7px;
  qproperty-iconSize: 28px 28px;
}}
QMenu[toolbarMenu="true"] QPushButton[toolPopup="true"]:hover {{
  background: #f1f5ff;
}}
"""
