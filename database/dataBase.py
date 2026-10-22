import json
import sqlite3


def getUser(userID):

    conn = sqlite3.connect("bot.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, inventory FROM users WHERE user_id=?", (userID,))
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            "INSERT INTO users(user_id, balance, inventory) VALUES(?,?,?)",
            (userID, 0, "[]"),
        )
        conn.commit()
        conn.close()
        return {"balance": 0, "inventory": []}
    balance = row[0]
    inventoryText = row[1]

    try:
        inventoryLIST = json.loads(inventoryText)
    except:
        conn.close()
        inventoryLIST = []
    conn.close()
    return {"balance": balance, "inventory": inventoryLIST}


def updateUser(userID, balance=None):

    conn = sqlite3.connect("bot.db", check_same_thread=False)
    cursor = conn.cursor()
    if balance is not None:
        cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (balance, userID))
    conn.commit()
    conn.close()


def updateInventory(userID, inventoryLIST):
    conn = sqlite3.connect("bot.db", check_same_thread=False)
    cursor = conn.cursor()
    if inventoryLIST is not None:
        inventoryJSON = json.dumps(inventoryLIST)
        cursor.execute(
            "UPDATE users SET inventory=? WHERE user_id=?", (inventoryJSON, userID)
        )
        conn.commit()
    conn.close()


def getLeaderboard():
    conn = sqlite3.connect("bot.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    rows = cursor.fetchall()

    leaderboard = [{"user_id": row[0], "balance": row[1]} for row in rows]
    conn.close()
    return leaderboard


def getAllUsers():
    conn = sqlite3.connect("bot.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    users_list = []
    for row in rows:
        # zip une ('user_id', 123) y ('balance', 50), dict lo convierte a diccionario
        user_dict = dict(zip(column_names, row))
        users_list.append(user_dict)
    conn.close()
    return users_list
