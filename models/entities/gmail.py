import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import schedule
from confiDB import Database

# Lista para almacenar emprendedores registrados con exito, que seran enviadas por correo
solicitud_emprendedores = []

# Verificar correos de usuarios administradores en la base de datos
def correos_admin():
    database = Database()
    cursor_pointer = database.connection.cursor()
    cursor_pointer.execute("SELECT email FROM users")  # Solo seleccionar la columna de correos
    myresult = cursor_pointer.fetchall()
    
    # Almacenar correos electrónicos en una lista
    lista_correos = [record[0] for record in myresult]
    
    cursor_pointer.close()
    
    return lista_correos


def enviar_correo_personalizado(lista_razones_sociales):
    # Configuración
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'rolandoerojasnunez@gmail.com'
    sender_password = 'eprittkpsnstnbqh'  # Esto debería manejarse de forma segura
    receiver_email = 'rolando@produccionesb.cl'
    
    # Crear el objeto de mensaje
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f'Registro de Nuevos Emprendedores {datetime.now().date()}'

    # Crear el contenido del mensaje con las razones sociales
    message = "Estimado Administrador, te informamos que existen los siguientes emprendedores esperando su validacion en el portal:\n\n"
    for razon_social in lista_razones_sociales:
        message += f"- {razon_social}\n"

    # Agregar el pie de mensaje
    message += "\n\nEste es un mensaje generado automáticamente. Por favor, no responder a esta dirección de correo.\nLa Florida Emprende"

    msg.attach(MIMEText(message, 'plain'))

    try:
        # Conexión al servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Envío del correo
        server.sendmail(sender_email, receiver_email, msg.as_string())

        # Cierre de la conexión
        server.quit()
        print("Correo enviado exitosamente")
        # Limpiar la lista de razones sociales exitosas
        lista_razones_sociales.clear()
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Función para enviar el correo programado
def enviar_correo_programado():
    global solicitud_emprendedores
    if solicitud_emprendedores:
        enviar_correo_personalizado(solicitud_emprendedores)
    else:
        print("No hay razones sociales exitosas para enviar.")

# Función para programar el envío del correo
def programar_envio_correo():
    diainicial = "monday"
    diafinal = "friday"
    hora = "09:00"

    # Programar la ejecución de la función con las variables pasadas como argumentos
    schedule.every().monday.to.friday.at(hora).do(enviar_correo_programado, diainicial=diainicial, diafinal=diafinal, hora=hora)

# Función para enviar el correo programado
def enviar_correo_programado():
    global solicitud_emprendedores
    if solicitud_emprendedores:
        enviar_correo_personalizado(solicitud_emprendedores)
    else:
        print("No hay razones sociales exitosas para enviar.")