from sqlalchemy import text
from database import engine

def add_observaciones_column():
    print("Intentando añadir la columna 'observaciones' a la tabla 'items_pedido'...")
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE items_pedido ADD COLUMN IF NOT EXISTS observaciones TEXT;"))
            conn.commit()
        print("¡Éxito! Columna añadida correctamente.")
    except Exception as e:
        print(f"Error al añadir la columna: {e}")

if __name__ == "__main__":
    add_observaciones_column()
