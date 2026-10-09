from scapy.all import sniff, IP, TCP, ARP

def start_passive_listen(packet_count=20):
    print(f"[*] Analizando flujo de red (Estilo IDS)...")
    packets = sniff(count=packet_count)
    
    print(f"\n{'ORIGEN':<15} | {'DESTINO':<15} | {'PROT':<6} | {'INFO'}")
    print("-" * 60)
    
    for pkt in packets:
        if pkt.haslayer(IP):
            src = pkt[IP].src
            dst = pkt[IP].dst
            proto = "TCP" if pkt.haslayer(TCP) else "UDP"
            
            # Detectar si es una IP externa (fuera de tu red 192.168.x.x)
            es_externa = " [EXTERNA]" if not src.startswith("192.168") else ""
            
            info = f"Puerto: {pkt.sport} -> {pkt.dport}" if pkt.haslayer(TCP) else ""
            print(f"{src:<15} | {dst:<15} | {proto:<6} | {info}{es_externa}")
            
        elif pkt.haslayer(ARP) and pkt.op == 1:
            print(f"[ARP] {pkt.psrc} está buscando a {pkt.pdst}")