import sys
import argparse
import logging

from PySide2.QtCore import Qt, QObject
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QStyle, QLineEdit,\
                              QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout,\
                              QFileDialog, QRadioButton, QLabel, QComboBox, QButtonGroup
from PySide2.QtGui import QGuiApplication, QIcon

from utils import main
import log_util


log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='Debug mode')
    return parser.parse_args()


class Gui(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.widget = QWidget(self)
        self.init_ui(title)

    def init_ui(self, title):
        self.config(title)
        self.add_widgets()

    def config(self, title):
        self.setWindowTitle(title)
        self.setFixedSize(800, 350)
        self.widget.setFixedSize(800, 350)
        self.set_icon()
        self.center()

    def add_widgets(self):
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.input())
        self.vbox.addLayout(self.output())
        self.vbox.addLayout(self.custom())
        self.widget.setLayout(self.vbox)

    def set_icon(self):
        icon = QIcon('icon.jpg')
        self.setWindowIcon(icon)

    def center(self):
        self.setGeometry(
            QStyle.alignedRect(
                Qt.LeftToRight,
                Qt.AlignCenter,
                self.size(),
                QGuiApplication.primaryScreen().availableGeometry(),
            ),
        )

    def input(self):
        self.audio_path = QLineEdit()
        self.audio_path.setPlaceholderText('Audio path...')

        self.select_audio_btn = QPushButton()
        self.select_audio_btn.setText('Select file')
        self.select_audio_btn.released.connect(self.open_path)

        hbox_input = QHBoxLayout()
        hbox_input.addWidget(self.audio_path)
        hbox_input.addWidget(self.select_audio_btn)
        return hbox_input

    def open_path(self):
        path_to_audio, _ = QFileDialog.getOpenFileName(self, self.tr('Load audio'), self.tr('~/'), self.tr('Audio file (*.*)'))
        self.audio_path.setText(path_to_audio)

    def output(self):
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText('Ouput path...')

        self.select_output_btn = QPushButton()
        self.select_output_btn.setText('Select file')
        self.select_output_btn.released.connect(self.set_output_path)

        hbox_output = QHBoxLayout()
        hbox_output.addWidget(self.output_path)
        hbox_output.addWidget(self.select_output_btn)
        return hbox_output

    def set_output_path(self):
        output_dir = QFileDialog.getExistingDirectory(self, self.tr('Select output directory'), self.tr('~/'))
        self.output_path.setText(output_dir)

    def custom(self):
        self.semitones = QLineEdit()
        self.semitones.setPlaceholderText('Semitones: +1, -1, +1.5, ...')

        self.yes = QRadioButton('Yes')
        self.no = QRadioButton('No')
        self.no.setChecked(True)

        hbox = QHBoxLayout()
        hbox.addWidget(self.yes)
        hbox.addWidget(self.no)
        group = QButtonGroup()
        group.addButton(self.yes)
        group.addButton(self.no)

        self.format = QComboBox()
        self.format.addItem('')
        self.format.addItem('flac')
        self.format.addItem('mp3')
        self.format.addItem('m4a')
        self.format.addItem('wav')
        self.format.addItem('webm')

        self.run_btn = QPushButton()
        self.run_btn.setText('Go')
        self.run_btn.released.connect(self._main)

        grid = QGridLayout()
        grid.addWidget(QLabel('Change pitch'), 0, 0)
        grid.addWidget(self.semitones, 1, 0)
        grid.addWidget(QLabel('Split'), 0, 1)
        grid.addLayout(hbox, 1, 1)
        grid.addWidget(QLabel('Output format'), 0, 2)
        grid.addWidget(self.format, 1, 2)
        grid.addWidget(self.run_btn, 2, 1)

        return grid

    def _main(self):
        if not self.audio_path.text() or not self.output_path.text() or not self.format.currentText():
            return
        try:
            semitones = float(self.semitones.text()) if self.semitones.text() else 0
        except Exception as e:
            semitones = 0
            log.exception('%s(%s)', type(e).__name__, e)
        split = True if self.yes.isChecked() else False
        main(self.audio_path.text(), semitones, split, self.format.currentText(), self.output_path.text())

    def tr(self, text):
        return QObject.tr(self, text)


if __name__ == '__main__':
    args = parse_args()

    log_util.configure_logging(__package__, logging.DEBUG if args.debug else None)

    app = QApplication(sys.argv)
    gui = Gui('Song Modifier')
    gui.show()

    sys.exit(app.exec_())
