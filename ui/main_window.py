# Nama  : Maulida Citra Illiyyin
# NIM   : F1D02310145
# Kelas : Pemrograman Visual C

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QInputDialog, QHeaderView, QTextEdit, QLabel, QLineEdit)
from PySide6.QtCore import QThread, Signal, Qt
from api.client import PostAPI

class LoadDataWorker(QThread):
    finished = Signal(dict)
    def run(self):
        try:
            data, code = PostAPI.get_all()
            if isinstance(data, dict):
                self.finished.emit(data)
            else:
                self.finished.emit({"data": []})
        except Exception as e:
            print(f"Worker Error: {e}")
            self.finished.emit({"data": []})

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Post Manager") 
        self.resize(1100, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        
        self.btn_refresh = QPushButton("🔄 Refresh Data")
        self.btn_refresh.clicked.connect(self.start_load_data)
        self.left_layout.addWidget(self.btn_refresh)

        self.btn_add = QPushButton("➕ Tambah Data Baru")
        self.btn_add.clicked.connect(self.add_post)
        self.left_layout.addWidget(self.btn_add)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Author", "Status"])
        self.table.setSelectionBehavior(QHeaderView.SelectRows)
        self.table.setSelectionMode(QHeaderView.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.cellClicked.connect(self.show_detail) 
        self.left_layout.addWidget(self.table)
        
        self.main_layout.addWidget(self.left_container, 2)

        self.right_container = QWidget()
        self.right_container.setFixedWidth(350)
        self.right_layout = QVBoxLayout(self.right_container)
        
        self.right_layout.addWidget(QLabel("<b>EDIT DATA</b>"))
        
        self.edit_id = QLineEdit(); self.edit_id.setReadOnly(True)
        self.edit_id.setStyleSheet("background-color: #f0f0f0;")
        self.edit_title = QLineEdit()
        self.edit_author = QLineEdit()
        self.edit_body = QTextEdit()
        
        self.right_layout.addWidget(QLabel("ID (Read-only):"))
        self.right_layout.addWidget(self.edit_id)
        self.right_layout.addWidget(QLabel("Title:"))
        self.right_layout.addWidget(self.edit_title)
        self.right_layout.addWidget(QLabel("Author:"))
        self.right_layout.addWidget(self.edit_author)
        self.right_layout.addWidget(QLabel("Body Content:"))
        self.right_layout.addWidget(self.edit_body)

        self.btn_save = QPushButton("💾 Simpan Perubahan")
        self.btn_save.clicked.connect(self.update_post)
        self.btn_save.setEnabled(False)
        self.right_layout.addWidget(self.btn_save)

        self.btn_delete = QPushButton("🗑️ Hapus Data")
        self.btn_delete.setStyleSheet("background-color: #ff4d4d; color: white; font-weight: bold;")
        self.btn_delete.clicked.connect(self.delete_post)
        self.btn_delete.setEnabled(False)
        self.right_layout.addWidget(self.btn_delete)
        
        self.right_layout.addStretch()
        self.main_layout.addWidget(self.right_container)

        self.start_load_data()

    def start_load_data(self):
        self.btn_refresh.setText("⏳ Sedang Mengambil Data...")
        self.btn_refresh.setEnabled(False) 
        self.worker = LoadDataWorker()
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.start()

    def on_data_loaded(self, response_json):
        self.btn_refresh.setEnabled(True)
        self.btn_refresh.setText("🔄 Refresh Data")
        self.btn_save.setEnabled(False)
        self.btn_delete.setEnabled(False)

        posts = response_json.get('data', [])
        
        self.table.setRowCount(0)
        for row, post in enumerate(posts):
            self.table.insertRow(row)

            id_val = str(post.get('id', ''))
            id_item = QTableWidgetItem(id_val)
            id_item.setData(Qt.UserRole, post)
            
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, QTableWidgetItem(str(post.get('title', ''))))
            self.table.setItem(row, 2, QTableWidgetItem(str(post.get('author', ''))))
            self.table.setItem(row, 3, QTableWidgetItem(str(post.get('status', ''))))
    
    def show_detail(self, row, column): 
        item = self.table.item(row, 0)
        if item:
            data = item.data(Qt.UserRole)
            if data:
                self.edit_title.blockSignals(True)
                self.edit_id.setText(str(data.get('id', '')))
                self.edit_title.setText(str(data.get('title', '')))
                self.edit_author.setText(str(data.get('author', '')))
                self.edit_body.setPlainText(str(data.get('body', '')))
                self.edit_title.blockSignals(False)
                self.btn_save.setEnabled(True)
                self.btn_delete.setEnabled(True)

    def add_post(self):
        title, ok1 = QInputDialog.getText(self, "Tambah", "Judul:")
        if not ok1 or not title.strip(): return
        author, ok2 = QInputDialog.getText(self, "Tambah", "Author:")
        if not ok2 or not author.strip(): return
        body, ok3 = QInputDialog.getMultiLineText(self, "Tambah", "Body:")
        if not ok3 or not body.strip(): return

        new_data = {"title": title, "body": body, "author": author, "slug": title.lower().replace(" ","-"), "status": "published"}
        res, code = PostAPI.create(new_data)
        if code in [200, 201]:
            QMessageBox.information(self, "Sukses", "Data Berhasil Ditambah!")
            self.start_load_data()
        else:
            self.handle_422(res)

    def update_post(self):
        post_id = self.edit_id.text()
        if not post_id: return
        updated_data = {"title": self.edit_title.text(), "author": self.edit_author.text(), "body": self.edit_body.toPlainText(), "slug": self.edit_title.text().lower().replace(" ","-"), "status": "published"}
        res, code = PostAPI.update(post_id, updated_data)
        if code in [200, 204]:
            QMessageBox.information(self, "Sukses", "Data Berhasil Diupdate!")
            self.start_load_data() 
        else:
            self.handle_422(res)

    def delete_post(self):
        post_id = self.edit_id.text()
        if not post_id: return
        yakin = QMessageBox.question(self, "Hapus", f"Yakin hapus ID {post_id}?", QMessageBox.Yes | QMessageBox.No)
        if yakin == QMessageBox.Yes:
            code = PostAPI.delete(post_id)
            if code in [200, 204]:
                QMessageBox.information(self, "Sukses", "Data Terhapus!")
                self.start_load_data()

    def handle_422(self, res):
        msg = res.get('message', 'Terjadi kesalahan')
        errors = res.get('errors', {})
        detail = "".join([f"- {k}: {', '.join(v)}\n" for k, v in errors.items()])
        QMessageBox.warning(self, "Info", f"{msg}\n{detail}")
