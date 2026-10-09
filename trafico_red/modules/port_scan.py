from scapy.all import IP, TCP, sr1, conf

def scan_ports(target_ip):
    if target_ip == "127.0.0.1":
        conf.L3socket = conf.L3socket
    
    common_ports = {
        21: "FTP", 22: "SSH", 23: "Telnet (Inseguro)", 25: "SMTP",
        53: "DNS", 80: "HTTP", 110: "POP3", 139: "NetBIOS",
        143: "IMAP", 443: "HTTPS", 445: "SMB (Archivos Windows)",
        554: "RTSP (Cámara IP)", 1433: "SQL Server", 3306: "MySQL",
        3389: "RDP (Escritorio Windows)", 5432: "PostgreSQL",
        5900: "VNC", 8000: "FastAPI", 8080: "Proxy/Spring", 9000: "SonarQube/PHP"
    }

    print(f"\n[!] Iniciando escaneo de puertos en {target_ip}...")
    puertos_abiertos = 0
    for port, service in common_ports.items():
        print(f"[*] Probando puerto {port} ({service})...      ", end="\r")
        # Creamos el paquete SYN
        pkt = IP(dst=target_ip)/TCP(dport=port, flags="S")
        resp = sr1(pkt, timeout=0.8, verbose=0)

        if resp is None:
            # Sin respuesta = Filtrado por Firewall o pérdida de paquetes
            continue

        if resp.haslayer(TCP) and resp[TCP].flags == 0x12: # 0x12 es SYN-ACK (¡Puerto Abierto!)
            print(f"[+] Puerto {port:<5} ({service}): ABIERTO                       ")
            puertos_abiertos += 1
            
        elif resp.haslayer(TCP) and resp[TCP].flags == 0x14: # 0x14 es RST-ACK (Puerto Cerrado)
            pass
    print(" " * 60, end="\r")