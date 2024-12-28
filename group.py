from database import Database

class GroupManager:
    def __init__(self):
        self.db = Database()

    def create_group(self, name):
        query = "INSERT INTO groups (name) VALUES (?)"
        self.db.execute_query(query, (name,))

    def delete_group(self, name):
        query = "DELETE FROM groups WHERE name = ?"
        self.db.execute_query(query, (name,))

    def list_groups(self):
        query = "SELECT id, name FROM groups"
        return self.db.fetch_all(query)
