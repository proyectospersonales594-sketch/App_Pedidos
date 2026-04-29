from database import engine
import models

def init_db():
    print("Creando las tablas en la base de datos de Supabase...")
    # Esto lee todas las clases que heredan de Base en models.py y crea sus tablas correspondientes
    # Si la tabla ya existe, no hace nada (no la sobreescribe).
    models.Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente.")

if __name__ == "__main__":
    init_db()
