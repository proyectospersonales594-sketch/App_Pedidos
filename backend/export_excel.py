import io
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

def generate_pedidos_excel(pedidos_por_fecha):
    wb = Workbook()
    
    # Definir estilos basados en la plantilla
    header_fill = PatternFill(start_color="002060", end_color="002060", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    title_font = Font(bold=True, size=14) 
    
    border_side = Side(border_style="thin", color="000000")
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    
    if not pedidos_por_fecha:
        ws = wb.active
        ws.title = "Sin pedidos"
        ws["A1"] = "No hay pedidos para exportar"
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output
    
    for idx, (fecha, pedidos) in enumerate(pedidos_por_fecha.items()):
        if isinstance(fecha, (datetime.date, datetime.datetime)):
            sheet_name = f"Para_el_{fecha.strftime('%d-%m-%Y')}"
            title_date = fecha.strftime('%d/%m/%Y')
        else:
            sheet_name = "Sin_Fecha"
            title_date = "FECHA INDEFINIDA"
            
        ws = wb.create_sheet(title=sheet_name)
        
        # Fila 1: Título General
        ws.merge_cells("A1:M1")
        ws["A1"] = f"PEDIDOS JOSE CARO {title_date}"
        ws["A1"].font = title_font
        ws["A1"].alignment = Alignment(horizontal="left", vertical="center")
        
        # Fila 2: Cabeceras
        headers = ["ID Pedido", "Fecha de entrega", "Nombre de negocio", "Tipo", "Direccion", 
                   "Barrio_poblacion", "Contacto_comercial", "Telefono", "Productos", 
                   "Cantidad", "Precio unit.", "Valor total", "Observaciones"]
        
        for col_num, header_title in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col_num, value=header_title)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align
            cell.border = thin_border
            
        current_row = 3
        
        for pedido in pedidos:
            cliente = pedido["cliente"]
            items = pedido["items"]
            
            start_row = current_row
            num_items = len(items)
            end_row = current_row + num_items - 1
            
            cols_to_merge = [1, 2, 3, 4, 5, 6, 7, 8] # Columnas de cliente
            
            # Combinar celdas si hay múltiples productos
            if num_items > 1:
                for col_idx in cols_to_merge:
                    ws.merge_cells(start_row=start_row, start_column=col_idx, end_row=end_row, end_column=col_idx)
            
            # Insertar datos del cliente
            ws.cell(row=start_row, column=1, value=pedido["id"]).alignment = Alignment(horizontal="center", vertical="center")
            
            fecha_entrega_str = pedido["fecha_entrega"].strftime('%Y-%m-%d') if pedido.get("fecha_entrega") else ''
            ws.cell(row=start_row, column=2, value=fecha_entrega_str).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=start_row, column=3, value=cliente.get("nombre_negocio", "")).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=start_row, column=4, value=cliente.get("tipo_negocio", "")).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=start_row, column=5, value=cliente.get("direccion", "")).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=start_row, column=6, value=cliente.get("barrio_poblacion", "")).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=start_row, column=7, value=cliente.get("contacto_comercial", "")).alignment = Alignment(horizontal="center", vertical="center")
            ws.cell(row=start_row, column=8, value=cliente.get("telefono", "")).alignment = Alignment(horizontal="center", vertical="center")
            
            # Aplicar bordes a la sección del cliente
            for r in range(start_row, end_row + 1):
                for c in cols_to_merge:
                    ws.cell(row=r, column=c).border = thin_border
            
            # Insertar productos
            for i, item in enumerate(items):
                r = start_row + i
                
                c_prod = ws.cell(row=r, column=9, value=item["producto_nombre"])
                c_cant = ws.cell(row=r, column=10, value=item["cantidad"])
                c_precio = ws.cell(row=r, column=11, value=item["precio_unitario"])
                c_total = ws.cell(row=r, column=12, value=item["cantidad"] * item["precio_unitario"])
                c_obs = ws.cell(row=r, column=13, value=item.get("observaciones", ""))
                
                for c in [c_prod, c_cant, c_precio, c_total, c_obs]:
                    c.border = thin_border
                    c.alignment = Alignment(horizontal="center", vertical="center")
                    
                # Formato de moneda
                c_precio.number_format = '#,##0'
                c_total.number_format = '#,##0'
                
            current_row = end_row + 1

        # Ajustar anchos de columnas
        for col_idx in range(1, 14):
            ws.column_dimensions[get_column_letter(col_idx)].width = 18
            
        ws.column_dimensions['I'].width = 25 # Productos
        ws.column_dimensions['M'].width = 25 # Observaciones
        ws.column_dimensions['C'].width = 25 # Nombre de negocio

    # Eliminar hoja por defecto si hay más hojas
    if len(wb.sheetnames) > 1 and "Sheet" in wb.sheetnames:
        del wb["Sheet"]
        
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
