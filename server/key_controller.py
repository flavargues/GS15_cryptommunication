import mysql.connector


class KeyController:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            database="gs15_cryptommunication",
            user="gs15",
            password="gs15",
            buffered=True
        )

    def get_user_public_keys(self):
        self.db.cursor().execute("select name from users;")
        test = self.db.cursor().fetchall()
        for t in test:
            print(t)


KeyController().get_user_public_keys()
