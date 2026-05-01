import io
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

def generate_pedidos_excel(pedidos_por_fecha):
    wb = Workbook()
    
    # Estilos base
    header_fill = PatternFill(start_color="002060", end_color="002060", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    border_side = Side(border_style="thin", color="000000")
    thin_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)
    
    # Colores intercalados por pedido
    fill_azul_medio = PatternFill(start_color="8DB4E2", end_color="8DB4E2", fill_type="solid")
    fill_azul_claro = PatternFill(start_color="C5D9F1", end_color="C5D9F1", fill_type="solid")
    
    if not pedidos_por_fecha:
        ws = wb.active
        ws.title = "Sin pedidos"
        ws["A1"] = "No hay pedidos para exportar"
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output
    
    for fecha, pedidos in pedidos_por_fecha.items():
        if isinstance(fecha, (datetime.date, datetime.datetime)):
            sheet_name = f"Para_el_{fecha.strftime('%d-%m-%Y')}"
            title_date = fecha.strftime('%d/%m/%Y')
        else:
            sheet_name = "Sin_Fecha"
            title_date = "FECHA INDEFINIDA"
            
        ws = wb.create_sheet(title=sheet_name)
        
        # Fila 1: Título (Centrado en 12 columnas: A a L)
        ws.merge_cells("A1:L1")
        cell_title = ws["A1"]
        cell_title.value = f"PEDIDOS JOSE CARO {title_date}"
        cell_title.font = header_font
        cell_title.fill = header_fill
        cell_title.alignment = Alignment(horizontal="center", vertical="center")
        
        # Fila 2: Cabeceras (Eliminamos ID Pedido)
        headers = ["Fecha de entrega", "Nombre de negocio", "Tipo", "Direccion", 
                   "Barrio_poblacion", "Contacto_comercial", "Telefono", "Productos", 
                   "Cantidad", "Precio unit.", "Valor total", "Observaciones"]
        
        for col_num, header_title in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col_num, value=header_title)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align
            cell.border = thin_border
            
        current_row = 3
        for p_idx, pedido in enumerate(pedidos):
            cliente = pedido["cliente"]
            items = pedido["items"]
            current_fill = fill_azul_medio if p_idx % 2 == 0 else fill_azul_claro
            
            num_items = len(items)
            start_row = current_row
            end_row = current_row + num_items - 1
            
            # 1. Aplicar fondo y bordes a todo el bloque (12 columnas)
            for r in range(start_row, end_row + 1):
                for c in range(1, 13):
                    cell = ws.cell(row=r, column=c)
                    cell.fill = current_fill
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="center", vertical="center")

            # 2. Insertar datos del cliente (Columnas 1-7)
            f_ent = pedido["fecha_entrega"].strftime('%Y-%m-%d') if pedido.get("fecha_entrega") else ''
            ws.cell(row=start_row, column=1, value=f_ent)
            ws.cell(row=start_row, column=2, value=cliente.get("nombre_negocio", ""))
            ws.cell(row=start_row, column=3, value=cliente.get("tipo_negocio", ""))
            
            c_dir = ws.cell(row=start_row, column=4, value=cliente.get("direccion", ""))
            c_dir.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
            ws.cell(row=start_row, column=5, value=cliente.get("barrio_poblacion", ""))
            ws.cell(row=start_row, column=6, value=cliente.get("contacto_comercial", ""))
            ws.cell(row=start_row, column=7, value=cliente.get("telefono", ""))

            if num_items > 1:
                for col_idx in range(1, 8):
                    ws.merge_cells(start_row=start_row, start_column=col_idx, end_row=end_row, end_column=col_idx)

            # 3. Insertar productos (Columnas 8-12)
            for i, item in enumerate(items):
                r = start_row + i
                ws.cell(row=r, column=8, value=item["producto_nombre"]).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                ws.cell(row=r, column=9, value=item["cantidad"])
                
                c_precio = ws.cell(row=r, column=10, value=item["precio_unitario"])
                c_precio.number_format = '#,##0'
                
                c_total = ws.cell(row=r, column=11, value=item["cantidad"] * item["precio_unitario"])
                c_total.number_format = '#,##0'
                
                c_obs = ws.cell(row=r, column=12, value=item.get("observaciones", ""))
                c_obs.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
            current_row = end_row + 1

        # Auto-ajustar anchos
        for col in ws.columns:
            max_length = 0
            column_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if cell.value:
                        lines = str(cell.value).split('\n')
                        current_max = max(len(line) for line in lines)
                        if current_max > max_length: max_length = current_max
                except: pass
            ws.column_dimensions[column_letter].width = max(max_length + 2, 10)

    if len(wb.sheetnames) > 1 and "Sheet" in wb.sheetnames:
        del wb["Sheet"]
        
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
