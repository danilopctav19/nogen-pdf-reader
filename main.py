import json
import os
import sys
import fitz
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QFileDialog, QToolBar, QScrollArea,
    QLineEdit, QToolButton, QMenu, QMessageBox
)
from PySide6.QtGui import (
    QAction, QWheelEvent, QPixmap,
    QImage, QShortcut, QKeySequence
)
from PySide6.QtCore import Qt


class NogenPDF(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nogen PDF Reader")
        self.resize(800, 600)
        self.zoom = 1.0

        self.label = QLabel("Abra um PDF")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: #2b2b2b; color: #dddddd")
        self.config_path = "config.json"

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.label)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)
        self.fit_width = False
        self.fit_page = False

        self.doc = None
        self.page_number = 0
        self.recent_files = []

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        open_btn = toolbar.addAction("Abrir")

        self.recent_btn = QToolButton()
        self.recent_btn.setText("Recentes")
        self.recent_btn.setPopupMode(QToolButton.InstantPopup)

        self.recent_menu = QMenu(self)
        self.recent_btn.setMenu(self.recent_menu)

        toolbar.addWidget(self.recent_btn)

        prev_btn = toolbar.addAction("←")
        next_btn = toolbar.addAction("→")
        zoom_in_btn = toolbar.addAction("+")
        zoom_out_btn = toolbar.addAction("-")
        fit_btn = toolbar.addAction("Fit Width")

        open_btn.triggered.connect(self.open_pdf)
        prev_btn.triggered.connect(self.prev_page)
        next_btn.triggered.connect(self.next_page)
        zoom_in_btn.triggered.connect(self.zoom_in)
        zoom_out_btn.triggered.connect(self.zoom_out)
        fit_btn.triggered.connect(self.toggle_fit_width)
        
        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(40)
        self.page_input.setAlignment(Qt.AlignCenter)

        self.page_total = QLabel("/0")

        self.fit_btn = fit_btn
        toolbar.addWidget(self.page_input)
        toolbar.addWidget(self.page_total)

        toolbar.addSeparator()
        self.zoom_input = QLineEdit("100")
        self.zoom_input.setFixedWidth(50)
        self.zoom_input.setAlignment(Qt.AlignCenter)

        toolbar.addWidget(self.zoom_input)

        percent = QLabel("%")
        toolbar.addWidget(percent)

        self.zoom_input.returnPressed.connect(self.set_zoom)

        self.page_input.returnPressed.connect(self.go_to_page)

        QShortcut(QKeySequence("Right"), self).activated.connect(self.next_page)
        QShortcut(QKeySequence("Left"), self).activated.connect(self.prev_page)

        self.load_config()

    def open_pdf(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Abrir PDF", "", "PDF Files (*.pdf)"
        )

        if file:
            self.doc = fitz.open(file)
            self.page_number = 0
            self.show_page()

            self.add_recent_file(file)

    def show_page(self):
        if not self.doc:
            return

        page = self.doc.load_page(self.page_number)

        page_rect = page.rect

        view_width = self.scroll.viewport().width()
        view_height = self.scroll.viewport().height()

        if self.fit_page:
            zoom_w = view_width / page_rect.width
            zoom_h = view_height / page_rect.height
            self.zoom = min(zoom_w, zoom_h)

        elif self.fit_width:
            self.zoom = view_width / page_rect.width

        mat = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=mat)

        fmt = QImage.Format_RGB888 if pix.n < 5 else QImage.Format_RGBA8888

        img = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            fmt
        )

        self.label.setPixmap(QPixmap.fromImage(img))

        total = len(self.doc)
        current = self.page_number + 1

        self.page_input.setText(str(current))
        self.page_total.setText(f"/ {total}")

        zoom_percent = int(self.zoom * 100)
        self.zoom_input.setText(str(zoom_percent))

        self.setWindowTitle(f"Nogen PDF Reader - [{current}] de {total}")
        self.save_config()

    def save_config(self):
        if not self.doc:
            return

        data = {
            "last_file": self.doc.name,
            "last_page": self.page_number,
            "zoom": self.zoom,
            "fit_width": self.fit_width,
            "fit_page": self.fit_page,
            "recent_files": self.recent_files
        }

        with open(self.config_path, "w") as f:
            json.dump(data, f)

    def load_config(self):
        if not os.path.exists(self.config_path):
            return
        
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
            file = data.get("last_file")
            page = data.get("last_page", 0)
            zoom = data.get("zoom", 1.0)
            fit_width = data.get("fit_width", False)
            fit_page = data.get("fit_page", False)
            self.recent_files = data.get("recent_files", [])
            self.update_recent_menu()

            if file and os.path.exists(file):
                self.doc = fitz.open(file)
                self.zoom = zoom
                self.fit_width = fit_width
                self.fit_page = fit_page
                self.page_number = page
                self.show_page()

        except:
            pass

    def add_recent_file(self, filename):
        if filename in self.recent_files:
            self.recent_files.remove(filename)

        self.recent_files.insert(0, filename)

        self.recent_files = self.recent_files[:10]

        self.save_config()
        self.update_recent_menu()

    def next_page(self):
        if self.doc and self.page_number < len(self.doc) - 1:
            self.page_number += 1
            self.show_page()

    def prev_page(self):
        if self.doc and self.page_number > 0:
            self.page_number -= 1
            self.show_page()

    def go_to_page(self):
        if self.doc:
            try:
                page = int(self.page_input.text()) - 1
                if 0 <= page < len(self.doc):
                    self.page_number = page
                    self.show_page()
            except:
                pass

    def set_zoom(self):
        if self.doc:
            try:
                value = float(self.zoom_input.text())

                if 20 <= value <= 500:
                    self.zoom = value / 100
                    self.fit_width = False
                    self.fit_page = False
                    self.show_page()
                else:
                    self.show_page()

            except ValueError:
                self.show_page()

    def zoom_in(self):
        if self.doc:
            self.zoom += 0.2
            self.show_page()

    def zoom_out(self):
        if self.doc and self.zoom > 0.4:
            self.zoom -= 0.2
            self.show_page()

    def wheelEvent(self, event: QWheelEvent):
        if self.doc:
            modifiers = QApplication.keyboardModifiers()

            if modifiers == Qt.ControlModifier:
                delta = event.angleDelta().y()

                if delta > 0:
                    self.zoom += 0.1
                else:
                    if self.zoom > 0.2:
                        self.zoom -= 0.1

                self.fit_width = False
                self.fit_page = False

                self.zoom = max(0.2, min(self.zoom, 5.0))

                self.show_page()

    def toggle_fit_width(self):
        self.fit_width = not self.fit_width
    
        if self.fit_width:
            self.fit_btn.setText("☑ Fit Width")
        else:
            self.fit_btn.setText("☐ Fit Width")
    
        self.show_page()

    def update_recent_menu(self):
        self.recent_menu.clear()

        if not self.recent_files:
            action = QAction("(Nenhum arquivo recente)", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
            return

        for path in self.recent_files:
            filename = os.path.basename(path)

            action = QAction(filename, self)
            action.triggered.connect(
                lambda checked=False, p=path: self.open_recent_file(p)
            )

        self.recent_menu.addAction(action)

    def open_recent_file(self, path):
        if not os.path.exists(path):
            QMessageBox.warning(
                self,
                "Arquivo não encontrado",
                "O arquivo foi movido, renomeado ou excluído."
            )

            self.recent_files.remove(path)
            self.save_config()
            self.update_recent_menu()
            return

        self.doc = fitz.open(path)
        self.page_number = 0
        self.show_page()

        self.add_recent_file(path)

app = QApplication(sys.argv)
window = NogenPDF()
window.show()
sys.exit(app.exec())
