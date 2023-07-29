'''
dependency:
pip3 install PySide2

shortcuts:
"[" -> last image
"]" -> next image
"\" -> delete image

Features:
1. Input box for jumping to image by name.

2. The app will automatically resume from the image that was last viewed by user, which is a good feature if the app crashed or closed unintentionally.
If you want to resume from the first image, you can use the "Start from First" button.
'''

import pickle
import os
import sys
from PySide2.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QMessageBox, QLineEdit
from PySide2.QtGui import QPixmap, QKeyEvent
from PySide2.QtCore import Qt, QObject, QEvent


class IgnoreKeysLineEdit(QLineEdit):
    def __init__(self, ignored_keys=None, parent=None):
        super().__init__(parent)
        self.ignored_keys = ignored_keys if ignored_keys else []

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in self.ignored_keys:
            event.ignore()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        self.setReadOnly(False)

    def focusOutEvent(self, event):
        self.setReadOnly(True)


class ImageViewer(QMainWindow):
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.deleted_folder_path = os.path.join(folder_path, "deleted")
        if not os.path.exists(self.deleted_folder_path):
            os.makedirs(self.deleted_folder_path)
        self.image_paths = self.get_image_paths()
        self.current_index = self.load_last_image_index()
        self.init_ui()

    def load_last_image_index(self):
        try:
            with open('last_image_index.pkl', 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return 0

    def save_current_index(self):
        with open('last_image_index.pkl', 'wb') as f:
            pickle.dump(self.current_index, f)

    def init_ui(self):
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        self.image_name_label = QLabel()
        self.image_name_label.setAlignment(Qt.AlignCenter)

        self.set_image()

        self.last_image_button = QPushButton("<- Last")
        self.last_image_button.clicked.connect(self.last_image)

        self.next_image_button = QPushButton("Next ->")
        self.next_image_button.clicked.connect(self.next_image)

        self.delete_image_button = QPushButton("Delete")
        self.delete_image_button.clicked.connect(self.confirm_delete_image)

        self.jump_to_button = QPushButton("Jump to")
        self.jump_to_button.clicked.connect(self.jump_to_image_by_name)

        self.start_from_first_button = QPushButton("Start from First")
        self.start_from_first_button.clicked.connect(self.start_from_first)

        self.jump_to_input = IgnoreKeysLineEdit(
            ignored_keys=[Qt.Key_BracketLeft, Qt.Key_BracketRight, Qt.Key_Backslash])
        self.jump_to_input.setReadOnly(True)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.last_image_button)
        button_layout.addWidget(self.next_image_button)
        button_layout.addWidget(self.delete_image_button)
        button_layout.addWidget(self.jump_to_input)
        button_layout.addWidget(self.jump_to_button)
        button_layout.addWidget(self.start_from_first_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.image_name_label)
        main_layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_BracketLeft:
            self.last_image()
        elif event.key() == Qt.Key_BracketRight:
            self.next_image()
        elif event.key() == Qt.Key_Backslash:
            self.confirm_delete_image()

    def get_image_paths(self):
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif"]
        image_paths = []
        for file_name in sorted(os.listdir(self.folder_path)):
            if os.path.splitext(file_name)[1].lower() in image_extensions:
                image_paths.append(os.path.join(self.folder_path, file_name))
        return image_paths

    def set_image(self):
        pixmap = QPixmap(self.image_paths[self.current_index])
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_name_label.setText(os.path.basename(self.image_paths[self.current_index]))
        self.save_current_index()

    def next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.set_image()

    def last_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.set_image()

    def confirm_delete_image(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("Confirm Delete")
        message_box.setText("Are you sure you want to delete this image?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.Yes)
        response = message_box.exec_()
        if response == QMessageBox.Yes:
            self.delete_image()

    def delete_image(self):
        os.rename(self.image_paths[self.current_index],
                  os.path.join(self.deleted_folder_path, os.path.basename(self.image_paths[self.current_index])))
        self.image_paths.pop(self.current_index)
        if self.current_index >= len(self.image_paths):
            self.current_index = len(self.image_paths) - 1
        self.set_image()

    def jump_to_image_by_name(self):
        image_name = self.jump_to_input.text()
        try:
            image_index = self.image_paths.index(os.path.join(self.folder_path, image_name))
            self.current_index = image_index
            self.set_image()
        except ValueError:
            print(f"No image named {image_name} in the directory.")

    def start_from_first(self):
        self.current_index = 0
        self.set_image()


if __name__ == "__main__":
    folder_path = "images"
    app = QApplication(sys.argv)
    image_viewer = ImageViewer(folder_path)
    image_viewer.show()
    sys.exit(app.exec_())
