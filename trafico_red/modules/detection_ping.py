import logging
import concurrent.futures # <-- Librería nativa de Python para multihilo
from scapy.all import IP, ICMP, sr1

# Silenciamos las advertencias de Scapy
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

def ping_individual(ip_destino):
    
    packet = IP(dst=ip_destino)/ICMP()
    resp = sr1(packet, timeout=0.5, verbose=0)
    if resp and resp.haslayer(ICMP) and resp.getlayer(ICMP).type == 0:
        return ip_destino
    return None

def scan_ping(network_prefix, n=254):
    prefix = network_prefix.strip().rstrip('.')
    print(f"[*] Escaneando subred {prefix}.1 hasta {prefix}.{n} ...")

    hosts_vivos = []
    lista_ips = [f"{prefix}.{i}" for i in range(1, n + 1)]

    # Creamos 50 "trabajadores" (hilos) para escanear en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # 'map' le asigna una IP diferente a cada hilo de forma simultánea
        resultados = executor.map(ping_individual, lista_ips)
        for ip in resultados:
            if ip is not None:
                print(f"[V] Host REAL encontrado: {ip}")
                hosts_vivos.append(ip)

    print(f"\n--- Escaneo finalizado: {len(hosts_vivos)} dispositivos reales ---")
    return hosts_vivos