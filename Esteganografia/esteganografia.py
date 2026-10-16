import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from PIL import Image
import tkinter as tk
from tkinter import filedialog

def obtener_llave(password: str):
    salt = b'laboratorio_ciberseguridad_2026'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def cifrar_mensaje(mensaje: str, llave: bytes):
    f = Fernet(llave)
    return f.encrypt(mensaje.encode())

def descifrar_mensaje(datos_cifrados: bytes, llave: bytes):
    f = Fernet(llave)
    return f.decrypt(datos_cifrados).decode()

def mensaje_a_bits(datos_binarios: bytes):
    datos_con_fin = datos_binarios + b'#####END#####'
    return ''.join(format(byte, '08b') for byte in datos_con_fin)

def ocultar_en_imagen(ruta_original: str, bits: str, ruta_salida: str):
    img = Image.open(ruta_original).convert('RGB')
    pixeles = list(img.getdata())
    nuevos_pixeles = []

    indice_bit = 0
    for r, g, b in pixeles:
        canales = [r, g, b]
        for i in range(3):
            if indice_bit < len(bits):
                canales[i] = (canales[i] & ~1) | int(bits[indice_bit])
                indice_bit += 1
        nuevos_pixeles.append(tuple(canales))

    img.putdata(nuevos_pixeles)
    img.save(ruta_salida, "PNG")
    print(f"Proceso terminado. Archivo generado: {ruta_salida}")
    
def extraer_datos_de_imagen(ruta_stego):
    img = Image.open(ruta_stego).convert('RGB')
    pixeles = list(img.getdata())
    bits_extraidos = ""
    for p in pixeles:
        for canal in p:
            bits_extraidos += str(canal & 1)
            
    # Agrupar los bits en bloques exactos de 8 (1 byte)
    bytes_lista = bytearray()
    for i in range(0, len(bits_extraidos), 8):
        byte_str = bits_extraidos[i:i+8]
        if len(byte_str) == 8:
            bytes_lista.append(int(byte_str, 2))
            
    bytes_totales = bytes(bytes_lista)

    delimitador = b'#####END#####'
    if delimitador in bytes_totales:
        return bytes_totales.split(delimitador)[0]
    return None

def seleccionar_archivo(titulo="Seleccionar imagen"):
    root = tk.Tk()
    root.withdraw()
    ruta = filedialog.askopenfilename(
        title=titulo,
        filetypes=[("Archivos de imagen", "*.png")]
    )
    root.destroy()
    return ruta

def ejecucion_principal():
    print("--- Sistema de Ocultamiento Desktop Friendly ---")
    opcion = input("¿Deseas (O)cultar o (E)xtraer?: ").upper()
    pass_usuario = input("Contraseña Maestra: ")

    llave = obtener_llave(pass_usuario)

    if opcion == 'O':
        msg = input("Mensaje Secreto: ")
        
        print("Selecciona la imagen original")
        img_in = seleccionar_archivo("Selecciona la imagen original (PNG)")

        if not img_in:
            print("No se seleccionó ningún archivo.")
            return

        cifrado = cifrar_mensaje(msg, llave)
        bits_a_esconder = mensaje_a_bits(cifrado)
        ocultar_en_imagen(img_in, bits_a_esconder, "resultado_stego.png")

    elif opcion == 'E':
        print("Selecciona la imagen para extraer el secreto...")
        ruta = seleccionar_archivo("Imagen con secreto")

        if ruta:
            datos_cifrados = extraer_datos_de_imagen(ruta)
            if datos_cifrados:
                try:
                    mensaje_final = descifrar_mensaje(datos_cifrados, llave)
                    print("\n" + "="*30)
                    print(f"MENSAJE REVELADO: {mensaje_final}")
                    print("="*30 + "\n")
                except:
                    print("Error: Contraseña incorrecta. No se pudo descifrar el contenido.")
            else:
                print("No se encontró ninguna información oculta en esta imagen.")
                
ejecucion_principal()