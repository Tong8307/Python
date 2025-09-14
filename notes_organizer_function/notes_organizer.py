import os
from datetime import datetime

from styles.notes_organizer_styles import get_notes_organizer_styles
from database import db_manager as db

from PyQt5.QtCore import (
    Qt, QPoint, QRect, QTimer, QEasingCurve, QPropertyAnimation, QSize, QSizeF, pyqtSignal
)
from PyQt5.QtGui import (
    QPixmap, QPainter, QImage, QPen, QColor, QFont, QPainterPath, QCursor,
    QTransform, QIcon, QPdfWriter, QTextListFormat, QTextCharFormat
)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QMessageBox,
    QTabWidget, QFileDialog, QToolButton, QMenu, QPushButton, QWidgetAction,
    QFrame, QSlider, QComboBox, QColorDialog
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
        # rich text so formatting tools work
        self.setAcceptRichText(True)
        self.setMinimumHeight(360)
        self.setObjectName("notesEditor")

        # tools
        self.tool = None                   # "pencil"|"pen"|"marker"|"eraser"|None
        self.eraser_mode = "normal"        # "normal"|"lasso"
        self.colors = {"pencil": QColor("#555555"),
                       "pen": QColor("#000000"),
                       "marker": QColor("#ffeb3b")}
        self.widths = {"pencil": 2, "pen": 4, "marker": 14, "eraser": 22}
        self.alphas = {"pencil": 255, "pen": 255, "marker": 110}

        # overlay state
        self.strokes = []
        self._current_pts = []
        self.undo_stack = []
        self.redo_stack = []

        # images
        self.images = []
        self.selected_idx = None
        self._drag_offset = QPoint(0, 0)

        # overlay UI rects
        self._btn_delete_rect = None           # top-left of selected image
        self._resize_handle_rect = None        # bottom-right of selected image
        self._resizing_image = False
        self._resize_start_pos = None
        self._resize_start_size = None

        # cropping
        self._cropping = False
        self._crop_start = None
        self._crop_rect = None
        self._crop_drag_mode = None  # "move" | "nw"|"ne"|"sw"|"se"|"n"|"s"|"w"|"e"
        self._crop_drag_offset = QPoint(0, 0)
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
        self.selectionChangedForImage.emit(True)
        self.selected_idx = len(self.images) - 1
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
        # default crop rect centered over selected image
        im = self.images[self.selected_idx]
        pos_v = self._to_view(im["pos"]); sz = im["pm"].size()
        rect = QRect(pos_v.x() + sz.width()//6, pos_v.y() + sz.height()//6,
                     sz.width()//3*2//2*2, sz.height()//3*2//2*2)
        self._crop_rect = rect

        # floating buttons near bottom center
        y = self.viewport().height() - 40
        self._crop_cancel_btn.move(self.viewport().width()//2 - 46, y)
        self._crop_ok_btn.move(self.viewport().width()//2 + 10, y)
        self._crop_cancel_btn.show(); self._crop_ok_btn.show()
        self.viewport().update()

    def _cancel_crop(self):
        self._cropping = False
        self._crop_start = None
        self._crop_rect = None
        self._crop_drag_mode = None
        self._crop_cancel_btn.hide(); self._crop_ok_btn.hide()
        self.viewport().update()

    def _apply_crop(self):
        if not self._cropping or self.selected_idx is None or not self._crop_rect:
            self._cancel_crop(); return
        im = self.images[self.selected_idx]
        pm, pos_doc = im["pm"], im["pos"]
        rect_view = self._crop_rect
        rect_doc = QRect(rect_view.x(), rect_view.y()+self._vy(), rect_view.width(), rect_view.height())
        im_rect_doc = QRect(pos_doc, pm.size())
        rect_doc = rect_doc.intersected(im_rect_doc)
        if rect_doc.isEmpty(): self._cancel_crop(); return
        local = QRect(rect_doc.x()-pos_doc.x(), rect_doc.y()-pos_doc.y(), rect_doc.width(), rect_doc.height())
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

    # ---------- crop hit-testing ----------
    def _crop_handle_under(self, p: QPoint):
        if not self._crop_rect: return None
        r = self._crop_rect
        handle = 10
        def rect_at(x, y): return QRect(x-handle//2, y-handle//2, handle, handle)
        corners = {
            "nw": rect_at(r.left(),  r.top()),
            "ne": rect_at(r.right(), r.top()),
            "sw": rect_at(r.left(),  r.bottom()),
            "se": rect_at(r.right(), r.bottom()),
        }
        for k, rr in corners.items():
            if rr.contains(p): return k
        if r.adjusted(8,8,-8,-8).contains(p): return "move"
        if QRect(r.left()+r.width()//2-handle//2, r.top()-handle//2, handle, handle).contains(p): return "n"
        if QRect(r.left()+r.width()//2-handle//2, r.bottom()-handle//2, handle, handle).contains(p): return "s"
        if QRect(r.left()-handle//2, r.top()+r.height()//2-handle//2, handle, handle).contains(p): return "w"
        if QRect(r.right()-handle//2, r.top()+r.height()//2-handle//2, handle, handle).contains(p): return "e"
        return None

    # ---------- mouse & paint ----------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self._cropping:
                mode = self._crop_handle_under(e.pos())
                if mode:
                    self._crop_drag_mode = mode
                    self._crop_drag_offset = e.pos() - self._crop_rect.topLeft()
                else:
                    self._crop_start = e.pos()
                    self._crop_rect = QRect(self._crop_start, self._crop_start)
                self.viewport().update(); return

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
            # drag/resize
            if self._crop_drag_mode and e.buttons() & Qt.LeftButton:
                r = QRect(self._crop_rect)
                p = e.pos()
                if self._crop_drag_mode == "move":
                    tl = p - self._crop_drag_offset
                    self._crop_rect.moveTo(tl)
                else:
                    if "n" in self._crop_drag_mode: r.setTop(p.y())
                    if "s" in self._crop_drag_mode: r.setBottom(p.y())
                    if "w" in self._crop_drag_mode: r.setLeft(p.x())
                    if "e" in self._crop_drag_mode: r.setRight(p.x())
                    self._crop_rect = r.normalized()
                # aspect lock if any
                if self.crop_ratio:
                    r = QRect(self._crop_rect)
                    h = r.height()
                    w = int(round(h * self.crop_ratio))
                    if w <= 0: w = 1
                    r.setWidth(w)
                    self._crop_rect = r
                self.viewport().update(); return
            if self._crop_start and e.buttons() & Qt.LeftButton:
                r = QRect(self._crop_start, e.pos()).normalized()
                if self.crop_ratio:
                    h = r.height()
                    w = int(round(h * self.crop_ratio))
                    if r.left() == self._crop_start.x(): r.setRight(r.left() + w)
                    else: r.setLeft(r.right() - w)
                self._crop_rect = r
                self.viewport().update(); return

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

            if self._cropping:
                self._crop_drag_mode = None
                return

            if self.selected_idx is not None:
                self.viewport().update(); return

            if not self._current_pts:
                super().mouseReleaseEvent(e); return

            if self.tool == "eraser":
                if self.eraser_mode == "normal":
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
        p.setRenderHint(QPainter.Antialiasing)

        # images
        self._btn_delete_rect = None
        self._resize_handle_rect = None
        for i, im in enumerate(self.images):
            p.save(); p.setOpacity(im["opacity"])
            pos_v = self._to_view(im["pos"])
            p.drawPixmap(pos_v, im["pm"])
            p.restore()

            # overlay controls for selected image
            if self.selected_idx == i and not self._cropping:
                rect_v = QRect(pos_v, im["pm"].size())
                # subtle border
                pen = QPen(QColor(11,31,94,180)); pen.setWidth(2)
                p.setPen(pen); p.setBrush(Qt.NoBrush); p.drawRect(rect_v.adjusted(0,0,-1,-1))
                # delete (×) at top-left
                del_size = 18
                self._btn_delete_rect = QRect(rect_v.left()-1, rect_v.top()-1, del_size+6, del_size+6)
                p.setBrush(QColor(255,255,255,240)); p.setPen(QPen(QColor("#0b1f5e")))
                p.drawRoundedRect(self._btn_delete_rect, 5, 5)
                f = QFont(); f.setBold(True); f.setPointSize(10); p.setFont(f)
                p.drawText(self._btn_delete_rect, Qt.AlignCenter, "×")
                # resize handle (bottom-right)
                h = 14
                self._resize_handle_rect = QRect(rect_v.right()-h+1, rect_v.bottom()-h+1, h, h)
                p.setBrush(QColor("#0b1f5e")); p.setPen(Qt.NoPen)
                p.drawRect(self._resize_handle_rect)

        # strokes
        for s in self.strokes: s.paint(p, yoff)

        # live stroke preview
        if self._current_pts and self.tool in ("pencil","pen","marker","eraser") and not self._cropping:
            if self.tool == "eraser":
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

        # crop overlay
        if self._cropping and self._crop_rect:
            r = QRect(self._crop_rect)
            # darken outside
            p.save()
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(0,0,0,80))
            full = self.viewport().rect()
            p.drawRect(full)
            p.setCompositionMode(QPainter.CompositionMode_Clear)
            if self.crop_shape == "circle":
                d = min(r.width(), r.height())
                circle = QRect(r.center().x()-d//2, r.center().y()-d//2, d, d)
                path = QPainterPath(); path.addEllipse(circle)
                p.setCompositionMode(QPainter.CompositionMode_SourceOver)
                p.setPen(QPen(QColor("#00bcd4"), 2, Qt.SolidLine))
                p.setBrush(Qt.NoBrush); p.drawEllipse(circle)
                p.setPen(Qt.NoPen); p.setBrush(QColor(0,0,0,80))
            else:
                p.setCompositionMode(QPainter.CompositionMode_Source)
                p.setBrush(QColor(255,255,255,0))
                p.drawRect(r)
                p.setCompositionMode(QPainter.CompositionMode_SourceOver)
                p.setPen(QPen(QColor("#00bcd4"), 2)); p.setBrush(Qt.NoBrush); p.drawRect(r)
            p.restore()
            # handles
            handle = 10
            p.setBrush(QColor("#00bcd4")); p.setPen(Qt.NoPen)
            for pt in (r.topLeft(), r.topRight(), r.bottomLeft(), r.bottomRight(),
                       QPoint(r.center().x(), r.top()),
                       QPoint(r.center().x(), r.bottom()),
                       QPoint(r.left(), r.center().y()),
                       QPoint(r.right(), r.center().y())):
                p.drawRect(QRect(pt.x()-handle//2, pt.y()-handle//2, handle, handle))

        p.end()

    # ---------- image hit testing ----------
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
        # Placeholder for future DB-backed overlays.
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
    """Right-side image tools: Crop, Aspect/Shape, Rotate, Opacity. Closes with ✕."""
    startCrop = pyqtSignal()
    rotateStep = pyqtSignal(int)      # ±90
    rotateTo   = pyqtSignal(int)      # 0..360
    setOpacity = pyqtSignal(int)      # 0..100
    cropShapeChanged = pyqtSignal(str)
    cropRatioChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("imgPanel")
        self.setFrameShape(QFrame.StyledPanel)

        v = QVBoxLayout(self)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(12)

        # header with close 'x'
        hdr = QHBoxLayout()
        title = QLabel("Image"); title.setObjectName("imgPanelTitle")
        self.btn_close = QToolButton(); self.btn_close.setText("✕"); self.btn_close.setToolTip("Close")
        self.btn_close.clicked.connect(self.hide)
        hdr.addWidget(title); hdr.addStretch(); hdr.addWidget(self.btn_close)
        v.addLayout(hdr)

        # Crop controls
        crop_card = QFrame(); crop_card.setObjectName("imgCard")
        cv = QVBoxLayout(crop_card); cv.setContentsMargins(10,10,10,10); cv.setSpacing(8)

        row0 = QHBoxLayout()
        btn_start = QToolButton(); btn_start.setObjectName("notesTB"); btn_start.setText("Crop")
        btn_start.setToolTip("Start cropping")
        btn_start.clicked.connect(self.startCrop.emit)
        row0.addWidget(btn_start); row0.addStretch()
        cv.addLayout(row0)

        shape_row = QHBoxLayout()
        lbl_shape = QLabel("Shape")
        self.btn_rect = QToolButton(); self.btn_rect.setCheckable(True); self.btn_rect.setChecked(True)
        self.btn_rect.setText("▭"); self.btn_rect.setObjectName("notesTB")
        self.btn_circle = QToolButton(); self.btn_circle.setCheckable(True)
        self.btn_circle.setText("◯"); self.btn_circle.setObjectName("notesTB")
        shape_row.addWidget(lbl_shape); shape_row.addWidget(self.btn_rect); shape_row.addWidget(self.btn_circle); shape_row.addStretch()
        cv.addLayout(shape_row)

        self.btn_rect.toggled.connect(lambda on: on and self.cropShapeChanged.emit("rect"))
        self.btn_circle.toggled.connect(lambda on: on and self.cropShapeChanged.emit("circle"))

        ratio_row = QHBoxLayout()
        ratio_row.addWidget(QLabel("Aspect"))
        self.cb_ratio = QComboBox(); self.cb_ratio.addItems(["Free","1:1","4:5","5:4","16:9","3:2"])
        self.cb_ratio.currentTextChanged.connect(self.cropRatioChanged.emit)
        ratio_row.addWidget(self.cb_ratio); ratio_row.addStretch()
        cv.addLayout(ratio_row)

        v.addWidget(crop_card)

        # Rotate
        rot_card = QFrame(); rot_card.setObjectName("imgCard")
        rv = QVBoxLayout(rot_card); rv.setContentsMargins(10,10,10,10); rv.setSpacing(8)
        rv.addWidget(QLabel("Rotate"))
        rrow = QHBoxLayout()
        btn_l = QToolButton(); btn_l.setObjectName("notesTB"); btn_l.setIcon(QIcon(PHOTO("rotate_left.png"))); btn_l.setIconSize(QSize(20,20))
        btn_r = QToolButton(); btn_r.setObjectName("notesTB"); btn_r.setIcon(QIcon(PHOTO("rotate_right.png"))); btn_r.setIconSize(QSize(20,20))
        btn_l.clicked.connect(lambda: self.rotateStep.emit(-90)); btn_r.clicked.connect(lambda: self.rotateStep.emit(90))
        rrow.addWidget(btn_l); rrow.addWidget(btn_r); rrow.addStretch(); rv.addLayout(rrow)
        self.sld_angle = QSlider(Qt.Horizontal); self.sld_angle.setRange(0, 360); self.sld_angle.setValue(0)
        self.sld_angle.valueChanged.connect(self.rotateTo.emit); rv.addWidget(self.sld_angle)
        v.addWidget(rot_card)

        # Opacity
        adj_card = QFrame(); adj_card.setObjectName("imgCard")
        av = QVBoxLayout(adj_card); av.setContentsMargins(10,10,10,10); av.setSpacing(8)
        av.addWidget(QLabel("Opacity"))
        self.sld_opacity = QSlider(Qt.Horizontal); self.sld_opacity.setRange(0,100); self.sld_opacity.setValue(100)
        self.sld_opacity.valueChanged.connect(self.setOpacity.emit); av.addWidget(self.sld_opacity)
        v.addWidget(adj_card)

        v.addStretch()

        # hidden until an image exists
        self.hide()
        self.setEnabled(False)

    def set_from_props(self, props: dict):
        if not props: return
        self.sld_opacity.blockSignals(True); self.sld_opacity.setValue(props.get("opacity", 100)); self.sld_opacity.blockSignals(False)
        self.sld_angle.blockSignals(True); self.sld_angle.setValue(props.get("angle", 0)); self.sld_angle.blockSignals(False)

# ---------------- Note tab ----------------

class NoteTabWidget(QWidget):
    def __init__(self, note_id, user_id, title="", content="", overlay=None):
        super().__init__()
        self.note_id = note_id
        self.user_id = user_id 

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

        # Top toolbar (UNIFORM style, text tools BEFORE draw tools)
        tb = QHBoxLayout(); tb.setSpacing(6)

        def tb_btn(name, tip):
            b = QToolButton(); b.setIcon(QIcon(PHOTO(name))); b.setIconSize(QSize(28,28))
            b.setToolTip(tip); b.setObjectName("notesTB"); return b

        # text-formatting (left side)
        def mk_txt_btn(txt, tip):
            b = QToolButton(); b.setText(txt); b.setToolTip(tip); b.setObjectName("notesTB")
            return b

        self.btn_bold = mk_txt_btn("B", "Bold")
        self.btn_italic = mk_txt_btn("I", "Italic")
        self.btn_underline = mk_txt_btn("U", "Underline")
        self.btn_bullets = mk_txt_btn("•", "Bulleted list")

        self.cb_fontsize = QComboBox(); self.cb_fontsize.setObjectName("notesTB")
        self.cb_fontsize.addItems([str(s) for s in (10,12,14,16,18,20,24,28,32)])
        self.cb_fontsize.setCurrentText("14")

        self.btn_fontcolor = QToolButton(); self.btn_fontcolor.setObjectName("notesTB"); self.btn_fontcolor.setText("A")
        self.btn_fontcolor.setToolTip("Font color")
        self._font_color = QColor("#000000")
        self._refresh_font_color_button()

        for w in (self.btn_bold, self.btn_italic, self.btn_underline, self.btn_bullets, self.cb_fontsize, self.btn_fontcolor):
            tb.addWidget(w)

        tb.addWidget(QLabel("  |  "))

        # draw tools (right side of text tools)
        self.btn_img  = tb_btn("image.png", "Insert Image")
        self.btn_undo = tb_btn("undo.png", "Undo")
        self.btn_redo = tb_btn("redo_notes.png", "Redo")
        self.btn_pencil = tb_btn("pencil.png", "Pencil")
        self.btn_pen    = tb_btn("pen.png", "Pen")
        self.btn_mark   = tb_btn("marker.png", "Highlighter")
        self.btn_eras   = tb_btn("eraser.png", "Eraser")

        for b in (self.btn_img, self.btn_undo, self.btn_redo, self.btn_pencil, self.btn_pen, self.btn_mark, self.btn_eras):
            tb.addWidget(b)

        tb.addStretch(); root.addLayout(tb)

        # Main area
        main_row = QHBoxLayout(); main_row.setSpacing(8)
        wrap = QFrame(); wrap.setObjectName("noteBG")
        wrap_lay = QHBoxLayout(wrap); wrap_lay.setContentsMargins(10,10,10,10); wrap_lay.setSpacing(6)

        self.editor = InkTextEdit()
        if overlay: self.editor.dict_to_overlay(overlay)
        if content and "<" in content and "</" in content:
            self.editor.setHtml(content)
        else:
            self.editor.setPlainText(content)
        wrap_lay.addWidget(self.editor, 1)

        # Image tools panel (auto open when image exists; no extra icon)
        self.img_panel = ImageToolsPanel(); wrap_lay.addWidget(self.img_panel, 0)

        # Wire panel ↔ editor
        self.img_panel.rotateStep.connect(self.editor.rotate_selected_step)
        self.img_panel.rotateTo.connect(self.editor.rotate_selected_to)
        self.img_panel.setOpacity.connect(self.editor.set_selected_opacity)
        self.img_panel.cropShapeChanged.connect(self.editor.set_crop_shape)
        self.img_panel.cropRatioChanged.connect(self.editor.set_crop_ratio_string)
        self.img_panel.startCrop.connect(self.editor.begin_crop)

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

        self.btn_bold.clicked.connect(self._toggle_bold)
        self.btn_italic.clicked.connect(self._toggle_italic)
        self.btn_underline.clicked.connect(self._toggle_underline)
        self.btn_bullets.clicked.connect(self._toggle_bullets)
        self.cb_fontsize.currentTextChanged.connect(self._change_font_size)
        self.btn_fontcolor.clicked.connect(self._pick_font_color)

        # Use same PNGs for toolbar + cursors
        ICON_SIZE = 40; BTN_PAD = 16
        def _apply_big(btn): btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE)); btn.setFixedSize(ICON_SIZE+BTN_PAD, ICON_SIZE+BTN_PAD)
        for b in (self.btn_pencil, self.btn_pen, self.btn_mark, self.btn_eras): _apply_big(b)

        pencil_path = PHOTO("pencil.png")
        pen_path    = PHOTO("pen.png")
        marker_path = PHOTO("marker.png")
        eraser_path = PHOTO("eraser.png")
        self.editor.set_tool_pixmaps({"pencil":pencil_path,"pen":pen_path,"marker":marker_path,"eraser":eraser_path},
                                     base_size=ICON_SIZE)

        # UNIFORM toolbar styling for everything
        uni_css = (
            "QToolButton#notesTB{"
            "  border:2px solid #0b1f5e; border-radius:12px; background:#fff; padding:6px 10px;"
            "}"
            "QToolButton#notesTB:hover{ background:#e9eef7; }"
            "QComboBox#notesTB{"
            "  border:2px solid #0b1f5e; border-radius:12px; padding:4px 8px; background:#fff; min-width:56px;"
            "}"
            "QComboBox#notesTB::drop-down{ width: 0px; }"
        )
        for w in (self.btn_bold, self.btn_italic, self.btn_underline, self.btn_bullets, self.cb_fontsize,
                  self.btn_fontcolor, self.btn_img, self.btn_undo, self.btn_redo,
                  self.btn_pencil, self.btn_pen, self.btn_mark, self.btn_eras):
            try: w.setStyleSheet(uni_css)
            except Exception: pass

    # ---- UI helpers ----
    def _refresh_font_color_button(self):
        col = self._font_color.name()
        self.btn_fontcolor.setStyleSheet(
            "QToolButton#notesTB{border:2px solid #0b1f5e;border-radius:12px;background:#fff;padding:6px 10px;}"
            "QToolButton#notesTB:hover{background:#e9eef7;}"
            f"QToolButton#notesTB{{color:#0b1f5e;}}"
        )
        self.btn_fontcolor.setText("A")
        self.btn_fontcolor.setToolTip(f"Font color ({col})")

    # ---- text formatting slots ----
    def _merge_fmt(self, fmt: QTextCharFormat):
        cur = self.editor.textCursor()
        if not cur.hasSelection():
            self.editor.mergeCurrentCharFormat(fmt)
        else:
            cur.mergeCharFormat(fmt)
            self.editor.mergeCurrentCharFormat(fmt)

    def _toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Normal if self.editor.fontWeight() > QFont.Normal else QFont.Bold)
        self._merge_fmt(fmt)

    def _toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.editor.fontItalic())
        self._merge_fmt(fmt)

    def _toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.editor.fontUnderline())
        self._merge_fmt(fmt)

    def _toggle_bullets(self):
        cur = self.editor.textCursor()
        if cur.currentList():
            lst = cur.currentList()
            cur.beginEditBlock()
            block = cur.block()
            lst.remove(block)
            cur.endEditBlock()
        else:
            lf = QTextListFormat(); lf.setStyle(QTextListFormat.ListDisc)
            cur.createList(lf)

    def _change_font_size(self, s: str):
        try: val = float(s)
        except Exception: return
        fmt = QTextCharFormat(); fmt.setFontPointSize(val)
        self._merge_fmt(fmt)

    def _pick_font_color(self):
        c = QColorDialog.getColor(self._font_color, self, "Font color", QColorDialog.DontUseNativeDialog)
        if c.isValid():
            self._font_color = c
            fmt = QTextCharFormat(); fmt.setForeground(c)
            self._merge_fmt(fmt)
            self._refresh_font_color_button()

    def _on_image_count_change(self, count: int):
        # Panel only visible when images exist
        self.img_panel.setVisible(count > 0)
        self.img_panel.setEnabled(count > 0)
        if count > 0:
            # auto open
            self.img_panel.show()

    def _on_image_selection_change(self, has):
        self.img_panel.setEnabled(has or len(self.editor.images) > 0)
        if has and not self.img_panel.isVisible():
            self.img_panel.show()
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
            pal_lbl = QLabel(w)
            pal_icon = PHOTO("palette.png")
            if pal_icon:
                pal_lbl.setPixmap(QPixmap(pal_icon).scaled(35,35, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
            # Include user_id in the filename to avoid conflicts
            abs_path = os.path.join(MEDIA_DIR, f"{self.user_id}-{self.note_id}-{i}.png")
            pm.save(abs_path, "PNG")
            img_out.append({"abspath": abs_path, "pos": (pos.x(), pos.y()),
                            "opacity": im["opacity"], "angle": im["angle"]})
        overlay["images"] = img_out

        # Save content as HTML so formatting persists
        return {"title": (self.title_input.text().strip() or "Untitled"),
                "content": self.editor.toHtml(),
                "overlay": overlay,
                "updated_at": datetime.utcnow().isoformat(),
                "user_id": self.user_id}  # Include user_id in payload

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
    def __init__(self, on_return_callback=None, user_id=None):
        super().__init__()
        self.on_return_callback = on_return_callback
        self.user_id = user_id 
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
        self.btn_back = tb_btn("notes_back.png", "Back")
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
        rows = db.list_notes(self.user_id, order="updated_desc", limit=10)
        if rows:
            for r in rows:
                self._open_by_id(r["id"])
        else:
            self._new_note()

    # ----- internal helpers -----
    def _open_by_id(self, nid: int):
        # if already open, just focus that tab
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, NoteTabWidget) and getattr(w, "note_id", None) == nid:
                self.tabs.setCurrentIndex(i)
                return

        # Get note with user_id filter to ensure user owns the note
        row = db.get_note(nid, self.user_id)  # Pass user_id here
        if not row:
            QMessageBox.warning(self, "Access Denied", "You don't have permission to access this note.")
            return

        tab = NoteTabWidget(nid, self.user_id, row["title"] or "Untitled", row["content"] or "", overlay=None)
        idx = self.tabs.addTab(tab, self._elided(row["title"] or "Untitled"))
        self.tabs.setCurrentIndex(idx)
        tab.title_input.textChanged.connect(lambda s, i=idx: self.tabs.setTabText(i, self._elided(s or "Untitled")))
        tab._save_timer.timeout.connect(self._save_active)
    def _new_note(self):
        # Pass user_id when creating a new note
        nid = db.create_note("Untitled", "", user_id=self.user_id)
        self._open_by_id(nid)
        
    # In the _save_active method, ensure user_id is passed:
    def _save_active(self):
        w = self.tabs.currentWidget()
        if not isinstance(w, NoteTabWidget): return
        payload = w.to_payload()
        # Pass user_id when updating note
        db.update_note(w.note_id, payload["title"], payload["content"], user_id=self.user_id)
        self.tabs.setTabText(self.tabs.currentIndex(), self._elided(payload["title"]))

    def _elided(self, s: str) -> str: return s if len(s) <= 18 else (s[:15] + "…")

    def _close_tab(self, index: int):
        w = self.tabs.widget(index)
        if isinstance(w, NoteTabWidget):
            payload = w.to_payload()
            # Pass user_id when updating note
            db.update_note(w.note_id, payload["title"], payload["content"], user_id=self.user_id)
        self.tabs.removeTab(index)

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
