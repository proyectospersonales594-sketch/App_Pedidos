import re
with open('main.py', 'r') as f:
    content = f.read()

exportar_idx = content.find('@app.get("/pedidos/exportar")')
exportar_block = content[exportar_idx:]
content = content[:exportar_idx]

get_pedido_idx = content.find('@app.get("/pedidos/{pedido_id}"')
content = content[:get_pedido_idx] + exportar_block + '\n' + content[get_pedido_idx:]

with open('main.py', 'w') as f:
    f.write(content)
