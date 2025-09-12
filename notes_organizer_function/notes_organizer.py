# notes_organizer_function/notes_organizer.py
# Notes editor (text + inking) backed by SQLite for note title/content only.
# Image/ink overlay is runtime-only for now; exports work as before.

import os
from datetime import datetime

from styles.notes_organizer_styles import get_notes_organizer_styles
from database import db_manager as db

from PyQt5.QtCore import (
    Qt, QPoint, QRect, QTimer, QEasingCurve, QPropertyAnimation, QSize, QSizeF, pyqtSignal
)
from PyQt5.QtGui import (
    QPixmap, QPainter, QImage, QPen, QColor, QFont, QPainterPath, QCursor,
    QTransform, QIcon, QPdfWriter
)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QMessageBox,
    QTabWidget, QFileDialog, QToolButton, QMenu, QPushButton, QWidgetAction,
    QFrame, QSlider, QComboBox, QSpinBox, QColorDialog
)

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MEDIA_DIR = os.path.join(APP_ROOT, "notes_media")

# ---- asset helpers (tries common folders) ----
ASSET_DIR_CANDIDATES = ["Photo", "assets", "icons", "images"]
def _find_asset(*names) -> str:
    for base in ASSET_DIR_CANDIDATES:
        for n in names:
            p = os.path.join(APP_ROOT, base, n)
            if os.path.exists(p):
                return p
    return ""
def PHOTO(name):  # keep compat
    return _find_asset(name)

# ---------------- Small model helpers ----------------

class Stroke:
    __slots__ = ("points", "color", "width", "alpha", "mode")
    def __init__(self, points, color, width, alpha=255, mode="pen"):
        self.points = points
        self.color = QColor(color)
        self.width = int(width)
        self.alpha = int(alpha)
        self.mode  = mode  # "pencil"|"pen"|"marker"

    def paint(self, p: QPainter, y_offset: int):
        pen = QPen(self.color)
        c = QColor(self.color); c.setAlpha(self.alpha)
        pen.setColor(c); pen.setWidth(self.width)
        pen.setCapStyle(Qt.RoundCap); pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen)
        if len(self.points) < 2: return
        path = QPainterPath(QPoint(self.points[0].x(), self.points[0].y() - y_offset))
        for pt in self.points[1:]:
            path.lineTo(pt.x(), pt.y() - y_offset)
        p.drawPath(path)

# ---------------- InkTextEdit: text + drawing overlay ----------------

