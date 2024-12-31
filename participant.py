from database import Database

class ParticipantManager:
    def __init__(self):
        self.db = Database()

    def add_participant(self, group_name, first_name, last_name, nickname):
        group_id = self.get_group_id(group_name)
        if not group_id:
            raise ValueError(f"Group '{group_name}' does not exist.")
        query = """
            INSERT INTO participants (first_name, last_name, nickname, group_id)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_query(query, (first_name, last_name, nickname, group_id))

    def delete_participant(self, group_name, nickname):
        group_id = self.get_group_id(group_name)
        if not group_id:
            raise ValueError(f"Group '{group_name}' does not exist.")
        query = """
            DELETE FROM participants 
            WHERE nickname = ? AND group_id = ?
        """
        self.db.execute_query(query, (nickname, group_id))

    def get_group_id(self, group_name):
        query = "SELECT id FROM groups WHERE name = ?"
        result = self.db.fetch_one(query, (group_name,))
        return result[0] if result else None
