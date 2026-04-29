from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ClienteBase(BaseModel):
    nombre_cliente: str
    cc_o_nit: str
    direccion: Optional[str] = None
    barrio_poblacion: Optional[str] = None
    ubicacion: Optional[str] = None
    contacto_comercial: Optional[str] = None
    telefono: Optional[str] = None
    correo_electronico: Optional[str] = None
    nombre_negocio: Optional[str] = None
    dias_visita: Optional[str] = None
    tipo_negocio: Optional[str] = None

class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True

class PedidoResponse(BaseModel):
    id: int
    cliente_id: int
    fecha: datetime
    fecha_entrega: Optional[datetime] = None
    estado: str
    total: float

    class Config:
        from_attributes = True

class PedidoListResponse(PedidoResponse):
    cliente_nombre: str
    nombre_negocio: Optional[str] = None

class ItemPedidoCreate(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float
    observaciones: Optional[str] = None

class PedidoCreate(BaseModel):
    cliente_id: int
    fecha_entrega: Optional[datetime] = None
    items: List[ItemPedidoCreate]

class PrecioSugeridoResponse(BaseModel):
    precio: float
    origen: str

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float

class ProductoResponse(ProductoBase):
    id: int

    class Config:
        from_attributes = True

class ItemHistorialProductoResponse(BaseModel):
    pedido_id: int
    fecha: datetime
    cliente_nombre: str
    cantidad: int
    precio_unitario: float

    class Config:
        from_attributes = True
class ItemPedidoResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    producto_nombre: str
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True

class PedidoDetailResponse(PedidoListResponse):
    items: List[ItemPedidoResponse]