class InkTextEdit(QTextEdit):
    """QTextEdit with an ink/image overlay that scrolls with content."""
    selectionChangedForImage = pyqtSignal(bool)
    imageCountChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)
        self.setMinimumHeight(360)
        self.setObjectName("notesEditor")

        # Neutral cursor (I-beam) until a tool is chosen
        self.tool = None                   # "pencil"|"pen"|"marker"|"eraser"|None
        self.eraser_mode = "normal"        # "normal"|"lasso"
        self.colors = {"pencil": QColor("#555555"),
                       "pen": QColor("#000000"),
                       "marker": QColor("#ffeb3b")}
        self.widths = {"pencil": 2, "pen": 4, "marker": 14, "eraser": 22}
        self.alphas = {"pencil": 255, "pen": 255, "marker": 110}

        # Overlay state
        self.strokes = []
        self._current_pts = []
        self.undo_stack = []
        self.redo_stack = []

        # images
        self.images = []
        self.selected_idx = None
        self._drag_offset = QPoint(0, 0)

        # overlay rects
        self._btn_delete_rect = None
        self._resize_handle_rect = None
        self._resizing_image = False
        self._resize_start_pos = None
        self._resize_start_size = None

        # cropping
        self._cropping = False
        self._crop_start = None
        self._crop_rect = None
        self.crop_ratio = None
        self.crop_shape = "rect"

        # floating ✔ / ✖ in crop
        self._crop_ok_btn = QPushButton("✔", self.viewport())
        self._crop_cancel_btn = QPushButton("✖", self.viewport())
        for b in (self._crop_ok_btn, self._crop_cancel_btn):
            b.hide(); b.setFixedSize(36, 28); b.setObjectName("cropFloatBtn")
        self._crop_ok_btn.clicked.connect(self._apply_crop)
        self._crop_cancel_btn.clicked.connect(self._cancel_crop)

        # cursor assets
        self._cursor_pixmaps = {}   # tool -> QPixmap
        self._cursor_base   = 36    # toolbar button size; cursor is ~0.5px smaller (logical)

        self._apply_tool_cursor()

    # ---------- coordinate helpers ----------
    def _vy(self): return self.verticalScrollBar().value()
    def _to_doc(self, p: QPoint) -> QPoint: return QPoint(p.x(), p.y() + self._vy())
    def _to_view(self, p: QPoint) -> QPoint: return QPoint(p.x(), p.y() - self._vy())

    # ---------- public: set tool pngs ----------
    def set_tool_pixmaps(self, mapping: dict, base_size: int = 36):
        self._cursor_pixmaps = {}
        for k, path in mapping.items():
            pm = QPixmap(path) if path else QPixmap()
            if not pm.isNull():
                self._cursor_pixmaps[k] = pm
        self._cursor_base = int(base_size)
        self._apply_tool_cursor()

    # ---------- cursor handling ----------
    def _apply_tool_cursor(self):
        cur = QCursor(Qt.IBeamCursor)
        if self.tool in ("pencil", "pen", "marker", "eraser"):
            pm = self._cursor_pixmaps.get(self.tool)
            if pm and not pm.isNull():
                # Cursor ~0.5 logical px smaller than toolbar icon (DPI-aware)
                dpr = getattr(self.window(), "devicePixelRatioF", lambda: 1.0)()
                cursor_logical = max(8.0, float(self._cursor_base) - 0.5)
                size_px = int(round(cursor_logical * dpr))
                pm2x = pm.scaled(size_px, size_px, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                try:
                    pm2x.setDevicePixelRatio(dpr)
                except Exception:
                    pass

                # Add N/L badge for eraser
                if self.tool == "eraser":
                    w, h = pm2x.width(), pm2x.height()
                    layered = QPixmap(w, h); layered.fill(Qt.transparent)
                    qp = QPainter(layered); qp.setRenderHint(QPainter.Antialiasing)
                    qp.drawPixmap(0, 0, pm2x)
                    br = QRect(w - 16, h - 14, 14, 12)
                    qp.setPen(QPen(QColor("#0b1f5e"))); qp.setBrush(QColor(255, 255, 255))
                    qp.drawRoundedRect(br, 3, 3)
                    qp.setPen(QPen(QColor("#0b1f5e"))); f = QFont(); f.setPointSize(7); f.setBold(True); qp.setFont(f)
                    qp.drawText(br, Qt.AlignCenter, "N" if self.eraser_mode == "normal" else "L")
                    qp.end()
                    try: layered.setDevicePixelRatio(dpr)
                    except Exception: pass
                    pm2x = layered

                cur = QCursor(pm2x)
        self.viewport().setCursor(cur)

    def enterEvent(self, e): self._apply_tool_cursor(); super().enterEvent(e)
    def leaveEvent(self, e): self.viewport().unsetCursor(); super().leaveEvent(e)

    def set_mode(self, mode: str):
        self.tool = mode
        self._apply_tool_cursor()

    def clear_mode_to_text(self):
        self.tool = None
        self._apply_tool_cursor()

    def set_eraser_mode(self, mode: str):
        self.eraser_mode = mode
        self._apply_tool_cursor()

    def set_tool_size(self, mode: str, width: int):
        if mode in self.widths:
            self.widths[mode] = max(1, int(width))

    # ---------- crop panel controls ----------
    def set_crop_shape(self, name: str): self.crop_shape = name or "rect"
    def set_crop_ratio_string(self, s: str):
        mapping = {"Free": None, "1:1": 1.0, "4:5": 4/5, "5:4": 5/4, "16:9": 16/9, "3:2": 3/2}
        self.crop_ratio = mapping.get(s, None)
    def set_crop_size(self, w: int, h: int):
        if not self._cropping or self._crop_rect is None: return
        tl = self._crop_rect.topLeft()
        self._crop_rect = QRect(tl, QSize(max(1, w), max(1, h)))
        self.viewport().update()

    # ---------- image ops ----------
    def insert_image(self, path: str):
        pm = QPixmap(path)
        if pm.isNull():
            QMessageBox.warning(self, "Image", "Failed to load image."); return
        pos_doc = QPoint(40, self._vy() + 40)
        self.images.append({"pm": pm, "base": pm, "pos": pos_doc, "opacity": 1.0, "angle": 0.0})
        self.undo_stack.append(("add_image", len(self.images) - 1))
        self.redo_stack.clear()
        self.imageCountChanged.emit(len(self.images))
        self.viewport().update()

    def get_selected_props(self):
        if self.selected_idx is None: return None
        im = self.images[self.selected_idx]
        return {"opacity": int(im["opacity"]*100), "angle": int(round(im["angle"]))}

    def set_selected_opacity(self, value: int):
        if self.selected_idx is None: return
        self.images[self.selected_idx]["opacity"] = max(0.0, min(1.0, value/100.0))
        self.viewport().update()

    def _rebuild_rotation(self, im, angle: float):
        im["angle"] = angle % 360
        t = QTransform(); t.rotate(im["angle"])
        im["pm"] = im["base"].transformed(t, Qt.SmoothTransformation)

    def rotate_selected_step(self, degrees: int):
        if self.selected_idx is None: return
        im = self.images[self.selected_idx]
        self._rebuild_rotation(im, im["angle"] + degrees)
        self.viewport().update()

    def rotate_selected_to(self, angle: int):
        if self.selected_idx is None: return
        im = self.images[self.selected_idx]
        self._rebuild_rotation(im, angle)
        self.viewport().update()

    def begin_crop(self):
        if self.selected_idx is None: return
        self._cropping = True
        self._crop_start = None
        self._crop_rect = None
        # show floating buttons near bottom center
        y = self.viewport().height() - 40
        self._crop_cancel_btn.move(self.viewport().width()//2 - 46, y)
        self._crop_ok_btn.move(self.viewport().width()//2 + 10, y)
        self._crop_cancel_btn.show(); self._crop_ok_btn.show()
        self.viewport().update()

    def _cancel_crop(self):
        self._cropping = False
        self._crop_start = None
        self._crop_rect = None
        self._crop_cancel_btn.hide(); self._crop_ok_btn.hide()
        self.viewport().update()

    def _apply_crop(self):
        if not self._cropping or self.selected_idx is None or not self._crop_rect:
            self._cancel_crop(); return
        im = self.images[self.selected_idx]
        pm, pos = im["pm"], im["pos"]
        rect_doc = self._crop_rect.intersected(QRect(pos, pm.size()))
        if rect_doc.isEmpty(): self._cancel_crop(); return
        local = QRect(rect_doc.x()-pos.x(), rect_doc.y()-pos.y(), rect_doc.width(), rect_doc.height())
        cropped = pm.copy(local)

        if self.crop_shape == "circle":
            size = min(cropped.width(), cropped.height())
            square = cropped.copy(0, 0, size, size)
            masked = QPixmap(size, size); masked.fill(Qt.transparent)
            qp = QPainter(masked); qp.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath(); path.addEllipse(0, 0, size, size)
            qp.setClipPath(path); qp.drawPixmap(0, 0, square); qp.end()
            cropped = masked

        im["base"] = cropped
        self._rebuild_rotation(im, im["angle"])
        self._cancel_crop()

    # ---------- reset adjustments ----------
    def reset_selected_image(self):
        if self.selected_idx is None: return
        im = self.images[self.selected_idx]
        im["opacity"] = 1.0
        self._rebuild_rotation(im, 0.0)  # keep base (size/crop)
        self.viewport().update()

    # ---------- hit testing ----------
    def _hit_image(self, p_view: QPoint):
        if self._btn_delete_rect and self._btn_delete_rect.contains(p_view):
            return "btn_delete"
        if self._resize_handle_rect and self._resize_handle_rect.contains(p_view):
            return "handle_resize"
        p_doc = self._to_doc(p_view)
        for i in reversed(range(len(self.images))):
            im = self.images[i]; pm, pos = im["pm"], im["pos"]
            if QRect(pos, pm.size()).contains(p_doc):
                return i
        return None

    def _confirm_delete_selected_image(self):
        if self.selected_idx is None: return
        reply = QMessageBox.question(self, "Delete Image", "Delete this image?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            idx = self.selected_idx
            item = self.images.pop(idx)
            self.undo_stack.append(("del_image", (idx, item)))
            self.redo_stack.clear()
            self.selected_idx = None
            self._btn_delete_rect = None
            self._resize_handle_rect = None
            self.selectionChangedForImage.emit(False)
            self.imageCountChanged.emit(len(self.images))
            self.viewport().update()

    # ---------- undo/redo ----------
    def undo(self):
        if not self.strokes and not self.images and not self.undo_stack:
            return
        if self.undo_stack:
            kind, payload = self.undo_stack.pop()
            if kind == "stroke":
                self.redo_stack.append(("stroke", self.strokes.pop()))
            elif kind == "add_image":
                self.redo_stack.append(("add_image", self.images.pop()))
                self.imageCountChanged.emit(len(self.images))
            elif kind == "del_image":
                idx, item = payload
                self.images.insert(idx, item)
                self.redo_stack.append(("del_image", idx))
                self.imageCountChanged.emit(len(self.images))
        elif self.strokes:
            self.redo_stack.append(("stroke", self.strokes.pop()))
        self.viewport().update()

    def redo(self):
        if not self.redo_stack: return
        kind, payload = self.redo_stack.pop()
        if kind == "stroke":
            self.strokes.append(payload); self.undo_stack.append(("stroke", None))
        elif kind == "add_image":
            self.images.append(payload); self.undo_stack.append(("add_image", len(self.images)-1))
            self.imageCountChanged.emit(len(self.images))
        elif kind == "del_image":
            idx = payload
            item = self.images.pop(idx)
            self.undo_stack.append(("del_image", (idx, item)))
            self.imageCountChanged.emit(len(self.images))
        self.viewport().update()

    # ---------- erasing helpers ----------
    def _near_any(self, pt: QPoint, eraser_pts, radius: int) -> bool:
        r2 = radius * radius
        x, y = pt.x(), pt.y()
        for ep in eraser_pts:
            dx, dy = ep.x()-x, ep.y()-y
            if dx*dx + dy*dy <= r2:
                return True
        return False

    def _erase_stroke_by_radius(self, stroke: Stroke, eraser_pts, radius: int):
        """Return list of stroke segments after pixel-like erase along path."""
        segments, cur = [], []
        for pt in stroke.points:
            if self._near_any(pt, eraser_pts, radius):
                if len(cur) >= 2:
                    segments.append(Stroke(cur, stroke.color, stroke.width, stroke.alpha, stroke.mode))
                cur = []
            else:
                cur.append(pt)
        if len(cur) >= 2:
            segments.append(Stroke(cur, stroke.color, stroke.width, stroke.alpha, stroke.mode))
        return segments

    # ---------- mouse & paint ----------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            hit = self._hit_image(e.pos())
            if hit == "btn_delete":
                self._confirm_delete_selected_image(); return
            if hit == "handle_resize" and self.selected_idx is not None:
                self._resizing_image = True
                self._resize_start_pos = e.pos()
                im = self.images[self.selected_idx]
                self._resize_start_size = im["base"].size()
                self.viewport().setCursor(Qt.SizeFDiagCursor); return
            if isinstance(hit, int):
                self.clear_mode_to_text()
                self.selected_idx = hit
                im = self.images[self.selected_idx]
                self._drag_offset = self._to_doc(e.pos()) - im["pos"]
                self.selectionChangedForImage.emit(True)
                self.viewport().update(); return

            if self.selected_idx is not None:
                self.selected_idx = None
                self.selectionChangedForImage.emit(False)
                self.viewport().update()

            if self.tool in ("pencil", "pen", "marker", "eraser"):
                self._current_pts = [self._to_doc(e.pos())]
                self.redo_stack.clear()
                self.viewport().update(); return
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._cropping:
            y = self.viewport().height() - 40
            self._crop_cancel_btn.move(self.viewport().width()//2 - 46, y)
            self._crop_ok_btn.move(self.viewport().width()//2 + 10, y)

        if self._resizing_image and self.selected_idx is not None and (e.buttons() & Qt.LeftButton):
            im = self.images[self.selected_idx]
            delta = e.pos() - self._resize_start_pos
            factor = max(0.1, 1.0 + (delta.x() + delta.y()) / 200.0)
            new_w = max(10, int(self._resize_start_size.width() * factor))
            new_h = max(10, int(self._resize_start_size.height() * factor))
            new_base = im["base"].scaled(new_w, new_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            im["base"] = new_base
            t = QTransform(); t.rotate(im["angle"])
            im["pm"] = new_base.transformed(t, Qt.SmoothTransformation)
            self.viewport().update(); return

        if self._cropping and self.selected_idx is not None and e.buttons() & Qt.LeftButton:
            cur = self._to_doc(e.pos())
            if self._crop_start is None: self._crop_start = cur
            r = QRect(self._crop_start, cur).normalized()
            if self.crop_ratio:
                h = r.height(); w = int(h * self.crop_ratio)
                if r.left() == self._crop_start.x(): r.setRight(r.left() + w)
                else: r.setLeft(r.right() - w)
            self._crop_rect = r
            self.viewport().update(); return

        if self.selected_idx is not None and e.buttons() & Qt.LeftButton and not self._cropping:
            im = self.images[self.selected_idx]
            im["pos"] = self._to_doc(e.pos()) - self._drag_offset
            self.viewport().update(); return

        if self._current_pts and e.buttons() & Qt.LeftButton:
            self._current_pts.append(self._to_doc(e.pos()))
            self.viewport().update(); return

        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self._resizing_image:
                self._resizing_image = False
                self._apply_tool_cursor()
                self.viewport().update(); return

            if self._cropping: return  # wait for ✔ / ✖
            if self.selected_idx is not None:
                self.viewport().update(); return

            if not self._current_pts:
                super().mouseReleaseEvent(e); return

            if self.tool == "eraser":
                if self.eraser_mode == "normal":
                    # Normal eraser: erase without preview path
                    radius = max(4, self.widths["eraser"])
                    new_strokes = []
                    changed = False
                    for s in self.strokes:
                        segs = self._erase_stroke_by_radius(s, self._current_pts, radius)
                        if len(segs) != 1 or segs and len(segs[0].points) != len(s.points):
                            changed = True
                        new_strokes.extend(segs)
                    if changed: self.undo_stack.append(("stroke", None))
                    self.strokes = new_strokes
                else:  # lasso
                    poly = self._current_pts[:]
                    survivors = []
                    changed = False
                    for s in self.strokes:
                        if any(self._point_in_poly(pt, poly) for pt in s.points):
                            changed = True
                            continue
                        survivors.append(s)
                    if changed: self.undo_stack.append(("stroke", None))
                    self.strokes = survivors
            else:
                pts = self._smooth(self._current_pts)
                if self.tool == "pencil":
                    color, width, alpha = self.colors["pencil"], self.widths["pencil"], self.alphas["pencil"]
                elif self.tool == "marker":
                    color, width, alpha = self.colors["marker"], self.widths["marker"], self.alphas["marker"]
                else:
                    color, width, alpha = self.colors["pen"], self.widths["pen"], self.alphas["pen"]
                self.strokes.append(Stroke(pts, color, width, alpha, self.tool))
                self.undo_stack.append(("stroke", None))

            self._current_pts = []
            self.viewport().update(); return

        super().mouseReleaseEvent(e)

    def paintEvent(self, ev):
        super().paintEvent(ev)
        p = QPainter(self.viewport()); yoff = self._vy()

        # images
        for im in self.images:
            p.save(); p.setOpacity(im["opacity"])
            p.drawPixmap(self._to_view(im["pos"]), im["pm"]); p.restore()

        # strokes
        for s in self.strokes: s.paint(p, yoff)

        # live stroke preview
        if self._current_pts and self.tool in ("pencil","pen","marker","eraser"):
            if self.tool == "eraser":
                # Only lasso shows a dashed preview; normal eraser shows none.
                if self.eraser_mode == "lasso":
                    pen = QPen(QColor("#999")); pen.setWidth(1); pen.setStyle(Qt.DashLine); p.setPen(pen)
                    path = QPainterPath(self._to_view(self._current_pts[0]))
                    for pt in self._current_pts[1:]: path.lineTo(self._to_view(pt))
                    p.drawPath(path)
            else:
                if self.tool == "pencil":
                    color, width, alpha = self.colors["pencil"], self.widths["pencil"], self.alphas["pencil"]
                elif self.tool == "marker":
                    color, width, alpha = self.colors["marker"], self.widths["marker"], self.alphas["marker"]
                else:
                    color, width, alpha = self.colors["pen"], self.widths["pen"], self.alphas["pen"]
                pen = QPen(color); c = QColor(color); c.setAlpha(alpha)
                pen.setColor(c); pen.setWidth(width); pen.setCapStyle(Qt.RoundCap); pen.setJoinStyle(Qt.RoundJoin); p.setPen(pen)
                path = QPainterPath(self._to_view(self._current_pts[0]))
                for pt in self._current_pts[1:]: path.lineTo(self._to_view(pt))
                p.drawPath(path)
        p.end()

    # ---------- helpers ----------
    def _smooth(self, pts):
        if len(pts) < 3: return pts[:]
        out = [pts[0]]
        for i in range(1, len(pts)-1):
            p0, p1, p2 = pts[i-1], pts[i], pts[i+1]
            qx = 0.25*p0.x() + 0.5*p1.x() + 0.25*p2.x()
            qy = 0.25*p0.y() + 0.5*p1.y() + 0.25*p2.y()
            out.append(QPoint(int(qx), int(qy)))
        out.append(pts[-1]); return out

    def _point_in_poly(self, pt: QPoint, poly: list) -> bool:
        x, y = pt.x(), pt.y(); inside = False; n = len(poly)
        for i in range(n):
            x1, y1 = poly[i].x(), poly[i].y()
            x2, y2 = poly[(i+1)%n].x(), poly[(i+1)%n].y()
            if ((y1 > y) != (y2 > y)) and (x < (x2-x1)*(y-y1)/(y2-y1+1e-9) + x1):
                inside = not inside
        return inside

    def overlay_to_dict(self):
        return {
            "strokes": [{
                "points": [(p.x(), p.y()) for p in s.points],
                "color": (s.color.red(), s.color.green(), s.color.blue()),
                "width": s.width, "alpha": s.alpha, "mode": s.mode
            } for s in self.strokes],
            "images": [{
                "abspath": None,
                "pos": (im["pos"].x(), im["pos"].y()),
                "opacity": im["opacity"], "angle": im["angle"]
            } for im in self.images]
        }

    def dict_to_overlay(self, d: dict):
        # Placeholder for future DB-backed overlays. For now, ignore persisted data.
        self.strokes = []
        self.images = []
        self.imageCountChanged.emit(0)
        self.viewport().update()

    def flattened_overlay_image(self, width_px=None) -> QImage:
        if width_px is None: width_px = max(640, self.viewport().width())
        doc = self.document().clone(); doc.setTextWidth(width_px)
        height_px = int(doc.size().height()) + 20
        img = QImage(width_px, max(200, height_px), QImage.Format_ARGB32); img.fill(Qt.white)
        p = QPainter(img); doc.drawContents(p, QRect(0, 0, width_px, height_px))
        for im in self.images:
            p.save(); p.setOpacity(im["opacity"]); p.drawPixmap(im["pos"], im["pm"]); p.restore()
        for s in self.strokes: s.paint(p, 0)
        p.end(); return img

# ---------------- Image Tools Panel ----------------

class ImageToolsPanel(QFrame):
    """Right-side, collapsible panel with smooth animation and cute styling."""
    startCrop = pyqtSignal()
    rotateStep = pyqtSignal(int)      # ±90
    rotateTo   = pyqtSignal(int)      # 0..360
    setOpacity = pyqtSignal(int)      # 0..100
    resetReq   = pyqtSignal()
    cropShapeChanged = pyqtSignal(str)
    cropRatioChanged = pyqtSignal(str)
    cropSizeEdited   = pyqtSignal(int, int)
    expandedChanged  = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("imgPanel")
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumWidth(220)
        self.setMaximumWidth(260)

        v = QVBoxLayout(self); v.setContentsMargins(12, 12, 12, 12); v.setSpacing(12)

        # header
        hdr = QHBoxLayout()
        title = QLabel("Image"); title.setObjectName("imgPanelTitle")
        self.btn_toggle = QToolButton()
        self.btn_toggle.setIcon(QIcon(PHOTO("panel_toggle.png")))
        self.btn_toggle.setIconSize(QSize(18,18))
        self.btn_toggle.setToolTip("Collapse/Expand")
        self.btn_toggle.clicked.connect(self.toggle)
        hdr.addWidget(title); hdr.addStretch(); hdr.addWidget(self.btn_toggle)
        v.addLayout(hdr)

        # Crop
        crop_card = QFrame(); crop_card.setObjectName("imgCard")
        cv = QVBoxLayout(crop_card); cv.setContentsMargins(10,10,10,10); cv.setSpacing(8)
        row0 = QHBoxLayout()
        lbl_crop = QLabel("Crop")
        btn_crop = QToolButton()
        btn_crop.setIcon(QIcon(PHOTO("edit.png"))); btn_crop.setIconSize(QSize(22,22))
        btn_crop.setText("Start"); btn_crop.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn_crop.setObjectName("primaryBtn")
        btn_crop.clicked.connect(self.startCrop.emit)
        row0.addWidget(lbl_crop); row0.addStretch(); row0.addWidget(btn_crop)
        cv.addLayout(row0)

        shape_row = QHBoxLayout()
        self.btn_rect = QToolButton(); self.btn_rect.setCheckable(True); self.btn_rect.setChecked(True)
        self.btn_rect.setText("▭"); self.btn_rect.setObjectName("segmentBtn")
        self.btn_circle = QToolButton(); self.btn_circle.setCheckable(True)
        self.btn_circle.setText("◯"); self.btn_circle.setObjectName("segmentBtn")
        shape_row.addWidget(self.btn_rect); shape_row.addWidget(self.btn_circle); shape_row.addStretch()
        cv.addLayout(shape_row)
        self.btn_rect.toggled.connect(lambda on: on and self._emit_shape("rect"))
        self.btn_circle.toggled.connect(lambda on: on and self._emit_shape("circle"))

        ratio_row = QHBoxLayout()
        ratio_row.addWidget(QLabel("Aspect"))
        self.cb_ratio = QComboBox(); self.cb_ratio.addItems(["Free","1:1","4:5","5:4","16:9","3:2"])
        self.cb_ratio.currentTextChanged.connect(self.cropRatioChanged.emit)
        ratio_row.addWidget(self.cb_ratio); ratio_row.addStretch()
        cv.addLayout(ratio_row)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("W")); self.sp_w = QSpinBox(); self.sp_w.setRange(1, 10000); self.sp_w.setButtonSymbols(QSpinBox.NoButtons)
        size_row.addWidget(self.sp_w); size_row.addWidget(QLabel("H"))
        self.sp_h = QSpinBox(); self.sp_h.setRange(1, 10000); self.sp_h.setButtonSymbols(QSpinBox.NoButtons)
        size_row.addWidget(self.sp_h); size_row.addStretch()
        cv.addLayout(size_row)
        self.sp_w.valueChanged.connect(lambda v: self.cropSizeEdited.emit(v, self.sp_h.value()))
        self.sp_h.valueChanged.connect(lambda v: self.cropSizeEdited.emit(self.sp_w.value(), v))

        v.addWidget(crop_card)

        # Rotate
        rot_card = QFrame(); rot_card.setObjectName("imgCard")
        rv = QVBoxLayout(rot_card); rv.setContentsMargins(10,10,10,10); rv.setSpacing(8)
        rv.addWidget(QLabel("Rotate"))
        rrow = QHBoxLayout()
        btn_l = QToolButton(); btn_l.setIcon(QIcon(PHOTO("rotate_left.png"))); btn_l.setIconSize(QSize(20,20))
        btn_r = QToolButton(); btn_r.setIcon(QIcon(PHOTO("rotate_right.png"))); btn_r.setIconSize(QSize(20,20))
        btn_l.clicked.connect(lambda: self.rotateStep.emit(-90)); btn_r.clicked.connect(lambda: self.rotateStep.emit(90))
        rrow.addWidget(btn_l); rrow.addWidget(btn_r); rrow.addStretch(); rv.addLayout(rrow)
        self.sld_angle = QSlider(Qt.Horizontal); self.sld_angle.setRange(0, 360); self.sld_angle.setValue(0)
        self.sld_angle.valueChanged.connect(self.rotateTo.emit); rv.addWidget(self.sld_angle)
        v.addWidget(rot_card)

        # Opacity + reset
        adj_card = QFrame(); adj_card.setObjectName("imgCard")
        av = QVBoxLayout(adj_card); av.setContentsMargins(10,10,10,10); av.setSpacing(8)
        av.addWidget(QLabel("Opacity"))
        self.sld_opacity = QSlider(Qt.Horizontal); self.sld_opacity.setRange(0,100); self.sld_opacity.setValue(100)
        self.sld_opacity.valueChanged.connect(self.setOpacity.emit); av.addWidget(self.sld_opacity)
        btn_reset = QPushButton("Reset adjustments"); btn_reset.setObjectName("resetBtn"); btn_reset.clicked.connect(self.resetReq.emit)
        av.addWidget(btn_reset); v.addWidget(adj_card)

        v.addStretch()

        # start disabled/hidden; will show when an image exists
        self.hide(); self.setEnabled(False)

    def _emit_shape(self, name: str): self.cropShapeChanged.emit(name)

    def set_from_props(self, props: dict):
        if not props: return
        self.sld_opacity.blockSignals(True); self.sld_opacity.setValue(props.get("opacity", 100)); self.sld_opacity.blockSignals(False)
        self.sld_angle.blockSignals(True); self.sld_angle.setValue(props.get("angle", 0)); self.sld_angle.blockSignals(False)

    # full collapse with animation & signal
    def set_expanded(self, expanded: bool):
        cur_expanded = (self.maximumWidth() > 0)
        if expanded == cur_expanded:
            self.expandedChanged.emit(expanded)
            return
        anim = QPropertyAnimation(self, b"maximumWidth", self)
        anim.setDuration(220); anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(self.maximumWidth()); anim.setEndValue(260 if expanded else 0)
        def _after():
            self.expandedChanged.emit(expanded)
        anim.finished.connect(_after)
        anim.start(); self._anim = anim

    def toggle(self): self.set_expanded(self.maximumWidth() == 0)

# ---------------- Note tab ----------------

class NoteTabWidget(QWidget):
    def __init__(self, note_id, title="", content="", overlay=None):
        super().__init__()
        self.note_id = note_id

        root = QVBoxLayout(self); root.setContentsMargins(10, 8, 10, 10); root.setSpacing(8)

        # Title (cute + counter 0/50)
        title_area = QVBoxLayout()
        lbl = QLabel("Note Title"); lbl.setStyleSheet("font-size:16px; font-weight:600; color:#0b1f5e;")
        title_row = QHBoxLayout()
        self.title_input = QLineEdit(title); self.title_input.setObjectName("cuteTitleInput")
        self.title_input.setPlaceholderText("Enter a cute title (max 50 chars)"); self.title_input.setMaxLength(50)
        self.counter = QLabel(f"{len(self.title_input.text())}/50"); self.counter.setObjectName("titleCounter")
        self.title_input.textChanged.connect(lambda s: self.counter.setText(f"{len(s)}/50"))
        title_row.addWidget(self.title_input); title_row.addWidget(self.counter)
        title_area.addWidget(lbl); title_area.addLayout(title_row); root.addLayout(title_area)

        # Top toolbar
        tb = QHBoxLayout(); tb.setSpacing(6)
        def tb_btn(name, tip):
            b = QToolButton(); b.setIcon(QIcon(PHOTO(name))); b.setIconSize(QSize(28,28))
            b.setToolTip(tip); b.setObjectName("notesTB"); return b
        self.btn_img  = tb_btn("image.png", "Insert Image")
        self.btn_undo = tb_btn("undo.png", "Undo")
        self.btn_redo = tb_btn("redo_notes.png", "Redo")
        self.btn_pencil = tb_btn("pencil.png", "Pencil")
        self.btn_pen    = tb_btn("pen.png", "Pen")
        self.btn_mark   = tb_btn("marker.png", "Highlighter")
        self.btn_eras   = tb_btn("eraser.png", "Eraser")
        for b in (self.btn_img, self.btn_undo, self.btn_redo,
                  self.btn_pencil, self.btn_pen, self.btn_mark, self.btn_eras):
            tb.addWidget(b)
        tb.addStretch(); root.addLayout(tb)

        # Main area
        main_row = QHBoxLayout(); main_row.setSpacing(8)
        wrap = QFrame(); wrap.setObjectName("noteBG")
        wrap_lay = QHBoxLayout(wrap); wrap_lay.setContentsMargins(10,10,10,10); wrap_lay.setSpacing(6)

        self.editor = InkTextEdit(); self.editor.setPlainText(content)
        if overlay: self.editor.dict_to_overlay(overlay)
        wrap_lay.addWidget(self.editor, 1)

        # Image panel + "peek" tab
        self.img_panel = ImageToolsPanel(); wrap_lay.addWidget(self.img_panel, 0)
        self.img_peek = QToolButton(); self.img_peek.setObjectName("imgPeek")
        self.img_peek.setIcon(QIcon(PHOTO("image.png"))); self.img_peek.setIconSize(QSize(18,18))
        self.img_peek.setFixedWidth(18); self.img_peek.setToolTip("Image tools")
        self.img_peek.clicked.connect(lambda: self.img_panel.set_expanded(True))
        wrap_lay.addWidget(self.img_peek, 0, Qt.AlignVCenter)
        self.img_peek.hide()

        # Wire panel ↔ editor
        self.img_panel.startCrop.connect(self.editor.begin_crop)
        self.img_panel.rotateStep.connect(self.editor.rotate_selected_step)
        self.img_panel.rotateTo.connect(self.editor.rotate_selected_to)
        self.img_panel.setOpacity.connect(self.editor.set_selected_opacity)
        self.img_panel.resetReq.connect(self.editor.reset_selected_image)
        self.img_panel.cropShapeChanged.connect(self.editor.set_crop_shape)
        self.img_panel.cropRatioChanged.connect(self.editor.set_crop_ratio_string)
        self.img_panel.cropSizeEdited.connect(self.editor.set_crop_size)
        self.img_panel.expandedChanged.connect(lambda expanded: self.img_peek.setVisible(not expanded))

        # Editor signals → panel visibility / enabling
        self.editor.selectionChangedForImage.connect(self._on_image_selection_change)
        self.editor.imageCountChanged.connect(self._on_image_count_change)

        main_row.addWidget(wrap, 1); root.addLayout(main_row, 1)

        # Debounced autosave
        self._save_timer = QTimer(self); self._save_timer.setSingleShot(True); self._save_timer.setInterval(800)
        self.title_input.textChanged.connect(self._debounce_save); self.editor.textChanged.connect(self._debounce_save)

        # Actions
        self.btn_img.clicked.connect(self._insert_image)
        self.btn_undo.clicked.connect(self.editor.undo); self.btn_redo.clicked.connect(self.editor.redo)
        self.btn_pencil.clicked.connect(lambda: self._tool_popup("pencil", self.btn_pencil))
        self.btn_pen.clicked.connect   (lambda: self._tool_popup("pen",    self.btn_pen))
        self.btn_mark.clicked.connect  (lambda: self._tool_popup("marker", self.btn_mark))
        self.btn_eras.clicked.connect  (lambda: self._tool_popup("eraser", self.btn_eras))

        # Use same PNGs for toolbar + cursors
        ICON_SIZE = 40; BTN_PAD = 16
        def _apply_big(btn): btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE)); btn.setFixedSize(ICON_SIZE+BTN_PAD, ICON_SIZE+BTN_PAD)
        for b in (self.btn_pencil, self.btn_pen, self.btn_mark, self.btn_eras): _apply_big(b)
        for b in (self.btn_pencil, self.btn_pen, self.btn_mark, self.btn_eras):
            b.setStyleSheet("QToolButton{border:2px solid #0b1f5e;border-radius:12px;background:#fff;}QToolButton:hover{background:#e9eef7;}")

        pencil_path = PHOTO("pencil.png")
        pen_path    = PHOTO("pen.png")
        marker_path = PHOTO("marker.png")
        eraser_path = PHOTO("eraser.png")
        self.editor.set_tool_pixmaps({"pencil":pencil_path,"pen":pen_path,"marker":marker_path,"eraser":eraser_path},
                                     base_size=ICON_SIZE)

        self._update_tool_button_styles()

    # ---- UI helpers ----
    def _q_rgba(self, c: QColor, a: int = 60) -> str:
        return f"rgba({c.red()},{c.green()},{c.blue()},{max(0,min(255,a))})"

    def _update_tool_button_styles(self):
        # Colored border + soft tint to indicate current tool color
        pc = self.editor.colors["pencil"]; pen = self.editor.colors["pen"]; mk = self.editor.colors["marker"]
        self.btn_pencil.setStyleSheet(
            f"QToolButton{{border:2px solid {pc.name()};border-radius:12px;background:{self._q_rgba(pc,40)};}}"
            "QToolButton:hover{background:#e9eef7;}"
        )
        self.btn_pen.setStyleSheet(
            f"QToolButton{{border:2px solid {pen.name()};border-radius:12px;background:{self._q_rgba(pen,30)};}}"
            "QToolButton:hover{background:#e9eef7;}"
        )
        self.btn_mark.setStyleSheet(
            f"QToolButton{{border:2px solid {mk.name()};border-radius:12px;background:{self._q_rgba(mk,70)};}}"
            "QToolButton:hover{background:#e9eef7;}"
        )
        # Eraser keeps neutral frame
        self.btn_eras.setStyleSheet("QToolButton{border:2px solid #0b1f5e;border-radius:12px;background:#fff;}QToolButton:hover{background:#e9eef7;}")

    def _on_image_count_change(self, count: int):
        self.img_panel.setVisible(count > 0)
        self.img_peek.setVisible(False)
        self.img_panel.setEnabled(False)

    def _on_image_selection_change(self, has):
        self.img_panel.setEnabled(has)
        if has:
            props = self.editor.get_selected_props()
            self.img_panel.set_from_props(props)

    def _debounce_save(self): self._save_timer.start()

    def _tool_popup(self, name: str, anchor_btn: QToolButton):
        self.editor.set_mode(name)
        menu = QMenu(self)
        w = QWidget(menu); row = QHBoxLayout(w); row.setContentsMargins(8,8,8,8); row.setSpacing(10)

        # Color picker (ONLY for pencil/pen/marker)
        if name in ("pencil", "pen", "marker"):
            pal_path = PHOTO("palette.png")
            if pal_path:
                pal_lbl = QLabel(w)
                pal_lbl.setPixmap(QPixmap(pal_path).scaled(35,35, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                row.addWidget(pal_lbl)

            swatch = QPushButton("  "); swatch.setFixedSize(28,28)
            def _set_swatch(col: QColor):
                swatch.setStyleSheet(f"border:2px solid #0b1f5e;border-radius:6px;background:{col.name()};")
            cur_col = self.editor.colors.get(name, QColor("#000"))
            _set_swatch(cur_col)

            def _pick():
                c = QColorDialog.getColor(cur_col, self, "Pick color", QColorDialog.DontUseNativeDialog)
                if c.isValid():
                    self.editor.colors[name] = c
                    _set_swatch(c)
                    self._update_tool_button_styles()

            swatch.clicked.connect(_pick)
            row.addWidget(swatch)

        # size presets
        def dot(font_pt, width_val):
            btn = QPushButton("●", w); f = btn.font(); f.setPointSize(font_pt); btn.setFont(f)
            btn.setFixedSize(28,28); btn.clicked.connect(lambda: (self.editor.set_tool_size(name, width_val), menu.close()))
            return btn

        if name == "pencil": sizes = [(8,2),(11,3),(14,4),(18,6)]
        elif name == "pen":  sizes = [(10,4),(13,6),(16,8),(20,10)]
        elif name == "marker": sizes = [(12,12),(16,16),(20,20),(24,26)]
        else: sizes = [(12,16),(16,22),(20,28),(24,36)]  # eraser only size + mode

        for fpt, wv in sizes: row.addWidget(dot(fpt, wv))

        if name == "eraser":
            # Only Normal/Lasso toggles; NO color picker
            row.addWidget(QLabel("  |  ", w))
            nbtn = QPushButton("Normal", w); lbtn = QPushButton("Lasso", w)
            nbtn.clicked.connect(lambda: (self.editor.set_eraser_mode("normal"), self.editor._apply_tool_cursor(), menu.close()))
            lbtn.clicked.connect(lambda: (self.editor.set_eraser_mode("lasso"),  self.editor._apply_tool_cursor(), menu.close()))
            row.addWidget(nbtn); row.addWidget(lbtn)

        w_action = QWidgetAction(menu); w_action.setDefaultWidget(w)
        menu.addAction(w_action)
        menu.exec_(anchor_btn.mapToGlobal(anchor_btn.rect().bottomLeft()))

    def to_payload(self) -> dict:
        os.makedirs(MEDIA_DIR, exist_ok=True)
        overlay = self.editor.overlay_to_dict()
        # Persist temp images for export
        img_out = []
        for i, im in enumerate(self.editor.images):
            pm, pos = im["pm"], im["pos"]
            abs_path = os.path.join(MEDIA_DIR, f"{self.note_id}-{i}.png")
            pm.save(abs_path, "PNG")
            img_out.append({"abspath": abs_path, "pos": (pos.x(), pos.y()),
                            "opacity": im["opacity"], "angle": im["angle"]})
        overlay["images"] = img_out

        return {"title": (self.title_input.text().strip() or "Untitled"),
                "content": self.editor.toPlainText(),
                "overlay": overlay,
                "updated_at": datetime.utcnow().isoformat()}

    def _insert_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.jpeg)")
        if path: self.editor.insert_image(path)

# ---------------- Organizer ----------------

class NoteOrganizerWidget(QWidget):
    """
    A tabbed notes editor that reads/writes notes to SQLite via db_manager.
    - On startup, opens up to 10 most recently updated notes (if any)
      or creates a new one.
    """
    def __init__(self, on_return_callback=None):
        super().__init__()
        self.on_return_callback = on_return_callback
        self.setWindowTitle("Notes Editor")
        self.setMinimumSize(780, 720)
        self.setObjectName("notesOrganizer")
        self.setStyleSheet(get_notes_organizer_styles())

        os.makedirs(MEDIA_DIR, exist_ok=True)

        main = QVBoxLayout(self); main.setContentsMargins(10, 10, 10, 10); main.setSpacing(8)

        # Header toolbar (Back / New / Save / Export)
        tb = QHBoxLayout(); tb.setSpacing(6)
        def tb_btn(name, tip):
            b = QToolButton(); b.setIcon(QIcon(PHOTO(name))); b.setIconSize(QSize(26,26))
            b.setToolTip(tip); b.setObjectName("notesTB"); return b
        self.btn_back = tb_btn("back.png", "Back")
        self.btn_new  = tb_btn("new.png", "New Note")
        self.btn_save = tb_btn("save.png", "Save")
        self.btn_export = QToolButton(); self.btn_export.setObjectName("notesTB"); self.btn_export.setText("Export")
        self.btn_export.setPopupMode(QToolButton.InstantPopup)
        m = QMenu(self); m.addAction("Export as TXT", self._export_txt); m.addAction("Export as PDF", self._export_pdf)
        self.btn_export.setMenu(m)
        for b in (self.btn_back, self.btn_new, self.btn_save, self.btn_export): tb.addWidget(b)
        tb.addStretch(); main.addLayout(tb)

        # Tabs
        self.tabs = QTabWidget(); self.tabs.setObjectName("notesTabs")
        self.tabs.setTabsClosable(True); self.tabs.tabCloseRequested.connect(self._close_tab)
        bar = self.tabs.tabBar()
        try:
            bar.setUsesScrollButtons(True); bar.setExpanding(False); bar.setElideMode(Qt.ElideRight); self.tabs.setMovable(True)
        except Exception: pass
        self.tabs.setStyleSheet(self.tabs.styleSheet() + "QTabBar::tab{min-width:120px;max-width:160px;}")
        main.addWidget(self.tabs, 1)

        # wire
        self.btn_back.clicked.connect(lambda: self.on_return_callback() if self.on_return_callback else None)
        self.btn_new.clicked.connect(self._new_note); self.btn_save.clicked.connect(self._save_active)

        # Start
        rows = db.list_notes(order="updated_desc", limit=10)
        if rows:
            for r in rows:
                self._open_by_id(r["id"])
        else:
            self._new_note()

    # ----- internal helpers -----
    def _open_by_id(self, nid: int):
        row = db.get_note(nid)
        if not row: return
        tab = NoteTabWidget(nid, row["title"] or "Untitled", row["content"] or "", overlay=None)
        idx = self.tabs.addTab(tab, self._elided(row["title"] or "Untitled"))
        self.tabs.setCurrentIndex(idx)
        tab.title_input.textChanged.connect(lambda s, i=idx: self.tabs.setTabText(i, self._elided(s or "Untitled")))
        tab._save_timer.timeout.connect(self._save_active)

    def _elided(self, s: str) -> str: return s if len(s) <= 18 else (s[:15] + "…")

    def _new_note(self):
        nid = db.create_note("Untitled", "")
        self._open_by_id(nid)

    def _close_tab(self, index: int):
        w = self.tabs.widget(index)
        if isinstance(w, NoteTabWidget):
            payload = w.to_payload()
            db.update_note(w.note_id, payload["title"], payload["content"])
        self.tabs.removeTab(index)

    def _save_active(self):
        w = self.tabs.currentWidget()
        if not isinstance(w, NoteTabWidget): return
        payload = w.to_payload()
        db.update_note(w.note_id, payload["title"], payload["content"])
        self.tabs.setTabText(self.tabs.currentIndex(), self._elided(payload["title"]))

    # Exports
    def _export_txt(self):
        w = self.tabs.currentWidget()
        if not isinstance(w, NoteTabWidget): return
        title = w.title_input.text().strip() or "Untitled"
        path, _ = QFileDialog.getSaveFileName(self, "Export TXT", f"{title}.txt", "Text Files (*.txt)")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(title + "\n\n" + w.editor.toPlainText())
        QMessageBox.information(self, "Export", "TXT file saved.")

    def _export_pdf(self):
        w = self.tabs.currentWidget()
        if not isinstance(w, NoteTabWidget): return
        title = w.title_input.text().strip() or "Untitled"
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", f"{title}.pdf", "PDF Files (*.pdf)")
        if not path: return
        img = w.editor.flattened_overlay_image(width_px=max(800, w.editor.viewport().width()))
        writer = QPdfWriter(path); writer.setResolution(96)
        mm_w = img.width() / 96.0 * 25.4; mm_h = img.height() / 96.0 * 25.4
        writer.setPageSizeMM(QSizeF(mm_w, mm_h))
        painter = QPainter(writer); painter.drawImage(0, 0, img); painter.end()
        QMessageBox.information(self, "Export", "PDF exported (with images and ink).")
