import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QWidget,
    QMessageBox, QDialog, QTableWidget, QTableWidgetItem, QListWidgetItem, QComboBox
)
from group import GroupManager
from bill import BillManager
from participant import ParticipantManager


class ExpenseSplitterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xsplittr")
        self.setGeometry(1500, 500, 800, 1000)

        # Managers
        self.group_manager = GroupManager()
        self.bill_manager = BillManager()

        # Main Layout
        self.main_layout = QVBoxLayout()

        # Group Management
        self.setup_group_section()

        # Group List Display
        self.group_list_widget = QListWidget()
        self.main_layout.addWidget(self.group_list_widget)

        # Add Delete Group Button
        delete_group_button = QPushButton("Delete Group")
        delete_group_button.clicked.connect(self.delete_group)
        self.main_layout.addWidget(delete_group_button)

        # Close App Button
        close_app_button = QPushButton("Close App")
        close_app_button.clicked.connect(self.close_application)
        self.main_layout.addWidget(close_app_button)

        # Main Widget
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        self.update_group_list()

    def setup_group_section(self):
        group_layout = QVBoxLayout()

        group_label = QLabel("Groups")
        group_layout.addWidget(group_label)

        create_group_layout = QHBoxLayout()
        self.group_name_input = QLineEdit()
        self.group_name_input.setPlaceholderText("Enter New Group Name")
        create_group_btn = QPushButton("Create Group")
        create_group_btn.clicked.connect(self.create_group)
        create_group_layout.addWidget(self.group_name_input)
        create_group_layout.addWidget(create_group_btn)

        group_layout.addLayout(create_group_layout)

        self.main_layout.addLayout(group_layout)

    def create_group(self):
        group_name = self.group_name_input.text()

        if not group_name:
            QMessageBox.warning(self, "Error", "Group name cannot be empty.")
            return

        try:
            self.group_manager.create_group(group_name)
            QMessageBox.information(self, "Success", f"Group '{group_name}' created.")
            self.group_name_input.clear()
            self.update_group_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_group_list(self):
        try:
            groups = self.group_manager.list_groups()
            self.group_list_widget.clear()

            for group in groups:
                group_name = group[1]
                item = f"{group_name} (Double-click to manage)"
                list_item = QListWidgetItem(item)
                list_item.setData(0, group_name)
                self.group_list_widget.addItem(list_item)

            self.group_list_widget.itemDoubleClicked.connect(self.open_group_management_window)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_group_management_window(self, item):
        """Open a new window to manage participants for the selected group."""
        group_name = item.data(0)
        group_window = GroupManagementWindow(group_name)
        group_window.exec_()

    def close_application(self):
        """Close the entire application."""
        self.close()

    def delete_group(self):
        """Delete the selected group from the list."""
        selected_group = self.group_list_widget.currentItem()

        if selected_group is None:
            QMessageBox.warning(self, "Error", "Please select a group to delete.")
            return

        group_name = selected_group.data(0)
        confirm = QMessageBox.question(self, "Confirm", f"Are you sure you want to delete the group '{group_name}'?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            try:
                self.group_manager.delete_group(group_name)
                QMessageBox.information(self, "Success", f"Group '{group_name}' deleted.")
                self.update_group_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


class GroupManagementWindow(QDialog):
    def __init__(self, group_name):
        super().__init__()
        self.setWindowTitle(f"Manage Group: {group_name}")
        self.setGeometry(1500, 500, 800, 1000)

        self.group_name = group_name
        self.group_manager = GroupManager()
        self.bill_manager = BillManager()
        self.participant_manager = ParticipantManager()

        self.layout = QVBoxLayout()

        # Participant Management Section
        self.setup_participant_section()

        self.setLayout(self.layout)
        self.update_participant_list()

    def setup_participant_section(self):
        participant_label = QLabel("Add Participants to the Group")
        self.layout.addWidget(participant_label)

        participant_input_layout = QHBoxLayout()
        self.participant_first_name_input = QLineEdit()
        self.participant_first_name_input.setPlaceholderText("Enter Participant First Name")
        self.participant_last_name_input = QLineEdit()
        self.participant_last_name_input.setPlaceholderText("Enter Participant Last Name")
        self.participant_nickname_input = QLineEdit()
        self.participant_nickname_input.setPlaceholderText("Enter Unique Nickname")

        add_participant_btn = QPushButton("Add Participant")
        add_participant_btn.clicked.connect(self.add_participant)

        participant_input_layout.addWidget(self.participant_first_name_input)
        participant_input_layout.addWidget(self.participant_last_name_input)
        participant_input_layout.addWidget(self.participant_nickname_input)
        participant_input_layout.addWidget(add_participant_btn)

        self.layout.addLayout(participant_input_layout)

        # Participants List
        self.participant_list_widget = QListWidget()
        self.layout.addWidget(self.participant_list_widget)

        # Add Delete Participant Button
        self.delete_participant_button = QPushButton("Delete Participant")
        self.delete_participant_button.clicked.connect(self.delete_participant)
        self.layout.addWidget(self.delete_participant_button)

        # Add Bill Button (Initially Hidden)
        self.add_bill_button = QPushButton("Manage Bills")
        self.add_bill_button.setEnabled(False)  # Disabled initially
        self.add_bill_button.clicked.connect(self.open_bill_management_window)
        self.layout.addWidget(self.add_bill_button)

        # Done Button to close the window
        done_button = QPushButton("Done")
        done_button.clicked.connect(self.close)
        self.layout.addWidget(done_button)

    def add_participant(self):
        first_name = self.participant_first_name_input.text()
        last_name = self.participant_last_name_input.text()
        nickname = self.participant_nickname_input.text()

        # Print to debug inputs
        print(f"Adding participant with: First Name='{first_name}', Last Name='{last_name}', Nickname='{nickname}'")

        if not first_name or not last_name or not nickname:
            QMessageBox.warning(self, "Error", "First name, last name, and nickname are required.")
            return

        try:
            print("Attempting to add participant...")
            self.participant_manager.add_participant(self.group_name, first_name, last_name, nickname)
            print("Participant added successfully.")
            QMessageBox.information(self, "Success",
                                    f"Participant '{first_name} {last_name}' with nickname '{nickname}' added.")
            self.participant_first_name_input.clear()
            self.participant_last_name_input.clear()
            self.participant_nickname_input.clear()
            self.update_participant_list()
        except sqlite3.IntegrityError:
            print("IntegrityError: Duplicate nickname.")
            QMessageBox.warning(self, "Duplicate Nickname",
                                "The nickname you entered already exists. Please use a different nickname.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

    def update_participant_list(self):
        """Update the list of participants for the group."""
        try:
            participants = self.participant_manager.db.fetch_all("""
                SELECT first_name, last_name, nickname 
                FROM participants 
                WHERE group_id = (SELECT id FROM groups WHERE name = ?)
            """, (self.group_name,))

            self.participant_list_widget.clear()
            for participant in participants:
                participant_display = f"{participant[0]} {participant[1]} ({participant[2]})"  # Include nickname
                self.participant_list_widget.addItem(participant_display)

            if participants:
                self.add_bill_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_participant(self):
        """Delete a participant from the group."""
        selected_participant = self.participant_list_widget.currentItem()

        if selected_participant is None:
            QMessageBox.warning(self, "Error", "Please select a participant to delete.")
            return

        # Extract the display text and parse the nickname
        participant_display = selected_participant.text()
        _, _, nickname = participant_display.rpartition('(')  # Extract nickname from display
        nickname = nickname.rstrip(')')  # Remove trailing parenthesis

        confirm = QMessageBox.question(self, "Confirm",
                                       f"Are you sure you want to delete the participant with nickname '{nickname}'?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            try:
                # Use the nickname to delete the participant
                self.participant_manager.delete_participant(self.group_name, nickname)
                QMessageBox.information(self, "Success", f"Participant with nickname '{nickname}' deleted.")
                self.update_participant_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def open_bill_management_window(self):
        """Open a new window to manage bills for the selected group."""
        bill_window = BillManagementWindow(self.group_name)
        bill_window.exec_()


class BillManagementWindow(QDialog):
    def __init__(self, group_name):
        super().__init__()
        self.setWindowTitle(f"Manage Bills for {group_name}")
        self.setGeometry(1300, 500, 1300, 1000)

        self.group_name = group_name
        self.bill_manager = BillManager()

        self.layout = QVBoxLayout()

        # Bill Management Section
        self.setup_bill_section()

        # Add "Done" Button
        done_button = QPushButton("Done")
        done_button.clicked.connect(self.close)  # Close the window when clicked
        self.layout.addWidget(done_button)

        self.setLayout(self.layout)

        self.update_bill_table()

    def setup_bill_section(self):
        bill_label = QLabel("Add a New Bill")
        self.layout.addWidget(bill_label)

        bill_input_layout = QHBoxLayout()
        self.bill_title_input = QLineEdit()
        self.bill_title_input.setPlaceholderText("Bill Title")
        self.bill_amount_input = QLineEdit()
        self.bill_amount_input.setPlaceholderText("Amount")
        self.bill_date_input = QLineEdit()
        self.bill_date_input.setPlaceholderText("Date (YYYY-MM-DD)")

        self.split_method_dropdown = QComboBox()
        self.split_method_dropdown.addItems(BillManager.SPLIT_METHODS)

        add_bill_btn = QPushButton("Add Bill")
        add_bill_btn.clicked.connect(self.add_bill)

        bill_input_layout.addWidget(self.bill_title_input)
        bill_input_layout.addWidget(self.bill_amount_input)
        bill_input_layout.addWidget(self.bill_date_input)
        bill_input_layout.addWidget(self.split_method_dropdown)
        bill_input_layout.addWidget(add_bill_btn)

        self.layout.addLayout(bill_input_layout)

        # Bills Table Section
        table_layout = QVBoxLayout()
        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(5)
        self.bills_table.setHorizontalHeaderLabels(["Title", "Amount", "Date", "Split Method", "Group"])
        table_layout.addWidget(self.bills_table)

        delete_bill_btn = QPushButton("Delete")
        delete_bill_btn.clicked.connect(self.remove_bill)
        table_layout.addWidget(delete_bill_btn)

        self.layout.addLayout(table_layout)

    def add_bill(self):
        title = self.bill_title_input.text()
        amount = self.bill_amount_input.text()
        date = self.bill_date_input.text()
        split_method = self.split_method_dropdown.currentText()

        if not title or not amount or not date:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        try:
            amount = float(amount)

            self.bill_manager.add_bill(self.group_name, title, amount, date, split_method)

            QMessageBox.information(self, "Success", f"Bill '{title}' added.")

            # Clear input fields after adding the bill
            self.bill_title_input.clear()
            self.bill_amount_input.clear()
            self.bill_date_input.clear()

            # Update the bill table to reflect the new data
            self.update_bill_table()

        except ValueError:
            QMessageBox.critical(self, "Error", "Amount must be a valid number.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def update_bill_table(self):
        try:
            bills = self.bill_manager.db.fetch_all("""
                SELECT b.title, b.amount, b.date, b.split_method, g.name AS group_name, b.id
                FROM bills b
                JOIN groups g ON b.group_id = g.id
                WHERE g.name = ?
            """, (self.group_name,))

            self.bills_table.setRowCount(len(bills))

            for row, bill in enumerate(bills):
                for col, value in enumerate(bill[:-1]):
                    self.bills_table.setItem(row, col, QTableWidgetItem(str(value)))

                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda checked, bill_id=bill[-1]: self.remove_bill(title()))
                self.bills_table.setCellWidget(row, 5, delete_button)


        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def remove_bill(self):
        selected_row = self.bills_table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a bill to delete.")
            return

        title = self.bills_table.item(selected_row, 0).text()

        try:
            confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to delete this bill?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if confirm == QMessageBox.Yes:
                self.bill_manager.remove_bill(self.group_name, title)

                QMessageBox.information(self, "Success", f"Bill '{title}' has been deleted.")
                self.update_bill_table()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseSplitterApp()
    window.show()
    sys.exit(app.exec_())
