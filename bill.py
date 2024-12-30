from database import Database

class BillManager:
    SPLIT_METHODS = ["Equal", "Percentage", "Custom"]

    def __init__(self):
        self.db = Database()

    def add_bill(self, group_name, title, amount, date, split_method, percentages=None):
        # Get the group ID
        group_id = self.get_group_id(group_name)
        if not group_id:
            raise ValueError(f"Group '{group_name}' does not exist.")

        # Insert the bill into the database
        query = """
            INSERT INTO bills (title, amount, date, split_method, group_id)
            VALUES (?, ?, ?, ?, ?)
        """
        bill_id = self.db.execute_query(query, (title, amount, date, split_method, group_id)).lastrowid

        # Fetch participants for the group
        participants = self.db.fetch_all("SELECT id FROM participants WHERE group_id = ?", (group_id,))
        if not participants:
            raise ValueError("Cannot add a bill to a group with no participants.")

        # Handle percentage split
        if split_method.lower() == "percentage" and percentages:
            for participant_name, percentage in percentages:
                # Get participant ID by their full name
                participant_id = self.db.fetch_one("""
                    SELECT id FROM participants WHERE first_name || ' ' || last_name = ?
                """, (participant_name,))[0]

                # Calculate the owed amount based on percentage
                owed_amount = self.round_to_nearest_five_cents(amount * (percentage / 100))

                # Insert the split into bill_participants table
                self.db.execute_query("""
                    INSERT INTO bill_participants (bill_id, participant_id, amount)
                    VALUES (?, ?, ?)
                """, (bill_id, participant_id, owed_amount))

        # Handle equal split
        elif split_method.lower() == "equal":
            # Calculate equal split amount
            per_person_amount = self.round_to_nearest_five_cents(amount / len(participants))

            # Insert equal split into bill_participants table
            for participant in participants:
                participant_id = participant[0]
                self.db.execute_query("""
                    INSERT INTO bill_participants (bill_id, participant_id, amount)
                    VALUES (?, ?, ?)
                """, (bill_id, participant_id, per_person_amount))

        # Raise error for unsupported split methods
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

    def remove_bill(self, group_name, title):
        group_id = self.get_group_id(group_name)
        if not group_id:
            raise ValueError(f"Group '{group_name}' does not exist.")
        query = """
            DELETE FROM bills 
            WHERE title = ? AND group_id = ?
        """
        self.db.execute_query(query, (title, group_id))

    def get_group_id(self, group_name):
        query = "SELECT id FROM groups WHERE name = ?"
        result = self.db.fetch_one(query, (group_name,))
        return result[0] if result else None
