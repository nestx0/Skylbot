import json
import sqlite3


class PlantsDatabase:
    DB_FILE = "bot.db"

    @classmethod
    def create_table(cls):
        """Crea la tabla si no existe al iniciar el bot."""
        conn = sqlite3.connect(cls.DB_FILE, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_plants (
                user_id INTEGER PRIMARY KEY,
                plants_data TEXT DEFAULT '[]'
            )
        """)
        conn.commit()
        conn.close()

    @classmethod
    def getInventory(cls, user_id: int) -> list:
        """Devuelve la lista de diccionarios lista para pasársela a inventario.load()"""
        conn = sqlite3.connect(cls.DB_FILE, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT plants_data FROM users_plants WHERE user_id=?", (user_id,)
        )
        row = cursor.fetchone()

        if row is None:
            cursor.execute(
                "INSERT INTO users_plants (user_id, plants_data) VALUES (?, ?)",
                (user_id, "[]"),
            )
            conn.commit()
            conn.close()
            return []

        plants_text = row[0]
        conn.close()

        try:
            return json.loads(plants_text)
        except json.JSONDecodeError:
            return []

    @classmethod
    def updateInventory(cls, user_id: int, inventory_list: list):
        """Recibe el inventario.toDict() y lo guarda en la base de datos."""
        conn = sqlite3.connect(cls.DB_FILE, check_same_thread=False)
        cursor = conn.cursor()

        plants_json = json.dumps(inventory_list)

        cursor.execute(
            """
            INSERT INTO users_plants (user_id, plants_data)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET plants_data=excluded.plants_data
        """,
            (user_id, plants_json),
        )

        conn.commit()
        conn.close()
