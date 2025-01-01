import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QWidget,
    QMessageBox, QDialog, QTableWidget, QTableWidgetItem, QListWidgetItem, QComboBox, QDoubleSpinBox, QButtonGroup, QRadioButton
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

        if not first_name or not last_name or not nickname:
            QMessageBox.warning(self, "Error", "First name, last name, and nickname are required.")
            return

        try:
            self.participant_manager.add_participant(self.group_name, first_name, last_name, nickname)
            QMessageBox.information(self, "Success",
                                    f"Participant '{first_name} {last_name}' with nickname '{nickname}' added.")
            self.participant_first_name_input.clear()
            self.participant_last_name_input.clear()
            self.participant_nickname_input.clear()
            self.update_participant_list()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Duplicate Nickname",
                                "The nickname you entered already exists. Please use a different nickname.")
        except Exception as e:
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

        participant_display = selected_participant.text()
        _, _, nickname = participant_display.rpartition('(')
        nickname = nickname.rstrip(')')

        confirm = QMessageBox.question(self, "Confirm",
                                       f"Are you sure you want to delete the participant with nickname '{nickname}'?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm == QMessageBox.Yes:
            try:
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
        self.setup_bill_section()

        finish_trip_btn = QPushButton("Finish Trip")
        finish_trip_btn.clicked.connect(self.finish_trip)
        self.layout.addWidget(finish_trip_btn)

        done_button = QPushButton("Done")
        done_button.clicked.connect(self.close)
        self.layout.addWidget(done_button)

        self.setLayout(self.layout)
        self.update_bill_table()

    def finish_trip(self):
        pass  # Implementation of finish_trip

    def setup_bill_section(self):
        # Label for the section
        bill_label = QLabel("Add a New Bill")
        self.layout.addWidget(bill_label)

        # Input layout for title, amount, date, and split method
        bill_input_layout = QHBoxLayout()
        self.bill_title_input = QLineEdit()
        self.bill_title_input.setPlaceholderText("Bill Title")
        self.bill_amount_input = QLineEdit()
        self.bill_amount_input.setPlaceholderText("Amount")
        self.bill_date_input = QLineEdit()
        self.bill_date_input.setPlaceholderText("Date (YYYY-MM-DD)")

        self.split_method_dropdown = QComboBox()
        self.split_method_dropdown.addItems(BillManager.SPLIT_METHODS)
        self.split_method_dropdown.currentTextChanged.connect(self.toggle_percentage_input)

        add_bill_btn = QPushButton("Add Bill")
        add_bill_btn.clicked.connect(self.add_bill)

        bill_input_layout.addWidget(self.bill_title_input)
        bill_input_layout.addWidget(self.bill_amount_input)
        bill_input_layout.addWidget(self.bill_date_input)
        bill_input_layout.addWidget(self.split_method_dropdown)
        bill_input_layout.addWidget(add_bill_btn)

        # Add bill input layout to the main layout
        self.layout.addLayout(bill_input_layout)

        # Dynamic Percentage Input Section (Added below the bill input fields)
        self.percentage_input_widget = QWidget()
        self.percentage_input_layout = QVBoxLayout(self.percentage_input_widget)

        self.percentage_inputs = []

        participants = self.bill_manager.db.fetch_all("""
            SELECT nickname as participant_name
            FROM participants
            WHERE group_id = (SELECT id FROM groups WHERE name = ?)
        """, (self.group_name,))

        for participant in participants:
            nickname = participant[0]
            row_layout = QHBoxLayout()
            # Add label for nickname
            label = QLabel(f"{nickname}:")
            label.setFixedWidth(100)  # Align all labels neatly
            row_layout.addWidget(label)

            # Add percentage input field
            input_field = QDoubleSpinBox()
            input_field.setSuffix("%")
            input_field.setRange(0, 100)
            input_field.setDecimals(2)
            input_field.setSingleStep(1.0)
            self.percentage_inputs.append((nickname, input_field))
            row_layout.addWidget(input_field)

            # Align and compact the layout
            row_layout.setSpacing(20)  # Reduce spacing between label and input
            row_layout.setContentsMargins(0, 0, 0, 0)  # Remove unnecessary margins

            # Add the row layout to the main percentage input layout
            self.percentage_input_layout.addLayout(row_layout)

        # Add percentage input widget directly below the bill input layout
        self.layout.addWidget(self.percentage_input_widget)
        self.percentage_input_widget.setVisible(False)  # Hidden by default

        # Table layout for displaying bills
        table_layout = QVBoxLayout()
        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(6)
        self.bills_table.setHorizontalHeaderLabels(
            ["Title", "Amount", "Date", "Split Method", "Group", "Split Details"]
        )
        table_layout.addWidget(self.bills_table)

        delete_bill_btn = QPushButton("Delete Bill")
        delete_bill_btn.clicked.connect(self.remove_bill)
        table_layout.addWidget(delete_bill_btn)

        # Add the table layout to the main layout
        self.layout.addLayout(table_layout)

    def toggle_percentage_input(self, method):
        if method.lower() == "percentage":
            self.percentage_input_widget.setVisible(True)
        else:
            self.percentage_input_widget.setVisible(False)

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
            percentages = None

            payer_id = self.select_payer()
            if payer_id is None:
                QMessageBox.warning(self, "Error", "No payer selected.")
                return

            if split_method.lower() == "percentage":
                percentages = []
                for nickname, input_field in self.percentage_inputs:
                    percentage = input_field.value()
                    percentages.append((nickname, percentage))

                total_percentage = sum(p[1] for p in percentages)
                if abs(total_percentage - 100) > 0.01:
                    QMessageBox.warning(self, "Error", "Percentages must total 100%.")
                    return

                payer_id = self.select_payer()  # Added call to select payer
                if payer_id is None:  # Ensure payer is selected
                    QMessageBox.warning(self, "Error", "No payer selected.")
                    return

            self.bill_manager.add_bill(self.group_name, title, amount, date, split_method, percentages, payer_id)

            QMessageBox.information(self, "Success", f"Bill '{title}' added.")

            self.bill_title_input.clear()
            self.bill_amount_input.clear()
            self.bill_date_input.clear()

            # Reset percentage inputs (if visible)
            if split_method.lower() == "percentage":
                for _, input_field in self.percentage_inputs:
                    input_field.setValue(0.0)

            self.update_bill_table()

        except ValueError:
            QMessageBox.critical(self, "Error", "Amount must be a valid number.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def select_payer(self):
        dialog = PayerSelectionDialog(self.group_name)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.selected_payer
        return None

    def update_bill_table(self):
        try:
            self.bills_table.setRowCount(0)  # Clear the table

            # Fetch all bills for the group
            bills = self.bill_manager.db.fetch_all("""
                SELECT b.id, b.title, b.amount, b.date, b.split_method, g.name
                FROM bills b
                JOIN groups g ON b.group_id = g.id
                WHERE g.name = ?
            """, (self.group_name,))

            self.bill_ids = []  # Backend storage for bill IDs

            for row, bill in enumerate(bills):
                bill_id, title, amount, date, split_method, group_name = bill

                # Store bill_id for backend use
                self.bill_ids.append(bill_id)

                # Populate the table
                self.bills_table.insertRow(row)
                self.bills_table.setItem(row, 0, QTableWidgetItem(title))
                self.bills_table.setItem(row, 1, QTableWidgetItem(str(amount)))
                self.bills_table.setItem(row, 2, QTableWidgetItem(date))
                self.bills_table.setItem(row, 3, QTableWidgetItem(split_method))
                self.bills_table.setItem(row, 4, QTableWidgetItem(group_name))

                # Add split details column
                contributions = self.bill_manager.db.fetch_all("""
                    SELECT p.nickname, bp.amount
                    FROM bill_splits bp
                    JOIN participants p ON bp.participant_id = p.id
                    WHERE bp.bill_id = ?
                """, (bill_id,))

                if split_method.lower() == "equal":
                    split_details = f"Each owes: {contributions[0][1]:.2f}" if contributions else "No participants"
                elif split_method.lower() == "percentage":
                    split_details = ", ".join(
                        [f"{participant} owes: {amount:.2f}" for participant, amount in contributions]
                    )
                else:
                    split_details = "Custom or unsupported split method"

                self.bills_table.setItem(row, 5, QTableWidgetItem(split_details))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while updating the table: {e}")

    def remove_bill(self):
        selected_row = self.bills_table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a bill to delete.")
            return

        bill_id = self.bill_ids[selected_row]

        try:
            confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to delete this bill?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if confirm == QMessageBox.Yes:
                self.bill_manager.remove_bill(bill_id)
                QMessageBox.information(self, "Success", f"Bill has been deleted.")
                self.update_bill_table()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class PayerSelectionDialog(QDialog):
    def __init__(self, group_name):
        super().__init__()
        self.setWindowTitle("Select Payer")
        self.setGeometry(1700, 800, 400, 300)

        self.group_name = group_name
        self.bill_manager = BillManager()
        self.selected_payer = None

        self.layout = QVBoxLayout()

        # Fetch participants for the group
        participants = self.bill_manager.db.fetch_all("""
            SELECT id, nickname FROM participants WHERE group_id = (SELECT id FROM groups WHERE name = ?)
        """, (self.group_name,))

        # Check if participants exist
        if not participants:
            QMessageBox.warning(self, "Error", "No participants available to select as the payer.")
            self.reject()  # Close the dialog if no participants exist
            return

        # Add radio buttons for each participant
        self.radio_group = QButtonGroup(self)
        for participant_id, nickname in participants:
            radio_button = QRadioButton(nickname)
            self.radio_group.addButton(radio_button, participant_id)
            self.layout.addWidget(radio_button)

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept_selection)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)


    def accept_selection(self):
        selected_button = self.radio_group.checkedButton()
        if selected_button:
            self.selected_payer = self.radio_group.id(selected_button)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Please select a payer.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseSplitterApp()
    window.show()
    sys.exit(app.exec_())
