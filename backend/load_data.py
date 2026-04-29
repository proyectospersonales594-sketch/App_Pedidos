import pandas as pd
from database import SessionLocal
from models import Cliente
import os

def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "..", "inputs", "DATA ENTREGABLE.xlsx")
    
    if not os.path.exists(file_path):
        print(f"El archivo {file_path} no existe.")
        return

    print("Cargando datos del Excel...")
    df = pd.read_excel(file_path)
    
    # Rellenar nulos con string vacío
    df = df.fillna("")

    db = SessionLocal()
    
    # Limpiamos la tabla primero o simplemente añadimos (aquí añadimos)
    # Por si se corre varias veces y no queremos duplicados:
    db.query(Cliente).delete()
    db.commit()

    clientes_a_insertar = []

    for index, row in df.iterrows():
        # Saltamos si el nombre del cliente está vacío
        nombre = str(row.iloc[1]).strip()
        if not nombre:
            continue

        cliente = Cliente(
            nombre_cliente=nombre,
            cc_o_nit=str(row.iloc[2]).strip(),
            direccion=str(row.iloc[3]).strip(),
            barrio_poblacion=str(row.iloc[4]).strip(),
            ubicacion=str(row.iloc[5]).strip(),
            contacto_comercial=str(row.iloc[6]).strip(),
            telefono=str(row.iloc[7]).strip(),
            correo_electronico=str(row.iloc[8]).strip(),
            nombre_negocio=str(row.iloc[9]).strip(),
            dias_visita=str(row.iloc[10]).strip(),
            tipo_negocio=str(row.iloc[11]).strip()
        )
        clientes_a_insertar.append(cliente)

    print(f"Se van a insertar {len(clientes_a_insertar)} clientes...")
    db.add_all(clientes_a_insertar)
    db.commit()
    db.close()
    
    print("Datos cargados exitosamente usando SQLAlchemy (SQL).")

if __name__ == "__main__":
    load_data()
