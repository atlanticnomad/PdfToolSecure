import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QListWidget, QTabWidget, QLineEdit, QMessageBox, QComboBox, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt
from PIL import Image
import fitz  # PyMuPDF
import os

class PDFTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Tool")
        self.setMinimumSize(650, 480)

        self.language = "de"  # Default language is German
        self.texts = {
            "de": {
                "merge": "📎 PDFs zusammenführen",
                "images": "🖼 Bilder zu PDF",
                "select_pdfs": "📂 PDFs auswählen",
                "merge_btn": "✅ PDFs zusammenführen & speichern",
                "select_images": "🖼 Bilder auswählen",
                "convert_btn": "📄 Bilder in PDF umwandeln & speichern",
                "status_done": "✅ PDF gespeichert:",
                "msg_select_2pdfs": "Bitte wähle mindestens 2 PDF-Dateien aus.",
                "msg_select_images": "Bitte wähle mindestens ein Bild aus.",
                "msg_error_insert": "Fehler beim Einfügen:",
                "msg_error_save": "Fehler beim Speichern:",
                "password_label": "🔒 Passwort (optional):",
                "lang_select": "Sprache:"
            },
            "en": {
                "merge": "📎 Merge PDFs",
                "images": "🖼 Images to PDF",
                "select_pdfs": "📂 Select PDFs",
                "merge_btn": "✅ Merge & Save PDFs",
                "select_images": "🖼 Select Images",
                "convert_btn": "📄 Convert to PDF",
                "status_done": "✅ PDF saved:",
                "msg_select_2pdfs": "Please select at least 2 PDF files.",
                "msg_select_images": "Please select at least one image.",
                "msg_error_insert": "Error inserting:",
                "msg_error_save": "Error saving:",
                "password_label": "🔒 Password (optional):",
                "lang_select": "Language:"
            }
        }

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Language selector (ComboBox)
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Deutsch", "English"])
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # Main tabs: Merge PDF & Images to PDF
        self.tabs = QTabWidget()
        self.tabs.addTab(self.init_merge_pdf_tab(), self.tr("merge"))
        self.tabs.addTab(self.init_images_to_pdf_tab(), self.tr("images"))
        layout.addWidget(self.tabs)

        # Status label for feedback
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.update_language()

    def tr(self, key):
        # Returns the translated string based on the current language
        return self.texts[self.language].get(key, key)

    def update_language(self):
        # Update all UI labels to reflect selected language
        self.tabs.setTabText(0, self.tr("merge"))
        self.tabs.setTabText(1, self.tr("images"))
        self.btn_select_pdfs.setText(self.tr("select_pdfs"))
        self.btn_merge.setText(self.tr("merge_btn"))
        self.btn_select_images.setText(self.tr("select_images"))
        self.btn_convert.setText(self.tr("convert_btn"))
        self.pass_label_merge.setText(self.tr("password_label"))
        self.pass_label_img.setText(self.tr("password_label"))
        self.lang_label.setText(self.tr("lang_select"))

    def change_language(self, index):
        # Switch language between German (index 0) and English (index 1)
        self.language = "de" if index == 0 else "en"
        self.update_language()

    def init_merge_pdf_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.pdf_list = QListWidget()
        layout.addWidget(self.pdf_list)

        self.btn_select_pdfs = QPushButton()
        self.btn_select_pdfs.clicked.connect(self.select_pdfs)
        layout.addWidget(self.btn_select_pdfs)

        # Password field
        pass_layout = QHBoxLayout()
        self.pass_label_merge = QLabel()
        self.pass_input_merge = QLineEdit()
        self.pass_input_merge.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(self.pass_label_merge)
        pass_layout.addWidget(self.pass_input_merge)
        layout.addLayout(pass_layout)

        self.btn_merge = QPushButton()
        self.btn_merge.clicked.connect(self.merge_pdfs)
        layout.addWidget(self.btn_merge)

        tab.setLayout(layout)
        return tab

    def init_images_to_pdf_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.image_list = QListWidget()
        layout.addWidget(self.image_list)

        self.btn_select_images = QPushButton()
        self.btn_select_images.clicked.connect(self.select_images)
        layout.addWidget(self.btn_select_images)

        # Password field
        pass_layout = QHBoxLayout()
        self.pass_label_img = QLabel()
        self.pass_input_img = QLineEdit()
        self.pass_input_img.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(self.pass_label_img)
        pass_layout.addWidget(self.pass_input_img)
        layout.addLayout(pass_layout)

        self.btn_convert = QPushButton()
        self.btn_convert.clicked.connect(self.images_to_pdf)
        layout.addWidget(self.btn_convert)

        tab.setLayout(layout)
        return tab

    def select_pdfs(self):
        # Open file dialog to select multiple PDFs
        files, _ = QFileDialog.getOpenFileNames(self, self.tr("select_pdfs"), "", "PDF Dateien (*.pdf)")
        if files:
            self.pdf_list.clear()
            self.pdf_list.addItems(files)

    def merge_pdfs(self):
        # Merge selected PDFs into one file, optionally with password
        pdf_paths = [self.pdf_list.item(i).text() for i in range(self.pdf_list.count())]
        if len(pdf_paths) < 2:
            self.show_message(self.tr("msg_select_2pdfs"))
            return

        output_path, _ = QFileDialog.getSaveFileName(self, self.tr("merge_btn"), "", "PDF Datei (*.pdf)")
        if not output_path:
            return
        if not output_path.endswith(".pdf"):
            output_path += ".pdf"

        password = self.pass_input_merge.text()
        merged = fitz.open()
        try:
            for path in pdf_paths:
                merged.insert_pdf(fitz.open(path))
            if password:
                merged.save(output_path, encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw=password, user_pw=password)
            else:
                merged.save(output_path)
            self.status_label.setText(f"{self.tr('status_done')} {output_path}")
        except Exception as e:
            self.show_message(f"{self.tr('msg_error_insert')} {str(e)}")
        finally:
            merged.close()

    def select_images(self):
        # Open file dialog to select images
        files, _ = QFileDialog.getOpenFileNames(self, self.tr("select_images"), "", "Bilder (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if files:
            self.image_list.clear()
            self.image_list.addItems(files)

    def images_to_pdf(self):
        # Convert selected images to PDF, optionally with password
        image_paths = [self.image_list.item(i).text() for i in range(self.image_list.count())]
        if not image_paths:
            self.show_message(self.tr("msg_select_images"))
            return

        output_path, _ = QFileDialog.getSaveFileName(self, self.tr("convert_btn"), "", "PDF Datei (*.pdf)")
        if not output_path:
            return
        if not output_path.endswith(".pdf"):
            output_path += ".pdf"

        images = []
        for path in image_paths:
            try:
                img = Image.open(path).convert("RGB")
                images.append(img)
            except Exception as e:
                self.show_message(f"{self.tr('msg_error_insert')} {str(e)}")
                return

        try:
            tmp_path = "temp_unencrypted_output.pdf"
            if len(images) > 1:
                images[0].save(tmp_path, save_all=True, append_images=images[1:])
            else:
                images[0].save(tmp_path)

            password = self.pass_input_img.text()
            if password:
                doc = fitz.open(tmp_path)
                doc.save(output_path, encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw=password, user_pw=password)
                doc.close()
                os.remove(tmp_path)
            else:
                os.rename(tmp_path, output_path)

            self.status_label.setText(f"{self.tr('status_done')} {output_path}")
        except Exception as e:
            self.show_message(f"{self.tr('msg_error_save')} {str(e)}")

    def show_message(self, msg):
        # Show a warning dialog with a custom message
        QMessageBox.warning(self, "Hinweis", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFTool()
    window.show()
    sys.exit(app.exec())

