from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Force reload - v2

# Importamos los modelos y la base de datos
import models
import schemas
from database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import Response
import datetime
from datetime import timezone, timedelta
from export_excel import generate_pedidos_excel
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from tasks import tarea_envio_alertas
from database import SessionLocal

# Inicializamos el scheduler con zona horaria de Colombia
col_tz = timezone(timedelta(hours=-5))
scheduler = BackgroundScheduler(timezone=col_tz)

def verificar_reporte_diario():
    """
    Verifica si ya se envió el reporte de hoy. 
    Si no, lo envía y actualiza la fecha en la base de datos.
    """
    db = SessionLocal()
    try:
        # Obtener fecha hoy en Colombia (UTC-5)
        col_tz = timezone(timedelta(hours=-5))
        hoy = datetime.datetime.now(col_tz).date().isoformat() 
        
        # Consultar la última fecha de envío
        config = db.query(models.Configuracion).filter(models.Configuracion.clave == "ultimo_envio_alerta").first()
        
        if not config:
            # Si no existe el registro, lo creamos
            config = models.Configuracion(clave="ultimo_envio_alerta", valor="")
            db.add(config)
            db.commit()

        if config.valor != hoy:
            print(f"Iniciando envío de reporte diario para hoy ({hoy})...")
            # Ejecutar la tarea de envío
            enviado = tarea_envio_alertas()
            
            if enviado:
                # Solo actualizamos la fecha si se envió con éxito
                config.valor = hoy
                db.commit()
                print("Reporte diario enviado exitosamente.")
            else:
                print("No se pudo enviar el reporte hoy. Se reintentará en el próximo inicio.")
        else:
            print(f"El reporte de hoy ({hoy}) ya fue enviado anteriormente.")
            
    except Exception as e:
        print(f"Error al verificar/enviar reporte diario: {e}")
    finally:
        db.close()

import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- FASE DE PRODUCCIÓN ---
    # 1. Al despertar, verificamos el reporte en un HILO SEPARADO
    # Esto evita que la App se quede "congelada" al iniciar si el correo tarda.
    print("Servidor iniciado/despertado. Iniciando verificación de reporte en segundo plano...")
    thread = threading.Thread(target=verificar_reporte_diario)
    thread.start()

    # 2. Programar también el scheduler
    scheduler.add_job(
        verificar_reporte_diario, 
        trigger=CronTrigger(day_of_week='mon-sat', hour=7, minute=0, timezone=col_tz),
        id="alerta_diaria_clientes",
        name="Verificar y enviar alerta diaria a las 7am",
        replace_existing=True,
    )

    scheduler.start()
    yield
    scheduler.shutdown()
    print("Scheduler detenido.")

app = FastAPI(title="App Pedidos API", lifespan=lifespan)

# Configuramos CORS (Cross-Origin Resource Sharing)
# Esto es vital para que el frontend en Vue (que corre en otro puerto) pueda llamar a nuestra API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiar esto a la URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"mensaje": "Bienvenido a la API de App Pedidos"}

# Aquí agregaremos las rutas para Clientes, Productos y Pedidos más adelante.
@app.get("/clientes", response_model=List[schemas.ClienteResponse])
def get_clientes(search: str = Query(None, description="Filtrar por nombre de cliente"), db: Session = Depends(get_db)):
    query = db.query(models.Cliente)
    if search:
        # Busca tanto por nombre_cliente como por nombre_negocio
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                models.Cliente.nombre_cliente.ilike(search_filter),
                models.Cliente.nombre_negocio.ilike(search_filter)
            )
        )
    
    # Ordenar alfabéticamente
    query = query.order_by(models.Cliente.nombre_cliente.asc())
    return query.all()

@app.get("/clientes/opciones")
def get_clientes_opciones(db: Session = Depends(get_db)):
    ubicaciones = db.query(models.Cliente.ubicacion).filter(models.Cliente.ubicacion.isnot(None)).distinct().all()
    tipos_negocio = db.query(models.Cliente.tipo_negocio).filter(models.Cliente.tipo_negocio.isnot(None)).distinct().all()
    
    return {
        "ubicaciones": sorted([u[0] for u in ubicaciones if u[0].strip()]),
        "tipos_negocio": sorted([t[0] for t in tipos_negocio if t[0].strip()])
    }

@app.post("/clientes", response_model=schemas.ClienteResponse)
def create_cliente(cliente: schemas.ClienteBase, db: Session = Depends(get_db)):
    db_cliente = models.Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.put("/clientes/{cliente_id}", response_model=schemas.ClienteResponse)
def update_cliente(cliente_id: int, cliente: schemas.ClienteBase, db: Session = Depends(get_db)):
    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Actualizar los campos
    for key, value in cliente.model_dump().items():
        setattr(db_cliente, key, value)
        
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.delete("/clientes/{cliente_id}")
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    db.delete(db_cliente)
    db.commit()
    return {"mensaje": "Cliente eliminado exitosamente"}

