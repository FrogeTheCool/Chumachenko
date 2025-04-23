import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QListWidget, QLineEdit, QPushButton,
                             QLabel, QMessageBox, QInputDialog)
from PyQt5.QtGui import QIcon
import sqlite3


class Contact:
    def __init__(self, name, phone, email=""):
        self.name = name
        self.phone = phone
        self.email = email


class PhoneBookApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhoneBook Pro")
        self.setWindowIcon(QIcon('phone_icon.ico'))
        self.setGeometry(100, 100, 600, 400)

        self.init_db()
        self.init_ui()
        self.load_contacts()

    def init_db(self):
        self.conn = sqlite3.connect('phonebook.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT
            )
        ''')
        self.conn.commit()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Искать контакты...")
        self.search_input.textChanged.connect(self.search_contacts)
        search_button = QPushButton("Искать")
        search_button.clicked.connect(self.search_contacts)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        self.contacts_list = QListWidget()
        self.contacts_list.itemDoubleClicked.connect(self.edit_contact)

        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Добавить контакт")
        add_button.clicked.connect(self.add_contact)
        edit_button = QPushButton("Отредактировать контакт")
        edit_button.clicked.connect(self.edit_selected_contact)
        delete_button = QPushButton("Удалить контакт")
        delete_button.clicked.connect(self.delete_contact)
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)

        layout.addLayout(search_layout)
        layout.addWidget(self.contacts_list)
        layout.addLayout(buttons_layout)

        main_widget.setLayout(layout)

    def load_contacts(self, search_term=None):
        self.contacts_list.clear()
        if search_term:
            self.cursor.execute('''
                SELECT name, phone, email FROM contacts 
                WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            self.cursor.execute('SELECT name, phone, email FROM contacts')

        contacts = self.cursor.fetchall()
        for name, phone, email in contacts:
            contact_str = f"{name} - {phone}"
            if email:
                contact_str += f" ({email})"
            self.contacts_list.addItem(contact_str)

    def add_contact(self):
        name, ok = QInputDialog.getText(self, 'Добавить контакт', 'Имя:')
        if not ok or not name:
            return

        phone, ok = QInputDialog.getText(self, 'Добавить контакт', 'Телефон:')
        if not ok or not phone:
            return

        email, ok = QInputDialog.getText(self, 'Добавить контакт', 'Электронная почта (необязательно):')
        if not ok:
            return

        self.cursor.execute('''
            INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)
        ''', (name, phone, email))
        self.conn.commit()
        self.load_contacts()

    def edit_selected_contact(self):
        selected_item = self.contacts_list.currentItem()
        if selected_item:
            self.edit_contact(selected_item)

    def edit_contact(self, item):
        contact_data = item.text().split(" - ")
        name = contact_data[0]

        self.cursor.execute('''
            SELECT name, phone, email FROM contacts WHERE name = ?
        ''', (name,))
        contact = self.cursor.fetchone()

        if not contact:
            return

        name, phone, email = contact

        new_name, ok = QInputDialog.getText(self, 'Отредактировать контакт', 'Имя:', text=name)
        if not ok or not new_name:
            return

        new_phone, ok = QInputDialog.getText(self, 'Отредактировать контакт', 'Телефон:', text=phone)
        if not ok or not new_phone:
            return

        new_email, ok = QInputDialog.getText(self, 'Отредактировать контакт', 'Почта:', text=email if email else "")
        if not ok:
            return

        self.cursor.execute('''
            UPDATE contacts SET name = ?, phone = ?, email = ? WHERE name = ?
        ''', (new_name, new_phone, new_email, name))
        self.conn.commit()
        self.load_contacts()

    def delete_contact(self):
        selected_item = self.contacts_list.currentItem()
        if not selected_item:
            return

        contact_name = selected_item.text().split(" - ")[0]

        reply = QMessageBox.question(
            self, 'Удалить контакт',
            f'Вы уверены что хотите удалить {contact_name}?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.cursor.execute('DELETE FROM contacts WHERE name = ?', (contact_name,))
            self.conn.commit()
            self.load_contacts()

    def search_contacts(self):
        search_term = self.search_input.text()
        self.load_contacts(search_term)

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    phonebook = PhoneBookApp()
    phonebook.show()
    sys.exit(app.exec_())