import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def generar_html_tabla(clientes, titulo, descripcion):
    """Genera una tabla HTML atractiva para una lista de clientes."""
    if not clientes:
        return f"""
        <div style="margin-bottom: 30px;">
            <h2 style="color: #4f46e5; font-family: sans-serif;">{titulo}</h2>
            <p style="color: #4b5563; font-family: sans-serif;">{descripcion}</p>
            <p style="color: #10b981; font-family: sans-serif; font-weight: bold;">¡Excelente! No hay clientes en esta categoría hoy.</p>
        </div>
        """

    filas_html = ""
    for c in clientes:
        filas_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #1f2937; font-weight: 600; word-break: break-word; font-size: 15px;">{c.nombre_negocio or 'N/A'}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; color: #4b5563; white-space: nowrap; font-size: 15px;">{c.telefono or 'N/A'}</td>
        </tr>
        """

    tabla_html = f"""
    <div style="margin-bottom: 30px;">
        <h2 style="color: #4f46e5; font-family: sans-serif; margin-bottom: 5px;">{titulo}</h2>
        <p style="color: #4b5563; font-family: sans-serif; margin-bottom: 15px;">{descripcion}</p>
        <div class="table-wrapper" style="width: 100%;">
            <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);">
                <thead style="background-color: #f3f4f6;">
                    <tr>
                        <th style="padding: 12px; text-align: left; color: #374151; font-weight: 600; border-bottom: 2px solid #e5e7eb; width: 70%;">Negocio</th>
                        <th style="padding: 12px; text-align: left; color: #374151; font-weight: 600; border-bottom: 2px solid #e5e7eb; width: 30%;">Celular</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </div>
    </div>
    """
    return tabla_html


def enviar_correo_alertas(destinatario, clientes_sin_pedidos, clientes_riesgo):
    """Construye y envía el correo con las dos listas de clientes."""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("ERROR: Credenciales SMTP no configuradas en .env")
        return False

    remitente = SMTP_USERNAME

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reporte Diario de Clientes Inactivos"
    msg["From"] = remitente
    msg["To"] = destinatario

    html_sin_pedidos = generar_html_tabla(
        clientes_sin_pedidos,
        "Clientes Nunca Activados",
        "Hola Jose Caro, estos son los clientes que al día de hoy están en la base de datos, pero no han realizado pedidos. ¡Comunícate con ellos y actívalos!"
    )

    html_riesgo = generar_html_tabla(
        clientes_riesgo,
        "Clientes en Riesgo de Fuga (Inactivos por mas de 8 días)",
        "Jose Caro, estos son los clientes activados, que no hacen pedido hace 8 días o más."
    )

    html_body = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @media only screen and (max-width: 600px) {{
                .container {{ padding: 15px !important; }}
                .header h1 {{ font-size: 22px !important; }}
                td, th {{ padding: 10px 8px !important; font-size: 14px !important; }}
                .table-wrapper {{ overflow-x: auto !important; -webkit-overflow-scrolling: touch; }}
                table {{ min-width: 440px !important; }}
            }}
        </style>
    </head>
    <body style="background-color: #f3f4f6; padding: 20px; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <div class="container" style="max-width: 670px; margin: 0 auto; background-color: #ffffff; padding: 40px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border: 1px solid #e5e7eb;">
            <div class="header" style="text-align: center; margin-bottom: 35px;">
                <div style="background-color: #4f46e5; width: 60px; height: 60px; border-radius: 15px; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;">
                    <span style="color: white; font-size: 30px; font-weight: bold; line-height: 60px;">P</span>
                </div>
                <h1 style="color: #1f2937; margin: 0; font-size: 28px; font-weight: 800;">Reporte de Activación</h1>
                <p style="color: #6b7280; margin-top: 8px; font-size: 16px;">Sistema de Gestión de Pedidos</p>
            </div>
            
            <div style="width: 100%;">
                {html_sin_pedidos}
            </div>
            
            <div style="height: 1px; background-color: #e5e7eb; margin: 40px 0;"></div>
            
            <div style="width: 100%;">
                {html_riesgo}
            </div>
            
            <div style="text-align: center; margin-top: 45px; padding-top: 25px; border-top: 1px solid #f3f4f6;">
                <p style="color: #9ca3af; font-size: 13px;">Este es un mensaje automático prioritario para Jose Caro.</p>
            </div>
        </div>
    </body>
    </html>
    """

    parte_html = MIMEText(html_body, "html")
    msg.attach(parte_html)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        print(f"Correo de alerta enviado exitosamente a {destinatario}")
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False
