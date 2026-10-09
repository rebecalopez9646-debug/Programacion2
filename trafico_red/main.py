from modules.detection_ping import scan_ping
from modules.detection_passive import start_passive_listen
from modules.port_scan import scan_ports
from modules.scan_arp import scan_arp
import socket

def menu():
    print("--- PR2 SCAN: Herramienta de Análisis de Tráfico de Redes---")
    print("1. Ping Sweep")
    print("2. Escucha Pasiva (Wireshark style)")
    print("3. Escaneo de Puertos Comunes")
    print("4. Escaneo ARP (Descubrimiento Total)")

    opcion = input("Selecciona una opción: ")

    if opcion == "1":
        ip = input("Introduce la IP a testear: ")
        vivo = scan_ping(ip)
        #print(f'Host {'Activo' if vivo else 'Inactivo'}')
    elif opcion == "2":
        start_passive_listen()
    elif opcion == "3":
        objetivo = input("IP objetivo: ")
        try:
            ip_real = socket.gethostbyname(objetivo)

            if objetivo != ip_real:
                print(f"[*] Resolviendo dominio {objetivo} -> {ip_real}")

            scan_ports(ip_real)
        except socket.gaierror:
            print("[-] Error: No se pudo resolver el nombre de dominio. Verifica la URL (sin http:// ni /).")
    elif opcion=="4":
        rango=input("Introduce el rango de la IP: ")
        scan_arp(rango)

if __name__ == "__main__":
    menu()