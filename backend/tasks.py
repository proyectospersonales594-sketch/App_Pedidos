from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from database import SessionLocal
from models import Cliente, Pedido
from email_service import enviar_correo_alertas

import time

def tarea_envio_alertas():
    # Esperar 10 segundos para asegurar que la red de Render esté lista al arrancar
    print("Esperando 10 segundos para estabilidad de red...")
    time.sleep(10)
    
    print("Ejecutando tarea de alerta de clientes...")
    db: Session = SessionLocal()
    try:
        # ... (lógica de búsqueda de clientes sin cambios) ...
        # 1. Clientes que nunca han hecho pedidos
        clientes_sin_pedidos = db.query(Cliente).filter(
            ~Cliente.id.in_(db.query(Pedido.cliente_id).distinct())
        ).all()

        # 2. Clientes inactivos > 8 días (Usando hora Colombia UTC-5)
        ahora_col = datetime.now(timezone(timedelta(hours=-5))).replace(tzinfo=None)
        hace_8_dias = ahora_col - timedelta(days=8)
        subquery = db.query(
            Pedido.cliente_id, 
            func.max(Pedido.fecha).label('ultima_fecha')
        ).group_by(Pedido.cliente_id).subquery()
        
        clientes_riesgo_query = db.query(Cliente, subquery.c.ultima_fecha).join(
            subquery, Cliente.id == subquery.c.cliente_id
        ).filter(subquery.c.ultima_fecha <= hace_8_dias).all()
        
        clientes_riesgo = []
        for c, f in clientes_riesgo_query:
            c.ultima_fecha = f
            clientes_riesgo.append(c)

        print(f"Encontrados: {len(clientes_sin_pedidos)} sin pedidos, {len(clientes_riesgo)} inactivos.")

        # Intentar envío (Usando el correo de la cuenta para saltar restricciones de prueba)
        exito = enviar_correo_alertas("proyectospersonales594@gmail.com", clientes_sin_pedidos, clientes_riesgo)
        return exito
        
    except Exception as e:
        print(f"Error en tarea_envio_alertas: {e}")
        return False
    finally:
        db.close()
