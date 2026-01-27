import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER NOT NULL DEFAULT 0
    );"""
)
conn.commit()


def getUser(userID):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (userID,))
    row = cursor.fetchone()

    if row is None:
        cursor.execute("INSERT INTO users(user_id) VALUES(?)", (userID,))
        conn.commit()
        return {"balance": 0}
    return {"balance": row[0]}


def updateUser(userID, balance=None):
    if balance is not None:
        cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (balance, userID))
    conn.commit()


def getLeaderboard():
    cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    rows = cursor.fetchall()

    leaderboard = [{"user_id": row[0], "balance": row[1]} for row in rows]

    return leaderboard


def getAllUsers():
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    users_list = []
    for row in rows:
        # zip une ('user_id', 123) y ('balance', 50), dict lo convierte a diccionario
        user_dict = dict(zip(column_names, row))
        users_list.append(user_dict)

    return users_list
