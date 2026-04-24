# sqlite_setup.py
import sqlite3

def crear_bd():
    conn = sqlite3.connect('tienda.db')
    cursor = conn.cursor()

    # Tablas
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY, nombre TEXT, email TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS compras (id INTEGER PRIMARY KEY, cliente_id INTEGER, producto_id INTEGER, fecha TEXT)''')

    # Datos Dummy
    cursor.executemany('INSERT INTO clientes (nombre, email) VALUES (?, ?)', 
                       [('Ana Garcia', 'ana@email.com'), ('Luis Perez', 'luis@email.com')])
    cursor.executemany('INSERT INTO productos (nombre, precio) VALUES (?, ?)', 
                       [('Cuaderno', 2500.50), ('Mochila', 15000.00)])
    cursor.executemany('INSERT INTO compras (cliente_id, producto_id, fecha) VALUES (?, ?, ?)', 
                       [(1, 1, '2026-03-25'), (1, 2, '2026-03-26'), (2, 1, '2026-03-28')])

    conn.commit()
    conn.close()
    print("Base de datos 'tienda.db' creada exitosamente.")

if __name__ == "__main__":
    crear_bd()