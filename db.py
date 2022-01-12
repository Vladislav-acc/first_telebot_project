import sqlite3


class BotDatabaseConn:
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.conn = sqlite3.connect(self.filename, check_same_thread=False)
        return self.conn

    def __exit__(self, type, value, tb):
        self.conn.close()


class BotDatabase:

    def __init__(self, filename):
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_database(self):

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER UNIQUE,
            name TEXT,
            email TEXT,
            address TEXT)
            """)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS devices(
            id INTEGER PRIMARY KEY,
            device_id TEXT UNIQUE,
            name TEXT)
            """)
        first_dev = self.cursor.execute("""SELECT * FROM devices""")
        if first_dev.fetchone() is None:
            self.cursor.execute("""INSERT INTO devices(device_id, name) VALUES (?, ?)""",
                                ('001-RAT', 'RAT'))
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY,
            player_id REFERENCES players(id),
            device_id REFERENCES devices(id))
            """)
        self.conn.commit()

    def something_to_test(self):

        self.cursor.execute("""INSERT INTO players (chat_id, name, email, address) VALUES (?, ?, ?, ?)""",
                            (126, 'Vlad', 'vlad@mail.ru', 'MSK'))
        self.cursor.execute("""INSERT INTO orders (player_id, device_id) VALUES (?, ?)""",
                            (1, 1))
        info = self.cursor.execute("""SELECT * FROM orders""")
        print(info.fetchall())
        info = self.cursor.execute("""SELECT * FROM players""")
        print(info.fetchall())
        info = self.cursor.execute("""SELECT * FROM devices""")
        print(info.fetchall())

    def insert_into_db(self, chat_id, name, email, address, device):
        self.cursor.execute("""INSERT INTO players (chat_id, name, email, address) VALUES (?, ?, ?, ?)""",
                            (chat_id, name, email, address))
        player_id = self.cursor.execute(f"""SELECT id FROM players WHERE chat_id = {chat_id}""").fetchone()[0]
        device_id = self.cursor.execute(f"""SELECT id FROM devices WHERE name = '{device}'""").fetchone()[0]
        self.cursor.execute("""INSERT INTO orders (player_id, device_id) VALUES (?, ?)""",
                            (player_id, device_id))
        self.conn.commit()

    def find_user(self, chat_id):
        user = self.cursor.execute(f"""SELECT name, email, address FROM players WHERE chat_id = {chat_id}""").fetchone()
        return user

    def update_user(self, chat_id, name, email, address, device):
        self.cursor.execute("""UPDATE players SET name = ?, email = ?, address = ? WHERE chat_id = ?""",
                            (name, email, address, chat_id))
        player_id = self.cursor.execute(f"""SELECT id FROM players WHERE chat_id = {chat_id}""").fetchone()[0]
        device_id = self.cursor.execute(f"""SELECT id FROM devices WHERE name = '{device}'""").fetchone()[0]
        self.cursor.execute("""INSERT INTO orders (player_id, device_id) VALUES (?, ?)""",
                            (player_id, device_id))
        self.conn.commit()

    def device_list(self):
        devices = self.cursor.execute(
            """SELECT name FROM devices""").fetchall()
        return devices

    def close_db(self):
        self.conn.close()
