from database import Database

class BillManager:
    SPLIT_METHODS = ["equal", "percentage", "custom"]

    def __init__(self):
        self.db = Database()

    def add_bill(self, group_name, title, amount, date, split_method):
        group_id = self.get_group_id(group_name)
        if not group_id:
            raise ValueError(f"Group '{group_name}' does not exist.")
        query = """
            INSERT INTO bills (title, amount, date, split_method, group_id)
            VALUES (?, ?, ?, ?, ?)
        """
        self.db.execute_query(query, (title, amount, date, split_method, group_id))

    def get_recent_bills(self):
        query = """
            SELECT b.title, b.amount, b.date, b.split_method, g.name
            FROM bills b
            JOIN groups g ON b.group_id = g.id
            ORDER BY b.id DESC
            LIMIT 5
        """
        return self.db.fetch_all(query)

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