@app.get("/clientes/{cliente_id}/pedidos", response_model=List[schemas.PedidoResponse])
def get_pedidos_cliente(cliente_id: int, db: Session = Depends(get_db)):
    pedidos = db.query(models.Pedido).filter(models.Pedido.cliente_id == cliente_id).order_by(models.Pedido.fecha.desc()).all()
    return pedidos

# --- PRODUCTOS ---

@app.get("/productos", response_model=List[schemas.ProductoResponse])
def get_productos(search: str = Query(None, description="Filtrar por nombre de producto"), db: Session = Depends(get_db)):
    query = db.query(models.Producto)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(models.Producto.nombre.ilike(search_filter))
    
    query = query.order_by(models.Producto.nombre.asc())
    return query.all()

@app.post("/productos", response_model=schemas.ProductoResponse)
def create_producto(producto: schemas.ProductoBase, db: Session = Depends(get_db)):
    db_producto = models.Producto(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.put("/productos/{producto_id}", response_model=schemas.ProductoResponse)
def update_producto(producto_id: int, producto: schemas.ProductoBase, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    for key, value in producto.model_dump().items():
        setattr(db_producto, key, value)
        
    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.delete("/productos/{producto_id}")
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    db_producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    db.delete(db_producto)
    db.commit()
    return {"mensaje": "Producto eliminado exitosamente"}

@app.get("/productos/{producto_id}/historial", response_model=List[schemas.ItemHistorialProductoResponse])
def get_historial_producto(producto_id: int, db: Session = Depends(get_db)):
    historial = db.query(
        models.ItemPedido.pedido_id,
        models.Pedido.fecha,
        models.Cliente.nombre_cliente.label("cliente_nombre"),
        models.ItemPedido.cantidad,
        models.ItemPedido.precio_unitario
    ).join(models.Pedido, models.ItemPedido.pedido_id == models.Pedido.id)\
     .join(models.Cliente, models.Pedido.cliente_id == models.Cliente.id)\
     .filter(models.ItemPedido.producto_id == producto_id)\
     .order_by(models.Pedido.fecha.desc()).all()
    
    return historial

# --- ENDPOINTS PEDIDOS ---

@app.get("/pedidos/sugerencia-precio", response_model=schemas.PrecioSugeridoResponse)
def get_sugerencia_precio(cliente_id: int, producto_id: int, db: Session = Depends(get_db)):
    ultimo_item = db.query(models.ItemPedido)\
        .join(models.Pedido)\
        .filter(models.Pedido.cliente_id == cliente_id, models.ItemPedido.producto_id == producto_id)\
        .order_by(models.Pedido.fecha.desc())\
        .first()

    if ultimo_item:
        return {"precio": ultimo_item.precio_unitario, "origen": "historial"}

    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto:
        return {"precio": producto.precio, "origen": "base"}

    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.post("/pedidos", response_model=schemas.PedidoResponse)
def create_pedido(pedido_in: schemas.PedidoCreate, db: Session = Depends(get_db)):
    total = sum(item.cantidad * item.precio_unitario for item in pedido_in.items)
    
    db_pedido = models.Pedido(
        cliente_id=pedido_in.cliente_id,
        fecha_entrega=pedido_in.fecha_entrega,
        total=total,
        estado="Pendiente"
    )
    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)

    for item in pedido_in.items:
        db_item = models.ItemPedido(
            pedido_id=db_pedido.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            observaciones=item.observaciones
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_pedido)
    return db_pedido

@app.get("/pedidos", response_model=List[schemas.PedidoListResponse])
def get_pedidos(db: Session = Depends(get_db)):
    pedidos = db.query(
        models.Pedido.id,
        models.Pedido.cliente_id,
        models.Pedido.fecha,
        models.Pedido.fecha_entrega,
        models.Pedido.estado,
        models.Pedido.total,
        models.Cliente.nombre_cliente.label("cliente_nombre"),
        models.Cliente.nombre_negocio.label("nombre_negocio")
    ).join(models.Cliente, models.Pedido.cliente_id == models.Cliente.id)\
     .order_by(models.Pedido.fecha.desc()).all()
    
    return pedidos
@app.get("/pedidos/exportar")
def exportar_pedidos_excel(db: Session = Depends(get_db)):
    col_tz = timezone(timedelta(hours=-5))
    ahora_col = datetime.datetime.now(col_tz)
    hoy = ahora_col.date()
    
    # Lógica de corte: Si es después de las 12 PM, solo exportar de mañana en adelante
    if ahora_col.hour >= 12:
        fecha_inicio_export = hoy + datetime.timedelta(days=1)
    else:
        fecha_inicio_export = hoy

    # Obtener pedidos cuya fecha de entrega sea >= fecha_inicio_export y no sea null
    pedidos_db = db.query(models.Pedido).filter(
        models.Pedido.fecha_entrega != None,
        models.Pedido.fecha_entrega >= fecha_inicio_export
    ).order_by(models.Pedido.fecha_entrega.asc(), models.Pedido.id.asc()).all()
    
    # Agrupar pedidos por fecha_entrega
    pedidos_por_fecha = {}
    
    for p in pedidos_db:
        # Extraer items con producto_nombre
        items_db = db.query(
            models.ItemPedido.cantidad,
            models.ItemPedido.precio_unitario,
            models.ItemPedido.observaciones,
            models.Producto.nombre.label("producto_nombre")
        ).join(models.Producto, models.ItemPedido.producto_id == models.Producto.id)\
         .filter(models.ItemPedido.pedido_id == p.id).all()
        
        items = []
        for i in items_db:
            items.append({
                "cantidad": i.cantidad,
                "precio_unitario": i.precio_unitario,
                "observaciones": i.observaciones,
                "producto_nombre": i.producto_nombre
            })
            
        cliente_db = p.cliente
        cliente_dict = {
            "nombre_negocio": cliente_db.nombre_negocio or cliente_db.nombre_cliente,
            "tipo_negocio": cliente_db.tipo_negocio,
            "direccion": cliente_db.direccion,
            "barrio_poblacion": cliente_db.barrio_poblacion,
            "contacto_comercial": cliente_db.contacto_comercial,
            "telefono": cliente_db.telefono
        }
        
        pedido_dict = {
            "id": p.id,
            "fecha_entrega": p.fecha_entrega,
            "cliente": cliente_dict,
            "items": items
        }
        
        fecha_key = p.fecha_entrega
        try:
            if hasattr(fecha_key, 'date'):
                fecha_key = fecha_key.date()
        except Exception:
            pass
            
        if fecha_key not in pedidos_por_fecha:
            pedidos_por_fecha[fecha_key] = []
            
        pedidos_por_fecha[fecha_key].append(pedido_dict)
        
    excel_file = generate_pedidos_excel(pedidos_por_fecha)
    
    filename = f"pedidos Jose Caro {hoy.strftime('%d-%m-%Y')}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    
    return Response(
        content=excel_file.getvalue(), 
        headers=headers,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.get("/pedidos/{pedido_id}", response_model=schemas.PedidoDetailResponse)
def get_pedido_detalle(pedido_id: int, db: Session = Depends(get_db)):
    # Obtener el pedido con la información del cliente
    pedido = db.query(
        models.Pedido.id,
        models.Pedido.cliente_id,
        models.Pedido.fecha,
        models.Pedido.fecha_entrega,
        models.Pedido.estado,
        models.Pedido.total,
        models.Cliente.nombre_cliente.label("cliente_nombre"),
        models.Cliente.nombre_negocio.label("nombre_negocio")
    ).join(models.Cliente, models.Pedido.cliente_id == models.Cliente.id)\
     .filter(models.Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Obtener los items del pedido con el nombre del producto
    items = db.query(
        models.ItemPedido.id,
        models.ItemPedido.producto_id,
        models.ItemPedido.cantidad,
        models.ItemPedido.precio_unitario,
        models.ItemPedido.observaciones,
        models.Producto.nombre.label("producto_nombre")
    ).join(models.Producto, models.ItemPedido.producto_id == models.Producto.id)\
     .filter(models.ItemPedido.pedido_id == pedido_id).all()

    # Combinar resultado en el esquema esperado
    pedido_dict = dict(pedido._mapping)
    pedido_dict["items"] = [dict(item._mapping) for item in items]
    
    return pedido_dict
@app.delete("/pedidos/{pedido_id}")
def delete_pedido(pedido_id: int, db: Session = Depends(get_db)):
    db_pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Eliminar items primero (por la clave foránea)
    db.query(models.ItemPedido).filter(models.ItemPedido.pedido_id == pedido_id).delete()
    
    # Eliminar el pedido
    db.delete(db_pedido)
    db.commit()
    return {"mensaje": "Pedido eliminado correctamente"}

@app.put("/pedidos/{pedido_id}", response_model=schemas.PedidoResponse)
def update_pedido(pedido_id: int, pedido_data: schemas.PedidoCreate, db: Session = Depends(get_db)):
    db_pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Actualizar cabecera
    db_pedido.cliente_id = pedido_data.cliente_id
    db_pedido.fecha_entrega = pedido_data.fecha_entrega
    
    # Calcular nuevo total
    total = sum(item.cantidad * item.precio_unitario for item in pedido_data.items)
    db_pedido.total = total
    
    # Reemplazar items: eliminar viejos y agregar nuevos
    db.query(models.ItemPedido).filter(models.ItemPedido.pedido_id == pedido_id).delete()
    
    for item in pedido_data.items:
        db_item = models.ItemPedido(
            pedido_id=pedido_id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            observaciones=item.observaciones
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_pedido)
    return db_pedido

