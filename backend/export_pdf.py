import io
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

def generate_pedidos_pdf(pedidos_por_fecha):
    output = io.BytesIO()
    # A4 landscape is 29.7 cm x 21 cm
    doc = SimpleDocTemplate(
        output, 
        pagesize=landscape(A4), 
        rightMargin=1*cm, 
        leftMargin=1*cm, 
        topMargin=1.5*cm, 
        bottomMargin=1.5*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    cell_style = ParagraphStyle(name='CellStyle', fontSize=8, leading=10, alignment=1) # Center
    header_cell_style = ParagraphStyle(name='HeaderStyle', fontSize=9, leading=11, alignment=1, textColor=colors.white, fontName='Helvetica-Bold')
    
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
        elements.append(Spacer(1, 0.5*cm))
        
        data = [header_row]
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#002060')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,0), (-1,0), 6),
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
            
            # Alternate row colors by order (not by item)
            bg_color = colors.HexColor('#8DB4E2') if p_idx % 2 == 0 else colors.HexColor('#C5D9F1')
            
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
                
                # Style background for this row
                table_style.add('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color)
                row_idx += 1
            
            # Merge customer cells if multiple items
            if len(items) > 1:
                start_merge = row_idx - len(items)
                end_merge = row_idx - 1
                for col in range(8): # First 8 columns
                    table_style.add('SPAN', (col, start_merge), (col, end_merge))
        
        # Calculate optimal widths
        # total width is A4 landscape width (29.7cm) - margins (2cm) = 27.7cm
        col_widths = [
            1.8*cm, 2.5*cm, 1.6*cm, 2.7*cm, 
            2.0*cm, 2.5*cm, 1.9*cm, 1.9*cm, 
            3.2*cm, 1.2*cm, 1.8*cm, 2.0*cm, 
            2.6*cm
        ]
        
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(table_style)
        elements.append(t)
        elements.append(Spacer(1, 1*cm))
        
    doc.build(elements)
    output.seek(0)
    return output
