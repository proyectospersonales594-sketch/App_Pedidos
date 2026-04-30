from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import SessionLocal
from models import Cliente, Pedido
from email_service import enviar_correo_alertas

def tarea_envio_alertas():
    print("Ejecutando tarea de alerta de clientes...")
    db: Session = SessionLocal()
    try:
        # 1. Clientes que nunca han hecho pedidos
        # SELECT * FROM clientes WHERE id NOT IN (SELECT DISTINCT cliente_id FROM pedidos)
        clientes_sin_pedidos = db.query(Cliente).filter(
            ~Cliente.id.in_(db.query(Pedido.cliente_id).distinct())
        ).all()

        # 2. Clientes que no han hecho pedidos en los últimos 8 días (o más)
        # SQLAlchemy func.max para la última fecha
        # Equivalente en SQL: SELECT c.*, MAX(p.fecha) FROM clientes JOIN pedidos GROUP BY c.id HAVING MAX(p.fecha) <= NOW() - 8 days
        hace_8_dias = datetime.utcnow() - timedelta(days=8)
        
        # Primero buscamos el max(fecha) por cliente
        subquery = db.query(
            Pedido.cliente_id, 
            func.max(Pedido.fecha).label('ultima_fecha')
        ).group_by(Pedido.cliente_id).subquery()
        
        # Filtramos aquellos cuya ultima_fecha es <= hace_8_dias
        clientes_riesgo_query = db.query(Cliente, subquery.c.ultima_fecha).join(
            subquery, Cliente.id == subquery.c.cliente_id
        ).filter(subquery.c.ultima_fecha <= hace_8_dias).all()
        
        # clientes_riesgo_query devuelve tuplas (Cliente, ultima_fecha)
        # Vamos a inyectar 'ultima_fecha' en el objeto Cliente para simplificar el frontend del correo
        clientes_riesgo = []
        for c, f in clientes_riesgo_query:
            c.ultima_fecha = f
            clientes_riesgo.append(c)

        print(f"Encontrados: {len(clientes_sin_pedidos)} sin pedidos, {len(clientes_riesgo)} inactivos > 8 días.")

        # Si no hay nada que reportar, podemos decidir no enviar o enviar igual. Enviaremos igual.
        enviar_correo_alertas("carojames79@gmail.com", clientes_sin_pedidos, clientes_riesgo)
        
    except Exception as e:
        print(f"Error en tarea_envio_alertas: {e}")
    finally:
        db.close()
