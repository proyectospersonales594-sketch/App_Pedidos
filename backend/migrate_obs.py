import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrate():
    url = os.getenv("DATABASE_URL")
    print(f"Conectando a la base de datos...")
    try:
        conn = psycopg2.connect(url)
        conn.autocommit = True
        cur = conn.cursor()
        print("Ejecutando ALTER TABLE...")
        # En PostgreSQL ALTER TABLE no tiene IF NOT EXISTS para ADD COLUMN en versiones antiguas, 
        # pero podemos usar un bloque anónimo o simplemente intentar y capturar el error.
        try:
            cur.execute("ALTER TABLE items_pedido ADD COLUMN observaciones TEXT;")
            print("Columna 'observaciones' añadida con éxito.")
        except Exception as e:
            if "already exists" in str(e):
                print("La columna 'observaciones' ya existe.")
            else:
                raise e
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrate()
