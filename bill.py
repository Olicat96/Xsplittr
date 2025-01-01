from database import Database

class BillManager:
    SPLIT_METHODS = ["Equal", "Percentage"]

    def __init__(self):
        self.db = Database()

    def add_bill(self, group_name, title, amount, date, split_method, percentages=None, paid_by=None):
        group_id = self.get_group_id(group_name)
        if not group_id:
            raise ValueError(f"Group '{group_name}' does not exist.")

        if not paid_by:
            raise ValueError("A payer must be specified for the bill.")
        if not self.db.fetch_one("SELECT id FROM participants WHERE id = ? AND group_id = ?", (paid_by, group_id)):
            raise ValueError(f"Payer ID {paid_by} is not valid or not part of the group '{group_name}'.")

        query = """
            INSERT INTO bills (title, amount, date, split_method, group_id, paid_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        bill_id = self.db.execute_query(query, (title, amount, date, split_method, group_id, paid_by)).lastrowid

        participants = self.db.fetch_all("SELECT id FROM participants WHERE group_id = ?", (group_id,))
        if not participants:
            raise ValueError("Cannot add a bill to a group with no participants.")

        if split_method.lower() == "percentage" and percentages:
            for participant_name, percentage in percentages:
                participant_id = self.db.fetch_one("""
                    SELECT id FROM participants WHERE nickname = ?
                """, (participant_name,))[0]

                owed_amount = self.round_to_nearest_five_cents(amount * (percentage / 100))

                self.db.execute_query("""
                    INSERT INTO bill_splits (bill_id, participant_id, amount)
                    VALUES (?, ?, ?)
                """, (bill_id, participant_id, owed_amount))

        elif split_method.lower() == "equal":
            per_person_amount = self.round_to_nearest_five_cents(amount / len(participants))

            for participant in participants:
                participant_id = participant[0]
                self.db.execute_query("""
                    INSERT INTO bill_splits (bill_id, participant_id, amount)
                    VALUES (?, ?, ?)
                """, (bill_id, participant_id, per_person_amount))

        else:
            raise ValueError("Unsupported split method or missing percentage data.")

    def get_recent_bills(self):
        query = """
            SELECT b.title, b.amount, b.date, b.split_method, g.name
            FROM bills b
            JOIN groups g ON b.group_id = g.id
            ORDER BY b.id DESC
            LIMIT 5
        """
        return self.db.fetch_all(query)

    @staticmethod
    def round_to_nearest_five_cents(amount):
        return round(amount * 20) / 20

    def remove_bill(self, bill_id):
        self.db.execute_query("DELETE FROM bill_splits WHERE bill_id = ?", (bill_id,))

        query = """
            DELETE FROM bills 
            WHERE id = ?
        """
        self.db.execute_query(query, (bill_id,))

    def get_group_id(self, group_name):
        query = "SELECT id FROM groups WHERE name = ?"
        result = self.db.fetch_one(query, (group_name,))
        return result[0] if result else None
