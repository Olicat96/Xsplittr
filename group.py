from database import Database

class GroupManager:
    def __init__(self):
        self.db = Database()

    def create_group(self, name, split_method):
        query = "INSERT INTO groups (name, split_method) VALUES (?, ?)"
        self.db.execute_query(query, (name, split_method))

    def delete_group(self, name):
        query = "DELETE FROM groups WHERE name = ?"
        self.db.execute_query(query, (name,))

    def list_groups(self):
        query = "SELECT id, name, split_method FROM groups"
        return self.db.fetch_all(query)
