import sys
import fitz
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QFileDialog, QToolBar, QScrollArea
)
from PySide6.QtGui import QPixmap, QImage, QShortcut, QKeySequence
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

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.label)
        self.scroll.setWidgetResizable(True)

        self.setCentralWidget(self.scroll)

        self.doc = None
        self.page_number = 0

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        open_btn = toolbar.addAction("Abrir")
        prev_btn = toolbar.addAction("←")
        next_btn = toolbar.addAction("→")
        zoom_in_btn = toolbar.addAction("+")
        zoom_out_btn = toolbar.addAction("-")

        open_btn.triggered.connect(self.open_pdf)
        prev_btn.triggered.connect(self.prev_page)
        next_btn.triggered.connect(self.next_page)
        zoom_in_btn.triggered.connect(self.zoom_in)
        zoom_out_btn.triggered.connect(self.zoom_out)

        QShortcut(QKeySequence("Right"), self).activated.connect(self.next_page)
        QShortcut(QKeySequence("Left"), self).activated.connect(self.prev_page)

    def open_pdf(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Abrir PDF", "", "PDF Files (*.pdf)"
        )

        if file:
            self.doc = fitz.open(file)
            self.page_number = 0
            self.show_page()

    def show_page(self):
        page = self.doc.load_page(self.page_number)

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

        self.setWindowTitle(f"Nogen PDF Reader - [{current}] de {total} páginas")

    def next_page(self):
        if self.doc and self.page_number < len(self.doc) - 1:
            self.page_number += 1
            self.show_page()

    def prev_page(self):
        if self.doc and self.page_number > 0:
            self.page_number -= 1
            self.show_page()

    def zoom_in(self):
        if self.doc:
            self.zoom += 0.2
            self.show_page()

    def zoom_out(self):
        if self.doc and self.zoom > 0.4:
            self.zoom -= 0.2
            self.show_page()

app = QApplication(sys.argv)
window = NogenPDF()
window.show()
sys.exit(app.exec())
