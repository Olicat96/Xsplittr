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

        try:
            self.db.execute_query("DELETE FROM bill_splits WHERE bill_id = ?", (bill_id,))
            self.db.execute_query("DELETE FROM bills WHERE id = ?", (bill_id,))
        except Exception as e:
            raise RuntimeError(f"Failed to remove bill with ID {bill_id}: {e}")

    def get_group_id(self, group_name):
        query = "SELECT id FROM groups WHERE name = ?"
        result = self.db.fetch_one(query, (group_name,))
        return result[0] if result else None

    def calculate_balances(self, group_name):
        group_id = self.get_group_id(group_name)
        if not group_id:
            raise ValueError(f"Group '{group_name}' does not exist.")

        # Fetch all participants in the group
        participants = self.db.fetch_all("""
            SELECT id, nickname FROM participants WHERE group_id = ?
        """, (group_id,))

        balances = {participant[1]: 0.0 for participant in participants}  # Initialize balances

        # Fetch all bills and their splits for the group
        bills = self.db.fetch_all("""
            SELECT id, paid_by, amount FROM bills WHERE group_id = ?
        """, (group_id,))

        for bill_id, paid_by, amount in bills:
            # Fetch splits for the bill
            splits = self.db.fetch_all("""
                SELECT participant_id, amount FROM bill_splits WHERE bill_id = ?
            """, (bill_id,))

            payer_nickname = self.db.fetch_one("""
                SELECT nickname FROM participants WHERE id = ?
            """, (paid_by,))[0]
            balances[payer_nickname] += amount

            for participant_id, owed_amount in splits:
                participant_nickname = self.db.fetch_one("""
                    SELECT nickname FROM participants WHERE id = ?
                """, (participant_id,))[0]
                balances[participant_nickname] -= owed_amount
        return balances

    def calculate_settlements(self, group_name):
        group_id = self.get_group_id(group_name)
        if not group_id:
            raise ValueError(f"Group '{group_name}' does not exist.")

        # Fetch all debts for the specific group
        debts = self.db.fetch_all("""
            SELECT p2.nickname AS payer, p1.nickname AS participant, bs.amount
            FROM bill_splits bs
            JOIN participants p1 ON p1.id = bs.participant_id
            JOIN participants p2 ON p2.id = (SELECT paid_by FROM bills WHERE id = bs.bill_id)
            WHERE bs.bill_id IN (
                SELECT id FROM bills WHERE group_id = ?
            )
        """, (group_id,))

        # Use a dictionary to calculate pairwise debts
        debt_map = {}
        for payer, participant, amount in debts:
            if payer == participant:
                continue
            if (participant, payer) in debt_map:
                existing_debt = debt_map[(participant, payer)]
                if existing_debt > amount:
                    debt_map[(participant, payer)] -= amount
                else:
                    debt_map.pop((participant, payer))
                    amount -= existing_debt
                    if amount > 0:
                        debt_map[(payer, participant)] = amount
            else:
                # Add new debt
                if (payer, participant) in debt_map:
                    debt_map[(payer, participant)] += amount
                else:
                    debt_map[(payer, participant)] = amount

        # Generate settlements
        settlements = [f"{participant} owes {payer} CHF {amount:.2f}" for (payer, participant), amount in debt_map.items()]

        return settlements

