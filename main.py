import sys
import fitz
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QFileDialog, QToolBar
)
from PySide6.QtGui import QPixmap, QImage, QShortcut, QKeySequence
from PySide6.QtCore import Qt


class NogenPDF(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Nogen PDF Reader")
        self.resize(800, 600)

        self.label = QLabel("Abra um PDF")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background color: #f4ecd8")
        self.setCentralWidget(self.label)

        self.doc = None
        self.page_number = 0

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        open_btn = toolbar.addAction("Abrir")
        prev_btn = toolbar.addAction("←")
        next_btn = toolbar.addAction("→")

        open_btn.triggered.connect(self.open_pdf)
        prev_btn.triggered.connect(self.prev_page)
        next_btn.triggered.connect(self.next_page)

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
        pix = page.get_pixmap()

        img = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format_RGB888
        )

        self.label.setPixmap(QPixmap.fromImage(img))

        self.setWindowTitle(f"Nogen PDF Reader - Página {self.page_number + 1}")

    def next_page(self):
        if self.doc and self.page_number < len(self.doc) - 1:
            self.page_number += 1
            self.show_page()

    def prev_page(self):
        if self.doc and self.page_number > 0:
            self.page_number -= 1
            self.show_page()


app = QApplication(sys.argv)
window = NogenPDF()
window.show()
sys.exit(app.exec())
