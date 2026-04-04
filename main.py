import sys
import fitz
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QFileDialog, QToolBar, QScrollArea, QLineEdit
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
        
        self.page_input = QLineEdit()
        self.page_input.setFixedWidth(40)
        self.page_input.setAlignment(Qt.AlignCenter)

        self.page_total = QLabel("/0")

        toolbar.addWidget(self.page_input)
        toolbar.addWidget(self.page_total)

        toolbar.addSeparator()
        self.zoom_label = QLabel("100%")
        toolbar.addWidget(self.zoom_label)

        self.page_input.returnPressed.connect(self.go_to_page)

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

        self.page_input.setText(str(current))
        self.page_total.setText(f"/{total}")

        self.setWindowTitle(f"Nogen PDF Reader - [{current}] de {total} páginas")

        zoom_percent = int(self.zoom * 100)
        self.zoom_label.setText(f"{zoom_percent}%")

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
