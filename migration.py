import sqlite3

# Conectar a la base de datos existente
conn = sqlite3.connect("bot.db")
cursor = conn.cursor()
cursor.execute("UPDATE users SET inventory = '[]'")

try:
    # Esta es la instrucción mágica.
    # Añade la columna 'inventory' de tipo TEXT.
    # DEFAULT '[]' es CRUCIAL: hace que todos los usuarios que ya existen
    # tengan automáticamente una lista vacía en lugar de NULL/Nada.
    cursor.execute("ALTER TABLE users ADD COLUMN inventory TEXT DEFAULT '[]'")

    print("✅ Columna 'inventory' añadida con éxito.")
    conn.commit()

except sqlite3.OperationalError as e:
    # Este error salta si la columna ya existe (por si ejecutas el script dos veces)
    print(f"⚠️ Aviso: {e}. Probablemente la columna ya existía.")

except Exception as e:
    print(f"❌ Error inesperado: {e}")

finally:
    conn.close()
