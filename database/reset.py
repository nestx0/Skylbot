import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

try:
    print("⏳ Borrando columna 'inventory'...")
    # 1. Eliminar la columna existente
    cursor.execute("ALTER TABLE users DROP COLUMN inventory")
    print("✅ Columna borrada.")

except sqlite3.OperationalError as e:
    # Si la columna no existe, dará error, pero seguimos adelante
    print(f"ℹ️ Nota: {e} (Probablemente ya estaba borrada)")

print("⏳ Creando columna 'inventory' de nuevo...")
# 2. Crear la columna de nuevo con el valor por defecto '[]'
cursor.execute("ALTER TABLE users ADD COLUMN inventory TEXT DEFAULT '[]'")

conn.commit()
conn.close()

print("✨ ¡Listo! La columna inventory ha sido reiniciada desde cero.")
