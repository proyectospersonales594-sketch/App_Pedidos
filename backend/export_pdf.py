import io
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def generate_pedidos_pdf(pedidos_por_fecha):
    output = io.BytesIO()
    # A4 landscape is 29.7 cm x 21 cm. Usamos margenes muy pequeños (0.5cm) para maximizar el espacio
    doc = SimpleDocTemplate(
        output, 
        pagesize=landscape(A4), 
        rightMargin=0.5*cm, 
        leftMargin=0.5*cm, 
        topMargin=0.5*cm, 
        bottomMargin=0.5*cm
    )
    
    elements = []
    
    # Estilo moderno: titulo más pequeño, sin colores de excel
    title_style = ParagraphStyle(
        name='ModernTitle', 
        fontSize=12, 
        leading=14, 
        alignment=1, # Centro
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )
    
    # Textos más sobrios (gris oscuro)
    cell_style = ParagraphStyle(
        name='CellStyle', 
        fontSize=7.5, 
        leading=9, 
        alignment=1, # Centro
        textColor=colors.HexColor('#334155')
    )
    
    header_cell_style = ParagraphStyle(
        name='HeaderStyle', 
        fontSize=8, 
        leading=10, 
        alignment=1, 
        textColor=colors.HexColor('#0f172a'), 
        fontName='Helvetica-Bold'
    )
    
    if not pedidos_por_fecha:
        elements.append(Paragraph("No hay pedidos para exportar", title_style))
        doc.build(elements)
        output.seek(0)
        return output
    
    # Cabeceras
    headers = [
        "F. Entrega", "Negocio", "Tipo", "Dirección", 
        "Barrio", "Cliente", "NIT", "Teléfono", "Producto", 
        "Cant", "P. Unit.", "Total", "Obs"
    ]
    
    header_row = [Paragraph(h, header_cell_style) for h in headers]
    
    for fecha, pedidos in pedidos_por_fecha.items():
        if isinstance(fecha, (datetime.date, datetime.datetime)):
            title_date = fecha.strftime('%d/%m/%Y')
        else:
            title_date = "FECHA INDEFINIDA"
            
        elements.append(Paragraph(f"PEDIDOS JOSE CARO - {title_date}", title_style))
        elements.append(Spacer(1, 0.3*cm))
        
        data = [header_row]
        
        # Diseño moderno: sin bordes verticales, líneas sutiles
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')), # Fondo gris ultra claro para la cabecera
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Lineas divisorias sutiles horizontales (nada de cajas de Excel)
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#cbd5e1')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#cbd5e1')),
            
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
        ])
        
        row_idx = 1
        for p_idx, pedido in enumerate(pedidos):
            cliente = pedido["cliente"]
            items = pedido["items"]
            
            f_ent = pedido["fecha_entrega"].strftime('%d/%m/%Y') if pedido.get("fecha_entrega") else ''
            negocio = cliente.get("nombre_negocio", "")
            tipo = cliente.get("tipo_negocio", "")
            direccion = cliente.get("direccion", "")
            barrio = cliente.get("barrio_poblacion", "")
            nombre_cliente = cliente.get("nombre_cliente", "")
            nit = cliente.get("cc_o_nit", "")
            telefono = cliente.get("telefono", "")
            
            # Intercalado de filas muy sutil (blanco y casi blanco)
            bg_color = colors.HexColor('#ffffff') if p_idx % 2 == 0 else colors.HexColor('#f8fafc')
            
            for i, item in enumerate(items):
                producto = item["producto_nombre"]
                cant = str(item["cantidad"])
                p_unit = f'${item["precio_unitario"]:,.0f}'
                total = f'${item["cantidad"] * item["precio_unitario"]:,.0f}'
                obs = item.get("observaciones", "") or ""
                
                row_data = [
                    Paragraph(f_ent, cell_style),
                    Paragraph(negocio, cell_style),
                    Paragraph(tipo, cell_style),
                    Paragraph(direccion, cell_style),
                    Paragraph(barrio, cell_style),
                    Paragraph(nombre_cliente, cell_style),
                    Paragraph(nit, cell_style),
                    Paragraph(telefono, cell_style),
                    Paragraph(producto, cell_style),
                    Paragraph(cant, cell_style),
                    Paragraph(p_unit, cell_style),
                    Paragraph(total, cell_style),
                    Paragraph(obs, cell_style)
                ]
                
                data.append(row_data)
                
                table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color)
                row_idx += 1
            
            # Combinar las celdas del cliente si hay varios items
            if len(items) > 1:
                start_merge = row_idx - len(items)
                end_merge = row_idx - 1
                for col in range(8): # Primeras 8 columnas (datos del cliente)
                    table_style.add('SPAN', (col, start_merge), (col, end_merge))
        
        # Nuevos anchos calculados para usar los 28.7 cm disponibles (29.7 - 0.5 - 0.5)
        # Esto soluciona que la fecha se divida en dos renglones
        col_widths = [
            2.0*cm, # F. Entrega
            2.7*cm, # Negocio
            1.7*cm, # Tipo
            2.9*cm, # Dirección
            2.0*cm, # Barrio
            2.7*cm, # Cliente
            2.1*cm, # NIT
            2.2*cm, # Teléfono
            3.5*cm, # Producto
            1.1*cm, # Cant
            1.8*cm, # P. Unit
            2.0*cm, # Total
            2.0*cm  # Obs
        ]
        
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(1, 1*cm))
        
    doc.build(elements)
    output.seek(0)
    return output
