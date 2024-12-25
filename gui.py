import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QWidget,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from group import GroupManager
from participant import ParticipantManager
from bill import BillManager


class ExpenseSplitterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xsplittr")
        self.setGeometry(100, 100, 800, 600)

        # Managers
        self.group_manager = GroupManager()
        self.participant_manager = ParticipantManager()
        self.bill_manager = BillManager()

        # Main Layout
        self.main_layout = QVBoxLayout()

        # Group Management
        self.setup_group_section()

        # Participant Management
        self.setup_participant_section()

        # Bill Management
        self.setup_bill_section()

        # Recent Bills Viewer
        self.setup_recent_bills_section()

        # Main Widget
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # Update dropdowns
        self.update_group_dropdowns()

    def setup_group_section(self):
        group_layout = QVBoxLayout()
        group_label = QLabel("Group Management")
        group_layout.addWidget(group_label)

        create_group_layout = QHBoxLayout()
        self.group_name_input = QLineEdit()
        self.group_name_input.setPlaceholderText("Group Name")
        self.split_method_combo = QComboBox()
        self.split_method_combo.addItems(["equal", "percentage"])
        create_group_btn = QPushButton("Create Group")
        create_group_btn.clicked.connect(self.create_group)
        create_group_layout.addWidget(self.group_name_input)
        create_group_layout.addWidget(self.split_method_combo)
        create_group_layout.addWidget(create_group_btn)

        group_layout.addLayout(create_group_layout)

        # Delete Group
        delete_group_layout = QHBoxLayout()
        self.delete_group_combo = QComboBox()
        delete_group_btn = QPushButton("Delete Group")
        delete_group_btn.clicked.connect(self.delete_group)
        delete_group_layout.addWidget(self.delete_group_combo)
        delete_group_layout.addWidget(delete_group_btn)

        group_layout.addLayout(delete_group_layout)
        self.main_layout.addLayout(group_layout)

    def delete_group(self):
        """Delete the selected group."""
        group_name = self.delete_group_combo.currentText()

        if not group_name:
            QMessageBox.warning(self, "Error", "No group selected.")
            return

        try:
            self.group_manager.delete_group(group_name)
            QMessageBox.information(self, "Success", f"Group '{group_name}' deleted.")
            self.update_group_dropdowns()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def create_group(self):
        group_name = self.group_name_input.text()
        split_method = self.split_method_combo.currentText()

        if not group_name:
            QMessageBox.warning(self, "Error", "Group name cannot be empty.")
            return

        try:
            self.group_manager.create_group(group_name, split_method)
            QMessageBox.information(self, "Success",
                                    f"Group '{group_name}' created with '{split_method}' split method.")
            self.group_name_input.clear()
            self.update_group_dropdowns()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def setup_participant_section(self):
        participant_layout = QVBoxLayout()
        participant_label = QLabel("Participant Management")
        participant_layout.addWidget(participant_label)

        add_participant_layout = QHBoxLayout()
        self.participant_group_combo = QComboBox()
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("First Name")
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Last Name")
        add_participant_btn = QPushButton("Add Participant")
        add_participant_btn.clicked.connect(self.add_participant)
        add_participant_layout.addWidget(self.participant_group_combo)
        add_participant_layout.addWidget(self.first_name_input)
        add_participant_layout.addWidget(self.last_name_input)
        add_participant_layout.addWidget(add_participant_btn)

        participant_layout.addLayout(add_participant_layout)
        self.main_layout.addLayout(participant_layout)

    def add_participant(self):
        group_name = self.participant_group_combo.currentText()
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()

        if not group_name or not first_name or not last_name:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        try:
            self.participant_manager.add_participant(group_name, first_name, last_name)
            QMessageBox.information(self, "Success",
                                    f"Participant '{first_name} {last_name}' added to group '{group_name}'.")
            self.first_name_input.clear()
            self.last_name_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def setup_bill_section(self):
        bill_layout = QVBoxLayout()
        bill_label = QLabel("Bill Management")
        bill_layout.addWidget(bill_label)

        add_bill_layout = QHBoxLayout()
        self.bill_group_combo = QComboBox()
        self.bill_title_input = QLineEdit()
        self.bill_title_input.setPlaceholderText("Bill Title")
        self.bill_amount_input = QLineEdit()
        self.bill_amount_input.setPlaceholderText("Amount")
        self.bill_date_input = QLineEdit()
        self.bill_date_input.setPlaceholderText("Date (YYYY-MM-DD)")
        add_bill_btn = QPushButton("Add Bill")
        add_bill_btn.clicked.connect(self.add_bill)
        add_bill_layout.addWidget(self.bill_group_combo)
        add_bill_layout.addWidget(self.bill_title_input)
        add_bill_layout.addWidget(self.bill_amount_input)
        add_bill_layout.addWidget(self.bill_date_input)
        add_bill_layout.addWidget(add_bill_btn)

        bill_layout.addLayout(add_bill_layout)
        self.main_layout.addLayout(bill_layout)

    def add_bill(self):
        group_name = self.bill_group_combo.currentText()
        title = self.bill_title_input.text()
        amount = self.bill_amount_input.text()
        date = self.bill_date_input.text()

        if not group_name or not title or not amount or not date:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        try:
            amount = float(amount)
            self.bill_manager.add_bill(group_name, title, amount, date)
            QMessageBox.information(self, "Success", f"Bill '{title}' added to group '{group_name}'.")
            self.bill_title_input.clear()
            self.bill_amount_input.clear()
            self.bill_date_input.clear()
            self.update_recent_bills_table()
        except ValueError:
            QMessageBox.critical(self, "Error", "Amount must be a number.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_group_dropdowns(self):
        """Update dropdowns for groups in Participant and Bill Management sections."""
        try:
            groups = self.group_manager.list_groups()
            group_names = [group[1] for group in groups]  # Extract names from group tuples

            # Update Participant Management
            self.participant_group_combo.clear()
            self.participant_group_combo.addItems(group_names)

            # Update Bill Management
            self.bill_group_combo.clear()
            self.bill_group_combo.addItems(group_names)

            # Update Delete Group Dropdown
            self.delete_group_combo.clear()
            self.delete_group_combo.addItems(group_names)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def setup_recent_bills_section(self):
        bills_layout = QVBoxLayout()
        bills_label = QLabel("Recent Bills")
        bills_layout.addWidget(bills_label)

        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(4)
        self.bills_table.setHorizontalHeaderLabels(["Title", "Amount", "Date", "Group"])
        bills_layout.addWidget(self.bills_table)

        self.main_layout.addLayout(bills_layout)
        self.update_recent_bills_table()

    def update_recent_bills_table(self):
        try:
            recent_bills = self.bill_manager.get_recent_bills()
            self.bills_table.setRowCount(len(recent_bills))
            for row, bill in enumerate(recent_bills):
                for col, value in enumerate(bill):
                    self.bills_table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseSplitterApp()
    window.show()
    sys.exit(app.exec_())
