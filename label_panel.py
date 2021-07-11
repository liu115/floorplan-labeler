from PyQt5.QtCore import QModelIndex, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QVBoxLayout, QListWidgetItem, QMenu, QPushButton, QWidget, QListView, QAction, QListWidget, QLabel, QHBoxLayout


class LabelPanel(QWidget):
    sig_delete_room = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.list_view = QListWidget()
        self.del_btn = QPushButton('del')
        self.del_btn.clicked.connect(self.click_delete)
        layout.addWidget(self.list_view)
        layout.addWidget(self.del_btn)

    def add_label(self, id, color):
        item = QListWidgetItem(id)
        item.setBackground(color)
        self.list_view.addItem(item)

    def click_delete(self):
        items = self.list_view.selectedItems()
        if len(items) > 0:
            id = items[0].text()
            self.sig_delete_room.emit(id)
            self.list_view.takeItem(self.list_view.row(items[0]))
            self.list_view.setCurrentIndex(QModelIndex())

    def clear(self):
        self.list_view.clear()


class LabelListItem(QStandardItem):
    def __init__(self, text=None, color=None):
        super().__init__()
        self.setText(text)
        if color is not None:
            self.setBackground(color)
        self.setSelectable(False)
        self.setEditable(False)
