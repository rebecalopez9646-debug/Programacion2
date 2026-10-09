from scapy.all import Ether, ARP, srp, conf, get_if_list, get_if_addr
from modules.port_scan import scan_ports

def obtener_interfaz_activa():
    return conf.iface

def scan_arp(ip_input):
    partes = ip_input.strip().rstrip('.').split('.')
    if len(partes) >= 3:
        network = f"{partes[0]}.{partes[1]}.{partes[2]}.0/24"
    else:
        print("[-] Error: Formato inválido.")
        return
    interfaz = obtener_interfaz_activa()
    print(f"[*] Usando interfaz: {interfaz}")
    print(f"[*] Escaneando red: {network}")

    try:
        packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)
        ans, unans = srp(packet, timeout=3, iface=interfaz, verbose=0)

        ips_encontradas = []

        print(f"\n{'IP':<15} | {'MAC Address':<20}")
        print("-" * 40)
        for sent, received in ans:
            ip_viva = received.psrc
            mac_viva = received.hwsrc
            print(f"{ip_viva:<15} | {mac_viva:<20}")
            ips_encontradas.append(ip_viva)
        if len(ans) == 0:
            print("\n[!] No se encontraron dispositivos.")
        else:
            print(f"\n[+] Se encontraron {len(ans)} dispositivos vivos.")
            # --- NUEVA LÓGICA DE ESCANEO DE PUERTOS ---
            continuar = input("\n¿Deseas realizar un escaneo de puertos a los hosts encontrados? (s/n): ").lower()

            if continuar == 's':
                print("\n[1] Escanear TODOS los hosts encontrados")
                print("[2] Escanear una IP específica")
                sub_opcion = input("Selecciona una opción: ")

                if sub_opcion == "1":
                    for ip in ips_encontradas:
                        scan_ports(ip) # Llamamos a tu módulo de puertos
                elif sub_opcion == "2":
                    target = input("Introduce la IP objetivo: ")
                    if target in ips_encontradas:
                        scan_ports(target)
                    else:
                        print("[-] Esa IP no estaba en la lista de dispositivos vivos.")

    except PermissionError:
        print("[-] ERROR: ¡Debes ejecutar el script con SUDO!")
    except Exception as e:
        print(f"[-] Error técnico: {e}")